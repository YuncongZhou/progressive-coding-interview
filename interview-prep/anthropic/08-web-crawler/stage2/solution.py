"""
Web Crawler - Stage 2

Domain filtering and robots.txt.

Design Rationale:
- Respect robots.txt rules
- Filter by allowed domains
- Track excluded URLs
"""

from typing import Set, List, Callable, Optional
from collections import deque
import re


class WebCrawler:
    """Web crawler with domain filtering and robots.txt support."""

    def __init__(self, fetcher: Callable[[str], str] = None):
        self._fetcher = fetcher or self._default_fetcher
        self._visited: Set[str] = set()
        self._excluded: Set[str] = set()
        self._allowed_domains: Set[str] = set()
        self._robots_rules: dict[str, List[str]] = {}  # domain -> disallowed paths

    def set_allowed_domains(self, domains: List[str]) -> None:
        """Set domains that can be crawled."""
        self._allowed_domains = set(domains)

    def add_robots_rules(self, domain: str, disallowed: List[str]) -> None:
        """Add robots.txt rules for a domain."""
        self._robots_rules[domain] = disallowed

    def crawl(self, start_url: str, max_pages: int = 100) -> List[str]:
        """Crawl starting from URL."""
        queue = deque([start_url])
        result = []

        while queue and len(result) < max_pages:
            url = queue.popleft()

            if url in self._visited or url in self._excluded:
                continue

            if not self._is_allowed(url):
                self._excluded.add(url)
                continue

            self._visited.add(url)
            result.append(url)

            try:
                content = self._fetcher(url)
                links = self.extract_links(content, url)
                for link in links:
                    if link not in self._visited and link not in self._excluded:
                        queue.append(link)
            except Exception:
                pass

        return result

    def _is_allowed(self, url: str) -> bool:
        """Check if URL is allowed to be crawled."""
        domain = self._get_domain(url)
        path = self._get_path(url)

        # Check domain filter
        if self._allowed_domains and domain not in self._allowed_domains:
            return False

        # Check robots.txt rules
        if domain in self._robots_rules:
            for disallowed in self._robots_rules[domain]:
                if path.startswith(disallowed):
                    return False

        return True

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        match = re.match(r'https?://([^/]+)', url)
        return match.group(1) if match else ""

    def _get_path(self, url: str) -> str:
        """Extract path from URL."""
        match = re.match(r'https?://[^/]+(.*)', url)
        return match.group(1) if match else "/"

    def extract_links(self, content: str, base_url: str) -> List[str]:
        """Extract links from HTML content."""
        pattern = r'href=["\']([^"\']+)["\']'
        matches = re.findall(pattern, content)

        links = []
        for href in matches:
            absolute_url = self._resolve_url(href, base_url)
            if absolute_url:
                links.append(absolute_url)

        return links

    def _resolve_url(self, href: str, base_url: str) -> Optional[str]:
        """Resolve relative URL to absolute."""
        if href.startswith(('http://', 'https://')):
            return href
        if href.startswith('/'):
            match = re.match(r'(https?://[^/]+)', base_url)
            if match:
                return match.group(1) + href
        if not href.startswith(('#', 'javascript:', 'mailto:')):
            base = base_url.rsplit('/', 1)[0]
            return f"{base}/{href}"
        return None

    def _default_fetcher(self, url: str) -> str:
        raise NotImplementedError("Provide a fetcher function")

    def visited_count(self) -> int:
        return len(self._visited)

    def excluded_count(self) -> int:
        """Return number of excluded URLs."""
        return len(self._excluded)

    def get_excluded(self) -> List[str]:
        """Get list of excluded URLs."""
        return sorted(self._excluded)

    def has_visited(self, url: str) -> bool:
        return url in self._visited

    def reset(self) -> None:
        self._visited.clear()
        self._excluded.clear()
