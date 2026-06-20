# Panchang Desk Calendar Generator — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a config-driven Python generator that emits a multi-page PDF + per-page 300 DPI PNGs for a Vikram Samvat pūrṇimānta desk calendar in the 10×3.5 in long-desktop tent format.

**Architecture:** A small `panchang/` package with a clean dependency DAG: `models` (dataclasses) ← `config` (YAML→model + validation), `panchang` (date→tithi/paksha/festival logic), `theme` (CSS tokens), `layout` (model→HTML per panel), `render` (Playwright Chromium → PNG + PDF). `generate.py` is the CLI glue. No astronomy in code — all panchang data comes from a hand-editable YAML config.

**Tech Stack:** Python 3.10+, PyYAML, Playwright (Chromium), pypdf, pytest. Bundled Noto Sans Devanagari / Noto Serif / Cormorant Garamond fonts. HTML/CSS rendered headless to PNG (device-scale screenshot) and vector PDF.

## Global Constraints

- **Page size:** every panel is exactly **10 in × 3.5 in landscape**; PNGs are exactly **3000 × 1050 px** (300 DPI). CSS coordinate space is **960 × 336 px** (96 px/in); PNG via `device_scale_factor = dpi/96 = 3.125`; PDF via `page.pdf(width="10in", height="3.5in")`.
- **Top safe strip:** keep the topmost `top_safe_mm` (default 8 mm) clear of important text/art (tent binding edge).
- **Page count is derived, never hard-coded:** `len(months) + 1` (cover + one panel per lunar month). Sample VS 2083 = 14 pages.
- **No astronomy in code.** Tithis/month boundaries are read from config only.
- **No logo.** Footer strip carries only the Krishna/Shukla paksha legend.
- **Reckoning (pūrṇimānta):** Krishna paksha = `start`→`amavasya` (`tithi = (d-start).days+1`); Shukla paksha = `amavasya+1`→`end` (`tithi = (d-amavasya).days`); `end` = Shukla 15 = Pūrṇimā.
- **Editing the calendar = editing the YAML.** No code change should be needed to swap photos, quotes, festivals, dimensions, colours, or fonts.
- **Project root for all paths below:** `panchang_calendar/` (a new sibling of the existing `vs2083_calendar/`). **All test/run commands assume `cwd = panchang_calendar/`.**
- **Photo paths in the YAML are relative to the YAML file's own directory.**
- When implementing the Playwright render step, **verify the Playwright sync API via context7** (`browser.new_page` viewport + `device_scale_factor`, `page.pdf`, `page.screenshot` clip) before writing code, and note that you did so.

---

## File Structure

```
panchang_calendar/
  generate.py                 # CLI entry
  panchang/
    __init__.py
    models.py                 # dataclasses (Calendar, MonthData, Theme, …)
    config.py                 # load_config(path) -> Calendar  (+ validation)
    panchang.py               # date→tithi/paksha/festival logic; grid builder
    theme.py                  # page_px, device_scale, font_face_css
    layout.py                 # month_html(cal, m), cover_html(cal)
    render.py                 # build_panels, render_all → PNG + merged PDF
  fonts/
    fetch_fonts.sh            # one-time font download
    NotoSansDevanagari.ttf    # (fetched)
    NotoSerif.ttf             # (fetched)
    CormorantGaramond.ttf     # (fetched)
  config/
    vs2083.yaml               # sample, pre-filled from PANCHANG_VS2083_REFERENCE.md
  assets/
    images/01.jpg … 13.jpg    # copied from vs2083_calendar/images/
  tests/
    __init__.py
    test_panchang.py
    test_config.py
    test_render.py
  out/                        # build output (gitignored): calendar.pdf + pages/*.png
  requirements.txt
  .gitignore
  README.md
```

---

### Task 1: Project scaffold, dependencies, assets & fonts

**Files:**
- Create: `panchang_calendar/panchang/__init__.py` (empty)
- Create: `panchang_calendar/tests/__init__.py` (empty)
- Create: `panchang_calendar/requirements.txt`
- Create: `panchang_calendar/.gitignore`
- Create: `panchang_calendar/fonts/fetch_fonts.sh`
- Create: `panchang_calendar/assets/images/01.jpg … 13.jpg` (copied)
- Test: `panchang_calendar/tests/test_scaffold.py`

**Interfaces:**
- Consumes: nothing.
- Produces: importable `panchang` package; `fonts/*.ttf`; `assets/images/NN.jpg`. Later tasks rely on these paths existing.

- [ ] **Step 1: Create directories and empty package files**

```bash
cd /Users/abhiag/Downloads/panchang
mkdir -p panchang_calendar/panchang panchang_calendar/tests \
         panchang_calendar/fonts panchang_calendar/config \
         panchang_calendar/assets/images panchang_calendar/out
: > panchang_calendar/panchang/__init__.py
: > panchang_calendar/tests/__init__.py
```

- [ ] **Step 2: Write `requirements.txt`**

```
pyyaml>=6.0
playwright>=1.40
pypdf>=4.0
pytest>=7.0
```

- [ ] **Step 3: Write `.gitignore`**

```
out/
__pycache__/
*.pyc
_panels/
```

- [ ] **Step 4: Copy the 13 month photos**

```bash
cp /Users/abhiag/Downloads/panchang/vs2083_calendar/images/*.jpg \
   /Users/abhiag/Downloads/panchang/panchang_calendar/assets/images/
ls panchang_calendar/assets/images/   # expect 01.jpg … 13.jpg
```

- [ ] **Step 5: Write `fonts/fetch_fonts.sh`**

```bash
#!/usr/bin/env bash
# One-time download of bundled fonts (OFL). Run once; the .ttf files are committed.
set -euo pipefail
cd "$(dirname "$0")"
base="https://github.com/google/fonts/raw/main/ofl"
curl -fL -o NotoSansDevanagari.ttf "$base/notosansdevanagari/NotoSansDevanagari%5Bwdth%2Cwght%5D.ttf"
curl -fL -o NotoSerif.ttf          "$base/notoserif/NotoSerif%5Bwdth%2Cwght%5D.ttf"
curl -fL -o CormorantGaramond.ttf  "$base/cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf"
echo "Fonts downloaded:"; ls -la *.ttf
```

- [ ] **Step 6: Install dependencies and fetch fonts**

```bash
cd /Users/abhiag/Downloads/panchang/panchang_calendar
pip install -r requirements.txt
python -m playwright install chromium
bash fonts/fetch_fonts.sh
```
Expected: three `*.ttf` files listed, each non-zero size; Chromium installs without error.

- [ ] **Step 7: Write the scaffold smoke test** — `tests/test_scaffold.py`

```python
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parent.parent


def test_package_imports():
    assert importlib.import_module("panchang") is not None


def test_assets_present():
    imgs = sorted((ROOT / "assets" / "images").glob("*.jpg"))
    assert len(imgs) == 13, f"expected 13 month photos, found {len(imgs)}"


def test_fonts_present():
    for name in ("NotoSansDevanagari.ttf", "NotoSerif.ttf", "CormorantGaramond.ttf"):
        f = ROOT / "fonts" / name
        assert f.exists() and f.stat().st_size > 0, f"missing/empty font: {name}"
```

- [ ] **Step 8: Run the test**

Run: `cd /Users/abhiag/Downloads/panchang/panchang_calendar && python -m pytest tests/test_scaffold.py -v`
Expected: 3 passed.

- [ ] **Step 9: Commit**

```bash
cd /Users/abhiag/Downloads/panchang
git add panchang_calendar/panchang/__init__.py panchang_calendar/tests/__init__.py \
        panchang_calendar/tests/test_scaffold.py panchang_calendar/requirements.txt \
        panchang_calendar/.gitignore panchang_calendar/fonts/fetch_fonts.sh \
        panchang_calendar/fonts/*.ttf panchang_calendar/assets/images/*.jpg
git commit -m "scaffold: panchang_calendar package, deps, fonts, month photos"
```

---

### Task 2: Data model (`models.py`)

**Files:**
- Create: `panchang_calendar/panchang/models.py`
- Test: `panchang_calendar/tests/test_models.py`

**Interfaces:**
- Consumes: nothing (stdlib `dataclasses`, `datetime`).
- Produces: dataclasses used everywhere downstream — `Quote(text, attribution)`, `Festival(label, tithi=None, date=None)`, `MonthData(index, name_dev, name_rom, ritu, season_label, start, amavasya, end, photo, quote, festivals, adhika)`, `RituPalette(accent, shukla, krishna)`, `PageSpec(width_in, height_in, dpi, top_safe_mm, calendar_pct)`, `Fonts(devanagari, serif, quote)`, `Theme(page, fonts, ritu)`, `Cover(title, subtitle, note)`, `Calendar(samvat, reckoning, gregorian_span, cover, theme, months)` with `.page_count`.

