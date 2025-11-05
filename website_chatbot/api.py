"""
FastAPI application for Website Chatbot.
RESTful API endpoints for website-grounded Q&A.
"""

import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional, List, Dict
from dotenv import load_dotenv
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

from utils.vector_store import VectorStore
from utils.vertex_chat_client import VertexAIChatClient
from agents.workflow import WebsiteChatbotWorkflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Global variables for shared resources
vector_store: Optional[VectorStore] = None
vertex_client: Optional[VertexAIChatClient] = None
workflow: Optional[WebsiteChatbotWorkflow] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app.
    Initializes resources on startup and cleans up on shutdown.
    """
    global vector_store, vertex_client, workflow
    
    logger.info("Initializing application resources...")
    
    try:
        # Initialize vector store
        vector_store = VectorStore(
            project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
            location=os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1'),
            embedding_model=os.getenv('VERTEX_AI_EMBEDDING_MODEL', 'text-embedding-004'),
            collection_name=os.getenv('CHROMADB_COLLECTION_NAME', 'website_content'),
            chroma_tenant=os.getenv('CHROMADB_TENANT'),
            chroma_database=os.getenv('CHROMADB_DATABASE'),
            chroma_api_key=os.getenv('CHROMADB_API_KEY')
        )
        
        # Load existing index
        if not vector_store.load():
            logger.warning("No indexed website found! Search endpoints will not work until website is indexed.")
        else:
            logger.info("Vector store loaded successfully")
        
        # Initialize Vertex AI client
        vertex_client = VertexAIChatClient(
            project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
            location=os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1'),
            model_name=os.getenv('VERTEX_AI_MODEL', 'gemini-1.5-pro')
        )
        logger.info("Vertex AI client initialized")
        
        # Create workflow
        workflow = WebsiteChatbotWorkflow(
            vector_store=vector_store,
            vertex_client=vertex_client
        )
        logger.info("Workflow initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize resources: {e}")
        raise
    
    yield  # Application runs here
    
    # Cleanup
    logger.info("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title="Website Chatbot API",
    description="Grounded Q&A API with indexed website content using Google Vertex AI",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv('CORS_ORIGINS', '*').split(','),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    query: str = Field(..., description="User's question", min_length=1, max_length=2000)
    chat_history: Optional[List[Dict]] = Field(default=None, description="Optional chat history")
    top_k: int = Field(default=5, description="Number of search results to use", ge=1, le=20)
    stream: bool = Field(default=False, description="Whether to stream the response")


class SearchRequest(BaseModel):
    """Request model for search endpoint."""
    query: str = Field(..., description="Search query", min_length=1, max_length=500)
    top_k: int = Field(default=5, description="Number of results to return", ge=1, le=20)


class IndexRequest(BaseModel):
    """Request model for indexing endpoint."""
    url: str = Field(..., description="Website URL to index")
    max_depth: int = Field(default=3, description="Maximum crawl depth", ge=1, le=10)
    max_pages: int = Field(default=100, description="Maximum pages to crawl", ge=1, le=1000)
    use_js_crawler: bool = Field(default=True, description="Use JavaScript-aware crawler")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    answer: str
    sources: List[Dict]
    query: str


class SearchResult(BaseModel):
    """Model for a single search result."""
    title: str
    url: str
    heading: Optional[str]
    text: str
    score: float


class SearchResponse(BaseModel):
    """Response model for search endpoint."""
    query: str
    results: List[SearchResult]


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    version: str
    indexed: bool


# API Endpoints

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "indexed": vector_store is not None and vector_store.collection is not None
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "indexed": vector_store is not None and vector_store.collection is not None
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint - process a user query and return grounded answer.
    
    Args:
        request: ChatRequest with query, optional chat history, and top_k
        
    Returns:
        ChatResponse with answer and sources
    """
    if workflow is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    if vector_store.collection is None:
        raise HTTPException(
            status_code=400,
            detail="No indexed website found. Please index a website first using /api/index"
        )
    
    try:
        logger.info(f"Processing chat request: {request.query[:100]}")
        
        # Process query through workflow
        result = await workflow.process_query(
            query=request.query,
            chat_history=request.chat_history,
            top_k=request.top_k
        )
        
        return ChatResponse(
            answer=result.get('answer', ''),
            sources=result.get('sources', []),
            query=request.query
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint - stream the response as it's generated.
    
    Args:
        request: ChatRequest with query, optional chat history, and top_k
        
    Returns:
        StreamingResponse with Server-Sent Events
    """
    if workflow is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    if vector_store.collection is None:
        raise HTTPException(
            status_code=400,
            detail="No indexed website found. Please index a website first using /api/index"
        )
    
    async def event_generator():
        """Generate SSE events for streaming response."""
        try:
            logger.info(f"Processing streaming chat request: {request.query[:100]}")
            
            # Send initial event
            yield f"event: start\ndata: {{\"status\": \"processing\"}}\n\n"
            
            # Process query through workflow with streaming
            async for chunk in workflow.process_query_stream(
                query=request.query,
                chat_history=request.chat_history,
                top_k=request.top_k
            ):
                if chunk.get('type') == 'sources':
                    import json
                    yield f"event: sources\ndata: {json.dumps(chunk)}\n\n"
                elif chunk.get('type') == 'token':
                    import json
                    yield f"event: token\ndata: {json.dumps(chunk)}\n\n"
                elif chunk.get('type') == 'complete':
                    import json
                    yield f"event: complete\ndata: {json.dumps(chunk)}\n\n"
            
        except Exception as e:
            logger.error(f"Error in streaming chat: {e}")
            import json
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/api/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Search endpoint - perform semantic search on indexed content.
    
    Args:
        request: SearchRequest with query and top_k
        
    Returns:
        SearchResponse with search results
    """
    if vector_store is None or vector_store.collection is None:
        raise HTTPException(
            status_code=400,
            detail="No indexed website found. Please index a website first using /api/index"
        )
    
    try:
        logger.info(f"Processing search request: {request.query}")
        
        # Perform search
        results = vector_store.search(request.query, top_k=request.top_k)
        
        # Format results
        search_results = [
            SearchResult(
                title=chunk.title,
                url=chunk.url,
                heading=chunk.heading,
                text=chunk.text,
                score=float(score)
            )
            for chunk, score in results
        ]
        
        return SearchResponse(
            query=request.query,
            results=search_results
        )
        
    except Exception as e:
        logger.error(f"Error processing search request: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing search: {str(e)}")


@app.post("/api/index")
async def index_website(request: IndexRequest):
    """
    Index a website by crawling and creating embeddings.
    This is an async operation that runs in the background.
    
    Args:
        request: IndexRequest with URL and crawl parameters
        
    Returns:
        Status message
    """
    try:
        from utils.crawler import WebsiteCrawler
        from utils.js_crawler import JavaScriptWebsiteCrawler
        
        logger.info(f"Starting website indexing: {request.url}")
        
        # Create crawler
        if request.use_js_crawler:
            crawler = JavaScriptWebsiteCrawler(
                base_url=request.url,
                max_depth=request.max_depth,
                max_pages=request.max_pages,
                delay=1.0,
                headless=True
            )
        else:
            crawler = WebsiteCrawler(
                base_url=request.url,
                max_depth=request.max_depth,
                max_pages=request.max_pages,
                delay=0.5
            )
        
        # Crawl website
        pages = await crawler.crawl()
        logger.info(f"Crawled {len(pages)} pages")
        
        # Index pages
        chunk_size = int(os.getenv('CHUNK_SIZE', '1000'))
        chunk_overlap = int(os.getenv('CHUNK_OVERLAP', '200'))
        
        vector_store.index_pages(pages, chunk_size, chunk_overlap)
        vector_store.save()
        
        logger.info("Website indexed successfully")
        
        return {
            "status": "success",
            "message": f"Successfully indexed {len(pages)} pages from {request.url}",
            "pages_indexed": len(pages)
        }
        
    except Exception as e:
        logger.error(f"Error indexing website: {e}")
        raise HTTPException(status_code=500, detail=f"Error indexing website: {str(e)}")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or default to 8080 (GCP Cloud Run default)
    port = int(os.getenv('PORT', '8080'))
    host = os.getenv('HOST', '0.0.0.0')
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        reload=os.getenv('ENVIRONMENT', 'production') == 'development',
        log_level="info"
    )
