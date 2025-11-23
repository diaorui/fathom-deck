# PeekDeck Design Document

> **A glance is all you need.**

## Overview

PeekDeck is a configurable, widget-based monitoring system that generates static dashboards for tracking various data sources. Users define pages with widgets, each widget fetches and visualizes specific data, and the system outputs static HTML pages deployed via GitHub Actions.

**First Use Case:** Cryptocurrency monitoring dashboards (Bitcoin, Ethereum, etc.)

**Design Principles:**
- **Generic by design** - widgets work across use cases (crypto, stocks, weather, etc.)
- **Practical over perfect** - use proven data sources, avoid hard problems
- **Minimal configuration** - users edit 1-2 YAML files to create new pages
- **Unified visual design** - consistent styling despite widget diversity
- **Flexible updates** - different widgets update at different frequencies

---

## Core Concepts

### 1. Pages
A **page** is a single dashboard with multiple widgets. Each page is self-contained and defines its own theme, icon, and widget layout.

**Examples:**
- `bitcoin.yaml` - Bitcoin monitoring page with price, news, and market stats widgets
- `ethereum.yaml` - Ethereum dashboard
- `ai.yaml` - AI news and developments

Pages are grouped by **category** (e.g., `crypto`, `tech`) for organization in the main index, but each page is independent.

### 2. Widgets
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
peek-deck/
├── src/peek_deck/           # Python source code
│   ├── core/                  # Core framework (BaseWidget, cache, renderer)
│   └── widgets/               # All widgets (flat structure)
│       ├── crypto_price.py
│       ├── crypto_price_chart.py
│       ├── crypto_market_stats.py
│       ├── google_news.py
│       └── ...
│
├── templates/                 # Jinja2 templates
│   ├── widgets/
│   │   ├── base.html          # Shared widget wrapper
│   │   ├── crypto-price.html
│   │   ├── crypto-market-stats.html
│   │   ├── google-news.html
│   │   └── ...
│   └── pages/
│       ├── page.html          # Page layout template
│       └── index.html         # Main index template
│
├── pages/                     # Page configurations (flat structure)
│   ├── bitcoin.yaml
│   ├── ethereum.yaml
│   ├── ai.yaml
│   └── ...
│
├── config/
│   └── index.yaml             # Optional: customize index grouping
│
├── data/
│   ├── raw/                   # Raw API responses (stage 1 output)
│   ├── processed/             # Processed data (stage 2 output)
│   └── cache/                 # Timestamp tracking, seen items, etc.
│
├── docs/                      # Generated HTML output (GitHub Pages)
│   ├── index.html             # Main index page (groups all pages)
│   ├── bitcoin.html
│   ├── ethereum.html
│   ├── ai.html
│   └── ...
│
└── .github/workflows/
    └── update.yml             # Smart workflow (runs every 5 min)
