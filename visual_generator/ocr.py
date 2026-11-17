#!/usr/bin/env python3
"""OCR validation: compare a rendered image against its JSON source.

Every visual must pass this check before delivery (README, principle 4).
Requires tesseract (``tesseract-ocr`` package) with the ``fra`` and
``eng`` languages — an optional system dependency of the library.

Usage (CLI)::

    vg-ocr-check --data data/match.json

Usage (library)::

    from visual_generator import check_file, check_visual
    missing = check_visual(data)   # list of expected strings not found

Collects every string the JSON contributes to the visual (name,
lines, captions, region notes…), runs tesseract over the rendered
image, and reports each expected string that the transcript does not
contain (case- and accent-insensitive). Fail-closed: the CLI exits
non-zero when a string is missing.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import unicodedata

_SKIP_KEYS = ("art", "left_crest", "right_crest", "map_art",
              "left_civs", "left_avatar", "right_avatar",
              "icon", "x", "y", "color")


def norm(s: str) -> str:
    """Case- and accent-insensitive comparison form."""
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def collect_strings(obj) -> list[str]:
    """Every string the JSON contributes to the visible text of the visual."""
    out = []
    if isinstance(obj, str):
        if len(obj) > 2 and not obj.startswith(("#", "path/")):
            out.append(obj)
    elif isinstance(obj, list):
        for v in obj:
            out += collect_strings(v)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k in _SKIP_KEYS:
                continue
            out += collect_strings(v)
    return out


def ocr(path: str) -> str | None:
    """Tesseract transcript of the image, or None when unavailable.

    Unavailable tesseract is fatal unless the caller opted out via
    ``OCR_CHECK_ALLOW_MISSING_TESSERACT=1`` (dev sandboxes only).
    """
    try:
        r = subprocess.run(
            ["tesseract", path, "stdout", "-l", "fra+eng"],
            capture_output=True, text=True, timeout=120)
        return r.stdout
    except FileNotFoundError:
        if os.environ.get("OCR_CHECK_ALLOW_MISSING_TESSERACT") == "1":
            print("warn: tesseract not found, OCR check skipped (dev sandbox only)")
            return None
        sys.exit("tesseract not found: apt-get install tesseract-ocr tesseract-ocr-fra")


def check_visual(data: dict, transcript: str | None = None) -> list[str]:
    """Expected strings missing from the OCR transcript of a rendered visual.

    ``data`` is the visual dict (its ``output`` key is the rendered
    image). Returns the missing strings — empty when the visual passes.
    """
    expected = collect_strings(data.get("sections", {}))
    raw = transcript if transcript is not None else ocr(data["output"])
    if raw is None:
        return []
    text = norm(raw)
    return [s for s in expected if norm(s) not in text]


def check_file(path: str) -> list[str]:
    """``check_visual`` from the JSON visual definition at ``path``."""
    with open(path, encoding="utf-8") as fh:
        return check_visual(json.load(fh))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True)
    args = p.parse_args()
    with open(args.data, encoding="utf-8") as fh:
        data = json.load(fh)
    raw = ocr(data["output"])
    if raw is None:
        return
    missing = check_visual(data, transcript=raw)
    for s in missing:
        print(f"MISSING: {s!r}")
    if missing:
        sys.exit(f"{len(missing)} expected string(s) not found in OCR transcript")
    print(f"ok: all strings found in {data['output']}")


if __name__ == "__main__":
    main()
