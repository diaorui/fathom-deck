"""In-memory HTTP response cache for request deduplication within a single workflow run."""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple


class URLCache:
    """In-memory cache for HTTP responses during single workflow run.

    Prevents fetching the same URL multiple times when multiple widgets
    request the same endpoint (e.g., multiple coins from same API).
    """

    def __init__(self, ttl_seconds: int = 180):  # 3 minute TTL
        self.cache: Dict[str, Tuple[Any, datetime]] = {}
        self.ttl = timedelta(seconds=ttl_seconds)

    def get(self, url: str) -> Optional[Any]:
        """Get cached response for URL if still valid."""
        if url in self.cache:
            data, timestamp = self.cache[url]
            if datetime.now() - timestamp < self.ttl:
                return data
            else:
                del self.cache[url]  # Expired, remove it
        return None

    def set(self, url: str, data: Any):
        """Cache response data for URL."""
        self.cache[url] = (data, datetime.now())

    def clear(self):
        """Clear all cached data."""
        self.cache.clear()


# Global instance for the workflow run
_url_cache = URLCache()


def get_cached(url: str) -> Optional[Any]:
    """Get cached response for URL."""
    return _url_cache.get(url)


def cache_response(url: str, data: Any):
    """Cache response data for URL."""
    _url_cache.set(url, data)


def clear_cache():
    """Clear all cached responses."""
    _url_cache.clear()
