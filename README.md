# visual-generator

A generic, data-driven visual generator: **JSON + template + art + text
sections**. Any visual — TCG card, match announcement, gallery,
annotated world map, parchment rules poster — is defined by:

- a **JSON data file** — the content (names, texts, numbers, image paths);
- a **template** — a Python layout module;
- **art** — image-model generated pictures (or real game assets),
  never carrying text;
- **text sections** — drawn by the engine with a real vector font,
  which makes every output OCR-verifiable.

The engine and templates are project-agnostic: all game-specific
content lives in the JSON data files of the consuming project.

## Install

```bash
pip install visual-generator        # or: uv add visual-generator
```

- Runtime dependency: **Pillow only**.
- **Fonts**: the engine draws with DejaVu Serif. It auto-locates the
  system fonts (e.g. `fonts-dejavu` on Debian/Ubuntu) or the
  [matplotlib](https://pypi.org/project/matplotlib/) bundle — install
  the light extra if your system has neither:
  `pip install "visual-generator[fonts]"`. `--font-dir` overrides.
- **OCR check** (recommended, optional): requires
  [tesseract](https://github.com/tesseract-ocr/tesseract) with the
  `fra` and `eng` languages (`apt-get install tesseract-ocr
  tesseract-ocr-fra`).

## Quick start

A visual is one JSON file. The `template` key selects the layout;
`sections` carries the content (schema per template below).

```json
{
  "template": "match_announcement",
  "output": "out/match.jpg",
  "art": "assets/battle.jpg",
  "sections": {
    "left_name": "Lion House",
    "left_crest": "assets/crest_lion.png",
    "right_name": "Stag House",
    "right_crest": "assets/crest_stag.png",
    "map_art": "assets/terr_golden-coast.jpg",
    "map_name": "Golden Coast",
    "vs": "VS",
    "context_line": "Season attack — Cycle 3",
    "sub_line": "Sunday 23:30 · Season II",
    "footer": "Demo Game"
  }
}
```

Render and validate (fail-closed: non-zero exit on any defect):

```bash
vg-render --data out/match.json
vg-ocr-check --data out/match.json
```

Or from Python:

```python
from visual_generator import render_file, check_file

render_file("out/match.json")
assert check_file("out/match.json") == []   # missing strings, if any
```

## Public API

`visual_generator` — the stable surface consumed by integrations
(BotForge and friends). Breaking changes before 1.0 go through a 0.x
bump (SemVer).

| Name | Signature | Purpose |
|---|---|---|
| `render_visual` | `(data: dict, font_dir: str \| None = None, out: str \| None = None) -> str` | Render an in-memory visual dict; returns the output path |
| `render_file` | `(path: str, font_dir=None, out=None) -> str` | Same, from a JSON file |
| `check_visual` | `(data: dict, transcript: str \| None = None) -> list[str]` | Expected strings missing from the OCR transcript of `data["output"]` (empty = pass) |
| `check_file` | `(path: str) -> list[str]` | Same, from the JSON file |
| `collect_strings` | `(obj) -> list[str]` | Every string the JSON contributes to the visual's text |
| `load_fonts` | `(font_dir: str \| None = None) -> dict` | DejaVu Serif font paths (`b`/`r`/`i`), used by templates |
| `list_templates` | `() -> list[str]` | Available template names |

CLIs (same fail-closed contract): `vg-render`, `vg-ocr-check`,
`vg-demo-assets` (regenerates the neutral demo art procedurally).

## The one hard rule

**The image model never renders text.** Image models produce
convincing-looking but misspelled pseudo-text. Every word on a visual
is drawn by the engine from the JSON — the only way to guarantee
correct text and prove it by OCR.

## Templates and data schemas

Every visual JSON carries `template`, `output`, and optionally
`canvas` (`{"width", "height"}`), `palette` (hex overrides of the
template's documented palette keys), `art` (path(s) to text-free
art). `sections` is the template's content, schemas below — this is
the contract consuming projects write into their JSON. Art paths are
relative to the working directory of the render call.

### `card_tcg` — TCG card

![TCG card — Ambush](examples/card_ambush.jpg)

Fixed anatomy (name banner / art window / type line / rule box /
extra box / footer as fixed canvas fractions — the art never shifts
text zones). `cost`: int = N gear icons, string = round text badge.

```json
{ "sections": {
    "name": "Ambush", "cost": 2,
    "art": "assets/card_art.jpg",
    "type_line": "Special action — Technology",
    "rule": "One extra attack this cycle.\nSecond paragraph.",
    "extra_label": "Linked condition:", "extra_value": "Wolves",
    "footer_left": "1/10", "footer_right": "Demo Game" } }
```

### `entity_card` — one entity's sheet

![Entity card — Northern Keep](examples/entity_territory.jpg)

Collector-card anatomy: name banner + badge, art window over a
translucent backdrop, parchment plates (heads + lines), optional
linked-value box. The civilization / map / player card case.

```json
{ "art": "assets/entity_art.jpg", "backdrop": "assets/scene.jpg", "badge": "r3",
  "sections": {
    "title": "Northern Keep", "type_line": "Defensive territory",
    "plates": [ { "head": "Territory bonus",
                  "lines": ["Buildings +10/20/30/40 % HP per cycle", "…"] } ],
    "extra_label": "Grants civilization", "extra_value": "Wolves",
    "footer_left": "demo:territory:northern-keep", "footer_right": "Demo Game" } }
```

### `match_announcement` — X-vs-Y banner

![Match announcement — Lion House vs Stag House](examples/match_lion_vs_stag.jpg)

Discord-sized (1200×675): large crests centered per side, names below,
attacker's civ icons (max 3) under the name, battle-map medallion in
the center, VS badge, context band. Dim battle backdrop via the
top-level `art` key.

```json
{ "art": "assets/battle.jpg", "sections": {
    "left_name": "Lion House", "left_crest": "assets/crest_lion.png",
    "left_civs": ["assets/civ_red.png", "assets/civ_green.png"],
    "right_name": "Stag House", "right_crest": "assets/crest_stag.png",
    "map_art": "assets/terr_golden-coast.jpg", "map_name": "Golden Coast",
    "vs": "VS", "context_line": "Season attack — Cycle 3",
    "sub_line": "Sunday 23:30 · Season II", "footer": "Demo Game" } }
```

### `gallery` — titled grid of art + captions

![Gallery — territories](examples/gallery_territories.jpg)

```json
{ "sections": {
    "title": "DEMO GAME — Territories",
    "item_width": 400, "item_height": 500, "columns": 4, "gap": 24,
    "items": [ { "art": "assets/terr_twin-lakes.jpg",
                 "caption": "Twin Lakes", "sub": "Grants the Otters civilization" } ] } }
```

### `world_map` — annotated map with geo-placed pins

![World map — regions pinned at geographic positions](examples/world_map_regions.jpg)

Real map art background, one label plate per territory, readable over
busy art. `x`/`y` are pixel coordinates on the 1600×1200 canvas
(title band: top 100 px). **Place regions on actual land** — inspect
the map art first; pins in the ocean are a defect.

```json
{ "art": "assets/world_map_art.jpg", "sections": {
    "title": "THE WORLD — WEEK 3", "footer": "Demo Game — Season II",
    "regions": [ { "name": "Black Forest", "x": 680, "y": 240,
                   "color": "#5c8a4e", "note": "Elks · Lion" } ] } }
```

### `parchment_poster` — rules poster on parchment

![Parchment rules poster](examples/rules_poster.jpg)

Parchment texture background (`art`), titled, auto-fitted
multi-column rules text; fail-closed when the content cannot fit.

```json
{ "art": "assets/parchment.jpg", "sections": {
    "title": "THE RULES OF THE GAME", "subtitle": "Demo Game — Season II",
    "footer": "— As it is written, so shall it be played —",
    "source_line": "Source : docs/rules", "columns": 2,
    "sections": [ { "head": "Territories",
                    "body": "Each territory is a map.\nSecond paragraph." } ] } }
```

### `contact_sheet` — N card visuals side by side

![Contact sheet — technologies](examples/sheet_ambush.jpg)

Re-renders each card (same data as the individual visuals) onto a
titled dark sheet, aspect kept. Each entry of `cards` is a full
visual definition (minus `template` and `output`) rendered by
`card_template` at a reduced size.

```json
{ "sections": {
    "title": "DEMO GAME — Technologies", "columns": 5,
    "card_template": "card_tcg",
    "cards": [ { "canvas": {"width": 744, "height": 1032},
                 "sections": { "…card_tcg schema…": "…" } } ] } }
```

Each template also documents its schema in its module docstring
(`visual_generator/templates/<name>.py`), and every `data/*.json` in
this repo is a working example.

## Agent skill

This repository ships the canonical agent skill for the library:
[`.agents/skills/visual-generator/SKILL.md`](.agents/skills/visual-generator/SKILL.md)
(plus its [`scripts/render_and_check.py`](.agents/skills/visual-generator/scripts/render_and_check.py)
batch helper). Any project using the library should point its agents
at that skill: it documents the install, the CLIs, the per-template
JSON schemas, the OCR validation contract and the known pitfalls —
everything needed to reproduce the reference rendering.

## Principles

1. **The image model never renders text** (see above).
2. **Data is the source of truth** — edit the JSON, re-render, never
   edit the image.
3. **Templates own the layout** — zone positions are fixed fractions
   of the canvas; art is center-cropped into its window and never
   shifts the text zones.
4. **Every output must pass OCR** before delivery.
5. **Assets are content, not decoration** — the JSON references the
   real game assets (crests, map thumbnails, civilization icons); the
   renderer places them, it never invents them.

## Versioning and publishing

Version **0.1.0** — the first publiable release. SemVer applies: the
public API is young, breaking changes before 1.0 go through a 0.x
bump.

Releases are published by the repo owner: pushing a `v*` tag (or
dispatching the workflow manually) triggers
[`.github/workflows/publish.yml`](.github/workflows/publish.yml):
`uv build` → `twine check` → publish to PyPI with the `PYPI_TOKEN`
secret. Nothing is published without that secret being set by the
owner.

## Project layout

```
├── AGENTS.md               ← agent instructions (rules, workflow)
├── .agents/skills/         ← agent skill (visual generation pipeline)
├── visual_generator/      ← the pip-installable package
│   ├── engine.py           ← core renderer (templates, palettes, fonts)
│   ├── ocr.py              ← OCR validation (fail-closed, importable)
│   ├── demo_assets.py      ← procedural demo art (no text, no model)
│   └── templates/          ← one layout module per visual kind
├── tests/                  ← render + OCR suite (runs in CI)
├── data/                   ← JSON examples (source of truth per visual)
└── examples/               ← rendered outputs + their assets
```

License: MIT.
