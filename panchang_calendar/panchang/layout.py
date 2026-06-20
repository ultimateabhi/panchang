"""Build standalone HTML for each panel (cover + month) from the model + theme.
Coordinate space is the 96-px/in CSS box (960×336 for 10×3.5in); render.py
screenshots it at device scale for the 300-DPI PNG and prints it to PDF."""
from __future__ import annotations
import base64
import html as _html
import mimetypes
from pathlib import Path

from .models import Calendar, MonthData
from . import panchang as P
from .theme import font_face_css, page_px

FONTS_DIR = Path(__file__).resolve().parent.parent / "fonts"


def _esc(s: str) -> str:
    return _html.escape(s or "")


def _img_data_uri(path: str) -> str:
    p = Path(path)
    mime = mimetypes.guess_type(p.name)[0] or "image/jpeg"
    b64 = base64.b64encode(p.read_bytes()).decode()
    return f"data:{mime};base64,{b64}"


def _document(cal: Calendar, body: str, extra_css: str = "") -> str:
    w, h = page_px(cal.theme)
    top_safe_px = round(cal.theme.page.top_safe_mm / 25.4 * 96)
    cal_pct = cal.theme.page.calendar_pct
    f = cal.theme.fonts
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
{font_face_css(cal.theme, FONTS_DIR)}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:{w}px; height:{h}px; }}
body {{ font-family:'{f.serif}','Noto Serif',serif; color:#241d16;
       -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
.dev {{ font-family:'{f.devanagari}','Noto Sans Devanagari',sans-serif; }}
.panel {{ width:{w}px; height:{h}px; display:flex; overflow:hidden; background:#fbf8f1; }}
.top-safe {{ height:{top_safe_px}px; }}
/* ----- photo (left) ----- */
.photo {{ flex:0 0 {100 - cal_pct}%; background-size:cover; background-position:center;
          position:relative; }}
.photo::after {{ content:''; position:absolute; inset:0 0 0 auto; width:24px;
                 background:linear-gradient(90deg, rgba(251,248,241,0), #fbf8f1); }}
/* ----- calendar column (right) ----- */
.cal {{ flex:0 0 {cal_pct}%; padding:{top_safe_px}px 14px 8px 14px;
        display:flex; flex-direction:column; }}
.title {{ display:flex; align-items:baseline; gap:8px; }}
.title .mdev {{ font-size:22px; }}
.title .mrom {{ font-size:15px; font-weight:700; color:#2a2018; }}
.title .ritu {{ font-size:10px; color:var(--accent); margin-left:auto; }}
.adhika {{ font-size:8px; letter-spacing:.04em; color:#fff; background:var(--accent);
           padding:1px 5px; border-radius:7px; }}
.span {{ font-size:9px; color:#6a5f50; margin:1px 0 4px; }}
.quote {{ font-family:'{f.quote}','Noto Serif',serif; font-size:12px; line-height:1.45;
          color:#3a3028; margin:2px 0 5px; }}
.quote .attr {{ display:block; font-family:'{f.serif}',serif; font-size:8px;
                letter-spacing:.06em; color:#9a8c72; margin-top:2px; text-transform:uppercase; }}
table.grid {{ width:100%; border-collapse:collapse; table-layout:fixed; flex:1; }}
.grid th {{ background:var(--accent); color:#fff; font-size:10px; padding:2px 0;
            font-weight:600; }}
.grid td {{ border:.5px solid #e3dccf; vertical-align:top; padding:1px 2px;
            line-height:1; }}
.grid td.out {{ background:#f3f0e9; }}
.grid td.kr {{ background:var(--krishna); }}
.grid td.sh {{ background:var(--shukla); }}
.cellnum {{ display:flex; align-items:baseline; justify-content:space-between; }}
.tithi {{ font-size:13px; font-weight:700; color:var(--accent); }}
.tithi.out {{ color:#bfb6a4; }}
.greg {{ font-size:6.5px; font-weight:700; color:#8a7c66; }}
.greg.out {{ color:#c4bcab; }}
.fest {{ display:block; font-size:6px; font-weight:700; color:var(--accent);
         line-height:1.05; margin-top:1px; overflow:hidden; max-height:13px; }}
.badge {{ display:block; font-size:6px; color:#5d5345; margin-top:1px; }}
.legend {{ display:flex; gap:10px; font-size:7px; color:#7a6e5c; margin-top:4px;
           align-items:center; }}
.legend .sw {{ display:inline-block; width:7px; height:7px; border:.5px solid #ccc;
               vertical-align:-1px; margin-right:3px; }}
{extra_css}
</style></head><body>{body}</body></html>"""


def month_html(cal: Calendar, m: MonthData) -> str:
    pal = cal.theme.ritu[m.ritu]
    style_vars = f"--accent:{_esc(pal.accent)};--krishna:{_esc(pal.krishna)};--shukla:{_esc(pal.shukla)}"
    img = _img_data_uri(m.photo)
    span = (f"{P.greg_label(m.start)} – {P.greg_label(m.end)} {m.end.year}"
            f" · {(m.end - m.start).days + 1} days")
    adhika = f'<span class="adhika">अधिक मास</span>' if m.adhika else ""

    head = "".join(f'<th class="dev">{w}</th>' for w in P.WEEKDAYS_DEV)
    rows = ""
    for week in P.month_grid(m):
        rows += "<tr>"
        for c in week:
            if not c.in_month:
                rows += (f'<td class="out"><div class="cellnum">'
                         f'<span class="tithi out">&nbsp;</span>'
                         f'<span class="greg out">{P.greg_label(c.date)}</span>'
                         f'</div></td>')
                continue
            klass = "kr" if c.paksha == "K" else "sh"
            fest = f'<span class="fest">{_esc(c.festival)}</span>' if c.festival else ""
            badge = f'<span class="badge dev">{_esc(c.badge)}</span>' if c.badge else ""
            rows += (f'<td class="{klass}"><div class="cellnum">'
                     f'<span class="tithi dev">{P.deva(c.tithi)}</span>'
                     f'<span class="greg">{P.greg_label(c.date)}</span></div>'
                     f'{badge}{fest}</td>')
        rows += "</tr>"

    kr = P.krishna_length(m)
    legend = (f'<div class="legend">'
              f'<span><span class="sw" style="background:{_esc(pal.krishna)}"></span>'
              f'<span class="dev">कृष्ण १→{P.deva(kr)} ○</span></span>'
              f'<span><span class="sw" style="background:{_esc(pal.shukla)}"></span>'
              f'<span class="dev">शुक्ल १→१५ ●</span></span></div>')

    body = f"""<section class="panel" style="{style_vars}">
  <div class="photo" style="background-image:url('{img}')"></div>
  <div class="cal">
    <div class="title">
      <span class="mdev dev">{_esc(m.name_dev)}</span>
      <span class="mrom">{_esc(m.name_rom)}</span>{adhika}
      <span class="ritu">{_esc(m.season_label)}</span>
    </div>
    <div class="span">{_esc(span)}</div>
    <div class="quote">"{_esc(m.quote.text)}"<span class="attr">— {_esc(m.quote.attribution)}</span></div>
    <table class="grid"><tr>{head}</tr>{rows}</table>
    {legend}
  </div>
</section>"""
    return _document(cal, body)


def cover_html(cal: Calendar) -> str:
    pal = cal.theme.ritu[cal.months[0].ritu]
    rows = ""
    for m in cal.months:
        pal_m = cal.theme.ritu[m.ritu]
        span = f"{P.greg_label(m.start)} – {P.greg_label(m.end)} '{str(m.end.year)[2:]}"
        star = " ★" if m.adhika else ""
        rows += (f'<tr><td class="ci" style="color:{_esc(pal_m.accent)}">{m.index:02d}</td>'
                 f'<td><span class="dev">{_esc(m.name_dev)}</span> '
                 f'<b>{_esc(m.name_rom)}</b>{star}</td>'
                 f'<td class="cspan">{_esc(span)}</td>'
                 f'<td class="cse" style="color:{_esc(pal_m.accent)}">'
                 f'{_esc(m.season_label.split(" ")[0])}</td></tr>')

    extra = """
.cover { display:flex; flex-direction:column; padding:30px 28px 14px; height:336px; }
.cover .kick { letter-spacing:.28em; text-transform:uppercase; font-size:8px; color:#9a6a2c; }
.cover h1 { font-size:30px; line-height:1.05; color:#7a3b14; margin:3px 0; }
.cover h1 .yr { color:#c0561e; }
.cover .sub { font-size:10px; color:#3a2f25; margin-bottom:4px; }
.cover .note { font-size:7.5px; line-height:1.5; color:#4a4036; margin-bottom:6px; }
.cov-tbl { width:100%; border-collapse:collapse; }
.cov-tbl td { padding:1.5px 6px; border-bottom:.5px solid #e3dccf; font-size:8.5px; text-align:left; }
.cov-tbl .ci { font-weight:700; width:22px; }
.cov-tbl .cspan { color:#5d5345; white-space:nowrap; }
.cov-tbl .cse { white-space:nowrap; }
"""
    body = f"""<section class="panel cover" style="--accent:{_esc(pal.accent)}">
  <div class="kick">The Lunar Almanac · Pūrṇimānta</div>
  <h1>{_esc(cal.cover.title)} <span class="yr">{cal.samvat}</span></h1>
  <div class="sub">{_esc(cal.cover.subtitle)}</div>
  <div class="note">{_esc(cal.cover.note)}</div>
  <table class="cov-tbl">{rows}</table>
</section>"""
    return _document(cal, body, extra_css=extra)
