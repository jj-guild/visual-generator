#!/usr/bin/env python3
"""Avatar pipeline — compose a character cutout over a prepared background.

The avatar flow (the jj-guild case, generalised):

1. ``bg_*.png``      — a sharp background scene (center uncluttered);
2. ``raw_user.png``  — a raw character render on a flat uniform
   background (full body, empty hands, clean silhouette);
3. ``prepare_background`` — square center-crop, optional brightness,
   Gaussian blur (the background must read as *scene*, not detail);
4. ``cutout_character`` — transparent extraction (rembg + alpha
   matting, preserving thin limbs and headset interstices);
5. ``detect_anchor`` — locate the nameplate (gold blob cluster) and
   derive the placement anchor;
6. ``build_avatar`` — anchor-driven composition: ``headroom`` free
   space above the head, ``plate_bottom`` fixing the anchor's height,
   centering on the anchor (never on the arms), body cut flush by the
   bottom edge, PNG under the size bound.

Fail-closed everywhere: missing art, unreadable input, undetectable
anchor, or an avatar that cannot meet the size bound abort with an
explicit message and a non-zero exit.
"""

from __future__ import annotations

import os
import sys

DEFAULT_SIZE = 896
DEFAULT_HEADROOM = 0.15
DEFAULT_PLATE_BOTTOM = 0.85
DEFAULT_BLUR = 5.0
DEFAULT_MAX_BYTES = 1024 * 1024


def _require_file(path: str, what: str) -> None:
    if not path or not os.path.isfile(path):
        sys.exit(f"avatar: {what} not found: {path!r}")


