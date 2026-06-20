import textwrap
from pathlib import Path
import pytest
from panchang.config import load_config, ConfigError

VALID = textwrap.dedent("""\
calendar:
  samvat: 2083
  reckoning: purnimanta
  gregorian_span: "span"
  cover: {title: "Vikram Samvat", subtitle: "s", note: "n"}
theme:
  page: {width_in: 10, height_in: 3.5, dpi: 300, top_safe_mm: 8, calendar_pct: 42}
  fonts: {devanagari: "Noto Sans Devanagari", serif: "Noto Serif", quote: "Cormorant Garamond"}
  ritu:
    vasanta: {accent: "#4E8B3A", shukla: "#e8f2e2", krishna: "#d2e4c8"}
months:
  - name_dev: "चैत्र"
    name_rom: "Chaitra"
    ritu: vasanta
    season_label: "Vasanta (spring)"
    start: 2026-03-04
    amavasya: 2026-03-18
    end: 2026-04-02
    photo: photo.jpg
    quote: {text: "Q", attribution: "Sadhguru"}
    festivals:
      - {tithi: "S1", label: "Gudi Padwa"}
      - {date: 2026-03-20, label: "Fixed"}
""")


def _write(tmp_path, body):
    (tmp_path / "photo.jpg").write_bytes(b"\xff\xd8\xff")   # dummy jpeg bytes
    p = tmp_path / "c.yaml"
    p.write_text(body, encoding="utf-8")
    return p


def test_loads_valid_config(tmp_path):
    cal = load_config(_write(tmp_path, VALID))
    assert cal.samvat == 2083
    assert cal.page_count == 2
    m = cal.months[0]
    assert m.name_rom == "Chaitra" and m.index == 1
    assert m.festivals[0].tithi == "S1"
    assert m.photo.endswith("photo.jpg") and Path(m.photo).is_absolute()


def test_missing_required_field(tmp_path):
    bad = VALID.replace('    name_rom: "Chaitra"\n', "")
    with pytest.raises(ConfigError, match="name_rom"):
        load_config(_write(tmp_path, bad))


def test_amavasya_out_of_range(tmp_path):
    bad = VALID.replace("amavasya: 2026-03-18", "amavasya: 2026-04-10")
    with pytest.raises(ConfigError, match="amavasya"):
        load_config(_write(tmp_path, bad))


def test_unknown_ritu(tmp_path):
    bad = VALID.replace("ritu: vasanta", "ritu: monsoon")
    with pytest.raises(ConfigError, match="ritu"):
        load_config(_write(tmp_path, bad))


def test_missing_photo(tmp_path):
    p = tmp_path / "c.yaml"
    p.write_text(VALID, encoding="utf-8")          # note: no photo.jpg written
    with pytest.raises(ConfigError, match="photo"):
        load_config(p)
