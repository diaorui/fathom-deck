"""Centralized HTTP client with automatic caching, retries, and request management."""

import hashlib
import json
import requests
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple, Literal
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError


class URLCache:
    """In-memory cache for HTTP responses during single workflow run.

    Prevents fetching the same URL multiple times when multiple widgets
    request the same endpoint (e.g., multiple coins from same API).
    """

    def __init__(self, ttl_seconds: int = 180):  # 3 minute TTL
        self.cache: Dict[str, Tuple[Any, datetime]] = {}
        self.ttl = timedelta(seconds=ttl_seconds)

    def get(self, cache_key: str) -> Optional[Any]:
        """Get cached response for cache key if still valid."""
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.ttl:
                return data
            else:
                del self.cache[cache_key]  # Expired, remove it
        return None

    def set(self, cache_key: str, data: Any):
        """Cache response data for cache key."""
        self.cache[cache_key] = (data, datetime.now())

    def clear(self):
        """Clear all cached data."""
        self.cache.clear()

    def stats(self) -> Dict[str, int]:
        """Return cache statistics."""
        return {
            "total_entries": len(self.cache),
            "valid_entries": sum(
                1 for _, (_, ts) in self.cache.items()
                if datetime.now() - ts < self.ttl
            )
        }


class HTTPClient:
    """Centralized HTTP client with automatic caching, retries, and consistent error handling.

    Benefits:
    - Automatic cache key generation from URL + params
    - Built-in retry logic with exponential backoff
    - Consistent logging across all requests
    - Support for JSON, text, and binary responses
    - Configurable timeouts and headers
    - Widget-agnostic interface

    Example usage:
        client = get_http_client()

        # Simple JSON request
        data = client.get("https://api.example.com/data")

        # With query parameters
        data = client.get(
            "https://api.example.com/search",
            params={"q": "bitcoin", "limit": 10}
        )

        # With custom headers and timeout
        data = client.get(
            "https://api.example.com/data",
            headers={"Authorization": "Bearer token"},
            timeout=30,
            response_type="text"
        )
    """

    def __init__(
        self,
        cache: Optional[URLCache] = None,
        default_timeout: int = 10,
        default_user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        max_retries: int = 3,
        retry_min_wait: int = 2,
        retry_max_wait: int = 10,
    ):
        """Initialize HTTP client.

        Args:
            cache: URLCache instance (creates new one if not provided)
            default_timeout: Default request timeout in seconds
            default_user_agent: Default User-Agent header
            max_retries: Maximum number of retry attempts
            retry_min_wait: Minimum wait time between retries (seconds)
            retry_max_wait: Maximum wait time between retries (seconds)
        """
        self.cache = cache or URLCache()
        self.default_timeout = default_timeout
        self.default_user_agent = default_user_agent
        self.max_retries = max_retries
        self.retry_min_wait = retry_min_wait
        self.retry_max_wait = retry_max_wait

        # Statistics
        self.stats_requests = 0
        self.stats_cache_hits = 0
        self.stats_cache_misses = 0

    def _generate_cache_key(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> str:
        """Generate consistent cache key from URL, params, and relevant headers.

        Cache key includes:
        - URL
        - Sorted query parameters
        - Authorization headers (if present)

        This ensures the same request always generates the same cache key.
        """
        key_parts = [url]

        # Add sorted params
        if params:
            sorted_params = "&".join(
                f"{k}={v}" for k, v in sorted(params.items())
            )
            key_parts.append(sorted_params)

        # Add auth headers (they affect response content)
        if headers:
            auth_headers = {
                k: v for k, v in headers.items()
                if k.lower() in ("authorization", "api-key", "x-api-key")
            }
            if auth_headers:
                sorted_auth = "&".join(
                    f"{k}={v}" for k, v in sorted(auth_headers.items())
                )
                key_parts.append(sorted_auth)

        # Generate hash for long URLs
        cache_key = "|".join(key_parts)
        if len(cache_key) > 200:
            # Use hash for very long cache keys
            return hashlib.sha256(cache_key.encode()).hexdigest()

        return cache_key

    def _make_request(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> requests.Response:
        """Make HTTP request with retry logic.

        This method is decorated with @retry to handle transient failures.
        """
        # Merge with default headers
        final_headers = {"User-Agent": self.default_user_agent}
        if headers:
            final_headers.update(headers)

        # Use default timeout if not specified
        final_timeout = timeout or self.default_timeout

        # Make request
        response = requests.get(
            url,
            params=params,
            headers=final_headers,
            timeout=final_timeout
        )
        response.raise_for_status()

        return response

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        response_type: Literal["json", "text", "binary"] = "json",
        use_cache: bool = True,
    ) -> Any:
        """Make GET request with automatic caching and retry logic.

        Args:
            url: Target URL
            params: Query parameters
            headers: HTTP headers (merged with defaults)
            timeout: Request timeout in seconds (uses default if not specified)
            response_type: How to parse response ("json", "text", or "binary")
            use_cache: Whether to use cache (default: True)

        Returns:
            Parsed response data based on response_type

        Raises:
            requests.exceptions.RequestException: On HTTP errors after retries
            json.JSONDecodeError: If response_type="json" but response is not valid JSON
        """
        self.stats_requests += 1

        # Generate cache key
        cache_key = self._generate_cache_key(url, params, headers)

        # Check cache first
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                self.stats_cache_hits += 1
                print(f"✅ Cache hit: {url}")
                return cached

        self.stats_cache_misses += 1

        # Build full URL for logging
        full_url = url
        if params:
            param_str = "&".join(f"{k}={v}" for k, v in params.items())
            full_url = f"{url}?{param_str}"

        print(f"📡 Fetching: {full_url}")

        # Make request with retry logic
        try:
            # Apply retry decorator dynamically
            retrying_request = retry(
                stop=stop_after_attempt(self.max_retries),
                wait=wait_exponential(
                    multiplier=1,
                    min=self.retry_min_wait,
                    max=self.retry_max_wait
                ),
                reraise=True
            )(self._make_request)

            response = retrying_request(url, params, headers, timeout)

            # Parse response based on type
            if response_type == "json":
                data = response.json()
            elif response_type == "text":
                data = response.text
            elif response_type == "binary":
                data = response.content
            else:
                raise ValueError(f"Invalid response_type: {response_type}")

            # Cache successful response
            if use_cache:
                self.cache.set(cache_key, data)

            return data

        except RetryError as e:
            # All retries exhausted
            print(f"❌ Failed after {self.max_retries} retries: {url}")
            raise e.last_attempt.exception()
        except requests.exceptions.RequestException as e:
            print(f"❌ HTTP request failed: {url} - {e}")
            raise
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response from {url}: {e}")
            raise

    def clear_cache(self):
        """Clear all cached responses."""
        self.cache.clear()
        print("🗑️  Cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics."""
        cache_hit_rate = (
            (self.stats_cache_hits / self.stats_requests * 100)
            if self.stats_requests > 0
            else 0.0
        )

        return {
            "total_requests": self.stats_requests,
            "cache_hits": self.stats_cache_hits,
            "cache_misses": self.stats_cache_misses,
            "cache_hit_rate": f"{cache_hit_rate:.1f}%",
            **self.cache.stats()
        }


# Global instance for the workflow run
_http_client = HTTPClient()


def get_http_client() -> HTTPClient:
    """Get the global HTTP client instance."""
    return _http_client
