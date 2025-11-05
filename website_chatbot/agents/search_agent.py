"""
Website Search Agent using Microsoft Agent Framework.
Searches indexed website content and provides grounded responses with links.
"""

import asyncio
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

from agent_framework import (
    Executor,
    WorkflowContext,
    handler,
)

from utils.vector_store import VectorStore, DocumentChunk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SearchRequest:
    """Request to search the website knowledge base."""
    query: str
    top_k: int = 5


@dataclass
class SearchResult:
    """Result from searching the knowledge base."""
    query: str
    chunks: List[Dict]
    sources: List[str]


class WebsiteSearchAgent(Executor):
    """
    Agent that searches indexed website content.
    Uses vector store for semantic search.
    """
    
    def __init__(
        self,
        vector_store: VectorStore,
        executor_id: str = "website_search_agent"
    ):
        """
        Initialize the search agent.
        
        Args:
            vector_store: Vector store containing indexed website content
            executor_id: Unique identifier for this executor
        """
        super().__init__(id=executor_id)
        self.vector_store = vector_store
        chunk_count = vector_store.get_chunk_count()
        logger.info(f"Initialized WebsiteSearchAgent with {chunk_count} chunks")
    
    @handler
    async def search(
        self,
        request: SearchRequest,
        ctx: WorkflowContext
    ) -> SearchResult:
        """
        Search the website knowledge base.
        
        Args:
            request: Search request with query
            ctx: Workflow context
            
        Returns:
            SearchResult with relevant chunks and sources
        """
        logger.info(f"Searching for: {request.query}")
        
        # Perform semantic search
        results = self.vector_store.search(request.query, top_k=request.top_k)
        
        # Format results
        chunks = []
        sources = set()
        
        for chunk, score in results:
            chunk_data = {
                'text': chunk.text,
                'url': chunk.url,
                'title': chunk.title,
                'heading': chunk.heading,
                'score': score
            }
            chunks.append(chunk_data)
            sources.add(chunk.url)
        
        result = SearchResult(
            query=request.query,
            chunks=chunks,
            sources=list(sources)
        )
        
        logger.info(f"Found {len(chunks)} relevant chunks from {len(sources)} pages")
        
        # Send result to next step
        await ctx.send_message(result)
        
        return result


@dataclass
class AnswerRequest:
    """Request to generate an answer based on search results."""
    query: str
    search_result: SearchResult
    chat_history: List[Dict] = None


@dataclass
class AnswerResponse:
    """Generated answer with sources."""
    query: str
    answer: str
    sources: List[Dict]


