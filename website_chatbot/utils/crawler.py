"""
Website crawler module for indexing entire websites.
Crawls all pages from a given URL up to a specified depth.
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Set, List, Dict
import logging
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WebPage:
    """Represents a crawled web page."""
    url: str
    title: str
    content: str
    headings: List[str]
    links: List[str]


class WebsiteCrawler:
    """Crawls and indexes an entire website."""
    
    def __init__(
        self, 
        base_url: str, 
        max_depth: int = 3, 
        max_pages: int = 100,
        delay: float = 0.5
    ):
        """
        Initialize the website crawler.
        
        Args:
            base_url: The starting URL to crawl
            max_depth: Maximum depth to crawl from base URL
            max_pages: Maximum number of pages to crawl
            delay: Delay between requests in seconds
        """
        self.base_url = base_url
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.delay = delay
        self.visited_urls: Set[str] = set()
        self.pages: List[WebPage] = []
        self.domain = urlparse(base_url).netloc
        
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and belongs to the same domain."""
        try:
            parsed = urlparse(url)
            # Only crawl URLs from the same domain
            if parsed.netloc != self.domain:
                return False
            # Skip non-HTTP(S) URLs
            if parsed.scheme not in ['http', 'https']:
                return False
            # Skip common file extensions
            skip_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.exe']
            if any(url.lower().endswith(ext) for ext in skip_extensions):
                return False
            return True
        except Exception:
            return False
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract clean text content from HTML."""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_headings(self, soup: BeautifulSoup) -> List[str]:
        """Extract all headings from the page."""
        headings = []
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            for heading in soup.find_all(tag):
                text = heading.get_text().strip()
                if text:
                    headings.append(text)
        return headings
    
    async def _fetch_page(self, session: aiohttp.ClientSession, url: str) -> tuple[str, BeautifulSoup]:
        """Fetch a single page and return its content."""
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    html = await response.text()
                    return html, BeautifulSoup(html, 'html.parser')
        except Exception as e:
            logger.warning(f"Error fetching {url}: {e}")
        return None, None
    
    async def _crawl_page(
        self, 
        session: aiohttp.ClientSession, 
        url: str, 
        depth: int
    ) -> List[str]:
        """
        Crawl a single page and extract its content and links.
        
        Returns:
            List of new URLs to crawl
        """
        if (url in self.visited_urls or 
            depth > self.max_depth or 
            len(self.pages) >= self.max_pages):
            return []
        
        self.visited_urls.add(url)
        logger.info(f"Crawling: {url} (depth: {depth}, pages: {len(self.pages)})")
        
        html, soup = await self._fetch_page(session, url)
        if not soup:
            return []
        
        # Extract page information
        title = soup.find('title').get_text().strip() if soup.find('title') else url
        content = self._extract_text_content(soup)
        headings = self._extract_headings(soup)
        
        # Extract all links
        links = []
        new_urls = []
        for link in soup.find_all('a', href=True):
            absolute_url = urljoin(url, link['href'])
            # Remove fragments
            absolute_url = absolute_url.split('#')[0]
            links.append(absolute_url)
            
            if (self._is_valid_url(absolute_url) and 
                absolute_url not in self.visited_urls and
                len(self.pages) < self.max_pages):
                new_urls.append(absolute_url)
        
        # Store page data
        page = WebPage(
            url=url,
            title=title,
            content=content,
            headings=headings,
            links=list(set(links))
        )
        self.pages.append(page)
        
        # Add delay to be respectful
        await asyncio.sleep(self.delay)
        
        return new_urls
    
    async def crawl(self) -> List[WebPage]:
        """
        Crawl the website starting from base_url.
        
        Returns:
            List of WebPage objects
        """
        logger.info(f"Starting crawl of {self.base_url}")
        
        async with aiohttp.ClientSession() as session:
            # Start with the base URL
            urls_to_crawl = [(self.base_url, 0)]  # (url, depth)
            
            while urls_to_crawl and len(self.pages) < self.max_pages:
                url, depth = urls_to_crawl.pop(0)
                
                if url in self.visited_urls:
                    continue
                
                new_urls = await self._crawl_page(session, url, depth)
                
                # Add new URLs with incremented depth
                for new_url in new_urls:
                    if new_url not in self.visited_urls:
                        urls_to_crawl.append((new_url, depth + 1))
        
        logger.info(f"Crawl complete. Indexed {len(self.pages)} pages")
        return self.pages


async def main():
    """Example usage of the crawler."""
    crawler = WebsiteCrawler(
        base_url="https://example.com",
        max_depth=2,
        max_pages=50
    )
    
    pages = await crawler.crawl()
    
    print(f"\nCrawled {len(pages)} pages:")
    for page in pages[:5]:  # Show first 5
        print(f"  - {page.title} ({page.url})")
        print(f"    Content length: {len(page.content)} chars")
        print(f"    Headings: {len(page.headings)}")


if __name__ == "__main__":
    asyncio.run(main())
