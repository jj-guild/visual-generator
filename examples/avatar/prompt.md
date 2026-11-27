# Avatar recipe — JeanJack on LAN background

Combines `examples/character/JeanJack/crop.png` and
`examples/scene/lan/background.png` into
`examples/avatar/JeanJack.jpg`. Every parameter below was validated
during the jj-guild avatar session; nothing here is arbitrary.

```bash
# 1. background: square center-crop + Gaussian blur
#    --blur 4: the scene stays readable as a LAN party while the
#    character detaches from it (5 was too strong, 3 was refused).
python tools/make_avatar.py bg \
    --src examples/scene/lan/raw.png \
    --out examples/scene/lan/background.png --blur 4

# 2. crop: transparent character (rembg, soft alpha matting tuned
#    for thin arms and headset interstices)
python tools/make_avatar.py cutout \
    --src examples/character/JeanJack/raw.png \
    --out examples/character/JeanJack/crop.png

# 3. avatar: anchor-driven composition (auto-detection on the gold
#    nameplate), size bound passed explicitly — it is a per-request
#    constraint, never a universal default; ask the user when
#    absent. This case asks for < 1 MB (999,424 bytes = 976 KiB).
#    --dx 20: the character is posed slightly sideways; the anchor
#    sits right of the face center, so a small right nudge restores
#    visual centering.
python tools/make_avatar.py compose \
    --bg examples/scene/lan/background.png \
    --character examples/character/JeanJack/crop.png \
    --out examples/avatar/JeanJack.png --dx 20 --max-kb 976
```

## Retained parameters (user-validated)

| Parameter | Value | Reason |
|---|---|---|
| `--blur` | 4 | background readable, character detached; below 4 the PNG cannot fit the bound cleanly |
| `--dx` | 20 | visual centering of the sideways-posed character |
| `--brightness` | none | the validated scene is natively bright (mean luminance ≈ 72 after blur); brightness correction is allowed only on explicit user request |
| `--max-kb` | 976 | the < 1 MB bound of THIS case; per-request, ask when absent |

## Size-bound behavior (per-request)

- PNG first; without a bound the avatar stays PNG.
- If the bound is set and the PNG exceeds it, the pipeline falls
  back to JPEG and searches for the HIGHEST quality whose file size
  stays under the bound — approaching the requested limit for
  maximum quality, never settling for an undersized file.
- Fail-closed: if even the minimum quality cannot fit, nothing is
  delivered.
