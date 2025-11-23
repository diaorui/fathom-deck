# PeekDeck

> **A glance is all you need.**

A configurable, widget-based monitoring system that generates static dashboards for tracking various data sources.

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run all stages (fetch, process, render)
./run.sh all

# Or run individual stages
./run.sh fetch    # Stage 1: Fetch data from APIs
./run.sh process  # Stage 2: Process raw data
./run.sh render   # Stage 3: Render HTML

# View the output
open docs/bitcoin.html
```

### GitHub Pages Deployment

**1. Push to GitHub**

```bash
git remote add origin https://github.com/YOUR_USERNAME/peek-deck.git
git push -u origin main
```

**2. Configure Secrets (Optional)**

Go to **Settings** → **Secrets and variables** → **Actions** and add:
- `YOUTUBE_API_KEY` - For YouTube widget (required if using youtube-videos widget)

**3. Enable GitHub Pages**

- Go to **Settings** → **Pages**
- Set **Source** to `gh-pages` branch
- Save

**4. Run Workflow**

- Go to **Actions** → **Update Widgets**
- Click **Run workflow**

Your dashboards will be live at:
`https://YOUR_USERNAME.github.io/peek-deck/bitcoin.html`

The workflow runs every 5 minutes and only fetches data for widgets that need updating (based on `update_minutes`).

## Project Structure

```
peek-deck/
├── pages/                     # Page configurations
│   ├── bitcoin.yaml
│   ├── ethereum.yaml
│   └── ai.yaml
│
├── src/peek_deck/             # Python source code
│   ├── core/                  # Core framework
│   │   ├── base_widget.py     # BaseWidget class
│   │   ├── cache.py           # Cache system
│   │   ├── config.py          # Pydantic models
│   │   └── loader.py          # Config/widget loaders
│   ├── widgets/               # Widget implementations
│   │   ├── crypto_price.py
│   │   ├── crypto_price_chart.py
│   │   ├── crypto_market_stats.py
│   │   ├── google_news.py
│   │   ├── reddit_posts.py
│   │   ├── hackernews_posts.py
│   │   ├── youtube_videos.py
│   │   ├── github_repos.py
│   │   ├── huggingface_models.py
│   │   └── huggingface_papers.py
│   ├── fetch.py               # Stage 1: Fetch data
│   ├── process.py             # Stage 2: Process data
│   └── render.py              # Stage 3: Render HTML
│
├── templates/                 # Jinja2 templates
│   ├── widgets/               # Widget templates
│   └── pages/                 # Page templates
│
├── data/                      # Generated data (gitignored)
│   ├── raw/                   # Raw API responses
│   ├── processed/             # Processed data
│   └── cache/                 # Cache metadata
│
└── docs/                      # Generated HTML (gitignored locally)
    ├── index.html
    ├── bitcoin.html
    └── ai.html
```

## Available Widgets

### Crypto Widgets
- **crypto-price** - Current price, bid, ask, volume (Binance API)
- **crypto-price-chart** - Historical price charts with multiple timeframes
- **crypto-market-stats** - Market cap, supply, volume, ATH/ATL (CoinGecko API)

### News & Discussion
- **google-news** - News articles from Google News RSS
- **reddit-posts** - Top posts from any subreddit
- **hackernews-posts** - Search HackerNews stories
- **youtube-videos** - YouTube search results

### Tech & AI
- **github-repos** - Trending GitHub repositories
- **huggingface-models** - Trending models from Hugging Face
- **huggingface-papers** - Latest papers from Hugging Face

## Adding a New Page

Create a YAML file in `pages/`:

```yaml
# pages/ethereum.yaml
category: crypto
id: ethereum
name: Ethereum
description: Real-time Ethereum monitoring
icon: "Ξ"
enabled: true

theme:
  primary_color: "#627eea"
  background: "#1a1a1a"
  text_color: "#ffffff"
  card_background: "#2d2d2d"
  border_radius: "8px"

params:
  symbol: ETHUSDT
  coin_id: ethereum

widgets:
  - type: crypto-price
    size: small
    update_minutes: 5

  - type: crypto-price-chart
    size: large
    update_minutes: 10

  - type: crypto-market-stats
    size: full
    update_minutes: 30
```

Run the pipeline:

```bash
./run.sh all
```

## How It Works

### 3-Stage Pipeline

1. **Fetch** - Gets raw data from external APIs
   - Checks cache to avoid unnecessary API calls
   - Saves raw JSON to `data/raw/`

2. **Process** - Transforms/enriches data
   - Applies any data transformations
   - Saves to `data/processed/`

3. **Render** - Generates static HTML
   - Uses Jinja2 templates
   - Outputs to `docs/`
   - Updates cache timestamps

### Cache System

- Tracks last update time for each widget instance
- Skips fetching if widget was updated recently
- Configured per-widget via `update_minutes`
- Only updates widgets that need refreshing

### Branch Structure (GitHub)

- **main** - Code, configs, templates (you edit this)
- **data** - Generated content (docs/ + cache/) - auto-updated by workflow
- **gh-pages** - Deployed HTML for GitHub Pages - auto-deployed from docs/

## Design Principles

- **Ship fast, iterate** - MVP first, perfection later
- **Simple > complex** - Use proven solutions
- **Fail gracefully** - One widget failure shouldn't break the page
- **Cache aggressively** - Respect API limits
