# GitHub Setup Guide

This guide walks you through deploying PeekDeck to GitHub Pages with automatic updates.

## Prerequisites

- A GitHub account
- This repository pushed to GitHub

## Step 1: Create Repository

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .
git commit -m "Initial commit: PeekDeck MVP"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/fathom-deck.git
git branch -M main
git push -u origin main
```

## Step 2: Configure GitHub Secrets

The workflow needs API keys to fetch data. Add these as repository secrets:

1. Go to your repo on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

Add these secrets:

| Secret Name | Value | Required? |
|-------------|-------|-----------|
| `GEMINI_API_KEY` | Your Gemini API key | Optional (no auth needed) |
| `COINGECKO_API_KEY` | Your CoinGecko API key | Optional (for future widgets) |

**Note:** Gemini's public API doesn't require authentication, so `GEMINI_API_KEY` can be left empty for now.

## Step 3: Enable GitHub Pages

1. Go to **Settings** → **Pages**
2. Under **Source**, select **Deploy from a branch**
3. Under **Branch**, select `gh-pages` and `/ (root)`
4. Click **Save**

## Step 4: Create Data Branch

The workflow uses a separate `data` branch to store generated content:

```bash
# The workflow will create this automatically on first run
# Or create it manually:
git checkout -b data
git push -u origin data
git checkout main
```

## Step 5: Enable Workflow

1. Go to **Actions** tab in your repo
2. If prompted, click **I understand my workflows, go ahead and enable them**
3. Click on **Update Widgets** workflow
4. Click **Run workflow** → **Run workflow** to trigger first run

## Step 6: Verify It Works

1. Wait for the workflow to complete (1-2 minutes)
2. Check the **Actions** tab for green checkmark
3. Visit: `https://YOUR_USERNAME.github.io/fathom-deck/crypto/bitcoin.html`

## Branch Structure

Your repo will have 3 branches:

- **`main`** - Code, configs, templates (you edit this)
- **`data`** - Generated content (docs/ + cache/) - auto-updated by workflow
- **`gh-pages`** - Deployed HTML for GitHub Pages - auto-updated from docs/

## Workflow Behavior

The workflow runs **every 5 minutes** and:

1. Checks which widgets need updating (based on `update_minutes` and cache)
2. Fetches data from APIs (only if needed)
3. Processes data (LLM summaries, etc.)
4. Renders HTML pages
5. Commits changes to `data` branch
6. Deploys to GitHub Pages

**Smart execution:** If no widgets need updating, the workflow completes in seconds without making API calls.

## Customizing Update Frequency

Edit `.github/workflows/update.yml`:

```yaml
on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes
    # - cron: '*/15 * * * *'  # Every 15 minutes
    # - cron: '0 * * * *'     # Every hour
```

Widget-specific frequency is controlled in `series/crypto/pages/*.yaml`:

```yaml
widgets:
  - type: crypto-price
    update_minutes: 5     # Updates every 5 min (if workflow runs)

  - type: news
    update_minutes: 60    # Updates every 60 min
```

## Monitoring

- **Workflow runs**: Check Actions tab
- **Artifacts**: Download `processing-artifacts` to debug failures
- **Cache state**: View `data/cache/widget_timestamps.json` in `data` branch

## Troubleshooting

### Workflow fails with "No module named 'peek_deck'"

This is handled by `PYTHONPATH` in the workflow. If it still fails, check that `src/peek_deck/` exists in your repo.

### API rate limits

- **Gemini**: 5M requests/month (very generous)
- **CoinGecko**: 10K requests/month on free tier

With 5-minute updates for Bitcoin:
- Gemini: ~8,640 requests/month (0.17% of limit)
- Should never hit limits with just Bitcoin

### Pages not updating

1. Check if workflow is enabled (Actions tab)
2. Verify `gh-pages` branch exists
3. Check Pages settings point to `gh-pages` branch

## Next Steps

Once deployed:

1. Add more pages (ethereum.yaml, etc.)
2. Add more widgets (news, charts)
3. Customize the theme in `series/crypto/config.yaml`
