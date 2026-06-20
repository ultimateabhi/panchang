# Panchang Desk Calendar Generator — Design

**Date:** 2026-06-20
**Status:** Approved (brainstorming) — ready for implementation plan

## 1. Goal

Build a small, reusable Python repository that generates the **design files** (a
multi-page **PDF** + **per-page PNGs at 300 DPI**) for a **Panchang (Vikram Samvat,
luni-solar) desk calendar** in the **"long desktop" tent format**.

This is **not** a Gregorian calendar. It is a Vikram Samvat pūrṇimānta panchang,
laid out one panel per lunar month plus a cover. A prior grid wall-calendar build
exists in `vs2083_calendar/`; we **reuse its data and lunar logic and its month
photos**, but produce a **fresh desktop-tent design** — not the grid look.

Printing/production is handled elsewhere. Our only job is correct artwork at the
right size.

## 2. Non-goals (YAGNI)

- **No astronomy in code.** Tithis, nakshatras, and month boundaries are *not*
  computed. They are read from a human-editable config and verified by hand. The
  generator only does data-mapping + layout + rendering.
- No interactive UI, no web server, no print/bleed/CMYK production handling.
- No automatic photo sourcing or download. Photos are local files referenced by the
  config (reused from `vs2083_calendar/images/`).
- **No logo.** The footer strip carries only the paksha legend.
- No support for amānta reckoning in the sample (the engine is reckoning-agnostic in
  that it just maps supplied dates, but the sample and labels assume pūrṇimānta).

## 3. Page format

- Each panel: **10 in × 3.5 in (254 mm × 88.9 mm), landscape** — the long desktop
  proportion.
- Export at **300 DPI** → each PNG is **3000 × 1050 px**.
- The tent binds along the **top** edge, so the topmost **~8 mm** strip is kept clear
  of important text/art (a configurable `top_safe_mm` token).

## 4. Page count — derived, never hard-coded

A Vikram Samvat year has **12 or 13 lunar months** (13 in a leap year, which adds an
adhika/extra month). The generator produces **one panel per lunar month present in
the config, plus one cover page**. Page count = `len(months) + 1`. For the sample
(VS 2083, a leap year) this is **13 + 1 = 14 pages**. Never assume a fixed count;
derive it from the config every time.

## 5. Layout per month panel

Right column holds the calendar; the photo gets the clean left. Quote sits **above**
the (slightly smaller) calendar table within the right column.

```
┌───────────────────────────────────────────────────────────┐  ← top ~8 mm clear (binding)
│  ┌─────────────────────────┐   MONTH TITLE BLOCK           │
│  │                         │   चैत्र  Chaitra · Vasanta      │
│  │                         │   4 Mar – 2 Apr 2026 · 30 days │
│  │      PHOTO (full)       │   ┌─ quote ──────────────────┐ │
│  │      left ~58%          │   │ "When stillness arises…" │ │
│  │                         │   │            — Sadhguru     │ │
│  │                         │   ├─ weekday header ─────────┤ │
│  │                         │   │ र सो मं बु गु शु श          │ │
│  │                         │   │ [ lunar-range date grid ]│ │
│  └─────────────────────────┘   └─ paksha legend ──────────┘ │
└───────────────────────────────────────────────────────────┘
```

- **Left ~58%** (`100 - calendar_pct`): the month photo, full-bleed, with a subtle
  right-edge feather/gradient into the parchment so the seam reads as premium, not
  hard. The photo is clean — no text overlaid.
- **Right ~42%** (`calendar_pct`, configurable), on a light **parchment** background
  tinted by the month's ṛtu palette, stacked top→bottom:
  1. **Month title block** — Devanagari name + romanized name + ṛtu label; a
     sub-line with the Gregorian span and day count. Adhika months show an
     "अधिक मास / leap" badge.
  2. **Quote + attribution** — the month's quote in an elegant serif, attribution
     in small caps beneath.
  3. **Weekday header** — Devanagari weekday initials (र सो मं बु गु शु श),
     accent-colored bar.
  4. **Lunar-range date grid** — see §6.
  5. **Footer strip** — a compact Krishna/Shukla paksha legend.
