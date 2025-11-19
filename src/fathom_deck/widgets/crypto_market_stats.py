"""Crypto market stats widget using CoinGecko API."""

import requests
from datetime import datetime
from typing import Any, Dict
from tenacity import retry, stop_after_attempt, wait_exponential

from ..core.base_widget import BaseWidget
from ..core.http_cache import get_cached, cache_response
from ..core.utils import format_large_number


class CryptoMarketStatsWidget(BaseWidget):
    """Displays cryptocurrency market statistics from CoinGecko.

    Required params:
        - coin_id: CoinGecko coin ID (e.g., "bitcoin", "ethereum")
    """

    def get_required_params(self) -> list[str]:
        return ["coin_id"]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def _fetch_from_coingecko(self, coin_id: str) -> Dict[str, Any]:
        """Fetch coin data from CoinGecko API with retry logic."""
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "false",
            "developer_data": "false",
        }

        # Check cache first
        cache_key = f"{url}?{','.join([f'{k}={v}' for k, v in params.items()])}"
        cached = get_cached(cache_key)
        if cached:
            print(f"✅ Cache hit: {cache_key}")
            return cached

        print(f"📡 Fetching: {url}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Cache the response
        cache_response(cache_key, data)
        return data

    def fetch_data(self) -> Dict[str, Any]:
        """Fetch market stats from CoinGecko."""
        self.validate_params()

        coin_id = self.merged_params["coin_id"]

        try:
            coin_data = self._fetch_from_coingecko(coin_id)
            market_data = coin_data["market_data"]

            # Extract relevant market stats
            data = {
                "coin_id": coin_id,
                "name": coin_data["name"],
                "symbol": coin_data["symbol"].upper(),
                "market_cap": market_data["market_cap"]["usd"],
                "total_supply": market_data.get("total_supply"),
                "circulating_supply": market_data.get("circulating_supply"),
                "max_supply": market_data.get("max_supply"),
                "ath": {
                    "price": market_data["ath"]["usd"],
                    "date": market_data["ath_date"]["usd"],
                },
                "atl": {
                    "price": market_data["atl"]["usd"],
                    "date": market_data["atl_date"]["usd"],
                },
                "price_change_24h_percent": market_data.get("price_change_percentage_24h", 0),
                "market_cap_rank": coin_data.get("market_cap_rank"),
                "fetched_at": datetime.now().isoformat(),
            }

            print(f"✅ Fetched market stats for {coin_data['name']}")
            return data

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to fetch {coin_id} from CoinGecko: {e}")
            raise
        except (KeyError, ValueError) as e:
            print(f"❌ Failed to parse CoinGecko response for {coin_id}: {e}")
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
        max_supply_display = f"{max_supply:,.0f}" if max_supply else "∞"
        supply_percent = f"{(circulating_supply / max_supply * 100):.1f}%" if (circulating_supply and max_supply) else "N/A"

        # Format ATH/ATL dates
        ath_date = datetime.fromisoformat(ath["date"].replace("Z", "+00:00"))
        ath_date_display = ath_date.strftime("%b %d, %Y")

        atl_date = datetime.fromisoformat(atl["date"].replace("Z", "+00:00"))
        atl_date_display = atl_date.strftime("%b %d, %Y")

        # 24h change color
        change_color = "var(--color-positive)" if price_change_24h >= 0 else "var(--color-negative)"
        change_sign = "+" if price_change_24h >= 0 else ""

        return self.render_template(
            "widgets/crypto_market_stats.html",
            size=self.size,
            name=name,
            symbol=symbol,
            market_cap_display=market_cap_display,
            rank=rank,
            price_change_24h=price_change_24h,
            change_color=change_color,
            change_sign=change_sign,
            circulating_display=circulating_display,
            supply_percent=supply_percent,
            max_supply_display=max_supply_display,
            ath_price=ath['price'],
            ath_date_display=ath_date_display,
            atl_price=atl['price'],
            atl_date_display=atl_date_display,
            timestamp_iso=timestamp_iso
        )
