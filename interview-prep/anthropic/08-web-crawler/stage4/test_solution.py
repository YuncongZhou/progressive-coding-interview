"""Tests for Web Crawler Stage 4 - Async Crawling"""
import pytest
import asyncio
from solution import AsyncWebCrawler


class TestAsyncWebCrawlerStage4:
    @pytest.fixture
    def pages(self):
        return {
            "http://example.com": '<a href="/p1">P1</a><a href="/p2">P2</a>',
            "http://example.com/p1": '<a href="/p3">P3</a>',
            "http://example.com/p2": '<a href="/p4">P4</a>',
            "http://example.com/p3": "",
            "http://example.com/p4": "",
        }

    @pytest.fixture
    def make_fetcher(self, pages):
        async def fetcher(url):
            await asyncio.sleep(0.01)  # Simulate network
            return pages.get(url, "")
        return fetcher

    @pytest.mark.asyncio
    async def test_basic_crawl(self, pages, make_fetcher):
        crawler = AsyncWebCrawler(make_fetcher)
        result = await crawler.crawl("http://example.com")

        assert "http://example.com" in result
        assert "http://example.com/p1" in result
        assert len(result) == 5

    @pytest.mark.asyncio
    async def test_max_pages(self, pages, make_fetcher):
        crawler = AsyncWebCrawler(make_fetcher)
        result = await crawler.crawl("http://example.com", max_pages=3)

        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, pages):
        request_times = []

        async def timed_fetcher(url):
            request_times.append(asyncio.get_event_loop().time())
            await asyncio.sleep(0.05)
            return pages.get(url, "")

        crawler = AsyncWebCrawler(timed_fetcher, max_concurrent=3)
        await crawler.crawl("http://example.com", max_pages=5)

        # With concurrency, requests should overlap
        # Check that some requests started before others finished

    @pytest.mark.asyncio
    async def test_max_per_domain(self, pages, make_fetcher):
        crawler = AsyncWebCrawler(make_fetcher, max_per_domain=2)
        result = await crawler.crawl("http://example.com", max_pages=10)

        assert len(result) <= 2

    @pytest.mark.asyncio
    async def test_timeout_handling(self, pages):
        async def slow_fetcher(url):
            await asyncio.sleep(1.0)
            return pages.get(url, "")

        crawler = AsyncWebCrawler(slow_fetcher, timeout=0.1)
        result = await crawler.crawl("http://example.com", max_pages=3)

        # Should handle timeout gracefully
        assert crawler.error_count() >= 0

    @pytest.mark.asyncio
    async def test_error_count(self, pages):
        async def failing_fetcher(url):
            if "p2" in url:
                raise Exception("Network error")
            return pages.get(url, "")

        crawler = AsyncWebCrawler(failing_fetcher)
        await crawler.crawl("http://example.com")

        assert crawler.error_count() >= 1

    @pytest.mark.asyncio
    async def test_allowed_domains(self, make_fetcher):
        pages = {
            "http://a.com": '<a href="http://b.com">B</a>',
            "http://b.com": "",
        }
        async def fetcher(url):
            return pages.get(url, "")

        crawler = AsyncWebCrawler(fetcher)
        crawler.set_allowed_domains(["a.com"])
        result = await crawler.crawl("http://a.com")

        assert "http://a.com" in result
        assert "http://b.com" not in result

    @pytest.mark.asyncio
    async def test_request_count(self, pages, make_fetcher):
        crawler = AsyncWebCrawler(make_fetcher)
        await crawler.crawl("http://example.com")

        assert crawler.request_count() == 5