- **Vertical budget** (~80 mm usable after the top safe strip): title ~12 mm,
  quote ~16–18 mm, weekday header ~5 mm, grid ~40 mm (≈6.5 mm/row for 6 rows),
  footer ~6 mm. Tight but feasible. Grid row height **auto-scales** to the number of
  weeks so a 5-row or 6-row month both fit. This density is the one thing to eyeball
  on the first render; if too tight we widen `calendar_pct` or shrink the quote.

## 6. Date grid semantics (lunar-range + tithi)

The lunar month straddles two Gregorian months (e.g. Kārtika = 26 Oct – 23 Nov), so
the grid renders the **actual lunar month range**, not a Gregorian month:

- Rows are 7-column weeks (Sunday-first, matching the existing build's
  `र सो मं बु गु शु श`). The grid spans from the Sunday on/before `start` to the
  Saturday on/after `end`; days outside `[start, end]` render as muted "inactive"
  cells showing only the Gregorian date.
- Each **active** cell shows:
  - the **Devanagari tithi numeral** (prominent),
  - the **Gregorian day + month abbreviation** (small),
  - paksha shading: **Krishna** (waning, `start`→`amavasya`) uses the ṛtu *krishna*
    tint; **Shukla** (waxing, `amavasya+1`→`end`) uses the ṛtu *shukla* tint,
  - boundary badges: `कृ॰ प्रतिपदा` (Krishna 1) at start, `○ अमावस्या` at the new
    moon, `शु॰ प्रतिपदा` at Shukla 1, `● पूर्णिमा` at end,
  - **festival label** when present, in the ṛtu accent color (truncated to fit;
    marquee festivals like DIWALI / HOLI emphasized).
- Tithi math (reused from `vs2083_calendar/generate.py`):
  - Krishna paksha: `tithi = (d - start).days + 1` for `start ≤ d ≤ amavasya`.
  - Shukla paksha: `tithi = (d - amavasya).days` for `amavasya < d ≤ end`
    (so `end` = Shukla 15 = Pūrṇimā).
- **Festival keying**: a festival entry is matched by **tithi key** (`K8`, `S15`,
  `Amavasya`) or by **fixed Gregorian `date`** (e.g. Makar Sankranti 14 Jan 2027).
  Fixed-date wins if both would apply to a cell.

## 7. Cover panel

Same 10 × 3.5 in dimensions. Content entirely from config:

- Samvat title + year, Gregorian span, "pūrṇimānta" reckoning kicker, a short
  explanatory note (waning krishna → amāvāsyā, waxing shukla → pūrṇimā; adhika māsa),
  and a **compact index** of all months (number, Devanagari + roman name, Gregorian
  span, season; leap month starred). The index is generated by iterating the same
  `months:` list, so it stays correct for 12- or 13-month years.

## 8. Architecture

```
panchang_calendar/
  generate.py            # CLI entry: load config → render panels → PNG + PDF
  panchang/
    __init__.py
    config.py            # load + validate YAML; build the ordered page list (cover + months)
    panchang.py          # reckoning-agnostic lunar logic: map dates→tithi/paksha; resolve festivals per cell
    layout.py            # build per-panel HTML (month panels + cover) from theme + data
    render.py            # Playwright Chromium: panel HTML → 300 DPI PNG + per-panel PDF; merge via pypdf
    theme.py             # dimension tokens, ṛtu palette, font stacks, parchment styling
  fonts/                 # bundled fonts for offline-safe Devanagari + serif (see §10)
  config/
    vs2083.yaml          # sample, pre-filled from PANCHANG_VS2083_REFERENCE.md
  assets/
    images/01.jpg … 13.jpg   # copied from vs2083_calendar/images/
  out/                   # build output: calendar.pdf + pages/NN_<slug>.png
  README.md
  requirements.txt
```

### Module responsibilities (each independently understandable + testable)

- **`config.py`** — *what:* read the YAML, validate required fields, normalize dates,
  and emit a typed in-memory model (`Calendar` with `theme`, `cover`, `months[]`).
  *depends on:* `pyyaml`. *interface:* `load_config(path) -> Calendar`. Raises clear
  errors on missing/invalid fields (e.g. `amavasya` outside `[start, end]`).
- **`panchang.py`** — *what:* pure functions mapping a month's dates to per-day
  `(paksha, tithi, badge, festival_label)`; no rendering, no I/O. *depends on:* stdlib
  `datetime`. *interface:* `month_days(month) -> list[DayCell]`,
  `resolve_festival(month, date, paksha, tithi) -> str|None`. This is the testable
  core; lifted from the old `month_page` logic but decoupled from HTML.
