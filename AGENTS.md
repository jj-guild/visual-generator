# AGENTS.md — visual-generator

Instructions for AI coding agents working in this repository.

## What this repo is

A data-driven visual generator: **JSON + template + art + text
sections**. Any game can use it for TCG cards, match announcements,
galleries, annotated world maps or parchment rules posters. The
long-term goal is a pip-installable library (see the `lib` issue) —
keep the engine and templates project-agnostic; game specifics
belong in the JSON data files of the consuming project, never here.

## Non-negotiable rules

1. **The image model never renders text.** All visible words are drawn
   by the engine from the JSON with a real vector font. This is the
   only way to guarantee correct text, and it is what makes every
   output OCR-verifiable.
2. **Every rendered output must pass `tools/ocr_check.py`** before it
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
   neutral examples only (`tools/make_demo_assets.py` generates the
   demo art procedurally, without any image model).

## Workflow

1. Write/extend the JSON in `data/` (schema in the template docstring).
2. Render: `python engine/render.py --data data/<name>.json`.
3. Validate: `python tools/ocr_check.py --data data/<name>.json`, plus
   a visual check for layout defects.
4. Commit JSON + art + rendered output together, with a message
   naming the template.

## Adding a template

- One module per visual kind in `templates/`, exposing
  `render(data, fonts)` and `DEFAULT_PALETTE` (palette keys documented,
  hex overrides allowed from the JSON `palette` key).
- Document the JSON schema in the module docstring, with a working
  example.
- `engine/render.py` injects `resolve_palette` into the template
  module — templates never import the engine.
- Ship a `data/` example and validate its rendering by OCR.
- Keep assets small: example images ≤ ~300 KB, meaningful names.

## Avatars (character + background pipeline)

Avatars do not go through the JSON/template engine: they are a
dedicated, element-based pipeline — `engine/avatar.py` (core) and
`tools/make_avatar.py` (light CLI). Full agent instructions live in
[`.agents/skills/avatar/SKILL.md`](.agents/skills/avatar/SKILL.md);
the non-negotiables:

1. **Elements are generated once, never edited.** If a criterion
   fails (wrong face, missing arm, bad mic), regenerate the raw
   element. Never retouch a generated render — no inpainting, no
   clone patch, no pixel surgery. Compositing (crop, scale, position,
   blur) is the only allowed transformation.
2. **`examples/character/<Name>/raw.png`** — full body, empty hands,
   **flat uniform background** (the crop depends on it), thin parts
   separated from the body (arms, headset interstices), kept at max
   quality.
3. **`examples/scene/<name>/raw.png`** — sharp scene, **center
   uncluttered**, no readable text, no logos, ≥ 1024 px. The prepared
   background (square crop + blur, `background.png`) must stay
   readable: a backdrop, not a wash.
4. **Ask, never assume, the missing constraints**: final aspect and
   size, avatar file size bound — per-request, no universal default.
   The avatar lands in `examples/avatar/<Name>.png` (JPEG fallback
   under the bound, at the highest fitting quality).
5. **Framing is anchor-driven**: 15% headroom, nameplate anchor at
   85%, centering on the anchor (never the arms), body cut flush by
   the bottom edge. All encoded in the CLI defaults.
6. **The pipeline is fail-closed**: undetected anchor, unreadable
   art, avatar over the size bound — all abort. Deliver only what
   passed the QA checklist from the avatar skill.

## Style

Fail-closed everywhere: unknown template, missing section field,
unreadable art, missing fonts, non-fitting poster content — all abort
with a non-zero exit and an explicit message.
