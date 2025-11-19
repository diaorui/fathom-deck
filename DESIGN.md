# FathomDeck Design Document

> **Still waters, moving data.**

## Overview

FathomDeck is a configurable, widget-based monitoring system that generates static dashboards for tracking various data sources. Users define pages with widgets, each widget fetches and visualizes specific data, and the system outputs static HTML pages deployed via GitHub Actions.

**First Use Case:** Cryptocurrency monitoring dashboards (Bitcoin, Ethereum, etc.)

**Design Principles:**
- **Generic by design** - widgets work across use cases (crypto, stocks, weather, etc.)
- **Practical over perfect** - use proven data sources, avoid hard problems
- **Minimal configuration** - users edit 1-2 YAML files to create new pages
- **Unified visual design** - consistent styling despite widget diversity
- **Flexible updates** - different widgets update at different frequencies

---

## Core Concepts

### 1. Series
A **series** is a collection of related pages sharing the same widget types and visual style.

**Examples:**
- **Crypto series**: Bitcoin page, Ethereum page, Solana page
- **Stocks series**: AAPL page, GOOGL page, TSLA page
- **Weather series**: NYC page, London page, Tokyo page

Each series has:
- Available widget types
- Shared visual template
- Series index page (lists all pages in the series)
- Default configuration

### 2. Pages
A **page** is a single dashboard with multiple widgets.

Example: `bitcoin.yaml` defines a Bitcoin monitoring page with price, news, and market stats widgets.

### 3. Widgets
A **widget** is a self-contained component that:
1. Fetches data from an external source
2. Optionally processes data (e.g., LLM summary)
3. Renders HTML output
4. Declares its size and update frequency

**Widget naming:** Uses hyphen notation (e.g., `crypto-price`, `news`)
- The full widget type is `crypto-price`, not "price widget in crypto series"
- Implementation: `CryptoPriceWidget` class in `src/widgets/crypto_price.py`
- No confusion with namespaces or object notation

**Widget types fall into two categories:**

1. **Domain-specific widgets** - `crypto-price`, `crypto-market-stats`, `stocks-price`
   - Tied to specific data sources and business logic
   - Know about their domain (crypto vs stocks)
   - Example: `crypto-price` uses Gemini API for crypto data

2. **Generic widgets** - `news`, potentially `chart`, `table`, etc.
   - Work across any domain via parameters
   - Data source determined by config, not hardcoded
   - Example: `news` widget works for Bitcoin news, AAPL news, weather news - just change the `query` param

**Parameter-driven instances:** Both types are reusable within their scope via parameters - `crypto-price` works for BTC, ETH, ADA, etc. by passing different `symbol` and `coin_id` parameters.

---

## Directory Structure

```
fathom-deck/
├── src/fathom_deck/           # Python source code
│   ├── core/                  # Core framework (BaseWidget, cache, renderer)
│   └── widgets/               # All widgets (flat structure)
│       ├── crypto_price.py
│       ├── crypto_price_chart.py
│       ├── crypto_market_stats.py
│       ├── news.py
│       └── ...
│
├── templates/                 # Shared templates (all series use these)
│   ├── widgets/
│   │   ├── base.html          # Shared widget wrapper
│   │   ├── crypto-price.html
│   │   ├── crypto-market-stats.html
│   │   ├── news.html
│   │   └── ...
│   └── pages/
│       ├── page.html          # Default page layout
│       └── index.html         # Default series index
│
├── series/
│   ├── crypto/                # Crypto-focused series
│   │   ├── config.yaml        # Theme, defaults, widget list
│   │   └── pages/
│   │       ├── bitcoin.yaml
│   │       ├── ethereum.yaml
│   │       └── _index.yaml
│   │
│   └── finance/               # Broader finance series (example)
│       ├── config.yaml        # Different theme (e.g., green vs orange)
│       └── pages/
│           ├── overview.yaml  # Mix of stocks + top cryptos
│           └── markets.yaml
│
├── data/
│   ├── raw/                   # Raw API responses (stage 1 output)
│   ├── processed/             # Processed data (stage 2 output)
│   └── cache/                 # Timestamp tracking, seen items, etc.
│
├── docs/                      # Generated HTML output (GitHub Pages)
│   ├── index.html             # Main landing page
│   ├── crypto/
│   └── finance/
│
└── .github/workflows/
    └── update.yml             # Single smart workflow (runs every 5 min)
```

**What users interact with:**
- `series/crypto/pages/*.yaml` - Add new pages
- `series/crypto/config.yaml` - Customize theme, widget list
- `templates/` - Shared across all series (rarely need to edit)

**Why templates are shared:**
- Same `crypto-price` widget can be used in `series/crypto/` AND `series/finance/`
- No duplication - one template, multiple series
- CSS variables (from `config.yaml`) handle theming differences
- Advanced: Can override by creating `series/crypto/templates/widgets/crypto-price.html`

**What gets generated:**
- `data/raw/` - Raw API responses from external sources (git-ignored)
- `data/processed/` - Processed/enriched data ready for rendering (git-ignored)
- `data/cache/` - Metadata (timestamps, seen items) for smart updates (committed)
- `docs/` - Static HTML files deployed to GitHub Pages (committed)

---

## Configuration System

### Page Configuration (`pages/crypto/bitcoin.yaml`)