```

**What users interact with:**
- `pages/*.yaml` - Add new pages (self-contained configs)
- `config/index.yaml` - Optional: customize index grouping
- `templates/` - Widget and page templates (rarely need to edit)

**What gets generated:**
- `data/raw/` - Raw API responses from external sources (saved to data branch)
- `data/processed/` - Processed/enriched data ready for rendering (saved to data branch)
- `data/cache/` - Metadata (timestamps, seen items) for smart updates (saved to data branch)
- `docs/` - Static HTML files deployed to GitHub Pages (saved to data branch)

---

## Configuration System

### Page Configuration (`pages/bitcoin.yaml`)

```yaml
# Page metadata
id: bitcoin
name: Bitcoin
description: Live Bitcoin monitoring dashboard
icon: "₿"
enabled: true

# Category for index grouping
category: crypto

# Visual theme (CSS variables)
theme:
  primary_color: "#f7931a"      # Bitcoin orange
  background: "#1a1a1a"         # Dark mode
  text_color: "#ffffff"
  card_background: "#2d2d2d"
  border_radius: "8px"

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
  - type: google-news
    size: full            # 12 columns
    params:
      query: "Bitcoin"    # Google News search query
      max_items: 5
    update_minutes: 60    # Update hourly

  # Row 3: Fear & Greed + Reddit
  - type: crypto-fear-greed
    size: medium
    update_minutes: 360   # Update every 6 hours

  - type: reddit-posts
    size: medium
    params:
      subreddit: "Bitcoin"   # r/Bitcoin
    update_minutes: 120
```

**Key Design Decisions:**

1. **Self-contained**: Each page defines its own theme, icon, and category
2. **Parameter inheritance**: Page-level params (symbol, coin_id) passed to all widgets
3. **Grid-based sizing**: `small` (3 cols), `medium` (6 cols), `large` (9 cols), `full` (12 cols)
4. **Flexible updates**: Each widget declares its own `update_minutes`
5. **Category grouping**: Pages with same category grouped together in index.html

### Index Configuration (`config/index.yaml`)

**Optional file** to customize how pages are grouped and displayed in index.html:

```yaml
# Category definitions (optional - can be inferred from pages)
groups:
  - id: crypto
    name: "Cryptocurrency"
    icon: "💰"
    description: "Track crypto prices, news, and market sentiment"

  - id: tech
    name: "Technology"
    icon: "💻"
    description: "AI and tech developments"

# Featured pages (shown at top of index)
featured: [bitcoin, ai]

# Sort order within groups
sort_by: name  # Options: name, category, recent
```

**Note:** If `config/index.yaml` doesn't exist, the system auto-generates index by discovering all pages and grouping by category.

---

## Widget System Architecture

### Widget Loading

Widgets are loaded dynamically based on page configs:
- Page config specifies `type: crypto-price`
- Pipeline imports `src/peek_deck/widgets/crypto_price.py` (converts kebab-case to snake_case)
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
| **crypto-price** | Gemini | Current price, 24h change, volume | Small | 5 | 120 req/min, live exchange data |
| **crypto-price-chart** | Gemini | Price history line chart (24h/7d/30d/90d/1y) | Medium/Large | 10 | Uses Chart.js with candles endpoint, tabbed interface |
| **crypto-market-stats** | CoinGecko | Market cap, supply, volume, ATH/ATL | Small/Medium | 30 | CoinGecko has fundamentals Gemini lacks |
| **google-news** | Google News RSS | Top 8 articles with source favicons | Full | 30 | RSS feed, no auth required, shows "View All" link |
| **reddit-posts** | Reddit API | Top 8 posts from subreddit | Full | 15 | JSON endpoint, no auth, shows "View All" link |

### Advanced Widgets (Post-MVP)

| Widget | Data Source | Content | Size | Update (min) | Notes |
|--------|-------------|---------|------|--------------|-------|
| **crypto-fear-greed** | Alternative.me | Fear/Greed score (0-100) + gauge | Medium | 360 | Free API, updates daily |
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
| **Google News RSS** | News | Yes (no auth) | Good | No strict limit | Latest news via RSS, query by coin name |
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
| **crypto-price** | Gemini | 5M/month limit, no auth, live exchange data | Coinpaprika |
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
- Load page configs from `pages/`
- Render Jinja2 templates with data
- Generate HTML files to `docs/`
- Generate `docs/index.html` (grouped by category)
- Update `data/cache/last_render.json` with timestamps

**Output:** `docs/bitcoin.html`, `docs/ethereum.html`, `docs/index.html`

**Benefits:**
- Fast, no external calls
- Can iterate on templates quickly
- Re-render anytime without cost

### Pipeline Flow

```
┌─────────────┐
│   Config    │ (pages/bitcoin.yaml)
└──────┬──────┘
       │
       ▼
┌─────────────┐     data/raw/           ┌─────────────┐     data/processed/    ┌─────────────┐
│   Fetch     │ ──────────────────────> │   Process   │ ──────────────────────> │   Render    │
│  (APIs)     │    bitcoin_price.json   │   (LLM)     │   bitcoin_price.json   │ (Templates) │
└─────────────┘                         └─────────────┘                        └──────┬──────┘
                                                                                       │
                                                                                       ▼
                                                                                  docs/
                                                                                  bitcoin.html
```

**Smart execution:**
- Fetch only runs for widgets due for update
- Process only runs if new raw data exists
- Render only runs if processed data changed
- Can force full pipeline or run stages independently

---

## SEO & AEO Strategy

### Overview

PeekDeck generates static HTML dashboards that need to be discoverable by both traditional search engines (Google, Bing) and AI-powered answer engines (ChatGPT, Perplexity, Gemini).

**Key Statistics (2025):**
- 65% of searches end without a click (zero-click searches)
- 34% of U.S. adults use ChatGPT for search
- Pages with schema markup see 30-50% increase in search impressions
- Perplexity traffic converts at 20-30% on well-structured pages
- Listicle format accounts for 32% of all LLM citations

### Current Gaps

**Missing SEO components:**
- Meta descriptions, Open Graph tags, Twitter Cards
- Structured data (JSON-LD schema)
- Canonical URLs, robots meta tags
- Sitemap.xml, robots.txt
- Favicon & app icons

**Missing AEO optimizations:**
- Year markers for recency (2025)
- Listicle content structure
- Descriptive widget headers
- Page summaries for AI extraction

### Architecture Design

#### 1. SEO Configuration in Page YAML

Add optional `seo` section to page configs:

```yaml
# pages/bitcoin.yaml
seo:
  title: "Bitcoin Dashboard 2025 - Live Price, Charts & Market Stats"
  description: "Track Bitcoin price, market cap, and news with live updates..."
  keywords: ["bitcoin", "BTC", "cryptocurrency", "price tracker"]
  og_image: "https://yourdomain.com/images/bitcoin-og.png"  # Optional
```

**Fallback behavior:** If `seo` section missing, auto-generate from page name/description/widgets.

#### 2. SEOManager Class

Create `src/peek_deck/core/seo_manager.py` with:

**Responsibilities:**
- Generate SEO metadata (title, description, keywords, canonical URL)
- Auto-generate from page config if custom SEO not provided
- Create JSON-LD structured data (WebApplication, BreadcrumbList, Dataset schemas)
- Generate sitemap.xml (all pages + index with priorities)
- Generate robots.txt (allow all, point to sitemap)

**Key methods:**
- `generate_metadata(page_config, custom_seo)` → SEOMetadata
- `generate_structured_data(page_config, metadata)` → JSON-LD dict
- `generate_sitemap(pages, base_url)` → sitemap.xml string
- `generate_robots_txt(base_url)` → robots.txt string

#### 3. Meta Tags in Page Template

Update `templates/pages/page.html` with comprehensive meta tags:

**Categories:**
- **Primary:** title, description, keywords, author, robots, canonical
- **Open Graph:** og:type, og:url, og:title, og:description, og:image, og:site_name
- **Twitter:** twitter:card, twitter:url, twitter:title, twitter:description, twitter:image
- **Icons:** favicon (16x16, 32x32), apple-touch-icon, manifest
- **Additional:** theme-color (from page theme), updated timestamp

#### 4. Structured Data (JSON-LD)

Add `<script type="application/ld+json">` to page template with:

**Schema types:**
- `WebApplication` - Dashboard metadata (name, description, URL, author, dateModified)
- `BreadcrumbList` - Navigation hierarchy (Home → Page)
- `Dataset` - Data collection metadata (optional, for data-focused pages)

**Format:** JSON-LD (Google's recommended format, easier to maintain)

#### 5. Integration in render.py

**Render stage modifications:**
1. Initialize SEOManager with base_url and project_name
2. For each page: generate SEO metadata and structured data
3. Pass to template via `seo` and `structured_data` context variables
4. After all pages: generate sitemap.xml and robots.txt in docs/

### AEO Content Optimization

**Decision: Minimal AEO optimizations for live dashboards**

Unlike static content (blog posts, articles), PeekDeck displays **live data** that updates frequently. Aggressive AEO tactics don't fit this use case well:

**What we skipped:**
- ❌ **Year markers in titles** - Live dashboards with hourly updates don't need "2025" labels. Widget timestamps prove freshness better than a year in the title. Would look outdated when shared/bookmarked later.
- ❌ **Listicle summaries** - "What's on this dashboard" lists are redundant and annoying for users who came to see actual data, not a list of what they're about to see. Hurts UX without clear benefit.

**What provides natural AEO value:**
- ✅ **Descriptive page names** - "Bitcoin", "Ethereum", "Artificial Intelligence" (clear topics)
- ✅ **Comprehensive single-source** - Each dashboard is self-contained with all relevant information
- ✅ **Structured data** - JSON-LD WebApplication schema signals what the page contains
- ✅ **Meta descriptions** - Clearly describe dashboard purpose
- ✅ **Regular updates** - Sitemap shows `changefreq: hourly`, signaling freshness

**Philosophy:** For live dashboards, data freshness speaks louder than SEO tricks. Focus on accurate metadata and let the content quality drive discoverability.

### Implementation Status

**Phase 1: Core SEO** ✅ Complete
- Meta tags in page/index templates (description, author, robots, theme-color)
- Canonical URLs with base_url from config/index.yaml
- Open Graph tags for social sharing
- Twitter Card meta tags
- Sitemap.xml generation (all pages with priorities and changefreq)
- Robots.txt generation (allow all, points to sitemap)

**Phase 2: Structured Data** ✅ Complete
- JSON-LD WebApplication schema for dashboard pages
- JSON-LD WebSite schema for index page
- BreadcrumbList navigation hierarchy

**Phase 3: AEO Optimization** ✅ Simplified
- Decided against year markers (not needed for live data)
- Decided against listicle summaries (hurts UX)
- Focus on natural signals: descriptive names, structured data, fresh content

**Phase 4: Social & Advanced** ⏸️ Optional/Future
- Programmatic OG image generation
- FAQ schema for common questions
- Widget-specific structured data

### Expected Results

**SEO Benefits:**
- Complete indexing coverage via sitemap.xml
- Rich results potential from structured data (WebApplication schema)
- Better social sharing appearance (Open Graph + Twitter Cards)
- Clear crawling guidance via robots.txt
- Proper canonical URLs prevent duplicate content issues

**AEO Benefits:**
- Structured data helps LLMs understand page purpose
- Descriptive page names and meta descriptions provide clear context
- Hourly update frequency signals fresh, relevant data
- Self-contained dashboards are easy for AI to extract and summarize

**Measurement:**
- Monitor in Google Search Console after deployment
- Track social sharing appearance via Open Graph validators
- Test structured data with Google Rich Results Test

### Configuration

SEO settings are configured in `config/index.yaml`:

```yaml
# Base URL for deployment (required for canonical URLs, sitemap, Open Graph)
base_url: "https://yourdomain.com"

# Optional: Custom SEO metadata for index page
seo:
  description: "Your custom index description"
```

**Why config/index.yaml:**
- Deployment-specific (different per user)
- Already required for index page configuration
- Single location for site-wide settings

### References

SEO Best Practices:
- [Meta tags in SEO](https://searchengineland.com/guide/meta-tags)
- [SEO Meta Data Best Practices for 2025](https://saleshive.com/blog/seo-meta-data-best-practices-rankings-2025/)
- [SEO HTML Tags 2025](https://mangools.com/blog/seo-html-tags/)

AEO Best Practices:
- [Answer Engine Optimization](https://neilpatel.com/blog/answer-engine-optimization/)
- [AEO for ChatGPT, Perplexity, and Gemini](https://www.poweredbysearch.com/blog/aeo-llm-seo-best-practices/)
- [Complete Guide to AEO 2025](https://www.o8.agency/blog/ai/answer-engine-optimization-guide)

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
        run: python -m peek_deck fetch
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          COINGECKO_API_KEY: ${{ secrets.COINGECKO_API_KEY }}

      - name: Stage 2 - Process data
        run: python -m peek_deck process
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}  # For LLM calls

      - name: Stage 3 - Render HTML
        run: python -m peek_deck render

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

### Goal: Create New Page with One File

**Scenario:** User wants to add Cardano dashboard

**Step 1:** Create `pages/cardano.yaml`

```yaml
id: cardano
name: Cardano
icon: "₳"
category: crypto

# Theme (copy from bitcoin.yaml for consistent crypto styling)
theme:
  primary_color: "#f7931a"
  background: "#1a1a1a"
  text_color: "#ffffff"
  card_background: "#2d2d2d"
  border_radius: "8px"

params:
  symbol: ADA
  coin_id: cardano

# Copy widget config from bitcoin.yaml or customize
widgets:
  - type: crypto-price
    size: small
  - type: google-news
    size: full
    params:
      query: "Cardano ADA"  # Customize search query per page
```

**Step 2:** That's it!

The system auto-discovers `cardano.yaml` in `pages/` and:
1. Generates `docs/cardano.html`
2. Adds it to `docs/index.html` under the "Cryptocurrency" section (grouped by `category: crypto`)

**For 10 or fewer pages:** Simply copy-paste theme values across pages in the same category. This is simpler than managing shared configs.

### Advanced Customization (Optional)

Users can override defaults:

| Level | What to Override | Example |
|-------|------------------|---------|
| **Widget template** | Individual widget HTML | `template: custom/my_price.html` in widget config |
| **Page template** | Entire page layout | `template: custom/page.html` in page config |
| **Theme colors** | Per-page unique theme | `theme: { primary_color: "#0033AD" }` |

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
    id: str = Field(pattern=r'^[a-z0-9-]+$')
    name: str
    category: str = 'general'  # For index grouping
    theme: Optional[dict] = None
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

## Carousel Widget Design Principles

Many widgets use a horizontal carousel layout for browsing content (news, papers, repos, posts). These design principles ensure carousels look polished and professional:

### Core Layout Principles

**1. Fixed card dimensions**
- Every card has the same width (typically 280px on desktop, 100% on mobile)
- Creates visual rhythm and predictable horizontal scanning
- Users build muscle memory for scrolling distance
- Prevents jarring size changes that break focus

**2. Uniform layout within carousel**
- Every card in the same carousel follows identical structure
- Reduces cognitive load - users learn the pattern once
- Information is always in expected locations (title top, metadata bottom)
- Enables fast scanning without re-learning each card

**3. Reserved space for all elements**
- Every element has fixed height, even when empty
- Use `min-height: calc()` to reserve space for optional content
- Prevents layout shift - cards don't jump when scrolling
- Professional polish and visual stability

### Information Hierarchy

**4. Three-part card structure**
- **Top**: Thumbnail/preview image (140px height)
- **Middle**: Main content (title, description) with `flex: 1`
- **Bottom**: Metadata/actions (stats, links, timestamps)
- Natural reading order: preview → content → details
- Clear visual hierarchy guides the eye

**5. Metadata pinned to bottom**
- Use `margin-top: auto` to push metadata to bottom
- Consistent location for timestamps, links, stats
- Users know exactly where to look for actions
- Creates visual anchor point across all cards

### Content Handling

**6. Graceful empty states**
- Placeholder images (emoji via `::before`) for missing thumbnails
- Maintains visual balance and completeness
- Empty space looks broken; placeholder shows intentional design
- Subtle emoji maintains brand personality without overwhelming

**7. Controlled overflow**
- Use `-webkit-line-clamp` with `overflow: hidden` for text
- Multi-line title: 2 lines with `line-height: 1.4`
- Single-line metadata: `white-space: nowrap` with `text-overflow: ellipsis`
- One verbose title doesn't break the entire layout
- Forces uniform information density

**8. Consistent dimensions**
- Thumbnails: 140px height across all carousel widgets
- Spacing: 6-10px margins, standardized across widgets
- Line heights: 1.4 for multi-line content, 1.2 for single-line
- Cross-widget familiarity - users build mental model
- Creates visual harmony despite different content types

### Navigation

**9. "View All" card at end**
- Final card in carousel links to full view on source site
- Clear call-to-action without disrupting carousel flow
- Suggests more content exists beyond preview
- Natural endpoint to scrolling
- Consistent pattern across all carousel widgets

**10. Responsive image containers with aspect-ratio**
- Use CSS `aspect-ratio` property, not fixed heights
- Maintains correct proportions across all screen sizes
- Standard ratios: 2:1 for most platforms (GitHub, Reddit, HackerNews, Google News), 1.85:1 for HuggingFace
- Same aspect ratio on desktop and mobile - only override `background-size` when needed
- Desktop: `background-size: contain` for GitHub (no cropping), `cover` for others (fills space)
- Mobile: Can switch to `contain` (e.g., HuggingFace) to prevent cropping on small screens
- Benefits: More maintainable (adapts to card width changes), explicit intent (ratio visible in code), no layout shift

```css
/* ✅ GOOD: Responsive with aspect-ratio */
.thumbnail {
    width: 100%;
    aspect-ratio: 2 / 1;  /* Explicit, maintainable */
    background-size: cover;
}

