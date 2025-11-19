"""Cache system for tracking widget update times and data."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional


class Cache:
    """Manages widget update timestamps and determines when widgets need refreshing."""

    def __init__(self, cache_dir: Path):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "widget_timestamps.json"
        self.timestamps: Dict[str, str] = {}
        self.load()

    def load(self):
        """Load timestamps from disk."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    self.timestamps = json.load(f)
                print(f"✅ Loaded {len(self.timestamps)} cached timestamps")
            except Exception as e:
                print(f"⚠️  Failed to load cache: {e}")
                self.timestamps = {}
        else:
            self.timestamps = {}

    def save(self):
        """Save timestamps to disk."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.timestamps, f, indent=2)
            print(f"💾 Saved {len(self.timestamps)} timestamps to cache")
        except Exception as e:
            print(f"❌ Failed to save cache: {e}")

    def get_cache_key(self, series_id: str, page_id: str, widget_type: str, widget_params: Dict[str, Any]) -> str:
        """Generate unique cache key for a widget instance.

        Includes series_id to prevent collisions when page IDs are reused across series.
        """
        # Include params that affect data (e.g., symbol, coin_id)
        # Sort to ensure consistent keys
        param_str = "_".join(f"{k}={v}" for k, v in sorted(widget_params.items()))
        base = f"{series_id}_{page_id}_{widget_type}"
        return f"{base}_{param_str}" if param_str else base

    def needs_update(self, cache_key: str, update_minutes: Optional[int]) -> bool:
        """Check if widget needs updating based on last update time."""
        if update_minutes is None:
            # No update frequency specified, always update
            return True

        if cache_key not in self.timestamps:
            # Never updated before
            return True

        try:
            last_update = datetime.fromisoformat(self.timestamps[cache_key])
            time_since_update = datetime.now() - last_update
            threshold = timedelta(minutes=update_minutes)
            needs_update = time_since_update >= threshold

            if needs_update:
                print(f"🔄 {cache_key}: Last updated {time_since_update.total_seconds() / 60:.1f}m ago (threshold: {update_minutes}m)")
            else:
                remaining = (threshold - time_since_update).total_seconds() / 60
                print(f"⏭️  {cache_key}: Updated {time_since_update.total_seconds() / 60:.1f}m ago, skipping ({remaining:.1f}m remaining)")

            return needs_update
        except Exception as e:
            print(f"⚠️  Error checking cache for {cache_key}: {e}")
            return True  # Update on error

    def mark_updated(self, cache_key: str):
        """Mark widget as updated at current time."""
        self.timestamps[cache_key] = datetime.now().isoformat()

    def get_last_update(self, cache_key: str) -> Optional[datetime]:
        """Get the last update time for a widget."""
        if cache_key in self.timestamps:
            try:
                return datetime.fromisoformat(self.timestamps[cache_key])
            except Exception:
                return None
        return None
