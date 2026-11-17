#!/usr/bin/env python3
"""Template: match announcement — two players, one place, the context.

Landscape 576×324 (Discord embed target, < 600 px). Composition:

- **left player**: round avatar medallion, pseudo below;
- **right player**: mirrored;
- **center**: the battle map thumbnail in a gold medallion, map name
  under it, VS badge below;
- **bottom band**: tournament line, settings line, time line;
- backdrop: a dim battle scene (top-level ``art``), no empty plate
  zones — every zone carries image or text.

JSON schema::

    {
      "template": "match_announcement",
      "output": "examples/match_announcement.jpg",
      "art": "path/to/battle_backdrop.jpg",
      "sections": {
        "left_name": "Aldric",
        "left_avatar": "path/to/avatar.png",
        "right_name": "Brunhild",
        "right_avatar": "path/to/avatar.png",
        "map_art": "path/to/map_thumbnail.jpg",
        "map_name": "Golden Coast",
        "vs": "VS",
        "context_line": "Winter Tournament — Round 2",
        "sub_line": "Settings: Hard · 2v2",
        "footer": "Sunday 23:30 · Season II"
      }
    }

Pseudos should stay short (≈ 14 characters max per side).
"""
from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont

DEFAULT_PALETTE = {
    "bg": (24, 20, 16), "band": (52, 40, 24), "gold": (176, 141, 74),
    "text_light": (238, 220, 168), "subtitle": (205, 180, 130),
    "vs_bg": (176, 44, 32), "vs_ring": (218, 193, 121), "vs_txt": (255, 240, 210),
}

W, H = 576, 324

STRUCTURE = {
    "canvas": {"width": W, "height": H},
    "target": "discord-embed",
    "zones": {
        "art": {"kind": "image", "rect": [0, 0, W, H],
                "note": "battle backdrop, dimmed by the template"},
        "left_avatar": {"kind": "image", "rect": [34, 66, 138, 170],
                        "note": "left player avatar, round medallion"},
        "left_name": {"kind": "text", "rect": [16, 182, 156, 210],
                      "note": "left player pseudo, centered"},
        "right_avatar": {"kind": "image", "rect": [438, 66, 542, 170],
                         "note": "right player avatar, round medallion"},
        "right_name": {"kind": "text", "rect": [420, 182, 560, 210],
                       "note": "right player pseudo, centered"},
        "map_art": {"kind": "image", "rect": [242, 54, 334, 146],
                    "note": "battle map thumbnail, round medallion"},
        "map_name": {"kind": "text", "rect": [198, 152, 378, 176],
                     "note": "map name, centered"},
        "vs": {"kind": "text", "rect": [270, 190, 306, 222],
               "note": "VS badge between the players"},
        "context_line": {"kind": "text", "rect": [18, 240, 558, 268],
                         "note": "tournament line (bold)"},
        "sub_line": {"kind": "text", "rect": [18, 268, 558, 290],
                     "note": "settings line"},
        "footer": {"kind": "text", "rect": [18, 290, 558, 306],
                   "note": "time / misc line"},
    },
}


def _crop_to(art, w, h):
    """Center-crop art to the w:h window (no stretching)."""
    aw, ah = art.size
    scale = max(w / aw, h / ah)
    big = art.resize((int(aw * scale), int(ah * scale)))
    x, y = (big.width - w) // 2, (big.height - h) // 2
    return big.crop((x, y, x + w, y + h))


def _medallion(canvas, img, cx, cy, r, pal):
    """Paste img center-cropped into a gold-ringed circle at (cx, cy)."""
    m = 2 * r
    crop = _crop_to(img.convert("RGB"), m, m)
    mask = Image.new("L", (m, m), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, m - 1, m - 1], fill=255)
    canvas.paste(crop, (cx - r, cy - r), mask)
    ImageDraw.Draw(canvas).ellipse([cx - r, cy - r, cx + r, cy + r],
                                   outline=pal["gold"], width=3)


def render(data, fonts):
    sec = data["sections"]
    pal = resolve_palette(DEFAULT_PALETTE, data.get("palette"))
    c = Image.new("RGB", (W, H), pal["bg"])
    d = ImageDraw.Draw(c)

    art_path = data.get("art")
    if art_path:
        art = Image.open(art_path).convert("RGB").resize((W, H))
        c.paste(Image.blend(c, art, 0.55), (0, 0))
        d = ImageDraw.Draw(c)
    d.rectangle([0, 0, W - 1, H - 1], outline=pal["gold"], width=4)

    # --- players (avatar medallions + pseudos) ---
    for side, cx in (("left", 86), ("right", W - 86)):
        avatar = Image.open(sec[f"{side}_avatar"])
        _medallion(c, avatar, cx, 118, 52, pal)
        d.text((cx, 196), sec[f"{side}_name"],
               font=ImageFont.truetype(fonts["b"], 22),
               fill=pal["text_light"], anchor="mm")

    # --- battle map medallion + name ---
    mcx, mcy = W // 2, 100
    _medallion(c, Image.open(sec["map_art"]), mcx, mcy, 46, pal)
    d.text((mcx, 160), sec.get("map_name", ""),
           font=ImageFont.truetype(fonts["b"], 18),
           fill=pal["text_light"], anchor="mm")

    # --- VS badge ---
    d = ImageDraw.Draw(c)
    r = 17
    d.ellipse([mcx - r, 205 - r, mcx + r, 205 + r],
              fill=pal["vs_bg"], outline=pal["vs_ring"], width=2)
    d.text((mcx, 205), sec.get("vs", "VS"),
           font=ImageFont.truetype(fonts["b"], 16),
           fill=pal["vs_txt"], anchor="mm")

    # --- bottom band: tournament / settings / time ---
    d.rectangle([18, 232, W - 18, 310], fill=pal["band"],
                outline=pal["gold"], width=2)
    d.text((W // 2, 252), sec["context_line"],
           font=ImageFont.truetype(fonts["b"], 19),
           fill=pal["text_light"], anchor="mm")
    d.text((W // 2, 274), sec.get("sub_line", ""),
           font=ImageFont.truetype(fonts["r"], 15),
           fill=pal["subtitle"], anchor="mm")
    d.text((W // 2, 294), sec.get("footer", ""),
           font=ImageFont.truetype(fonts["r"], 13),
           fill=pal["subtitle"], anchor="mm")
    return c