```yaml
# Series this page belongs to
series: crypto

# Page metadata
id: bitcoin
name: Bitcoin
description: Real-time Bitcoin monitoring dashboard
icon: "₿"
enabled: true

# Page-specific parameters (passed to all widgets)
params:
  symbol: BTC
  coin_id: bitcoin  # CoinGecko ID

# Widget layout (12-column grid system)
widgets:
  # Row 1: Price + 24h chart
  - type: crypto-price
    size: small           # 3 columns
    params:
      show_change: true

  - type: crypto-price-chart
    size: medium          # 6 columns
    params:
      timeframe: 24h

  - type: crypto-market-stats
    size: small           # 3 columns

  # Row 2: News (full width)
  - type: news
    size: full            # 12 columns
    params:
      query: "Bitcoin"    # Google News search query
      max_items: 5
      use_llm_summary: true
    update_minutes: 60    # Update hourly

  # Row 3: Fear & Greed + Reddit
  - type: crypto-fear-greed
    size: medium
    update_minutes: 360   # Update every 6 hours

  - type: reddit
    size: medium
    params:
      subreddit: "Bitcoin"   # r/Bitcoin
    update_minutes: 120
```

**Key Design Decisions:**

1. **Inheritance**: Page inherits `symbol` and `coin_id` params, widgets can override
2. **Grid-based sizing**: `small` (3 cols), `medium` (6 cols), `large` (9 cols), `full` (12 cols)
3. **Flexible updates**: Each widget declares its own `update_minutes`
4. **Domain-prefixed widget types**: `crypto-price` is crypto-specific, `stocks-price` would be separate

### Series Configuration (`series/crypto/config.yaml`)

```yaml
id: crypto
name: Cryptocurrency Monitoring
description: Track cryptocurrency prices, news, and market sentiment

# Visual theme (CSS variables)
theme:
  primary_color: "#f7931a"      # Bitcoin orange
  background: "#1a1a1a"         # Dark mode
  text_color: "#ffffff"
  card_background: "#2d2d2d"
  border_radius: "8px"

# Optional: Override default templates
# Convention: looks for series/crypto/templates/*.html first, falls back to templates/*.html
templates:
  page: series/crypto/templates/page.html
  index: series/crypto/templates/index.html
```

### Series Index Configuration (`series/crypto/pages/_index.yaml`)

```yaml
series: crypto

# Index page content
title: Cryptocurrency Dashboards
description: Monitor multiple cryptocurrencies in real-time

# Display options
sort_by: market_cap           # How to order pages in index
featured: [bitcoin, ethereum]  # Highlight these
show_stats: true              # Show aggregate stats
```

**Note:** All pages in `series/crypto/pages/*.yaml` (except `_index.yaml`) are automatically included.

---

## Widget System Architecture

### Widget Loading

Widgets are loaded dynamically based on page configs:
- Page config specifies `type: crypto-price`
- Pipeline imports `src/fathom_deck/widgets/crypto_price.py` (converts kebab-case to snake_case)
- Instantiates the `BaseWidget` subclass found in that module
- Only used widgets are loaded (lazy loading)
- Config is the source of truth, not the filesystem

### BaseWidget Interface

Every widget inherits from `BaseWidget` which defines:

**Configuration:**
- `type` - Widget identifier (e.g., "crypto-price")
- `size` - Grid size (small/medium/large/full)
- `params` - Widget-specific parameters
- `update_minutes` - Update frequency

**Lifecycle methods:**
1. `fetch_data()` - Get data from API/source (required)
2. `process_data()` - Optional processing (e.g., LLM summary)
3. `render()` - Generate HTML (required)

**Execution flow:**
```
fetch_data() → process_data() → render() → return WidgetData
```

**Cache integration:**
- Each widget instance gets unique cache key from params
- Failed fetches can fall back to cached data
- Cache stores rendered HTML + metadata

### Widget Implementation Pattern

Each widget implements three things:

**1. Data Fetching** - Call external API with params
- Example: `crypto-price` calls CoinGecko with `coin_id` param

**2. Data Rendering** - Use Jinja2 template with data
- Templates follow standard card structure (header/body/footer)

**3. Error Handling** - Graceful fallbacks
- Use cached data if API fails
- Show error state if no cache available

### Widget Template Strategy

**Hybrid approach: Shared wrapper + dedicated content**

```
templates/widgets/
  ├── base.html              # Shared wrapper (all widgets extend this)
  ├── crypto-price.html      # Widget-specific template
  ├── crypto-news.html
  └── crypto-price-chart.html
```

**How it works:**
- `base.html` provides consistent structure (header, body container, footer)
- Each widget template extends base and fills in widget-specific content
- All widgets get consistent styling and layout automatically

**MVP approach:**
- Start with dedicated templates for each widget
- Shared wrapper (`base.html`) provides structure consistency
- Skip reusable components initially (timestamp badges, error states, etc.)
- Refactor later: Extract common patterns into `components/` if beneficial

**Benefits:**
- Simple to start - just write widget content
- Consistent design - wrapper enforces structure
- Flexible - can refactor without breaking existing widgets
- Pragmatic - optimize when needed, not prematurely

---

## Visual Design System

### Challenge: Unified Design with Diverse Widgets

Widgets have vastly different content:
- **Price widget**: Single number + chart
- **News widget**: List of articles
- **Sentiment widget**: Gauge visualization
- **Chart widget**: Time-series graph

**Solution: Card-based grid system with standardized components**

### Grid Layout (12-column)

Widgets use CSS Grid with 12 columns. Size can be specified as named preset or direct column count:

| Size | Columns | Width | Typical Use |
|------|---------|-------|-------------|
| `small` | 3 | 25% | Price, single metrics |
| `medium` | 6 | 50% | Charts, sentiment |
| `large` | 9 | 75% | Large charts |
| `full` | 12 | 100% | News lists, tables |
| `1-12` | 1-12 | 8%-100% | Custom layouts (e.g., `size: 4` for 33%) |

**Responsive behavior:** All widgets stack vertically (100% width) on mobile

**Layout example:**
```
Desktop (12 columns):
┌────────┬────────────────────┬────────┐
│ small  │      medium        │ small  │  ← Row 1
│ (3)    │       (6)          │ (3)    │
├────────────────────────────────────────┤
│              full (12)                 │  ← Row 2
└────────────────────────────────────────┘

Mobile (stacked):
┌────────────────┐
│ small          │
├────────────────┤
│ medium         │
├────────────────┤
│ small          │
├────────────────┤
│ full           │
└────────────────┘
```

