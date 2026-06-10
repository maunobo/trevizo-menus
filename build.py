#!/usr/bin/env python3
"""Build Trevizo bilingual menu preview from content/en.md + content/gr.md.

Usage: python3 build.py
Output: index.html (self-contained, ready for GitHub Pages)
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
from html import escape
from dataclasses import dataclass, field
from typing import Optional

ROOT = Path(__file__).resolve().parent
CONTENT_EN = ROOT / "content" / "en.md"
CONTENT_GR = ROOT / "content" / "gr.md"
# Optional: if these exist, build also embeds them under a "Show proposed revisions" toggle.
CONTENT_EN_PROPOSED = ROOT / "content" / "en-proposed.md"
CONTENT_GR_PROPOSED = ROOT / "content" / "gr-proposed.md"
OUTPUT = ROOT / "index.html"

# ─── Per-menu visual config ──────────────────────────────────────────────
# Menus are matched by position in the MD files (menu[0] EN ↔ menu[0] GR).
MENU_CONFIG = [
    {
        "slug": "wines",
        "page_class": "a5 wines",
        "format": "A5",
        "color_label": "deep maroon",
        "meta_en": "A5 · deep maroon · Red section offsets right to make mascot space",
        "meta_gr": "A5 · σκούρο μπορντό · Ερυθρά με offset δεξιά για χώρο mascot",
        "logo": "cream",
        "front_mascot": "corner-mascot",
        "back_mascot": None,
        "desc_class": "item-region",
        "title_class": "",
        "has_col_header": True,
        "col_header_en": ("Glass", "Bottle"),
        "col_header_gr": ("Ποτήρι", "Φιάλη"),
    },
    {
        "slug": "cocktails",
        "page_class": "a5 cocktails",
        "format": "A5",
        "color_label": "spritz orange",
        "meta_en": "A5 · spritz orange · Aperol-inspired · brand top-center",
        "meta_gr": "A5 · πορτοκαλί spritz · έμπνευση από Aperol · brand πάνω-κέντρο",
        "logo": "cream",
        "front_mascot": "front-mascot",
        "back_mascot": None,
        "desc_class": "item-desc",
        "title_class": "",
        "has_col_header": False,
    },
    {
        "slug": "food",
        "page_class": "a5 food",
        "format": "A5",
        "color_label": "cream paper",
        "meta_en": "A5 · cream paper · vermilion mascot",
        "meta_gr": "A5 · κρεμ χαρτί · βερμιγιόν mascot",
        "logo": "vermilion",
        "front_mascot": "front-mascot",
        "back_mascot": None,
        "desc_class": "item-desc",
        "title_class": "",
        "has_col_header": False,
    },
    {
        "slug": "brunch",
        "page_class": "a5 brunch",
        "format": "A5",
        "color_label": "cream + dusk blue edge band",
        "meta_en": "A5 · cream paper · dusk blue edge band w/ SAT·SUN·10:00—16:00",
        "meta_gr": "A5 · κρεμ χαρτί · μπλε edge band με ΣΑΒ·ΚΥΡ·10:00—16:00",
        "logo": "vermilion",
        "front_mascot": "front-mascot",
        "back_mascot": None,
        "desc_class": "item-desc",
        "title_class": "",
        "has_col_header": False,
        "edge_band_text_en": "SAT · SUN · 10:00 — 16:00",
        "edge_band_text_gr": "ΣΑΒ · ΚΥΡ · 10:00 — 16:00",
    },
    {
        "slug": "spirits",
        "page_class": "a4 spirits",
        "format": "A4",
        "color_label": "petrol teal",
        "meta_en": "A4 · petrol teal · roman titles · mascots both sides",
        "meta_gr": "A4 · πετρόλ τιλ · κανονικοί τίτλοι · mascots και στις δύο πλευρές",
        "logo": "cream",
        "front_mascot": "front-mascot",
        "back_mascot": "corner-mascot",
        "desc_class": "item-desc",
        "title_class": "title-roman",
        "has_col_header": False,
    },
]


# ─── Data model ──────────────────────────────────────────────────────────
@dataclass
class Item:
    name: str
    quantity: Optional[str] = None
    price: str = ""
    description: Optional[str] = None
    is_sub: bool = False


@dataclass
class Section:
    name: str
    flags: set = field(default_factory=set)
    items: list = field(default_factory=list)


@dataclass
class Side:
    name: str
    flags: set = field(default_factory=set)
    sections: list = field(default_factory=list)
    footer: Optional[str] = None


@dataclass
class Menu:
    name: str
    sides: list = field(default_factory=list)


# ─── Parser ──────────────────────────────────────────────────────────────
def parse_flags(s: Optional[str]) -> set:
    if not s:
        return set()
    return {f.strip() for f in s.split(",")}


def parse(md_text: str) -> list[Menu]:
    menus: list[Menu] = []
    current_menu: Optional[Menu] = None
    current_side: Optional[Side] = None
    current_section: Optional[Section] = None

    for raw in md_text.split("\n"):
        line = raw.strip()
        if not line:
            continue
        if line.startswith("//"):  # inline comment
            continue
        if line.startswith("# Menu:"):
            current_menu = Menu(name=line[len("# Menu:") :].strip())
            menus.append(current_menu)
            current_side = None
            current_section = None
            continue
        m = re.match(r"^## Side:\s*(\w+)(?:\s*\{([^}]+)\})?$", line)
        if m and current_menu:
            current_side = Side(name=m.group(1), flags=parse_flags(m.group(2)))
            current_menu.sides.append(current_side)
            current_section = None
            continue
        m = re.match(r"^###\s+(.+?)(?:\s*\{([^}]+)\})?$", line)
        if m and current_side is not None:
            current_section = Section(
                name=m.group(1).strip(), flags=parse_flags(m.group(2))
            )
            current_side.sections.append(current_section)
            continue
        if line.startswith(">") and current_side is not None:
            current_side.footer = line[1:].strip()
            continue
        if "|" in line and current_section is not None:
            is_sub = line.startswith("~ ")
            content = line[2:].strip() if is_sub else line
            parts = [p.strip() for p in content.split("|")]
            name_raw = parts[0]
            price = parts[1] if len(parts) > 1 else ""
            desc = parts[2] if len(parts) > 2 and parts[2] else None
            qty = None
            qm = re.search(r"\{([^}]+)\}", name_raw)
            if qm:
                qty = qm.group(1)
                name = re.sub(r"\s*\{[^}]+\}", "", name_raw).strip()
            else:
                name = name_raw
            current_section.items.append(
                Item(
                    name=name,
                    quantity=qty,
                    price=price,
                    description=desc,
                    is_sub=is_sub,
                )
            )

    return menus


def validate(en: list[Menu], gr: list[Menu]) -> None:
    assert len(en) == len(gr), f"Menu count: en={len(en)} gr={len(gr)}"
    for em, gm in zip(en, gr):
        assert len(em.sides) == len(gm.sides), f"Side count differs in '{em.name}'"
        for es, gs in zip(em.sides, gm.sides):
            assert len(es.sections) == len(gs.sections), (
                f"Section count differs in {em.name} / {es.name}"
            )
            for esec, gsec in zip(es.sections, gs.sections):
                assert len(esec.items) == len(gsec.items), (
                    f"Item count differs in {em.name} / {es.name} / {esec.name}"
                )


# ─── Bilingual rendering helpers ─────────────────────────────────────────
def i18n(en: str, gr: str) -> str:
    """Render text as one span per language, or shared if identical."""
    en_s = escape(en)
    gr_s = escape(gr)
    if en_s == gr_s:
        return en_s
    return f'<span class="lang-en">{en_s}</span><span class="lang-gr">{gr_s}</span>'


def render_item(en_item: Item, gr_item: Item, desc_class: str) -> str:
    qty_html = ""
    if en_item.quantity or gr_item.quantity:
        en_q = en_item.quantity or ""
        gr_q = gr_item.quantity or ""
        qty_html = f'<span class="qty">{i18n(en_q, gr_q)}</span>'
    name_html = i18n(en_item.name, gr_item.name) + qty_html
    price_html = escape(en_item.price)
    row = (
        f'<div class="item-row">'
        f'<div class="item-name">{name_html}</div>'
        f'<div class="item-price">{price_html}</div>'
        f"</div>"
    )
    desc_html = ""
    if en_item.description or gr_item.description:
        d_en = en_item.description or ""
        d_gr = gr_item.description or ""
        desc_html = f'<div class="{desc_class}">{i18n(d_en, d_gr)}</div>'
    cls = "item iced-tea-flavor" if en_item.is_sub else "item"
    return f'<div class="{cls}">{row}{desc_html}</div>'


def render_section(
    en_sec: Section, gr_sec: Section, cfg: dict, *, force_columns: bool = False
) -> str:
    inline_style = ""
    if "pad-right" in en_sec.flags:
        inline_style = ' style="padding-right: 110px;"'
    classes = "section"
    if "col-2" in en_sec.flags:
        classes += " col-2"
    header = (
        f'<div class="section-header">{i18n(en_sec.name, gr_sec.name)}</div>'
    )
    # Detect sub-items (e.g., Iced Tea flavors) — wrap them in a styled block.
    items_html: list[str] = []
    pending_subs: list[str] = []
    for ei, gi in zip(en_sec.items, gr_sec.items):
        rendered = render_item(ei, gi, cfg["desc_class"])
        if ei.is_sub:
            pending_subs.append(rendered)
        else:
            if pending_subs:
                items_html.append(
                    f'<div class="iced-tea-flavors">{"".join(pending_subs)}</div>'
                )
                pending_subs = []
            items_html.append(rendered)
    if pending_subs:
        items_html.append(
            f'<div class="iced-tea-flavors">{"".join(pending_subs)}</div>'
        )
    return (
        f'<div class="{classes}"{inline_style}>{header}{"".join(items_html)}</div>'
    )


def render_brand_block(cfg: dict, menu_en: Menu, menu_gr: Menu) -> str:
    """Wordmark + title block, on front sides only."""
    title_class = f"title {cfg['title_class']}".strip()
    # Stacked title for "Aperitivo & Food" and "Beverages & Beer / Spirits"
    title_en = menu_en.name
    title_gr = menu_gr.name
    if cfg["slug"] == "spirits":
        # Front title = the part of the menu name before "/" (e.g. "Beverages & Beers");
        # back title ("Spirits"/"Αποστάγματα") is handled separately. Single line — no <br> break.
        en_html = escape(title_en.split("/")[0].strip())
        gr_html = escape(title_gr.split("/")[0].strip())
    else:
        en_html = escape(title_en)
        gr_html = escape(title_gr)
    if en_html == gr_html:
        title_html = en_html
    else:
        title_html = (
            f'<span class="lang-en">{en_html}</span>'
            f'<span class="lang-gr">{gr_html}</span>'
        )
    return (
        f'<div class="wordmark">T R E V I Z O</div>'
        f'<h1 class="{title_class}">{title_html}</h1>'
    )


def render_col_header(cfg: dict) -> str:
    if not cfg.get("has_col_header"):
        return ""
    en_l, en_r = cfg["col_header_en"]
    gr_l, gr_r = cfg["col_header_gr"]
    left = i18n(en_l, gr_l)
    right = i18n(en_r, gr_r)
    return f'<div class="col-header">{left}<span>/</span><span>{right}</span></div>'


def render_edge_band(cfg: dict) -> str:
    en_text = cfg.get("edge_band_text_en")
    gr_text = cfg.get("edge_band_text_gr")
    if not en_text:
        return ""
    band_text = i18n(en_text, gr_text)
    return (
        f'<div class="brunch-edge-band">'
        f'<div class="vertical-text">{band_text}</div>'
        f"</div>"
    )


def render_logo(mascot_class: str, logo_color: str) -> str:
    # -resize PNGs are cropped tight to the mascot; the originals had ~30% transparent padding
    # that made the drawing appear small inside the CSS box even when the box was sized correctly.
    src = f"assets/trevizo-logo-{logo_color}-resize.png"
    return (
        f'<div class="logo-mascot {mascot_class}">'
        f'<img src="{src}" alt="Trevizo mascot">'
        f"</div>"
    )


# ─── Sticker variant overlays ───────────────────────────────────────────
# Optional risograph sticker accents per menu/side. Hidden by default;
# revealed when body.variant-stickers is set via the dev toggle.
# Sizes/positions tuned to peek into negative space without competing with text.
STICKER_OVERLAYS = {
    # menu_slug: [ { side, file, style, replaces_mascot? } ]
    # Placements peek into negative space WITHOUT overlapping section content or titles.
    # Subject choices reflect each menu's content (Italian food → pizza/salami/bread; Spirits → bottle trio).
    "wines": [
        # TODO: swap to grapes once a grapes sticker is provided. Orange slice is a placeholder.
        {"side": "front", "file": "sticker-orange-slice.png",
         "style": "top: 22px; left: 14px; width: 64px; transform: rotate(-12deg);"},
        # Wines back: flex-centered Rosé + Champagne fill the page — skip.
    ],
    "cocktails": [
        # TODO: swap to a martini-glass-with-olive sticker once provided. Olive pick is the closest stand-in.
        {"side": "front", "file": "sticker-olive-pick.png",
         "style": "top: 28px; right: 14px; width: 32px; transform: rotate(15deg);"},
        # Cocktails back: section gap is too narrow for a sticker. Skip.
    ],
    "food": [
        {"side": "front", "file": "sticker-pizza-slice.png",
         "style": "top: 22px; right: 14px; width: 70px; transform: rotate(10deg);"},
        # Food back: Platter section gets the salami board as a contextual match.
        {"side": "back", "file": "sticker-salami-board.png",
         "style": "bottom: 18px; left: 14px; width: 80px; transform: rotate(-6deg);"},
    ],
    "brunch": [
        # Italian Breads section gets the bread basket — direct content match.
        {"side": "front", "file": "sticker-bread-basket.png",
         "style": "bottom: 100px; right: 14px; width: 68px; transform: rotate(8deg);"},
        {"side": "back", "file": "sticker-olive-branch.png",
         "style": "top: 18px; right: 14px; width: 70px; transform: rotate(15deg);"},
    ],
    "spirits": [
        # Beverages front: TODO — needs cappuccino sticker (none in current asset library).
        # Spirits back: 3 bottles (Gin/Vermouth/Bitter) REPLACES the corner mascot at the bistro's request.
        {"side": "back", "file": "sticker-three-bottles.png",
         "style": "bottom: 40px; right: 16px; width: 130px; transform: rotate(-4deg);",
         "replaces_mascot": True},
    ],
}


def render_stickers(slug: str, is_front: bool) -> str:
    side = "front" if is_front else "back"
    items = [s for s in STICKER_OVERLAYS.get(slug, []) if s["side"] == side]
    return "".join(
        f'<img class="sticker-overlay" src="assets/stickers/{s["file"]}" alt="" '
        f'style="{s["style"]}">'
        for s in items
    )


def render_footer(en_side: Side, gr_side: Side) -> str:
    if not en_side.footer:
        return ""
    return f'<div class="footer">{i18n(en_side.footer, gr_side.footer or en_side.footer)}</div>'


def render_side(
    en_side: Side, gr_side: Side, cfg: dict, menu_en: Menu, menu_gr: Menu,
    is_front: bool,
) -> str:
    label = "Front" if is_front else "Back"
    side_classes = "page front" if is_front else "page back"

    parts: list[str] = []

    # Guides overlay (always rendered, toggled by .show-guides on body)
    guide_label = "Front" if is_front else "Back"
    parts.append(
        f'<div class="guides">'
        f'<div class="trim-line"></div>'
        f'<div class="guide-label trim">{guide_label}</div>'
        f"</div>"
    )

    # Edge band (Brunch only)
    if "edge-band" in en_side.flags:
        parts.append(render_edge_band(cfg))

    # Mascot
    if is_front and cfg.get("front_mascot"):
        parts.append(render_logo(cfg["front_mascot"], cfg["logo"]))
    if not is_front and cfg.get("back_mascot"):
        parts.append(render_logo(cfg["back_mascot"], cfg["logo"]))

    # Sticker variant overlays (hidden unless body.variant-stickers is set)
    parts.append(render_stickers(cfg["slug"], is_front))

    # Inner page
    inner_parts: list[str] = []
    if is_front:
        inner_parts.append(render_brand_block(cfg, menu_en, menu_gr))
    elif cfg["slug"] == "spirits":
        # Spirits back: roman (non-italic) per A4 design system.
        # Greek = "Αποστάγματα" (more refined than "Ποτά"; operator preference 2026-05-26).
        inner_parts.append(
            '<h1 class="title title-roman">'
            '<span class="lang-en">Spirits</span>'
            '<span class="lang-gr">Αποστάγματα</span>'
            "</h1>"
        )

    # Decide section layout
    has_columns = any(
        "column-left" in s.flags or "column-right" in s.flags
        for s in en_side.sections
    )

    if has_columns:
        # Spirits back 2-col grid
        left = [
            render_section(es, gs, cfg)
            for es, gs in zip(en_side.sections, gr_side.sections)
            if "column-left" in es.flags
        ]
        right = [
            render_section(es, gs, cfg)
            for es, gs in zip(en_side.sections, gr_side.sections)
            if "column-right" in es.flags
        ]
        grid = (
            '<div class="spirits-grid">'
            f'<div class="left-col">{"".join(left)}</div>'
            f'<div class="right-col">{"".join(right)}</div>'
            "</div>"
        )
        inner_parts.append(grid)
    elif cfg.get("has_col_header") and is_front:
        # Wines front: title → rule → col-header → sections.
        # Rule sits directly under the title to separate the brand block from the price legend below.
        sections_html = "".join(
            render_section(es, gs, cfg)
            for es, gs in zip(en_side.sections, gr_side.sections)
        )
        inner_parts.append(
            f'<div style="margin-top: 10px;">'
            f'<div class="rule"></div>'
            f'{render_col_header(cfg)}'
            f'{sections_html}'
            f"</div>"
        )
    elif cfg.get("has_col_header") and not is_front:
        # Wines back: rule → col-header → sections, matching the front's hierarchy
        # so both pages of the menu share the same visual structure.
        inner_parts.append('<div class="rule"></div>')
        inner_parts.append(render_col_header(cfg))
        for es, gs in zip(en_side.sections, gr_side.sections):
            inner_parts.append(render_section(es, gs, cfg))
    else:
        # Generic: wrap in sections-wrap on fronts (for vertical-centering CSS)
        sections_html = "".join(
            render_section(es, gs, cfg)
            for es, gs in zip(en_side.sections, gr_side.sections)
        )
        if is_front:
            inner_parts.append(f'<div class="sections-wrap">{sections_html}</div>')
        else:
            inner_parts.append(sections_html)

    # Kitchen hours — Food front only, sits just above the footer.
    if cfg["slug"] == "food" and is_front:
        inner_parts.append(
            '<div class="kitchen-hours">'
            '<span class="lang-en">Kitchen open until 23:00</span>'
            '<span class="lang-gr">Η κουζίνα λειτουργεί έως 23:00</span>'
            "</div>"
        )

    # Footer
    inner_parts.append(render_footer(en_side, gr_side))

    parts.append(f'<div class="{side_classes}">{"".join(inner_parts)}</div>')

    label_en = "Front · Side A" if is_front else "Back · Side B"
    label_gr = "Μπροστά · Πλευρά Α" if is_front else "Πίσω · Πλευρά Β"
    page_label = i18n(label_en, label_gr)

    return (
        f'<div class="page-wrap">'
        f'<div class="card-scaler">'
        f'<div class="page-outer {cfg["page_class"]}">{"".join(parts)}</div>'
        f"</div>"
        f'<div class="page-label">{page_label}</div>'
        f"</div>"
    )


def render_menu(idx: int, en_menu: Menu, gr_menu: Menu) -> str:
    cfg = MENU_CONFIG[idx]
    num = f"{idx + 1:02d}"
    title = i18n(en_menu.name, gr_menu.name)
    meta = i18n(cfg["meta_en"], cfg["meta_gr"])

    sides_html: list[str] = []
    for i, (es, gs) in enumerate(zip(en_menu.sides, gr_menu.sides)):
        sides_html.append(render_side(es, gs, cfg, en_menu, gr_menu, is_front=(i == 0)))

    return (
        f'<div class="row">'
        f'<div class="row-header">'
        f'<div class="row-num">{num}</div>'
        f'<div class="row-title">{title}</div>'
        f'<div class="row-meta">{meta}</div>'
        f"</div>"
        f'<div class="spread">{"".join(sides_html)}</div>'
        f"</div>"
    )


# ─── Stylesheet (extracted from V6, plus EN/GR toggle additions) ────────
STYLES = """
  * { margin: 0; padding: 0; box-sizing: border-box; }
  /* Theme: dark by default; body[data-theme="light"] flips the preview chrome (menus themselves keep their flood colors). */
  html, body { background: #0d0d0d; min-height: 100vh; font-family: 'Archivo', sans-serif; color: #ddd; transition: background-color 0.2s, color 0.2s; }
  body { padding: 32px 24px 80px; }

  body[data-theme="light"] { background: #f4f1ea; color: #2a2724; }
  body[data-theme="light"] .top h1 { color: #B8481F; }
  body[data-theme="light"] .top p { color: #555; }
  body[data-theme="light"] .top .tag { background: #ece8df; border-color: #d8d3c7; color: #6b6b6b; }
  body[data-theme="light"] .top .preview-note { background: #ece8df; color: #4a463f; }
  body[data-theme="light"] .top .preview-note strong { color: #B8481F; }
  body[data-theme="light"] .controls { background: linear-gradient(to bottom, #f4f1ea 0%, #f4f1ea 60%, rgba(244,241,234,0.85) 100%); }
  body[data-theme="light"] .controls button { color: #4a463f; border-color: #c8c2b3; }
  body[data-theme="light"] .controls button:hover { color: #2a2724; border-color: #6b6b6b; }
  body[data-theme="light"] .controls .lang-toggle { border-color: #c8c2b3; }
  body[data-theme="light"] .row-header { border-left-color: #B8481F; }
  body[data-theme="light"] .row-num { color: #B8481F; }
  body[data-theme="light"] .row-title { color: #2a2724; }
  body[data-theme="light"] .row-meta { color: #777; }
  body[data-theme="light"] .page-label { color: #777; }
  body[data-theme="light"] .page-outer { box-shadow: 0 8px 30px rgba(0,0,0,0.15); }

  .top { max-width: 1500px; margin: 0 auto 24px; }
  .top h1 { font-family: 'Playfair Display', serif; font-style: italic; font-weight: 900; font-size: 32px; color: #E63C2E; margin-bottom: 6px; letter-spacing: -0.01em; }
  .top p { color: #999; font-size: 13px; line-height: 1.6; max-width: 900px; }
  .top strong { color: #F5EEDF; }
  .top em { color: #E63C2E; font-style: normal; font-weight: 500; }
  .top .tag { display: inline-block; padding: 3px 9px; border-radius: 999px; background: #1a1a1a; border: 1px solid #2a2a2a; color: #888; font-family: 'Archivo', monospace; font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase; margin-top: 8px; }
  /* min-height sized for the longer GR text (2 lines) so toggling EN↔GR doesn't reflow the menus below. */
  .top .preview-note { margin-top: 14px; padding: 12px 16px; background: #1a1a1a; border-left: 3px solid #E8A23D; border-radius: 0 4px 4px 0; color: #c8c2b3; font-size: 12px; line-height: 1.55; min-height: 64px; box-sizing: border-box; }
  .top .preview-note strong { color: #E8A23D; }

  .controls { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; margin: 24px 0 32px; position: sticky; top: 0; z-index: 100; padding: 8px 0; background: linear-gradient(to bottom, #0d0d0d 0%, #0d0d0d 60%, rgba(13,13,13,0.85) 100%); }
  .controls button { padding: 9px 16px; background: transparent; color: #aaa; border: 1px solid #444; border-radius: 999px; font-family: 'Archivo', sans-serif; font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; cursor: pointer; transition: all 0.15s ease; }
  .controls button:hover { color: #fff; border-color: #888; }
  .controls button.active { background: #E63C2E; border-color: #E63C2E; color: #fff; }
  .controls .lang-toggle { display: inline-flex; border: 1px solid #444; border-radius: 999px; overflow: hidden; }
  .controls .lang-toggle button { border: none; border-radius: 0; padding: 9px 18px; display: inline-flex; align-items: center; justify-content: center; gap: 8px; }
  .controls .lang-toggle button.active { background: #E63C2E; color: #fff; }
  .controls .lang-toggle .flag { font-size: 14px; line-height: 1; }

  /* Theme toggle button — small icon-only button. */
  .controls .theme-toggle { padding: 9px 14px; min-width: 40px; }

  /* Mobile: pack all visible controls into a single row + give menu cards visible breathing room. */
  @media (max-width: 640px) {
    html, body { overflow-x: hidden; }
    body { padding: 12px 18px 60px; }
    /* Card scaler clips the scaled card's layout box to its visual (scaled) size — no overflow. */
    .card-scaler { overflow: hidden; }
    .controls { flex-direction: row; flex-wrap: nowrap; gap: 6px; justify-content: center; align-items: center; }
    .controls .lang-toggle { display: inline-flex; flex: 0 1 auto; width: auto; }
    .controls .lang-toggle button { padding: 8px 12px; font-size: 10px; }
    .controls .lang-toggle .flag { font-size: 13px; }
    .controls > button { padding: 8px 10px; font-size: 10px; letter-spacing: 0.06em; }
    .controls .theme-toggle { padding: 8px 10px; min-width: 38px; }
    /* Designer-only tools are hidden on mobile — irrelevant for bistro preview. */
    .controls .dev-control { display: none !important; }
    .top { margin-bottom: 14px; }
    .top h1 { font-size: 22px; }
    .top p { font-size: 12px; }
    .top .preview-note { font-size: 11px; padding: 10px 12px; min-height: 0; }
    .row { margin-bottom: 36px; }
    .row-meta { display: none; }
    /* Stack the two pages of each menu vertically with visible padding around so they don't kiss the viewport edge. */
    .spread { flex-direction: column; align-items: center; gap: 22px; padding: 6px 4px; }
    .page-wrap { max-width: 100%; }
  }

  /* Dev-only controls — hidden unless ?dev=1 */
  body:not([data-dev]) .dev-control { display: none; }

  /* EN/GR visibility */
  body[data-lang="en"] .lang-gr { display: none; }
  body[data-lang="gr"] .lang-en { display: none; }

  /* Designer toggle: force the original Playfair Display everywhere for comparison.
     Note: Playfair has no Greek glyphs, so in GR mode Greek chars will fall back to
     system serif — that mismatch is the whole reason we picked Noto Serif Display as default. */
  body.fonts-original .title,
  body.fonts-original .section-header {
    font-family: 'Playfair Display', serif !important;
  }

  /* Revisions toggle: swap which content set is visible. Both sets are rendered at build time;
     CSS just controls which is shown. */
  [data-revision="proposed"] { display: none; }
  body.revisions-on [data-revision="current"] { display: none; }
  body.revisions-on [data-revision="proposed"] { display: block; }

  /* PROPOSED revision — global header treatment: bigger TREVIZO wordmark, smaller menu titles, across every menu. */
  body.revisions-on [data-revision="proposed"] .wordmark { font-size: 14px; letter-spacing: 0.5em; padding-left: 0.5em; }
  body.revisions-on [data-revision="proposed"] .wines .title { font-size: 32px; }
  body.revisions-on [data-revision="proposed"] .cocktails .page.front .title { font-size: 36px; }
  body.revisions-on [data-revision="proposed"] .food .page.front .title { font-size: 40px; }
  body.revisions-on [data-revision="proposed"] .brunch .page.front .title { font-size: 42px; }
  body.revisions-on [data-revision="proposed"] .spirits .page.front .title { font-size: 28px; }
  body.revisions-on [data-revision="proposed"] .spirits .page.back .title { font-size: 40px; }
  /* PROPOSED Food front carries 2 sections (Wine Sides + Salads; Bruschetta moved to the back) —
     uses the default centered food-front treatment, no overrides needed. */

  /* PROPOSED: category/section headers (White, Red, Aperitivo, Coffee, Gin, …) slightly larger on every menu. */
  body.revisions-on [data-revision="proposed"] .section-header { font-size: 15px; }
  body.revisions-on [data-revision="proposed"] .a4 .section-header { font-size: 14.5px; }

  /* "Larger text" toggle — bumps product item text ~10% for a more generous A5 print read.
     Inter-item spacing is tightened so the densest pages still fit their fixed page height. */
  body.text-extended .item-name { font-size: 10.5px; }
  body.text-extended .item-price { font-size: 10.5px; }
  body.text-extended .item-desc { font-size: 8.5px; line-height: 1.22; }
  body.text-extended .item-region { font-size: 8.5px; line-height: 1.22; }
  body.text-extended .item { margin-bottom: 4px; }
  body.text-extended .section { margin-top: 10px; }
  body.text-extended .section-header { margin-bottom: 3px; }
  body.text-extended .col-header { font-size: 8px; }
  /* A4 (Beverages & Beers / Spirits) has headroom — bump it to match the A5 menus' larger-text feel
     instead of the timid +5% it had before (which made it look smaller than the A5 cards). */
  body.text-extended .a4 .item-name { font-size: 10px; }
  body.text-extended .a4 .item-price { font-size: 10px; }
  body.text-extended .a4 .item-desc { font-size: 8.5px; }
  body.text-extended .a4 .iced-tea-flavor .item-name { font-size: 8.5px; }
  body.text-extended .a4 .iced-tea-flavor .item-desc { font-size: 8px; }
  /* A4 has plenty of headroom — keep its generous spacing in larger-text mode (don't let the
     general .section/.item tightening above shrink it; that made Beverages/Spirits look cramped). */
  body.text-extended .a4 .item { margin-bottom: 5px; }
  body.text-extended .a4 .section { margin-top: 13px; }
  /* Food back is the densest A5 page (Bruschetta + Pinsa + Platter + Desserts) — tighten it further. */
  body.text-extended .food .page.back .item { margin-bottom: 2.5px; }
  body.text-extended .food .page.back .section { margin-top: 8px; }

  .row { max-width: 1500px; margin: 0 auto 50px; }
  .row-header { display: flex; align-items: baseline; gap: 16px; margin-bottom: 18px; padding: 6px 0 6px 14px; border-left: 3px solid #E63C2E; }
  .row-num { font-family: 'Archivo', monospace; font-size: 13px; color: #E63C2E; letter-spacing: 0.2em; font-weight: 600; }
  .row-title { font-family: 'Playfair Display', serif; font-style: italic; font-weight: 700; font-size: 22px; color: #F5EEDF; }
  .row-meta { font-family: 'Archivo', monospace; font-size: 11px; color: #777; letter-spacing: 0.12em; text-transform: uppercase; margin-left: auto; }

  .spread { display: flex; gap: 28px; flex-wrap: wrap; align-items: flex-start; }
  .page-wrap { display: flex; flex-direction: column; align-items: center; gap: 10px; }
  .page-label { font-family: 'Archivo', monospace; font-size: 10px; color: #777; letter-spacing: 0.2em; text-transform: uppercase; }

  .page-outer { position: relative; box-shadow: 0 8px 40px rgba(0,0,0,0.8); overflow: hidden; }
  .a5 { width: 370px; height: 518px; }
  .a4 { width: 518px; height: 728px; }

  .a5 .page { position: absolute; top: 7px; left: 7px; right: 7px; bottom: 7px; padding: 28px 30px 34px 30px; }
  .a4 .page { position: absolute; top: 7px; left: 7px; right: 7px; bottom: 7px; padding: 28px 40px 34px 40px; }

  /* Guides */
  .guides { position: absolute; inset: 0; pointer-events: none; opacity: 0; transition: opacity 0.2s; z-index: 50; }
  .show-guides .guides { opacity: 1; }
  .trim-line { position: absolute; top: 7px; left: 7px; right: 7px; bottom: 7px; border: 1.5px dashed rgba(232, 162, 61, 0.85); }
  .guide-label { position: absolute; font-family: 'Archivo', monospace; font-size: 9px; background: rgba(0,0,0,0.7); color: #E8A23D; padding: 2px 6px; border-radius: 2px; letter-spacing: 0.04em; }
  .guide-label.trim { top: 4px; left: 12px; }

  .logo-mascot { position: absolute; z-index: 2; pointer-events: none; }
  .logo-mascot img { display: block; width: 100%; height: 100%; object-fit: contain; object-position: center; }
  .logo-mascot::after { content: ''; position: absolute; inset: 0; border: 1px dashed rgba(232, 162, 61, 0); border-radius: 2px; transition: border-color 0.2s; pointer-events: none; }
  .show-guides .logo-mascot::after { border-color: rgba(232, 162, 61, 0.65); background: rgba(232, 162, 61, 0.04); }

  /* Typography — brand display serif is Noto Serif Display.
     Decided 2026-05-26 after A/B vs Playfair Display: Noto Serif Display unifies EN + GR
     rendering (Playfair has no Greek glyphs) and is available in Canva's default library. */
  .wordmark { font-family: 'Archivo Black', sans-serif; font-weight: 900; font-size: 11px; letter-spacing: 0.42em; text-align: center; padding-left: 0.42em; }
  .title { font-family: 'Noto Serif Display', serif; font-weight: 900; font-style: italic; line-height: 1; text-align: center; letter-spacing: -0.01em; }
  .title-roman { font-style: normal; letter-spacing: -0.005em; line-height: 0.95; }
  .title-stacked { line-height: 0.95; }
  /* Kitchen hours line — sits just above the footer on Food front. Mirrors the footer's styling
     so the two read as a stacked block at the bottom of the page. */
  .kitchen-hours { position: absolute; bottom: 36px; left: 30px; right: 30px; text-align: center; font-family: 'Archivo', sans-serif; font-weight: 400; font-style: italic; font-size: 8px; letter-spacing: 0.18em; text-transform: uppercase; opacity: 0.7; }

  .col-header { display: flex; justify-content: flex-end; align-items: baseline; font-family: 'Archivo', sans-serif; font-weight: 500; font-size: 7px; letter-spacing: 0.22em; text-transform: uppercase; opacity: 0.55; }
  .col-header span { padding-left: 0.8em; }
  .rule { height: 1px; opacity: 0.28; margin: 2px 0 4px; }
  .section { margin-top: 12px; }
  .section:first-of-type { margin-top: 10px; }
  .section-header { font-family: 'Noto Serif Display', serif; font-style: italic; font-weight: 700; font-size: 13px; margin-bottom: 4px; }
  .item { margin-bottom: 6px; }
  .item-row { display: grid; grid-template-columns: 1fr auto; column-gap: 8px; align-items: baseline; }
  .item-name { font-family: 'Archivo', sans-serif; font-weight: 600; font-size: 9.5px; line-height: 1.25; }
  .item-name .qty { font-weight: 400; font-style: italic; font-size: 8px; opacity: 0.7; margin-left: 0.2em; }
  .item-price { font-family: 'Archivo', sans-serif; font-weight: 600; font-size: 9.5px; white-space: nowrap; font-feature-settings: "tnum"; }
  .item-desc { font-family: 'Archivo', sans-serif; font-weight: 400; font-size: 8px; margin-top: 1px; line-height: 1.3; padding-right: 30px; }
  .item-region { font-family: 'Archivo', sans-serif; font-weight: 400; font-size: 8px; margin-top: 1px; line-height: 1.3; padding-right: 30px; opacity: 0.7; }
  .footer { position: absolute; bottom: 22px; left: 30px; right: 30px; text-align: center; font-family: 'Archivo', sans-serif; font-weight: 400; font-size: 7px; opacity: 0.55; letter-spacing: 0.18em; text-transform: uppercase; }

  /* A4 spirits/beverages scaling — breathing room between items and sections (applies to both pages of menu 05). */
  .a4 .section { margin-top: 16px; }
  .a4 .section-header { font-size: 13px; padding-bottom: 3px; border-bottom: 1px solid currentColor; margin-bottom: 6px; }
  .a4 .item { margin-bottom: 5px; break-inside: avoid; }
  .a4 .item-name { font-weight: 500; }
  .a4 .footer { bottom: 18px; left: 40px; right: 40px; }
  .a4 .iced-tea-flavors { padding-left: 6px; break-inside: avoid; }
  .a4 .iced-tea-flavor { font-family: 'Archivo', sans-serif; font-weight: 400; font-style: italic; font-size: 7.5px; opacity: 0.78; line-height: 1.4; margin-bottom: 0; }
  .a4 .iced-tea-flavor .item-name { font-weight: 400; font-style: italic; font-size: 7.5px; }
  .a4 .iced-tea-flavor .item-desc { font-size: 7px; opacity: 0.85; padding-right: 0; }

  /* Beverages front: 2-column item flow within each section. Section headers span full width. */
  .spirits .page.front .col-2 { column-count: 2; column-gap: 20px; }
  .spirits .page.front .col-2 .section-header { column-span: all; -webkit-column-span: all; }

  /* Brunch edge band — dusk blue (was vermilion). Takes the freed-up palette slot since Cocktails moved to orange.
     Toggle .colors-original on body reverts to the original deeper vermilion. */
  .brunch-edge-band { position: absolute; top: 0; left: 0; bottom: 0; width: 40px; background: #2C5687; z-index: 1; display: flex; align-items: center; justify-content: center; overflow: hidden; }
  body.colors-original .brunch-edge-band { background: #C8362E; }
  .brunch-edge-band .vertical-text { font-family: 'Archivo', sans-serif; font-weight: 600; font-size: 11px; letter-spacing: 0.32em; color: #F5EEDF; white-space: nowrap; transform: rotate(-90deg); transform-origin: center center; padding-left: 0.32em; }

  /* ───── Per-menu treatments ───── */
  .wines.page-outer { background: #5E2A2E; }
  .wines .page { color: #F5EEDF; }
  .wines .title { font-size: 50px; margin-top: 8px; }
  .wines .rule { background: #F5EEDF; }
  .wines .item-region { color: #F5EEDF; }
  .wines .corner-mascot { bottom: 24px; right: 22px; width: 88px; height: 112px; }
  /* Wines back: vertically center the Rosé + Champagne lists with extra section gap — mirrors the Cocktails back layout. */
  .wines .page.back { display: flex; flex-direction: column; justify-content: center; padding-top: 28px; padding-bottom: 50px; }
  .wines .page.back .section:first-of-type { margin-top: 0; }
  .wines .page.back .section + .section { margin-top: 28px; }

  /* Cocktails background: spritz orange (Aperol-inspired). Replaces dusk blue.
     Passes WCAG AA contrast (~5.3:1) with cream #F5EEDF text.
     Toggle .colors-original on body reverts to the original dusk blue for A/B comparison. */
  .cocktails.page-outer { background: #B8481F; }
  body.colors-original .cocktails.page-outer { background: #2C5687; }

  /* Sticker variant — risograph cutouts as accents in each menu's negative space.
     Hidden by default; revealed via the "Sticker variant" toggle. */
  .sticker-overlay { display: none; position: absolute; pointer-events: none; z-index: 1; transform-origin: center; }
  body.variant-stickers .sticker-overlay { display: block; }
  /* Soft drop shadow to lift the sticker off the menu, like a print-and-stick effect. */
  body.variant-stickers .sticker-overlay { filter: drop-shadow(0 2px 4px rgba(0,0,0,0.18)); }
  /* In sticker variant: some stickers replace the mascot in their slot — hide the mascot there. */
  body.variant-stickers .spirits .page.back .logo-mascot.corner-mascot { display: none; }
  .cocktails .page { color: #F5EEDF; }
  .cocktails .page.front { padding-top: 150px; padding-bottom: 50px; display: flex; flex-direction: column; }
  .cocktails .page.front .title { font-size: 44px; margin-top: 8px; }
  .cocktails .page.front .sections-wrap { flex: 1; display: flex; flex-direction: column; justify-content: center; }
  .cocktails .page.front .sections-wrap .section:first-of-type { margin-top: 0; }
  .cocktails .item-desc { color: #F5EEDF; }
  .cocktails .front-mascot { top: 22px; left: 50%; transform: translateX(-50%); width: 88px; height: 112px; }
  .cocktails .page.back { display: flex; flex-direction: column; justify-content: center; padding-top: 28px; padding-bottom: 50px; }
  .cocktails .page.back .section:first-of-type { margin-top: 0; }
  .cocktails .page.back .section + .section { margin-top: 28px; }

  .food.page-outer { background: #F5EEDF; }
  .food .page { color: #5E2A2E; }
  .food .page.front { padding-top: 150px; padding-bottom: 50px; display: flex; flex-direction: column; }
  /* Title is now single-word ("Food" / "Φαγητό") — restored full display size to match Wines/Brunch. */
  .food .page.front .title { font-size: 50px; margin-top: 8px; line-height: 1; }
  .food .page.front .sections-wrap { flex: 1; display: flex; flex-direction: column; justify-content: center; }
  .food .page.front .sections-wrap .section:first-of-type { margin-top: 0; }
  .food .rule { background: #5E2A2E; }
  .food .item-desc { color: #5E2A2E; opacity: 0.8; }
  .food .item-region { color: #5E2A2E; }
  .food .front-mascot { top: 22px; left: 50%; transform: translateX(-50%); width: 88px; height: 112px; }

  .brunch.page-outer { background: #F5EEDF; }
  .brunch .page { color: #5E2A2E; padding-left: 60px; padding-right: 50px; }
  .brunch .page.front { padding-top: 150px; padding-bottom: 50px; display: flex; flex-direction: column; }
  .brunch .page.front .title { font-size: 54px; margin-top: 8px; }
  .brunch .page.front .sections-wrap { flex: 1; display: flex; flex-direction: column; justify-content: center; }
  .brunch .page.front .sections-wrap .section:first-of-type { margin-top: 0; }
  .brunch .page.back { display: flex; flex-direction: column; justify-content: center; padding-top: 28px; padding-bottom: 50px; }
  .brunch .page.back .section:first-of-type { margin-top: 0; }
  .brunch .page.back .section + .section { margin-top: 18px; }
  .brunch .rule { background: #5E2A2E; }
  .brunch .item-desc { color: #5E2A2E; opacity: 0.8; }
  .brunch .front-mascot { top: 22px; left: calc(50% + 14px); transform: translateX(-50%); width: 88px; height: 112px; }

  .spirits.page-outer { background: #1F5F63; }
  .spirits .page { color: #F5EEDF; }
  .spirits .page.front { padding-top: 175px; }
  /* Spirits back: title sits higher with a generous gap to the lists. Reduces the "bottom-heavy" feel
     while keeping the right column top-aligned with the left (Vodka level with Gin). */
  .spirits .page.back { padding-top: 28px; }
  .spirits .page.back .spirits-grid { margin-top: 36px; }
  .spirits .title { margin-top: 8px; }
  .spirits .page.front .title { font-size: 34px; line-height: 1; white-space: nowrap; }
  .spirits .page.back .title { font-size: 50px; }
  .spirits .page.front .section:first-of-type { margin-top: 24px; }
  .spirits .rule { background: #F5EEDF; }
  .spirits .front-mascot { top: 24px; left: 50%; transform: translateX(-50%); width: 104px; height: 131px; }
  /* Spirits back mascot: positioned more centrally in the right-column empty space below Whiskey,
     instead of tucked into the bottom-right corner. Moves up + leftward to fill the whitespace. */
  .spirits .corner-mascot { bottom: 100px; right: 70px; width: 104px; height: 131px; }

  .spirits-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; margin-top: 14px; }
  .spirits .spirits-grid .section:first-of-type { margin-top: 0; }
  /* Right col content aligns to top (Vodka level with Gin) — was justify-content: center which made Vodka float. */
  .spirits .right-col { display: flex; flex-direction: column; justify-content: flex-start; }
  .spirits .right-col .section { padding-right: 14px; }
  .spirits .right-col .section:first-of-type { margin-top: 0; }
"""

SCRIPT = """
  // Read URL flags
  const params = new URLSearchParams(location.search);
  if (params.get('dev') === '1') document.body.dataset.dev = '1';

  // Initial language from URL (?lang=gr) or default to EN
  const initialLang = params.get('lang') === 'gr' ? 'gr' : 'en';
  document.body.dataset.lang = initialLang;
  document.querySelectorAll('[data-lang-btn]').forEach(b => {
    b.classList.toggle('active', b.dataset.langBtn === initialLang);
  });

  function setLang(lang) {
    document.body.dataset.lang = lang;
    document.querySelectorAll('[data-lang-btn]').forEach(b => {
      b.classList.toggle('active', b.dataset.langBtn === lang);
    });
    const u = new URL(location.href);
    u.searchParams.set('lang', lang);
    history.replaceState(null, '', u);
  }

  function toggleGuides(btn) {
    document.querySelectorAll('.page-outer').forEach(el => el.classList.toggle('show-guides'));
    btn.classList.toggle('active');
  }

  function toggleOriginalFonts(btn) {
    document.body.classList.toggle('fonts-original');
    btn.classList.toggle('active');
  }

  // Color comparison: dusk blue Cocktails + vermilion Brunch ribbon (the original palette).
  function toggleOriginalColors(btn) {
    document.body.classList.toggle('colors-original');
    btn.classList.toggle('active');
  }

  // Proposed revisions: swaps the rendered content from `en/gr.md` to `en/gr-proposed.md` rendering.
  function toggleRevisions(btn) {
    document.body.classList.toggle('revisions-on');
    btn.classList.toggle('active');
  }

  // Larger text: bumps product item text for evaluating A5 print legibility.
  function toggleExtended(btn) {
    document.body.classList.toggle('text-extended');
    btn.classList.toggle('active');
  }

  // Sticker variant: layer riso-style cutouts on each menu's negative space.
  function toggleStickers(btn) {
    document.body.classList.toggle('variant-stickers');
    btn.classList.toggle('active');
  }

  // Theme: dark (default) ⇄ light. Persisted via localStorage so the preference survives reload.
  const savedTheme = localStorage.getItem('trevizo-theme') || 'dark';
  if (savedTheme === 'light') document.body.dataset.theme = 'light';
  document.querySelectorAll('[data-theme-icon]').forEach(el => {
    el.textContent = savedTheme === 'light' ? '☀️' : '🌙';
  });
  function toggleTheme(btn) {
    const next = document.body.dataset.theme === 'light' ? 'dark' : 'light';
    if (next === 'light') document.body.dataset.theme = 'light';
    else delete document.body.dataset.theme;
    localStorage.setItem('trevizo-theme', next);
    btn.querySelector('[data-theme-icon]').textContent = next === 'light' ? '☀️' : '🌙';
  }

  // Mobile fit: the menu cards have fixed pixel widths (A5 370px, A4 518px) that overflow a phone
  // viewport, exposing the page background beyond the card. Scale each card down with `zoom` (which,
  // unlike transform, also shrinks the layout box so there's no horizontal overflow and the page-label
  // sits flush below). Cards stay centered with breathing room via the mobile .spread flex centering.
  function fitMobileCards() {
    const mobile = window.matchMedia('(max-width: 640px)').matches;
    const avail = document.documentElement.clientWidth - 36; // side breathing room
    document.querySelectorAll('.card-scaler').forEach(scaler => {
      const card = scaler.querySelector('.page-outer');
      if (!card) return;
      if (!mobile) {
        scaler.style.width = scaler.style.height = '';
        card.style.transform = card.style.transformOrigin = '';
        return;
      }
      const isA4 = card.classList.contains('a4');
      const w = isA4 ? 518 : 370, h = isA4 ? 728 : 518;
      const scale = Math.min(1, avail / w);
      // Size the scaler to the scaled card so layout reflows correctly; scale the card inside it.
      // transform (unlike zoom) reliably scales the absolutely-positioned .page child on iOS Safari.
      scaler.style.width = (w * scale).toFixed(1) + 'px';
      scaler.style.height = (h * scale).toFixed(1) + 'px';
      card.style.transformOrigin = 'top left';
      card.style.transform = 'scale(' + scale.toFixed(4) + ')';
    });
  }
  window.addEventListener('resize', fitMobileCards);
  window.addEventListener('orientationchange', fitMobileCards);
  fitMobileCards();
"""


def render_html(
    en: list[Menu], gr: list[Menu],
    en_proposed: Optional[list[Menu]] = None,
    gr_proposed: Optional[list[Menu]] = None,
) -> str:
    current_rows = "\n".join(render_menu(i, em, gm) for i, (em, gm) in enumerate(zip(en, gr)))
    proposed_rows = ""
    if en_proposed and gr_proposed:
        proposed_rows = "\n".join(
            render_menu(i, em, gm) for i, (em, gm) in enumerate(zip(en_proposed, gr_proposed))
        )
    menu_rows = (
        f'<div data-revision="current">{current_rows}</div>'
        + (f'<div data-revision="proposed">{proposed_rows}</div>' if proposed_rows else "")
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Trevizo · Menu Preview</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600&family=Archivo+Black&family=Noto+Serif+Display:ital,wght@0,700;0,900;1,700;1,900&family=Playfair+Display:ital,wght@0,700;0,900;1,700;1,900&display=swap" rel="stylesheet">
  <style>{STYLES}</style>
</head>
<body data-lang="en" class="revisions-on">
  <div class="top">
    <h1>Trevizo · Menu Preview</h1>
    <p>
      <span class="lang-en">All five menus, both sides. Use the toggle to switch between English and Greek.</span>
      <span class="lang-gr">Και οι πέντε κατάλογοι, και οι δύο πλευρές. Χρησιμοποιήστε τον διακόπτη για εναλλαγή Αγγλικά / Ελληνικά.</span>
    </p>
    <div class="preview-note">
      <strong>
        <span class="lang-en">Preview only.</span>
        <span class="lang-gr">Μόνο για προεπισκόπηση.</span>
      </strong>
      <span class="lang-en"> Final colors and paper feel will be confirmed at print proof. Please review: item names, prices, descriptions, and Greek translations. Layout and design are locked.</span>
      <span class="lang-gr"> Τα τελικά χρώματα και η αίσθηση του χαρτιού θα επιβεβαιωθούν στο proof εκτύπωσης. Παρακαλώ ελέγξτε: ονόματα, τιμές, περιγραφές και ελληνικές μεταφράσεις. Η διάταξη και ο σχεδιασμός είναι κλειδωμένα.</span>
    </div>
  </div>

  <div class="controls">
    <div class="lang-toggle">
      <button data-lang-btn="en" onclick="setLang('en')"><span class="flag">🇬🇧</span> EN</button>
      <button data-lang-btn="gr" onclick="setLang('gr')"><span class="flag">🇬🇷</span> GR</button>
    </div>
    <button class="theme-toggle" onclick="toggleTheme(this)" title="Toggle light/dark theme"><span data-theme-icon>🌙</span></button>
    <button class="dev-control" onclick="toggleOriginalColors(this)" title="Compare new colors vs. original palette">Original colors</button>
    <button class="dev-control active" onclick="toggleRevisions(this)" title="Toggle between the proposed (default) and original menu content">Proposed ⇄ original</button>
    <button onclick="toggleExtended(this)" title="Preview larger product text for A5 print">Larger text</button>
    <button class="dev-control" onclick="toggleStickers(this)" title="Show risograph sticker accents on each menu">Sticker variant</button>
    <button class="dev-control" onclick="toggleGuides(this)">Show trim · margins · mascot zone</button>
    <button class="dev-control" onclick="toggleOriginalFonts(this)">Use Playfair Display (original)</button>
  </div>

{menu_rows}

  <script>{SCRIPT}</script>
</body>
</html>
"""


def main() -> int:
    if not CONTENT_EN.exists():
        print(f"missing: {CONTENT_EN}", file=sys.stderr)
        return 1
    if not CONTENT_GR.exists():
        print(f"missing: {CONTENT_GR}", file=sys.stderr)
        return 1

    en = parse(CONTENT_EN.read_text(encoding="utf-8"))
    gr = parse(CONTENT_GR.read_text(encoding="utf-8"))

    print(f"parsed: {len(en)} menus (EN), {len(gr)} menus (GR)")
    validate(en, gr)
    print("validated: structural parity OK")

    en_proposed = None
    gr_proposed = None
    if CONTENT_EN_PROPOSED.exists() and CONTENT_GR_PROPOSED.exists():
        en_proposed = parse(CONTENT_EN_PROPOSED.read_text(encoding="utf-8"))
        gr_proposed = parse(CONTENT_GR_PROPOSED.read_text(encoding="utf-8"))
        print(f"parsed proposed: {len(en_proposed)} menus (EN), {len(gr_proposed)} menus (GR)")
        validate(en_proposed, gr_proposed)
        print("validated: proposed parity OK")

    html = render_html(en, gr, en_proposed, gr_proposed)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"wrote: {OUTPUT} ({len(html):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
