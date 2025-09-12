![smol](https://github.com/NosibleAI/smol-html/blob/main/smol.png?raw=true)


# smol-html

Small, dependable HTML cleaner/minifier with sensible defaults.

## Motivation

Nosible is a search engine, which means we need to store and process a very large number of webpages. To make this tractable, we strip out visual chrome and other non-essential components that don’t matter for downstream tasks (indexing, ranking, retrieval, and LLM pipelines) while preserving the important content and structure. This package cleans and minifies HTML, greatly reducing size on disk; combined with Brotli compression (by Google), the savings are even larger.

![Cleaning impact on size](https://github.com/NosibleAI/smol-html/blob/main/eval.png?raw=true)

### 📦 Installation

```bash
pip install smol-html
```

### ⚡ Installing with uv 

```bash
uv pip install smol-html
```

### Requirements

- Python: 3.9
- Dependencies:
  - beautifulsoup4>=4.0.1
  - brotli>=0.5.2
  - lxml[html-clean]>=1.3.2
  - minify-html>=0.2.6

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
cleaned = cleaner.make_smol(raw_html=html)

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
out = cleaner.make_smol(raw_html="<p>Hi <!-- note --> <a href='x'>link</a></p>")
```

Customize a few options:

```python
from smol_html import SmolHtmlCleaner

cleaner = SmolHtmlCleaner(
    attr_stop_words={"nav", "advert"},
    remove_header_lists=False,
    minify=True,
)

out = cleaner.make_smol(raw_html="<p>Hi</p>")
```

## Compressed Bytes Output

Produce compressed bytes using Brotli with `make_smol_bytes`.

- By default, the compressed bytes are URL-safe Base64 encoded (`base64_encode=True`).
- If you enable Base64, you must decode before Brotli-decompressing.
- You can disable Base64 by passing `base64_encode=False` and decompress directly.

Default (Base64-encoded) output:

```python
from smol_html import SmolHtmlCleaner
import base64
import brotli  # only needed if you want to decompress here in the example

html = """
<html>
  <body>
    <div>  Hello <span> world </span> </div>
  </body>
</html>
"""

cleaner = SmolHtmlCleaner()

# Get compressed bytes (quality 11 is strong compression)
compressed = cleaner.make_smol_bytes(raw_html=html, compression_level=11)

# Because Base64 is enabled by default, decode before decompressing
decoded = base64.urlsafe_b64decode(compressed)
decompressed = brotli.decompress(decoded).decode("utf-8")
print(decompressed)

# Or write Base64-encoded compressed output directly to a file
with open("page.html.br.b64", "wb") as f:
    f.write(compressed)
```

Disable Base64 and decompress directly:

```python
from smol_html import SmolHtmlCleaner
import brotli

cleaner = SmolHtmlCleaner()
compressed_raw = cleaner.make_smol_bytes(
    raw_html="<p>Hi</p>",
    compression_level=11,
    base64_encode=False,
)
print(brotli.decompress(compressed_raw).decode("utf-8"))
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

### `make_smol_bytes` Options

| Parameter | Type | Default |
|---|---|---|
| `compression_level` | `int` | `4` |
| `base64_encode` | `bool` | `True` |
