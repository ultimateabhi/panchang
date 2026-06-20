#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vikram Samvat 2083 — 13-Month Lunisolar Calendar Generator
===========================================================
Generates a printable wall calendar in two formats:
  1. HTML  — opens in any browser; uses Google Fonts + external image URL
  2. PDF   — via wkhtmltopdf; embeds image as base64

Usage:
    python3 generate.py                  # outputs to current directory
    python3 generate.py --outdir ./out   # outputs to ./out/

Requirements:
    - Python 3.8+
    - Pillow        (pip install Pillow)       — only for AVIF/image conversion
    - wkhtmltopdf   (apt install wkhtmltopdf)  — only for PDF generation

The script will:
  1. Look for 'image.jpg' in the script's directory
  2. If not found, look for any image.* and convert via Pillow
  3. Base64-encode it for PDF embedding
  4. Write Vikram_Samvat_2083_Calendar.html and .pdf to --outdir
"""

import datetime, html, subprocess, os, sys, base64, argparse

D = datetime.date
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Image handling
# ---------------------------------------------------------------------------
def get_image_b64(script_dir):
    """Return a data:image/jpeg;base64,... URI for embedding."""
    b64_path = os.path.join(script_dir, "sg_b64.txt")
    jpg_path = os.path.join(script_dir, "image.jpg")

    # If pre-computed base64 exists, use it
    if os.path.exists(b64_path):
        with open(b64_path) as f:
            return f.read().strip()

    # Otherwise build from image.jpg (or convert from other formats)
    if not os.path.exists(jpg_path):
        # Try to find any image file and convert
        for ext in ("avif", "png", "webp", "bmp", "tiff"):
            src = os.path.join(script_dir, f"image.{ext}")
            if os.path.exists(src):
                from PIL import Image
                Image.open(src).convert("RGB").save(jpg_path, "JPEG", quality=85)
                print(f"  Converted image.{ext} → image.jpg")
                break

    if not os.path.exists(jpg_path):
        print("  ⚠ No image found — PDF will have no image.")
        return ""

    with open(jpg_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    uri = "data:image/jpeg;base64," + b64
    # Cache for next run
    with open(b64_path, "w") as f:
        f.write(uri)
    print(f"  Encoded image.jpg → sg_b64.txt ({len(b64)//1024}KB)")
    return uri


# ---------------------------------------------------------------------------
# Calendar data
# ---------------------------------------------------------------------------
WEEKDAYS_HI = ["र","सो","मं","बु","गु","शु","श"]

QUOTES = [
  ("\u201cWhenever righteousness wanes and unrighteousness prevails,\nI manifest Myself.\u201d",
   "Bhagavad G\u012bt\u0101 4.7"),
  ("\u201cWhoever offers Me a leaf, a flower, a fruit, or water\nwith devotion \u2014 that offering of love, I accept.\u201d",
   "Bhagavad G\u012bt\u0101 9.26"),
  ("\u201cSetting aside all meritorious deeds, just surrender\ncompletely to My will. I shall liberate you; do not grieve.\u201d",
   "Bhagavad G\u012bt\u0101 18.66"),
  ("\u201cOne must elevate oneself by one\u2019s own mind,\nnot degrade oneself. The mind alone is the friend,\nand the mind alone is the enemy.\u201d",
   "Bhagavad G\u012bt\u0101 6.5"),
  ("\u201cThe Guru is Brahm\u0101, the Guru is Vishnu,\nthe Guru is Maheshwara. The Guru is Parabrahman itself.\nSalutations to that Guru.\u201d",
   "Guru Stotram"),
  ("\u201cThat which is the finest essence \u2014 this whole world has\nthat as its soul. That is Reality. That is the Self.\nThat thou art.\u201d",
   "Ch\u0101ndogya Upanishad 6.8.7"),
  ("\u201cYou are the visible manifestation of the essence\nof the words \u2018That thou art.\u2019 You alone are the Creator,\nthe Sustainer, and the Destroyer.\u201d",
   "Ga\u1e47apati Atharvash\u012brsha"),
  ("\u201cLead me from the unreal to the real,\nfrom darkness to light,\nfrom death to immortality.\u201d",
   "B\u1e5bhad\u0101ra\u1e47yaka Upanishad 1.3.28"),
  ("\u201cFix your mind on Me, be devoted to Me,\noffer service to Me, bow down to Me \u2014\nyou shall certainly reach Me.\u201d",
   "Bhagavad G\u012bt\u0101 9.34"),
  ("\u201cOf the months I am M\u0101rgash\u012brsha;\nof the seasons I am the flower-bearer, spring.\u201d",
   "Bhagavad G\u012bt\u0101 10.35"),
  ("\u201cWe meditate on the radiant light of that divine Sun;\nmay it illuminate our minds.\u201d",
   "G\u0101yatr\u012b Mantra \u2014 \u1e5ag Veda 3.62.10"),
  ("\u201cThe Self is not born, nor does it ever die.\nIt is unborn, eternal, ever-existing, and primeval.\nIt is not slain when the body is slain.\u201d",
   "Bhagavad G\u012bt\u0101 2.20"),
  ("\u201cI am the beginning, the middle and also the end\nof all beings. I am the radiance of the radiant.\u201d",
   "Bhagavad G\u012bt\u0101 10.20, 10.36"),
]

# PURNIMANTA reckoning: each month runs full moon -> full moon.
#   start    = day after the previous Pūrṇimā (Krishna Pratipadā)
#   amavasya = the new moon within the month (end of the waning fortnight)
#   end      = this month's Pūrṇimā (full moon)
# Sequence within a month: Krishna paksha (start -> amavasya), then Shukla paksha
# (amavasya+1 -> end). Festivals keyed by ("K", tithi) / ("S", tithi) / "amavasya".
# Shukla paksha is always 15 days, so Pūrṇimā = ("S",15).
months = [
 dict(n=1, dev="चैत्र", rom="Chaitra", start=D(2026,3,4), amavasya=D(2026,3,18), end=D(2026,4,2),
      nak="Chitrā", ritu="Vasanta (spring)", ritukey="vasanta",
      fest={("S",1):"Gudi Padwa · Ugadi",("S",9):"Rāma Navamī",("S",15):"Hanumān Jayantī"}),
 dict(n=2, dev="वैशाख", rom="Vaishākha", start=D(2026,4,3), amavasya=D(2026,4,17), end=D(2026,5,2),
      nak="Vishākhā", ritu="Vasanta (spring)", ritukey="vasanta",
      fest={("S",3):"Akshaya Tritīyā",("S",15):"Buddha Pūrṇimā"}),
 dict(n=3, dev="अधिक ज्येष्ठ", rom="Adhika Jyeshtha", start=D(2026,5,3), amavasya=D(2026,5,16), end=D(2026,5,31),
      nak="(leap month)", ritu="Grīshma (summer)", ritukey="grishma", adhik=True, fest={}),
 dict(n=4, dev="ज्येष्ठ", rom="Jyeshtha", start=D(2026,6,1), amavasya=D(2026,6,14), end=D(2026,6,29),
      nak="Jyeshthā", ritu="Grīshma (summer)", ritukey="grishma",
      fest={("S",10):"Gangā Dussehra",("S",11):"Nirjalā Ekādashī",("S",15):"Vat Pūrṇimā"}),
 dict(n=5, dev="आषाढ", rom="Āshādha", start=D(2026,6,30), amavasya=D(2026,7,14), end=D(2026,7,29),
      nak="Pūrva/Uttara Āshādhā", ritu="Varshā (monsoon)", ritukey="varsha",
      fest={("S",2):"Rath Yātrā",("S",11):"Devshayanī Ekādashī",("S",15):"Guru Pūrṇimā"}),
 dict(n=6, dev="श्रावण", rom="Shrāvana", start=D(2026,7,30), amavasya=D(2026,8,12), end=D(2026,8,27),
      nak="Shravana", ritu="Varshā (monsoon)", ritukey="varsha",
      fest={("S",5):"Nāg Panchamī",("S",15):"Rakshā Bandhan"}),
 dict(n=7, dev="भाद्रपद", rom="Bhādrapada", start=D(2026,8,28), amavasya=D(2026,9,10), end=D(2026,9,25),
      nak="Pūrva/Uttara Bhādrapadā", ritu="Sharad (autumn)", ritukey="sharad",
      fest={("K",8):"Janmāshtamī",("S",4):"Gaṇesha Chaturthī",("S",14):"Anant Chaturdashī"}),
 dict(n=8, dev="आश्विन", rom="Āshwina", start=D(2026,9,26), amavasya=D(2026,10,10), end=D(2026,10,25),
      nak="Ashwinī", ritu="Sharad (autumn)", ritukey="sharad",
      fest={("K",1):"Pitru Paksha begins",("S",1):"Sharad Navrātri",("S",10):"Dussehra",("S",15):"Sharad Pūrṇimā"}),
 dict(n=9, dev="कार्तिक", rom="Kārtika", start=D(2026,10,26), amavasya=D(2026,11,8), end=D(2026,11,23),
      nak="Krittikā", ritu="Hemanta (pre-winter)", ritukey="hemanta",
      fest={("K",13):"Dhanteras","amavasya":"DIWALI",("S",1):"Govardhan Pūjā",("S",2):"Bhai Dooj",("S",11):"Dev Uthanī Ekādashī",("S",15):"Kārtik Pūrṇimā"}),
 dict(n=10, dev="मार्गशीर्ष", rom="Mārgashīrsha", start=D(2026,11,24), amavasya=D(2026,12,8), end=D(2026,12,23),
      nak="Mrigashīrshā", ritu="Hemanta (pre-winter)", ritukey="hemanta",
      fest={("S",11):"Gītā Jayantī",("S",15):"Dattātreya Jayantī"}),
 dict(n=11, dev="पौष", rom="Pausha", start=D(2026,12,24), amavasya=D(2027,1,7), end=D(2027,1,22),
      nak="Pushya", ritu="Shishira (winter)", ritukey="shishira",
      fest={("S",15):"Pausha Pūrṇimā"}, greg_fest={D(2027,1,14):"Makar Sankrānti"}),
 dict(n=12, dev="माघ", rom="Māgha", start=D(2027,1,23), amavasya=D(2027,2,6), end=D(2027,2,21),
      nak="Maghā", ritu="Shishira (winter)", ritukey="shishira",
      fest={("S",5):"Vasant Panchamī",("S",15):"Māghī Pūrṇimā"}),
 dict(n=13, dev="फाल्गुन", rom="Phālguna", start=D(2027,2,22), amavasya=D(2027,3,8), end=D(2027,3,23),
      nak="Pūrva/Uttara Phalgunī", ritu="Shishira (winter)", ritukey="shishira",
      fest={("K",14):"Mahā Shivarātri",("S",14):"Holikā Dahan",("S",15):"HOLI"}),
]

RITU_COLOR  = {"vasanta":"#4E8B3A","grishma":"#C8771B","varsha":"#1F8A8A",
               "sharad":"#C0561E","hemanta":"#5B4B9A","shishira":"#3F6B8C"}
RITU_SHUKLA = {"vasanta":"#e8f2e2","grishma":"#f7ecda","varsha":"#ddf0f0",
               "sharad":"#f9e8dd","hemanta":"#eae5f4","shishira":"#e2ecf2"}
RITU_KRISHNA= {"vasanta":"#d2e4c8","grishma":"#f0dcc2","varsha":"#c8e2e2",
               "sharad":"#f0d4c4","hemanta":"#d9d2ea","shishira":"#cddde8"}

MON  = ["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
DEVD = {'0':'०','1':'१','2':'२','3':'३','4':'४','5':'५','6':'६','7':'७','8':'८','9':'९'}

# ---------------------------------------------------------------------------
# Per-month Sadhguru quote + source image (selected via quote_picker.html)
# Each entry: month number -> (quote text, Isha image URL)
# ---------------------------------------------------------------------------
ATTRIB = "Sadhguru"
_W = "?auto=format&fit=max&w=1200"
PICKS = {
 1:  ("When stillness arises from intense alertness and awareness, your perception opens up in ways that you have never thought possible.",
      "https://www.datocms-assets.com/46272/1649547011-apr-10-20200503_sun_0096-e.jpg" + _W),
 2:  ("Devotion means keeping your intellect aside to let a larger intelligence function through you.",
      "https://www.datocms-assets.com/46272/1633393966-1633393965017.jpg" + _W),
 3:  ("If you want Transformation, the largest part has to happen in your Body, because the Body carries substantially more memory than the Mind.",
      "https://www.datocms-assets.com/46272/1685748627-jun-3-20150129_chi_0387-e.jpg" + _W),
 4:  ("Success means doing something the way it works.",
      "https://www.datocms-assets.com/46272/1633395280-1633395278790.jpg" + _W),
 5:  ("May you realize the true purpose and potential of life. On this Guru Purnima, grace is upon you. I am with you.",
      "https://www.datocms-assets.com/46272/1633396482-1633396481184.jpg" + _W),
 6:  ("Your ways of thinking and feeling, your likes and dislikes, your philosophies and ideologies all melt down when you fall in love.",
      "https://www.datocms-assets.com/46272/1724023819-aug-19-20120229_chi_0465-enhanced-nr-e.jpg" + _W),
 7:  ("If you want to explore the deepest dimensions of life playfully, you need a heart full of love, a joyful mind, and a vibrant body.",
      "https://www.datocms-assets.com/46272/1633362865-1633362864542.jpg" + _W),
 8:  ("If you treat your tools, including your own body and mind, with reverence, every activity will be a fruitful and joyful process.",
      "https://www.datocms-assets.com/46272/1633410574-1633410573224.jpg" + _W),
 9:  ("Lighting up in joy, love, and consciousness is vital in times of crisis. This Diwali, light up your Humanity to its full glory.",
      "https://www.datocms-assets.com/46272/1636470573-1636470572390.jpg" + _W),
 10: ("The word Yoga means union. That means you consciously obliterate the boundaries of individuality and reverberate with the rest of the cosmos.",
      "https://www.datocms-assets.com/46272/1733873429-dec-11-20210815_cmm_0578-e.jpg" + _W),
 11: ("This is an ideal day to clear your home, your mind, and your emotions of all that is redundant, and make a Fresh Start.",
      "https://www.datocms-assets.com/46272/1705188619-jan-14-20190922_sun_0339-enhanced-e.jpg" + _W),
 12: ("Life is not in its goal. Life is in its process – in how you Experience it within yourself right now.",
      "https://static.sadhguru.org/d/46272/1769133603-image_1769079468_7934.jpg" + _W),
 13: ("Adiyogi Shiva is the source of the science of yoga. His relevance is not in his ancientness but of the future.",
      "https://www.datocms-assets.com/46272/1633391546-1633391545445.jpg" + _W),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def deva(n):
    return ''.join(DEVD[c] for c in str(n))


def _fetch_image(url, dest):
    """Download an image URL to dest. Returns the raw bytes."""
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    with open(dest, "wb") as f:
        f.write(data)
    return data


def prepare_images(outdir, download=True):
    """Download each month's chosen image into <outdir>/images/NN.jpg and return
    {month: {'html': <relative path or remote url>, 'pdf': <base64 data-uri or url>}}.
    HTML uses the local file (easy to swap); PDF embeds base64 so it is portable.
    If a download fails (e.g. offline), falls back to the remote URL for both."""
    imgdir = os.path.join(outdir, "images")
    os.makedirs(imgdir, exist_ok=True)
    out = {}
    for n, (quote, url) in sorted(PICKS.items()):
        rel  = f"images/{n:02d}.jpg"
        dest = os.path.join(outdir, rel)
        data = None
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            with open(dest, "rb") as f:
                data = f.read()
        elif download:
            try:
                data = _fetch_image(url, dest)
                print(f"   ✓ image {n:02d} downloaded ({len(data)//1024} KB)")
            except Exception as e:
                print(f"   ⚠ image {n:02d} download failed ({e}); using remote URL")
        if data:
            out[n] = {"html": rel,
                      "pdf": "data:image/jpeg;base64," + base64.b64encode(data).decode()}
        else:
            out[n] = {"html": url, "pdf": url}
    return out


# ---------------------------------------------------------------------------
# Page builders
# ---------------------------------------------------------------------------
def month_page(m, for_pdf, images):
    accent  = RITU_COLOR[m["ritukey"]]
    sh_bg   = RITU_SHUKLA[m["ritukey"]]
    kr_bg   = RITU_KRISHNA[m["ritukey"]]
    length  = (m["end"] - m["start"]).days + 1
    gstart  = m["start"] - datetime.timedelta(days=(m["start"].weekday()+1) % 7)
    gend    = m["end"]   + datetime.timedelta(days=(5 - m["end"].weekday()) % 7)
    gf      = m.get("greg_fest", {})
    adhik   = '<span class="adhik">अधिक मास</span>' if m.get("adhik") else ''
    span    = (f'{m["start"].day} {MON[m["start"].month]} {m["start"].year} – '
               f'{m["end"].day} {MON[m["end"].month]} {m["end"].year}')

    # Quote (Sadhguru, chosen per month via quote_picker.html)
    qt       = PICKS[m["n"]][0]
    attr     = ATTRIB
    qt_html  = html.escape(qt).replace("\\n", "<br/>").replace("\n", "<br/>")

    # Image: HTML uses local file images/NN.jpg (easy to replace); PDF embeds base64
    img_src  = images[m["n"]]["pdf"] if for_pdf else images[m["n"]]["html"]
    img_html = (f'<img src="{img_src}" alt="{html.escape(m["rom"])}" class="top-img"/>'
                if img_src else
                f'<div class="top-img-ph" style="border-color:{accent}40;color:{accent}">'
                f'<span class="dev" style="font-size:20px">{m["dev"]}</span></div>')

    # Top section: quote (left) + image (right), then heading below
    top = f'''<div class="top-row">
      <div class="top-left">
        <div class="quote-block">
          <div class="qt">{qt_html}</div>
          <div class="qt-attr">— {html.escape(attr)}</div>
        </div>
      </div>
      <div class="top-right">{img_html}</div>
    </div>
    <div class="mhead" style="border-color:{accent}">
      <div class="mnum" style="color:{accent}">{m["n"]:02d}<span class="of">/13</span></div>
      <div class="mtitle">
        <div class="namerow"><span class="dev mname">{m["dev"]}</span><span class="rom">{html.escape(m["rom"])}</span>{adhik}</div>
        <div class="sub">{span} · {length} days · <span style="color:{accent}">{html.escape(m["ritu"])}</span></div>
      </div>
    </div>'''

    # Grid
    nrows  = ((gend - gstart).days + 1) // 7
    cell_h = min(18, 90 // nrows)

    cells = '<tr class="wd">' + ''.join(f'<th class="dev">{w}</th>' for w in WEEKDAYS_HI) + '</tr>'
    rows  = ''
    d = gstart
    while d <= gend:
        rows += '<tr>'
        for _ in range(7):
            if m["start"] <= d <= m["end"]:
                # Purnimanta: Krishna paksha (start -> amavasya) then Shukla (-> end)
                if d <= m["amavasya"]:
                    tnum, paksha = (d - m["start"]).days + 1, "K"
                    pnum, bg, ncol = tnum, kr_bg, accent
                else:
                    tnum, paksha = (d - m["amavasya"]).days, "S"
                    pnum, bg, ncol = tnum, sh_bg, accent
                badge = ''
                if   d == m["start"]:        badge = '<span class="bd">कृ॰ प्रतिपदा</span>'
                elif d == m["amavasya"]:     badge = '<span class="bd new">○ अमावस्या</span>'
                elif d == m["amavasya"] + datetime.timedelta(days=1):
                                             badge = '<span class="bd">शु॰ प्रतिपदा</span>'
                elif d == m["end"]:          badge = '<span class="bd full">● पूर्णिमा</span>'
                if d == m["amavasya"]:
                    fe = gf.get(d) or m["fest"].get("amavasya", '')
                else:
                    fe = gf.get(d) or m["fest"].get((paksha, tnum), '')
                fh = f'<span class="fest" style="color:{accent}">{html.escape(fe)}</span>' if fe else ''
                yr = f"\'{str(d.year)[2:]}" if d.month == 1 and d.day == 1 else ''
                cell = (f'<td class="act" style="background:{bg};height:{cell_h}mm">'
                        f'<div class="ctop"><span class="devanum" style="color:{ncol}">{deva(pnum)}</span>'
                        f'<span class="greg">{d.day} {MON[d.month]}{yr}</span></div>{badge}{fh}</td>')
            else:
                cell = (f'<td class="ina" style="height:{cell_h}mm">'
                        f'<div class="ctop"><span class="devanum">&nbsp;</span>'
                        f'<span class="greg ina-txt">{d.day} {MON[d.month]}</span></div></td>')
            rows += cell
            d += datetime.timedelta(days=1)
        rows += '</tr>'

    kr_len = (m["amavasya"] - m["start"]).days + 1
    grid = f'<table class="cal">{cells}{rows}</table>'
    foot = f'''<div class="mfoot"><div class="legend">
      <span><span class="sw" style="background:{kr_bg}"></span>कृष्ण (१→{deva(kr_len)} ○)</span>
      <span><span class="sw" style="background:{sh_bg}"></span>शुक्ल (१→१५ ●)</span>
    </div></div>'''

    return f'<section class="page month" style="--accent:{accent}">{top}{grid}{foot}</section>'


def cover():
    rows = ''
    for m in months:
        a    = RITU_COLOR[m["ritukey"]]
        span = f'{m["start"].day} {MON[m["start"].month]} – {m["end"].day} {MON[m["end"].month]} {str(m["end"].year)[2:]}'
        star = ' ★' if m.get("adhik") else ''
        rows += (f'<tr><td class="ci" style="color:{a}">{m["n"]:02d}</td>'
                 f'<td><span class="cdev dev">{m["dev"]}</span> <b>{html.escape(m["rom"])}</b>{star}</td>'
                 f'<td class="cspan">{span}</td>'
                 f'<td class="cse" style="color:{a}">{html.escape(m["ritu"].split(" ")[0])}</td></tr>')
    return f'''<section class="page cover">
      <div class="cov-top"><div class="cov-kick">The Lunar Almanac · Pūrṇimānta</div>
      <h1>Vikram Samvat<br><span class="yr">2083</span></h1>
      <div class="cov-sub">Thirteen lunar months &nbsp;·&nbsp; 4 Mar 2026 – 23 Mar 2027 &nbsp;·&nbsp; Pūrṇimānta reckoning</div>
      <p class="cov-note">VS 2083 has a thirteenth month — <b>adhika māsa</b> (★ Adhika Jyeshtha).
      In the <b>pūrṇimānta</b> system each month runs full moon → full moon: waning
      <i>krishna</i> <span class="dev">१</span>→ (○ अमावस्या), then waxing <i>shukla</i>
      <span class="dev">१→१५</span> (● पूर्णिमा, month-end). Devanagari = tithi; small = Gregorian date.</p></div>
      <table class="cov-tbl"><tr class="ch"><th>#</th><th>Month</th><th>Gregorian</th><th>Season</th></tr>{rows}</table>
      <div class="cov-foot">★ leap month</div></section>'''


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
def build_css(for_pdf):
    devnum  = "'FreeSans',sans-serif" if for_pdf else "'Noto Sans Devanagari','FreeSans',sans-serif"
    devname = "'Poppins','FreeSans',sans-serif" if for_pdf else "'Noto Sans Devanagari','Poppins',sans-serif"
    badge_font = "'FreeSans','Poppins',sans-serif" if for_pdf else "'Noto Sans Devanagari','FreeSans',sans-serif"
    page_pad = "0" if for_pdf else "8mm"  # small whitespace at top of each page (HTML only)
    return f"""