@media (max-width: 768px) {
    .thumbnail {
        background-size: contain;  /* Only override what changes */
    }
}

/* ❌ BAD: Fixed height breaks on different card widths */
.thumbnail {
    width: 100%;
    height: 140px;  /* Only correct for one specific width */
}
```

### Why These Principles Matter

These aren't just code patterns - they solve real UX problems:

- **Layout shift** destroys user trust (principle 3)
- **Inconsistent structure** forces users to re-learn each card (principle 2)
- **Empty space** looks broken and unprofessional (principle 6)
- **Overflow content** breaks visual rhythm (principle 7)
- **Random dimensions** creates visual chaos (principles 1, 8)
- **Fixed heights** break on responsive layouts (principle 10)

Following these principles creates carousels that feel polished, professional, and easy to scan - even when displaying very different content types (papers vs posts vs repos). The aspect-ratio approach ensures images look perfect on any screen size without manual height calculations.

---

## Timezone Handling

### The Problem: Server Time vs User Time

PeekDeck has a unique timezone challenge:
- **Server time**: GitHub Actions runs in UTC
- **Data timestamps**: APIs return timestamps in various timezones (UTC, local, etc.)
- **User time**: Viewers of the dashboard are in different timezones worldwide
- **Static HTML**: No server-side rendering to convert timestamps per-user

### Design Principle: Store UTC, Display Local

**All timestamps MUST be stored in UTC internally, converted to user's local timezone in the browser.**

### Implementation Rules

**Rule 1: Always use `datetime.now(timezone.utc)` in Python**
```python
# ✅ CORRECT: UTC-aware timestamp
from datetime import datetime, timezone
fetched_at = datetime.now(timezone.utc).isoformat()

