"""Crypto price widget using Gemini API."""
from ..core.output_manager import OutputManager

from datetime import datetime, timezone
from typing import Any, Dict

from ..core.base_widget import BaseWidget
from ..core.url_fetch_manager import get_url_fetch_manager
from ..core.utils import format_large_number


class CryptoPriceWidget(BaseWidget):
    """Displays current cryptocurrency price from Gemini exchange.

    Required params:
        - symbol: Trading pair symbol (e.g., "btcusd", "ethusd")
    """

    def get_required_params(self) -> list[str]:
        return ["symbol"]

    def fetch_data(self) -> Dict[str, Any]:
        """Fetch current price data from Gemini."""
        self.validate_params()

        symbol = self.merged_params["symbol"].lower()
        client = get_url_fetch_manager()

        try:
            # Fetch ticker data from Gemini API
            url = f"https://api.gemini.com/v1/pubticker/{symbol}"
            ticker_data = client.get(url, response_type="json")

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
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }

            OutputManager.log(f"✅ Fetched {symbol.upper()}: ${data['price']:,.2f}")
            return data

        except Exception as e:
            OutputManager.log(f"❌ Failed to fetch {symbol} from Gemini: {e}")
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
            display_name=display_name,
            price=price,
            bid=processed_data['bid'],
            ask=processed_data['ask'],
            volume_display=volume_display,
            timestamp_iso=processed_data['fetched_at']
        )

    def to_markdown(self, processed_data: Dict[str, Any]) -> str:
        """Convert crypto price data to markdown format."""
        symbol = processed_data.get("symbol", "")
        price = processed_data.get("price", 0)
        bid = processed_data.get("bid", 0)
        ask = processed_data.get("ask", 0)
        volume = processed_data.get("volume", {})
        timestamp_iso = processed_data.get("fetched_at", "")

        try:
            dt = datetime.fromisoformat(timestamp_iso.replace('Z', '+00:00'))
            timestamp_display = dt.strftime("%B %d, %Y at %H:%M UTC")
        except:
            timestamp_display = timestamp_iso

        # Get display name like HTML does
        base_currency = symbol[:3]
        if base_currency == "BTC":
            display_name = "Bitcoin"
        elif base_currency == "ETH":
            display_name = "Ethereum"
        elif base_currency == "SOL":
            display_name = "Solana"
        else:
            display_name = base_currency

        md_parts = []
        # Match HTML: just title and large price
        md_parts.append(f"## {display_name} Price")
        md_parts.append("")
        md_parts.append(f"### ${price:,.2f}")
        md_parts.append("")
        return '\n'.join(md_parts)
