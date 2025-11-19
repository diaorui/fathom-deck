"""Configuration and widget loading utilities."""

import importlib
import yaml
from pathlib import Path
from typing import Dict, List, Type

from .base_widget import BaseWidget
from .config import PageConfig, SeriesConfig


def load_yaml(file_path: Path) -> dict:
    """Load YAML file."""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


def load_page_config(page_file: Path) -> PageConfig:
    """Load and validate page configuration."""
    data = load_yaml(page_file)
    return PageConfig(**data)


def load_series_config(series_dir: Path) -> SeriesConfig:
    """Load and validate series configuration."""
    config_file = series_dir / "config.yaml"
    if not config_file.exists():
        # Return default config if not found
        return SeriesConfig(
            id=series_dir.name,
            name=series_dir.name.title()
        )
    data = load_yaml(config_file)
    return SeriesConfig(**data)


def discover_pages(series_dir: Path) -> List[Path]:
    """Discover all page configs in a series directory."""
    pages_dir = series_dir / "pages"
    if not pages_dir.exists():
        return []

    # Find all .yaml files except _index.yaml
    page_files = [
        f for f in pages_dir.glob("*.yaml")
        if f.stem != "_index" and not f.stem.startswith("_")
    ]

    return sorted(page_files)


def load_widget_class(widget_type: str) -> Type[BaseWidget]:
    """Dynamically load widget class by type.

    Args:
        widget_type: Widget type in kebab-case (e.g., "crypto-price")

    Returns:
        Widget class

    Raises:
        ImportError if widget module not found
        AttributeError if widget class not found in module
    """
    # Convert kebab-case to snake_case for module name
    module_name = widget_type.replace("-", "_")

    try:
        # Import the widget module
        module = importlib.import_module(f"fathom_deck.widgets.{module_name}")

        # Convert to PascalCase for class name
        # e.g., "crypto_price" -> "CryptoPriceWidget"
        class_name = "".join(word.capitalize() for word in module_name.split("_")) + "Widget"

        # Get the class from the module
        widget_class = getattr(module, class_name)

        if not issubclass(widget_class, BaseWidget):
            raise TypeError(f"{class_name} is not a BaseWidget subclass")

        return widget_class

    except ImportError as e:
        raise ImportError(
            f"Widget module 'fathom_deck.widgets.{module_name}' not found. "
            f"Expected file: src/fathom_deck/widgets/{module_name}.py"
        ) from e
    except AttributeError as e:
        raise AttributeError(
            f"Widget class '{class_name}' not found in module '{module_name}'. "
            f"Expected class name: {class_name}"
        ) from e


def create_widget_instance(
    widget_type: str,
    size: str,
    params: Dict,
    page_params: Dict,
    update_minutes: int = None
) -> BaseWidget:
    """Create a widget instance.

    Args:
        widget_type: Widget type (e.g., "crypto-price")
        size: Widget size
        params: Widget-specific params
        page_params: Page-level params
        update_minutes: Update frequency

    Returns:
        Instantiated widget
    """
    widget_class = load_widget_class(widget_type)
    return widget_class(
        widget_type=widget_type,
        size=size,
        params=params,
        page_params=page_params,
        update_minutes=update_minutes
    )
