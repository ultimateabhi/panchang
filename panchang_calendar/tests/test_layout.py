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
