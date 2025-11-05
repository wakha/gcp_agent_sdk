"""
Multi-agent orchestration workflow for website chatbot.
Uses Microsoft Agent Framework to coordinate search and answer generation.
"""

import asyncio
from typing import Optional, List, Dict
import logging

from agent_framework import (
    WorkflowBuilder,
    WorkflowContext,
    WorkflowOutputEvent,
    WorkflowStatusEvent,
    WorkflowRunState,
)

from agents.search_agent import (
    WebsiteSearchAgent,
    AnswerGenerationAgent,
    SearchRequest,
    AnswerRequest,
)
from utils.vector_store import VectorStore
from utils.vertex_chat_client import VertexAIChatClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebsiteChatbotWorkflow:
    """
    Orchestrates multi-agent workflow for website-grounded chatbot.
    
    Flow:
    1. User query -> Search Agent (semantic search)
    2. Search results -> Answer Agent (generate grounded response)
    3. Answer + Sources -> User
    """
    
    def __init__(
        self,
        vector_store: VectorStore,
        vertex_client: VertexAIChatClient,
    ):
        """
        Initialize the workflow.
        
        Args:
            vector_store: Vector store with indexed website content
            vertex_client: Vertex AI chat client
        """
        self.vector_store = vector_store
        self.vertex_client = vertex_client
        
        # Initialize agents
        self.search_agent = WebsiteSearchAgent(vector_store)
        self.answer_agent = AnswerGenerationAgent(vertex_client)
        
        # Build workflow
        self.workflow = self._build_workflow()
        
        logger.info("Initialized WebsiteChatbotWorkflow")
    
    def _build_workflow(self):
        """Build the agent workflow graph."""
        builder = WorkflowBuilder()
        
        # Build a simple flow: Start -> Search Agent -> Answer Agent -> End
        workflow = (
            builder
            .set_start_executor(self.search_agent)
            .add_edge(self.search_agent, self.answer_agent)
            .build()
        )
        
        return workflow
    
    async def process_query(
        self,
        query: str,
        chat_history: Optional[List[Dict]] = None,
        top_k: int = 5
    ) -> Dict:
        """
        Process a user query through the workflow.
        
        Args:
            query: User's question
            chat_history: Optional chat history for context
            top_k: Number of search results to retrieve
            
        Returns:
            Dictionary with answer and sources
        """
        logger.info(f"Processing query: {query}")
        
        # Create initial search request
        search_request = SearchRequest(query=query, top_k=top_k)
        
        # Track workflow output
        output_data = {}
        search_result = None
        
        # Run workflow
        async for event in self.workflow.run_stream(search_request):
            if isinstance(event, WorkflowOutputEvent):
                logger.info(f"Workflow output event: {type(event.data)}")
                
                # Capture output
                if hasattr(event.data, 'query'):
                    output_data = event.data
            
            elif isinstance(event, WorkflowStatusEvent):
                logger.info(f"Workflow status: {event.state}")
                
                # Check if we need to pass data between agents
                if event.state == WorkflowRunState.IDLE:
                    # Workflow might need intermediate data
                    pass
        
        # Format response
        if hasattr(output_data, 'answer'):
            return {
                'query': query,
                'answer': output_data.answer,
                'sources': output_data.sources
            }
        else:
            return {
                'query': query,
                'answer': 'Sorry, I could not process your query.',
                'sources': []
            }
    
    async def process_query_stream(
        self,
        query: str,
        chat_history: Optional[List[Dict]] = None,
        top_k: int = 5
    ):
        """
        Process a user query through the workflow with streaming.
        
        Args:
            query: User's question
            chat_history: Optional chat history for context
            top_k: Number of search results to retrieve
            
        Yields:
            Dictionary chunks with type, content, and metadata
        """
        logger.info(f"Processing streaming query: {query}")
        
        # Create initial search request
        search_request = SearchRequest(query=query, top_k=top_k)
        
        # Track workflow output
        sources_sent = False
        
        # Run workflow
        async for event in self.workflow.run_stream(search_request):
            if isinstance(event, WorkflowOutputEvent):
                logger.info(f"Workflow output event: {type(event.data)}")
                
                # Send sources first if available
                if hasattr(event.data, 'sources') and not sources_sent:
                    yield {
                        'type': 'sources',
                        'sources': event.data.sources
                    }
                    sources_sent = True
                
                # Stream answer tokens
                if hasattr(event.data, 'answer'):
                    # For now, send the full answer as we don't have token-level streaming
                    # In a future version, this could stream individual tokens
                    answer = event.data.answer
                    yield {
                        'type': 'token',
                        'content': answer
                    }
            
            elif isinstance(event, WorkflowStatusEvent):
                logger.info(f"Workflow status: {event.state}")
                
                # Optionally yield status updates
                yield {
                    'type': 'status',
                    'state': event.state.name if hasattr(event.state, 'name') else str(event.state)
                }
        
        # Send completion event
        yield {
            'type': 'complete',
            'query': query
        }
    
    async def chat(self):
        """
        Run interactive chat session.
        """
        print("\n" + "="*60)
        print("Website Chatbot - Grounded on Indexed Website Content")
        print("="*60)
        print("Ask questions about the website content.")
        print("Type 'exit' or 'quit' to end the session.\n")
        
        chat_history = []
        
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("\nGoodbye! 👋")
                    break
                
                # Process query
                result = await self.process_query(
                    query=user_input,
                    chat_history=chat_history
                )
                
                # Display answer
                print(f"\nAssistant: {result['answer']}\n")
                
                # Display sources
                if result['sources']:
                    print("📚 Sources:")
                    for i, source in enumerate(result['sources'], 1):
                        sections = source.get('sections', [])
                        sections_str = f" ({', '.join(sections)})" if sections else ""
                        print(f"  {i}. {source['title']}{sections_str}")
                        print(f"     🔗 {source['url']}")
                    print()
                
                # Update chat history
                chat_history.append({
                    'role': 'user',
                    'content': user_input
                })
                chat_history.append({
                    'role': 'assistant',
                    'content': result['answer']
                })
                
                # Keep history manageable
                if len(chat_history) > 10:
                    chat_history = chat_history[-10:]
                
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                logger.error(f"Error processing query: {e}")
                print(f"\nError: {str(e)}\n")


async def main():
    """Example usage of the workflow."""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Initialize vector store
    vector_store = VectorStore(
        project_id=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        embedding_model=os.getenv("VERTEX_AI_EMBEDDING_MODEL", "text-embedding-004")
    )
    
    # Try to load existing index
    if not vector_store.load():
        print("No existing vector store found. Please run indexing first.")
        return
    
    # Initialize Vertex AI client
    vertex_client = VertexAIChatClient(
        project_id=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        model_name=os.getenv("VERTEX_AI_MODEL", "gemini-1.5-pro")
    )
    
    # Create workflow
    workflow = WebsiteChatbotWorkflow(
        vector_store=vector_store,
        vertex_client=vertex_client
    )
    
    # Run interactive chat
    await workflow.chat()


if __name__ == "__main__":
    asyncio.run(main())