- **`theme.py`** — *what:* turn theme tokens + a ṛtu key into concrete CSS values
  (accent/shukla/krishna colors, dimensions, font stacks). *depends on:* config model.
- **`layout.py`** — *what:* produce a complete HTML document string for one panel
  (cover or month) given the data model + theme. Pure string-building; no I/O.
  *interface:* `cover_html(cal) -> str`, `month_html(cal, month) -> str`.
- **`render.py`** — *what:* drive Playwright Chromium to turn each panel's HTML into
  a 300 DPI PNG (viewport 3000×1050, `device_scale_factor` from DPI) and a single-page
  PDF sized exactly 10×3.5 in; then merge the per-panel PDFs into `calendar.pdf` with
  `pypdf`. *depends on:* `playwright`, `pypdf`. *interface:*
  `render_all(panels, outdir) -> (pdf_path, [png_paths])`.
- **`generate.py`** — *what:* CLI glue. Flags: `--config`, `--outdir`, `--png-only`,
  `--pdf-only`, `--months N` (subset for quick preview). Orchestrates
  load → build HTML → render. Prints a per-page progress log.

## 9. Rendering pipeline (PDF + 300 DPI PNG)

1. `config.py` loads `vs2083.yaml` → `Calendar` model; page list = `[cover] + months`.
2. For each page, `layout.py` builds a standalone HTML doc (inline `<style>`, fonts
   referenced as bundled `file://` `@font-face`, photo embedded as base64 so
   the PDF is self-contained and rendering is order-independent).
3. `render.py` opens one Chromium page per panel:
   - **PNG**: set viewport `3000 × 1050`, `device_scale_factor = dpi/96` is *not*
     needed because we size the viewport in device pixels directly; CSS lays out in a
     10in×3.5in `@page`/container scaled to 3000×1050. Screenshot full panel → PNG.
   - **PDF**: `page.pdf(width="10in", height="3.5in", print_background=True,
     margin=0)` → one-page PDF per panel.
4. Merge per-panel PDFs in order via `pypdf` → `out/calendar.pdf`.
5. PNGs written to `out/pages/NN_<slug>.png` (`00_cover.png`, `01_chaitra.png`, …).

*(Exact viewport/scale mechanics — direct device-pixel viewport vs. CSS-inch container
+ `device_scale_factor` — to be settled during implementation by verifying a render is
crisp at 3000×1050; both are viable and the choice is a rendering detail, not a design
decision.)*

## 10. Fonts

Bundle offline-safe fonts in `fonts/` and reference via `@font-face` with `file://`
URLs so rendering never depends on network or system fonts:

- **Devanagari** (month names, tithi numerals, weekday initials, badges):
  Noto Sans Devanagari and/or Noto Serif Devanagari.
- **Latin serif** (titles, dates): Noto Serif.
- **Quote**: an elegant serif (e.g. Cormorant Garamond) — falls back to the bundled
  serif if absent.

Font family names are config tokens (`theme.fonts.*`) so they are swappable.

## 11. Config schema (YAML)

