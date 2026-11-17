"""Available layout templates (one module per visual kind).

A template module exposes ``render(data, fonts)`` and
``DEFAULT_PALETTE`` and documents its JSON schema in its docstring.
"""
from __future__ import annotations

import os

TEMPLATE_DIR = os.path.dirname(os.path.abspath(__file__))
_EXCLUDE = {"__init__.py"}


def list_templates() -> list[str]:
    """Sorted names of the available templates (usable as ``template``)."""
    return sorted(
        f[:-3] for f in os.listdir(TEMPLATE_DIR)
        if f.endswith(".py") and f not in _EXCLUDE
    )
