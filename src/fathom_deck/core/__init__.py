"""Core framework components."""

from .base_widget import BaseWidget, WidgetData
from .cache import Cache
from .config import PageConfig, SeriesConfig, ThemeConfig, WidgetConfig
from .http_cache import HTTPClient, get_http_client
from .url_metadata import (
    URLMetadata,
    URLMetadataExtractor,
    extract_url_metadata,
    get_url_metadata_extractor,
)

__all__ = [
    "BaseWidget",
    "WidgetData",
    "Cache",
    "PageConfig",
    "SeriesConfig",
    "ThemeConfig",
    "WidgetConfig",
    "HTTPClient",
    "get_http_client",
    "URLMetadata",
    "URLMetadataExtractor",
    "extract_url_metadata",
    "get_url_metadata_extractor",
]
