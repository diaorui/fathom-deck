# Naming Convention & Centralized Configuration

This document explains how project naming is managed centrally in PeekDeck, making future name changes effortless.

## 📍 Single Source of Truth

**All project names are defined in one place:**
**`project_config.py`** (at project root)

```python
# Display name (user-facing, with capitalization)
PROJECT_NAME = "PeekDeck"

# Package name (Python import, lowercase with underscore)
PACKAGE_NAME = "peek_deck"  # ✅ Renamed from fathom_deck

# Repository/URL name (lowercase with hyphen)
REPO_NAME = "fathom-deck"  # TODO: Will rename to peek-deck when renaming repository

# Tagline
PROJECT_TAGLINE = "A glance is all you need"

# Description
PROJECT_DESCRIPTION = f"{PROJECT_NAME} is a configurable, widget-based monitoring system..."
```

## 🔄 How to Change the Project Name

**To rename the entire project, only update `project_config.py`!**

### Step 1: Update Central Config

Edit `project_config.py`:

```python
PROJECT_NAME = "NewName"
PROJECT_TAGLINE = "New tagline here"
```

### Step 2: That's It!

All references will automatically update:
- ✅ **Python code** - imports from `peek_deck` module
- ✅ **Templates** - uses `{{ project_name }}` and `{{ project_tagline }}`
- ✅ **Documentation** - manually updated references (see below)

## 📂 Where the Name is Used

### Automatic (No Action Needed)

These places **automatically** use the centralized config:

1. **Python Package Metadata** (`src/peek_deck/__init__.py`)
   - Imports: `from project_config import PROJECT_NAME`
   - Used in docstrings and version info

2. **HTML Templates** (`templates/pages/*.html`)
   - Page title: `<title>{{ page.name }} - {{ project_name }}</title>`
   - Navigation: `{{ project_name }}`
   - Footer: `Powered by {{ project_name }}`
   - Header: `<h1>{{ project_name }}</h1>`
   - Tagline: `<p>{{ project_tagline }}</p>`

3. **Render Pipeline** (`src/peek_deck/render.py`)
   - Passes to templates: `project_name=PROJECT_NAME, project_tagline=PROJECT_TAGLINE`

### Manual (Update After Name Change)

These files need **manual updates** when renaming:

1. **`README.md`** (line 1 and line 103)
   ```markdown
   # PeekDeck
   > **A glance is all you need.**
   ```

2. **`DESIGN.md`** (line 1 and line 3)
   ```markdown
   # PeekDeck Design Document
   > **A glance is all you need.**
   ```

3. **`SETUP.md`** (if mentions project name)

## 🚀 Template Usage Pattern

When creating new templates, always use variables instead of hardcoded names:

```html
<!-- ✅ GOOD: Use variable -->
<title>{{ page.name }} - {{ project_name }}</title>
<h1>{{ project_name }}</h1>
<p>{{ project_tagline }}</p>

<!-- ❌ BAD: Hardcoded name -->
<title>{{ page.name }} - PeekDeck</title>
<h1>PeekDeck</h1>
```

## 🔍 Quick Reference

| Context | Variable to Use | Example |
|---------|----------------|---------|
| Python code | `PROJECT_NAME` | `from peek_deck import PROJECT_NAME` |
| Jinja2 templates | `{{ project_name }}` | `<h1>{{ project_name }}</h1>` |
| Jinja2 templates | `{{ project_tagline }}` | `<p>{{ project_tagline }}</p>` |
| Documentation | Manual update | Edit `README.md`, `DESIGN.md` |

## ✅ Package Rename Completed

The Python package has been **successfully renamed** from `fathom_deck` to `peek_deck`.

**What was changed:**
- ✅ Directory renamed: `src/fathom_deck/` → `src/peek_deck/`
- ✅ All Python imports updated to use `peek_deck`
- ✅ Workflow entry points updated (`.github/workflows/update.yml`)
- ✅ CLI entry point updated (`src/peek_deck/__main__.py`)
- ✅ README.md and run.sh updated
- ✅ `project_config.py` updated to reflect new package name

**How to use:**
```bash
python -m peek_deck fetch    # Instead of fathom_deck
python -m peek_deck render
```

## 📝 Future Repository Renaming

When ready to rename the **GitHub repository**:

### Repository Name (from `fathom-deck` to `peek-deck`)

1. Update `project_config.py`:
   ```python
   REPO_NAME = "peek-deck"  # Remove TODO comment
   ```

2. Rename on GitHub:
   - Go to Settings → Rename repository
   - Update local remote: `git remote set-url origin https://github.com/USER/peek-deck.git`

3. Update documentation references to new URL

## ✅ Verification Checklist

After renaming, verify these locations:

- [ ] `project_config.py` - Updated `PROJECT_NAME` and `PROJECT_TAGLINE`
- [ ] `README.md` - Title and tagline match
- [ ] `DESIGN.md` - Title and tagline match
- [ ] Generated `docs/index.html` - Shows new name (run `python -m peek_deck render`)
- [ ] Generated `docs/{page}.html` - Breadcrumb shows new name

## 🎯 Benefits of This Approach

1. **Single edit point** - Change name in one place
2. **No missed references** - Templates auto-update
3. **Type-safe** - Python imports catch errors
4. **Future-proof** - Easy to add more config values
5. **Clear documentation** - This file explains everything

## 📚 Related Files

- **Central config:** `project_config.py`
- **Python init:** `src/peek_deck/__init__.py`
- **Renderer:** `src/peek_deck/render.py`
- **Page template:** `templates/pages/page.html`
- **Index template:** `templates/pages/index.html`

---

**Last updated:** 2025-11-22
**Current name:** PeekDeck
**Previous name:** FathomDeck
