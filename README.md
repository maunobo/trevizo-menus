# Trevizo — Menu Preview

Bilingual (EN/GR) menu preview for Trevizo (Italian Spritzeria, Νέα Πεντέλη, Athens).
Hosted via GitHub Pages for operator review before Canva print production.

## URL params

- `?lang=gr` — open in Greek
- `?dev=1` — show the trim/margins/mascot guides + font comparison toggle

## Editing content

1. Edit `content/en.md` or `content/gr.md` (pipe-delimited, see header of each file for format).
2. Run `python3 build.py` — regenerates `index.html`.
3. Commit + push. GitHub Pages redeploys automatically.

## Layout

```
content/
  en.md     # English copy (single source of truth)
  gr.md     # Greek mirror (same structure, line-by-line)
assets/
  trevizo-logo-{cream,vermilion,white}-resize.png
build.py    # Parser + HTML renderer (pure stdlib)
index.html  # Generated; served by GitHub Pages
TREVIZO_HANDOFF.md  # Design system reference
```

## Brand notes

See `TREVIZO_HANDOFF.md` for design system specs (colors, typography, mascot placements, A5/A4 dimensions).
