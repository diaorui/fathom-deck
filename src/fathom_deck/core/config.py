"""Configuration models for FathomDeck."""

from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field


class WidgetConfig(BaseModel):
    """Configuration for a single widget instance."""

    type: str  # e.g., "crypto-price", "news"
    size: Union[Literal['small', 'medium', 'large', 'full'], int] = 'medium'
    params: Dict[str, Any] = Field(default_factory=dict)
    update_minutes: Optional[int] = Field(None, gt=0)
    max_cache_age: Optional[int] = Field(None, gt=0)  # Minutes. None = never expire

    class Config:
        extra = 'forbid'  # Reject unknown fields


class PageConfig(BaseModel):
    """Configuration for a single page (dashboard)."""

    series: str  # e.g., "crypto"
    id: str = Field(pattern=r'^[a-z0-9-]+$')
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    enabled: bool = True
    params: Dict[str, Any] = Field(default_factory=dict)
    widgets: List[WidgetConfig] = Field(min_length=1)

    class Config:
        extra = 'forbid'


class ThemeConfig(BaseModel):
    """Visual theme configuration."""

    primary_color: str = "#f7931a"  # Bitcoin orange default
    background: str = "#1a1a1a"
    text_color: str = "#ffffff"
    card_background: str = "#2d2d2d"
    border_radius: str = "8px"

    class Config:
        extra = 'allow'  # Allow custom CSS variables


class SeriesConfig(BaseModel):
    """Configuration for a series (collection of related pages)."""

    id: str = Field(pattern=r'^[a-z0-9-]+$')
    name: str
    description: Optional[str] = None
    theme: ThemeConfig = Field(default_factory=ThemeConfig)

    class Config:
        extra = 'forbid'
