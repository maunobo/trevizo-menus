#!/usr/bin/env python3
"""Add a correct TrimBox + visible crop marks to the CMYK print PDFs.

Input PDFs have MediaBox = trim + 3mm bleed (flood already runs to that edge), but TrimBox
equals MediaBox (wrong — tells the printer to cut at the bleed edge). This:
  1. Enlarges the MediaBox by a mark margin so crop marks have room.
  2. Sets BleedBox = the original page (the 3mm-bleed sheet).
  3. Sets TrimBox = 3mm inside the bleed sheet (the real cut line).
  4. Draws 8 crop marks at the trim corners.

Run after render_pdfs_cmyk.sh. Writes *-PRINT.pdf alongside.
"""
from __future__ import annotations
import sys
from pathlib import Path
import pikepdf

MM = 72.0 / 25.4
BLEED = 3 * MM            # 3mm bleed (already baked into the flood / MediaBox)
MARGIN = 6 * MM           # white room added around the sheet for the marks
MARK_LEN = 4 * MM         # length of each crop-mark tick
MARK_GAP = 1.5 * MM       # gap between trim corner and the tick
MARK_W = 0.4              # stroke width (pt)

ROOT = Path(__file__).resolve().parent


def marks_stream(x0, y0, x1, y1) -> bytes:
    """8 crop marks at the trim rectangle corners (x0,y0)-(x1,y1), in PDF user space."""
    g = MARK_GAP
    L = MARK_LEN
    segs = []
    for (cx, cy, sx, sy) in [
        (x0, y0, -1, -1),  # bottom-left
        (x1, y0, +1, -1),  # bottom-right
        (x0, y1, -1, +1),  # top-left
        (x1, y1, +1, +1),  # top-right
    ]:
        # horizontal tick (extends outward in x)
        segs.append((cx + sx * g, cy, cx + sx * (g + L), cy))
        # vertical tick (extends outward in y)
        segs.append((cx, cy + sy * g, cx, cy + sy * (g + L)))
    ops = [b"q", b"0 0 0 RG", f"{MARK_W} w".encode()]
    for (ax, ay, bx, by) in segs:
        ops.append(f"{ax:.3f} {ay:.3f} m {bx:.3f} {by:.3f} l S".encode())
    ops.append(b"Q")
    return b"\n".join(ops)


def process(src: Path, dst: Path) -> str:
    pdf = pikepdf.open(src)
    for page in pdf.pages:
        mb = [float(v) for v in page.MediaBox]
        bw, bh = mb[2] - mb[0], mb[3] - mb[1]          # bleed-sheet size
        # New media = bleed sheet + margin all around (content coords unchanged: shift origin negative)
        nmb = [mb[0] - MARGIN, mb[1] - MARGIN, mb[2] + MARGIN, mb[3] + MARGIN]
        # Trim = 3mm inside the bleed sheet
        tb = [mb[0] + BLEED, mb[1] + BLEED, mb[2] - BLEED, mb[3] - BLEED]
        page.MediaBox = nmb
        page.BleedBox = [mb[0], mb[1], mb[2], mb[3]]
        page.TrimBox = tb
        # Draw crop marks at the trim corners
        page.contents_add(
            pikepdf.Stream(pdf, marks_stream(tb[0], tb[1], tb[2], tb[3])),
            prepend=False,
        )
    pdf.save(dst)
    pdf.close()
    return f"{dst.name}  (trim {(tb[2]-tb[0])/MM:.0f}x{(tb[3]-tb[1])/MM:.0f}mm, media {(nmb[2]-nmb[0])/MM:.0f}x{(nmb[3]-nmb[1])/MM:.0f}mm)"


def main() -> int:
    src_dir = ROOT / "pdf-cmyk"
    out_dir = ROOT / "pdf-print"
    out_dir.mkdir(exist_ok=True)
    files = sorted(src_dir.glob("*-CMYK.pdf"))
    if not files:
        print("no CMYK PDFs found — run render_pdfs_cmyk.sh first", file=sys.stderr)
        return 1
    for src in files:
        dst = out_dir / (src.name.replace("-CMYK", "") .replace(".pdf", "-PRINT.pdf"))
        print("  " + process(src, dst))
    print(f"Done — {len(files)} files in {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
