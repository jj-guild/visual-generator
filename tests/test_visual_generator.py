"""Test suite: public API + every template renders its example + OCR check.

The OCR check is the anti-regression guard for each template's text
layout (AGENTS.md, rule 2). It requires tesseract; where tesseract is
unavailable (bare dev sandbox) the OCR part is skipped — CI runs it.
"""
from __future__ import annotations

import json
import os
import shutil
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
HAS_TESSERACT = shutil.which("tesseract") is not None

sys.path.insert(0, ROOT)

from visual_generator import (  # noqa: E402
    __version__,
    check_visual,
    collect_strings,
    list_templates,
    load_fonts,
    render_file,
    render_visual,
    template_structure,
)

EXAMPLES = sorted(
    f for f in os.listdir(DATA_DIR)
    if f.endswith(".json") and not f.startswith("_")
)


@pytest.fixture(autouse=True)
def repo_root_cwd(monkeypatch):
    """Art paths in the example JSONs are repo-relative."""
    monkeypatch.chdir(ROOT)


def test_public_api_surface():
    assert __version__ == "0.1.0"
    assert callable(render_visual)
    assert callable(render_file)
    assert callable(check_visual)
    assert callable(load_fonts)


def test_list_templates():
    assert list_templates() == [
        "entity_card",
        "kingdom",
        "match_announcement",
        "merchant",
        "world_map",
    ]


def test_template_structure_contract():
    """Every template declares a canvas under 600 px wide (Discord
    embed target) and zones inside the canvas."""
    for name in list_templates():
        st = template_structure(name)
        w, h = st["canvas"]["width"], st["canvas"]["height"]
        assert w < 600, name
        assert st["target"] == "discord-embed", name
        assert st["zones"], name
        for zone, spec in st["zones"].items():
            assert spec["kind"] in ("image", "text", "image+text"), (name, zone)
            x0, y0, x1, y1 = spec["rect"]
            assert 0 <= x0 < x1 <= w and 0 <= y0 < y1 <= h, (name, zone)


def test_every_example_has_a_known_template():
    for name in EXAMPLES:
        with open(os.path.join(DATA_DIR, name), encoding="utf-8") as fh:
            assert json.load(fh)["template"] in list_templates(), name


@pytest.mark.parametrize("name", EXAMPLES)
def test_render_example(name, tmp_path):
    out = str(tmp_path / f"{name[:-5]}.jpg")
    assert render_file(os.path.join("data", name), out=out) == out
    assert os.path.isfile(out) and os.path.getsize(out) > 10_000


@pytest.mark.parametrize("name", EXAMPLES)
@pytest.mark.skipif(not HAS_TESSERACT, reason="tesseract not installed (runs in CI)")
def test_ocr_example(name, tmp_path):
    out = str(tmp_path / f"{name[:-5]}.jpg")
    render_file(os.path.join("data", name), out=out)
    with open(os.path.join(DATA_DIR, name), encoding="utf-8") as fh:
        data = json.load(fh)
    missing = check_visual({**data, "output": out})
    assert missing == []


def test_collect_strings_skips_art_paths():
    data = {"name": "Ambush", "art": "examples/assets/battle.jpg",
            "left_avatar": "examples/assets/avatar.png",
            "regions": [{"name": "Black Forest", "x": 1, "y": 2,
                         "icon": "examples/assets/crest.png"}]}
    assert collect_strings(data) == ["Ambush", "Black Forest"]


def test_check_visual_reports_missing_strings():
    data = {"sections": {"name": "Ambush"}, "output": "unused.jpg"}
    assert check_visual(data, transcript="the card reads ambush here") == []
    assert check_visual(data, transcript="nothing relevant") == ["Ambush"]