```yaml
calendar:
  samvat: 2083
  reckoning: purnimanta
  gregorian_span: "4 Mar 2026 – 23 Mar 2027"
  cover:
    title: "Vikram Samvat"
    subtitle: "Thirteen lunar months · 4 Mar 2026 – 23 Mar 2027 · Pūrṇimānta"
    note: "VS 2083 has a thirteenth month — adhika māsa (Adhika Jyeshtha). …"
theme:
  page: { width_in: 10, height_in: 3.5, dpi: 300, top_safe_mm: 8, calendar_pct: 42 }
  fonts:
    devanagari: "Noto Sans Devanagari"
    serif: "Noto Serif"
    quote: "Cormorant Garamond"
  ritu:
    vasanta:  { accent: "#4E8B3A", shukla: "#e8f2e2", krishna: "#d2e4c8" }
    grishma:  { accent: "#C8771B", shukla: "#f7ecda", krishna: "#f0dcc2" }
    varsha:   { accent: "#1F8A8A", shukla: "#ddf0f0", krishna: "#c8e2e2" }
    sharad:   { accent: "#C0561E", shukla: "#f9e8dd", krishna: "#f0d4c4" }
    hemanta:  { accent: "#5B4B9A", shukla: "#eae5f4", krishna: "#d9d2ea" }
    shishira: { accent: "#3F6B8C", shukla: "#e2ecf2", krishna: "#cddde8" }
months:
  - name_dev: "चैत्र"
    name_rom: "Chaitra"
    adhika: false
    ritu: vasanta
    season_label: "Vasanta (spring)"
    start: 2026-03-04         # Krishna 1 (day after previous Pūrṇimā)
    amavasya: 2026-03-18      # new moon
    end: 2026-04-02           # Pūrṇimā (= Shukla 15)
    photo: assets/images/01.jpg
    quote:
      text: "When stillness arises from intense alertness and awareness, your perception opens up in ways that you have never thought possible."
      attribution: "Sadhguru"
    festivals:
      - { tithi: "S1",  label: "Gudi Padwa · Ugadi" }
      - { tithi: "S9",  label: "Rāma Navamī" }
      - { tithi: "S15", label: "Hanumān Jayantī" }
  # … 12 more months (Adhika Jyeshtha carries adhika: true; Pausha includes a
  #   fixed-date festival: { date: 2027-01-14, label: "Makar Sankrānti" })
```

The sample `vs2083.yaml` is fully pre-filled from `PANCHANG_VS2083_REFERENCE.md` (all
13 months, boundaries, festivals, ṛtu colors, per-month Sadhguru quotes) so the repo
builds a complete calendar out of the box. **Editing the calendar = editing the YAML;
no code changes required.**

### Festival entry forms
- `{ tithi: "S15", label: "…" }` — keyed by paksha + tithi index (`K`/`S` + number).
- `{ tithi: "Amavasya", label: "…" }` — keyed to the new moon.
- `{ date: 2027-01-14, label: "…" }` — keyed to a fixed Gregorian date.

## 12. Validation rules (config.py)

- Required per month: `name_dev`, `name_rom`, `ritu`, `start`, `amavasya`, `end`,
  `photo`, `quote.text`. Missing → clear error naming the month index.
- `start ≤ amavasya ≤ end`; otherwise error.
- `ritu` must be a key present in `theme.ritu`.
- `photo` path must exist (error lists the missing path).
- `festivals[].tithi` must parse as `K<n>`/`S<n>`/`Amavasya`, or provide `date`.

## 13. Deliverables

- The generator (`generate.py` + `panchang/` package).
- The sample `config/vs2083.yaml` + the 13 month photos (copied from
  `vs2083_calendar/images/`).
- `requirements.txt` (`pyyaml`, `playwright`, `pypdf`) + a note to run
  `playwright install chromium`.
- Build output committed-or-gitignored under `out/`: `calendar.pdf` (14 pages) +
  `pages/*.png` (3000×1050).
- A short **README**: how to run; how the config maps to the layout; how to swap
  photos, fonts, and dimensions.

## 14. Dependencies & environment

- Python 3.10+ (3.10.8 present).
- `pyyaml` ✅ present · `pypdf` ✅ present · `playwright` ❌ to install
  (`pip install playwright && playwright install chromium`).
- The README documents the one-time `playwright install chromium` step.

## 15. Testing strategy

- **Unit (`panchang.py`)**: tithi/paksha mapping for a known month (e.g. Kārtika) —
  assert Krishna 1 at start, Amāvāsyā/Diwali at the new moon, Shukla 15/Pūrṇimā at end,
  fixed-date festival (Makar Sankranti) lands on the right cell.
- **Unit (`config.py`)**: invalid configs (missing field, `amavasya` out of range,
  unknown ṛtu, missing photo) raise clear errors; valid sample loads to 13 months.
- **Render smoke**: generate one panel → assert PNG is exactly 3000×1050 and the
  merged PDF has `len(months)+1` pages.
- **Visual check**: eyeball the first full render for grid density / quote fit /
  photo-parchment seam (per §5 note).

## 16. Open implementation detail (not blocking)

- Exact Playwright sizing mechanism for crisp 300 DPI (device-pixel viewport vs.
  inch-sized CSS container + `device_scale_factor`) — decided during implementation by
  verifying output crispness; does not affect the design.
