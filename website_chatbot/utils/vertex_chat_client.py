"""
Vertex AI Chat Client for Microsoft Agent Framework.
Custom implementation to use Google Vertex AI models with the agent framework.
"""

import asyncio
from typing import List, Optional, AsyncIterator, Dict, Any
from dataclasses import dataclass
import logging

import vertexai
from vertexai.generative_models import GenerativeModel, Content, Part
from google.oauth2 import service_account

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    """Represents a chat message."""
    role: str  # 'user' or 'assistant'
    content: str
    
    def to_vertex_content(self) -> Content:
        """Convert to Vertex AI Content format."""
        # Map roles to Vertex AI format
        role_mapping = {
            'user': 'user',
            'assistant': 'model',
            'system': 'user'  # Vertex AI doesn't have separate system role
        }
        
        return Content(
            role=role_mapping.get(self.role, 'user'),
            parts=[Part.from_text(self.content)]
        )


class VertexAIChatClient:
    """
    Chat client that uses Google Vertex AI models.
    Compatible with Microsoft Agent Framework's chat client interface.
    """
    
    def __init__(
        self,
        project_id: str,
        location: str,
        model_name: str = "gemini-1.5-pro",
        credentials_path: Optional[str] = None
    ):
        """
        Initialize Vertex AI chat client.
        
        Args:
            project_id: Google Cloud project ID
            location: Google Cloud location (e.g., 'us-central1')
            model_name: Vertex AI model name
            credentials_path: Optional path to service account credentials
        """
        self.project_id = project_id
        self.location = location
        self.model_name = model_name
        
        # Initialize Vertex AI
        if credentials_path:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
            vertexai.init(
                project=project_id, 
                location=location,
                credentials=credentials
            )
        else:
            vertexai.init(project=project_id, location=location)
        
        self.model = GenerativeModel(model_name)
        logger.info(f"Initialized Vertex AI client with model: {model_name}")
    
    async def generate_response(
        self,
        messages: List[ChatMessage],
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """
        Generate a response from the model.
        
        Args:
            messages: List of chat messages
            system_instruction: Optional system instruction
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated response text
        """
        try:
            # Build conversation history
            contents = []
            
            # Add system instruction as first user message if provided
            if system_instruction:
                contents.append(Content(
                    role='user',
                    parts=[Part.from_text(f"System: {system_instruction}")]
                ))
            
            # Add conversation history
            for msg in messages:
                contents.append(msg.to_vertex_content())
            
            # Generate response
            generation_config = {
                'temperature': temperature,
                'max_output_tokens': max_tokens,
            }
            
            # Use generate_content for synchronous generation
            # We'll run it in executor to make it async
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    contents,
                    generation_config=generation_config
                )
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error: {str(e)}"
    
    async def generate_response_stream(
        self,
        messages: List[ChatMessage],
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> AsyncIterator[str]:
        """
        Generate a streaming response from the model.
        
        Args:
            messages: List of chat messages
            system_instruction: Optional system instruction
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Yields:
            Response text chunks
        """
        try:
            # Build conversation history
            contents = []
            
            if system_instruction:
                contents.append(Content(
                    role='user',
                    parts=[Part.from_text(f"System: {system_instruction}")]
                ))
            
            for msg in messages:
                contents.append(msg.to_vertex_content())
            
            generation_config = {
                'temperature': temperature,
                'max_output_tokens': max_tokens,
            }
            
            # Generate streaming response
            loop = asyncio.get_event_loop()
            response_stream = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    contents,
                    generation_config=generation_config,
                    stream=True
                )
            )
            
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            logger.error(f"Error in streaming response: {e}")
            yield f"Error: {str(e)}"


async def test_client():
    """Test the Vertex AI chat client."""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    client = VertexAIChatClient(
        project_id=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        model_name=os.getenv("VERTEX_AI_MODEL", "gemini-1.5-pro")
    )
    
    messages = [
        ChatMessage(role="user", content="What is the capital of France?")
    ]
    
    print("Testing synchronous response:")
    response = await client.generate_response(messages)
    print(f"Response: {response}\n")
    
    print("Testing streaming response:")
    messages.append(ChatMessage(role="user", content="Tell me a fun fact about it."))
    async for chunk in client.generate_response_stream(messages):
        print(chunk, end='', flush=True)
    print("\n")


if __name__ == "__main__":
    asyncio.run(test_client())