- [ ] **Step 1: Write the failing test** — `tests/test_models.py`

```python
from datetime import date
from panchang.models import (Calendar, Cover, Festival, Fonts, MonthData,
                             PageSpec, Quote, RituPalette, Theme)


def _calendar(n_months):
    page = PageSpec(width_in=10, height_in=3.5, dpi=300, top_safe_mm=8, calendar_pct=42)
    theme = Theme(page=page, fonts=Fonts("D", "S", "Q"),
                  ritu={"vasanta": RituPalette("#1", "#2", "#3")})
    months = [MonthData(index=i + 1, name_dev="x", name_rom="X", ritu="vasanta",
                        season_label="", start=date(2026, 3, 4),
                        amavasya=date(2026, 3, 18), end=date(2026, 4, 2),
                        photo="p.jpg", quote=Quote("q", "a"),
                        festivals=[Festival("F", tithi="S15")])
              for i in range(n_months)]
    return Calendar(samvat=2083, reckoning="purnimanta", gregorian_span="span",
                    cover=Cover("T", "sub", "note"), theme=theme, months=months)


def test_page_count_is_months_plus_cover():
    assert _calendar(13).page_count == 14
    assert _calendar(12).page_count == 13


def test_festival_optional_fields_default_none():
    f = Festival("DIWALI", tithi="Amavasya")
    assert f.date is None and f.tithi == "Amavasya"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/abhiag/Downloads/panchang/panchang_calendar && python -m pytest tests/test_models.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'panchang.models'`.

- [ ] **Step 3: Write `panchang/models.py`**

```python
"""Typed in-memory data model for the panchang calendar."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date


@dataclass
class Quote:
    text: str
    attribution: str = ""


@dataclass
class Festival:
    label: str
    tithi: str | None = None        # "K8" / "S15" / "Amavasya"
    date: date | None = None        # fixed Gregorian date (wins over tithi)


@dataclass
class MonthData:
    index: int                      # 1-based position in the year
    name_dev: str
    name_rom: str
    ritu: str
    season_label: str
    start: date                     # Krishna 1 (day after previous Pūrṇimā)
    amavasya: date                  # new moon
    end: date                       # Pūrṇimā (= Shukla 15)
    photo: str                      # absolute path after config resolves it
    quote: Quote
    festivals: list[Festival] = field(default_factory=list)
    adhika: bool = False


@dataclass
class RituPalette:
    accent: str
    shukla: str
    krishna: str


@dataclass
class PageSpec:
    width_in: float
    height_in: float
    dpi: int
    top_safe_mm: float
    calendar_pct: float


@dataclass
class Fonts:
    devanagari: str
    serif: str
    quote: str


@dataclass
class Theme:
    page: PageSpec
    fonts: Fonts
    ritu: dict[str, RituPalette]


@dataclass
class Cover:
    title: str
    subtitle: str
    note: str


@dataclass
class Calendar:
    samvat: int
    reckoning: str
    gregorian_span: str
    cover: Cover
    theme: Theme
    months: list[MonthData]

    @property
    def page_count(self) -> int:
        return len(self.months) + 1
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/abhiag/Downloads/panchang/panchang_calendar && python -m pytest tests/test_models.py -v`
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/abhiag/Downloads/panchang
git add panchang_calendar/panchang/models.py panchang_calendar/tests/test_models.py
git commit -m "feat: data model dataclasses for calendar"
```

---

### Task 3: Reckoning logic (`panchang.py`)

**Files:**
- Create: `panchang_calendar/panchang/panchang.py`
- Test: `panchang_calendar/tests/test_panchang.py`

**Interfaces:**
- Consumes: `MonthData` from `panchang.models`.
- Produces: `WEEKDAYS_DEV` (list, Sunday-first), `deva(n) -> str`, `greg_label(date) -> str`, `DayCell(date, in_month, paksha, tithi, badge, festival, is_amavasya, is_purnima)`, `tithi_for(month, d) -> (paksha|None, tithi|None)`, `resolve_festival(month, d, paksha, tithi) -> str|None`, `day_cell(month, d) -> DayCell`, `month_grid(month) -> list[list[DayCell]]`, `krishna_length(month) -> int`.

- [ ] **Step 1: Write the failing test** — `tests/test_panchang.py`

```python
from datetime import date
from panchang.models import Festival, MonthData, Quote
from panchang import panchang as P


def kartika():
    # VS 2083 Kārtika: 26 Oct → (8 Nov amāvāsyā) → 23 Nov 2026
    return MonthData(index=9, name_dev="कार्तिक", name_rom="Kartika", ritu="hemanta",
                     season_label="", start=date(2026, 10, 26),
                     amavasya=date(2026, 11, 8), end=date(2026, 11, 23),
                     photo="p", quote=Quote("q"),
                     festivals=[Festival("Dhanteras", tithi="K13"),
                                Festival("DIWALI", tithi="Amavasya"),
                                Festival("Kārtik Pūrṇimā", tithi="S15")])


def pausha():
    return MonthData(index=11, name_dev="पौष", name_rom="Pausha", ritu="shishira",
                     season_label="", start=date(2026, 12, 24),
                     amavasya=date(2027, 1, 7), end=date(2027, 1, 22),
                     photo="p", quote=Quote("q"),
                     festivals=[Festival("Makar Sankrānti", date=date(2027, 1, 14)),
                                Festival("Pausha Pūrṇimā", tithi="S15")])


def test_tithi_boundaries():
    m = kartika()
    assert P.tithi_for(m, date(2026, 10, 26)) == ("K", 1)      # Krishna 1 at start
    assert P.tithi_for(m, date(2026, 11, 8)) == ("K", 14)      # amāvāsyā
    assert P.tithi_for(m, date(2026, 11, 9)) == ("S", 1)       # Shukla 1
    assert P.tithi_for(m, date(2026, 11, 23)) == ("S", 15)     # Pūrṇimā
    assert P.tithi_for(m, date(2026, 12, 1)) == (None, None)   # outside


def test_festival_by_tithi_and_amavasya():
    m = kartika()
    assert P.resolve_festival(m, date(2026, 11, 8), "K", 14) == "DIWALI"
    assert P.resolve_festival(m, date(2026, 11, 23), "S", 15) == "Kārtik Pūrṇimā"
    assert P.resolve_festival(m, date(2026, 11, 10), "S", 2) is None


def test_fixed_date_festival_wins():
    m = pausha()
    assert P.resolve_festival(m, date(2027, 1, 14), "S", 7) == "Makar Sankrānti"


def test_badges_and_flags():
    c = P.day_cell(kartika(), date(2026, 11, 8))
    assert c.is_amavasya and "अमावस्या" in c.badge
    assert P.day_cell(kartika(), date(2026, 11, 23)).is_purnima


def test_deva_numerals():
    assert P.deva(15) == "१५"
    assert P.deva(1) == "१"


def test_grid_is_sunday_first_whole_weeks():
    weeks = P.month_grid(kartika())
    flat = [c for w in weeks for c in w]
    assert all(len(w) == 7 for w in weeks)
    assert flat[0].date.weekday() == 6          # Python: Sunday == 6
    assert any(c.in_month and c.date == date(2026, 10, 26) for c in flat)
    assert any(c.in_month and c.date == date(2026, 11, 23) for c in flat)


