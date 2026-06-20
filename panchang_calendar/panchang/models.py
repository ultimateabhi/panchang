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