### Widget Card Structure

Every widget follows a 3-part structure:

1. **Header** - Title, icon, timestamp
2. **Body** - Main content (varies by widget type)
3. **Footer** - Metadata, source links

**Benefits:**
- Consistent spacing regardless of content
- Unified visual appearance
- Easy theming with CSS variables

### Visual Consistency Rules

1. **Typography**:
   - All widgets use same font family
   - Standardized heading sizes (h1, h2, h3)
   - Consistent line heights

2. **Colors**:
   - Series-level theme defines color palette
   - Widgets use CSS variables: `var(--primary-color)`
   - Semantic colors: `--color-positive` (green), `--color-negative` (red)

3. **Spacing**:
   - Widget padding: 16px
   - Element margins: 8px, 16px, 24px (8px scale)
   - Grid gap: 16px

4. **Borders & Shadows**:
   - All widgets: `border-radius: var(--border-radius)`
   - Subtle shadow: `box-shadow: 0 2px 8px rgba(0,0,0,0.1)`

5. **Data Visualization**:
   - Use Chart.js for consistency
   - Shared color schemes across charts
   - Responsive canvas sizing

### Theme Customization

Themes are defined in `series/crypto/config.yaml` and compile to CSS variables:

**Theme categories:**
- **Colors** - Primary, secondary, background, text
- **Semantic colors** - Positive (green), negative (red), neutral (gray)
- **Layout** - Border radius, padding, spacing
- **Typography** - Font family, sizes, weights

**Example:** Bitcoin orange theme vs Ethereum blue theme
- BTC page: `primary_color: "#f7931a"` (orange)
- ETH page: `primary_color: "#627eea"` (blue)

All widgets automatically use theme colors via CSS variables.

---

## Crypto Use Case: Widget Catalog

### Essential Widgets (MVP)

| Widget | Data Source | Content | Size | Update (min) | Notes |
|--------|-------------|---------|------|--------------|-------|
| **crypto-price** | Gemini | Current price, 24h change, volume | Small | 5 | 120 req/min, real-time exchange data |
| **crypto-price-chart** | Gemini | Price history line chart (24h/7d/30d/1y) | Medium/Large | 10 | Uses Chart.js with candles endpoint |
| **crypto-market-stats** | CoinGecko | Market cap, supply, volume, ATH/ATL | Small/Medium | 30 | CoinGecko has fundamentals Gemini lacks |
| **news** | Google News RSS | Top 5 latest articles + optional LLM summary | Full | 60 | Generic widget, works for any topic |

### Advanced Widgets (Post-MVP)

| Widget | Data Source | Content | Size | Update (min) | Notes |
|--------|-------------|---------|------|--------------|-------|
| **crypto-fear-greed** | Alternative.me | Fear/Greed score (0-100) + gauge | Medium | 360 | Free API, updates daily |
| **reddit** | Reddit API | Top posts from subreddit (mentions, sentiment, keywords) | Medium | 120 | Generic widget, works for any subreddit |
| **crypto-events** | CoinMarketCal | Upcoming forks, updates, conferences | Full | 1440 | Free tier: 500 calls/day |
| **crypto-correlation** | CoinGecko | Price correlation heatmap with BTC/ETH | Medium | 720 | Requires fetching multiple coins |

### Optional/Future Widgets

| Widget | Data Source | Content | Size | Update (min) | Skip Reason |
|--------|-------------|---------|------|--------------|-------------|
| **crypto-exchange-flow** | CryptoQuant | Exchange inflows/outflows | Small | 360 | Limited free tier, data quality concerns |
| **crypto-top-holders** | Etherscan | Top 10 wallet addresses | Medium | 1440 | Only works for transparent chains (ETH, not BTC) |

### Widget Selection for Bitcoin Dashboard (Example)

```yaml
# Recommended layout for BTC page
widgets:
  - type: crypto-price          # Row 1, left
    size: small
  - type: crypto-price-chart    # Row 1, center
    size: medium
  - type: crypto-market-stats   # Row 1, right
    size: small
  - type: news                  # Row 2, full width
    size: full
    params:
      query: "Bitcoin"          # Search query for Google News
  - type: crypto-fear-greed     # Row 3, left
    size: medium
  - type: reddit                # Row 3, right
    size: medium
    params:
      subreddit: "Bitcoin"      # r/Bitcoin
```

---

## Widget Reusability Strategy

### Domain-Specific Widgets, Parameter-Driven Instances

**Key Decision:** Widgets are **domain-specific** (crypto vs stocks vs weather), not generic across domains.

**Why?** Different domains have:
- Different data sources (CoinGecko for crypto, Alpha Vantage for stocks)
- Different API structures and authentication
- Different business logic (crypto has market cap, stocks have P/E ratio)
- Different error handling and edge cases

**Reusability within a domain:**
- `crypto-price` widget works for BTC, ETH, SOL, etc. via **parameters**
- Same widget code, different `symbol` and `coin_id` params

**Reusability across domains:**
- **UI templates** - Visual structure (price card layout) can be copied/adapted
- **CSS design system** - Grid, colors, spacing rules apply to all widgets
- **Framework** - BaseWidget class, cache, config loader used by all
- **Utilities** - Number formatters, date helpers shared across widgets

**Example:**
```yaml
# Bitcoin page uses crypto-price
- type: crypto-price
  params:
    symbol: BTC
    coin_id: bitcoin

# Ethereum page uses same widget, different params
- type: crypto-price
  params:
    symbol: ETH
    coin_id: ethereum
```

If someone builds a stock series later, they'd create `stocks-price` widget (new code for Alpha Vantage API), but reuse the UI template structure and design system.