def test_krishna_length():
    assert P.krishna_length(kartika()) == 14     # 26 Oct → 8 Nov inclusive
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/abhiag/Downloads/panchang/panchang_calendar && python -m pytest tests/test_panchang.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'panchang.panchang'` (or AttributeError).

- [ ] **Step 3: Write `panchang/panchang.py`**

```python
"""Reckoning logic: map a lunar month's supplied dates to per-day
tithi/paksha/badge/festival cells. No astronomy — dates come from config."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta

from .models import MonthData

# Sunday-first weekday initials (Devanagari): र सो मं बु गु शु श
WEEKDAYS_DEV = ["र", "सो", "मं", "बु", "गु", "शु", "श"]

_DEV_DIGITS = {"0": "०", "1": "१", "2": "२", "3": "३", "4": "४",
               "5": "५", "6": "६", "7": "७", "8": "८", "9": "९"}
_MON_ABBR = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def deva(n: int) -> str:
    """Render an integer in Devanagari numerals."""
    return "".join(_DEV_DIGITS[c] for c in str(n))


def greg_label(d: date) -> str:
    """Short Gregorian label, e.g. '4 Mar' (adds year apostrophe on Jan 1)."""
    s = f"{d.day} {_MON_ABBR[d.month]}"
    if d.month == 1 and d.day == 1:
        s += f" '{str(d.year)[2:]}"
    return s


@dataclass
class DayCell:
    date: date
    in_month: bool
    paksha: str | None = None       # "K" / "S"
    tithi: int | None = None        # 1..15
    badge: str | None = None        # boundary label (Devanagari)
    festival: str | None = None
    is_amavasya: bool = False
    is_purnima: bool = False


def tithi_for(month: MonthData, d: date) -> tuple[str | None, int | None]:
    """(paksha, tithi) for a date inside the month, else (None, None)."""
    if d < month.start or d > month.end:
        return None, None
    if d <= month.amavasya:
        return "K", (d - month.start).days + 1
    return "S", (d - month.amavasya).days


def resolve_festival(month: MonthData, d: date,
                     paksha: str | None, tithi: int | None) -> str | None:
    """Festival label for a cell. Fixed Gregorian date wins; then tithi/amāvāsyā key."""
    for f in month.festivals:
        if f.date is not None and f.date == d:
            return f.label
    if d == month.amavasya:
        key = "Amavasya"
    elif paksha is not None and tithi is not None:
        key = f"{paksha}{tithi}"
    else:
        return None
    for f in month.festivals:
        if f.tithi and f.tithi.lower() == key.lower():
            return f.label
    return None


def _badge(month: MonthData, d: date) -> str | None:
    if d == month.start:
        return "कृ॰ प्रतिपदा"
    if d == month.amavasya:
        return "○ अमावस्या"
    if d == month.amavasya + timedelta(days=1):
        return "शु॰ प्रतिपदा"
    if d == month.end:
        return "● पूर्णिमा"
    return None


def day_cell(month: MonthData, d: date) -> DayCell:
    if not (month.start <= d <= month.end):
        return DayCell(date=d, in_month=False)
    paksha, tithi = tithi_for(month, d)
    return DayCell(
        date=d, in_month=True, paksha=paksha, tithi=tithi,
        badge=_badge(month, d),
        festival=resolve_festival(month, d, paksha, tithi),
        is_amavasya=(d == month.amavasya),
        is_purnima=(d == month.end),
    )


def month_grid(month: MonthData) -> list[list[DayCell]]:
    """Weeks (Sunday-first) spanning the lunar month range, padded to whole weeks."""
    gstart = month.start - timedelta(days=(month.start.weekday() + 1) % 7)
    gend = month.end + timedelta(days=(5 - month.end.weekday()) % 7)
    weeks: list[list[DayCell]] = []
    week: list[DayCell] = []
    d = gstart
    while d <= gend:
        week.append(day_cell(month, d))
        if len(week) == 7:
            weeks.append(week)
            week = []
        d += timedelta(days=1)
    if week:
        weeks.append(week)
    return weeks


def krishna_length(month: MonthData) -> int:
    return (month.amavasya - month.start).days + 1
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/abhiag/Downloads/panchang/panchang_calendar && python -m pytest tests/test_panchang.py -v`
Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/abhiag/Downloads/panchang
git add panchang_calendar/panchang/panchang.py panchang_calendar/tests/test_panchang.py
git commit -m "feat: pūrṇimānta reckoning logic (tithi/paksha/festival/grid)"
```

---

### Task 4: Config loader & validation (`config.py`)

**Files:**
- Create: `panchang_calendar/panchang/config.py`
- Test: `panchang_calendar/tests/test_config.py`

**Interfaces:**
- Consumes: all dataclasses from `panchang.models`; `pyyaml`.
- Produces: `load_config(path) -> Calendar` and `class ConfigError(ValueError)`. Resolves each month's `photo` to an **absolute path** (relative to the YAML file's directory) and validates it exists.

- [ ] **Step 1: Write the failing test** — `tests/test_config.py`

```python
import textwrap
from pathlib import Path
import pytest
from panchang.config import load_config, ConfigError

VALID = textwrap.dedent("""\
calendar:
  samvat: 2083
  reckoning: purnimanta
  gregorian_span: "span"
  cover: {title: "Vikram Samvat", subtitle: "s", note: "n"}
theme:
  page: {width_in: 10, height_in: 3.5, dpi: 300, top_safe_mm: 8, calendar_pct: 42}
  fonts: {devanagari: "Noto Sans Devanagari", serif: "Noto Serif", quote: "Cormorant Garamond"}
  ritu:
    vasanta: {accent: "#4E8B3A", shukla: "#e8f2e2", krishna: "#d2e4c8"}
months:
  - name_dev: "चैत्र"
    name_rom: "Chaitra"
    ritu: vasanta
    season_label: "Vasanta (spring)"
    start: 2026-03-04
    amavasya: 2026-03-18
    end: 2026-04-02
    photo: photo.jpg
    quote: {text: "Q", attribution: "Sadhguru"}
    festivals:
      - {tithi: "S1", label: "Gudi Padwa"}
      - {date: 2026-03-20, label: "Fixed"}
