"""Tests for Web Crawler Stage 1"""
import pytest
from solution import WebCrawler


class TestWebCrawlerStage1:
    def test_basic_crawl(self):
        pages = {
            "http://example.com": '<a href="/page1">Link</a>',
            "http://example.com/page1": '<a href="/page2">Link</a>',
            "http://example.com/page2": "No links",
        }
        crawler = WebCrawler(lambda url: pages.get(url, ""))
        result = crawler.crawl("http://example.com")

        assert "http://example.com" in result
        assert "http://example.com/page1" in result
        assert "http://example.com/page2" in result

    def test_max_pages(self):
        pages = {f"http://example.com/p{i}":
                 f'<a href="/p{i+1}">Next</a>' for i in range(20)}
        crawler = WebCrawler(lambda url: pages.get(url, ""))
        result = crawler.crawl("http://example.com/p0", max_pages=5)

        assert len(result) == 5

    def test_no_duplicate_visits(self):
        pages = {
            "http://example.com": '<a href="/page1">Link</a>',
            "http://example.com/page1":
                '<a href="/">Home</a><a href="/page1">Self</a>',
        }
        crawler = WebCrawler(lambda url: pages.get(url, ""))
        result = crawler.crawl("http://example.com")

        assert result.count("http://example.com") == 1
        assert result.count("http://example.com/page1") == 1

    def test_extract_links(self):
        crawler = WebCrawler()
        content = '''
        <a href="http://other.com">External</a>
        <a href="/path">Absolute</a>
        <a href="relative.html">Relative</a>
        '''
        links = crawler.extract_links(content, "http://example.com/page")

        assert "http://other.com" in links
        assert "http://example.com/path" in links
        assert "http://example.com/relative.html" in links

    def test_skip_javascript_links(self):
        crawler = WebCrawler()
        content = '<a href="javascript:void(0)">Click</a>'
        links = crawler.extract_links(content, "http://example.com")
        assert len(links) == 0

    def test_visited_count(self):
        pages = {
            "http://example.com": '<a href="/page1">Link</a>',
            "http://example.com/page1": "",
        }
        crawler = WebCrawler(lambda url: pages.get(url, ""))
        crawler.crawl("http://example.com")

        assert crawler.visited_count() == 2

    def test_has_visited(self):
        pages = {"http://example.com": ""}
        crawler = WebCrawler(lambda url: pages.get(url, ""))
        crawler.crawl("http://example.com")

        assert crawler.has_visited("http://example.com") is True
        assert crawler.has_visited("http://other.com") is False

    def test_reset(self):
        pages = {"http://example.com": ""}
        crawler = WebCrawler(lambda url: pages.get(url, ""))
        crawler.crawl("http://example.com")
        crawler.reset()

        assert crawler.visited_count() == 0

    def test_handles_fetch_error(self):
        def failing_fetcher(url):
            if "fail" in url:
                raise Exception("Network error")
            return '<a href="/fail">Bad</a>'

        crawler = WebCrawler(failing_fetcher)
        result = crawler.crawl("http://example.com")
        # Should complete without error
        assert "http://example.com" in result
