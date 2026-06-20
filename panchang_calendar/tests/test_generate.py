import sys
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parent.parent


def _main():
    sys.path.insert(0, str(ROOT))
    return importlib.import_module("generate").main


def test_cli_preview_png_only(tmp_path):
    main = _main()
    main(["--months", "1", "--png-only", "--outdir", str(tmp_path)])
    pages = sorted((tmp_path / "pages").glob("*.png"))
    assert [p.name for p in pages] == ["00_cover.png", "01_chaitra.png"]
    assert not (tmp_path / "calendar.pdf").exists()    # --png-only
