# Panchang Desk Calendar Generator

Generates print-ready design files — a multi-page **PDF** and **per-page PNGs at
300 DPI** — for a Vikram Samvat (pūrṇimānta) panchang desk calendar in the
**10 × 3.5 in long-desktop tent** format. One panel per lunar month + a cover;
page count is derived from the config (14 for the bundled VS 2083 leap year).

## Install

```bash
pip install -r requirements.txt
python -m playwright install chromium
bash fonts/fetch_fonts.sh          # one-time: download bundled fonts
```

## Run

```bash
python generate.py                 # full build → out/calendar.pdf + out/pages/*.png
python generate.py --months 2      # cover + first 2 months (quick preview)
python generate.py --png-only      # skip the PDF
python generate.py --config my.yaml --outdir build
```

## How the config maps to the layout

Everything is driven by `config/vs2083.yaml` — **edit the YAML, never the code**.

- `calendar:` — samvat year, reckoning, Gregorian span, and `cover:` text.
- `theme.page:` — `width_in`/`height_in` (panel size), `dpi` (PNG resolution),
  `top_safe_mm` (clear strip for the tent binding), `calendar_pct` (right-column
  width; raise it to give the grid/quote more room vs. the photo).
- `theme.fonts:` — family names; must match the bundled files in `fonts/`.
- `theme.ritu:` — per-season accent + Krishna/Shukla shading colours.
- `months:` — one entry per lunar month. `start`/`amavasya`/`end` are the
  Gregorian dates of Krishna 1 / new moon / Pūrṇimā. `photo` is relative to the
  YAML file. `quote.text`/`quote.attribution` print above the grid.
  `festivals:` are keyed by tithi (`{tithi: "S15", label: …}`,
  `{tithi: "Amavasya", …}`) or a fixed date (`{date: 2027-01-14, label: …}`).
  `adhika: true` marks a leap month.

Per panel: photo fills the left ~58%; the right ~42% (parchment, ṛtu-tinted) stacks
month title → quote → weekday header → lunar-range date grid → paksha legend.

## Swapping things

- **Photos:** replace `assets/images/NN.jpg` or point `photo:` at any path
  (relative to the YAML).
- **Fonts:** drop a TTF in `fonts/` and set the matching `theme.fonts.*` name
  (file names expected: `NotoSansDevanagari.ttf`, `NotoSerif.ttf`,
  `CormorantGaramond.ttf` — or edit `panchang/theme.py` if you rename them).
- **Dimensions / DPI:** edit `theme.page`.
- **Colours:** edit `theme.ritu`.

## Tests

```bash
python -m pytest -v
```
