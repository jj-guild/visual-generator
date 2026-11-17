#!/usr/bin/env python3
"""Template: kingdom — a realm's owned territories, side by side.

A castle scene as the background (top-level ``art``, lightly veiled),
the kingdom's name in the top band, the icon of every owned territory
in a centered row (optional caption under each), and the bottom band
for the ruler line.

JSON schema::

    {
      "template": "kingdom",
      "output": "examples/kingdom.jpg",
      "art": "path/to/castle_scene.jpg",
      "sections": {
        "title": "The Rivermark",
        "icons": [
          {"art": "path/to/territory_icon.jpg", "caption": "Twin Lakes"},
          {"art": "path/to/territory_icon.jpg", "caption": "Iron Hills"}
        ],
        "subtitle": "Ruled by Aldric — 6 territories",
        "footer": "Demo Game — Season II"
      }
    }

Up to 8 icons fit in the row (extras wrap onto a second row).
"""
from __future__ import annotations

from PIL import Image, ImageDraw, ImageFilter, ImageFont

DEFAULT_PALETTE = {
    "bg": (24, 20, 16), "band": (52, 40, 24), "gold": (176, 141, 74),
    "text_light": (238, 220, 168), "subtitle": (205, 180, 130),
    "spot": (34, 28, 20),
}

W, H = 576, 324
TITLE_H = 44
BAND_H = 62
ICON = 64
GAP = 8

STRUCTURE = {
    "canvas": {"width": W, "height": H},
    "target": "discord-embed",
    "zones": {
        "art": {"kind": "image", "rect": [0, 0, W, H],
                "note": "castle scene, full-bleed, veiled by the template"},
        "title": {"kind": "text", "rect": [0, 0, W, TITLE_H],
                  "note": "kingdom name, centered in the top band"},
        "icons": {"kind": "image+text", "rect": [8, TITLE_H + 8, W - 8, H - BAND_H - 8],
                  "note": "centered row of territory icons (round spots), "
                          "optional caption under each"},
        "subtitle": {"kind": "text", "rect": [18, H - BAND_H, W - 18, H - 30],
                     "note": "ruler line, centered"},
        "footer": {"kind": "text", "rect": [18, H - 30, W - 18, H],
                    "note": "footer line, centered"},
    },
}


def _crop_to(art, w, h):
    aw, ah = art.size
    scale = max(w / aw, h / ah)
    big = art.resize((int(aw * scale), int(ah * scale)))
    x, y = (big.width - w) // 2, (big.height - h) // 2
    return big.crop((x, y, x + w, y + h))


def render(data, fonts):
    sec = data["sections"]
    pal = resolve_palette(DEFAULT_PALETTE, data.get("palette"))
    c = Image.new("RGB", (W, H), pal["bg"])
    d = ImageDraw.Draw(c)

    art_path = data.get("art")
    if art_path:
        art = Image.open(art_path).convert("RGB").resize((W, H))
        art = art.filter(ImageFilter.GaussianBlur(1))
        veil = Image.new("RGB", (W, H), pal["band"])
        c.paste(Image.blend(art, veil, 0.30), (0, 0))
        d = ImageDraw.Draw(c)
    d.rectangle([0, 0, W - 1, H - 1], outline=pal["gold"], width=4)

    d.rectangle([0, 0, W - 1, TITLE_H], fill=pal["band"], outline=pal["gold"], width=2)
    d.text((W // 2, TITLE_H // 2), sec["title"],
           font=ImageFont.truetype(fonts["b"], 24),
           fill=pal["text_light"], anchor="mm")

    icons = sec.get("icons", [])
    per_row = min(len(icons), 8) or 1
    rows = (len(icons) + per_row - 1) // per_row if icons else 0
    row_h = ICON + 26
    cap_f = ImageFont.truetype(fonts["b"], 13)
    for i, item in enumerate(icons):
        r, col = divmod(i, per_row)
        n_in_row = min(per_row, len(icons) - r * per_row)
        row_w = n_in_row * ICON + (n_in_row - 1) * GAP
        x = (W - row_w) // 2 + col * (ICON + GAP)
        y = TITLE_H + 10 + r * row_h

        m = ICON
        crop = _crop_to(Image.open(item["art"]).convert("RGB"), m, m)
        mask = Image.new("L", (m, m), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, m - 1, m - 1], fill=255)
        c.paste(crop, (x, y), mask)
        d.ellipse([x, y, x + m - 1, y + m - 1],
                  outline=pal["gold"], width=3)
        if item.get("caption"):
            d.text((x + m // 2, y + m + 12), item["caption"],
                   font=cap_f, fill=pal["text_light"], anchor="mm")

    d.rectangle([18, H - BAND_H, W - 18, H - 4], fill=pal["band"],
                outline=pal["gold"], width=2)
    d.text((W // 2, H - BAND_H + 18), sec.get("subtitle", ""),
           font=ImageFont.truetype(fonts["r"], 14),
           fill=pal["subtitle"], anchor="mm")
    d.text((W // 2, H - BAND_H + 40), sec.get("footer", ""),
           font=ImageFont.truetype(fonts["r"], 13),
           fill=pal["subtitle"], anchor="mm")
    return c
