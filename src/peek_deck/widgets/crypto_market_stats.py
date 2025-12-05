"""Crypto market stats widget using CoinGecko API."""
from ..core.output_manager import OutputManager

from datetime import datetime, timezone
from typing import Any, Dict

from ..core.base_widget import BaseWidget
from ..core.url_fetch_manager import get_url_fetch_manager
from ..core.utils import format_large_number


class CryptoMarketStatsWidget(BaseWidget):
    """Displays cryptocurrency market statistics from CoinGecko.

    Required params:
        - coin_id: CoinGecko coin ID (e.g., "bitcoin", "ethereum")
    """

    def get_required_params(self) -> list[str]:
        return ["coin_id"]

    def fetch_data(self) -> Dict[str, Any]:
        """Fetch market stats from CoinGecko."""
        self.validate_params()

        coin_id = self.merged_params["coin_id"]
        client = get_url_fetch_manager()

        try:
            # Fetch coin data from CoinGecko API
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
            params = {
                "localization": "false",
                "tickers": "false",
                "market_data": "true",
                "community_data": "false",
                "developer_data": "false",
            }
            coin_data = client.get(url, params=params, response_type="json")
            market_data = coin_data["market_data"]

            # Extract relevant market stats
            current_price = market_data["current_price"]["usd"]
            ath_price = market_data["ath"]["usd"]
            atl_price = market_data["atl"]["usd"]

            data = {
                "coin_id": coin_id,
                "name": coin_data["name"],
                "symbol": coin_data["symbol"].upper(),
                "current_price": current_price,
                "market_cap": market_data["market_cap"]["usd"],
                "total_supply": market_data.get("total_supply"),
                "circulating_supply": market_data.get("circulating_supply"),
                "max_supply": market_data.get("max_supply"),
                "ath": {
                    "price": ath_price,
                    "date": market_data["ath_date"]["usd"],
                    "change_percent": ((current_price - ath_price) / ath_price * 100) if ath_price else 0,
                },
                "atl": {
                    "price": atl_price,
                    "date": market_data["atl_date"]["usd"],
                    "change_percent": ((current_price - atl_price) / atl_price * 100) if atl_price else 0,
                },
                "price_change_24h_percent": market_data.get("price_change_percentage_24h", 0),
                "market_cap_rank": coin_data.get("market_cap_rank"),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }

            OutputManager.log(f"✅ Fetched market stats for {coin_data['name']}")
            return data

        except Exception as e:
            OutputManager.log(f"❌ Failed to fetch market stats for {coin_id}: {e}")
            raise

    def render(self, processed_data: Dict[str, Any]) -> str:
        """Render market stats widget HTML."""
        name = processed_data["name"]
        symbol = processed_data["symbol"]
        market_cap = processed_data["market_cap"]
        circulating_supply = processed_data["circulating_supply"]
        max_supply = processed_data["max_supply"]
        ath = processed_data["ath"]
        atl = processed_data["atl"]
        price_change_24h = processed_data["price_change_24h_percent"]
        rank = processed_data["market_cap_rank"]
        timestamp_iso = processed_data["fetched_at"]

        # Format values
        market_cap_display = format_large_number(market_cap)
        circulating_display = f"{circulating_supply:,.0f}" if circulating_supply else "N/A"
        supply_percent = f"{(circulating_supply / max_supply * 100):.1f}%" if (circulating_supply and max_supply) else "N/A"

        # Pass ISO date strings for client-side formatting
        ath_date_iso = ath["date"]
        ath_change_percent = ath["change_percent"]
        ath_change_sign = "" if ath_change_percent < 0 else "+"

        atl_date_iso = atl["date"]
        atl_change_percent = atl["change_percent"]
        atl_change_sign = "+" if atl_change_percent >= 0 else ""

        return self.render_template(
            "widgets/crypto_market_stats.html",
            name=name,
            symbol=symbol,
            market_cap_display=market_cap_display,
            rank=rank,
            circulating_display=circulating_display,
            supply_percent=supply_percent,
            ath_price=ath['price'],
            ath_date_iso=ath_date_iso,
            ath_change_percent=ath_change_percent,
            ath_change_sign=ath_change_sign,
            atl_price=atl['price'],
            atl_date_iso=atl_date_iso,
            atl_change_percent=atl_change_percent,
            atl_change_sign=atl_change_sign,
            timestamp_iso=timestamp_iso
        )

    def to_markdown(self, processed_data: Dict[str, Any]) -> str:
        """Convert crypto market stats data to markdown format."""
        name = processed_data.get("name", "")
        symbol = processed_data.get("symbol", "")
        market_cap = processed_data.get("market_cap", 0)
        market_cap_rank = processed_data.get("market_cap_rank")
        circulating_supply = processed_data.get("circulating_supply")
        max_supply = processed_data.get("max_supply")
        ath = processed_data.get("ath", {})
        atl = processed_data.get("atl", {})

        # Format values like HTML does
        market_cap_display = format_large_number(market_cap)
        circulating_display = f"{circulating_supply:,.0f}" if circulating_supply else "N/A"
        supply_percent = f"{(circulating_supply / max_supply * 100):.1f}%" if (circulating_supply and max_supply) else "N/A"

        md_parts = []

        # Title (matches HTML)
        md_parts.append(f"## {name} Market Stats")
        md_parts.append("")

        # Market Cap with Rank
        md_parts.append(f"**Market Cap:** {market_cap_display}")
        if market_cap_rank:
            md_parts.append(f"Rank #{market_cap_rank}")
        md_parts.append("")

        # Circulating Supply
        md_parts.append(f"**Circulating Supply:** {circulating_display} {symbol}")
        if supply_percent != "N/A":
            md_parts.append(f"{supply_percent} of max")
        else:
            md_parts.append("No max supply")
        md_parts.append("")

        # All-Time High
        ath_price = ath.get('price', 0)
        ath_change = ath.get('change_percent', 0)
        ath_sign = "" if ath_change < 0 else "+"
        md_parts.append(f"**All-Time High:** ${ath_price:,.2f}")
        md_parts.append(f"{ath_sign}{ath_change:.1f}%")
        md_parts.append("")

        # All-Time Low
        atl_price = atl.get('price', 0)
        atl_change = atl.get('change_percent', 0)
        atl_sign = "+" if atl_change >= 0 else ""
        md_parts.append(f"**All-Time Low:** ${atl_price:,.2f}")
        md_parts.append(f"{atl_sign}{atl_change:.1f}%")
        md_parts.append("")

        return '\n'.join(md_parts)
