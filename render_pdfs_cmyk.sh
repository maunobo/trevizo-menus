#!/usr/bin/env bash
# Convert the RGB print PDFs (pdf/) into print-shop CMYK PDF/X-3 files (pdf-cmyk/).
#   - RGB → DeviceCMYK via a coated profile
#   - PDF/X-3 output intent embedded
#   - fonts embedded, prepress settings (no image downsampling), page size + bleed preserved
#
# Profile: Ghostscript bundled default_cmyk.icc (coated, SWOP-like). To use your printer's
# exact profile (e.g. ISO Coated v2 / FOGRA39), drop the .icc in this folder and set ICC=... below.
set -euo pipefail
cd "$(dirname "$0")"

ICC="$(find /opt/homebrew/Cellar/ghostscript -name default_cmyk.icc | head -1)"
[ -f "$ICC" ] || { echo "CMYK ICC profile not found"; exit 1; }
OUT_COND="Coated CMYK (Ghostscript default_cmyk)"

mkdir -p pdf-cmyk

# PDF/X-3 definition: registers the ICC as the output intent.
DEF="$(mktemp -t pdfx_def).ps"
cat > "$DEF" <<PSDEF
%!
[ /_objdef {icc_PDFX} /type /stream /OBJ pdfmark
[ {icc_PDFX} << /N 4 >> /PUT pdfmark
[ {icc_PDFX} ($ICC) (r) file /PUT pdfmark
[ /_objdef {OutputIntent_PDFX} /type /dict /OBJ pdfmark
[ {OutputIntent_PDFX} <<
    /Type /OutputIntent /S /GTS_PDFX
    /OutputCondition ($OUT_COND)
    /OutputConditionIdentifier (Custom)
    /Info ($OUT_COND)
    /DestOutputProfile {icc_PDFX}
  >> /PUT pdfmark
[ {Catalog} << /OutputIntents [ {OutputIntent_PDFX} ] >> /PUT pdfmark
PSDEF

for src in pdf/*.pdf; do
  base="$(basename "$src")"
  out="pdf-cmyk/${base%.pdf}-CMYK.pdf"
  gs -dPDFX -dBATCH -dNOPAUSE -dNOSAFER \
     -sDEVICE=pdfwrite \
     -dPDFSETTINGS=/prepress \
     -dCompatibilityLevel=1.3 \
     -sColorConversionStrategy=CMYK \
     -dProcessColorModel=/DeviceCMYK \
     -dOverrideICC=true \
     -sOutputICCProfile="$ICC" \
     -dEmbedAllFonts=true -dSubsetFonts=true \
     -dAutoRotatePages=/None \
     -dDownsampleColorImages=false -dDownsampleGrayImages=false \
     -sOutputFile="$out" \
     "$DEF" "$src" >/dev/null 2>&1
  echo "  $out"
done

rm -f "$DEF"
echo "Done — $(ls pdf-cmyk/*.pdf | wc -l | tr -d ' ') CMYK PDF/X files in pdf-cmyk/"