# ❌ WRONG: Uses server's local timezone
fetched_at = datetime.now().isoformat()  # Bug! Will break if server timezone changes
```

**Rule 2: Store timestamps in UTC in data files**
```json
{
  "fetched_at": "2025-01-15T10:30:00+00:00",  // ✅ UTC timezone explicit
  "articles": [
    {
      "pub_date": 1705318200.0  // ✅ Unix timestamp (always UTC)
    }
  ]
}
```

**Rule 3: Use `data-timestamp` attribute for client-side conversion**
```html
<!-- Backend passes UTC timestamp -->
<small data-timestamp="{{ timestamp_iso }}">Updated {{ timestamp_iso }}</small>

<!-- JavaScript converts to user's local time -->
<script>
  const elem = document.querySelector('[data-timestamp]');
  const utcTimestamp = elem.getAttribute('data-timestamp');
  const localTime = formatTimeAgo(utcTimestamp);  // Converts to user's timezone
  elem.textContent = localTime;  // "5m ago" in user's timezone
</script>
```

**Rule 4: JavaScript Date() handles timezone conversion automatically**
```javascript
// Browser's Date() constructor automatically converts to user's local timezone
const utcString = "2025-01-15T10:30:00Z";  // UTC timestamp from backend
const date = new Date(utcString);  // Converts to user's browser timezone

