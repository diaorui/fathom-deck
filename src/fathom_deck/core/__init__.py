"""Core framework components."""

from .base_widget import BaseWidget, WidgetData
from .cache import Cache
from .config import PageConfig, SeriesConfig, ThemeConfig, WidgetConfig

__all__ = [
    "BaseWidget",
    "WidgetData",
    "Cache",
    "PageConfig",
    "SeriesConfig",
    "ThemeConfig",
    "WidgetConfig",
]
