"""Reddit posts widget using Reddit RSS feed."""
from ..core.output_manager import OutputManager

import html
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any, Dict, List
from urllib.parse import urlparse

from ..core.base_widget import BaseWidget
from ..core.url_fetch_manager import get_url_fetch_manager
from ..core.url_metadata import get_url_metadata_extractor
from ..core.utils import format_timestamp_ago


class RedditPostsWidget(BaseWidget):
    """Displays rising posts from a subreddit.

    Required params:
        - subreddit: Subreddit name (e.g., "artificial", "bitcoin")

    Optional params:
        - limit: Number of posts to show (default: 10)
    """

    def get_required_params(self) -> list[str]:
        return ["subreddit"]

    def fetch_data(self) -> Dict[str, Any]:
        """Fetch rising posts from subreddit RSS feed."""
        self.validate_params()

        subreddit = self.merged_params["subreddit"]
        limit = self.merged_params.get("limit", 10)
        client = get_url_fetch_manager()

        try:
            # Fetch RSS feed from Reddit (rising posts)
            url = f"https://www.reddit.com/r/{subreddit}/rising.rss"
            xml_data = client.get(url, response_type="text")

            # Parse XML (Atom format)
            root = ET.fromstring(xml_data)
            ns = {'atom': 'http://www.w3.org/2005/Atom', 'media': 'http://search.yahoo.com/mrss/'}
            entries = root.findall('atom:entry', ns)

            # Get metadata extractor for external URLs
            metadata_extractor = get_url_metadata_extractor()

            # Extract posts
            posts = []
            for entry in entries[:limit]:
                title_elem = entry.find('atom:title', ns)
                link_elem = entry.find('atom:link', ns)
                author_elem = entry.find('atom:author/atom:name', ns)
                published_elem = entry.find('atom:published', ns)
                thumbnail_elem = entry.find('media:thumbnail', ns)
                content_elem = entry.find('atom:content', ns)

                if title_elem is None or link_elem is None:
                    continue

                # Parse timestamp
                published_timestamp = None
                if published_elem is not None and published_elem.text:
                    try:
                        dt = datetime.fromisoformat(published_elem.text)
                        published_timestamp = dt.timestamp()
                    except (ValueError, AttributeError):
                        pass

                # Get thumbnail URL
                thumbnail = None
                if thumbnail_elem is not None:
                    thumbnail = thumbnail_elem.get('url')

                # Extract author username (format: /u/username)
                author = ""
                if author_elem is not None and author_elem.text:
                    author = author_elem.text.replace('/u/', '')

                # Extract content from RSS feed and external URL
                external_url = None
                site_name = None
                favicon = None
                description = None

                if content_elem is not None and content_elem.text:
                    content_html = content_elem.text

                    # Extract text content from HTML (strip tags)
                    # Remove HTML tags and decode HTML entities
                    text_content = re.sub(r'<[^>]+>', '', content_html)
                    text_content = html.unescape(text_content)
                    text_content = text_content.strip()

                    # Clean up common patterns
                    text_content = re.sub(r'\s+', ' ', text_content)  # Normalize whitespace
                    text_content = re.sub(r'\[link\]', '', text_content)  # Remove [link] text
                    text_content = re.sub(r'submitted by.*', '', text_content)  # Remove "submitted by" footer
                    text_content = text_content.strip()

                    # Use RSS content as description
                    if text_content:
                        description = text_content

                    # Look for external links in the content
                    link_match = re.search(r'<a href="([^"]+)">\[link\]</a>', content_html)
                    if link_match:
                        url = link_match.group(1)
                        url = url.replace('&amp;', '&')

                        # Parse domain
                        parsed = urlparse(url)
                        domain = parsed.netloc.lower()

                        # Only fetch metadata for non-Reddit URLs
                        if domain and not any(reddit_domain in domain for reddit_domain in ['reddit.com', 'redd.it']):
                            external_url = url

                            # Fetch metadata from external website for site_name and favicon only
                            try:
                                metadata = metadata_extractor.extract(external_url)
                                if metadata:
                                    # Get site name (prefer og:site_name, fallback to domain)
                                    site_name = metadata.site_name
                                    if not site_name:
                                        # Clean up domain as fallback
                                        site_name = domain.replace('www.', '')

                                    # Get favicon
                                    favicon = metadata.favicon

                                    # Use external site description if RSS content is too short
                                    if metadata.description and (not description or len(description) < 50):
                                        description = metadata.description
                            except Exception as e:
                                OutputManager.log(f"⚠️  Failed to fetch metadata for {external_url}: {e}")

                posts.append({
                    "title": title_elem.text,
                    "author": author,
                    "url": link_elem.get('href', ''),
                    "published": published_timestamp,
                    "thumbnail": thumbnail,
                    "external_url": external_url,
                    "site_name": site_name,
                    "favicon": favicon,
                    "description": description,
                })

            data = {
                "subreddit": subreddit,
                "posts": posts,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }

            OutputManager.log(f"✅ Fetched {len(posts)} posts from r/{subreddit} (rising)")
            return data

        except Exception as e:
            OutputManager.log(f"❌ Failed to fetch or parse r/{subreddit} RSS: {e}")
            raise

    def render(self, processed_data: Dict[str, Any]) -> str:
        """Render Reddit posts widget HTML."""
        subreddit = processed_data["subreddit"]
        posts = processed_data["posts"]
        timestamp_iso = processed_data["fetched_at"]

        return self.render_template(
            "widgets/reddit_posts.html",
            subreddit=subreddit,
            posts=posts,
            timestamp_iso=timestamp_iso
        )

    def to_markdown(self, processed_data: Dict[str, Any]) -> str:
        """Convert Reddit posts data to markdown format."""
        subreddit = processed_data.get("subreddit", "")
        posts = processed_data.get("posts", [])
        timestamp_iso = processed_data.get("fetched_at", "")

        # Parse timestamp for display
        try:
            dt = datetime.fromisoformat(timestamp_iso.replace('Z', '+00:00'))
            timestamp_display = dt.strftime("%B %d, %Y at %H:%M UTC")
        except:
            timestamp_display = timestamp_iso

        md_parts = []

        # Widget header (match HTML: title with subreddit)
        md_parts.append(f"## Reddit: r/{subreddit}")
        md_parts.append("")

        for idx, post in enumerate(posts, 1):
            # Title with link (matches HTML)
            title = post['title']
            url = post.get('url', '')
            if url:
                md_parts.append(f"**[{title}]({url})**")
            else:
                md_parts.append(f"**{title}**")
            md_parts.append("")

            # Description (full, not truncated - key difference for AI)
            if post.get('description'):
                md_parts.append(post['description'])
                md_parts.append("")

            # Footer with source and time (matches HTML)
            footer_parts = []
            if post.get('external_url') and post.get('site_name'):
                external_url = post['external_url']
                site_name = post['site_name']
                footer_parts.append(f"🔗 [{site_name}]({external_url})")

            # Add publication time if available
            if post.get('published'):
                time_str = format_timestamp_ago(post['published'])
                if time_str:
                    footer_parts.append(time_str)

            if footer_parts:
                md_parts.append(" • ".join(footer_parts))
                md_parts.append("")
            md_parts.append("---")
            md_parts.append("")

        return '\n'.join(md_parts)
