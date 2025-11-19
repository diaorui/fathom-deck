"""Crypto price widget using Gemini API."""

import requests
from datetime import datetime
from typing import Any, Dict
from tenacity import retry, stop_after_attempt, wait_exponential

from ..core.base_widget import BaseWidget
from ..core.http_cache import get_cached, cache_response
from ..core.utils import format_large_number


class CryptoPriceWidget(BaseWidget):
    """Displays current cryptocurrency price from Gemini exchange.

    Required params:
        - symbol: Trading pair symbol (e.g., "btcusd", "ethusd")
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

        # Format the symbol for better readability (e.g., BTCUSD -> Bitcoin Price)
        # Extract base currency (first 3 chars for most cases)
        base_currency = symbol[:3]
        if base_currency == "BTC":
            display_name = "Bitcoin"
        elif base_currency == "ETH":
            display_name = "Ethereum"
        elif base_currency == "SOL":
            display_name = "Solana"
        else:
            display_name = base_currency

        # Format volume in USD (quote currency volume)
        volume_usd = volume['quote']
        volume_display = format_large_number(volume_usd)

        return self.render_template(
            "widgets/crypto_price.html",
            size=self.size,
            display_name=display_name,
            price=price,
            bid=processed_data['bid'],
            ask=processed_data['ask'],
            volume_display=volume_display,
            timestamp_iso=processed_data['fetched_at']
        )