// Example: User in PST sees "Jan 15, 2:30 AM"
//          User in JST sees "Jan 15, 7:30 PM"
```

### Common Timezone Bugs

**Bug 1: Cache update scheduling with local time**
```python
# ❌ WRONG: Compares UTC timestamp with local time
last_update = datetime.fromisoformat("2025-01-15T10:30:00+00:00")  # UTC
time_since = datetime.now() - last_update  # Local time! Breaks if server is not UTC

# ✅ CORRECT: Both in UTC
last_update = datetime.fromisoformat("2025-01-15T10:30:00+00:00")
time_since = datetime.now(timezone.utc) - last_update
```

**Bug 2: Mixing aware and naive datetimes**
```python
# ❌ WRONG: Cannot compare naive and aware datetimes
utc_time = datetime.now(timezone.utc)  # Timezone-aware
local_time = datetime.now()  # Timezone-naive
diff = utc_time - local_time  # TypeError!

# ✅ CORRECT: Both timezone-aware
utc_time = datetime.now(timezone.utc)
other_time = datetime.fromisoformat("2025-01-15T10:30:00Z").replace(tzinfo=timezone.utc)
diff = utc_time - other_time
```

**Bug 3: Forgetting to parse timezone from ISO strings**
```python
# ❌ WRONG: Strips timezone information
timestamp = "2025-01-15T10:30:00+00:00"
dt = datetime.fromisoformat(timestamp.replace("+00:00", ""))  # Loses timezone!

