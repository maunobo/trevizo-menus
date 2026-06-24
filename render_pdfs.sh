#!/usr/bin/env bash
# Render every print/*.html to pdf/*.pdf via headless Chrome.
# Text stays vector/selectable; flood backgrounds print (print-color-adjust: exact).
set -euo pipefail
cd "$(dirname "$0")"

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
mkdir -p pdf

for html in print/*.html; do
  base="$(basename "${html%.html}")"
  out="pdf/${base}.pdf"
  "$CHROME" --headless=new --disable-gpu --no-pdf-header-footer \
    --print-to-pdf="$out" --virtual-time-budget=10000 \
    "file://$PWD/$html" >/dev/null 2>&1
  echo "  $out"
done
echo "Done — $(ls pdf/*.pdf | wc -l | tr -d ' ') PDFs in pdf/"