@page {{ size: 21.6cm 16.5cm; margin: 6mm 7mm; }}
*{{box-sizing:border-box;}} html,body{{margin:0;padding:0;}}
body{{font-family:'Noto Serif','Georgia',serif;color:#241d16;
     -webkit-print-color-adjust:exact;print-color-adjust:exact;}}
.dev{{font-family:{devname};}}
.devanum{{font-family:{devnum};font-feature-settings:"lnum";}}
.page{{page-break-after:always;break-after:page;position:relative;overflow:hidden;width:100%;padding-top:{page_pad};}}
.page:last-child{{page-break-after:auto;}}

/* Cover */
.cover{{display:flex;flex-direction:column;height:152mm;}}
.cov-kick{{letter-spacing:.3em;text-transform:uppercase;font-size:8px;color:#9a6a2c;font-family:'Helvetica',sans-serif;}}
.cover h1{{font-size:36px;line-height:1.05;margin:4px 0 3px;font-weight:700;color:#7a3b14;}}
.cover .yr{{color:#c0561e;}}
.cov-sub{{font-size:11px;color:#3a2f25;margin-bottom:6px;}}
.cov-note{{font-size:10px;line-height:1.55;color:#4a4036;max-width:180mm;margin:0 0 8px;}}
.cov-note .dev{{font-size:11px;font-weight:700;}}
.cov-tbl{{width:100%;border-collapse:collapse;font-family:'Helvetica',sans-serif;}}
.cov-tbl td,.cov-tbl th{{padding:3.5px 6px;border-bottom:.5px solid #e3dccf;text-align:left;font-size:10.5px;}}
.cov-tbl .ch th{{font-size:8.5px;letter-spacing:.07em;text-transform:uppercase;color:#8a7c66;border-bottom:1px solid #cdbfa6;}}
.cov-tbl .ci{{font-weight:700;width:28px;}}
.cov-tbl .cspan{{color:#5d5345;white-space:nowrap;}} .cov-tbl .cse{{font-size:10px;white-space:nowrap;}}
.cov-tbl .cdev{{font-size:13px;}}
.cov-foot{{margin-top:auto;padding-top:6px;font-size:9px;color:#8a7c66;font-family:'Helvetica',sans-serif;border-top:1px solid #e3dccf;}}

/* Month: top row */
.top-row{{display:flex;gap:10px;margin-bottom:2px;height:34mm;}}
.top-left{{flex:1;overflow:hidden;}}
.top-right{{width:34mm;height:34mm;flex-shrink:0;}}
.top-img{{width:100%;height:100%;object-fit:cover;display:block;border-radius:3px;}}
.top-img-ph{{width:100%;height:100%;border:1.5px dashed;border-radius:3px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;font-family:'Helvetica',sans-serif;}}

/* Month heading */
.mhead{{display:flex;align-items:flex-start;gap:8px;border-left:5px solid;padding:2px 0 3px 8px;margin:2px 0 3px;}}
.mnum{{font-size:24px;font-weight:700;line-height:1;font-family:'Helvetica',sans-serif;}}
.mnum .of{{font-size:10px;color:#b3a892;}}
.namerow{{display:flex;align-items:baseline;gap:14px;}}
.mname{{font-size:20px;line-height:1;margin-right:12px;}} .rom{{font-size:16px;font-weight:700;color:#2a2018;}}
.adhik{{font-family:'Helvetica',sans-serif;font-size:7px;letter-spacing:.05em;text-transform:uppercase;color:#fff;background:#C8771B;padding:1px 5px;border-radius:7px;}}
.sub{{font-size:9px;color:#5d5345;margin-top:1px;font-family:'Helvetica',sans-serif;}}

/* Quote */
.quote-block{{padding:4px 4px 0 0;}}
.qt{{font-family:'Cormorant Garamond','Liberation Serif','Georgia',serif;font-size:10.5px;line-height:1.55;color:#3a3028;font-weight:400;}}
.qt-attr{{font-family:'Helvetica',sans-serif;font-size:7.5px;color:#9a8c72;margin-top:2px;letter-spacing:.04em;}}

/* Grid */
.cal{{width:100%;border-collapse:collapse;table-layout:fixed;}}
.cal th,.cal td{{border:.5px solid #ddd5c6;}}
.cal tr.wd th{{background:var(--accent);color:#fff;font-size:13px;padding:3px 0;font-weight:600;text-align:center;}}
.cal td{{vertical-align:top;padding:2px 3px;}}
.ctop{{display:flex;align-items:baseline;justify-content:space-between;}}
.devanum{{font-size:18px;font-weight:700;line-height:1;}}
.greg{{font-family:'Helvetica',sans-serif;font-size:8.5px;font-weight:600;color:#8a7c66;}}
.cal td.ina{{background:#f6f4ef;}} .ina-txt{{color:#c4bcab !important;}}
.bd{{display:inline-block;font-family:{badge_font};font-size:8.5px;font-weight:600;color:#4a3f30;margin-top:2px;}}
.bd.full{{color:#9a6a2c;font-weight:700;}} .bd.new{{color:#33414a;font-weight:700;}}
.fest{{display:block;font-family:'Helvetica',sans-serif;font-size:8px;font-weight:700;line-height:1.12;margin-top:1px;}}

/* Footer */
.mfoot{{margin-top:2px;}}
.legend{{display:flex;gap:12px;flex-wrap:wrap;font-family:'Helvetica',sans-serif;font-size:8px;color:#7a6e5c;align-items:center;}}
.legend .sw{{display:inline-block;width:9px;height:9px;border:.5px solid #ccc;vertical-align:-1px;margin-right:3px;}}
"""


# ---------------------------------------------------------------------------
# Build full HTML
# ---------------------------------------------------------------------------
GOOGLE_FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500'
    '&family=Noto+Sans+Devanagari:wght@400;600;700&family=Noto+Serif:wght@400;700&display=swap" rel="stylesheet">'
)

def build(for_pdf, images):
    pages    = cover() + ''.join(month_page(m, for_pdf, images) for m in months)
    fonts    = '' if for_pdf else GOOGLE_FONTS
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>Vikram Samvat 2083 — 13-Month Calendar (Pūrṇimānta)</title>{fonts}
<style>{build_css(for_pdf)}</style></head><body>{pages}</body></html>'''


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Generate VS 2083 calendar (HTML + PDF)")
    parser.add_argument("--outdir", default=".", help="Output directory (default: current dir)")
    parser.add_argument("--html-only", action="store_true", help="Skip PDF generation")
    parser.add_argument("--no-download", action="store_true",
                        help="Don't download images; reference remote Isha URLs instead")
    args = parser.parse_args()

    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    print("Vikram Samvat 2083 Calendar Generator")
    print("=" * 40)

    # 1. Prepare per-month images (download + cache in images/)
    print("\n1. Preparing images...")
    images = prepare_images(outdir, download=not args.no_download)

    # 2. Generate HTML
    print("\n2. Generating HTML...")
    html_path = os.path.join(outdir, "Vikram_Samvat_2083_Purnimanta_Calendar.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(build(for_pdf=False, images=images))
    print(f"   ✓ {html_path}")

    # 3. Generate PDF
    if args.html_only:
        print("\n3. PDF skipped (--html-only)")
    else:
        print("\n3. Generating PDF...")
        pdf_html = os.path.join(outdir, "_temp_pdf.html")
        pdf_path = os.path.join(outdir, "Vikram_Samvat_2083_Purnimanta_Calendar.pdf")
        with open(pdf_html, "w", encoding="utf-8") as f:
            f.write(build(for_pdf=True, images=images))
        cmd = [
            "wkhtmltopdf", "--enable-local-file-access",
            "--page-width", "21.6cm", "--page-height", "16.5cm",
            "--margin-top", "6mm", "--margin-bottom", "6mm",
            "--margin-left", "7mm", "--margin-right", "7mm",
            "--background", "--quiet",
            pdf_html, pdf_path,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        os.remove(pdf_html)
        if r.returncode == 0:
            size_kb = os.path.getsize(pdf_path) // 1024
            print(f"   ✓ {pdf_path} ({size_kb}KB)")
        else:
            print(f"   ✗ wkhtmltopdf failed (rc {r.returncode})")
            print(f"     {r.stderr[-300:]}")
            print("     Install: sudo apt install wkhtmltopdf")

    print("\nDone!")


if __name__ == "__main__":
    main()
