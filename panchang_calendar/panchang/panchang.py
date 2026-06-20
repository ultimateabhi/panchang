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
