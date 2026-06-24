#!/usr/bin/env python3
"""Print-export renderer — emits one clean, paginated, print-scaled HTML per menu per language.

Each output file contains the PROPOSED menu content with the proposed styling, laid out as two
print pages (front + back) at exact trim + 3mm bleed:
  - A5 menus → 154 × 216 mm pages
  - A4 menu  → 216 × 303 mm pages

Real (selectable) text + flood backgrounds (print-color-adjust: exact) so a headless-Chrome
print-to-PDF keeps text editable on import into Canva.

Usage:  python3 print_export.py          # writes print/*.html
Then render to PDF with render_pdfs.sh (headless Chrome).
"""
from __future__ import annotations
from pathlib import Path

import build  # reuse parse(), render_side(), MENU_CONFIG, STYLES

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "print"

# The preview cards are 370px (A5) / 518px (A4) wide, where 370px represents 154mm (incl. bleed).
# To fill a print page we scale the card up. Page size in CSS px (96dpi): mm * 96 / 25.4.
# Use the larger of width/height scale so the card fully covers the page (tiny excess is clipped
# in the bleed zone, never the trim area). Both formats work out to ~1.576.
PRINT_SCALE = 1.576

PAGE_SIZE = {
    "A5": "154mm 216mm",
    "A4": "216mm 303mm",
}
PAGE_DIMS_CSS = {
    "A5": ("154mm", "216mm"),
    "A4": ("216mm", "303mm"),
}

LANGS = ("en", "gr")


def print_css(fmt: str) -> str:
    w, h = PAGE_DIMS_CSS[fmt]
    return f"""
  /* ── Print export overrides ── */
  @page {{ size: {PAGE_SIZE[fmt]}; margin: 0; }}
  * {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
  html, body {{ margin: 0; padding: 0; background: #fff; }}

  /* Each side is one full bleed page. */
  .print-page {{
    width: {w}; height: {h};
    overflow: hidden;
    position: relative;
    page-break-after: always;
    break-after: page;
  }}
  .print-page:last-child {{ page-break-after: auto; break-after: auto; }}

  /* Neutralise preview chrome: no centering wrapper, no labels, no guides. */
  .print-page .page-wrap {{ display: block; gap: 0; margin: 0; align-items: stretch; }}
  .print-page .card-scaler {{ display: block; width: auto !important; height: auto !important; overflow: visible !important; }}
  .print-page .page-label,
  .print-page .guides {{ display: none !important; }}

  /* Scale the card up to fill the print page (vector text stays crisp/selectable). */
  .print-page .page-outer {{
    transform: scale({PRINT_SCALE});
    transform-origin: top left;
    box-shadow: none !important;
  }}
"""


def render_print_doc(menu_en, menu_gr, cfg, lang: str) -> str:
    sides = []
    for i, (es, gs) in enumerate(zip(menu_en.sides, menu_gr.sides)):
        side_html = build.render_side(es, gs, cfg, menu_en, menu_gr, is_front=(i == 0))
        # Print files live in print/ — rewrite asset paths up one level.
        side_html = side_html.replace('src="assets/', 'src="../assets/')
        sides.append(f'<div class="print-page {cfg["format"].lower()}">{side_html}</div>')

    # revisions-on + data-revision="proposed" so the proposed-specific CSS (header sizes, title
    # sizes, one-line spirits title) applies exactly as approved.
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600&family=Archivo+Black&family=Noto+Serif+Display:ital,wght@0,700;0,900;1,700;1,900&family=Playfair+Display:ital,wght@0,700;0,900;1,700;1,900&display=swap" rel="stylesheet">
  <style>{build.STYLES}</style>
  <style>{print_css(cfg["format"])}</style>
</head>
<body data-lang="{lang}" class="revisions-on">
  <div data-revision="proposed">
    {"".join(sides)}
  </div>
</body>
</html>
"""


def main() -> int:
    OUT_DIR.mkdir(exist_ok=True)
    en = build.parse(build.CONTENT_EN_PROPOSED.read_text(encoding="utf-8"))
    gr = build.parse(build.CONTENT_GR_PROPOSED.read_text(encoding="utf-8"))
    build.validate(en, gr)

    written = []
    for idx, (em, gm) in enumerate(zip(en, gr)):
        cfg = build.MENU_CONFIG[idx]
        for lang in LANGS:
            doc = render_print_doc(em, gm, cfg, lang)
            slug = f"{idx+1:02d}-{cfg['slug']}-{lang}"
            path = OUT_DIR / f"{slug}.html"
            path.write_text(doc, encoding="utf-8")
            written.append((slug, cfg["format"]))

    print(f"wrote {len(written)} print HTML files to {OUT_DIR}")
    for slug, fmt in written:
        print(f"  {slug}.html  ({fmt})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