# ✅ CORRECT: Preserves timezone
dt = datetime.fromisoformat(timestamp)  # Keeps timezone info
```

### Files That Must Use UTC

| File | Lines to Check | Reason |
|------|---------------|--------|
| `cache.py` | All `datetime.now()` calls | Cache timestamps compared across workflow runs |
| `render.py` | `generated_at` timestamp | Consistency with widget timestamps |
| `url_fetch_manager.py` | HTTP cache TTL | In-memory cache persists across widget fetches |
| `url_metadata.py` | Metadata cache TTL | File-based cache persists across runs |
| `utils.py` | Relative time calculations | Must match UTC timestamps from widgets |
| All widgets | `fetched_at` timestamp | Displayed to users in multiple timezones |

### Testing Timezone Correctness

**Test 1: Verify UTC storage**
```bash
# Check that all timestamps in data files are UTC
grep -r "fetched_at" data/processed/
# Should see: "2025-01-15T10:30:00+00:00" or "2025-01-15T10:30:00Z"
```

**Test 2: Simulate different server timezones**
```bash
# Run locally with different TZ to verify code doesn't break
TZ=America/Los_Angeles python -m peek_deck fetch
TZ=Asia/Tokyo python -m peek_deck fetch
# Cache should still work correctly
```

**Test 3: Browser timezone conversion**
```javascript
// Open browser console, change system timezone, reload page
// Timestamps should update to show correct "X ago" relative to new timezone
```

### Why This Matters

**GitHub Actions runs in UTC** - If code uses local time, it works in CI but breaks when run locally in other timezones.

**Users are worldwide** - A dashboard generated at 10:00 UTC should show:
- "10:00 AM" to London user
- "2:00 AM" to Los Angeles user
- "7:00 PM" to Tokyo user

**Cache consistency** - If cache uses local time, widget update scheduling breaks when:
- Running locally vs in CI
- Moving server to different region
- Daylight saving time changes

**Static HTML** - Can't do server-side timezone conversion per-user. Must use JavaScript to convert UTC → user's local time.

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
# src/peek_deck/core/http_cache.py
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

**Problem:** `python -m peek_deck.fetch` fails in GitHub Actions:
```
ModuleNotFoundError: No module named 'peek_deck'
```

**Solution:** Set PYTHONPATH in workflow:
```yaml
steps:
  - name: Stage 1 - Fetch
    run: |
      export PYTHONPATH="${PYTHONPATH}:${GITHUB_WORKSPACE}/src"
      python -m peek_deck.fetch
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

