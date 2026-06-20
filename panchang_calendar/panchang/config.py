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
