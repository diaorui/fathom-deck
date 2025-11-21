"""HackerNews posts widget using Algolia Search API with rich metadata."""

from datetime import datetime, timezone
from typing import Any, Dict, List

from ..core.base_widget import BaseWidget
from ..core.http_cache import get_http_client
from ..core.url_metadata import get_url_metadata_extractor
from ..core.utils import get_favicon_url


class HackernewsPostsWidget(BaseWidget):
    """Displays recent posts from HackerNews search with rich metadata.

    Extracts rich metadata (images, descriptions) from linked articles
    using aggressive 30-day caching to minimize fetches.

    Required params:
        - query: Search query (e.g., "bitcoin", "ai", "python")

    Optional params:
        - limit: Number of posts to show (default: 8)
        - min_points: Minimum points threshold for quality filter (default: 10)
        - sort_by: Sort order - "date" or "relevance" (default: "date")
        - extract_metadata: Extract rich metadata from article URLs (default: True)
    """

    def get_required_params(self) -> list[str]:
        return ["query"]

    def fetch_data(self) -> Dict[str, Any]:
        """Fetch recent posts from HackerNews with rich metadata."""
        self.validate_params()

        query = self.merged_params["query"]
        limit = self.merged_params.get("limit", 8)
        min_points = self.merged_params.get("min_points", 10)
        sort_by = self.merged_params.get("sort_by", "date")
        extract_meta = self.merged_params.get("extract_metadata", True)
        client = get_http_client()

        try:
            # Fetch posts from HackerNews Algolia API
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

            headers = {
                "User-Agent": "fathom-deck/1.0.0"
            }
            hn_data = client.get(base_url, params=params, headers=headers, response_type="json")

            # Extract posts from HN API response
            posts = []
            for hit in hn_data["hits"]:
                post_url = hit.get("url", f"https://news.ycombinator.com/item?id={hit['objectID']}")

                posts.append({
                    "title": hit["title"],
                    "url": post_url,
                    "hn_url": f"https://news.ycombinator.com/item?id={hit['objectID']}",
                    "author": hit["author"],
                    "points": hit["points"],
                    "num_comments": hit["num_comments"],
                    "created_at": hit["created_at"],
                    "object_id": hit["objectID"],

                    # Metadata fields (populated below)
                    "image": None,
                    "description": None,
                    "favicon": None,
                    "site_name": None,
                })

            print(f"✅ Fetched {len(posts)} HN posts for query '{query}'")

            # Extract rich metadata for external article links
            if extract_meta and posts:
                print(f"📸 Extracting metadata for all {len(posts)} posts...")

                extractor = get_url_metadata_extractor()

                for i, post in enumerate(posts):
                    # Only extract metadata for external links (not HN discussion pages)
                    if post['url'] == post['hn_url']:
                        continue

                    # Extract metadata from article URL (uses 30-day cache, very fast)
                    metadata = extractor.extract(post['url'])

                    if metadata:
                        # Add rich preview data
                        post['image'] = metadata.image
                        post['description'] = metadata.description
                        post['site_name'] = metadata.site_name

                        # Only set favicon if we have site_name (favicon without name is confusing)
                        if metadata.site_name:
                            # Use metadata favicon if available, otherwise Google favicon service
                            post['favicon'] = metadata.favicon or get_favicon_url(post['url'])

                # Count posts with rich metadata
                rich_count = sum(1 for p in posts if p['image'] or p['description'])
                print(f"   ✅ {rich_count}/{len(posts)} posts with rich previews")

            data = {
                "query": query,
                "sort_by": sort_by,
                "min_points": min_points,
                "posts": posts,
                "total_hits": hn_data["nbHits"],
                "has_metadata": extract_meta,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }

            return data

        except Exception as e:
            print(f"❌ Failed to fetch or parse HN posts for '{query}': {e}")
            raise

    def render(self, processed_data: Dict[str, Any]) -> str:
        """Render HackerNews posts widget HTML."""
        query = processed_data["query"]
        sort_by = processed_data["sort_by"]
        min_points = processed_data["min_points"]
        posts = processed_data["posts"]
        total_hits = processed_data["total_hits"]
        has_metadata = processed_data["has_metadata"]
        timestamp_iso = processed_data["fetched_at"]

        return self.render_template(
            "widgets/hackernews_posts.html",
            size=self.size,
            query=query,
            sort_by=sort_by,
            min_points=min_points,
            posts=posts,
            total_hits=total_hits,
            has_metadata=has_metadata,
            timestamp_iso=timestamp_iso
        )
