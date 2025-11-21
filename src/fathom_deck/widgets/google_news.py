"""Google News widget using RSS feed."""

import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any, Dict, List

from ..core.base_widget import BaseWidget
from ..core.http_cache import get_http_client


class GoogleNewsWidget(BaseWidget):
    """Displays recent news articles from Google News RSS feed.

    Required params:
        - query: Search query (e.g., "Bitcoin", "Ethereum", "ai site:x.com")

    Optional params:
        - title: Custom widget title (default: "Google News")
        - limit: Number of articles to show (default: 5)
        - locale: Language and region (default: "en-US")
        - region: Region code (default: "US")
    """

    def get_required_params(self) -> list[str]:
        return ["query"]

    def fetch_data(self) -> Dict[str, Any]:
        """Fetch news articles from Google News."""
        self.validate_params()

        query = self.merged_params["query"]
        title = self.merged_params.get("title", "Google News")
        limit = self.merged_params.get("limit", 5)
        locale = self.merged_params.get("locale", "en-US")
        region = self.merged_params.get("region", "US")
        client = get_http_client()

        try:
            # Fetch RSS feed from Google News
            url = "https://news.google.com/rss/search"
            params = {
                "q": query,
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
                    "url": link_elem.text,
                    "pub_date": pub_date_timestamp,
                })

            data = {
                "title": title,
                "query": query,
                "articles": articles,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }

            print(f"✅ Fetched {len(articles)} news articles for '{query}'")
            return data

        except Exception as e:
            print(f"❌ Failed to fetch or parse Google News for '{query}': {e}")
            raise

    def render(self, processed_data: Dict[str, Any]) -> str:
        """Render Google News widget HTML."""
        title = processed_data["title"]
        query = processed_data["query"]
        articles = processed_data["articles"]
        timestamp_iso = processed_data["fetched_at"]

        return self.render_template(
            "widgets/google_news.html",
            size=self.size,
            title=title,
            query=query,
            articles=articles,
            timestamp_iso=timestamp_iso
        )
