"""ProductHunt widget using RSS feed."""
from ..core.output_manager import OutputManager

import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any, Dict, List

from ..core.base_widget import BaseWidget
from ..core.url_fetch_manager import get_url_fetch_manager


class ProducthuntWidget(BaseWidget):
    """Displays recent products from ProductHunt RSS feed.

    Optional params:
        - category: Filter by category (e.g., "tech", "games", "books")
                   NOTE: ProductHunt RSS feed only supports 3 categories: "tech", "games", "books"
        - title: Custom widget title (default: "ProductHunt")
        - limit: Number of products to show (default: 10)
    """

    def get_required_params(self) -> list[str]:
        return []

    def fetch_data(self) -> Dict[str, Any]:
        """Fetch products from ProductHunt."""
        self.validate_params()

        category = self.merged_params.get("category")
        title = self.merged_params.get("title", "ProductHunt")
        limit = self.merged_params.get("limit", 10)
        client = get_url_fetch_manager()

        try:
            # Fetch RSS feed from ProductHunt
            url = "https://www.producthunt.com/feed"
            params = {}
            if category:
                params["category"] = category

            xml_data = client.get(url, params=params, response_type="text")

            # Parse XML (Atom format)
            root = ET.fromstring(xml_data)
            # Atom namespace
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            entries = root.findall('atom:entry', ns)

            # Extract products
            products = []
            for entry in entries[:limit]:
                title_elem = entry.find('atom:title', ns)
                link_elem = entry.find('atom:link[@rel="alternate"]', ns)
                published_elem = entry.find('atom:published', ns)
                content_elem = entry.find('atom:content', ns)
                author_elem = entry.find('atom:author/atom:name', ns)

                if title_elem is None or link_elem is None:
                    continue

                # Extract tagline from HTML content
                tagline = ""
                if content_elem is not None and content_elem.text:
                    # Content is HTML like: <p>\n  Tagline here\n</p>
                    content_html = content_elem.text
                    # Simple extraction - find first <p> tag content
                    if '<p>' in content_html:
                        try:
                            start = content_html.index('<p>') + 3
                            end = content_html.index('</p>', start)
                            tagline = content_html[start:end].strip()
                        except ValueError:
                            pass

                # Parse publication date (ISO 8601 format)
                pub_date_str = published_elem.text if published_elem is not None else None
                pub_date_timestamp = None
                if pub_date_str:
                    try:
                        # Parse ISO 8601: "2025-11-19T12:41:53-08:00"
                        dt = datetime.fromisoformat(pub_date_str)
                        pub_date_timestamp = dt.timestamp()
                    except (ValueError, AttributeError):
                        pass

                products.append({
                    "name": title_elem.text,
                    "tagline": tagline,
                    "url": link_elem.get('href', ''),
                    "pub_date": pub_date_timestamp,
                    "maker": author_elem.text if author_elem is not None else "",
                })

            data = {
                "title": title,
                "category": category,
                "products": products,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }

            category_str = f" (category: {category})" if category else ""
            OutputManager.log(f"✅ Fetched {len(products)} ProductHunt products{category_str}")
            return data

        except Exception as e:
            OutputManager.log(f"❌ Failed to fetch or parse ProductHunt feed: {e}")
            raise

    def render(self, processed_data: Dict[str, Any]) -> str:
        """Render ProductHunt widget HTML."""
        title = processed_data["title"]
        category = processed_data["category"]
        products = processed_data["products"]
        timestamp_iso = processed_data["fetched_at"]

        return self.render_template(
            "widgets/producthunt.html",
            size=self.size,
            title=title,
            category=category,
            products=products,
            timestamp_iso=timestamp_iso
        )
