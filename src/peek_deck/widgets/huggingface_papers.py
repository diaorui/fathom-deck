"""HuggingFace daily papers widget using HuggingFace API."""
from ..core.output_manager import OutputManager

from datetime import datetime, timezone
from typing import Any, Dict, List

from ..core.base_widget import BaseWidget
from ..core.url_fetch_manager import get_url_fetch_manager
from ..core.utils import format_time_ago


class HuggingfacePapersWidget(BaseWidget):
    """Displays daily AI research papers from HuggingFace.

    Optional params:
        - limit: Number of papers to show (default: 10)
        - sort: Sort order - "trending" or "publishedAt" (default: "trending")
    """

    def get_required_params(self) -> list[str]:
        return []

    def fetch_data(self) -> Dict[str, Any]:
        """Fetch daily papers from HuggingFace."""
        self.validate_params()

        limit = self.merged_params.get("limit", 10)
        sort = self.merged_params.get("sort", "trending")
        client = get_url_fetch_manager()

        try:
            # Fetch daily papers from HuggingFace API
            url = "https://huggingface.co/api/daily_papers"
            params = {
                "limit": limit,
                "sort": sort
            }

            response = client.get(url, params=params, response_type="json")

            # Extract papers from response
            papers = []
            for item in response:
                # Paper data is nested inside "paper" key
                paper = item.get("paper", {})

                # Extract author names
                authors = [author.get("name", "") for author in paper.get("authors", [])]
                author_str = ", ".join(authors[:3])  # Show first 3 authors
                if len(authors) > 3:
                    author_str += f" et al. ({len(authors)} authors)"

                # Extract organization info (if available)
                org = item.get("organization") or paper.get("organization")
                org_name = None
                org_fullname = None
                org_avatar = None
                if org:
                    org_name = org.get("name")
                    org_fullname = org.get("fullname")
                    org_avatar = org.get("avatar")

                # Use root-level fields which have some duplicates
                paper_id = paper["id"]

                papers.append({
                    "id": paper_id,
                    "title": item.get("title") or paper.get("title"),
                    "authors": author_str,
                    "organization_name": org_name,
                    "organization_fullname": org_fullname,
                    "organization_avatar": org_avatar,
                    "summary": item.get("summary") or paper.get("summary", ""),
                    "ai_summary": paper.get("ai_summary", ""),  # Concise AI-generated summary
                    "hf_url": f"https://huggingface.co/papers/{paper_id}",  # Primary link
                    "arxiv_url": f"https://arxiv.org/abs/{paper_id}",  # Secondary link
                    "thumbnail": item.get("thumbnail", ""),  # Paper preview image
                    "upvotes": paper.get("upvotes", 0),
                    "num_comments": item.get("numComments", 0),
                    "published_at": item.get("publishedAt") or paper.get("publishedAt"),
                    "github_repo": paper.get("githubRepo"),
                    "github_stars": paper.get("githubStars"),
                    "project_page": paper.get("projectPage"),
                })

            # Enforce limit - defensive check in case API returns more than requested
            if len(papers) > limit:
                papers = papers[:limit]

            data = {
                "papers": papers,
                "limit": limit,
                "sort": sort,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }

            OutputManager.log(f"✅ Fetched {len(papers)} HuggingFace daily papers")
            return data

        except Exception as e:
            OutputManager.log(f"❌ Failed to fetch HuggingFace daily papers: {e}")
            raise

    def render(self, processed_data: Dict[str, Any]) -> str:
        """Render HuggingFace papers widget HTML."""
        papers = processed_data["papers"]
        limit = processed_data["limit"]
        sort = processed_data["sort"]
        timestamp_iso = processed_data["fetched_at"]

        return self.render_template(
            "widgets/huggingface_papers.html",
            papers=papers,
            limit=limit,
            sort=sort,
            timestamp_iso=timestamp_iso
        )

    def to_markdown(self, processed_data: Dict[str, Any]) -> str:
        """Convert HuggingFace papers data to markdown format."""
        papers = processed_data["papers"]
        limit = processed_data.get("limit", 10)
        sort = processed_data.get("sort", "trending")
        timestamp_iso = processed_data.get("fetched_at", "")

        # Parse timestamp for display
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(timestamp_iso.replace('Z', '+00:00'))
            timestamp_display = dt.strftime("%B %d, %Y at %H:%M UTC")
        except:
            timestamp_display = timestamp_iso

        md_parts = []

        # Widget header (match HTML: title and sort indicator on same line)
        sort_indicator = "🔥 Trending" if sort == "trending" else "📅 Latest"
        md_parts.append(f"## HuggingFace Papers: {sort_indicator}")
        md_parts.append("")

        for idx, paper in enumerate(papers, 1):
            # Title with link to HuggingFace paper page (matches HTML)
            title = paper['title']
            hf_url = paper.get('hf_url', '')
            if hf_url:
                md_parts.append(f"**[{title}]({hf_url})**")
            else:
                md_parts.append(f"**{title}**")
            md_parts.append("")

            # Authors (matches HTML)
            md_parts.append(f"*{paper['authors']}*")
            md_parts.append("")

            # Organization (matches HTML)
            if paper.get('organization_fullname'):
                md_parts.append(f"🏢 {paper['organization_fullname']}")
                md_parts.append("")

            # Summary - show ai_summary OR full summary, not both (matches HTML)
            # Don't truncate - this is the key difference for AI consumption
            if paper.get('ai_summary'):
                md_parts.append(paper['ai_summary'])
            elif paper.get('summary'):
                md_parts.append(paper['summary'])
            md_parts.append("")

            # Stats and links (matches HTML footer)
            stats_parts = []
            stats_parts.append(f"▲ {paper.get('upvotes', 0)}")
            stats_parts.append(f"💬 {paper.get('num_comments', 0)}")
            if paper.get('github_stars'):
                stats_parts.append(f"⭐ {paper['github_stars']:,}")

            # Add publication time if available
            if paper.get('published_at'):
                time_str = format_time_ago(paper['published_at'])
                if time_str:
                    stats_parts.append(time_str)

            md_parts.append(" • ".join(stats_parts))
            md_parts.append("")

            # Links row (matches HTML)
            links_parts = [f"[🎓 arXiv]({paper['arxiv_url']})"]
            if paper.get('github_repo'):
                links_parts.append(f"[💻 code]({paper['github_repo']})")
            if paper.get('project_page'):
                links_parts.append(f"[🔗 project]({paper['project_page']})")
            md_parts.append(" • ".join(links_parts))
            md_parts.append("")
            md_parts.append("---")
            md_parts.append("")

        return '\n'.join(md_parts)