### 14. Text Overflow Prevention in Carousel Cards (Critical for Consistent Card Width)

**Problem:** Long text (especially links inside flex containers) can push carousel cards wider than their assigned width, breaking the layout on mobile where card width is dynamic.

**Root cause:** Flexbox allows children to grow beyond parent width unless explicitly constrained at EVERY level of nesting.

**Wrong approach:**
```css
/* ❌ BAD: Only constraining the card */
.carousel-card {
    max-width: 100%;
}

.card-title a {
    overflow: hidden;
    text-overflow: ellipsis;
}
/* Long text in <a> still pushes card wider! */
```

**Correct approach - Apply `min-width: 0` at EVERY flex container level:**

```css
/* ✅ GOOD: Constrain entire flex chain */
.carousel-card {
    max-width: 100%;
    min-width: 0; /* Allow flex children to shrink below content size */
}

.card-content {
    min-width: 0; /* CRITICAL: Must propagate down */
}

.card-title {
    min-width: 0; /* At every level */
}

.card-meta {
    min-width: 0; /* Don't skip any containers */
}

.card-meta-line {
    min-width: 0; /* All the way down */
}
```

**Special handling for `<a>` tags:**

**Multi-line titles (using `-webkit-line-clamp`):**
```css
/* ✅ GOOD: Keep <a> inline for line-clamp to work */
.title {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    overflow: hidden;
    min-width: 0;
}

.title a {
    /* NO display: block - breaks line-clamp! */
    color: inherit;
    text-decoration: none;
}
```

**Single-line names (using `white-space: nowrap`):**
```css
/* ✅ GOOD: <a> needs overflow styles */
.name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    min-width: 0;
}

.name a {
    display: block; /* Needed for overflow to work */
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
```

**Exception: Tags/badges that need to wrap:**
```css
/* ✅ GOOD: Some meta-lines need wrapping (e.g., tags) */
.meta-line {
    flex-wrap: nowrap; /* Default: single line with ellipsis */
    overflow: hidden;
    min-width: 0;
}

.meta-line.tags-line {
    flex-wrap: wrap; /* Exception: Allow tags to wrap within fixed height */
    min-height: calc((0.7rem + 4px) * 2 + 4px); /* Reserve space for 2 rows */
    max-height: calc((0.7rem + 4px) * 2 + 4px); /* Clip overflow */
}
```

**The flex overflow chain:**
```
.carousel-card (min-width: 0) ✓
  └─ .card-content (min-width: 0) ✓
      ├─ .card-title (min-width: 0) ✓
      │   └─ a (inline for line-clamp) ✓
      ├─ .card-organization (min-width: 0) ✓
      │   └─ a (block + overflow for single-line) ✓
      └─ .card-meta (min-width: 0) ✓
          └─ .card-meta-line (min-width: 0) ✓
```

**Why this matters:**
- Missing `min-width: 0` at ANY level breaks the entire chain
- Long organization names, titles, or URLs will push cards wider
- Especially critical on mobile where card width is dynamic (`calc(85% - 8px)`)
- Creates inconsistent card widths within the same carousel

**From experience:**
- Check EVERY text container in the component
- Don't assume `max-width: 100%` alone is sufficient
- Test with very long text in every field
- `min-width: 0` is NOT redundant - it's essential for flex overflow

### 15. Image Fallback in Carousel Cards (Handling Load Failures)

**Problem:** Using `background-image` for thumbnails provides no way to detect when images fail to load (broken URLs, 404s, network errors).

