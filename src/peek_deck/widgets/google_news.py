"""Google News widget using RSS feed with rich metadata extraction."""
from ..core.output_manager import OutputManager

import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any, Dict, List

from ..core.base_widget import BaseWidget
from ..core.url_fetch_manager import get_url_fetch_manager
from ..core.url_metadata import get_url_metadata_extractor
from ..core.utils import resolve_google_news_url, format_timestamp_ago


class GoogleNewsWidget(BaseWidget):
    """Displays recent news articles from Google News RSS feed with rich metadata.

    Resolves Google News redirect URLs and extracts rich metadata (images,
    descriptions) from the final article URLs using aggressive 30-day caching.

    Required params:
        - query: Search query (e.g., "Bitcoin", "Ethereum", "ai")

    Optional params:
        - site: Filter results to a specific site (e.g., "x.com", "reddit.com")
        - title: Custom widget title (default: "Google News")
        - limit: Number of articles to show (default: 5)
        - locale: Language and region (default: "en-US")
        - region: Region code (default: "US")
        - extract_metadata: Extract rich metadata from article URLs (default: True)
    """

    def get_required_params(self) -> list[str]:
        return ["query"]

    def fetch_data(self) -> Dict[str, Any]:
        """Fetch news articles from Google News with rich metadata."""
        self.validate_params()

        query = self.merged_params["query"]
        site = self.merged_params.get("site")
        title = self.merged_params.get("title", "Google News")
        limit = self.merged_params.get("limit", 5)
        locale = self.merged_params.get("locale", "en-US")
        region = self.merged_params.get("region", "US")
        extract_meta = self.merged_params.get("extract_metadata", True)
        client = get_url_fetch_manager()

        # Combine query and site filter if site is specified
        search_query = f"{query} site:{site}" if site else query

        try:
            # Fetch RSS feed from Google News
            url = "https://news.google.com/rss/search"
            params = {
                "q": search_query,
                "hl": locale,
                "gl": region,
                "ceid": f"{region}:en"
            }
            xml_data = client.get(url, params=params, response_type="text")

            # Parse XML
            root = ET.fromstring(xml_data)
            items = root.findall('.//item')

            # Extract articles
            articles = []
            for item in items[:limit]:
                title_elem = item.find('title')
                link_elem = item.find('link')
                pub_date_elem = item.find('pubDate')
                source_elem = item.find('source')

                if title_elem is None or link_elem is None:
                    continue

                # Parse title - format is "Headline - Source"
                title_text = title_elem.text
                if ' - ' in title_text:
                    # Split only on last ' - ' to preserve dashes in headline
                    parts = title_text.rsplit(' - ', 1)
                    headline = parts[0]
                    source_from_title = parts[1] if len(parts) > 1 else ""
                else:
                    headline = title_text
                    source_from_title = ""

                # Prefer source element over title parsing
                source_name = source_elem.text if source_elem is not None else source_from_title
                source_url = source_elem.get('url', '') if source_elem is not None else ''

                # Parse publication date (RFC 822 format)
                pub_date_str = pub_date_elem.text if pub_date_elem is not None else None
                pub_date_timestamp = None
                if pub_date_str:
                    try:
                        # Parse RFC 822 date: "Wed, 19 Nov 2025 08:43:00 GMT"
                        # Remove timezone string and parse as UTC
                        date_part = pub_date_str.rsplit(' ', 1)[0]  # Remove "GMT" or other TZ
                        dt = datetime.strptime(date_part, "%a, %d %b %Y %H:%M:%S")
                        # Treat as UTC and convert to Unix timestamp
                        dt_utc = dt.replace(tzinfo=timezone.utc)
                        pub_date_timestamp = dt_utc.timestamp()
                    except (ValueError, AttributeError):
                        pass

                articles.append({
                    "headline": headline,
                    "source": source_name,
                    "source_url": source_url,
                    "url": link_elem.text,  # Google News redirect URL
                    "pub_date": pub_date_timestamp,

                    # Metadata fields (populated below if enabled)
                    "article_url": None,  # Resolved final article URL
                    "image": None,
                    "description": None,
                })

            OutputManager.log(f"✅ Fetched {len(articles)} news articles for '{search_query}'")

            # Resolve URLs and extract rich metadata
            if extract_meta and articles:
                OutputManager.log(f"🔗 Resolving Google News redirect URLs...")

                # Step 1: Resolve all Google News redirect URLs
                for i, article in enumerate(articles):
                    google_url = article['url']
                    resolved_url = resolve_google_news_url(google_url, timeout=10)

                    if resolved_url != google_url:
                        article['article_url'] = resolved_url
                        OutputManager.log(f"   {i+1}/{len(articles)}: Resolved")
                    else:
                        OutputManager.log(f"   {i+1}/{len(articles)}: Failed to resolve")

                # Step 2: Extract metadata from resolved URLs
                OutputManager.log(f"📸 Extracting metadata from article URLs...")
                extractor = get_url_metadata_extractor()

                for i, article in enumerate(articles):
                    if not article['article_url']:
                        continue

                    # Extract metadata from resolved article URL (only image and description)
                    metadata = extractor.extract(article['article_url'])

                    if metadata:
                        article['image'] = metadata.image
                        article['description'] = metadata.description

                # Count articles with rich metadata
                resolved_count = sum(1 for a in articles if a['article_url'])
                rich_count = sum(1 for a in articles if a['image'] or a['description'])
                OutputManager.log(f"   ✅ {resolved_count}/{len(articles)} URLs resolved")
                OutputManager.log(f"   ✅ {rich_count}/{len(articles)} articles with rich previews")

            data = {
                "title": title,
                "query": query,
                "site": site,
                "search_query": search_query,
                "articles": articles,
                "has_metadata": extract_meta,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }

            return data

        except Exception as e:
            OutputManager.log(f"❌ Failed to fetch or parse Google News for '{search_query}': {e}")
            raise

    def render(self, processed_data: Dict[str, Any]) -> str:
        """Render Google News widget HTML."""
        title = processed_data["title"]
        query = processed_data["query"]
        site = processed_data["site"]
        search_query = processed_data["search_query"]
        articles = processed_data["articles"]
        has_metadata = processed_data["has_metadata"]
        timestamp_iso = processed_data["fetched_at"]

        return self.render_template(
            "widgets/google_news.html",
            title=title,
            query=query,
            site=site,
            search_query=search_query,
            articles=articles,
            has_metadata=has_metadata,
            timestamp_iso=timestamp_iso
        )

    def to_markdown(self, processed_data: Dict[str, Any]) -> str:
        """Convert Google News data to markdown format."""
        title = processed_data.get("title", "Google News")
        query = processed_data.get("query", "")
        site = processed_data.get("site")
        search_query = processed_data.get("search_query", query)
        articles = processed_data.get("articles", [])
        timestamp_iso = processed_data.get("fetched_at", "")

        # Parse timestamp for display
        try:
            dt = datetime.fromisoformat(timestamp_iso.replace('Z', '+00:00'))
            timestamp_display = dt.strftime("%B %d, %Y at %H:%M UTC")
        except:
            timestamp_display = timestamp_iso

        md_parts = []

        # Widget header (match HTML: title and query on same line)
        md_parts.append(f"## {title}: \"{search_query}\"")
        md_parts.append("")

        for idx, article in enumerate(articles, 1):
            # Title with link (matches HTML)
            headline = article['headline']
            # Use resolved article_url if available, otherwise Google News URL
            url = article.get('article_url') or article.get('url', '')
            if url:
                md_parts.append(f"**[{headline}]({url})**")
            else:
                md_parts.append(f"**{headline}**")
            md_parts.append("")

            # Description (full, not truncated - key difference for AI)
            if article.get('description'):
                md_parts.append(article['description'])
                md_parts.append("")

            # Source and time (matches HTML footer)
            footer_parts = []
            if article.get('source'):
                footer_parts.append(article['source'])

            # Add publication time if available
            if article.get('pub_date'):
                time_str = format_timestamp_ago(article['pub_date'])
                if time_str:
                    footer_parts.append(time_str)

            if footer_parts:
                md_parts.append(" • ".join(footer_parts))
                md_parts.append("")
            md_parts.append("---")
            md_parts.append("")

        return '\n'.join(md_parts)
