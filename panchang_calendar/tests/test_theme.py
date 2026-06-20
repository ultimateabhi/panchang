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
