"""Stage 3b: Render AI-friendly Markdown from processed data."""

import json
import yaml
from datetime import datetime, timezone
from pathlib import Path

from .core.cache import Cache
from .core.loader import (
    discover_all_pages,
    load_page_config,
    create_widget_instance
)
from peek_deck import PROJECT_NAME, PROJECT_TAGLINE


def render_ai_all():
    """Render AI-friendly Markdown pages from processed data."""
    project_root = Path.cwd()
    data_processed_dir = project_root / "data" / "processed"
    docs_dir = project_root / "docs"
    cache_dir = project_root / "data" / "cache"

    # Create directories
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Initialize cache
    cache = Cache(cache_dir)

    # Load index config (for base_url)
    index_config_file = project_root / "config" / "index.yaml"
    index_config = None
    base_url = None

    if index_config_file.exists():
        try:
            with open(index_config_file, 'r') as f:
                index_config = yaml.safe_load(f)
                if index_config:
                    base_url = index_config.get('base_url')
        except Exception as e:
            print(f"⚠️  Failed to load config/index.yaml: {e}")

    print("📝 Stage 3b: Rendering AI-friendly Markdown pages\n")

    # Track stats
    rendered_pages = 0
    failed_pages = 0

    # Discover all pages
    page_files = discover_all_pages()
    if not page_files:
        print("❌ No pages found in pages/ directory")
        return

    print(f"📄 Found {len(page_files)} page(s)\n")

    for page_file in page_files:
        # Load page config
        try:
            page_config = load_page_config(page_file)
        except Exception as e:
            print(f"❌ Failed to load {page_file.name}: {e}")
            failed_pages += 1
            continue

        if not page_config.enabled:
            continue

        print(f"📝 Rendering AI markdown: {page_config.id} ({page_config.name}) [{page_config.category}]")

        # Collect widget markdown and metadata
        widgets_markdown = []
        widget_types = []
        data_types = set()

        for widget_config in page_config.widgets:
            widget_type = widget_config.type

            # Generate cache key
            cache_key = cache.get_cache_key(
                page_config.category,
                page_config.id,
                widget_type,
                widget_config.params
            )

            # Load processed data
            processed_file = data_processed_dir / f"{cache_key}.json"
            if not processed_file.exists():
                print(f"    ⚠️  No processed data for {widget_type}, skipping")
                continue

            try:
                with open(processed_file, 'r') as f:
                    processed_data = json.load(f)
            except Exception as e:
                print(f"    ❌ Failed to read {processed_file.name}: {e}")
                continue

            # Create widget instance
            try:
                widget = create_widget_instance(
                    widget_type=widget_type,
                    params=widget_config.params,
                    page_params=page_config.params,
                    update_minutes=widget_config.update_minutes
                )
            except Exception as e:
                print(f"    ❌ Failed to create widget {widget_type}: {e}")
                continue

            # Render widget markdown
            try:
                widget_markdown = widget.to_markdown(processed_data)
                widgets_markdown.append(widget_markdown)

                # Extract the actual header from widget markdown for TOC
                # Look for first ## header
                import re
                header_match = re.search(r'^## (.+)$', widget_markdown, re.MULTILINE)
                if header_match:
                    widget_types.append(header_match.group(1))
                else:
                    # Fallback to widget type
                    widget_types.append(widget_type.replace('-', ' ').replace('_', ' ').title())

                # Categorize data types
                if 'price' in widget_type or 'market' in widget_type:
                    data_types.add('cryptocurrency')
                elif 'news' in widget_type:
                    data_types.add('news')
                elif 'reddit' in widget_type or 'hackernews' in widget_type:
                    data_types.add('social')
                elif 'github' in widget_type or 'huggingface' in widget_type:
                    data_types.add('repositories')
                elif 'youtube' in widget_type:
                    data_types.add('videos')
                elif 'papers' in widget_type:
                    data_types.add('research')

            except Exception as e:
                print(f"    ❌ Failed to render markdown for {widget_type}: {e}")
                continue

        # Generate page markdown
        try:
            page_markdown = generate_page_markdown(
                page_config=page_config,
                widgets_markdown=widgets_markdown,
                widget_types=widget_types,
                data_types=list(data_types),
                base_url=base_url
            )

            # Save page markdown to flat structure: docs/{page_id}.md
            page_output = docs_dir / f"{page_config.id}.md"
            with open(page_output, 'w') as f:
                f.write(page_markdown)

            print(f"    ✅ Saved to {page_config.id}.md")
            rendered_pages += 1

        except Exception as e:
            print(f"    ❌ Failed to render markdown page: {e}")
            failed_pages += 1

    # Print summary
    print(f"\n{'='*60}")
    print(f"📊 AI Markdown Render Summary:")
    print(f"   ✅ Rendered: {rendered_pages} markdown pages")
    print(f"   ❌ Failed: {failed_pages} pages")
    print(f"   📁 Output: {docs_dir}")
    print(f"{'='*60}\n")


