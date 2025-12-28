"""
Web Crawler - Stage 4

Concurrent crawling with async.

Design Rationale:
- Use asyncio for concurrent requests
- Limit concurrent connections
- Handle timeouts gracefully
"""

import asyncio
from typing import Set, List, Callable, Optional, Awaitable
from collections import defaultdict
import re


class AsyncWebCrawler:
    """Async web crawler with concurrency control."""

    def __init__(self, fetcher: Callable[[str], Awaitable[str]] = None,
                 max_concurrent: int = 5,
                 max_per_domain: int = 0,
                 timeout: float = 10.0):
        """
        Args:
            fetcher: Async function to fetch URL content
            max_concurrent: Max concurrent requests
            max_per_domain: Max requests per domain (0 = unlimited)
            timeout: Request timeout in seconds
        """
        self._fetcher = fetcher
        self._max_concurrent = max_concurrent
        self._max_per_domain = max_per_domain
        self._timeout = timeout
        self._visited: Set[str] = set()
        self._excluded: Set[str] = set()
        self._in_progress: Set[str] = set()
        self._allowed_domains: Set[str] = set()
        self._robots_rules: dict[str, List[str]] = {}
        self._domain_counts: dict[str, int] = defaultdict(int)
        self._request_count = 0
        self._error_count = 0

    def set_allowed_domains(self, domains: List[str]) -> None:
        self._allowed_domains = set(domains)

    def add_robots_rules(self, domain: str, disallowed: List[str]) -> None:
        self._robots_rules[domain] = disallowed

    async def crawl(self, start_url: str, max_pages: int = 100) -> List[str]:
        """Crawl concurrently."""
        queue = asyncio.Queue()
        await queue.put(start_url)
        result = []
        semaphore = asyncio.Semaphore(self._max_concurrent)

        async def process_url() -> bool:
            """Process a single URL. Returns True if should continue."""
            try:
                url = await asyncio.wait_for(queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                return False

            try:
                if url in self._visited or url in self._excluded or url in self._in_progress:
                    return True

                if not self._is_allowed(url):
                    self._excluded.add(url)
                    return True

                domain = self._get_domain(url)
                if self._max_per_domain > 0:
                    if self._domain_counts[domain] >= self._max_per_domain:
                        self._excluded.add(url)
                        return True

                self._in_progress.add(url)
                self._domain_counts[domain] += 1

                async with semaphore:
                    try:
                        content = await asyncio.wait_for(
                            self._fetcher(url),
                            timeout=self._timeout
                        )
                        self._request_count += 1

                        links = self.extract_links(content, url)
                        for link in links:
                            if (link not in self._visited and
                                link not in self._excluded and
                                link not in self._in_progress):
                                await queue.put(link)

                    except asyncio.TimeoutError:
                        self._error_count += 1
                    except Exception:
                        self._error_count += 1

                self._in_progress.discard(url)
                self._visited.add(url)
                result.append(url)
                return len(result) < max_pages

            except Exception:
                return True

        # Run workers
        while len(result) < max_pages:
            if queue.empty() and not self._in_progress:
                break
            should_continue = await process_url()
            if not should_continue and queue.empty():
                break

        return result

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

    def visited_count(self) -> int:
        return len(self._visited)

    def excluded_count(self) -> int:
        return len(self._excluded)

    def request_count(self) -> int:
        return self._request_count

    def error_count(self) -> int:
        """Number of failed requests."""
        return self._error_count

    def reset(self) -> None:
        self._visited.clear()
        self._excluded.clear()
        self._in_progress.clear()
        self._domain_counts.clear()
        self._request_count = 0
        self._error_count = 0
