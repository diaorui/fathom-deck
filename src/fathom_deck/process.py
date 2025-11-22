"""Stage 2: Process raw data (LLM enrichment, filtering, etc.)."""

import json
from pathlib import Path

from .core.loader import discover_pages, load_page_config, create_widget_instance


def process_all():
    """Process raw data into processed data."""
    project_root = Path.cwd()
    series_dir = project_root / "series"
    data_raw_dir = project_root / "data" / "raw"
    data_processed_dir = project_root / "data" / "processed"
    cache_dir = project_root / "data" / "cache"

    # Create directories
    data_processed_dir.mkdir(parents=True, exist_ok=True)

    print("🔄 Stage 2: Processing raw data\n")

    # Track stats
    processed_count = 0
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
                continue

            print(f"  📄 Page: {page_config.id}")

            # Process each widget
            for widget_config in page_config.widgets:
                widget_type = widget_config.type

                # Generate cache key (same as fetch stage)
                from .core.cache import Cache
                cache = Cache(cache_dir)
                cache_key = cache.get_cache_key(
                    series_id,
                    page_config.id,
                    widget_type,
                    widget_config.params
                )

                # Check if raw data exists
                raw_file = data_raw_dir / f"{cache_key}.json"
                if not raw_file.exists():
                    skipped_count += 1
                    continue

                # Check if processed data already exists and is up-to-date
                processed_file = data_processed_dir / f"{cache_key}.json"
                if processed_file.exists():
                    # Only skip if processed data is newer than raw data
                    if processed_file.stat().st_mtime >= raw_file.stat().st_mtime:
                        skipped_count += 1
                        continue
                    # Otherwise, raw data is newer - reprocess it

                # Load raw data
                try:
                    with open(raw_file, 'r') as f:
                        raw_data = json.load(f)
                except Exception as e:
                    print(f"    ❌ Failed to read {raw_file.name}: {e}")
                    failed_count += 1
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

                # Process data
                try:
                    print(f"    🔄 Processing {widget_type}...")
                    processed_data = widget.process_data(raw_data)

                    # Save processed data
                    with open(processed_file, 'w') as f:
                        json.dump(processed_data, f, indent=2)

                    processed_count += 1
                    print(f"    ✅ Saved to {processed_file.name}")

                except Exception as e:
                    print(f"    ❌ Failed to process {widget_type}: {e}")
                    failed_count += 1

    # Print summary
    print(f"\n{'='*60}")
    print(f"📊 Process Summary:")
    print(f"   ✅ Processed: {processed_count}")
    print(f"   ⏭️  Skipped (no raw data): {skipped_count}")
    print(f"   ❌ Failed: {failed_count}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    process_all()
