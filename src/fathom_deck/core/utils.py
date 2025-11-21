"""Utility functions for FathomDeck."""

from datetime import datetime
from urllib.parse import urlparse, quote
from typing import Optional


def format_time_ago(timestamp_str: str) -> str:
    """Convert ISO timestamp to relative time string.

    Args:
        timestamp_str: ISO format timestamp (e.g., "2025-01-15T10:30:00")

    Returns:
        Human-readable relative time (e.g., "5m ago", "2h ago", "3d ago")
    """
    try:
        # Parse ISO timestamp (handle both with and without microseconds)
        if '.' in timestamp_str:
            timestamp = datetime.fromisoformat(timestamp_str.split('.')[0])
        else:
            timestamp = datetime.fromisoformat(timestamp_str)

        now = datetime.now()
        delta = now - timestamp

        # Calculate time difference
        seconds = delta.total_seconds()

        if seconds < 0:
            return "just now"

        minutes = seconds / 60
        hours = minutes / 60
        days = hours / 24

        if seconds < 60:
            return f"{int(seconds)}s ago"
        elif minutes < 60:
            return f"{int(minutes)}m ago"
        elif hours < 24:
            return f"{int(hours)}h ago"
        elif days < 30:
            return f"{int(days)}d ago"
        else:
            months = days / 30
            return f"{int(months)}mo ago"

    except Exception as e:
        # Fallback to original timestamp if parsing fails
        return timestamp_str[:19]


def format_currency(value: float, decimals: int = 2) -> str:
    """Format a number as currency with commas and decimals.

    Args:
        value: Number to format
        decimals: Number of decimal places (default: 2)

    Returns:
        Formatted string (e.g., "$45,000.00")
    """
    return f"${value:,.{decimals}f}"


def format_large_number(value: float) -> str:
    """Format large numbers with K, M, B suffixes.

    Args:
        value: Number to format

    Returns:
        Formatted string (e.g., "1.5M", "2.3B")
    """
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    elif value >= 1_000:
        return f"${value / 1_000:.2f}K"
    else:
        return f"${value:.2f}"


def extract_domain(url: str) -> str:
    """Extract domain from URL.

    Args:
        url: Full URL

    Returns:
        Domain name (e.g., "example.com")

    Example:
        >>> extract_domain("https://www.example.com/path?query=1")
        "www.example.com"
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return ""


def get_favicon_url(url: str) -> str:
    """Get favicon URL for a domain using Google's favicon service.

    Args:
        url: Any URL from the domain

    Returns:
        URL to domain's favicon via Google service

    Example:
        >>> get_favicon_url("https://example.com/article")
        "https://www.google.com/s2/favicons?domain=example.com&sz=32"

    Notes:
        - Google's favicon service is reliable and handles missing favicons
        - Returns default icon if domain has no favicon
        - 32px size is good for most use cases
    """
    domain = extract_domain(url)
    if not domain:
        return ""
    return f"https://www.google.com/s2/favicons?domain={domain}&sz=32"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length, adding suffix if truncated.

    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: String to append if truncated (default: "...")

    Returns:
        Truncated text with suffix if needed

    Example:
        >>> truncate_text("This is a very long text", max_length=15)
        "This is a ve..."
    """
    if not text or len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def is_valid_url(url: str) -> bool:
    """Check if a string is a valid URL.

    Args:
        url: String to validate

    Returns:
        True if valid URL, False otherwise

    Example:
        >>> is_valid_url("https://example.com")
        True
        >>> is_valid_url("not a url")
        False
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def normalize_url(url: str) -> str:
    """Normalize URL by removing tracking parameters and fragments.

    Args:
        url: URL to normalize

    Returns:
        Normalized URL

    Example:
        >>> normalize_url("https://example.com/article?utm_source=twitter#section")
        "https://example.com/article"

    Notes:
        - Removes common tracking parameters (utm_*, fbclid, etc.)
        - Removes URL fragments (#section)
        - Useful for deduplication and caching
    """
    try:
        parsed = urlparse(url)

        # Remove common tracking parameters
        tracking_params = {
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
            'fbclid', 'gclid', 'msclkid', 'mc_cid', 'mc_eid',
        }

        # Parse query string and filter out tracking params
        from urllib.parse import parse_qs, urlencode
        query_dict = parse_qs(parsed.query)
        filtered_query = {
            k: v for k, v in query_dict.items()
            if k not in tracking_params
        }

        # Reconstruct URL without fragment and tracking params
        clean_query = urlencode(filtered_query, doseq=True) if filtered_query else ''
        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if clean_query:
            clean_url += f"?{clean_query}"

        return clean_url

    except Exception:
        return url