def generate_page_markdown(
    page_config,
    widgets_markdown: list,
    widget_types: list,
    data_types: list,
    base_url: str = None
) -> str:
    """Generate comprehensive Markdown for a single page.

    Args:
        page_config: PageConfig object
        widgets_markdown: List of markdown strings from widgets
        widget_types: List of widget type names
        data_types: List of data type categories
        base_url: Base URL for the site

    Returns:
        Complete markdown string for the page
    """
    # Generate YAML frontmatter
    frontmatter = {
        'title': f"{page_config.name} Dashboard",
        'description': page_config.description,
        'category': page_config.category,
        'page_id': page_config.id,
        'updated': datetime.now(timezone.utc).isoformat(),
    }

    if base_url:
        frontmatter['url'] = f"{base_url}/{page_config.id}.html"
        frontmatter['markdown_url'] = f"{base_url}/{page_config.id}.md"

    frontmatter['widgets'] = len(widgets_markdown)

    if data_types:
        frontmatter['data_types'] = data_types

    # Build markdown content
    md_parts = []

    # Add frontmatter
    md_parts.append("---")
    md_parts.append(yaml.dump(frontmatter, default_flow_style=False, sort_keys=False).strip())
    md_parts.append("---")
    md_parts.append("")

    # Add page header
    md_parts.append(f"# {page_config.name} Dashboard")
    md_parts.append("")
    md_parts.append(page_config.description)
    md_parts.append("")

    # Add metadata (with double-space line breaks)
    updated_time = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    md_parts.append(f"**Last Updated:** {updated_time}  ")  # Two spaces for hard line break

    if base_url:
        md_parts.append(f"**HTML Version:** [{page_config.id}.html]({base_url}/{page_config.id}.html)")

    md_parts.append("")
    md_parts.append("---")
    md_parts.append("")

    # Add table of contents
    if widget_types:
        md_parts.append("## Table of Contents")
        md_parts.append("")
        for idx, widget_title in enumerate(widget_types, 1):
            # Create anchor link from header (markdown style: lowercase, spaces->hyphens, remove special chars)
            # This matches CommonMark/GitHub behavior exactly
            import re
            anchor = widget_title.lower()
            # Remove emojis and other non-ASCII characters
            anchor = re.sub(r'[^\x00-\x7F]+', '', anchor)  # Remove non-ASCII completely
            # Remove all punctuation except hyphens and spaces
            anchor = re.sub(r'[^\w\s-]', '', anchor)  # Remove punctuation
            # Replace spaces with hyphens (do NOT collapse multiple hyphens)
            anchor = anchor.replace(' ', '-')
            # Remove leading/trailing hyphens
            anchor = anchor.strip('-')
            md_parts.append(f"{idx}. [{widget_title}](#{anchor})")
        md_parts.append("")
        md_parts.append("---")
        md_parts.append("")

    # Add widget sections
    for widget_md in widgets_markdown:
        md_parts.append(widget_md)
        md_parts.append("---")
        md_parts.append("")

    # Add footer
    md_parts.append(f"*Generated by {PROJECT_NAME} - {PROJECT_TAGLINE}*")
    md_parts.append("")

    return '\n'.join(md_parts)


if __name__ == "__main__":
    render_ai_all()
