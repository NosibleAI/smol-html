from __future__ import annotations

import base64

import minify_html
from bs4 import BeautifulSoup, Tag
from lxml import html as lxml_html
from lxml.html.clean import Cleaner


# -------------------------
# Public API
# -------------------------
class SmolHtmlCleaner:
    """
    Small, dependable HTML cleaner/minifier with sensible defaults.

    Parameters
    ----------
    non_text_to_keep : set of str, optional
        Tags preserved even if textless. Default includes meta/media/table/line-break tags.
    attr_stop_words : set of str, optional
        Attribute tokens indicating non-content scaffolding/UX. Default contains common UI tokens.
    remove_header_lists : bool, optional
        Prune links/lists inside ``<header>``. Default True.
    remove_footer_lists : bool, optional
        Prune links/lists inside ``<footer>``. Default True.
    minify : bool, optional
        Minify HTML output via ``minify_html``. Default True.
    minify_kwargs : dict, optional
        Extra args for ``minify_html.minify``. Default empty.

    lxml Cleaner parameters
    ----------------------
    meta : bool, optional
        Remove meta tags. Default False.
    page_structure : bool, optional
        Remove page structure tags (html, head, body). Default False.
    links : bool, optional
        Remove link tags. Default True.
    scripts : bool, optional
        Remove script tags. Default False.
    javascript : bool, optional
        Remove JavaScript content. Default True.
    comments : bool, optional
        Remove comments. Default True.
    style : bool, optional
        Remove style tags. Default True.
    processing_instructions : bool, optional
        Remove processing instructions. Default True.
    embedded : bool, optional
        Remove embedded content (object, embed, applet). Default True.
    frames : bool, optional
        Remove frame/iframe tags. Default True.
    forms : bool, optional
        Remove form tags. Default True.
    annoying_tags : bool, optional
        Remove tags considered annoying (blink, marquee, etc). Default True.
    kill_tags : set of str, optional
        Additional tags to remove. Default None.
    remove_unknown_tags : bool, optional
        Remove unknown tags. Default True.
    safe_attrs_only : bool, optional
        Only keep safe attributes. Default True.
    safe_attrs : set of str, optional
        Set of safe attributes to keep. Default is a sensible set.

    Notes
    -----
    Defaults and cleaning behavior are preserved; only the configuration surface
    moved from a dataclass to keyword-only parameters on the constructor.
    """

    def __init__(
        self,
        *,
        # Core behavior
        non_text_to_keep: set[str] = None,
        attr_stop_words: set[str] = None,
        remove_header_lists: bool = True,
        remove_footer_lists: bool = True,
        # Minify
        minify: bool = True,
        minify_kwargs: dict | None = None,
        # lxml Cleaner exposed explicitly (prefixed)
        meta: bool = False,
        page_structure: bool = False,
        links: bool = True,
        scripts: bool = False,
        javascript: bool = True,
        comments: bool = True,
        style: bool = True,
        processing_instructions: bool = True,
        embedded: bool = True,
        frames: bool = True,
        forms: bool = True,
        annoying_tags: bool = True,
        kill_tags: set[str] | None = None,
        remove_unknown_tags: bool = True,
        safe_attrs_only: bool = True,
        safe_attrs: set[str] = None,
    ):
        # Inline defaults identical to the prior CleanerConfig
        if safe_attrs is None:
            safe_attrs = {"href", "hreflang", "src", "srclang", "target", "alt", "kind", "type", "role", "abbr",
            "accept", "accept-charset", "datetime", "lang", "name", "rel", "title", "value", "content", "label",
            "item_type", "property", "itemprop"}

        if attr_stop_words is None:
            attr_stop_words = {"alert", "button", "checkbox", "dialog", "navigation", "tab", "tabpanel", "textbox",
            "menu", "banner", "form", "search", "progressbar", "radio", "slider", "comment", "nav", "sidebar",
            "breadcrumb", "dropdown", "menu-item", "toggle", "hamburger", "aside", "tooltip", "modal", "overlay",
            "popup", "advert", "hero", "utility", "login", "signup", "password", "email", "username"}

        if non_text_to_keep is None:
            non_text_to_keep = {"meta", "img", "picture", "figure", "figcaption", "video", "source", "audio", "table",
            "tr", "th", "td", "thead", "tbody", "tfoot", "caption", "br"}

        self.non_text_to_keep = non_text_to_keep
        self.attr_stop_words = attr_stop_words
        self.remove_header_lists = remove_header_lists
        self.remove_footer_lists = remove_footer_lists
        self.minify = minify
        self.minify_kwargs = dict(minify_kwargs or {})

        # Initialize lxml Cleaner with explicit kwargs gathered from parameters
        self._cleaner = Cleaner(
            meta=meta,
            page_structure=page_structure,
            links=links,
            scripts=scripts,
            javascript=javascript,
            comments=comments,
            style=style,
            processing_instructions=processing_instructions,
            embedded=embedded,
            frames=frames,
            forms=forms,
            annoying_tags=annoying_tags,
            kill_tags=kill_tags,
            remove_unknown_tags=remove_unknown_tags,
            safe_attrs_only=safe_attrs_only,
            safe_attrs=safe_attrs,
        )

    # -------------------------
    # User-friendly entry points
    # -------------------------

    def make_smol(self, *, raw_html: str | BeautifulSoup) -> str:
        """Clean and optionally minify HTML input.

        The cleaning pipeline applies pre-parse hooks (on strings), prunes elements
        by attribute stop words, sanitizes via lxml Cleaner, performs structural
        pruning of header/footer/body, then applies post-clean hooks.

        Parameters
        ----------
        raw_html : str or BeautifulSoup
            Raw HTML string or BeautifulSoup to be cleaned.

        Returns
        -------
        str
            Cleaned HTML as a string.
        """

        # Stage 0: hooks that operate on the raw string
        if isinstance(raw_html, str):
            soup = BeautifulSoup(raw_html or "", features="lxml")
        elif isinstance(raw_html, BeautifulSoup):
            soup = raw_html
        else:
            raise TypeError("raw_html must be a str or BeautifulSoup instance")

        # Stage 1: attribute-based pruning on the original soup
        # Remove small, likely non-content elements based on attribute tokens.
        self._strip_by_attribute_stop_words(soup=soup)

        # Stage 2: lxml cleaner pass (robust HTML sanitation)
        # Use lxml Cleaner to sanitize HTML, optionally minify afterwards.
        cleaned_html = self._lxml_clean(str(soup))
        clean_soup = BeautifulSoup(markup=cleaned_html, features="lxml")

        # Stage 3: structural pruning on header/body/footer of the cleaned soup
        self._prune_header_footer(clean_soup)
        self._prune_body(clean_soup)
        self._drop_empty_leaf_nodes(clean_soup)

        return str(clean_soup)

    def make_smol_bytes(self, *,
        raw_html: str | BeautifulSoup,
        compression_level: int = 4,
        base64_encode: bool = True,
    ) -> bytes:
        """Return cleaned HTML as bytes, optionally Brotli-compressed.

        If ``compression_level`` is 0, returns UTF-8 encoded bytes without compression.
        For ``compression_level`` > 0, compresses the bytes using Brotli.

        Parameters
        ----------
        raw_html : str or BeautifulSoup
            Raw HTML to clean.
        compression_level : int, optional
            Brotli quality/level. 0 disables compression. Default 4.
        base64_encode : bool, optional
            Apply URL-safe base64 encoding to the compressed output. Default True.

        Returns
        -------
        bytes
            Cleaned (and possibly compressed) HTML as bytes.
        """
        html = self.make_smol(raw_html=raw_html)
        data = html.encode("utf-8")

        if compression_level <= 0:
            return data

        try:
            import brotli as _brotli  # type: ignore
        except Exception as exc:  # pragma: no cover - import-time dependency
            raise RuntimeError(
                "Brotli is required for compression. Install 'brotli' or 'brotlicffi', "
                "or call with compression_level=0."
            ) from exc

        # Prefer TEXT mode if available for HTML content; fall back gracefully.
        mode = getattr(_brotli, "MODE_TEXT", None)
        if mode is None:
            mode = getattr(_brotli, "BROTLI_MODE_TEXT", None)

        if mode is not None:
            compressed = _brotli.compress(data, quality=int(compression_level), mode=mode)
        else:
            compressed = _brotli.compress(data, quality=int(compression_level))

        if base64_encode:
            return base64.urlsafe_b64encode(compressed)
        return compressed

    # -------------------------
    # Internal helpers
    # -------------------------
    def _lxml_clean(self, html_str: str) -> str:
        """Sanitize and optionally minify HTML using lxml + minify_html.

        Parameters
        ----------
        html_str : str
            HTML markup to be cleaned.

        Returns
        -------
        str
            Cleaned (and possibly minified) HTML markup.
        """
        try:
            cleaned = self._cleaner.clean_html(html_str)
            return minify_html.minify(cleaned, **self.minify_kwargs) if self.minify else cleaned
        except ValueError as ex:
            # Handle encoding declaration edge-cases by round-tripping via lxml
            msg = (
                "Unicode strings with encoding declaration are not supported. "
                "Please use bytes input or XML fragments without declaration."
            )
            if str(ex) == msg:
                raw_bytes = html_str.encode("utf-8", errors="ignore")
                doc = lxml_html.fromstring(raw_bytes)
                cleaned = self._cleaner.clean_html(doc)
                rendered = lxml_html.tostring(cleaned, encoding="utf-8").decode("utf-8")
                return minify_html.minify(rendered, **self.minify_kwargs) if self.minify else rendered
            raise

    def _strip_by_attribute_stop_words(self, *, soup: BeautifulSoup) -> None:
        """Remove small, likely non-content elements by attribute tokens.

        Scans leaf-like descendants under ``<body>`` and collects elements whose
        ``id``, ``class``, ``role``, or ``item_type`` values contain any of the
        configured ``attr_stop_words`` tokens (case-insensitive), then decomposes
        them. Mirrors the baseline leaf-ness and concatenation behavior.

        Parameters
        ----------
        soup : BeautifulSoup
            Parsed document to prune in place.
        """
        body = soup.find("body") or soup
        to_decompose: list[Tag] = []
        for el in body.descendants:
            if not isinstance(el, Tag):
                continue
            attrs = el.attrs if isinstance(el.attrs, dict) else {}
            if not attrs:
                continue
            # Only prune simple leaf-ish nodes to avoid huge deletes unintentionally
            if sum(1 for _ in el.descendants) > 1:
                continue
            for name in ("id", "class", "role", "item_type"):
                val = attrs.get(name)
                if val is None:
                    continue
                if isinstance(val, (list, tuple)):
                    # Match baseline behavior: concatenate tokens without separator
                    val_str = "".join(map(str, val))
                else:
                    val_str = str(val)
                if any(sw in val_str.lower() for sw in self.attr_stop_words):
                    to_decompose.append(el)
                    break
        for el in to_decompose:
            el.decompose()

    def _prune_header_footer(self, soup: BeautifulSoup) -> None:
        """Prune likely navigational clutter inside header and footer.

        Removes common list-like elements and links inside ``<header>``/``<footer>``
        when the corresponding toggles are enabled.
        """
        header = soup.find("header")
        footer = soup.find("footer")
        if header and self.remove_header_lists:
            self._decompose_tags(header, {"a", "img", "ol", "ul", "li"})
        if footer and self.remove_footer_lists:
            self._decompose_tags(footer, {"a", "img", "ol", "ul", "li"})

    def _prune_body(self, soup: BeautifulSoup) -> None:
        body = soup.find("body") or soup
        always_remove = {
            "input", "textarea", "button", "select", "option", "optgroup", "datalist",
            "label", "fieldset", "legend", "output", "meter", "dialog", "form",
            "search", "progress", "svg", "canvas", "use", "nav", "object", "noscript",
        }
        to_decompose: list[Tag] = []
        for el in body.descendants:
            if not isinstance(el, Tag):
                continue
            if not isinstance(el.name, str):
                continue
            if el.name in self.non_text_to_keep:
                continue
            if el.name in always_remove:
                to_decompose.append(el)
        for el in to_decompose:
            el.decompose()

    def _drop_empty_leaf_nodes(self, soup: BeautifulSoup) -> None:
        """Iteratively remove empty leaves using the baseline's strict leaf check.

        Walks leaf nodes (no descendants) and removes those with no text content,
        excluding tags explicitly whitelisted in ``non_text_to_keep``.
        """
        body = soup.find("body") or soup
        while True:
            to_decompose: list[Tag] = []
            for el in body.descendants:
                if not isinstance(el, Tag):
                    continue
                if not isinstance(el.name, str):
                    continue
                if el.name in self.non_text_to_keep:
                    continue
                # Baseline leaf check: element must have zero descendants at all
                if len(list(el.descendants)) != 0:
                    continue
                # Remove if no text once stripped
                if (el.get_text() or "").strip():
                    continue
                to_decompose.append(el)
            if not to_decompose:
                break
            for el in to_decompose:
                el.decompose()

    @staticmethod
    def _decompose_tags(root: Tag, names: set[str]) -> None:
        for el in list(root.descendants):
            if isinstance(el, Tag) and isinstance(el.name, str) and el.name in names:
                el.decompose()
