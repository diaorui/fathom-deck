"""Reddit posts widget using Reddit JSON API."""

import requests
from datetime import datetime
from typing import Any, Dict, List
from tenacity import retry, stop_after_attempt, wait_exponential

from ..core.base_widget import BaseWidget
from ..core.http_cache import get_cached, cache_response


class RedditPostsWidget(BaseWidget):
    """Displays recent posts from a subreddit.

    Required params:
        - subreddit: Subreddit name (e.g., "bitcoin", "cryptocurrency")

    Optional params:
        - limit: Number of posts to show (default: 5)
        - sort: Sort order - "hot", "new", "top", "rising" (default: "hot")
    """

    def get_required_params(self) -> list[str]:
        return ["subreddit"]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def _fetch_from_reddit(self, subreddit: str, sort: str, limit: int) -> Dict:
        """Fetch posts from Reddit JSON API."""
        url = f"https://www.reddit.com/r/{subreddit}/{sort}/.json"
        params = {"limit": limit}

        # Check cache first
        cache_key = f"{url}?limit={limit}"
        cached = get_cached(cache_key)
        if cached:
            print(f"✅ Cache hit: {cache_key}")
            return cached

        print(f"📡 Fetching: {url}")
        headers = {
            "User-Agent": "python:fathom-deck:v1.0.0 (by /u/fathom-deck-bot)"
        }
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Cache the response
        cache_response(cache_key, data)
        return data

    def fetch_data(self) -> Dict[str, Any]:
        """Fetch recent posts from subreddit."""
        self.validate_params()

        subreddit = self.merged_params["subreddit"]
        limit = self.merged_params.get("limit", 5)
        sort = self.merged_params.get("sort", "hot")

        try:
            reddit_data = self._fetch_from_reddit(subreddit, sort, limit)

            # Extract posts from Reddit API response
            posts = []
            for child in reddit_data["data"]["children"]:
                post_data = child["data"]

                # Handle thumbnail - can be URL, "self", "default", or missing
                thumbnail = post_data.get("thumbnail", "")
                if not thumbnail.startswith("http"):
                    thumbnail = None

                posts.append({
                    "title": post_data["title"],
                    "author": post_data["author"],
                    "score": post_data["score"],
                    "num_comments": post_data["num_comments"],
                    "url": f"https://www.reddit.com{post_data['permalink']}",
                    "created_utc": post_data["created_utc"],
                    "is_self": post_data["is_self"],
                    "thumbnail": thumbnail,
                })

            data = {
                "subreddit": subreddit,
                "sort": sort,
                "posts": posts,
                "fetched_at": datetime.now().isoformat(),
            }

            print(f"✅ Fetched {len(posts)} posts from r/{subreddit}")
            return data

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to fetch r/{subreddit}: {e}")
            raise
        except (KeyError, ValueError) as e:
            print(f"❌ Failed to parse Reddit response for r/{subreddit}: {e}")
            raise

    def render(self, processed_data: Dict[str, Any]) -> str:
        """Render Reddit posts widget HTML."""
        subreddit = processed_data["subreddit"]
        sort = processed_data["sort"]
        posts = processed_data["posts"]
        timestamp_iso = processed_data["fetched_at"]

        return self.render_template(
            "widgets/reddit_posts.html",
            size=self.size,
            subreddit=subreddit,
            sort=sort,
            posts=posts,
            timestamp_iso=timestamp_iso
        )
