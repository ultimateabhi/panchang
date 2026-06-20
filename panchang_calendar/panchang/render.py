"""Render panel HTML to 300-DPI PNGs and a merged PDF via Playwright Chromium."""
from __future__ import annotations
import shutil
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
            try:
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
            finally:
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
    shutil.rmtree(panel_dir, ignore_errors=True)
    return merged, png_paths
