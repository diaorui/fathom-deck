"""GitHub trending repositories widget using GitHub Search API."""

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List

from ..core.base_widget import BaseWidget
from ..core.http_cache import get_http_client
from ..core.url_metadata import get_url_metadata_extractor


class GithubReposWidget(BaseWidget):
    """Displays trending repositories from GitHub.

    Optional params:
        - query: Search query (default: "ai machine-learning llm")
        - days: Number of days to look back (default: 30)
        - min_stars: Minimum stars filter (default: 0)
        - language: Filter by language (default: None)
        - limit: Number of repos to show (default: 10)
    """

    def get_required_params(self) -> list[str]:
        return []

    def fetch_data(self) -> Dict[str, Any]:
        """Fetch trending repos from GitHub."""
        self.validate_params()

        query = self.merged_params.get("query", "ai machine-learning llm")
        days = self.merged_params.get("days", 30)
        min_stars = self.merged_params.get("min_stars", 0)
        language = self.merged_params.get("language")
        limit = self.merged_params.get("limit", 10)
        client = get_http_client()

        try:
            # Build search query
            # Calculate date for pushed filter (recently active repos)
            date_threshold = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")

            # Build query string - separate parts with spaces
            q_parts = [query, f"pushed:>{date_threshold}"]
            if min_stars > 0:
                q_parts.append(f"stars:>{min_stars}")
            if language:
                q_parts.append(f"language:{language}")

            q = " ".join(q_parts)

            # Fetch repos from GitHub Search API
            url = "https://api.github.com/search/repositories"
            params = {
                "q": q,
                "sort": "stars",
                "order": "desc",
                "per_page": limit
            }

            headers = {
                "User-Agent": "fathom-deck/1.0.0",
                "Accept": "application/vnd.github.v3+json"
            }
            response = client.get(url, params=params, headers=headers, response_type="json")

            # Get metadata extractor for preview images
            metadata_extractor = get_url_metadata_extractor()

            # Extract repos from response
            repos = []
            for repo in response.get("items", []):
                # Format star count
                stars = repo.get("stargazers_count", 0)
                if stars >= 1000:
                    stars_display = f"{stars / 1000:.1f}k"
                else:
                    stars_display = str(stars)

                # Format fork count
                forks = repo.get("forks_count", 0)
                if forks >= 1000:
                    forks_display = f"{forks / 1000:.1f}k"
                else:
                    forks_display = str(forks)

                # Extract metadata for preview image
                repo_url = repo["html_url"]
                metadata = metadata_extractor.extract(repo_url)
                preview_image = metadata.image if metadata else None

                # Get owner avatar from API
                owner_avatar = repo["owner"].get("avatar_url", "")

                repos.append({
                    "full_name": repo["full_name"],
                    "name": repo["name"],
                    "owner": repo["owner"]["login"],
                    "owner_avatar": owner_avatar,
                    "description": repo.get("description", ""),
                    "url": repo_url,
                    "preview_image": preview_image,
                    "stars": stars,
                    "stars_display": stars_display,
                    "forks": forks,
                    "forks_display": forks_display,
                    "language": repo.get("language"),
                    "topics": repo.get("topics", [])[:3],  # First 3 topics
                    "updated_at": repo.get("pushed_at"),  # Use pushed_at to match GitHub.com
                })

            data = {
                "repos": repos,
                "query": query,
                "search_query": q,  # Full search query with filters
                "days": days,
                "limit": limit,
                "total_count": response.get("total_count", 0),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }

            print(f"✅ Fetched {len(repos)} GitHub repos for query '{query}'")
            return data

        except Exception as e:
            print(f"❌ Failed to fetch GitHub repos: {e}")
            raise

    def render(self, processed_data: Dict[str, Any]) -> str:
        """Render GitHub repos widget HTML."""
        repos = processed_data["repos"]
        query = processed_data["query"]
        search_query = processed_data["search_query"]
        days = processed_data["days"]
        limit = processed_data["limit"]
        total_count = processed_data["total_count"]
        timestamp_iso = processed_data["fetched_at"]

        return self.render_template(
            "widgets/github_repos.html",
            size=self.size,
            repos=repos,
            query=query,
            search_query=search_query,
            days=days,
            limit=limit,
            total_count=total_count,
            timestamp_iso=timestamp_iso
        )
