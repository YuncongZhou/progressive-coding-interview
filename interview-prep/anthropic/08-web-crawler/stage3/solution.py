"""
Web Crawler - Stage 3

Rate limiting and politeness.

Design Rationale:
- Limit requests per domain
- Add delays between requests
- Track request timing
"""

from typing import Set, List, Callable, Optional
from collections import deque, defaultdict
import re
import time


class WebCrawler:
    """Web crawler with rate limiting."""

    def __init__(self, fetcher: Callable[[str], str] = None,
                 delay: float = 0.0, max_per_domain: int = 0):
        """
        Args:
            fetcher: Function to fetch URL content
            delay: Delay between requests in seconds
            max_per_domain: Max requests per domain (0 = unlimited)
        """
        self._fetcher = fetcher or self._default_fetcher
        self._delay = delay
        self._max_per_domain = max_per_domain
        self._visited: Set[str] = set()
        self._excluded: Set[str] = set()
        self._allowed_domains: Set[str] = set()
        self._robots_rules: dict[str, List[str]] = {}
        self._domain_counts: dict[str, int] = defaultdict(int)
        self._last_request_time: dict[str, float] = {}
        self._request_count = 0

    def set_allowed_domains(self, domains: List[str]) -> None:
        self._allowed_domains = set(domains)

    def add_robots_rules(self, domain: str, disallowed: List[str]) -> None:
        self._robots_rules[domain] = disallowed

    def crawl(self, start_url: str, max_pages: int = 100) -> List[str]:
        """Crawl with rate limiting."""
        queue = deque([start_url])
        result = []

        while queue and len(result) < max_pages:
            url = queue.popleft()

            if url in self._visited or url in self._excluded:
                continue

            if not self._is_allowed(url):
                self._excluded.add(url)
                continue

            domain = self._get_domain(url)

            # Check domain limit
            if self._max_per_domain > 0:
                if self._domain_counts[domain] >= self._max_per_domain:
                    self._excluded.add(url)
                    continue

            # Apply rate limiting delay
            self._wait_for_domain(domain)

            self._visited.add(url)
            self._domain_counts[domain] += 1
            self._last_request_time[domain] = time.time()
            self._request_count += 1
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

    def _wait_for_domain(self, domain: str) -> None:
        """Wait if needed to respect rate limit."""
        if self._delay <= 0:
            return

        last_time = self._last_request_time.get(domain)
        if last_time is not None:
            elapsed = time.time() - last_time
            if elapsed < self._delay:
                time.sleep(self._delay - elapsed)

    def _is_allowed(self, url: str) -> bool:
        domain = self._get_domain(url)
        path = self._get_path(url)

        if self._allowed_domains and domain not in self._allowed_domains:
            return False

        if domain in self._robots_rules:
            for disallowed in self._robots_rules[domain]:
                if path.startswith(disallowed):
                    return False

        return True

    def _get_domain(self, url: str) -> str:
        match = re.match(r'https?://([^/]+)', url)
        return match.group(1) if match else ""

    def _get_path(self, url: str) -> str:
        match = re.match(r'https?://[^/]+(.*)', url)
        return match.group(1) if match else "/"

    def extract_links(self, content: str, base_url: str) -> List[str]:
        pattern = r'href=["\']([^"\']+)["\']'
        matches = re.findall(pattern, content)

        links = []
        for href in matches:
            absolute_url = self._resolve_url(href, base_url)
            if absolute_url:
                links.append(absolute_url)

        return links

    def _resolve_url(self, href: str, base_url: str) -> Optional[str]:
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
        return len(self._excluded)

    def request_count(self) -> int:
        """Total number of requests made."""
        return self._request_count

    def domain_request_count(self, domain: str) -> int:
        """Requests made to specific domain."""
        return self._domain_counts.get(domain, 0)

    def reset(self) -> None:
        self._visited.clear()
        self._excluded.clear()
        self._domain_counts.clear()
        self._last_request_time.clear()
        self._request_count = 0
