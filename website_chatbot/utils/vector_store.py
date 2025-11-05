"""
Vector store module for embedding and searching website content.
Uses Google Vertex AI for embeddings and ChromaDB Cloud for vector storage.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging

import numpy as np
import chromadb
from chromadb.config import Settings
from google.cloud import aiplatform
from google.oauth2 import service_account
import vertexai
from vertexai.language_models import TextEmbeddingModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentChunk:
    """Represents a chunk of text with metadata."""
    
    def __init__(
        self, 
        text: str, 
        url: str, 
        title: str, 
        heading: str = None,
        chunk_id: int = 0
    ):
        self.text = text
        self.url = url
        self.title = title
        self.heading = heading
        self.chunk_id = chunk_id
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'text': self.text,
            'url': self.url,
            'title': self.title,
            'heading': self.heading,
            'chunk_id': self.chunk_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DocumentChunk':
        """Create from dictionary."""
        return cls(
            text=data['text'],
            url=data['url'],
            title=data['title'],
            heading=data.get('heading'),
            chunk_id=data.get('chunk_id', 0)
        )


class VectorStore:
    """Vector store for semantic search using Vertex AI embeddings and ChromaDB Cloud."""
    
    def __init__(
        self,
        project_id: str,
        location: str,
        embedding_model: str = "text-embedding-004",
        collection_name: str = "website_content",
        chroma_tenant: Optional[str] = None,
        chroma_database: Optional[str] = None,
        chroma_api_key: Optional[str] = None
    ):
        """
        Initialize the vector store with ChromaDB Cloud.
        
        Args:
            project_id: Google Cloud project ID
            location: Google Cloud location (e.g., 'us-central1')
            embedding_model: Vertex AI embedding model name
            collection_name: ChromaDB collection name
            chroma_tenant: ChromaDB Cloud tenant ID
            chroma_database: ChromaDB Cloud database name
            chroma_api_key: ChromaDB API key
        """
        self.project_id = project_id
        self.location = location
        self.embedding_model_name = embedding_model
        self.collection_name = collection_name
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        self.embedding_model = TextEmbeddingModel.from_pretrained(embedding_model)
        
        # Initialize ChromaDB client
        if chroma_api_key and chroma_tenant and chroma_database:
            # Use CloudClient for ChromaDB Cloud
            logger.info(f"Connecting to ChromaDB Cloud (tenant: {chroma_tenant}, database: {chroma_database})")
            self.chroma_client = chromadb.CloudClient(
                api_key=chroma_api_key,
                tenant=chroma_tenant,
                database=chroma_database
            )
        else:
            # Fallback to local in-memory client
            logger.info("Using local in-memory ChromaDB client")
            self.chroma_client = chromadb.Client(Settings(anonymized_telemetry=False))
        
        # Get or create collection
        try:
            self.collection = self.chroma_client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Connected to collection: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to connect to collection: {e}")
            raise
        
        logger.info(f"Initialized VectorStore with ChromaDB")
        logger.info(f"Embedding model: {embedding_model}")
    
    def _chunk_text(
        self, 
        text: str, 
        chunk_size: int = 1000, 
        overlap: int = 200
    ) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > chunk_size * 0.5:  # Only break if we're past halfway
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return [c for c in chunks if c]  # Remove empty chunks
    
    def _get_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Get embeddings for a list of texts using Vertex AI.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            NumPy array of embeddings
        """
        # Vertex AI has a batch limit, so process in batches
        batch_size = 5
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                embeddings = self.embedding_model.get_embeddings(batch)
                batch_embeddings = [emb.values for emb in embeddings]
                all_embeddings.extend(batch_embeddings)
                logger.info(f"Embedded batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
            except Exception as e:
                logger.error(f"Error getting embeddings: {e}")
                # Add zero vectors as fallback
                all_embeddings.extend([[0.0] * 768 for _ in batch])
        
        return np.array(all_embeddings)
    
    def index_pages(
        self, 
        pages: List, 
        chunk_size: int = 1000, 
        overlap: int = 200
    ) -> None:
        """
        Index web pages by creating embeddings and storing in ChromaDB Cloud.
        
        Args:
            pages: List of WebPage objects
            chunk_size: Size of text chunks
            overlap: Overlap between chunks
        """
        logger.info(f"Indexing {len(pages)} pages...")
        
        # Clear existing collection data
        try:
            self.chroma_client.delete_collection(name=self.collection_name)
            logger.info(f"Deleted existing collection: {self.collection_name}")
        except:
            pass
        
        self.collection = self.chroma_client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"Created fresh collection: {self.collection_name}")
        
        all_texts = []
        all_metadatas = []
        all_ids = []
        
        # Create chunks from all pages
        chunk_counter = 0
        for page in pages:
            page_chunks = self._chunk_text(page.content, chunk_size, overlap)
            
            for idx, chunk_text in enumerate(page_chunks):
                # Skip extremely large chunks
                if len(chunk_text) > 10000:
                    logger.warning(f"Skipping large chunk ({len(chunk_text)} chars) from {page.url}")
                    continue
                    
                # Try to associate chunk with a heading
                heading = None
                if page.headings:
                    for h in page.headings:
                        if h in chunk_text:
                            heading = h
                            break
                
                # Store metadata
                metadata = {
                    'url': str(page.url),
                    'title': str(page.title)[:500],  # Limit title length
                    'heading': str(heading)[:200] if heading else '',
                    'chunk_id': int(idx)
                }
                
                all_texts.append(chunk_text)
                all_metadatas.append(metadata)
                all_ids.append(f"chunk_{chunk_counter}")
                chunk_counter += 1
        
        logger.info(f"Created {len(all_texts)} chunks from {len(pages)} pages")
        
        # Generate embeddings using Vertex AI
        embeddings = self._get_embeddings(all_texts)
        logger.info(f"Generated {len(embeddings)} embeddings")
        
        # Add to ChromaDB in smaller batches (CloudaDB may have limits)
        batch_size = 50
        try:
            logger.info(f"Starting to add {len(all_texts)} chunks to ChromaDB Cloud...")
            for i in range(0, len(all_texts), batch_size):
                batch_end = min(i + batch_size, len(all_texts))
                
                self.collection.add(
                    embeddings=embeddings[i:batch_end].tolist(),
                    documents=all_texts[i:batch_end],
                    metadatas=all_metadatas[i:batch_end],
                    ids=all_ids[i:batch_end]
                )
                logger.info(f"Added batch {i//batch_size + 1}/{(len(all_texts)-1)//batch_size + 1} to ChromaDB")
            
            logger.info(f"Successfully indexed {len(all_texts)} chunks in ChromaDB Cloud")
        except Exception as e:
            logger.error(f"Error adding to ChromaDB: {e}")
            raise
    
    def search(
        self, 
        query: str, 
        top_k: int = 5
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        Search for relevant chunks using ChromaDB Cloud.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of (DocumentChunk, score) tuples
        """
        # Get query embedding
        query_embedding = self._get_embeddings([query])[0]
        
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )
        
        # Convert results to DocumentChunk format
        chunks_with_scores = []
        if results['documents'] and len(results['documents'][0]) > 0:
            for i in range(len(results['documents'][0])):
                metadata = results['metadatas'][0][i]
                chunk = DocumentChunk(
                    text=results['documents'][0][i],
                    url=metadata['url'],
                    title=metadata['title'],
                    heading=metadata['heading'] if metadata['heading'] else None,
                    chunk_id=metadata['chunk_id']
                )
                # ChromaDB returns distances, convert to similarity score
                score = 1 / (1 + results['distances'][0][i])
                chunks_with_scores.append((chunk, score))
        
        return chunks_with_scores
    
    def save(self) -> None:
        """
        Save method for compatibility - ChromaDB Cloud auto-persists.
        No action needed as data is stored on cloud server.
        """
        try:
            count = self.collection.count()
            logger.info(f"ChromaDB collection '{self.collection_name}' contains {count} chunks on cloud")
        except Exception as e:
            logger.warning(f"Could not get collection count: {e}")
    
    def load(self) -> bool:
        """
        Load method for compatibility - ChromaDB Cloud data is always available.
        
        Returns:
            True if collection exists and has data, False otherwise
        """
        try:
            count = self.collection.count()
            if count > 0:
                logger.info(f"Connected to ChromaDB collection '{self.collection_name}' with {count} chunks")
                return True
            else:
                logger.warning(f"ChromaDB collection '{self.collection_name}' is empty")
                return False
        except Exception as e:
            logger.error(f"Error connecting to ChromaDB collection: {e}")
            return False
    
    def get_chunk_count(self) -> int:
        """
        Get the number of chunks in the collection.
        
        Returns:
            Number of chunks in the collection
        """
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Error getting collection count: {e}")
            return 0
