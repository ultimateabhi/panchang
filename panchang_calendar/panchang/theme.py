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
