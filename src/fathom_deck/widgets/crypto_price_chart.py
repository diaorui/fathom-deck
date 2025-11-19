"""Crypto price chart widget using Gemini candles API."""

import requests
from datetime import datetime
from typing import Any, Dict, List
from tenacity import retry, stop_after_attempt, wait_exponential

from ..core.base_widget import BaseWidget
from ..core.http_cache import get_cached, cache_response


class CryptoPriceChartWidget(BaseWidget):
    """Displays cryptocurrency price history chart using candlestick data.

    Required params:
        - symbol: Trading pair symbol (e.g., "btcusd", "ethusd")
        - tabs: List of tab configurations with timeframe, limit, and label
    """

    def get_required_params(self) -> list[str]:
        return ["symbol", "tabs"]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def _fetch_candles(self, symbol: str, timeframe: str) -> List[List]:
        """Fetch candlestick data from Gemini API.

        Returns: List of [timestamp_ms, open, high, low, close, volume]
        """
        url = f"https://api.gemini.com/v2/candles/{symbol}/{timeframe}"

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
        """Fetch candlestick data for all configured tabs."""
        self.validate_params()

        symbol = self.merged_params["symbol"].lower()
        tabs_config = self.merged_params["tabs"]

        # Fetch data for all tabs
        all_tabs_data = []
        for tab_config in tabs_config:
            timeframe = tab_config.get("timeframe", "1day")
            limit = tab_config.get("limit", 30)
            label = tab_config.get("label", timeframe)

            tab_data = self._fetch_single_chart(symbol, timeframe, limit)
            tab_data["label"] = label
            all_tabs_data.append(tab_data)

        data = {
            "symbol": symbol.upper(),
            "tabs": all_tabs_data,
            "fetched_at": datetime.now().isoformat(),
        }
        print(f"✅ Fetched {len(all_tabs_data)} tabs for {symbol.upper()}")
        return data

    def _fetch_single_chart(self, symbol: str, timeframe: str, limit: int) -> Dict[str, Any]:
        """Fetch data for a single chart."""
        try:
            candles = self._fetch_candles(symbol, timeframe)

            # Gemini returns candles in descending order (newest first)
            # Reverse for chronological order
            candles = list(reversed(candles))

            # Limit to requested number of candles
            if limit:
                candles = candles[-limit:]

            # Parse candles into structured format
            parsed_candles = []
            for candle in candles:
                parsed_candles.append({
                    "timestamp": candle[0],
                    "open": float(candle[1]),
                    "high": float(candle[2]),
                    "low": float(candle[3]),
                    "close": float(candle[4]),
                    "volume": float(candle[5])
                })

            return {
                "timeframe": timeframe,
                "candles": parsed_candles,
            }

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to fetch candles for {symbol} from Gemini: {e}")
            raise
        except (KeyError, ValueError, IndexError) as e:
            print(f"❌ Failed to parse Gemini candles response for {symbol}: {e}")
            raise

    def render(self, processed_data: Dict[str, Any]) -> str:
        """Render tabbed price chart widget HTML with Chart.js."""
        symbol = processed_data["symbol"]
        tabs_data = processed_data["tabs"]
        fetched_at = processed_data["fetched_at"]

        # Format the symbol for better readability
        base_currency = symbol[:3]
        if base_currency == "BTC":
            display_name = "Bitcoin"
        elif base_currency == "ETH":
            display_name = "Ethereum"
        elif base_currency == "SOL":
            display_name = "Solana"
        else:
            display_name = base_currency

        # Generate tab buttons
        tab_buttons = []
        for i, tab_data in enumerate(tabs_data):
            active_class = "active" if i == 0 else ""
            label = tab_data["label"]
            tab_buttons.append(
                f'<button class="chart-tab-btn {active_class}" data-tab="tab-{i}">{label}</button>'
            )

        # Generate tab contents with charts
        tab_contents = []
        chart_scripts = []

        for i, tab_data in enumerate(tabs_data):
            timeframe = tab_data["timeframe"]
            candles = tab_data["candles"]

            # Prepare data for Chart.js
            labels = []
            prices = []
            for candle in candles:
                timestamp = candle["timestamp"]
                dt = datetime.fromtimestamp(timestamp / 1000)

                if timeframe == "1day":
                    label = dt.strftime("%b %d")
                elif timeframe == "6h":
                    label = dt.strftime("%b %d %H:%M")
                else:  # 1hr, etc.
                    label = dt.strftime("%H:%M")

                labels.append(label)
                prices.append(candle["close"])

            # Generate unique ID for this chart
            chart_id = f"chart-{symbol.lower()}-tab-{i}"

            # Show first tab, hide others
            display_style = "" if i == 0 else "display: none;"

            # Tab content HTML
            tab_content = f"""
        <div class="chart-tab-content" data-tab-id="tab-{i}" style="{display_style}">
            <div class="widget-body">
                <canvas id="{chart_id}"></canvas>
            </div>
            <div class="widget-footer">
                <small data-timestamp="{fetched_at}">Updated {fetched_at}</small>
            </div>
        </div>"""
            tab_contents.append(tab_content)

            # Chart.js script
            chart_script = f"""
        <script>
        (function() {{
            const ctx = document.getElementById('{chart_id}').getContext('2d');
            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: {labels},
                    datasets: [{{
                        label: '{symbol} Price',
                        data: {prices},
                        borderColor: 'rgb(247, 147, 26)',
                        backgroundColor: 'rgba(247, 147, 26, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            display: false
                        }},
                        tooltip: {{
                            mode: 'index',
                            intersect: false,
                            callbacks: {{
                                label: function(context) {{
                                    return '$' + context.parsed.y.toLocaleString('en-US', {{
                                        minimumFractionDigits: 2,
                                        maximumFractionDigits: 2
                                    }});
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        y: {{
                            ticks: {{
                                color: '#9ca3af',
                                callback: function(value) {{
                                    return '$' + value.toLocaleString();
                                }}
                            }},
                            grid: {{
                                color: 'rgba(255, 255, 255, 0.1)'
                            }}
                        }},
                        x: {{
                            ticks: {{
                                color: '#9ca3af',
                                maxRotation: 45,
                                minRotation: 45
                            }},
                            grid: {{
                                color: 'rgba(255, 255, 255, 0.1)'
                            }}
                        }}
                    }}
                }}
            }});
        }})();
        </script>"""
            chart_scripts.append(chart_script)

        # Combine everything
        html = f"""
        <div class="widget widget-crypto-price-chart widget-{self.size}">
            <div class="widget-header">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3>{display_name} Price Chart</h3>
                    <div class="chart-tabs">
                        {chr(10).join(tab_buttons)}
                    </div>
                </div>
            </div>
            {chr(10).join(tab_contents)}
        </div>

        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
        {chr(10).join(chart_scripts)}
        """
        return html.strip()
