"""
News aggregator module.

Collects financial news from various sources.
"""

import feedparser
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

from src.data_collection.cache_manager import CacheManager
from src.utils.config import get_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class NewsAggregator:
    """Aggregator for financial news."""

    def __init__(self, cache_manager: Optional[CacheManager] = None):
        """
        Initialize news aggregator.

        Args:
            cache_manager: Optional cache manager instance.
        """
        self.cache = cache_manager or CacheManager()
        config = get_config()
        self.newsapi_key = config.get("newsapi.api_key", None)

    def fetch_alpha_vantage_news(
        self,
        symbols: Optional[List[str]] = None,
        limit: int = 50,
        use_cache: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Fetch news from Alpha Vantage News API.

        Args:
            symbols: Optional list of stock symbols to filter news.
            limit: Maximum number of news items to fetch.
            use_cache: Whether to use cached data.

        Returns:
            List of news articles.
        """
        cache_key = f"news_alphavantage_{'_'.join(symbols or [])}_{limit}"

        if use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                logger.debug("Using cached Alpha Vantage news")
                return cached_data

        # Note: Alpha Vantage News API requires premium subscription
        # This is a placeholder implementation
        logger.warning("Alpha Vantage News API requires premium subscription")
        return []

    def fetch_newsapi_news(
        self,
        query: str = "finance",
        language: str = "en",
        sort_by: str = "publishedAt",
        limit: int = 50,
        use_cache: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Fetch news from NewsAPI.

        Args:
            query: Search query.
            language: Language code.
            sort_by: Sort order ('relevancy', 'popularity', 'publishedAt').
            limit: Maximum number of articles.
            use_cache: Whether to use cached data.

        Returns:
            List of news articles.
        """
        if not self.newsapi_key:
            logger.warning("NewsAPI key not configured")
            return []

        cache_key = f"news_newsapi_{query}_{limit}"

        if use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                logger.debug("Using cached NewsAPI news")
                return cached_data

        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "language": language,
                "sortBy": sort_by,
                "pageSize": min(limit, 100),  # NewsAPI max is 100
                "apiKey": self.newsapi_key,
            }

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            articles = data.get("articles", [])

            # Format articles
            formatted_articles = []
            for article in articles:
                formatted_articles.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "content": article.get("content", ""),
                    "url": article.get("url", ""),
                    "source": article.get("source", {}).get("name", ""),
                    "author": article.get("author", ""),
                    "published_at": article.get("publishedAt", ""),
                    "url_to_image": article.get("urlToImage", ""),
                })

            if use_cache:
                self.cache.set(cache_key, formatted_articles, ttl=3600)  # 1 hour TTL

            logger.info(f"Fetched {len(formatted_articles)} news articles")
            return formatted_articles

        except Exception as e:
            logger.error(f"Failed to fetch NewsAPI news: {e}")
            return []

    def fetch_rss_feed(
        self,
        feed_url: str,
        limit: int = 50,
        use_cache: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Fetch news from RSS feed.

        Args:
            feed_url: URL of the RSS feed.
            limit: Maximum number of items to fetch.
            use_cache: Whether to use cached data.

        Returns:
            List of news articles.
        """
        cache_key = f"news_rss_{feed_url}_{limit}"

        if use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                logger.debug(f"Using cached RSS feed: {feed_url}")
                return cached_data

        try:
            feed = feedparser.parse(feed_url)

            articles = []
            for entry in feed.entries[:limit]:
                articles.append({
                    "title": entry.get("title", ""),
                    "description": entry.get("description", ""),
                    "summary": entry.get("summary", ""),
                    "link": entry.get("link", ""),
                    "published_at": entry.get("published", ""),
                    "author": entry.get("author", ""),
                })

            if use_cache:
                self.cache.set(cache_key, articles, ttl=1800)  # 30 min TTL

            logger.info(f"Fetched {len(articles)} articles from RSS feed")
            return articles

        except Exception as e:
            logger.error(f"Failed to fetch RSS feed {feed_url}: {e}")
            return []

    def aggregate_news(
        self,
        symbols: Optional[List[str]] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Aggregate news from multiple sources.

        Args:
            symbols: Optional list of stock symbols.
            limit: Maximum number of articles per source.

        Returns:
            Combined list of news articles.
        """
        all_articles = []

        # Fetch from NewsAPI
        query = "finance"
        if symbols:
            query = " OR ".join(symbols)
        newsapi_articles = self.fetch_newsapi_news(query=query, limit=limit)
        all_articles.extend(newsapi_articles)

        # Fetch from Alpha Vantage (if available)
        alphavantage_articles = self.fetch_alpha_vantage_news(symbols=symbols, limit=limit)
        all_articles.extend(alphavantage_articles)

        # Remove duplicates based on title
        seen_titles = set()
        unique_articles = []
        for article in all_articles:
            title = article.get("title", "").lower()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_articles.append(article)

        logger.info(f"Aggregated {len(unique_articles)} unique news articles")
        return unique_articles

