"""Available layout templates (one module per visual kind).

A template module exposes:

- ``render(data, fonts)`` — draws the visual from the JSON data;
- ``DEFAULT_PALETTE`` — base palette (hex overrides from the JSON
  ``palette`` key);
- ``STRUCTURE`` — the declared image structure: the canvas dimensions
  and the named zones (image or text) where the consumer integrates
  its data. This is the layout contract: the consumer fills the
  zones, the template owns the geometry.

The module docstring documents the JSON schema.
"""
from __future__ import annotations

import importlib.util
import os
import sys

TEMPLATE_DIR = os.path.dirname(os.path.abspath(__file__))
_EXCLUDE = {"__init__.py"}


def list_templates() -> list[str]:
    """Sorted names of the available templates (usable as ``template``)."""
    return sorted(
        f[:-3] for f in os.listdir(TEMPLATE_DIR)
        if f.endswith(".py") and f not in _EXCLUDE
    )


def import_template(name: str):
    """Load a template module; fail-closed when absent or invalid."""
    path = os.path.join(TEMPLATE_DIR, f"{name}.py")
    if not os.path.isfile(path):
        sys.exit(f"unknown template: {name!r} (expected {path})")
    spec = importlib.util.spec_from_file_location(f"template_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    missing = [attr for attr in ("render", "DEFAULT_PALETTE", "STRUCTURE")
               if not hasattr(module, attr)]
    if missing:
        sys.exit(f"template {name!r} is missing {', '.join(missing)}")
    return module


def template_structure(name: str) -> dict:
    """The declared structure of a template (canvas + zones).

    ``{"canvas": {"width": int, "height": int}, "target": str,
    "zones": {name: {"kind": "image"|"text", "rect": [x0, y0, x1, y1],
    "note": str}}}`` — the geometry contract the consumer integrates
    its data into.
    """
    return import_template(name).STRUCTURE
