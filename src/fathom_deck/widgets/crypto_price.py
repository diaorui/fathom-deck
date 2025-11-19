"""Crypto price widget using Gemini API."""

import requests
from datetime import datetime
from typing import Any, Dict
from tenacity import retry, stop_after_attempt, wait_exponential

from ..core.base_widget import BaseWidget
from ..core.http_cache import get_cached, cache_response


class CryptoPriceWidget(BaseWidget):
    """Displays current cryptocurrency price from Gemini exchange.

    Required params:
        - symbol: Trading pair symbol (e.g., "btcusd", "ethusd")

    Optional params:
        - show_change: Whether to show 24h change (default: True)
    """

    def get_required_params(self) -> list[str]:
        return ["symbol"]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def _fetch_from_gemini(self, symbol: str) -> Dict[str, Any]:
        """Fetch ticker data from Gemini API with retry logic."""
        url = f"https://api.gemini.com/v1/pubticker/{symbol}"

        # Check cache first
        cached = get_cached(url)
        if cached:
            print(f"✅ Cache hit: {url}")
            return cached

        print(f"📡 Fetching: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Cache the response
        cache_response(url, data)
        return data

    def fetch_data(self) -> Dict[str, Any]:
        """Fetch current price data from Gemini."""
        self.validate_params()

        symbol = self.merged_params["symbol"].lower()

        try:
            ticker_data = self._fetch_from_gemini(symbol)

            # Extract relevant fields
            data = {
                "symbol": symbol.upper(),
                "price": float(ticker_data["last"]),
                "volume": {
                    "base": float(ticker_data["volume"].get(symbol[:3].upper(), 0)),
                    "quote": float(ticker_data["volume"].get(symbol[3:].upper(), 0)),
                },
                "bid": float(ticker_data["bid"]),
                "ask": float(ticker_data["ask"]),
                "fetched_at": datetime.now().isoformat(),
            }

            print(f"✅ Fetched {symbol.upper()}: ${data['price']:,.2f}")
            return data

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to fetch {symbol} from Gemini: {e}")
            raise
        except (KeyError, ValueError) as e:
            print(f"❌ Failed to parse Gemini response for {symbol}: {e}")
            raise

    def render(self, processed_data: Dict[str, Any]) -> str:
        """Render price widget HTML."""
        symbol = processed_data["symbol"]
        price = processed_data["price"]
        volume = processed_data["volume"]

        # Simple HTML for MVP - we'll use templates later
        html = f"""
        <div class="widget widget-crypto-price widget-{self.size}">
            <div class="widget-header">
                <h3>{symbol} Price</h3>
            </div>
            <div class="widget-body">
                <div class="price-display">
                    <span class="price-value">${price:,.2f}</span>
                </div>
                <div class="price-details">
                    <div>Bid: ${processed_data['bid']:,.2f}</div>
                    <div>Ask: ${processed_data['ask']:,.2f}</div>
                    <div>Volume: {volume['base']:,.2f}</div>
                </div>
            </div>
            <div class="widget-footer">
                <small>Updated: {processed_data['fetched_at'][:19]}</small>
            </div>
        </div>
        """
        return html.strip()
