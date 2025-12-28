"""Tests for Web Crawler Stage 3 - Rate Limiting"""
import pytest
import time
from solution import WebCrawler


class TestWebCrawlerStage3:
    def test_max_per_domain(self):
        pages = {f"http://example.com/p{i}":
                 f'<a href="/p{i+1}">Next</a>' for i in range(10)}
        crawler = WebCrawler(lambda url: pages.get(url, ""), max_per_domain=3)
        result = crawler.crawl("http://example.com/p0", max_pages=10)

        assert len(result) == 3

    def test_domain_isolation(self):
        pages = {
            "http://a.com": '<a href="http://b.com">B</a><a href="/p1">P1</a>',
            "http://a.com/p1": '<a href="/p2">P2</a>',
            "http://a.com/p2": "",
            "http://b.com": '<a href="/q1">Q1</a>',
            "http://b.com/q1": '<a href="/q2">Q2</a>',
            "http://b.com/q2": "",
        }
        crawler = WebCrawler(lambda url: pages.get(url, ""), max_per_domain=2)
        result = crawler.crawl("http://a.com", max_pages=10)

        a_count = sum(1 for url in result if "a.com" in url)
        b_count = sum(1 for url in result if "b.com" in url)

        assert a_count <= 2
        assert b_count <= 2

    def test_delay_between_requests(self):
        pages = {
            "http://example.com": '<a href="/p1">P1</a>',
            "http://example.com/p1": "",
        }
        crawler = WebCrawler(lambda url: pages.get(url, ""), delay=0.1)

        start = time.time()
        crawler.crawl("http://example.com")
        elapsed = time.time() - start

        # Should have at least one delay
        assert elapsed >= 0.1

    def test_request_count(self):
        pages = {
            "http://example.com": '<a href="/p1">P1</a>',
            "http://example.com/p1": '<a href="/p2">P2</a>',
            "http://example.com/p2": "",
        }
        crawler = WebCrawler(lambda url: pages.get(url, ""))
        crawler.crawl("http://example.com")

        assert crawler.request_count() == 3

    def test_domain_request_count(self):
        pages = {
            "http://a.com": '<a href="http://b.com">B</a><a href="/p1">P1</a>',
            "http://a.com/p1": "",
            "http://b.com": "",
        }
        crawler = WebCrawler(lambda url: pages.get(url, ""))
        crawler.crawl("http://a.com")

        assert crawler.domain_request_count("a.com") == 2
        assert crawler.domain_request_count("b.com") == 1

    def test_reset_clears_counts(self):
        pages = {"http://example.com": ""}
        crawler = WebCrawler(lambda url: pages.get(url, ""))
        crawler.crawl("http://example.com")
        crawler.reset()

        assert crawler.request_count() == 0
        assert crawler.domain_request_count("example.com") == 0

    def test_excluded_when_over_limit(self):
        pages = {f"http://example.com/p{i}":
                 f'<a href="/p{i+1}">Next</a>' for i in range(5)}
        crawler = WebCrawler(lambda url: pages.get(url, ""), max_per_domain=2)
        crawler.crawl("http://example.com/p0", max_pages=10)

        assert crawler.excluded_count() >= 2
