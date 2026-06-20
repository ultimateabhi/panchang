# Panchang Calendars — Vikram Samvat 2083 (Pūrṇimānta)

Code that generates **print-ready design files** for a Vikram Samvat (Indian luni-solar)
panchang calendar — **not** a Gregorian calendar. Everything covers **VS 2083**, a
13-month leap year (4 Mar 2026 – 23 Mar 2027, including the adhika month Adhika
Jyeshtha), in the **pūrṇimānta** (full-moon-ending) reckoning.

The repo holds **two independent generators** that share the same panchang data:

| Folder | Format | Look | Output |
|---|---|---|---|
| [`panchang_calendar/`](panchang_calendar/) | **Long-desktop tent**, 10 × 3.5 in, 300 DPI | Photo-left / parchment calendar-right, quote above a lunar-range tithi grid | Multi-page **PDF** + per-page **PNGs** |
| [`vs2083_calendar/`](vs2083_calendar/) | Wall calendar (grid) | Classic month grid | **HTML** + **PDF** |

Both are config/data-driven and do **no astronomy** — tithis, month boundaries, and
festivals are supplied by hand (and verified) from the canonical reference, then the
code only does layout + rendering.

## Which one do I want?

- **Desk calendar** (the newer, config-driven build) → **[`panchang_calendar/`](panchang_calendar/README.md)**.
  Edit `panchang_calendar/config/vs2083.yaml` and run `python generate.py`. See that
  folder's README for install (it needs Playwright/Chromium + bundled fonts), run
  commands, and how the YAML maps to the layout.
- **Wall calendar** (the original grid build) → **[`vs2083_calendar/`](vs2083_calendar/README.md)**.

## Repository layout

```
.
├── panchang_calendar/            # desk-calendar generator (config-driven; PDF + PNGs)
│   ├── generate.py               #   CLI entry point
│   ├── panchang/                 #   package: models, config, reckoning, theme, layout, render
│   ├── config/vs2083.yaml        #   the hand-editable calendar (edit this, not the code)
│   ├── assets/images/01..13.jpg  #   one photo per month
│   ├── fonts/                    #   bundled Devanagari + serif fonts (fetch once)
│   ├── tests/                    #   pytest suite
│   └── README.md                 #   ← full usage docs for the desk calendar
│
├── vs2083_calendar/              # original wall-calendar generator (HTML + PDF)
│   ├── generate.py
│   └── README.md                 #   ← usage docs for the wall calendar
│
├── PANCHANG_VS2083_REFERENCE.md  # canonical panchang data: reckoning, month
│                                 #   boundaries, festivals (by tithi), season colours,
│                                 #   per-month quotes — the source of truth for both builds
├── Long-desktop_design.png       # target visual design for the desk calendar
├── prompt.txt                    # original project brief
└── docs/superpowers/             # design spec + implementation plan for the desk build
    ├── specs/2026-06-20-panchang-desk-calendar-design.md
    └── plans/2026-06-20-panchang-desk-calendar.md
```

## Panchang reckoning (pūrṇimānta) in one paragraph

Each lunar month runs **full moon → full moon**. The waning fortnight (**Krishna
paksha**) goes from the day after the previous Pūrṇimā down to **Amāvāsyā** (new
moon); the waxing fortnight (**Shukla paksha**) runs from there up to **Pūrṇimā**,
which ends the month (Shukla 15). A consequence: Krishna-paksha festivals sit in the
month named after the *following* Pūrṇimā — e.g. Diwali falls on Kārtika Amāvāsyā and
Mahā Shivarātri in Phālguna. Full details, month boundaries, festivals, and the
per-month season (ṛtu) accent colours are in
[`PANCHANG_VS2083_REFERENCE.md`](PANCHANG_VS2083_REFERENCE.md).

> Festival placements are by tithi index and may differ ±1 day from a live local
> panchang; for ritual-critical dates, cross-check a local panchang.

## Editing the calendar

To change months, dates, festivals, photos, quotes, colours, fonts, or page
dimensions for the **desk** build, edit `panchang_calendar/config/vs2083.yaml` — no
code changes are required. For the **wall** build, the data lives in
`vs2083_calendar/generate.py`.
