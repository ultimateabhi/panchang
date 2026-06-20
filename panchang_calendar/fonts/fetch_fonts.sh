#!/usr/bin/env bash
# One-time download of bundled fonts (OFL). Run once; the .ttf files are committed.
set -euo pipefail
cd "$(dirname "$0")"
base="https://github.com/google/fonts/raw/main/ofl"
curl -fL -o NotoSansDevanagari.ttf "$base/notosansdevanagari/NotoSansDevanagari%5Bwdth%2Cwght%5D.ttf"
curl -fL -o NotoSerif.ttf          "$base/notoserif/NotoSerif%5Bwdth%2Cwght%5D.ttf"
curl -fL -o CormorantGaramond.ttf  "$base/cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf"
echo "Fonts downloaded:"; ls -la *.ttf