**Wrong approach:**
```html
<!-- ❌ BAD: No fallback when background-image fails -->
<div class="thumbnail" style="background-image: url('{{ post.thumbnail }}');"></div>
```

**Correct approach - Use `<img>` with `onerror` and layered fallback:**

**CSS (layering approach):**
```css
.thumbnail {
    width: 100%;
    aspect-ratio: 2 / 1;
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: rgba(255, 255, 255, 0.03);
}

/* Fallback icon - always visible in background */
.thumbnail::before {
    content: "💬";
    font-size: 3rem;
    opacity: 0.3;
    z-index: 0;
    position: relative;
}

/* Image overlays icon when it loads successfully */
.thumbnail img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    position: absolute;
    top: 0;
    left: 0;
    z-index: 1; /* Covers fallback icon */
}
```

**HTML:**
```html
<div class="thumbnail">
    {% if post.thumbnail %}
    <img src="{{ post.thumbnail }}"
         alt="{{ post.title }}"
         onerror="this.style.display='none'"
         loading="lazy">
    {% endif %}
</div>
```

**How it works:**
1. **Fallback icon** always present at `z-index: 0` (background layer)
2. **Image loads successfully** → covers icon at `z-index: 1`
3. **Image fails to load** → `onerror` hides img, revealing icon
4. **No thumbnail** → just shows icon (no img tag)

**Why this approach:**
- ✅ Handles broken/invalid URLs
- ✅ Handles network failures
- ✅ Handles 404s and server errors
- ✅ Graceful degradation - always shows something
- ✅ No layout shift - container size fixed by `aspect-ratio`
- ✅ `loading="lazy"` for performance

**Alternative (JavaScript-based):**
If you need more control, use `onload` to hide the fallback:
```html
<div class="thumbnail">
    <div class="fallback-icon">💬</div>
    <img src="{{ url }}"
         onload="this.previousElementSibling.style.display='none'"
         onerror="this.style.display='none'">
</div>
```

**Why layering > background-image:**
- `background-image` has no error event
- Can't detect when external URLs fail
- No way to show fallback UI
- Silent failures create broken-looking cards

**From experience:**
- Always provide fallback for external images (Reddit, news sites, etc.)
- Test with intentionally broken URLs
- Use `object-fit: cover` to maintain aspect ratio
- Consider adding blur-up placeholder for better UX

---

## Implementation Phases

| Phase | Focus | Deliverables | Duration |
|-------|-------|--------------|----------|
| **1. Core Framework** | Foundation | 3-stage pipeline (fetch/process/render), BaseWidget, config loader, cache system | Week 1 |
| **2. MVP Widgets** | Crypto essentials | 4 widgets: `crypto-price`, `crypto-price-chart`, `crypto-market-stats`, `google-news` | Week 2 |
| **3. Page System** | Multi-page support | Page config loader, index generation (grouped by category), CSS theming, templates | Week 3 |
| **4. Advanced Widgets** | Enhanced features | `crypto-fear-greed`, `reddit-posts`, `crypto-events` | Week 4 |
| **5. Deployment** | Automation | GitHub Actions workflow, smart stage skipping, error handling, deployment | Week 5 |

**Milestone:** End of Phase 2 = Working Bitcoin dashboard with 4 widgets

**Post-MVP (optional):**
- Extract common template components (`components/timestamp.html`, `components/error-state.html`)
- Add more widgets based on user needs
- Performance optimization if needed

---

## Other Page Ideas (Future)

Beyond crypto, the same architecture works for many **publicly interesting** monitoring use cases. Simply create new page configs and group them by category:

### 1. Tech News Aggregator

**Pages:**
- `hacker-news.yaml` - HackerNews top stories
- `ai-news.yaml` - AI/ML developments

**Widgets:**
- `hackernews-top` - Top 10 HackerNews posts with scores
- `github-trending` - Trending repos (by language)
- `tech-releases` - Latest releases (frameworks, tools)
- `news` - Tech news from major outlets (reuse generic widget)
- `reddit` - r/programming, r/technews (reuse generic widget)

**Data source:** HackerNews API (free), GitHub API (free)

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

### Widget Reusability Across Pages

**Generic widgets work everywhere:**
- `google-news` - Used in crypto, tech, markets, space pages
- `reddit-posts` - Used in crypto (r/Bitcoin), tech (r/programming), markets (r/stocks)

**Domain widgets can be reused in related pages:**
- `crypto-price` - Used in Bitcoin, Ethereum, Cardano pages AND market watch pages

**This demonstrates the power of the widget architecture** - build once, reuse across multiple pages.

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

