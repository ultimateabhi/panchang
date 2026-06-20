from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parent.parent


def test_package_imports():
    assert importlib.import_module("panchang") is not None


def test_assets_present():
    imgs = sorted((ROOT / "assets" / "images").glob("*.jpg"))
    assert len(imgs) == 13, f"expected 13 month photos, found {len(imgs)}"


def test_fonts_present():
    for name in ("NotoSansDevanagari.ttf", "NotoSerif.ttf", "CormorantGaramond.ttf"):
        f = ROOT / "fonts" / name
        assert f.exists() and f.stat().st_size > 0, f"missing/empty font: {name}"
