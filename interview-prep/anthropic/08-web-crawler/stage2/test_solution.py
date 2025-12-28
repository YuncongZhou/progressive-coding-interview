"""Tests for Web Crawler Stage 2 - Domain Filtering"""
import pytest
from solution import WebCrawler


class TestWebCrawlerStage2:
    def test_allowed_domains(self):
        pages = {
            "http://example.com": '<a href="http://other.com">External</a>',
            "http://other.com": "Other site",
        }
        crawler = WebCrawler(lambda url: pages.get(url, ""))
        crawler.set_allowed_domains(["example.com"])
        result = crawler.crawl("http://example.com")

        assert "http://example.com" in result
        assert "http://other.com" not in result

    def test_multiple_allowed_domains(self):
        pages = {
            "http://a.com": '<a href="http://b.com">B</a>',
            "http://b.com": '<a href="http://c.com">C</a>',
            "http://c.com": "C site",
        }
        crawler = WebCrawler(lambda url: pages.get(url, ""))
        crawler.set_allowed_domains(["a.com", "b.com"])
        result = crawler.crawl("http://a.com")

        assert "http://a.com" in result
        assert "http://b.com" in result
        assert "http://c.com" not in result

    def test_robots_rules(self):
        pages = {
            "http://example.com": '<a href="/private/data">Private</a>',
            "http://example.com/private/data": "Secret",
            "http://example.com/public": "Public",
        }
        crawler = WebCrawler(lambda url: pages.get(url, ""))
        crawler.add_robots_rules("example.com", ["/private/"])
        result = crawler.crawl("http://example.com")

        assert "http://example.com" in result
        assert "http://example.com/private/data" not in result

    def test_excluded_count(self):
        pages = {
            "http://example.com": '''
                <a href="http://other.com">External</a>
                <a href="/page1">Internal</a>
            ''',
            "http://example.com/page1": "",
        }
        crawler = WebCrawler(lambda url: pages.get(url, ""))
        crawler.set_allowed_domains(["example.com"])
        crawler.crawl("http://example.com")

        assert crawler.excluded_count() == 1

    def test_get_excluded(self):
        pages = {
            "http://example.com": '<a href="http://other.com">External</a>',
        }
        crawler = WebCrawler(lambda url: pages.get(url, ""))
        crawler.set_allowed_domains(["example.com"])
        crawler.crawl("http://example.com")

        excluded = crawler.get_excluded()
        assert "http://other.com" in excluded

    def test_no_domain_filter(self):
        pages = {
            "http://a.com": '<a href="http://b.com">B</a>',
            "http://b.com": "",
        }
        crawler = WebCrawler(lambda url: pages.get(url, ""))
        result = crawler.crawl("http://a.com")

        assert "http://a.com" in result
        assert "http://b.com" in result

    def test_robots_exact_match(self):
        pages = {
            "http://example.com": '''
                <a href="/admin">Admin</a>
                <a href="/admin-public">Admin Public</a>
            ''',
            "http://example.com/admin": "",
            "http://example.com/admin-public": "",
        }
        crawler = WebCrawler(lambda url: pages.get(url, ""))
        crawler.add_robots_rules("example.com", ["/admin"])
        result = crawler.crawl("http://example.com")

        assert "http://example.com/admin" not in result
        assert "http://example.com/admin-public" not in result