def _square_crop(img):
    w, h = img.size
    side = min(w, h)
    return img.crop(((w - side) // 2, (h - side) // 2, (w + side) // 2, (h + side) // 2))


def prepare_background(src: str, out: str, size: int = 1024,
                       blur: float = DEFAULT_BLUR, brightness: float = 1.0) -> str:
    """Square-crop, resize, optionally brighten then blur a scene image."""
    from PIL import Image, ImageEnhance, ImageFilter

    _require_file(src, "background source")
    bg = Image.open(src).convert("RGB")
    bg = _square_crop(bg).resize((size, size), Image.LANCZOS)
    if brightness and brightness != 1.0:
        bg = ImageEnhance.Brightness(bg).enhance(brightness)
    if blur:
        bg = bg.filter(ImageFilter.GaussianBlur(blur))
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    bg.save(out, optimize=True)
    return out


def cutout_character(src: str, out: str) -> str:
    """Extract the character with a transparent background (rembg).

    Alpha matting is tuned to preserve thin arms and the interstices
    of headsets: gentle foreground threshold, small erosion.
    """
    _require_file(src, "character source")
    try:
        from rembg import new_session, remove
    except ImportError:
        sys.exit("avatar: rembg is required for cutout (pip install rembg)")
    from PIL import Image

    img = Image.open(src).convert("RGB")
    session = new_session("isnet-general-use")
    cut = remove(img, session=session, alpha_matting=True,
                 alpha_matting_foreground_threshold=230,
                 alpha_matting_background_threshold=15,
                 alpha_matting_erode_size=8)
    cut = cut.crop(cut.getbbox())
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    cut.save(out, optimize=True)
    return out


def detect_anchor(character: str) -> tuple[float, float]:
    """Locate the gold nameplate; return (cx_fraction, bottom_fraction).

    The plate is found as a horizontal cluster of letter-sized gold
    blobs (R>110, G>80, B<210, G<R+20) in the lower two-thirds of the
    cutout. The anchor's bottom is the plate's lower edge, its x the
    cluster's center — arms and pose never influence placement.
    """
    _require_file(character, "character cutout")
    import numpy as np
    from PIL import Image
    from scipy import ndimage

    a = np.array(Image.open(character).convert("RGBA"))
    rgb = a[..., :3].astype(int)
    h, w = rgb.shape[:2]
    solid = a[..., 3] > 128
    mask = ((rgb[..., 0] > 110) & (rgb[..., 1] > 80) & (rgb[..., 2] < 210)
            & (rgb[..., 1] < rgb[..., 0] + 20) & solid)
    mask[: int(h * 0.4)] = False  # the plate sits on the torso, never on the head
    lab, n = ndimage.label(mask)
    letters = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if len(ys) < 60:
            continue
        lw = int(xs.max() - xs.min())
        lh = int(ys.max() - ys.min())
        if 8 <= lw <= 90 and 15 <= lh <= 120 and lw < 2 * lh:
            letters.append((float(ys.mean()), float(xs.mean()),
                            int(ys.max()), int(xs.min()), int(xs.max())))
    if len(letters) < 3:
        sys.exit("avatar: nameplate not detected — pass --anchor cx,bottom manually")
    # cluster letters sharing a horizontal band (same text line)
    ys_mean = sorted(l[0] for l in letters)
    bands = [[ys_mean[0]]]
    for y in ys_mean[1:]:
        if y - bands[-1][-1] < 60:
            bands[-1].append(y)
        else:
            bands.append([y])
    band_y = max(bands, key=len)
    lo, hi = min(band_y) - 80, max(band_y) + 80
    line = [l for l in letters if lo <= l[0] <= hi]
    if len(line) < 3:
        sys.exit("avatar: nameplate not detected — pass --anchor cx,bottom manually")
    plate_bottom = max(l[2] for l in line) + 14  # lower edge of the plate itself
    cx = (min(l[3] for l in line) + max(l[4] for l in line)) / 2
    return cx / w, min(plate_bottom / h, 0.98)


def build_avatar(bg: str, character: str, out: str, size: int = DEFAULT_SIZE,
                 headroom: float = DEFAULT_HEADROOM,
                 plate_bottom: float = DEFAULT_PLATE_BOTTOM,
                 anchor: tuple[float, float] | None = None,
                 max_bytes: int = DEFAULT_MAX_BYTES) -> str:
    """Compose the avatar: bg -> character, anchor-driven, cut flush.

    The vertical span head-top -> anchor bottom is mapped onto
    ``plate_bottom - headroom`` of the canvas; the character top sits
    at ``headroom``; horizontal centering follows the anchor. The
    character's full scaled height extends past the canvas bottom by
    construction, so the body is cut flush by the frame edge.
    """
    from PIL import Image

    _require_file(bg, "background")
    _require_file(character, "character cutout")
    if not 0.0 < headroom < plate_bottom < 1.0:
        sys.exit("avatar: need 0 < headroom < plate_bottom < 1")
    if anchor is None:
        anchor = detect_anchor(character)
    cx_frac, bottom_frac = anchor
    if not (0.0 <= cx_frac <= 1.0 and 0.0 < bottom_frac <= 1.0):
        sys.exit("avatar: anchor fractions out of range")

    bg_img = Image.open(bg).convert("RGB")
    if bg_img.size != (size, size):
        bg_img = _square_crop(bg_img).resize((size, size), Image.LANCZOS)
    ch = Image.open(character).convert("RGBA")
    cw, chh = ch.size
    anchor_px = bottom_frac * chh
    scale = ((plate_bottom - headroom) * size) / anchor_px
    ch_s = ch.resize((round(cw * scale), round(chh * scale)), Image.LANCZOS)
    px = round(size / 2 - cx_frac * cw * scale)
    py = round(headroom * size)

    canvas = bg_img.convert("RGBA")
    canvas.alpha_composite(ch_s, (px, py))
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    canvas.save(out, optimize=True)
    if os.path.getsize(out) > max_bytes:
        # palette quantization (RGBA-safe) before giving up
        quant = canvas.quantize(colors=256, method=Image.FASTOCTREE)
        quant.save(out, optimize=True)
    actual = os.path.getsize(out)
    if actual > max_bytes:
        sys.exit(f"avatar: {out} is {actual} bytes (> {max_bytes}); "
                 "reduce --size or simplify the art")
    return out
