"""visual-generator — data-driven visual generator.

A **visual** is a JSON document rendered by a **template** (a Python
layout module). The JSON always carries:

- ``template``   — template name; selects ``templates/<name>.py``
- ``output``     — output image path
- ``canvas``     — optional: ``{"width": int, "height": int}``
- ``palette``    — optional: dict of color overrides (hex strings)
- ``art``        — optional: path(s) to generated art (no text)
- ``sections``   — the content; schema defined per template

Each template also declares its **structure** — the canvas dimensions
(every default canvas targets Discord embeds: under 600 px wide) and
the named image/text zones the consumer fills — via
``template_structure(name)``.

Public API (the contract consumed by integrations)::

    from visual_generator import (
        render_visual,       # render an in-memory visual dict
        render_file,         # render a JSON file
        check_visual,        # OCR-validate a rendered visual (fail-closed)
        check_file,          # OCR-validate from the JSON file path
        load_fonts,          # DejaVu Serif font lookup (used by templates)
        list_templates,      # available template names
        template_structure,  # declared canvas + zones of a template
    )

Every word on a visual is drawn by the engine with a real vector font
(the image model never renders text), which makes every output
OCR-verifiable via ``check_visual``.
"""
from visual_generator.engine import load_fonts, render_file, render_visual
from visual_generator.ocr import check_file, check_visual, collect_strings
from visual_generator.templates import list_templates, template_structure

__version__ = "0.1.0"

__all__ = [
    "check_file",
    "check_visual",
    "collect_strings",
    "list_templates",
    "load_fonts",
    "render_file",
    "render_visual",
    "template_structure",
    "__version__",
]
