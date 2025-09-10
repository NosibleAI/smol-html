![Logo](https://github.com/NosibleAI/nosible-py/blob/main/docs/_static/readme.png?raw=true)

# smol-html

Small, dependable HTML cleaner/minifier with sensible defaults.

### 📦 Installation

```bash
pip install smol-html
```

### ⚡ Installing with uv 

```bash
uv pip install smol-html
```

## Quick Start

Clean an HTML string (or page contents):

```python
from smol_html import SmolHtmlCleaner

html = """
<html>
  <head><title> Example </title></head>
  <body>
    <div>  Hello <span> world </span> </div>
  </body>
</html>
"""

# All constructor arguments are keyword-only and optional.
cleaner = SmolHtmlCleaner()
cleaned = cleaner.clean(raw_html=html)

print(cleaned)
```

## Customization

`SmolHtmlCleaner` exposes keyword-only parameters with practical defaults. You can:
- Pass overrides to the constructor, or
- Adjust attributes on the instance after creation.

```python
from smol_html import SmolHtmlCleaner

cleaner = SmolHtmlCleaner()
cleaner.attr_stop_words.add("advert")  # e.g., add a custom stop word
```

## Usage Examples

Minimal:

```python
from smol_html import SmolHtmlCleaner

cleaner = SmolHtmlCleaner()
out = cleaner.clean(raw_html="<p>Hi <!-- note --> <a href='x'>link</a></p>")
```

Customize a few options:

```python
from smol_html import SmolHtmlCleaner

cleaner = SmolHtmlCleaner(
    attr_stop_words={"nav", "advert"},
    remove_header_lists=False,
    minify=True,
)

out = cleaner.clean(raw_html="<p>Hi</p>")
```

## Parameter Reference

To improve readability, the reference is split into two tables:
- What it does and when to change
- Types and default values

### What It Does

| Parameter | What it does | When to change |
|---|---|---|
| `non_text_to_keep` | Whitelist of empty/non-text tags to preserve (e.g., images, figures, tables, line breaks). | If important non-text elements are being removed or you want to keep/drop more empty tags. |
| `attr_stop_words` | Tokens matched against `id`/`class`/`role`/`item_type` on small elements; matches are removed as likely non-content. | Add tokens like `advert`, `hero`, `menu` to aggressively drop UI chrome, or remove tokens if content is lost. |
| `remove_header_lists` | Removes links/lists/images within `<header>` to reduce nav clutter. | Set `False` if your header contains meaningful content you want to keep. |
| `remove_footer_lists` | Removes links/lists/images within `<footer>` to reduce boilerplate. | Set `False` for content-heavy footers you need. |
| `minify` | Minifies output HTML using `minify_html`. | Set `False` for readability or debugging; use `--pretty` in the CLI. |
| `minify_kwargs` | Extra options passed to `minify_html.minify`. | Tune minification behavior (e.g., whitespace, comments) without changing cleaning. |
| `meta` | lxml Cleaner option: remove `<meta>` content when `True`. | Usually leave `False`; enable only for strict sanitation. |
| `page_structure` | lxml Cleaner option: remove page-structure tags (e.g., `<head>`, `<body>`) when `True`. | Rarely needed; keep `False` to preserve structure. |
| `links` | lxml Cleaner option: sanitize/clean links. | Leave `True` unless you need raw anchors untouched. |
| `scripts` | lxml Cleaner option: remove `<script>` tags when `True`. | Keep `False` to preserve scripts; usually safe to remove via `javascript=True` anyway. |
| `javascript` | lxml Cleaner option: remove JS and event handlers. | Set `False` only if you truly need inline JS (not recommended). |
| `comments` | lxml Cleaner option: remove HTML comments. | Set `False` to retain comments for debugging. |
| `style` | lxml Cleaner option: remove CSS and style attributes. | Set `False` to keep inline styles/CSS. |
| `processing_instructions` | lxml Cleaner option: remove processing instructions. | Rarely change; keep for safety. |
| `embedded` | lxml Cleaner option: remove embedded content (e.g., `<embed>`, `<object>`). | Set `False` to keep embedded media. |
| `frames` | lxml Cleaner option: remove frames/iframes. | Set `False` if iframes contain needed content. |
| `forms` | lxml Cleaner option: remove form elements. | Set `False` if you need to keep forms/inputs. |
| `annoying_tags` | lxml Cleaner option: remove tags considered "annoying" by lxml (e.g., `<blink>`, `<marquee>`). | Rarely change. |
| `kill_tags` | Additional explicit tags to remove entirely. | Add site-specific or custom tags to drop. |
| `remove_unknown_tags` | lxml Cleaner option: drop unknown/invalid tags. | Set `False` if you rely on custom elements. |
| `safe_attrs_only` | Only allow attributes listed in `safe_attrs`. | Set `False` if you need to keep arbitrary attributes. |
| `safe_attrs` | Allowed HTML attributes when `safe_attrs_only=True`. | Extend to keep additional attributes you trust. |

### Types and Defaults

| Parameter | Type | Default |
|---|---|---|
| `non_text_to_keep` | `set[str]` | media/meta/table/`br` tags |
| `attr_stop_words` | `set[str]` | common UI/navigation tokens |
| `remove_header_lists` | `bool` | `True` |
| `remove_footer_lists` | `bool` | `True` |
| `minify` | `bool` | `True` |
| `minify_kwargs` | `dict` | `{}` |
| `meta` | `bool` | `False` |
| `page_structure` | `bool` | `False` |
| `links` | `bool` | `True` |
| `scripts` | `bool` | `False` |
| `javascript` | `bool` | `True` |
| `comments` | `bool` | `True` |
| `style` | `bool` | `True` |
| `processing_instructions` | `bool` | `True` |
| `embedded` | `bool` | `True` |
| `frames` | `bool` | `True` |
| `forms` | `bool` | `True` |
| `annoying_tags` | `bool` | `True` |
| `kill_tags` | `set[str] &#124; None` | `None` |
| `remove_unknown_tags` | `bool` | `True` |
| `safe_attrs_only` | `bool` | `True` |
| `safe_attrs` | `set[str]` | curated set |
