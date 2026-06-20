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
