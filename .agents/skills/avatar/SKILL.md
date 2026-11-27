---
name: avatar
description: Compose square avatars (character + background) from generated art — generate the raw character and the sharp scene with the right criteria, then run the avatar pipeline (cutout, background blur, anchor-driven framing, size bound). Use whenever a user asks for an avatar, a profile picture, or a character-on-background composition.
---

# Avatar generation (avatar pipeline)

**Repository**: https://github.com/jj-guild/visual-generator

The pipeline turns two generated images into one avatar:

```
examples/character/<Name>/raw.png   (character on a flat uniform background)
examples/scene/<name>/raw.png       (sharp scene)
   ──►  tools/make_avatar.py  ──►  examples/avatar/<Name>.png|.jpg
```

It is element-based by doctrine: **each element is generated once,
never edited**. If a criterion fails, regenerate the element — never
retouch a generated render (no inpainting, no clone patch, no
pixel surgery). Compositing (crop, scale, position, blur) is the only
allowed transformation.

## File layout & naming (per-character / per-scene)

| Path | Meaning |
|---|---|
| `examples/character/<Name>/original.png` | identity reference, untouched |
| `examples/character/<Name>/raw.png` | generated render, untouched (flat background, full body) |
| `examples/character/<Name>/crop.png` | transparent character extraction |
| `examples/scene/<name>/raw.png` | generated sharp scene, untouched |
| `examples/scene/<name>/background.png` | prepared background: square crop + blur |
| `examples/avatar/<Name>.png` / `.jpg` | final: assembled, cropped, size-bound — profile-picture ready |
| `examples/character/<Name>/prompt.md` | generation prompt + blocking criteria |
| `examples/scene/<name>/prompt.md` | generation prompt + blocking criteria |
| `examples/avatar/prompt.md` | combination recipe (reference case) |

Candidates under selection are numbered in the same folder
(`raw_01.png`, `raw_02.png`, …) and removed once a candidate is chosen.

## Before generating — ask if absent

If the user does not specify, **ask** (never assume):

- the final **aspect and size** (default proposal: square, 896 px);
- the **size bound** of the avatar file — per-case constraint, there
  is NO universal default (proposal: < 1 MB); pass it with
  `--max-kb`; JPEG fallback compresses to fit before failing;
- whether the background is a generated scene or a user image.

Only the final avatar is size-bound. Raw assets are kept at maximum
quality — never downscale `raw.png` or the scene to save space.

## Generation criteria

### character `raw.png`

Full prompts live next to the assets (`examples/character/<Name>/prompt.md`) — every constraint is justified there. Skeleton (adapt, keep the constraints):

> Full-body 3D render of <character description> on a completely
> flat uniform plain light-gray studio background, centered, full
> figure visible head to feet, empty hands. <identity details>. Face:
> <eyes>, <mouth>, explicitly no nose if not wanted. Nothing held,
> nothing on the back.

Hard criteria, verified before moving on:

- **flat uniform background** — the cutout depends on it;
- **full body visible** (the pipeline crops, the render must not);
- **empty hands** unless the user explicitly asks for a held item;
- thin parts (arms, headset straps) clearly separated from the body
  so the cutout keeps the interstices;
- identity checks (zoom on the face) before any composition work.

### scene `raw.png` (the sharp scene)

Full prompts live next to the assets (`examples/scene/<name>/prompt.md`). Skeleton:

> <scene description>, center of the frame relatively uncluttered,
> no visible readable text, no logos. Natural photography look,
> sharp focus, high detail, action in the middle distance.

Hard criteria:

- **center uncluttered** — the avatar character lands dead center;
- **no readable text, no logos** (the model misspells text);
- **bright even ambient light, no visible light source** (no
  windows, no lamps in frame) — a dark scene sinks a dark
  character; ask the user before any `--brightness` correction;
- for crowd scenes: light-colored clothing, modern props, action
  everywhere (the blur keeps only silhouettes and glow);
