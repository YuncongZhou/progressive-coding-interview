"""
Web Crawler - Stage 1

Basic web crawler with URL queue.

Design Rationale:
- Track visited URLs to avoid revisiting
- Extract links from pages
- Simple BFS traversal
"""

from typing import Set, List, Callable
from collections import deque
import re


class WebCrawler:
    """Basic web crawler."""

    def __init__(self, fetcher: Callable[[str], str] = None):
        """
        Args:
            fetcher: Function to fetch URL content (for testing)
        """
        self._fetcher = fetcher or self._default_fetcher
        self._visited: Set[str] = set()

    def crawl(self, start_url: str, max_pages: int = 100) -> List[str]:
        """
        Crawl starting from URL.

        Returns list of visited URLs.
        """
        queue = deque([start_url])
        result = []

        while queue and len(result) < max_pages:
            url = queue.popleft()

            if url in self._visited:
                continue

            self._visited.add(url)
            result.append(url)

            try:
                content = self._fetcher(url)
                links = self.extract_links(content, url)
                for link in links:
                    if link not in self._visited:
                        queue.append(link)
            except Exception:
                pass  # Skip failed fetches

        return result

    def extract_links(self, content: str, base_url: str) -> List[str]:
        """Extract links from HTML content."""
        # Simple regex for href attributes
        pattern = r'href=["\']([^"\']+)["\']'
        matches = re.findall(pattern, content)

        links = []
        for href in matches:
            absolute_url = self._resolve_url(href, base_url)
            if absolute_url:
                links.append(absolute_url)

        return links

    def _resolve_url(self, href: str, base_url: str) -> str | None:
        """Resolve relative URL to absolute."""
        if href.startswith(('http://', 'https://')):
            return href
        if href.startswith('/'):
            # Get domain from base URL
            match = re.match(r'(https?://[^/]+)', base_url)
            if match:
                return match.group(1) + href
        if not href.startswith(('#', 'javascript:', 'mailto:')):
            # Relative path
            base = base_url.rsplit('/', 1)[0]
            return f"{base}/{href}"
        return None

    def _default_fetcher(self, url: str) -> str:
        """Default fetcher (placeholder)."""
        raise NotImplementedError("Provide a fetcher function")

    def visited_count(self) -> int:
        """Return number of visited URLs."""
        return len(self._visited)

    def has_visited(self, url: str) -> bool:
        """Check if URL was visited."""
        return url in self._visited

    def reset(self) -> None:
        """Reset crawler state."""
        self._visited.clear()
