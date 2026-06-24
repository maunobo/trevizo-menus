#!/usr/bin/env python3
"""Build the two working mascots from the designer/edited high-res logos.

  - trevizo-logo-cream-hires.png    = the user's beige+black croc (transparent) — dark-flood menus
                                        (Wines, Cocktails, Spirits). Reads crisp on maroon/teal/orange.
  - trevizo-logo-vermilion-hires.png = the orange croc, white background knocked out — cream-paper
                                        menus (Food, Brunch). Pops on cream.

Both resized to a lean-but-print-perfect working width.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

Image.MAX_IMAGE_PIXELS = None
ASSETS = Path(__file__).resolve().parent / "assets"
BEIGE = ASSETS / "trevizo-logo-beige.png"                          # already transparent
ORANGE = ASSETS / "LOGOS-FROM-DESIGNER" / "trevizo-logo-orange-CLEAN (1).png"  # white background
WORK_W = 2400
SENT = (255, 0, 255)
FF_THRESH = 60


def resized(img: Image.Image, w: int) -> Image.Image:
    return img.resize((w, round(img.height * w / img.width)), Image.LANCZOS)


def knockout_white(rgb: Image.Image) -> Image.Image:
    """Return RGBA with the outer white background made transparent (keeps interior whites)."""
    ff = rgb.copy()
    w, h = ff.size
    for corner in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        ImageDraw.floodfill(ff, corner, SENT, thresh=FF_THRESH)
    arr = np.asarray(ff)
    is_bg = (arr[:, :, 0] == SENT[0]) & (arr[:, :, 1] == SENT[1]) & (arr[:, :, 2] == SENT[2])
    alpha = Image.fromarray(np.where(is_bg, 0, 255).astype("uint8"), "L")
    out = rgb.copy(); out.putalpha(alpha)
    return out


def main() -> int:
    # Beige (already transparent) -> cream slot (dark-flood menus)
    beige = Image.open(BEIGE).convert("RGBA")
    resized(beige, WORK_W).save(ASSETS / "trevizo-logo-cream-hires.png")

    # Orange (white bg) -> knockout -> vermilion slot (cream-paper menus)
    orange = knockout_white(Image.open(ORANGE).convert("RGB"))
    resized(orange, WORK_W).save(ASSETS / "trevizo-logo-vermilion-hires.png")

    print("wrote trevizo-logo-cream-hires.png (beige) and trevizo-logo-vermilion-hires.png (orange)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
