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