class AnswerGenerationAgent(Executor):
    """
    Agent that generates answers based on search results.
    Uses Vertex AI to generate grounded responses.
    """
    
    def __init__(
        self,
        chat_client,
        executor_id: str = "answer_generation_agent"
    ):
        """
        Initialize the answer generation agent.
        
        Args:
            chat_client: Vertex AI chat client
            executor_id: Unique identifier for this executor
        """
        super().__init__(id=executor_id)
        self.chat_client = chat_client
        logger.info("Initialized AnswerGenerationAgent")
    
    def _build_context(self, search_result: SearchResult) -> str:
        """Build context from search results."""
        context_parts = []
        
        for i, chunk in enumerate(search_result.chunks, 1):
            heading = chunk.get('heading', '')
            heading_str = f" - {heading}" if heading else ""
            
            context_parts.append(
                f"[Source {i}] {chunk['title']}{heading_str}\n"
                f"URL: {chunk['url']}\n"
                f"Content: {chunk['text']}\n"
            )
        
        return "\n".join(context_parts)
    
    def _extract_source_urls(self, search_result: SearchResult) -> List[Dict]:
        """Extract unique sources with metadata."""
        sources_dict = {}
        
        for chunk in search_result.chunks:
            url = chunk['url']
            if url not in sources_dict:
                sources_dict[url] = {
                    'url': url,
                    'title': chunk['title'],
                    'sections': []
                }
            
            if chunk.get('heading'):
                sources_dict[url]['sections'].append(chunk['heading'])
        
        # Remove duplicate sections
        for source in sources_dict.values():
            source['sections'] = list(set(source['sections']))
        
        return list(sources_dict.values())
    
    @handler
    async def process_search_result(
        self,
        search_result: SearchResult,
        ctx: WorkflowContext
    ) -> AnswerResponse:
        """
        Process search results and generate an answer.
        
        Args:
            search_result: Search results from the search agent
            ctx: Workflow context
            
        Returns:
            AnswerResponse with generated answer and sources
        """
        logger.info(f"Generating answer for: {search_result.query}")
        
        # Build context from search results
        context = self._build_context(search_result)
        
        # Create system instruction
        system_instruction = """You are a helpful assistant that answers questions based on website content.

Your task:
1. Answer the user's question using ONLY the information provided in the context
2. Be specific and cite which source you're using
3. If the context doesn't contain enough information, say so
4. Keep answers concise but complete
5. Always reference the source number when using information

Format your answer naturally, mentioning relevant source numbers inline like "According to Source 1..." or "As mentioned in Source 2..."."""

        # Build prompt
        prompt = f"""Context from website:
{context}

User Question: {search_result.query}

Please provide a comprehensive answer based on the context above. Cite your sources by number."""

        # Import ChatMessage from our client
        from utils.vertex_chat_client import ChatMessage
        
        messages = [ChatMessage(role='user', content=prompt)]
        
        # Generate response
        answer = await self.chat_client.generate_response(
            messages=messages,
            system_instruction=system_instruction,
            temperature=0.3  # Lower temperature for more factual responses
        )
        
        # Extract sources
        sources = self._extract_source_urls(search_result)
        
        response = AnswerResponse(
            query=search_result.query,
            answer=answer,
            sources=sources
        )
        
        logger.info("Generated answer successfully")
        
        # Yield the output so it can be captured
        await ctx.yield_output(response)
        
        return response
    
    @handler
    async def generate_answer(
        self,
        request: AnswerRequest,
        ctx: WorkflowContext
    ) -> AnswerResponse:
        """
        Generate an answer based on search results.
        
        Args:
            request: Answer request with query and search results
            ctx: Workflow context
            
        Returns:
            AnswerResponse with generated answer and sources
        """
        logger.info(f"Generating answer for: {request.query}")
        
        # Build context from search results
        context = self._build_context(request.search_result)
        
        # Create system instruction
        system_instruction = """You are a helpful assistant that answers questions based on website content.

Your task:
1. Answer the user's question using ONLY the information provided in the context
2. Be specific and cite which source you're using
3. If the context doesn't contain enough information, say so
4. Keep answers concise but complete
5. Always reference the source number when using information

Format your answer naturally, mentioning relevant source numbers inline like "According to Source 1..." or "As mentioned in Source 2..."."""

        # Build prompt
        prompt = f"""Context from website:
{context}

User Question: {request.query}

Please provide a comprehensive answer based on the context above. Cite your sources by number."""

        # Import ChatMessage from our client
        from utils.vertex_chat_client import ChatMessage
        
        messages = []
        
        # Add chat history if available
        if request.chat_history:
            for msg in request.chat_history:
                messages.append(ChatMessage(
                    role=msg.get('role', 'user'),
                    content=msg.get('content', '')
                ))
        
        # Add current query
        messages.append(ChatMessage(role='user', content=prompt))
        
        # Generate response
        answer = await self.chat_client.generate_response(
            messages=messages,
            system_instruction=system_instruction,
            temperature=0.3  # Lower temperature for more factual responses
        )
        
        # Extract sources
        sources = self._extract_source_urls(request.search_result)
        
        response = AnswerResponse(
            query=request.query,
            answer=answer,
            sources=sources
        )
        
        logger.info("Generated answer successfully")
        
        # Yield result to output so it can be captured
        await ctx.yield_output(response)
        
        return response
