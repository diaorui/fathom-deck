"""Stage 1: Fetch raw data from external APIs."""

import json
from pathlib import Path
from typing import Dict, Any

from .core.cache import Cache
from .core.loader import discover_pages, load_page_config, create_widget_instance


def fetch_all():
    """Fetch data for all widgets across all series."""
    project_root = Path.cwd()
    series_dir = project_root / "series"
    data_raw_dir = project_root / "data" / "raw"
    cache_dir = project_root / "data" / "cache"

    # Create directories
    data_raw_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Initialize cache
    cache = Cache(cache_dir)

    print("🚀 Stage 1: Fetching data from external APIs\n")

    # Track stats
    total_widgets = 0
    fetched_count = 0
    skipped_count = 0
    failed_count = 0

    # Discover all series
    if not series_dir.exists():
        print(f"❌ Series directory not found: {series_dir}")
        return

    for series_path in series_dir.iterdir():
        if not series_path.is_dir():
            continue

        series_id = series_path.name
        print(f"\n📁 Series: {series_id}")

        # Discover pages in this series
        page_files = discover_pages(series_path)

        for page_file in page_files:
            # Load page config
            try:
                page_config = load_page_config(page_file)
            except Exception as e:
                print(f"❌ Failed to load {page_file.name}: {e}")
                continue

            if not page_config.enabled:
                print(f"⏭️  Skipping disabled page: {page_config.id}")
                continue

            print(f"\n  📄 Page: {page_config.id} ({page_config.name})")

            # Process each widget
            for widget_config in page_config.widgets:
                total_widgets += 1
                widget_type = widget_config.type

                # Generate cache key
                cache_key = cache.get_cache_key(
                    series_id,
                    page_config.id,
                    widget_type,
                    widget_config.params
                )

                # Check if widget needs update
                if not cache.needs_update(cache_key, widget_config.update_minutes):
                    skipped_count += 1
                    continue

                # Create widget instance
                try:
                    widget = create_widget_instance(
                        widget_type=widget_type,
                        size=str(widget_config.size),
                        params=widget_config.params,
                        page_params=page_config.params,
                        update_minutes=widget_config.update_minutes
                    )
                except Exception as e:
                    print(f"    ❌ Failed to create widget {widget_type}: {e}")
                    failed_count += 1
                    continue

                # Fetch data
                try:
                    print(f"    📡 Fetching {widget_type}...")
                    raw_data = widget.fetch_data()

                    # Save raw data
                    raw_file = data_raw_dir / f"{cache_key}.json"
                    with open(raw_file, 'w') as f:
                        json.dump(raw_data, f, indent=2)

                    fetched_count += 1
                    print(f"    ✅ Saved to {raw_file.name}")

                except Exception as e:
                    print(f"    ❌ Failed to fetch {widget_type}: {e}")
                    failed_count += 1

    # Print summary
    print(f"\n{'='*60}")
    print(f"📊 Fetch Summary:")
    print(f"   Total widgets: {total_widgets}")
    print(f"   ✅ Fetched: {fetched_count}")
    print(f"   ⏭️  Skipped (cached): {skipped_count}")
    print(f"   ❌ Failed: {failed_count}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    fetch_all()
