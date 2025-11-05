"""
Enhanced website crawler module for JavaScript-heavy websites (React, Vue, etc.).
Uses Playwright for rendering JavaScript content.
"""

import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Set, List, Dict
import logging
from dataclasses import dataclass
from playwright.async_api import async_playwright, Page, Browser

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


class JavaScriptWebsiteCrawler:
    """Crawls and indexes JavaScript-heavy websites using Playwright."""
    
    def __init__(
        self, 
        base_url: str, 
        max_depth: int = 3, 
        max_pages: int = 100,
        delay: float = 1.0,
        headless: bool = True
    ):
        """
        Initialize the website crawler.
        
        Args:
            base_url: The starting URL to crawl
            max_depth: Maximum depth to crawl from base URL
            max_pages: Maximum number of pages to crawl
            delay: Delay between requests in seconds
            headless: Run browser in headless mode
        """
        self.base_url = base_url
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.delay = delay
        self.headless = headless
        self.visited_urls: Set[str] = set()
        self.pages: List[WebPage] = []
        self.domain = urlparse(base_url).netloc
        
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and belongs to the same domain."""
        try:
            parsed = urlparse(url)
            # Only crawl URLs from the same domain
            if parsed.netloc and parsed.netloc != self.domain:
                return False
            # Skip non-HTTP(S) URLs
            if parsed.scheme and parsed.scheme not in ['http', 'https']:
                return False
            # Skip common file extensions
            skip_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.exe', '.mp4', '.mp3']
            if any(url.lower().endswith(ext) for ext in skip_extensions):
                return False
            # Skip anchors with just hash
            if url.startswith('#'):
                return False
            return True
        except Exception:
            return False
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract clean text content from HTML."""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header", "noscript"]):
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
                if text and len(text) > 1:  # Filter out empty or single-char headings
                    headings.append(text)
        return headings
    
    async def _wait_for_page_load(self, page: Page):
        """Wait for page to be fully loaded including dynamic content."""
        try:
            # Wait for network to be idle
            await page.wait_for_load_state("networkidle", timeout=10000)
            # Give extra time for React/Vue to render
            await asyncio.sleep(0.5)
        except Exception as e:
            logger.warning(f"Timeout waiting for page load: {e}")
    
    async def _extract_links(self, page: Page, current_url: str) -> List[str]:
        """Extract all links from the page."""
        links = []
        try:
            # Get all anchor tags
            link_elements = await page.query_selector_all('a[href]')
            
            for element in link_elements:
                try:
                    href = await element.get_attribute('href')
                    if href:
                        # Resolve relative URLs
                        absolute_url = urljoin(current_url, href)
                        # Remove fragments
                        absolute_url = absolute_url.split('#')[0]
                        
                        if self._is_valid_url(absolute_url):
                            links.append(absolute_url)
                except Exception:
                    continue
        except Exception as e:
            logger.warning(f"Error extracting links: {e}")
        
        return list(set(links))  # Remove duplicates
    
    async def _crawl_page(
        self, 
        page: Page,
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
        
        try:
            # Navigate to the page
            response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            if not response or response.status >= 400:
                logger.warning(f"Failed to load {url}: status {response.status if response else 'unknown'}")
                return []
            
            # Wait for page to fully load
            await self._wait_for_page_load(page)
            
            # Get the rendered HTML
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract page information
            title_element = await page.query_selector('title')
            title = await title_element.inner_text() if title_element else url
            
            content = self._extract_text_content(soup)
            headings = self._extract_headings(soup)
            
            # Extract all links
            links = await self._extract_links(page, url)
            
            # Filter new URLs to crawl
            new_urls = [
                link for link in links
                if link not in self.visited_urls and len(self.pages) < self.max_pages
            ]
            
            # Store page data
            page_data = WebPage(
                url=url,
                title=title.strip() if title else url,
                content=content,
                headings=headings,
                links=links
            )
            self.pages.append(page_data)
            
            logger.info(f"✓ Indexed: {title[:50]}... ({len(content)} chars, {len(headings)} headings, {len(new_urls)} new links)")
            
            # Add delay to be respectful
            await asyncio.sleep(self.delay)
            
            return new_urls
            
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            return []
    
    async def crawl(self) -> List[WebPage]:
        """
        Crawl the website starting from base_url using Playwright.
        
        Returns:
            List of WebPage objects
        """
        logger.info(f"Starting JavaScript-aware crawl of {self.base_url}")
        logger.info(f"Max depth: {self.max_depth}, Max pages: {self.max_pages}")
        
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            try:
                # Start with the base URL
                urls_to_crawl = [(self.base_url, 0)]  # (url, depth)
                
                while urls_to_crawl and len(self.pages) < self.max_pages:
                    url, depth = urls_to_crawl.pop(0)
                    
                    if url in self.visited_urls:
                        continue
                    
                    new_urls = await self._crawl_page(page, url, depth)
                    
                    # Add new URLs with incremented depth
                    for new_url in new_urls:
                        if new_url not in self.visited_urls:
                            urls_to_crawl.append((new_url, depth + 1))
                
            finally:
                await context.close()
                await browser.close()
        
        logger.info(f"Crawl complete. Indexed {len(self.pages)} pages")
        return self.pages


async def main():
    """Example usage of the crawler."""
    crawler = JavaScriptWebsiteCrawler(
        base_url="https://kandtconsultancy.com",
        max_depth=2,
        max_pages=50,
        delay=1.0,
        headless=True
    )
    
    pages = await crawler.crawl()
    
    print(f"\nCrawled {len(pages)} pages:")
    for page in pages:
        print(f"  - {page.title} ({page.url})")
        print(f"    Content length: {len(page.content)} chars")
        print(f"    Headings: {len(page.headings)}")
        print(f"    Links: {len(page.links)}")


if __name__ == "__main__":
    asyncio.run(main())
