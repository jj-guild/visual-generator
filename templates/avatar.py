#!/usr/bin/env python3
"""Template: avatar — a character composed onto a background.

Square avatar built from two art assets, no engine-drawn text: a
background image and a transparent character cutout. The layout is
anchor-driven: the character is scaled and centered so that its
``anchor`` point lands at a fixed fraction of the canvas, and the
body is cut flush by the bottom edge of the frame.

JSON schema::

    {
      "template": "avatar",
      "output": "examples/assets/jeanjack/avatar_JeanJack.png",
      "canvas": {"width": 896, "height": 896},
      "art": {
        "background": "examples/assets/jeanjack/bg_LAN.png",
        "character": "examples/assets/jeanjack/JeanJack.png"
      },
      "sections": {
        "headroom_fraction": 0.15,     # free space above the anchor's top zone
        "plate_bottom_fraction": 0.85, # where the anchor lands vertically
        "anchor": {
          "cx_fraction": 0.56,        # anchor x, fraction of character width
          "bottom_fraction": 0.631    # anchor y (bottom), fraction of character height
        }
      }
    }

Sizing rule: the vertical span from the character's top to the anchor
bottom is mapped onto ``(plate_bottom_fraction - headroom_fraction)``
of the canvas height; the character top sits at
``headroom_fraction``; horizontal centering follows the anchor
(arms/pose never influence placement). The character is always cut
flush by the bottom edge: the composition guarantees alpha content
down to the last canvas row. Fail-closed: missing or unreadable art,
invalid fractions, non-square canvas abort with a message.
"""

from __future__ import annotations

import os

DEFAULT_PALETTE = {"canvas_backdrop": (18, 18, 24)}


def render(data: dict, fonts: dict):
    import sys
    from PIL import Image

    canvas = data.get("canvas", {})
    W = int(canvas.get("width", 896))
    H = int(canvas.get("height", 896))
    if W != H:
        sys.exit(f"avatar template expects a square canvas, got {W}x{H}")

    sec = data.get("sections", {})
    headroom = float(sec.get("headroom_fraction", 0.15))
    plate_bottom = float(sec.get("plate_bottom_fraction", 0.85))
    anchor = sec.get("anchor", {})
    cx_frac = float(anchor.get("cx_fraction", 0.5))
    bottom_frac = float(anchor.get("bottom_fraction", 1.0))
    if not (0.0 < headroom < plate_bottom < 1.0):
        sys.exit("avatar: need 0 < headroom_fraction < plate_bottom_fraction < 1")
    if not (0.0 <= cx_frac <= 1.0 and 0.0 < bottom_frac <= 1.0):
        sys.exit("avatar: anchor fractions out of range")

    art = data.get("art", {})
    bg_path = art.get("background")
    ch_path = art.get("character")
    for label, path in (("background", bg_path), ("character", ch_path)):
        if not path or not os.path.isfile(path):
            sys.exit(f"avatar: {label} art missing: {path!r}")

    bg = Image.open(bg_path).convert("RGB")
    ch = Image.open(ch_path).convert("RGBA")

    # background: center-crop to square, resize to canvas
    bw, bh = bg.size
    side = min(bw, bh)
    bg = bg.crop(((bw - side) // 2, (bh - side) // 2,
                  (bw + side) // 2, (bh + side) // 2)).resize((W, H), Image.LANCZOS)

    # character scaling: top -> anchor bottom maps onto headroom -> plate_bottom
    cw, chh = ch.size
    anchor_px = bottom_frac * chh
    span = plate_bottom - headroom
    scale = (span * H) / anchor_px
    ch_s = ch.resize((int(round(cw * scale)), int(round(chh * scale))), Image.LANCZOS)

    py = int(round(headroom * H))
    px = int(round(W / 2 - cx_frac * cw * scale))

    # the character's full scaled height extends past the canvas bottom by
    # construction, so the body is cut flush by the frame edge
    canvas_img = bg.convert("RGBA")
    canvas_img.alpha_composite(ch_s, (px, py))
    return canvas_img.convert("RGBA")