""")


def _write(tmp_path, body):
    (tmp_path / "photo.jpg").write_bytes(b"\xff\xd8\xff")   # dummy jpeg bytes
    p = tmp_path / "c.yaml"
    p.write_text(body, encoding="utf-8")
    return p


def test_loads_valid_config(tmp_path):
    cal = load_config(_write(tmp_path, VALID))
    assert cal.samvat == 2083
    assert cal.page_count == 2
    m = cal.months[0]
    assert m.name_rom == "Chaitra" and m.index == 1
    assert m.festivals[0].tithi == "S1"
    assert m.photo.endswith("photo.jpg") and Path(m.photo).is_absolute()


def test_missing_required_field(tmp_path):
    bad = VALID.replace('    name_rom: "Chaitra"\n', "")
    with pytest.raises(ConfigError, match="name_rom"):
        load_config(_write(tmp_path, bad))


def test_amavasya_out_of_range(tmp_path):
    bad = VALID.replace("amavasya: 2026-03-18", "amavasya: 2026-04-10")
    with pytest.raises(ConfigError, match="amavasya"):
        load_config(_write(tmp_path, bad))


def test_unknown_ritu(tmp_path):
    bad = VALID.replace("ritu: vasanta", "ritu: monsoon")
    with pytest.raises(ConfigError, match="ritu"):
        load_config(_write(tmp_path, bad))


def test_missing_photo(tmp_path):
    p = tmp_path / "c.yaml"
    p.write_text(VALID, encoding="utf-8")          # note: no photo.jpg written
    with pytest.raises(ConfigError, match="photo"):
        load_config(p)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/abhiag/Downloads/panchang/panchang_calendar && python -m pytest tests/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'panchang.config'`.

- [ ] **Step 3: Write `panchang/config.py`**

```python
"""Load and validate the YAML calendar config into the typed model."""
from __future__ import annotations
from datetime import date, datetime
from pathlib import Path
import yaml

from .models import (Calendar, Cover, Festival, Fonts, MonthData,
                     PageSpec, Quote, RituPalette, Theme)


class ConfigError(ValueError):
    """Raised on any invalid or incomplete config."""


def _require(d: dict, key: str, where: str):
    if not isinstance(d, dict) or key not in d or d[key] in (None, ""):
        raise ConfigError(f"{where}: missing required field '{key}'")
    return d[key]


def _as_date(v, where) -> date:
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    raise ConfigError(f"{where}: expected a date (YYYY-MM-DD), got {v!r}")


def load_config(path) -> Calendar:
    path = Path(path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ConfigError("config: top level must be a mapping")
    base = path.parent

    cal_raw = _require(raw, "calendar", "config")
    theme = _build_theme(_require(raw, "theme", "config"))

    months_raw = _require(raw, "months", "config")
    if not isinstance(months_raw, list) or not months_raw:
        raise ConfigError("config: 'months' must be a non-empty list")
    months = [_build_month(m, i + 1, theme, base) for i, m in enumerate(months_raw)]

    cov = _require(cal_raw, "cover", "calendar.cover")
    cover = Cover(title=_require(cov, "title", "cover"),
                  subtitle=cov.get("subtitle", ""), note=cov.get("note", ""))

    return Calendar(
        samvat=_require(cal_raw, "samvat", "calendar"),
        reckoning=cal_raw.get("reckoning", "purnimanta"),
        gregorian_span=cal_raw.get("gregorian_span", ""),
        cover=cover, theme=theme, months=months,
    )


def _build_theme(t: dict) -> Theme:
    p = _require(t, "page", "theme")
    page = PageSpec(
        width_in=float(p.get("width_in", 10)),
        height_in=float(p.get("height_in", 3.5)),
        dpi=int(p.get("dpi", 300)),
        top_safe_mm=float(p.get("top_safe_mm", 8)),
        calendar_pct=float(p.get("calendar_pct", 42)),
    )
    f = t.get("fonts", {}) or {}
    fonts = Fonts(devanagari=f.get("devanagari", "Noto Sans Devanagari"),
                  serif=f.get("serif", "Noto Serif"),
                  quote=f.get("quote", "Cormorant Garamond"))
    ritu_raw = _require(t, "ritu", "theme")
    ritu = {k: RituPalette(accent=_require(v, "accent", f"theme.ritu.{k}"),
                           shukla=_require(v, "shukla", f"theme.ritu.{k}"),
                           krishna=_require(v, "krishna", f"theme.ritu.{k}"))
            for k, v in ritu_raw.items()}
    return Theme(page=page, fonts=fonts, ritu=ritu)


def _build_month(m: dict, index: int, theme: Theme, base: Path) -> MonthData:
    where = f"months[{index}] ({m.get('name_rom', '?') if isinstance(m, dict) else '?'})"
    start = _as_date(_require(m, "start", where), f"{where}.start")
    amav = _as_date(_require(m, "amavasya", where), f"{where}.amavasya")
    end = _as_date(_require(m, "end", where), f"{where}.end")
    if not (start <= amav <= end):
        raise ConfigError(f"{where}: require start <= amavasya <= end "
                          f"(got {start}, {amav}, {end})")
    ritu = _require(m, "ritu", where)
    if ritu not in theme.ritu:
        raise ConfigError(f"{where}: unknown ritu '{ritu}' "
                          f"(known: {', '.join(theme.ritu)})")
    photo_rel = _require(m, "photo", where)
    photo_abs = (base / photo_rel).resolve()
    if not photo_abs.exists():
        raise ConfigError(f"{where}: photo not found: {photo_abs}")
    q = _require(m, "quote", where)
    quote = Quote(text=_require(q, "text", f"{where}.quote"),
                  attribution=q.get("attribution", ""))
    festivals = [_build_festival(fe, f"{where}.festivals[{i}]")
                 for i, fe in enumerate(m.get("festivals", []) or [])]
    return MonthData(
        index=index, name_dev=_require(m, "name_dev", where),
        name_rom=_require(m, "name_rom", where), ritu=ritu,
        season_label=m.get("season_label", ""),
        start=start, amavasya=amav, end=end, photo=str(photo_abs),
        quote=quote, festivals=festivals, adhika=bool(m.get("adhika", False)),
    )


def _build_festival(fe: dict, where: str) -> Festival:
    label = _require(fe, "label", where)
    if "date" in fe:
        return Festival(label=label, date=_as_date(fe["date"], f"{where}.date"))
    tithi = str(_require(fe, "tithi", where))
    ok = tithi.lower() == "amavasya" or (tithi[0] in "KS" and tithi[1:].isdigit())
    if not ok:
        raise ConfigError(f"{where}: tithi must be 'K<n>'/'S<n>'/'Amavasya', got {tithi!r}")
    return Festival(label=label, tithi=tithi)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/abhiag/Downloads/panchang/panchang_calendar && python -m pytest tests/test_config.py -v`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/abhiag/Downloads/panchang
git add panchang_calendar/panchang/config.py panchang_calendar/tests/test_config.py
git commit -m "feat: YAML config loader with validation"
```

---

### Task 5: Sample config (`config/vs2083.yaml`)

**Files:**
- Create: `panchang_calendar/config/vs2083.yaml`
- Test: `panchang_calendar/tests/test_sample_config.py`

**Interfaces:**
- Consumes: `load_config` (Task 4); month photos at `assets/images/NN.jpg` (Task 1).
- Produces: the canonical pre-filled config; later tasks render from it. Photo paths are written relative to the YAML file: `../assets/images/NN.jpg`.

- [ ] **Step 1: Write the failing test** — `tests/test_sample_config.py`

```python
from pathlib import Path
from datetime import date
from panchang.config import load_config

CFG = Path(__file__).resolve().parent.parent / "config" / "vs2083.yaml"


def test_sample_loads_with_13_months():
    cal = load_config(CFG)
    assert cal.samvat == 2083
    assert len(cal.months) == 13
    assert cal.page_count == 14


def test_adhika_month_flagged():
    cal = load_config(CFG)
    adhika = [m for m in cal.months if m.adhika]
    assert len(adhika) == 1 and adhika[0].name_rom == "Adhika Jyeshtha"


def test_key_festivals_present():
    cal = load_config(CFG)
    kartika = next(m for m in cal.months if m.name_rom == "Kartika")
    labels = {f.label for f in kartika.festivals}
    assert "DIWALI" in labels
    pausha = next(m for m in cal.months if m.name_rom == "Pausha")
    assert any(f.date == date(2027, 1, 14) for f in pausha.festivals)


def test_all_photos_resolve():
    cal = load_config(CFG)            # load_config raises if any photo is missing
    assert all(Path(m.photo).exists() for m in cal.months)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/abhiag/Downloads/panchang/panchang_calendar && python -m pytest tests/test_sample_config.py -v`
Expected: FAIL (file not found / load error).

- [ ] **Step 3: Write `config/vs2083.yaml`**

```yaml
# Vikram Samvat 2083 — Pūrṇimānta desk calendar (13-month leap year).
# Edit this file to change the calendar; no code changes required.
# Dates are Gregorian (YYYY-MM-DD). Photo paths are relative to THIS file.
calendar:
  samvat: 2083
  reckoning: purnimanta
  gregorian_span: "4 Mar 2026 – 23 Mar 2027"
  cover:
    title: "Vikram Samvat"
    subtitle: "Thirteen lunar months · 4 Mar 2026 – 23 Mar 2027 · Pūrṇimānta"
    note: >-
      VS 2083 has a thirteenth month — adhika māsa (Adhika Jyeshtha). In the
      pūrṇimānta system each month runs full moon → full moon: waning krishna
      (१ → ○ अमावस्या), then waxing shukla (१ → १५, ● पूर्णिमा, month-end).
      Devanagari numerals mark the tithi; small text marks the Gregorian date.

theme:
  page: {width_in: 10, height_in: 3.5, dpi: 300, top_safe_mm: 8, calendar_pct: 42}
  fonts:
    devanagari: "Noto Sans Devanagari"
    serif: "Noto Serif"
    quote: "Cormorant Garamond"
  ritu:
    vasanta:  {accent: "#4E8B3A", shukla: "#e8f2e2", krishna: "#d2e4c8"}
    grishma:  {accent: "#C8771B", shukla: "#f7ecda", krishna: "#f0dcc2"}
    varsha:   {accent: "#1F8A8A", shukla: "#ddf0f0", krishna: "#c8e2e2"}
    sharad:   {accent: "#C0561E", shukla: "#f9e8dd", krishna: "#f0d4c4"}
    hemanta:  {accent: "#5B4B9A", shukla: "#eae5f4", krishna: "#d9d2ea"}
    shishira: {accent: "#3F6B8C", shukla: "#e2ecf2", krishna: "#cddde8"}

months:
  - name_dev: "चैत्र"
    name_rom: "Chaitra"
    ritu: vasanta
    season_label: "Vasanta (spring)"
    start: 2026-03-04
    amavasya: 2026-03-18
    end: 2026-04-02
    photo: ../assets/images/01.jpg
    quote:
      text: "When stillness arises from intense alertness and awareness, your perception opens up in ways that you have never thought possible."
      attribution: "Sadhguru"
    festivals:
      - {tithi: "S1",  label: "Gudi Padwa · Ugadi"}
      - {tithi: "S9",  label: "Rāma Navamī"}
      - {tithi: "S15", label: "Hanumān Jayantī"}

  - name_dev: "वैशाख"
    name_rom: "Vaishakha"
    ritu: vasanta
    season_label: "Vasanta (spring)"
    start: 2026-04-03
    amavasya: 2026-04-17
    end: 2026-05-02
    photo: ../assets/images/02.jpg
    quote:
      text: "Devotion means keeping your intellect aside to let a larger intelligence function through you."
      attribution: "Sadhguru"
    festivals:
      - {tithi: "S3",  label: "Akshaya Tritīyā"}
      - {tithi: "S15", label: "Buddha Pūrṇimā"}

  - name_dev: "अधिक ज्येष्ठ"
    name_rom: "Adhika Jyeshtha"
    adhika: true
    ritu: grishma
    season_label: "Grīshma (summer)"
    start: 2026-05-03
    amavasya: 2026-05-16
    end: 2026-05-31
    photo: ../assets/images/03.jpg
    quote:
      text: "If you want Transformation, the largest part has to happen in your Body, because the Body carries substantially more memory than the Mind."
      attribution: "Sadhguru"
    festivals: []

  - name_dev: "ज्येष्ठ"
    name_rom: "Jyeshtha"
    ritu: grishma
    season_label: "Grīshma (summer)"
    start: 2026-06-01
    amavasya: 2026-06-14
    end: 2026-06-29
    photo: ../assets/images/04.jpg
    quote:
      text: "Success means doing something the way it works."
      attribution: "Sadhguru"
    festivals:
      - {tithi: "S10", label: "Gangā Dussehra"}
      - {tithi: "S11", label: "Nirjalā Ekādashī"}
      - {tithi: "S15", label: "Vat Pūrṇimā"}

  - name_dev: "आषाढ"
    name_rom: "Ashadha"
    ritu: varsha
    season_label: "Varshā (monsoon)"
    start: 2026-06-30
    amavasya: 2026-07-14
    end: 2026-07-29
    photo: ../assets/images/05.jpg
    quote:
      text: "May you realize the true purpose and potential of life. On this Guru Purnima, grace is upon you. I am with you."
      attribution: "Sadhguru"
    festivals:
      - {tithi: "S2",  label: "Rath Yātrā"}
      - {tithi: "S11", label: "Devshayanī Ekādashī"}
      - {tithi: "S15", label: "Guru Pūrṇimā"}

  - name_dev: "श्रावण"
    name_rom: "Shravana"
    ritu: varsha
    season_label: "Varshā (monsoon)"
    start: 2026-07-30
    amavasya: 2026-08-12
    end: 2026-08-27
    photo: ../assets/images/06.jpg
    quote:
      text: "Your ways of thinking and feeling, your likes and dislikes, your philosophies and ideologies all melt down when you fall in love."
      attribution: "Sadhguru"
    festivals:
      - {tithi: "S5",  label: "Nāg Panchamī"}
      - {tithi: "S15", label: "Rakshā Bandhan"}

  - name_dev: "भाद्रपद"
    name_rom: "Bhadrapada"
    ritu: sharad
    season_label: "Sharad (autumn)"
    start: 2026-08-28
    amavasya: 2026-09-10
    end: 2026-09-25
    photo: ../assets/images/07.jpg
    quote:
      text: "If you want to explore the deepest dimensions of life playfully, you need a heart full of love, a joyful mind, and a vibrant body."
      attribution: "Sadhguru"
    festivals:
      - {tithi: "K8",  label: "Janmāshtamī"}
      - {tithi: "S4",  label: "Gaṇesha Chaturthī"}
      - {tithi: "S14", label: "Anant Chaturdashī"}

  - name_dev: "आश्विन"
    name_rom: "Ashwina"
    ritu: sharad
    season_label: "Sharad (autumn)"
    start: 2026-09-26
    amavasya: 2026-10-10
    end: 2026-10-25
    photo: ../assets/images/08.jpg
    quote:
      text: "If you treat your tools, including your own body and mind, with reverence, every activity will be a fruitful and joyful process."
      attribution: "Sadhguru"
    festivals:
      - {tithi: "K1",  label: "Pitru Paksha begins"}
      - {tithi: "S1",  label: "Sharad Navrātri"}
      - {tithi: "S10", label: "Dussehra"}
      - {tithi: "S15", label: "Sharad Pūrṇimā"}

  - name_dev: "कार्तिक"
    name_rom: "Kartika"
    ritu: hemanta
    season_label: "Hemanta (pre-winter)"
    start: 2026-10-26
    amavasya: 2026-11-08
    end: 2026-11-23
    photo: ../assets/images/09.jpg
    quote:
      text: "Lighting up in joy, love, and consciousness is vital in times of crisis. This Diwali, light up your Humanity to its full glory."
      attribution: "Sadhguru"
    festivals:
      - {tithi: "K13",       label: "Dhanteras"}
      - {tithi: "Amavasya",  label: "DIWALI"}
      - {tithi: "S1",        label: "Govardhan Pūjā"}
      - {tithi: "S2",        label: "Bhai Dooj"}
      - {tithi: "S11",       label: "Dev Uthanī Ekādashī"}
      - {tithi: "S15",       label: "Kārtik Pūrṇimā"}

  - name_dev: "मार्गशीर्ष"
    name_rom: "Margashirsha"
    ritu: hemanta
    season_label: "Hemanta (pre-winter)"
    start: 2026-11-24
    amavasya: 2026-12-08
    end: 2026-12-23
    photo: ../assets/images/10.jpg
    quote:
      text: "The word Yoga means union. That means you consciously obliterate the boundaries of individuality and reverberate with the rest of the cosmos."
      attribution: "Sadhguru"
    festivals:
      - {tithi: "S11", label: "Gītā Jayantī"}
      - {tithi: "S15", label: "Dattātreya Jayantī"}

  - name_dev: "पौष"
    name_rom: "Pausha"
    ritu: shishira
    season_label: "Shishira (winter)"
    start: 2026-12-24
    amavasya: 2027-01-07
    end: 2027-01-22
    photo: ../assets/images/11.jpg
    quote:
      text: "This is an ideal day to clear your home, your mind, and your emotions of all that is redundant, and make a Fresh Start."
      attribution: "Sadhguru"
    festivals:
      - {date: 2027-01-14, label: "Makar Sankrānti"}
      - {tithi: "S15",     label: "Pausha Pūrṇimā"}

  - name_dev: "माघ"
    name_rom: "Magha"
    ritu: shishira
    season_label: "Shishira (winter)"
    start: 2027-01-23
    amavasya: 2027-02-06
    end: 2027-02-21
    photo: ../assets/images/12.jpg
    quote:
      text: "Life is not in its goal. Life is in its process – in how you Experience it within yourself right now."
      attribution: "Sadhguru"
    festivals:
      - {tithi: "S5",  label: "Vasant Panchamī"}
      - {tithi: "S15", label: "Māghī Pūrṇimā"}

  - name_dev: "फाल्गुन"
    name_rom: "Phalguna"
    ritu: shishira
    season_label: "Shishira (winter)"
    start: 2027-02-22
    amavasya: 2027-03-08
    end: 2027-03-23
    photo: ../assets/images/13.jpg
    quote:
      text: "Adiyogi Shiva is the source of the science of yoga. His relevance is not in his ancientness but of the future."
      attribution: "Sadhguru"
    festivals:
      - {tithi: "K14", label: "Mahā Shivarātri"}
      - {tithi: "S14", label: "Holikā Dahan"}
      - {tithi: "S15", label: "HOLI"}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/abhiag/Downloads/panchang/panchang_calendar && python -m pytest tests/test_sample_config.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/abhiag/Downloads/panchang
git add panchang_calendar/config/vs2083.yaml panchang_calendar/tests/test_sample_config.py
git commit -m "feat: sample VS 2083 config pre-filled from reference"
```

---

### Task 6: Theme → CSS tokens (`theme.py`)

**Files:**
- Create: `panchang_calendar/panchang/theme.py`
- Test: `panchang_calendar/tests/test_theme.py`

**Interfaces:**
- Consumes: `Theme` from `panchang.models`.
- Produces: `page_px(theme) -> (int, int)`, `device_scale(theme) -> float`, `font_face_css(theme, fonts_dir) -> str`.

- [ ] **Step 1: Write the failing test** — `tests/test_theme.py`

```python
from pathlib import Path
from panchang.models import Fonts, PageSpec, RituPalette, Theme
from panchang import theme as T

ROOT = Path(__file__).resolve().parent.parent


def _theme():
    return Theme(page=PageSpec(10, 3.5, 300, 8, 42),
                 fonts=Fonts("Noto Sans Devanagari", "Noto Serif", "Cormorant Garamond"),
                 ritu={"vasanta": RituPalette("#4E8B3A", "#e8f2e2", "#d2e4c8")})


def test_page_px_at_96dpi():
    assert T.page_px(_theme()) == (960, 336)


def test_device_scale_is_dpi_over_96():
    assert abs(T.device_scale(_theme()) - 3.125) < 1e-9


def test_font_face_css_references_bundled_files():
    css = T.font_face_css(_theme(), ROOT / "fonts")
    assert css.count("@font-face") == 3
    assert "file://" in css
    assert "Noto Sans Devanagari" in css and "Cormorant Garamond" in css
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/abhiag/Downloads/panchang/panchang_calendar && python -m pytest tests/test_theme.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'panchang.theme'`.

- [ ] **Step 3: Write `panchang/theme.py`**

```python
"""Translate theme tokens into CSS values: dimensions, device scale, @font-face."""
from __future__ import annotations
from pathlib import Path
from .models import Theme


def page_px(theme: Theme) -> tuple[int, int]:
    """CSS-px box at 96 px/in (10in × 3.5in → 960 × 336)."""
    return (round(theme.page.width_in * 96), round(theme.page.height_in * 96))


def device_scale(theme: Theme) -> float:
    """Screenshot scale so CSS px → device px hits the target DPI (300/96 = 3.125)."""
    return theme.page.dpi / 96.0


def font_face_css(theme: Theme, fonts_dir) -> str:
    """@font-face blocks pointing at the bundled variable TTFs (file:// URLs)."""
    fonts_dir = Path(fonts_dir).resolve()
    faces = [
        (theme.fonts.devanagari, "NotoSansDevanagari.ttf"),
        (theme.fonts.serif, "NotoSerif.ttf"),
        (theme.fonts.quote, "CormorantGaramond.ttf"),
    ]
    out = []
    for family, fname in faces:
        uri = (fonts_dir / fname).as_uri()
        out.append(
            f"@font-face {{ font-family:'{family}'; src:url('{uri}'); "
            f"font-weight:300 800; font-display:block; }}"
        )
    return "\n".join(out)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/abhiag/Downloads/panchang/panchang_calendar && python -m pytest tests/test_theme.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/abhiag/Downloads/panchang
git add panchang_calendar/panchang/theme.py panchang_calendar/tests/test_theme.py
git commit -m "feat: theme→CSS tokens (page px, device scale, font-face)"
```

---

### Task 7: HTML layout (`layout.py`)

**Files:**
- Create: `panchang_calendar/panchang/layout.py`
- Test: `panchang_calendar/tests/test_layout.py`

**Interfaces:**
- Consumes: `Calendar`, `MonthData` (models); `panchang` logic (`month_grid`, `deva`, `greg_label`, `WEEKDAYS_DEV`, `krishna_length`); `theme` (`page_px`, `font_face_css`).
- Produces: `month_html(cal, month) -> str`, `cover_html(cal) -> str` — each a complete standalone HTML document. Photo embedded as a base64 data URI. Fonts dir defaults to `panchang_calendar/fonts`.

- [ ] **Step 1: Write the failing test** — `tests/test_layout.py`

```python
from pathlib import Path
from panchang.config import load_config
from panchang import layout

CFG = Path(__file__).resolve().parent.parent / "config" / "vs2083.yaml"
CAL = load_config(CFG)


def test_month_html_has_core_content():
    chaitra = CAL.months[0]
    html = layout.month_html(CAL, chaitra)
    assert "चैत्र" in html and "Chaitra" in html
    assert "Gudi Padwa" in html                 # a festival label
    assert "Sadhguru" in html                   # attribution
    assert "data:image" in html                 # embedded photo
    assert "१" in html                          # a Devanagari tithi numeral
    assert "960px" in html and "336px" in html  # 10x3.5in @96dpi box


def test_adhika_badge_only_on_leap_month():
    adhika = next(m for m in CAL.months if m.adhika)
    normal = CAL.months[0]
    assert "अधिक" in layout.month_html(CAL, adhika)
    assert "अधिक मास" not in layout.month_html(CAL, normal)


def test_cover_lists_all_months():
    html = layout.cover_html(CAL)
    assert "Vikram Samvat" in html and "2083" in html
    for m in CAL.months:
        assert m.name_rom in html
    assert "★" in html                          # adhika marker in the index
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/abhiag/Downloads/panchang/panchang_calendar && python -m pytest tests/test_layout.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'panchang.layout'`.

- [ ] **Step 3: Write `panchang/layout.py`**

```python
"""Build standalone HTML for each panel (cover + month) from the model + theme.
Coordinate space is the 96-px/in CSS box (960×336 for 10×3.5in); render.py
screenshots it at device scale for the 300-DPI PNG and prints it to PDF."""
from __future__ import annotations
import base64
import html as _html
import mimetypes
from pathlib import Path

from .models import Calendar, MonthData
from . import panchang as P
from .theme import font_face_css, page_px

FONTS_DIR = Path(__file__).resolve().parent.parent / "fonts"


def _esc(s: str) -> str:
    return _html.escape(s or "")


def _img_data_uri(path: str) -> str:
    p = Path(path)
    mime = mimetypes.guess_type(p.name)[0] or "image/jpeg"
    b64 = base64.b64encode(p.read_bytes()).decode()
    return f"data:{mime};base64,{b64}"


def _document(cal: Calendar, body: str, extra_css: str = "") -> str:
    w, h = page_px(cal.theme)
    top_safe_px = round(cal.theme.page.top_safe_mm / 25.4 * 96)
    cal_pct = cal.theme.page.calendar_pct
    f = cal.theme.fonts
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
{font_face_css(cal.theme, FONTS_DIR)}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:{w}px; height:{h}px; }}
body {{ font-family:'{f.serif}','Noto Serif',serif; color:#241d16;
       -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
.dev {{ font-family:'{f.devanagari}','Noto Sans Devanagari',sans-serif; }}
.panel {{ width:{w}px; height:{h}px; display:flex; overflow:hidden; background:#fbf8f1; }}
.top-safe {{ height:{top_safe_px}px; }}
/* ----- photo (left) ----- */
.photo {{ flex:0 0 {100 - cal_pct}%; background-size:cover; background-position:center;
          position:relative; }}
.photo::after {{ content:''; position:absolute; inset:0 0 0 auto; width:24px;
                 background:linear-gradient(90deg, rgba(251,248,241,0), #fbf8f1); }}
/* ----- calendar column (right) ----- */
.cal {{ flex:0 0 {cal_pct}%; padding:{top_safe_px}px 14px 8px 14px;
        display:flex; flex-direction:column; }}
.title {{ display:flex; align-items:baseline; gap:8px; }}
.title .mdev {{ font-size:22px; }}
.title .mrom {{ font-size:15px; font-weight:700; color:#2a2018; }}
.title .ritu {{ font-size:10px; color:var(--accent); margin-left:auto; }}
.adhika {{ font-size:8px; letter-spacing:.04em; color:#fff; background:var(--accent);
           padding:1px 5px; border-radius:7px; }}
.span {{ font-size:9px; color:#6a5f50; margin:1px 0 4px; }}
.quote {{ font-family:'{f.quote}','Noto Serif',serif; font-size:12px; line-height:1.45;
          color:#3a3028; margin:2px 0 5px; }}
.quote .attr {{ display:block; font-family:'{f.serif}',serif; font-size:8px;
                letter-spacing:.06em; color:#9a8c72; margin-top:2px; text-transform:uppercase; }}
table.grid {{ width:100%; border-collapse:collapse; table-layout:fixed; flex:1; }}
.grid th {{ background:var(--accent); color:#fff; font-size:10px; padding:2px 0;
            font-weight:600; }}
.grid td {{ border:.5px solid #e3dccf; vertical-align:top; padding:1px 2px;
            line-height:1; }}
.grid td.out {{ background:#f3f0e9; }}
.grid td.kr {{ background:var(--krishna); }}
.grid td.sh {{ background:var(--shukla); }}
.cellnum {{ display:flex; align-items:baseline; justify-content:space-between; }}
.tithi {{ font-size:13px; font-weight:700; color:var(--accent); }}
.tithi.out {{ color:#bfb6a4; }}
.greg {{ font-size:6.5px; font-weight:700; color:#8a7c66; }}
.greg.out {{ color:#c4bcab; }}
.fest {{ display:block; font-size:6px; font-weight:700; color:var(--accent);
         line-height:1.05; margin-top:1px; overflow:hidden; max-height:13px; }}
.badge {{ display:block; font-size:6px; color:#5d5345; margin-top:1px; }}
.legend {{ display:flex; gap:10px; font-size:7px; color:#7a6e5c; margin-top:4px;
           align-items:center; }}
.legend .sw {{ display:inline-block; width:7px; height:7px; border:.5px solid #ccc;
               vertical-align:-1px; margin-right:3px; }}
{extra_css}
</style></head><body>{body}</body></html>"""


def month_html(cal: Calendar, m: MonthData) -> str:
    pal = cal.theme.ritu[m.ritu]
    style_vars = f"--accent:{pal.accent};--krishna:{pal.krishna};--shukla:{pal.shukla}"
    img = _img_data_uri(m.photo)
    span = (f"{P.greg_label(m.start)} – {P.greg_label(m.end)} {m.end.year}"
            f" · {(m.end - m.start).days + 1} days")
    adhika = f'<span class="adhika">अधिक मास</span>' if m.adhika else ""

    head = "".join(f'<th class="dev">{w}</th>' for w in P.WEEKDAYS_DEV)
    rows = ""
    for week in P.month_grid(m):
        rows += "<tr>"
        for c in week:
            if not c.in_month:
                rows += (f'<td class="out"><div class="cellnum">'
                         f'<span class="tithi out">&nbsp;</span>'
                         f'<span class="greg out">{P.greg_label(c.date)}</span>'
                         f'</div></td>')
                continue
            klass = "kr" if c.paksha == "K" else "sh"
            fest = f'<span class="fest">{_esc(c.festival)}</span>' if c.festival else ""
            badge = f'<span class="badge dev">{c.badge}</span>' if c.badge else ""
            rows += (f'<td class="{klass}"><div class="cellnum">'
                     f'<span class="tithi dev">{P.deva(c.tithi)}</span>'
                     f'<span class="greg">{P.greg_label(c.date)}</span></div>'
                     f'{badge}{fest}</td>')
        rows += "</tr>"

    kr = P.krishna_length(m)
    legend = (f'<div class="legend">'
              f'<span><span class="sw" style="background:{pal.krishna}"></span>'
              f'<span class="dev">कृष्ण १→{P.deva(kr)} ○</span></span>'
              f'<span><span class="sw" style="background:{pal.shukla}"></span>'
              f'<span class="dev">शुक्ल १→१५ ●</span></span></div>')

    body = f"""<section class="panel" style="{style_vars}">
  <div class="photo" style="background-image:url('{img}')"></div>
  <div class="cal">
    <div class="title">
      <span class="mdev dev">{_esc(m.name_dev)}</span>
      <span class="mrom">{_esc(m.name_rom)}</span>{adhika}
      <span class="ritu">{_esc(m.season_label)}</span>
    </div>
    <div class="span">{_esc(span)}</div>
    <div class="quote">“{_esc(m.quote.text)}”<span class="attr">— {_esc(m.quote.attribution)}</span></div>
    <table class="grid"><tr>{head}</tr>{rows}</table>
    {legend}
  </div>
</section>"""
    return _document(cal, body)


def cover_html(cal: Calendar) -> str:
    pal = cal.theme.ritu[cal.months[0].ritu]
    rows = ""
    for m in cal.months:
        pal_m = cal.theme.ritu[m.ritu]
        span = f"{P.greg_label(m.start)} – {P.greg_label(m.end)} '{str(m.end.year)[2:]}"
        star = " ★" if m.adhika else ""
        rows += (f'<tr><td class="ci" style="color:{pal_m.accent}">{m.index:02d}</td>'
                 f'<td><span class="dev">{_esc(m.name_dev)}</span> '
                 f'<b>{_esc(m.name_rom)}</b>{star}</td>'
                 f'<td class="cspan">{_esc(span)}</td>'
                 f'<td class="cse" style="color:{pal_m.accent}">'
                 f'{_esc(m.season_label.split(" ")[0])}</td></tr>')

    extra = """
.cover { display:flex; flex-direction:column; padding:30px 28px 14px; height:336px; }
.cover .kick { letter-spacing:.28em; text-transform:uppercase; font-size:8px; color:#9a6a2c; }
.cover h1 { font-size:30px; line-height:1.05; color:#7a3b14; margin:3px 0; }
.cover h1 .yr { color:#c0561e; }
.cover .sub { font-size:10px; color:#3a2f25; margin-bottom:4px; }
.cover .note { font-size:7.5px; line-height:1.5; color:#4a4036; margin-bottom:6px; }
.cov-tbl { width:100%; border-collapse:collapse; }
.cov-tbl td { padding:1.5px 6px; border-bottom:.5px solid #e3dccf; font-size:8.5px; text-align:left; }
.cov-tbl .ci { font-weight:700; width:22px; }
.cov-tbl .cspan { color:#5d5345; white-space:nowrap; }
.cov-tbl .cse { white-space:nowrap; }
"""
    body = f"""<section class="panel cover" style="--accent:{pal.accent}">
  <div class="kick">The Lunar Almanac · Pūrṇimānta</div>
  <h1>{_esc(cal.cover.title)} <span class="yr">{cal.samvat}</span></h1>
  <div class="sub">{_esc(cal.cover.subtitle)}</div>
  <div class="note">{_esc(cal.cover.note)}</div>
  <table class="cov-tbl">{rows}</table>
</section>"""
    return _document(cal, body, extra_css=extra)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/abhiag/Downloads/panchang/panchang_calendar && python -m pytest tests/test_layout.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/abhiag/Downloads/panchang
git add panchang_calendar/panchang/layout.py panchang_calendar/tests/test_layout.py
git commit -m "feat: HTML layout for month panels and cover"
```

---

### Task 8: Render to PNG + PDF (`render.py`)

**Files:**
- Create: `panchang_calendar/panchang/render.py`
- Test: `panchang_calendar/tests/test_render.py`

**Interfaces:**
- Consumes: `Calendar` (models); `layout.month_html`/`cover_html`; `theme.page_px`/`device_scale`; `playwright.sync_api`; `pypdf`.
- Produces: `build_panels(cal) -> list[(name, html)]` (cover first), `render_all(cal, outdir, png=True, pdf=True) -> (pdf_path|None, list[png_path])`. PNG names: `00_cover.png`, `NN_<slug>.png`.

**Before coding:** verify the Playwright sync API via context7 (`p.chromium.launch`, `browser.new_page(viewport=..., device_scale_factor=...)`, `page.goto`, `page.screenshot(clip=...)`, `page.pdf(width=..., height=..., print_background=...)`). Note in the commit body that context7 was consulted.

- [ ] **Step 1: Write the failing test** — `tests/test_render.py`

```python
import struct
from pathlib import Path
from copy import copy
from pypdf import PdfReader
from panchang.config import load_config
from panchang import render

CFG = Path(__file__).resolve().parent.parent / "config" / "vs2083.yaml"


def _png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    assert head[:8] == b"\x89PNG\r\n\x1a\n"
    w, h = struct.unpack(">II", head[16:24])
    return w, h


def test_build_panels_cover_first():
    cal = load_config(CFG)
    panels = render.build_panels(cal)
    assert panels[0][0] == "00_cover"
    assert panels[1][0].startswith("01_")
    assert len(panels) == cal.page_count


def test_render_cover_plus_one_month(tmp_path):
    cal = load_config(CFG)
    cal.months = cal.months[:1]                 # cover + 1 month = 2 pages
    pdf_path, pngs = render.render_all(cal, tmp_path)
    assert len(pngs) == 2
    for p in pngs:
        assert _png_size(p) == (3000, 1050)     # exact 300-DPI 10x3.5in
    assert PdfReader(str(pdf_path)).pages and len(PdfReader(str(pdf_path)).pages) == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/abhiag/Downloads/panchang/panchang_calendar && python -m pytest tests/test_render.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'panchang.render'`.

- [ ] **Step 3: Write `panchang/render.py`**

```python
"""Render panel HTML to 300-DPI PNGs and a merged PDF via Playwright Chromium."""
from __future__ import annotations
from pathlib import Path

from playwright.sync_api import sync_playwright
from pypdf import PdfWriter

from .models import Calendar
from .theme import page_px, device_scale
from . import layout


def _slug(s: str) -> str:
    return "".join(c.lower() if c.isalnum() else "_" for c in s).strip("_")


def build_panels(cal: Calendar) -> list[tuple[str, str]]:
    """[(name, html), …] — cover first, then one per month."""
    panels = [("00_cover", layout.cover_html(cal))]
    for m in cal.months:
        panels.append((f"{m.index:02d}_{_slug(m.name_rom)}", layout.month_html(cal, m)))
    return panels


def render_all(cal: Calendar, outdir, png: bool = True, pdf: bool = True):
    outdir = Path(outdir)
    (outdir / "pages").mkdir(parents=True, exist_ok=True)
    panel_dir = outdir / "_panels"
    panel_dir.mkdir(parents=True, exist_ok=True)

    w, h = page_px(cal.theme)
    scale = device_scale(cal.theme)
    panels = build_panels(cal)
    png_paths: list[Path] = []
    pdf_paths: list[Path] = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for name, html in panels:
            html_path = panel_dir / f"{name}.html"
            html_path.write_text(html, encoding="utf-8")
            page = browser.new_page(viewport={"width": w, "height": h},
                                    device_scale_factor=scale)
            page.goto(html_path.as_uri())
            page.wait_for_timeout(250)          # let fonts/layout settle
            if png:
                pp = outdir / "pages" / f"{name}.png"
                page.screenshot(path=str(pp),
                                clip={"x": 0, "y": 0, "width": w, "height": h})
                png_paths.append(pp)
            if pdf:
                dp = panel_dir / f"{name}.pdf"
                page.pdf(path=str(dp),
                         width=f"{cal.theme.page.width_in}in",
                         height=f"{cal.theme.page.height_in}in",
                         print_background=True,
                         margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
                pdf_paths.append(dp)
            page.close()
        browser.close()

    merged = None
    if pdf:
        merged = outdir / "calendar.pdf"
        writer = PdfWriter()
        for dp in pdf_paths:
            writer.append(str(dp))
        with open(merged, "wb") as f:
            writer.write(f)
    return merged, png_paths
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/abhiag/Downloads/panchang/panchang_calendar && python -m pytest tests/test_render.py -v`
Expected: 2 passed. (First run is slower — Chromium launch.)

- [ ] **Step 5: Commit**

```bash
cd /Users/abhiag/Downloads/panchang
git add panchang_calendar/panchang/render.py panchang_calendar/tests/test_render.py
git commit -m "feat: Playwright render to 300-DPI PNG + merged PDF (context7-verified API)"
```

---

### Task 9: CLI, full build & README (`generate.py`, `README.md`)

**Files:**
- Create: `panchang_calendar/generate.py`
- Create: `panchang_calendar/README.md`
- Test: `panchang_calendar/tests/test_generate.py`

**Interfaces:**
- Consumes: `panchang.config.load_config`, `panchang.render.render_all`.
- Produces: `main(argv=None)` CLI with flags `--config`, `--outdir`, `--png-only`, `--pdf-only`, `--months N`.

- [ ] **Step 1: Write the failing test** — `tests/test_generate.py`

```python
import sys
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parent.parent


def _main():
    sys.path.insert(0, str(ROOT))
    return importlib.import_module("generate").main


def test_cli_preview_png_only(tmp_path):
    main = _main()
    main(["--months", "1", "--png-only", "--outdir", str(tmp_path)])
    pages = sorted((tmp_path / "pages").glob("*.png"))
    assert [p.name for p in pages] == ["00_cover.png", "01_chaitra.png"]
    assert not (tmp_path / "calendar.pdf").exists()    # --png-only
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/abhiag/Downloads/panchang/panchang_calendar && python -m pytest tests/test_generate.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'generate'`.

- [ ] **Step 3: Write `generate.py`**

```python
#!/usr/bin/env python3
"""CLI: generate the Panchang desk calendar (multi-page PDF + per-page 300-DPI PNGs).

Usage:
    python generate.py                      # full build from config/vs2083.yaml → out/
    python generate.py --months 2           # cover + first 2 months (quick preview)
    python generate.py --png-only           # skip the PDF
    python generate.py --config my.yaml --outdir build
"""
from __future__ import annotations
import argparse
import time
from pathlib import Path

from panchang.config import load_config
from panchang.render import render_all

HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG = HERE / "config" / "vs2083.yaml"
DEFAULT_OUTDIR = HERE / "out"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Generate the Panchang desk calendar.")
    ap.add_argument("--config", default=str(DEFAULT_CONFIG))
    ap.add_argument("--outdir", default=str(DEFAULT_OUTDIR))
    ap.add_argument("--png-only", action="store_true", help="Skip PDF generation")
    ap.add_argument("--pdf-only", action="store_true", help="Skip PNG generation")
    ap.add_argument("--months", type=int, default=0,
                    help="Render only the first N months (preview); 0 = all")
    args = ap.parse_args(argv)

    t0 = time.time()
    cal = load_config(args.config)
    if args.months > 0:
        cal.months = cal.months[:args.months]
    png = not args.pdf_only
    pdf = not args.png_only

    print(f"Panchang calendar: {cal.page_count} pages "
          f"(cover + {len(cal.months)} months)")
    merged, pngs = render_all(cal, args.outdir, png=png, pdf=pdf)
    if pdf:
        print(f"  PDF : {merged}")
    if png:
        print(f"  PNGs: {len(pngs)} → {Path(args.outdir) / 'pages'}")
    print(f"Done in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/abhiag/Downloads/panchang/panchang_calendar && python -m pytest tests/test_generate.py -v`
Expected: 1 passed.

- [ ] **Step 5: Run the full build and the whole test suite**

```bash
cd /Users/abhiag/Downloads/panchang/panchang_calendar
python generate.py
python -m pytest -v
```
Expected: `out/calendar.pdf` exists with 14 pages; `out/pages/` has `00_cover.png` … `13_phalguna.png` (14 PNGs, each 3000×1050); all tests pass.

- [ ] **Step 6: Visual check (manual, per spec §5)**

Open `out/pages/09_kartika.png` and `out/pages/00_cover.png`. Confirm: photo/parchment seam is clean; quote fits above the grid; grid rows aren't clipped; DIWALI shows on the amāvāsyā cell; Devanagari renders (not tofu boxes). If the grid is too tight, bump `theme.page.calendar_pct` (e.g. 45) in `config/vs2083.yaml` and re-run — **no code change**.

- [ ] **Step 7: Write `README.md`**

```markdown
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
```

- [ ] **Step 8: Commit**

```bash
cd /Users/abhiag/Downloads/panchang
git add panchang_calendar/generate.py panchang_calendar/README.md \
        panchang_calendar/tests/test_generate.py
git commit -m "feat: CLI generator + README; full VS 2083 build"
```

---

## Self-Review

**1. Spec coverage**

| Spec requirement | Task |
|---|---|
| 10×3.5in @300DPI, 3000×1050 PNG | Global Constraints; Tasks 6, 8 |
| Top safe strip (binding) | Tasks 6 (px calc), 7 (padding) |
| Page count derived (cover + months) | Tasks 2 (`page_count`), 5, 8 |
| No astronomy — config-driven | Tasks 3, 4, 5 |
| Lunar-range grid + tithi/paksha | Task 3 (`month_grid`), Task 7 |
| Krishna/Shukla shading, boundary badges, festivals | Tasks 3, 7 |
| Festivals by tithi / Amavasya / fixed date (fixed wins) | Task 3, 4 |
| Quote above grid; photo left ~58% | Task 7 |
| No logo; paksha legend footer | Task 7 |
| Cover panel + month index, adhika starred | Task 7 |
| YAML config + validation rules (§12) | Task 4 |
| Sample VS 2083 pre-filled from reference | Task 5 |
| Bundled offline fonts (Devanagari/serif/quote) | Tasks 1, 6 |
| Playwright → PNG + merged PDF | Task 8 |
| CLI, preview flag, README | Task 9 |
| Reuse month photos from vs2083_calendar/images | Task 1 |
| Testing strategy (unit + render smoke + visual) | Tasks 3,4,5,8 + Task 9 step 6 |

No gaps found.

**2. Placeholder scan:** No TBD/TODO/"handle edge cases"/"similar to" — every code and test step contains complete content. The only deferred item (exact font weight tuning / grid density) is handled by the §6 visual-check step with a concrete config knob, not a code placeholder.

**3. Type consistency:** `MonthData`, `Festival`, `Calendar.page_count`, `DayCell` fields (`in_month`, `paksha`, `tithi`, `badge`, `festival`, `is_amavasya`, `is_purnima`), `tithi_for`/`resolve_festival`/`month_grid`/`krishna_length`, `page_px`/`device_scale`/`font_face_css`, `month_html`/`cover_html`, `build_panels`/`render_all` signatures are used identically across the tasks that define and consume them. Photo is resolved to an absolute path in Task 4 and consumed as such in Task 7. Font file names (`NotoSansDevanagari.ttf` etc.) match between Task 1 (fetch), Task 6 (font_face_css), and the README.
