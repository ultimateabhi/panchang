import struct
from pathlib import Path
from copy import copy
from pypdf import PdfReader
from panchang.config import load_config
from panchang import render

CFG = Path(__file__).resolve().parent.parent / "config" / "vs2083.yaml"


def _png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    assert head[:8] == b"\x89PNG\r\n\x1a\n"
    w, h = struct.unpack(">II", head[16:24])
    return w, h


def test_build_panels_cover_first():
    cal = load_config(CFG)
    panels = render.build_panels(cal)
    assert panels[0][0] == "00_cover"
    assert panels[1][0].startswith("01_")
    assert len(panels) == cal.page_count


def test_render_cover_plus_one_month(tmp_path):
    cal = load_config(CFG)
    cal.months = cal.months[:1]                 # cover + 1 month = 2 pages
    pdf_path, pngs = render.render_all(cal, tmp_path)
    assert len(pngs) == 2
    for p in pngs:
        assert _png_size(p) == (3000, 1050)     # exact 300-DPI 10x3.5in
    assert PdfReader(str(pdf_path)).pages and len(PdfReader(str(pdf_path)).pages) == 2
