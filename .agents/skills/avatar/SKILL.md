---
name: avatar
description: Compose square avatars (character + background) from generated art — generate the raw character and the sharp scene with the right criteria, then run the avatar pipeline (cutout, background blur, anchor-driven framing, size bound). Use whenever a user asks for an avatar, a profile picture, or a character-on-background composition.
---

# Avatar generation (avatar pipeline)

**Repository**: https://github.com/jj-guild/visual-generator

The pipeline turns two generated images into one avatar:

```
raw_user.png  (character on a flat uniform background)
raw_bg_*.png  (sharp scene)  ──►  tools/make_avatar.py  ──►  avatar_user.png
```

It is element-based by doctrine: **each element is generated once,
never edited**. If a criterion fails, regenerate the element — never
retouch a generated render (no inpainting, no clone patch, no
pixel surgery). Compositing (crop, scale, position, blur) is the only
allowed transformation.

## Asset naming convention

| Prefix | Meaning |
|---|---|
| `raw_<name>.png` | generated character render, untouched (flat background, full body) |
| `raw_bg_<name>.png` | generated sharp scene, untouched |
| `cutout_<name>.png` | transparent character extraction |
| `bg_<name>_blurry.png` | prepared background: square crop + blur |
| `avatar_<name>.png` / `.jpg` | final: assembled, cropped, size-bound — profile-picture ready |

Candidates under selection are numbered: `raw_<name>_01.png`, …

## Before generating — ask if absent

If the user does not specify, **ask** (never assume):

- the final **aspect and size** (default proposal: square, 896 px);
- the **size bound** of the avatar file — per-case constraint, there
  is NO universal default (proposal: < 1 MB); pass it with
  `--max-kb`; JPEG fallback compresses to fit before failing;
- whether the background is a generated scene or a user image.

Only the final avatar is size-bound. Raw assets are kept at maximum
quality — never downscale `raw_user.png` or the scene to save space.

## Generation criteria

### raw_user.png (the character)

Prompt skeleton (adapt, keep the constraints):

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

### bg_*.png (the sharp scene)

Prompt skeleton:

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
python tools/make_avatar.py bg --src raw_bg_LAN.png --out bg_LAN_blurry.png --blur 4

# 2. cutout: transparent character (rembg, alpha matting tuned for
#    thin arms and headset interstices)
python tools/make_avatar.py cutout --src raw_user.png --out cutout_user.png

# 3. (optional) verify the auto-detected anchor
python tools/make_avatar.py anchor --character cutout_user.png

# 4. avatar: anchor-driven framing, cut flush at the bottom, size-bound
python tools/make_avatar.py compose --bg bg_LAN_blurry.png \
    --character cutout_user.png --out avatar_user.png
```

Agents doing programmatic work import the same core:

```python
from engine import avatar
avatar.prepare_background("raw_bg_LAN.png", "bg_LAN_blurry.png", blur=4)
avatar.cutout_character("raw_user.png", "cutout_user.png")
anchor = avatar.detect_anchor("cutout_user.png")   # (cx, bottom) fractions
avatar.build_avatar("bg_LAN_blurry.png", "cutout_user.png", "avatar_user.png",
                    max_bytes=1_000_000,  # per-case bound, ask the user
                    anchor=anchor)
```

### Framing rules (the defaults encode them)

| Rule | Default | Meaning |
|---|---|---|
| `--headroom` | 0.15 | 15% of the frame free above the head |
| `--plate-bottom` | 0.85 | the anchor (nameplate bottom) sits at 85% |
| anchor | auto | detected on the gold nameplate; centering follows it, **never the arms** |
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
   bound, the pipeline falls back to JPEG (quality ladder 92→70)
   which keeps gradients clean, unlike palette quantization.
5. Visual check of the face at full resolution: identity criteria
   (eyes, mouth, no unwanted features). If a criterion fails:
   **regenerate the raw element, never retouch it**.

## Reference run (jj-guild / JeanJack)

`examples/assets/jeanjack/` holds the full reference set:
`raw_JeanJack.png` (raw render), `cutout_JeanJack.png` (cutout),
`raw_bg_LAN_blurry.png` (sharp scene), `bg_LAN_blurry.png` (prepared background),
`avatar_JeanJack.jpg` (896 px, 143 KB — the < 1 MB bound of this case
forced the JPEG fallback, quality 92). Reproduce the avatar with the
commands above; the README section "Avatar generation" documents the
prompts used for both raw assets.
