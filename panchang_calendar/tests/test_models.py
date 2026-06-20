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
