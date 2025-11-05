"""
Main application for Website Chatbot.
Index a website and run the grounded chatbot.
"""

import asyncio
import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import logging

# Fix Windows encoding issues
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from utils.crawler import WebsiteCrawler
from utils.js_crawler import JavaScriptWebsiteCrawler
from utils.vector_store import VectorStore
from utils.vertex_chat_client import VertexAIChatClient
from agents.workflow import WebsiteChatbotWorkflow

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def index_website(args):
    """Index a website by crawling and creating embeddings."""
    print("\n" + "="*60)
    print("Website Indexing")
    print("="*60)
    
    # Load environment
    env_path = Path(__file__).parent / '.env'
    load_dotenv(env_path)
    
    # Get configuration
    website_url = args.url or os.getenv('TARGET_WEBSITE_URL')
    max_depth = args.depth or int(os.getenv('MAX_CRAWL_DEPTH', '3'))
    max_pages = args.max_pages or int(os.getenv('MAX_PAGES', '100'))
    use_js_crawler = args.js if hasattr(args, 'js') else True  # Default to JS crawler
    
    if not website_url:
        print("Error: Please provide a website URL using --url or set TARGET_WEBSITE_URL in .env")
        return
    
    crawler_type = "JavaScript-aware (Playwright)" if use_js_crawler else "Standard (aiohttp)"
    print(f"\nCrawling: {website_url}")
    print(f"Crawler type: {crawler_type}")
    print(f"Max depth: {max_depth}")
    print(f"Max pages: {max_pages}\n")
    
    # Crawl website - use JavaScript-aware crawler by default
    if use_js_crawler:
        crawler = JavaScriptWebsiteCrawler(
            base_url=website_url,
            max_depth=max_depth,
            max_pages=max_pages,
            delay=1.0,
            headless=True
        )
    else:
        crawler = WebsiteCrawler(
            base_url=website_url,
            max_depth=max_depth,
            max_pages=max_pages,
            delay=0.5
        )
    
    pages = await crawler.crawl()
    print(f"\n[OK] Crawled {len(pages)} pages\n")
    
    # Create vector store with ChromaDB Cloud
    print("Creating embeddings...")
    vector_store = VectorStore(
        project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
        location=os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1'),
        embedding_model=os.getenv('VERTEX_AI_EMBEDDING_MODEL', 'text-embedding-004'),
        collection_name=os.getenv('CHROMADB_COLLECTION_NAME', 'website_content'),
        chroma_tenant=os.getenv('CHROMADB_TENANT'),
        chroma_database=os.getenv('CHROMADB_DATABASE'),
        chroma_api_key=os.getenv('CHROMADB_API_KEY')
    )
    
    # Index pages
    chunk_size = int(os.getenv('CHUNK_SIZE', '1000'))
    chunk_overlap = int(os.getenv('CHUNK_OVERLAP', '200'))
    
    vector_store.index_pages(pages, chunk_size, chunk_overlap)
    
    # Save vector store (auto-persists on cloud)
    vector_store.save()
    print(f"\n[OK] Saved vector store to ChromaDB Cloud\n")
    
    print("="*60)
    print("Indexing Complete!")
    print("="*60)
    print("\nYou can now run the chatbot with: python main.py chat\n")


async def run_chatbot(args):
    """Run the interactive chatbot."""
    # Load environment
    env_path = Path(__file__).parent / '.env'
    load_dotenv(env_path)
    
    # Initialize vector store with ChromaDB Cloud
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
        print("\n" + "="*60)
        print("Error: No indexed website found!")
        print("="*60)
        print("\nPlease index a website first using:")
        print("  python main.py index --url <website_url>\n")
        return
    
    # Initialize Vertex AI client
    vertex_client = VertexAIChatClient(
        project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
        location=os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1'),
        model_name=os.getenv('VERTEX_AI_MODEL', 'gemini-1.5-pro')
    )
    
    # Create and run workflow
    workflow = WebsiteChatbotWorkflow(
        vector_store=vector_store,
        vertex_client=vertex_client
    )
    
    await workflow.chat()


async def test_search(args):
    """Test search functionality."""
    # Load environment
    env_path = Path(__file__).parent / '.env'
    load_dotenv(env_path)
    
    # Initialize vector store with ChromaDB Cloud
    vector_store = VectorStore(
        project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
        location=os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1'),
        embedding_model=os.getenv('VERTEX_AI_EMBEDDING_MODEL', 'text-embedding-004'),
        collection_name=os.getenv('CHROMADB_COLLECTION_NAME', 'website_content'),
        chroma_tenant=os.getenv('CHROMADB_TENANT'),
        chroma_database=os.getenv('CHROMADB_DATABASE'),
        chroma_api_key=os.getenv('CHROMADB_API_KEY')
    )
    
    if not vector_store.load():
        print("Error: No indexed website found!")
        return
    
    # Perform search
    query = args.query or "What is this website about?"
    print(f"\nSearching for: {query}\n")
    
    results = vector_store.search(query, top_k=5)
    
    print("Search Results:")
    print("="*60)
    for i, (chunk, score) in enumerate(results, 1):
        print(f"\n{i}. {chunk.title}")
        print(f"   URL: {chunk.url}")
        if chunk.heading:
            print(f"   Section: {chunk.heading}")
        print(f"   Score: {score:.4f}")
        print(f"   Text preview: {chunk.text[:200]}...")
    print("\n" + "="*60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Website Chatbot - Grounded Q&A with indexed website content'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Index command
    index_parser = subparsers.add_parser('index', help='Index a website')
    index_parser.add_argument('--url', type=str, help='Website URL to index')
    index_parser.add_argument('--depth', type=int, help='Maximum crawl depth')
    index_parser.add_argument('--max-pages', type=int, help='Maximum pages to crawl')
    index_parser.add_argument('--no-js', dest='js', action='store_false', 
                            help='Use standard crawler instead of JavaScript-aware crawler')
    index_parser.set_defaults(js=True)
    
    # Chat command
    chat_parser = subparsers.add_parser('chat', help='Run interactive chatbot')
    
    # Test search command
    test_parser = subparsers.add_parser('test', help='Test search functionality')
    test_parser.add_argument('--query', type=str, help='Search query')
    
    args = parser.parse_args()
    
    if args.command == 'index':
        asyncio.run(index_website(args))
    elif args.command == 'chat':
        asyncio.run(run_chatbot(args))
    elif args.command == 'test':
        asyncio.run(test_search(args))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
