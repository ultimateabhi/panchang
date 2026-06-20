#!/usr/bin/env python3
"""CLI: generate the Panchang desk calendar (multi-page PDF + per-page 300-DPI PNGs).

Usage:
    python generate.py                      # full build from config/vs2083.yaml → out/
    python generate.py --months 2           # cover + first 2 months (quick preview)
    python generate.py --png-only           # skip the PDF
    python generate.py --config my.yaml --outdir build
"""
from __future__ import annotations
import argparse
import time
from pathlib import Path

from panchang.config import load_config
from panchang.render import render_all

HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG = HERE / "config" / "vs2083.yaml"
DEFAULT_OUTDIR = HERE / "out"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Generate the Panchang desk calendar.")
    ap.add_argument("--config", default=str(DEFAULT_CONFIG))
    ap.add_argument("--outdir", default=str(DEFAULT_OUTDIR))
    ap.add_argument("--png-only", action="store_true", help="Skip PDF generation")
    ap.add_argument("--pdf-only", action="store_true", help="Skip PNG generation")
    ap.add_argument("--months", type=int, default=0,
                    help="Render only the first N months (preview); 0 = all")
    args = ap.parse_args(argv)

    if args.png_only and args.pdf_only:
        ap.error("--png-only and --pdf-only are mutually exclusive")
    if args.months < 0:
        ap.error("--months must be >= 0")

    t0 = time.time()
    cal = load_config(args.config)
    if args.months > 0:
        cal.months = cal.months[:args.months]
    png = not args.pdf_only
    pdf = not args.png_only

    print(f"Panchang calendar: {cal.page_count} pages "
          f"(cover + {len(cal.months)} months)")
    merged, pngs = render_all(cal, args.outdir, png=png, pdf=pdf)
    if pdf:
        print(f"  PDF : {merged}")
    if png:
        print(f"  PNGs: {len(pngs)} → {Path(args.outdir) / 'pages'}")
    print(f"Done in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
