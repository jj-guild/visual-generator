---
name: visual-generator
description: Render game visuals (match announcements, annotated world maps, merchant shops, entity cards, kingdom sheets) from JSON data + templates + art, with OCR-verified text. Use whenever a game designer asks for announcement banners, shop posts, entity sheets, realm overviews, or any branded image.
---

# Visual generation (visual-generator)

**Repository**: https://github.com/jj-guild/visual-generator

The repo is the source of truth: engine, templates, JSON data schemas,
examples, this skill and its companion instructions (`AGENTS.md`).

## The one hard rule

**The image model never renders text.** It produces convincing-looking
but misspelled pseudo-text. All text is drawn by the engine from the
JSON with a real vector font — that is what makes the output provable
by OCR. Never "save time" by asking the image model to write words.

## Install

The library is pip/uv-installable and exposes three CLIs:

```bash
uv pip install visual-generator        # or: pip install visual-generator
```

- `vg-render --data <visual.json>` — render one visual
- `vg-ocr-check --data <visual.json>` — fail-closed OCR validation
- `vg-demo-assets` — regenerate the demo art into `examples/assets/`

In a project managed by uv, add the dependency and sync:

```bash
uv add visual-generator
uv sync
uv run vg-render --data docs/visuals/data/<name>.json
```

Runtime dependency: `pillow` only. Fonts auto-locate DejaVu Serif
(system `fonts-dejavu`, or the matplotlib bundle via the optional
`fonts` extra: `pip install "visual-generator[fonts]"`);
`--font-dir` overrides.

## Pipeline (per visual)

1. **Data** — write `<name>.json` following the template's schema
   (documented in the template module docstring; live examples in the
   library `data/` directory). The JSON references real game assets
   (crests, map thumbnails, civ icons) — assets are content, the
   renderer only places them. Art paths are repo-relative, never
   sandbox paths.
2. **Art** — for art the game does not already provide, one
   image-generation call per visual, always with: `NO text, NO
   letters, NO words anywhere`. For maps: also demand region shapes
   you can pin territories onto, and **inspect the generated art
   before placing pins** — territories must sit on actual land.
3. **Download the art immediately** — generated URLs expire (~1 h).
   Never share an expired link or a sandbox path with the user:
   deliver through committed files (raw GitHub URLs).
4. **Render** — `vg-render --data <name>.json` (or `python -m
   visual_generator.engine --data …` from a repo checkout). The
   `template` key selects the layout module.
5. **Validate — mandatory.** `vg-ocr-check --data <name>.json`
   (fail-closed: non-zero exit if any expected string is missing from
   the OCR transcript; requires tesseract + `fra`). In sandboxes
   without tesseract, `OCR_CHECK_ALLOW_MISSING_TESSERACT=1` downgrades
   to a skip warning — then OCR every image with another available
   engine before delivery. Complete with a visual check for layout
   defects (cropped/overlapping text, pins in the ocean, cost icons
   legible).
6. **Commit** the JSON, the art and the rendered output together, with
   a message naming the template.

## Templates

All templates target Discord embeds: default canvases are under
600 px wide, and each module declares its `STRUCTURE` — the canvas
dimensions and the named image/text zones the consumer fills
(inspect via `template_structure(name)`).

- `match_announcement` — 576×324. Two players: round avatar
  medallions + pseudos, battle-map medallion in the center, VS
  badge, bottom band for tournament / settings / time. Dim battle
  backdrop via the top-level `art` key. Pseudos ≈ 14 chars max.
- `world_map` — 576×432. Real map art background with geo-placed
  region spots: colored pin, or round crest spot when `icon` is
  set (`x`/`y` px on the canvas; parchment plates stay readable
  over busy art).
- `merchant` — 576×384. Product sheets side by side: art window,
  name, short description, price on a gold band. `columns` ≤ 4.
- `entity_card` — 576×800 (scales with `canvas`). One entity's
  sheet, collector-card style: name banner + badge, art window over
  a translucent backdrop, parchment plates (heads + lines),
  optional linked-value box. The territory / civ / player card case.
- `kingdom` — 576×324. Castle scene background (`art`, veiled),
  kingdom name, centered row of owned-territory icons (optional
  caption each), ruler line in the bottom band. Up to 8 icons.

New template? Copy an existing one, keep the contract: `render(data,
fonts)` + `DEFAULT_PALETTE` + `STRUCTURE` (canvas < 600 px wide,
zones inside the canvas), document the JSON schema in the
docstring, ship a `data/` example and validate it by OCR.

## Known pitfalls (all learned the hard way)

- Image-model text is gibberish — see the hard rule.
- Art URLs expire (~1 h) — download immediately.
- Pins placed without inspecting the map art end up in the ocean —
  always check the generated map first.
- Text over busy art fails OCR — flatten a plate behind it (see the
  world_map / merchant templates).
- Sandbox paths in JSON break re-rendering — art paths are always
  repo-relative.
- Binary assets in git: keep example assets small (≤ ~300 KB each)
  and meaningful names (`crest_lion.png`, not `Gr508B4g-lion.png`).
