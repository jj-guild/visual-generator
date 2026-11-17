# AGENTS.md — visual-generator

Instructions for AI coding agents working in this repository.

## What this repo is

A data-driven visual generator: **JSON + template + art + text
sections**. Any game can use it for match announcements, annotated
world maps, merchant shops, entity cards or kingdom sheets. The
long-term goal is a pip-installable library (see the `lib` issue) —
keep the engine and templates project-agnostic; game specifics
belong in the JSON data files of the consuming project, never here.

## Non-negotiable rules

1. **The image model never renders text.** All visible words are drawn
   by the engine from the JSON with a real vector font. This is the
   only way to guarantee correct text, and it is what makes every
   output OCR-verifiable.
2. **Every rendered output must pass the OCR check** (`visual_generator/ocr.py`,
   CLI `vg-ocr-check`) before it
   is committed or delivered. The check is fail-closed.
3. **Data is the source of truth.** To change a visual, edit the JSON
   and re-render. Never edit a rendered image.
4. **Templates own the layout.** Zone positions are fixed canvas
   fractions; art is center-cropped into its window and must never
   shift text zones. If a text box moves depending on the art, the
   template is wrong — fix the template.
5. **Assets are content.** The JSON references the real game assets
   (crests, map thumbnails, civilization icons). The renderer places
   what it is given; it never invents or substitutes assets.
6. **Maps need geographic care.** Before pinning regions on a
   `world_map`, inspect the map art and place each territory on
   actual land at its geographic position. Pins in the ocean are a
   defect.
7. **Art URLs from image generation expire (~1 h).** Download
   immediately; deliver via committed files (raw GitHub URLs), never
   via generated links or sandbox paths.
8. **No game-specific content.** Names, brands, crests and lore of a
   concrete game live in that game's repository. This repo ships
   neutral examples only (`visual_generator/demo_assets.py` generates the
   demo art procedurally, without any image model).

## Workflow

1. Write/extend the JSON in `data/` (schema in the template docstring).
2. Render: `vg-render --data data/<name>.json`
   (from a repo checkout: `python -m visual_generator.engine --data …`).
3. Validate: `vg-ocr-check --data data/<name>.json`
   (or `python -m visual_generator.ocr --data …`), plus a visual
   check for layout defects.
4. Commit JSON + art + rendered output together, with a message
   naming the template.

## Adding a template

- One module per visual kind in `visual_generator/templates/`,
  exposing `render(data, fonts)`, `DEFAULT_PALETTE` (palette keys
  documented, hex overrides allowed from the JSON `palette` key) and
  a declared `STRUCTURE` — canvas dimensions (Discord embed target:
  under 600 px wide) and the named image/text zones the consumer
  fills. The structure is the layout contract; the consumer
  integrates the data, the template owns the geometry.
- Document the JSON schema in the module docstring, with a working
  example.
- `visual_generator/engine.py` injects `resolve_palette` into the
  template module — templates never import the engine.
- Ship a `data/` example, add it to the test suite, and validate its
  rendering by OCR.
- Keep assets small: example images ≤ ~300 KB, meaningful names.

## Style

Fail-closed everywhere: unknown template, missing section field,
unreadable art, missing fonts, non-fitting poster content — all abort
with a non-zero exit and an explicit message.