**Benefits of this approach:**
- Simple, predictable code (no complex abstraction layers)
- Easy to debug (crypto widgets don't affect stock widgets)
- Flexible (each domain can optimize for its data source)
- Fast to build new domains (~30% of original effort by reusing templates/styles)

---

## Data Sources: Quality & Reliability

### Crypto Data Sources

| Source | Type | Free Tier | Quality | Rate Limits (Free) | Notes |
|--------|------|-----------|---------|-------------------|-------|
| **Gemini** | Price/Trading | Yes (no auth) | Excellent | 120 req/min (~5M/month) | Very generous limits, exchange data |
| **CoinGecko** | Market/Fundamentals | Yes (API key) | Excellent | 10k calls/month | Market cap, supply, comprehensive |
| **Coinpaprika** | Price/Market | Yes (API key) | Excellent | 20k calls/month | Good alternative |
| **Google News RSS** | News | Yes (no auth) | Good | No strict limit | Real-time news via RSS, query by coin name |
| **Alternative.me** | Fear/Greed | Yes (no auth) | Good | No strict limit | Daily updates, unique metric |
| **CoinMarketCal** | Events | Yes (API key) | Fair | 500 calls/day | Event calendar |
| **Reddit API** | Social/News | Yes (no auth) | Variable | 60 calls/min | Generic, works with any subreddit |

### API Provider Strategy

**Key principle: Don't rely on a single provider**

With free tier limits (CoinGecko: 10k/month, Coinpaprika: 20k/month), using one provider for all widgets will quickly exceed quotas.

**Strategies to stay under limits:**
1. **Distribute load across providers** - Use different APIs for different widget types
2. **Batch API calls** - Fetch multiple coins in one request where supported
3. **Smart caching** - Cache aggressively, especially for slow-changing data
4. **Optimize update frequencies** - Not all widgets need 5-minute updates

**Recommended widget-to-source mapping:**

| Widget | Primary Source | Reason | Fallback |
|--------|---------------|--------|----------|
| **crypto-price** | Gemini | 5M/month limit, no auth, real-time exchange data | Coinpaprika |
| **crypto-price-chart** | Gemini | Candles endpoint, generous limits | CoinGecko |
| **crypto-market-stats** | CoinGecko | Has market cap, supply data (Gemini doesn't) | Coinpaprika |
| **news** | Google News RSS | Generic widget, query via params | Reddit API (fallback) |
| **crypto-fear-greed** | Alternative.me | Only source for this metric | N/A |
| **reddit** | Reddit API | Generic widget, subreddit via params | N/A |
| **crypto-events** | CoinMarketCal | Dedicated event calendar | N/A |

**Why this works:**
- **Gemini handles high-frequency widgets** (price, charts) - 5M/month is plenty
- **CoinGecko for fundamentals** (market cap, supply) - lower frequency, stays under 10k/month
- **Separate quotas** for news, social, fear/greed
- **No single point of failure** - distributed across 5+ providers

**Expected monthly usage (3 coins):**
- Gemini: ~43,000 calls/month (price + charts) - only 0.8% of 5M limit
- CoinGecko: ~1,440 calls/month (market stats) - only 14% of 10k limit
- Other providers: negligible usage

### Fallback Strategy

If primary source fails, widgets follow this priority:
1. **Use cached data** - Show with "Last updated X minutes ago" indicator
2. **Try fallback source** - If configured (e.g., Gemini → Coinpaprika for price)
3. **Show error state** - Display widget with error message if all fail

**Cache expiry:** Never expires by default. Widgets can optionally set `max_cache_age` (in minutes) to reject stale cache.

---

## 3-Stage Pipeline Architecture

The system uses a clean 3-stage pipeline for data flow:

### Stage 1: Fetch (`fetch.py`)

**Purpose:** Get raw data from external APIs

**Process:**
- For each widget that needs updating (based on `update_minutes` and last fetch time)
- Call external APIs (Gemini, CoinGecko, Google News, etc.)
- Save raw JSON responses to `data/raw/{page_id}_{widget_id}.json`
- Update `data/cache/last_fetch.json` with timestamps

**Output:** `data/raw/bitcoin_crypto-price.json`, `data/raw/bitcoin_news.json`, etc.

**Benefits:**
- Pure I/O, no logic
- Preserves original API responses for debugging
- Can retry processing/rendering without re-fetching

### Stage 2: Process (`process.py`)

**Purpose:** Transform and enrich raw data

**Process:**
- Load raw data from `data/raw/`
- Apply transformations:
  - LLM summarization (news articles)
  - Data filtering/cleaning
  - Calculations (correlations, averages)
- Save processed data to `data/processed/{page_id}_{widget_id}.json`
- Update `data/cache/last_process.json` with timestamps

**Output:** `data/processed/bitcoin_crypto-price.json`, `data/processed/bitcoin_news.json`, etc.

**Benefits:**
- Expensive operations (LLM) isolated
- Can skip if no new raw data
- Processed data is ready for rendering

### Stage 3: Render (`render.py`)

**Purpose:** Generate static HTML from processed data

**Process:**
- Load processed data from `data/processed/`
- Load page configs from `series/{series}/pages/`
- Render Jinja2 templates with data
- Generate HTML files to `docs/`
- Update `data/cache/last_render.json` with timestamps

**Output:** `docs/crypto/bitcoin.html`, `docs/crypto/index.html`, `docs/index.html`

**Benefits:**
- Fast, no external calls
- Can iterate on templates quickly
- Re-render anytime without cost

### Pipeline Flow

```
┌─────────────┐
│   Config    │ (series/crypto/pages/bitcoin.yaml)
└──────┬──────┘
       │
       ▼
┌─────────────┐     data/raw/           ┌─────────────┐     data/processed/    ┌─────────────┐
│   Fetch     │ ──────────────────────> │   Process   │ ──────────────────────> │   Render    │
│  (APIs)     │    bitcoin_price.json   │   (LLM)     │   bitcoin_price.json   │ (Templates) │
└─────────────┘                         └─────────────┘                        └──────┬──────┘
                                                                                       │
                                                                                       ▼
                                                                                  docs/crypto/
                                                                                  bitcoin.html
```

**Smart execution:**
- Fetch only runs for widgets due for update
- Process only runs if new raw data exists
- Render only runs if processed data changed
- Can force full pipeline or run stages independently

---

## Update Frequency & GitHub Actions

### Widget Update Frequency

Each widget specifies `update_minutes` directly in its configuration:

**Example widget update frequencies:**
- `crypto-price`: 5 minutes (price changes frequently)
- `crypto-price-chart`: 10 minutes (chart data updates regularly)
- `crypto-market-stats`: 30 minutes (stats change moderately)
- `crypto-news`: 60 minutes (news appears hourly)
- `crypto-fear-greed`: 360 minutes (6 hours - updates daily)
- `crypto-events`: 1440 minutes (24 hours - computationally expensive)

**Flexibility:** Any widget can use any frequency - no artificial tiers.

### GitHub Actions Strategy

**Recommended: Single Smart Workflow**

One workflow runs frequently (e.g., every 5 minutes):

```yaml
name: Update Widgets
on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout main branch
        uses: actions/checkout@v3
        with:
          ref: main
          fetch-depth: 0  # Fetch all history

      - name: Create/checkout data branch
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git fetch origin data:data || git checkout -b data
          git checkout data
          git merge main --no-edit || true

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Stage 1 - Fetch data
        run: python -m fathom_deck fetch
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          COINGECKO_API_KEY: ${{ secrets.COINGECKO_API_KEY }}

      - name: Stage 2 - Process data
        run: python -m fathom_deck process
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}  # For LLM calls

      - name: Stage 3 - Render HTML
        run: python -m fathom_deck render

      - name: Commit and push to data branch
        run: |
          git add docs/ data/cache/
          git diff --quiet && git diff --staged --quiet || \
            (git commit -m "Update widgets - $(date -u +'%Y-%m-%d %H:%M:%S UTC')" && \
             git push origin data)

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
          publish_branch: gh-pages
```

**Workflow steps explained:**

1. **Checkout main branch** - Get latest code from `main`
2. **Create/checkout data branch** - Switch to `data` branch (create if doesn't exist)
   - Merge latest code from `main` into `data`
   - This keeps config/code updated while isolating generated data
3. **Setup Python** - Install Python 3.11
4. **Install dependencies** - Install packages from `requirements.txt`
5. **Stage 1: Fetch** - Call external APIs
   - Check which widgets need updating (based on `update_minutes` and last fetch time)
   - Call APIs (Gemini, CoinGecko, Google News, etc.)
   - Save raw responses to `data/raw/`
   - Skip if no widgets due for update
6. **Stage 2: Process** - Transform data
   - Load raw data from `data/raw/`
   - Apply LLM processing (summarization, etc.)
   - Save processed data to `data/processed/`
   - Skip if no new raw data
7. **Stage 3: Render** - Generate HTML
   - Load processed data from `data/processed/`
   - Render Jinja2 templates
   - Output to `docs/`
   - Skip if no new processed data
8. **Commit to data branch** - Commit updated `docs/` and `data/cache/` to `data` branch
   - Includes timestamp in commit message
   - Only commits if there are changes
9. **Deploy to GitHub Pages** - Push `docs/` folder to `gh-pages` branch for hosting

**Benefits:**
- **Clean separation** - Fetch, process, render are independent stages
- **Protected main** - Code/config stays on `main`, generated data on `data` branch
- **Debuggable** - Inspect `data/raw/` and `data/processed/` to see what each stage produced
- **Recoverable** - If render fails, data is still saved; can re-render without re-fetching
- **Efficient** - Each stage skips if no new data
- **Flexible** - Can run stages independently for testing/debugging
- **Automatic** - Commits to `data` branch and deploys without manual intervention

**Branch structure:**
- `main` - Code, configs, templates (manual updates only)
- `data` - Generated content (docs/, data/) + code merged from main (auto-updated)
- `gh-pages` - Published HTML for GitHub Pages (auto-deployed from docs/)

**Alternative: Multiple Workflows (Optional)**

If you want more control, split by common frequencies:

- `update-fast.yml` - Every 5 min, regenerates widgets with `update_minutes <= 15`
- `update-slow.yml` - Every 30 min, regenerates widgets with `update_minutes > 15`

**Only use this if:**
- Single workflow is too slow
- You want different update schedules per environment
- Otherwise, stick with single smart workflow

### GitHub Actions Quotas

**Public repositories (your case):**
- Unlimited minutes on GitHub-hosted runners
- Soft limit: ~1000 workflow runs per day per repo
- Max 20 concurrent jobs

**Calculation for 5-minute cron:**
- 5-min cron: 288 runs/day (well under limit)
- Multiple workflows: 288 × 3 = 864 runs/day (still fine)

**Recommendation:** Use multiple workflows for clarity, one per update tier.

---

## User Configuration Experience

### Goal: Edit 1-2 Files to Create New Page

**Scenario:** User wants to add Cardano dashboard

**Step 1:** Create `pages/crypto/cardano.yaml`

```yaml
series: crypto
id: cardano
name: Cardano
icon: "₳"

params:
  symbol: ADA
  coin_id: cardano

# Copy widget config from bitcoin.yaml or use defaults
widgets:
  - type: crypto-price
    size: small
  - type: news
    size: full
    params:
      query: "Cardano ADA"  # Customize search query per page
```

**Step 2:** That's it!

The system auto-discovers `cardano.yaml` in `pages/crypto/` and:
1. Generates `docs/crypto/cardano.html`
2. Adds it to `docs/crypto/index.html`
3. Updates main `docs/index.html`

### Advanced Customization (Optional)

Users can override defaults at three levels:

| Level | What to Override | Example |
|-------|------------------|---------|
| **Widget template** | Individual widget HTML | `template: custom/my_price.html` in widget config |
| **Page template** | Entire page layout | `template: custom/page.html` in page config |
| **Theme colors** | Series or page colors | `theme: { primary_color: "#0033AD" }` |

**Most users won't need this** - defaults work for 90% of use cases.

---

## Configuration Validation

**Challenge:** Users will make mistakes in YAML files (typos, missing params, wrong types).

**Strategy:** Use Pydantic models to validate configs at load time, not execution time.

**Key validations:**
1. **Schema validation** - Required fields, correct types, valid enums (size: small/medium/large/full)
2. **Widget type existence** - Try importing the widget module, suggest similar names for typos
3. **Required parameters** - Each widget declares required params (e.g., crypto-price needs symbol, coin_id)

**Error handling:**
- **Clear messages** - Show file path, what's wrong, how to fix
- **Graceful degradation** - Skip invalid pages/widgets, continue with valid ones
- **Error report** - Generate `docs/errors.html` listing all config issues

**Example validation:**
```python
class PageConfig(BaseModel):
    series: str
    id: str = Field(pattern=r'^[a-z0-9-]+$')
    name: str
    widgets: list[WidgetConfig] = Field(min_items=1)

class WidgetConfig(BaseModel):
    type: str  # Validated against WIDGET_REGISTRY
    size: Union[Literal['small', 'medium', 'large', 'full'], int] = 'medium'  # Named or 1-12
    params: dict = {}
    update_minutes: Optional[int] = Field(None, gt=0)
    max_cache_age: Optional[int] = Field(None, gt=0)  # Minutes. None = never expire
```

**From TopicRadar:** Add `--dry-run` flag to validate configs without executing pipeline.

---

## Key Learnings & Best Practices

**These are non-obvious patterns learned from TopicRadar that are easy to overlook:**

### 1. URL Response Caching (Request Deduplication)

**Problem:** Within a single workflow run, multiple widgets may request the same URL:
- Bitcoin page: `crypto-price` widget fetches BTC price from Gemini
- Ethereum page: `crypto-price` widget fetches ETH price from Gemini (same API endpoint!)
- News widget: Multiple pages may search same Google News RSS feed

**Without caching:**
- Same URL fetched multiple times per run
- Risk of rate limiting / IP bans
- Slower execution
- Wastes API quota

**Solution:** In-memory URL response cache (per workflow run):

```python
# src/fathom_deck/core/http_cache.py
from datetime import datetime, timedelta

class URLCache:
    """In-memory cache for HTTP responses during single workflow run"""

    def __init__(self, ttl_seconds: int = 300):  # 5 minute TTL
        self.cache: dict[str, tuple[Any, datetime]] = {}
        self.ttl = timedelta(seconds=ttl_seconds)

    def get(self, url: str) -> Optional[Any]:
        if url in self.cache:
            data, timestamp = self.cache[url]
            if datetime.now() - timestamp < self.ttl:
                return data
            else:
                del self.cache[url]  # Expired
        return None

    def set(self, url: str, data: Any):
        self.cache[url] = (data, datetime.now())

# Global instance for the workflow run
_url_cache = URLCache()

# Usage in widgets
def fetch_from_api(url: str):
    cached = _url_cache.get(url)
    if cached:
        print(f"✅ Cache hit: {url}")
        return cached

    print(f"📡 Fetching: {url}")
    response = requests.get(url)
    data = response.json()

    _url_cache.set(url, data)
    return data
```

**Benefits:**
- Same URL only fetched once per run
- 5-minute TTL prevents stale data if run takes long
- In-memory only (no disk I/O)
- Automatically cleared between workflow runs

**When NOT to use:** If data must be fresh for each widget (rare).

### 2. Cache Update Safety (Critical!)

**Wrong approach (易错!):**
```python
# ❌ BAD: Update cache in fetch stage
def fetch_stage():
    data = fetch_api()
    save_to_raw(data)
    cache.mark_fetched(widget_id, timestamp=now())  # ❌ TOO EARLY
    # If process stage fails, we lose this data forever!
```

**Correct approach:**
```python
# ✅ GOOD: Update cache only after successful render
def render_stage():
    data = load_processed_data()
    html = render_template(data)
    save_html(html)

    # Only NOW mark as complete
    cache.mark_rendered(widget_id, timestamp=now())
    cache.save()
```

**Why?**
- If processing fails → Can re-run without re-fetching
- If rendering fails → Can re-run without re-processing
- Cache reflects actual completion, not just attempt

**From TopicRadar:** URLs only marked as "seen" in Stage 3 (render.py), never in earlier stages.

### 3. Graceful Degradation (Don't Crash the World)

**Wrong approach:**
```python
# ❌ BAD: One failure kills entire pipeline
for widget in widgets:
    data = widget.fetch()  # If this throws, entire page fails!
```

**Correct approach:**
```python
# ✅ GOOD: Collect failures, render what succeeded
failed_widgets = []

for widget in widgets:
    try:
        data = widget.fetch()
        html = widget.render(data)
    except Exception as e:
        print(f"❌ {widget.type} failed: {e}")
        print(f"💡 Hint: Check API key for {widget.data_source}")
        failed_widgets.append((widget.type, str(e)))
        html = render_error_state(widget, e)  # Show error in widget card

    add_to_page(html)

# Always generate page, even if some widgets failed
save_page(html)
sys.exit(0)  # Success! (partial success is still success)
```

**Benefits:**
- Bitcoin page renders even if Ethereum price fails
- User sees error widget instead of blank page
- Other widgets continue working
- Pipeline completes successfully

### 4. Provider Fallback Chain

**Pattern from TopicRadar:**
```python
strategies = [
    (primary_provider, primary_model),
    (fallback_provider, fallback_model)
]

for provider, model in strategies:
    try:
        return provider.call_api(...)
    except RateLimitError:
        print(f"⚠️  {provider} rate limited, trying next...")
        continue
    except APIError as e:
        print(f"❌ {provider} failed: {e}")
        continue

raise Exception("All providers failed")
```

**Apply to widgets:**
- Price widget: Gemini → Coinpaprika → Cached data
- News widget: Google News → Reddit → Cached data
- Never hard-fail, always have fallback

### 5. Structured JSON Output (LLM Calls)

**Wrong approach:**
```python
# ❌ BAD: Pray LLM returns valid JSON
response = llm.generate("Summarize this news...")
try:
    data = json.loads(response)  # Often fails!
except JSONDecodeError:
    # Now what? Retry? Give up?
```

**Correct approach:**
```python
# ✅ GOOD: Use JSON schema to guarantee structure
schema = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "bullets": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["summary", "bullets"]
}

response = llm.generate(prompt, json_schema=schema)
data = json.loads(response)  # Guaranteed to work!
```

**Why?**
- No parsing errors
- No retry loops
- Immediate validation
- Works with Pydantic models

### 6. PYTHONPATH Workaround (GitHub Actions)

**Problem:** `python -m fathom_deck.fetch` fails in GitHub Actions:
```
ModuleNotFoundError: No module named 'fathom_deck'
```

**Solution:** Set PYTHONPATH in workflow:
```yaml
steps:
  - name: Stage 1 - Fetch
    run: |
      export PYTHONPATH="${PYTHONPATH}:${GITHUB_WORKSPACE}/src"
      python -m fathom_deck.fetch
```

**Why needed?** GitHub Actions doesn't preserve environment between steps.

### 7. Upload Artifacts Even on Failure

**Pattern from TopicRadar:**
```yaml
- name: Upload artifacts for debugging
  if: always()  # ← Critical! Runs even if previous steps failed
  uses: actions/upload-artifact@v4
  with:
    name: processing-artifacts
    path: |
      data/raw/
      data/processed/
    retention-days: 7
```

**Why?**
- Debug failures by inspecting what was actually fetched
- See exactly where pipeline broke
- Download artifacts from Actions tab

### 8. Metadata Embedding (Don't Create Separate Files)

**Wrong approach:**
```
data/
├── bitcoin_price.json        # Actual data
└── bitcoin_price_meta.json   # Metadata (timestamp, source, etc.)
```

**Better approach:**
```json
{
  "_metadata": {
    "fetched_at": "2025-01-15T10:30:00Z",
    "source": "gemini",
    "widget_type": "crypto-price"
  },
  "data": {
    "price": 45000,
    "change_24h": 2.5
  }
}
```

**Benefits:**
- Single file to manage
- Atomic reads/writes
- No orphaned metadata files

### 9. Custom Jinja2 Filters for Widgets

**Essential filters for dashboard widgets:**

```python
# Register in renderer
env.filters['time_ago'] = time_ago        # "5h ago"
env.filters['format_currency'] = format_currency  # "$45,000.00"
env.filters['format_percent'] = format_percent    # "+2.5%"
env.filters['format_large_number'] = format_large_number  # "1.5M", "2.3B"
env.filters['truncate_smart'] = truncate_smart    # Smart text truncation
```

**Usage in templates:**
```html
<div class="price">{{ data.price|format_currency }}</div>
<div class="change">{{ data.change_24h|format_percent }}</div>
<div class="updated">{{ data.timestamp|time_ago }}</div>
```

### 10. Emoji Logging for Scannable Output

**Pattern:**
```python
print("📡 Fetching Bitcoin price from Gemini...")
print("✅ Success: $45,000 (+2.5%)")
print("⚠️  API rate limit approaching (80% used)")
print("❌ Failed to fetch Ethereum price")
print("💡 Hint: Check GEMINI_API_KEY environment variable")
print("🔄 Retrying with fallback provider...")
```

**Benefits:**
- Quick visual scanning in logs
- Easy to grep: `grep "❌"` shows only errors
- User-friendly in CI logs
- Professional appearance

### 11. Retry Logic with Exponential Backoff

**Wrong approach:**
```python
# ❌ BAD: No retries on transient failures
data = api.fetch()  # Network glitch → entire widget fails
```

**Correct approach:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    reraise=True
)
def fetch_from_api(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()
```

**Retries with:** 2s → 4s → 8s delays, then gives up.

### 12. Rate Limit Headers Tracking

**Monitor API quota usage:**
```python
def fetch_with_rate_limit_check(url, headers):
    response = requests.get(url, headers=headers)

    # Check rate limit headers
    remaining = response.headers.get('X-RateLimit-Remaining')
    limit = response.headers.get('X-RateLimit-Limit')

    if remaining and limit:
        usage_pct = (int(limit) - int(remaining)) / int(limit) * 100
        if usage_pct > 80:
            print(f"⚠️  API quota at {usage_pct:.1f}% - consider slowing down")

    return response.json()
```

**Prevents:** Unexpected quota exhaustion mid-month.

### 13. Widget Isolation (One Widget Failure ≠ Page Failure)

**Architecture principle:** Widgets should be completely independent.

**Bad coupling:**
```python
# ❌ BAD: News widget depends on price widget's data
crypto_price_widget.fetch()  # If this fails...
news_widget.fetch(price=crypto_price_widget.price)  # ...this can't run!
```

**Good isolation:**
```python
# ✅ GOOD: Each widget is self-contained
for widget in page.widgets:
    try:
        widget.fetch()
        widget.process()
        widget.render()
    except Exception:
        widget.render_error_state()
```

**Benefits:**
- Partial page success
- Easy to add/remove widgets
- Parallel execution possible

---

## Implementation Phases

| Phase | Focus | Deliverables | Duration |
|-------|-------|--------------|----------|
| **1. Core Framework** | Foundation | 3-stage pipeline (fetch/process/render), BaseWidget, config loader, cache system | Week 1 |
| **2. MVP Widgets** | Crypto essentials | 4 widgets: `crypto-price`, `crypto-price-chart`, `crypto-market-stats`, `news` | Week 2 |
| **3. Series System** | Multi-page support | Series config, page auto-discovery, index generation, CSS theming, templates | Week 3 |
| **4. Advanced Widgets** | Enhanced features | `crypto-fear-greed`, `reddit`, `crypto-events` | Week 4 |
| **5. Deployment** | Automation | GitHub Actions workflow, smart stage skipping, error handling, deployment | Week 5 |

**Milestone:** End of Phase 2 = Working Bitcoin dashboard with 4 widgets

**Post-MVP (optional):**
- Extract common template components (`components/timestamp.html`, `components/error-state.html`)
- Add more widgets based on user needs
- Performance optimization if needed

---

## Other Series Ideas (Future)

Beyond crypto, the same architecture works for many **publicly interesting** monitoring use cases:

### 1. Tech News Aggregator

**Pages:**
- `hacker-news.yaml` - HackerNews top stories
- `product-hunt.yaml` - ProductHunt trending products
- `ai-news.yaml` - AI/ML developments

**Widgets:**
- `hackernews-top` - Top 10 HackerNews posts with scores
- `producthunt-trending` - Today's top products
- `github-trending` - Trending repos (by language)
- `tech-releases` - Latest releases (frameworks, tools)
- `news` - Tech news from major outlets (reuse generic widget)
- `reddit` - r/programming, r/technews (reuse generic widget)

**Data source:** HackerNews API (free), ProductHunt API (free), GitHub API (free)

**Why public-facing:** Everyone interested in tech wants to see what's trending, not just personal projects.

### 2. Market Watch (Public Markets)

**Pages:**
- `indices.yaml` - Major market indices
- `big-tech.yaml` - FAANG stocks (Apple, Google, Microsoft, etc.)
- `commodities.yaml` - Gold, oil, silver

**Widgets:**
- `stocks-price` - Stock price for major companies
- `market-indices` - S&P 500, NASDAQ, Dow Jones charts
- `forex-rate` - Major currency pairs (USD/EUR, USD/JPY)
- `commodities-price` - Gold, oil, silver prices
- `market-movers` - Biggest gainers/losers today
- `news` - Market news (reuse generic widget)

**Data source:** Alpha Vantage (free tier), Yahoo Finance (via yfinance library)

**Why public-facing:** Tracking AAPL, TSLA, S&P 500 is universally interesting. No "your portfolio" - just popular stocks everyone watches.

### 3. Space & Science Dashboard

**Pages:**
- `iss.yaml` - International Space Station tracking
- `launches.yaml` - Upcoming rocket launches
- `astronomy.yaml` - Sky events tonight

**Widgets:**
- `iss-location` - Live ISS position on map
- `space-launches` - Next 10 rocket launches (SpaceX, NASA, etc.)
- `astronomy-events` - Visible planets, meteor showers, eclipses
- `nasa-apod` - NASA Astronomy Picture of the Day
- `space-weather` - Solar flares, aurora forecasts
- `news` - Space news (reuse generic widget)

**Data source:** Open-Notify (ISS), Launch Library API (launches), NASA APIs

**Why public-facing:** ISS tracking, SpaceX launches, astronomy events are broadly interesting.

### 4. Air Quality Monitor

**Pages:**
- `global-overview.yaml` - World's major cities
- `us-cities.yaml` - Top 20 US cities
- `asia-pacific.yaml` - Asian megacities

**Widgets:**
- `aqi-gauge` - Current AQI level with color coding
- `aqi-map` - Map view of multiple cities
- `aqi-trend` - Historical AQI chart (7-day)
- `health-recommendations` - Activity recommendations based on AQI
- `pollution-sources` - PM2.5, PM10, O3 breakdown
- `news` - Air quality news (reuse generic widget)

**Data source:** OpenAQ (free, comprehensive), IQAir (free tier)

**Why public-facing:** Public health data relevant to anyone planning outdoor activities or concerned about air quality.

### Widget Reusability Across Series

**Generic widgets work everywhere:**
- `news` - Used in crypto, tech, markets, space series
- `reddit` - Used in crypto (r/Bitcoin), tech (r/programming), markets (r/stocks)

**Domain widgets can be reused in related series:**
- `crypto-price` - Used in crypto series AND market watch series

**This demonstrates the power of the widget architecture** - build once, reuse across multiple series.

---

## Success Metrics

### Technical
- Page generation time: < 30 seconds for full rebuild
- Widget update time: < 5 seconds per widget
- Cache hit rate: > 80%
- API cost: < $5/month (using free tiers)

### User Experience
- New page setup: < 5 minutes
- Configuration complexity: 1 YAML file, < 30 lines
- Visual consistency: All widgets follow design system
- Mobile responsive: Works on all screen sizes

---

## Open Questions & Decisions Needed

| Question | Options | Recommendation |
|----------|---------|----------------|
| **LLM Usage** | Only news summaries vs broader usage | Start with news only, expand if valuable |
| **Chart Library** | Chart.js (simple) vs Plotly (interactive) | Chart.js - lighter, static is fine |
| **Mobile Design** | Stack all widgets vs simplified versions | Stack all - simpler to implement |
| **Error Handling** | Show error message vs hide widget | Show error - transparency is better |
| **Timestamp Display** | Relative ("5 min ago") vs absolute ("3:45 PM") | Relative for fresh data, absolute for old |

---

## Next Steps

1. Review and approve this design
2. Set up project structure
3. Implement Phase 1: Core framework
4. Build 1-2 prototype widgets
5. Create sample Bitcoin dashboard
6. Iterate based on real-world usage

