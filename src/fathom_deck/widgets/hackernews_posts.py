"""HackerNews posts widget using Algolia Search API."""

import requests
from datetime import datetime
from typing import Any, Dict, List
from tenacity import retry, stop_after_attempt, wait_exponential

from ..core.base_widget import BaseWidget
from ..core.http_cache import get_cached, cache_response


class HackernewsPostsWidget(BaseWidget):
    """Displays recent posts from HackerNews search.

    Required params:
        - query: Search query (e.g., "bitcoin", "ai", "python")

    Optional params:
        - limit: Number of posts to show (default: 8)
        - min_points: Minimum points threshold for quality filter (default: 10)
        - sort_by: Sort order - "date" or "relevance" (default: "date")
    """

    def get_required_params(self) -> list[str]:
        return ["query"]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def _fetch_from_hackernews(self, query: str, limit: int, min_points: int, sort_by: str) -> Dict:
        """Fetch posts from HackerNews Algolia API."""
        # Choose endpoint based on sort order
        if sort_by == "relevance":
            base_url = "https://hn.algolia.com/api/v1/search"
        else:  # default to date
            base_url = "https://hn.algolia.com/api/v1/search_by_date"

        params = {
            "query": query,
            "tags": "story",
            "hitsPerPage": limit,
        }

        # Add numeric filter for minimum points
        if min_points > 0:
            params["numericFilters"] = f"points>{min_points}"

        # Build cache key from params
        cache_key = f"{base_url}?{'&'.join(f'{k}={v}' for k, v in sorted(params.items()))}"
        cached = get_cached(cache_key)
        if cached:
            print(f"✅ Cache hit: {cache_key}")
            return cached

        print(f"📡 Fetching: {base_url}")
        headers = {
            "User-Agent": "fathom-deck/1.0.0"
        }
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Cache the response
        cache_response(cache_key, data)
        return data

    def fetch_data(self) -> Dict[str, Any]:
        """Fetch recent posts from HackerNews."""
        self.validate_params()

        query = self.merged_params["query"]
        limit = self.merged_params.get("limit", 8)
        min_points = self.merged_params.get("min_points", 10)
        sort_by = self.merged_params.get("sort_by", "date")

        try:
            hn_data = self._fetch_from_hackernews(query, limit, min_points, sort_by)

            # Extract posts from HN API response
            posts = []
            for hit in hn_data["hits"]:
                posts.append({
                    "title": hit["title"],
                    "url": hit.get("url", f"https://news.ycombinator.com/item?id={hit['objectID']}"),
                    "hn_url": f"https://news.ycombinator.com/item?id={hit['objectID']}",
                    "author": hit["author"],
                    "points": hit["points"],
                    "num_comments": hit["num_comments"],
                    "created_at": hit["created_at"],
                    "object_id": hit["objectID"],
                })

            data = {
                "query": query,
                "sort_by": sort_by,
                "min_points": min_points,
                "posts": posts,
                "total_hits": hn_data["nbHits"],
                "fetched_at": datetime.now().isoformat(),
            }

            print(f"✅ Fetched {len(posts)} HN posts for query '{query}'")
            return data

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to fetch HN posts for '{query}': {e}")
            raise
        except (KeyError, ValueError) as e:
            print(f"❌ Failed to parse HN response for '{query}': {e}")
            raise

    def render(self, processed_data: Dict[str, Any]) -> str:
        """Render HackerNews posts widget HTML."""
        query = processed_data["query"]
        sort_by = processed_data["sort_by"]
        min_points = processed_data["min_points"]
        posts = processed_data["posts"]
        total_hits = processed_data["total_hits"]
        timestamp_iso = processed_data["fetched_at"]

        return self.render_template(
            "widgets/hackernews_posts.html",
            size=self.size,
            query=query,
            sort_by=sort_by,
            min_points=min_points,
            posts=posts,
            total_hits=total_hits,
            timestamp_iso=timestamp_iso
        )