- resolution ≥ 1024 px on the short side;
- the *scene must stay readable after the blur*: it is a backdrop,
  not a wash.

## Pipeline

```bash
# 1. background: square center-crop + Gaussian blur (never color-correct
#    the scene beyond the explicit --brightness the user asked for)
python tools/make_avatar.py bg \
    --src examples/scene/<name>/raw.png --out examples/scene/<name>/background.png --blur 4

# 2. crop: transparent character (rembg, alpha matting tuned for
#    thin arms and headset interstices)
python tools/make_avatar.py cutout \
    --src examples/character/<Name>/raw.png --out examples/character/<Name>/crop.png

# 3. (optional) verify the auto-detected anchor
python tools/make_avatar.py anchor --character examples/character/<Name>/crop.png

# 4. avatar: anchor-driven framing, cut flush at the bottom, size-bound
python tools/make_avatar.py compose --bg examples/scene/<name>/background.png \
    --character examples/character/<Name>/crop.png \
    --out examples/avatar/<Name>.png --max-kb <bound>
```

Agents doing programmatic work import the same core:

```python
from engine import avatar
avatar.prepare_background("scene/raw.png", "scene/background.png", blur=4)
avatar.cutout_character("character/raw.png", "character/crop.png")
anchor = avatar.detect_anchor("character/crop.png")   # (cx, bottom) fractions
avatar.build_avatar("scene/background.png", "character/crop.png", "avatar/Name.png",
                    max_bytes=1_000_000,  # per-request bound, ask the user
                    anchor=anchor)
```

### Framing rules (the defaults encode them)

| Rule | Default | Meaning |
|---|---|---|
| `--headroom` | 0.15 | 15% of the frame free above the head |
| `--plate-bottom` | 0.85 | the anchor (nameplate bottom) sits at 85% |
| anchor | auto | detected on the gold nameplate; centering follows it, **never the arms**. VERIFY the detection: glossy warm metal highlights can fool it — pass the measured fractions (`--anchor cx,bottom`) when it drifts |
| bottom edge | by construction | the body is cut flush, zero background gap |
| `--size` | 896 | square canvas |
| `--max-kb` | none | size bound in KiB — per-case, ask the user; PNG first, JPEG fallback under the bound (fail-closed) |

The anchor maps the head-to-plate span onto 70% of the frame height;
~15% of body stays visible below the plate, then the frame cuts it.

## QA before delivering (all fail-closed)

1. **Cutout**: render on a checkerboard — interstices transparent,
   no leftover background, no halo; thin limbs present (numeric check:
   multiple alpha segments at mid-torso height).
2. **Background**: square, blurred as requested, center readable.
3. **Avatar**: character top ≈ `headroom`, anchor at
   `plate_bottom`, alpha content down to the last canvas row (no
   bottom gap), background visible left and right.
4. **Size**: under the bound when one was requested — the pipeline
   refuses to deliver otherwise. PNG first; if the PNG exceeds the
   bound, the pipeline falls back to JPEG, binary-searching the
   HIGHEST quality that fits the bound (approaching the requested
   limit — a 1 MB bound must not yield a 50 KB file), which keeps
   gradients clean, unlike palette quantization.
5. Visual check of the face at full resolution: identity criteria
   (eyes, mouth, no unwanted features). If a criterion fails:
   **regenerate the raw element, never retouch it**.

## Reference run (jj-guild / JeanJack)

- `examples/character/JeanJack/` — `original.png` (identity
  reference), `raw.png`, `crop.png`, `prompt.md`;
- `examples/scene/lan/` — `raw.png`, `background.png`, `prompt.md`;
- `examples/avatar/JeanJack.png` — 896 px, 995 KB: the lossless
  PNG fits this case's < 1 MB bound directly (earlier, glossier
  renders needed the JPEG fallback).
- `examples/avatar/prompt.md` — the exact combination recipe.

Reproduce the avatar with the commands above; each prompt file
documents its blocking criteria.
