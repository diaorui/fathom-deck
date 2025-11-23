# PeekDeck

> **A glance is all you need.**

A configurable, widget-based monitoring system that generates static dashboards for tracking various data sources.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Pipeline

```bash
# Run all stages (fetch, process, render)
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
python -m peek_deck all
```

Or run individual stages:

```bash
python -m peek_deck fetch    # Stage 1: Fetch data from APIs
python -m peek_deck process  # Stage 2: Process raw data
python -m peek_deck render   # Stage 3: Render HTML
```

### 3. View the Output

Open `docs/crypto/bitcoin.html` in your browser to see the Bitcoin dashboard.

## Project Structure

```
fathom-deck/
├── src/peek_deck/             # Python source code
│   ├── core/                  # Core framework
│   │   ├── base_widget.py     # BaseWidget class
│   │   ├── cache.py           # Cache system
│   │   ├── config.py          # Pydantic models
│   │   └── loader.py          # Config/widget loaders
│   ├── widgets/               # All widgets
│   │   └── crypto_price.py    # Crypto price widget
│   ├── fetch.py               # Stage 1: Fetch data
│   ├── process.py             # Stage 2: Process data
│   └── render.py              # Stage 3: Render HTML
│
├── templates/                 # Jinja2 templates
│   ├── widgets/               # Widget templates (future)
│   └── pages/
│       └── page.html          # Page layout
│
├── series/                    # Series configurations
│   └── crypto/
│       ├── config.yaml        # Series theme/config
│       └── pages/
│           └── bitcoin.yaml   # Bitcoin page config
│
├── data/                      # Generated data (gitignored)
│   ├── raw/                   # Raw API responses
│   ├── processed/             # Processed data
│   └── cache/                 # Cache metadata
│
└── docs/                      # Generated HTML (gitignored locally)
    └── crypto/
        └── bitcoin.html       # Bitcoin dashboard
```

## Adding a New Page

Create a YAML file in `series/crypto/pages/`:

```yaml
# ethereum.yaml
series: crypto
id: ethereum
name: Ethereum
description: Real-time Ethereum monitoring
icon: "Ξ"
enabled: true

params:
  symbol: ethusd
  coin_id: ethereum

widgets:
  - type: crypto-price
    size: medium
    update_minutes: 5
```

Then run the pipeline:

```bash
./run.sh all
```

## GitHub Actions (Automated Updates)

PeekDeck includes a GitHub Actions workflow that automatically updates your dashboards every 5 minutes.

**Setup:**
1. Push your repo to GitHub
2. Follow the instructions in `SETUP.md`
3. Enable GitHub Pages pointing to the `gh-pages` branch

The workflow will:
- Run every 5 minutes
- Only fetch data for widgets that need updating (based on `update_minutes`)
- Automatically deploy to GitHub Pages
- Store generated content in a separate `data` branch

**Your dashboards will be live at:**
`https://YOUR_USERNAME.github.io/fathom-deck/crypto/bitcoin.html`

See `SETUP.md` for complete deployment instructions.

## How It Works

### 3-Stage Pipeline

1. **Fetch** - Gets raw data from external APIs (Gemini, etc.)
   - Checks cache to avoid unnecessary API calls
   - Saves raw JSON to `data/raw/`

2. **Process** - Transforms/enriches data
   - Currently just passes through (for LLM summaries later)
   - Saves to `data/processed/`

3. **Render** - Generates static HTML
   - Uses Jinja2 templates
   - Outputs to `docs/`
   - Updates cache timestamps

### Cache System

- Tracks last update time for each widget instance
- Skips fetching if widget was updated recently
- Configured per-widget via `update_minutes`
- Uses unique keys: `{series}_{page}_{widget_type}_{params}`

### Current Widgets

- **crypto-price** - Fetches cryptocurrency prices from Gemini API
  - Required params: `symbol` (e.g., "btcusd")
  - Shows: current price, bid, ask, volume

## Next Steps

See `DESIGN.md` for the complete architecture and roadmap.

**MVP is complete!** The next steps would be:
1. Add more widgets (news, charts, market stats)
2. Set up GitHub Actions workflow
3. Improve templates with Jinja2 widget templates
4. Add more cryptocurrencies

## Design Principles

- **Ship fast, iterate** - MVP first, perfection later
- **Simple > complex** - Use proven solutions
- **Fail gracefully** - One widget failure shouldn't break the page
- **Cache aggressively** - Respect API limits
