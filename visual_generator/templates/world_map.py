#!/usr/bin/env python3
"""Template: annotated world map with crest spots.

A real world-map art as the background (no text in the art), with the
game's territories pinned at geographic positions — one spot per
region: a colored pin, or a **crest spot** (a round medallion carrying
that region's image/crest), with a parchment label plate readable
over busy art.

JSON schema::

    {
      "template": "world_map",
      "output": "examples/world_map_regions.jpg",
      "art": "path/to/world_map_art.jpg",
      "sections": {
        "title": "THE WORLD — WEEK 3",
        "footer": "Demo Game — Season II",
        "regions": [
          {"name": "Black Forest", "x": 246, "y": 156,
           "color": "#5c8a4e", "note": "Elks · Lion",
           "icon": "path/to/crest.png"}
        ]
      }
    }

``x``/``y`` are pixel coordinates on the 576×432 canvas (the title
band occupies the top 48 px, the footer band the bottom 28 px).
``icon`` is optional — without it the region gets a colored pin,
with it a gold-ringed round spot carrying the image (crest, civ
icon, thumbnail). **Place regions on actual land** — inspect the map
art first and pin each territory where it belongs geographically;
pins in the ocean are a defect.
"""
from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont

DEFAULT_PALETTE = {
    "bg": (24, 20, 16), "plate": (240, 228, 200), "plate_edge": (120, 96, 52),
    "ink": (40, 30, 16), "title_txt": (240, 228, 200), "title_band": (52, 40, 24),
    "title_edge": (176, 141, 74), "subtitle": (205, 180, 130),
    "gold": (176, 141, 74),
}

W, H = 576, 432
TITLE_H = 48
FOOTER_H = 28
SPOT = 36

STRUCTURE = {
    "canvas": {"width": W, "height": H},
    "target": "discord-embed",
    "zones": {
        "art": {"kind": "image", "rect": [0, TITLE_H, W, H - FOOTER_H],
                "note": "world map art, full-bleed under the bands"},
        "title": {"kind": "text", "rect": [0, 0, W, TITLE_H],
                  "note": "map title, centered in the top band"},
        "footer": {"kind": "text", "rect": [0, H - FOOTER_H, W, H],
                   "note": "footer line, centered"},
        "regions": {"kind": "image+text", "rect": [0, TITLE_H, W, H - FOOTER_H],
                    "note": "one spot per region at its (x, y): colored "
                            "pin, or round crest spot when `icon` is set; "
                            "name + note on a parchment plate to the right"},
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

    art = Image.open(data["art"]).convert("RGB").resize((W, H - TITLE_H - FOOTER_H))
    c.paste(art, (0, TITLE_H))

    d.rectangle([0, 0, W - 1, H - 1], outline=pal["title_edge"], width=4)
    d.rectangle([0, 0, W - 1, TITLE_H], fill=pal["title_band"],
                outline=pal["title_edge"], width=2)
    d.text((W // 2, TITLE_H // 2), sec["title"],
           font=ImageFont.truetype(fonts["b"], 22),
           fill=pal["title_txt"], anchor="mm")

    name_f = ImageFont.truetype(fonts["b"], 16)
    note_f = ImageFont.truetype(fonts["r"], 13)
    for region in sec["regions"]:
        x, y = region["x"], region["y"]
        r, g, b = tuple(int(region.get("color", "#b08d4a").lstrip("#")[i:i + 2], 16)
                        for i in (0, 2, 4))

        icon_path = region.get("icon")
        if icon_path:
            m = SPOT
            crop = _crop_to(Image.open(icon_path).convert("RGB"), m, m)
            mask = Image.new("L", (m, m), 0)
            ImageDraw.Draw(mask).ellipse([0, 0, m - 1, m - 1], fill=255)
            c.paste(crop, (x - m // 2, y - m // 2), mask)
            d.ellipse([x - m // 2, y - m // 2, x + m // 2, y + m // 2],
                      outline=pal["gold"], width=3)
        else:
            d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(r, g, b),
                      outline=pal["plate_edge"], width=2)

        label_w = max(d.textlength(region["name"], font=name_f),
                      d.textlength(region.get("note", ""), font=note_f)) + 18
        plate_h = 44 if region.get("note") else 28
        dx = x + (SPOT // 2 if icon_path else 10)
        d.rounded_rectangle([dx, y - plate_h // 2, dx + label_w, y + plate_h // 2],
                            radius=6, fill=pal["plate"], outline=pal["plate_edge"], width=2)
        d.text((dx + 9, y - (7 if region.get("note") else 0)), region["name"],
               font=name_f, fill=pal["ink"], anchor="lm")
        if region.get("note"):
            d.text((dx + 9, y + 12), region["note"], font=note_f,
                   fill=(90, 66, 34), anchor="lm")

    d.rectangle([0, H - FOOTER_H, W - 1, H - 1], fill=pal["title_band"])
    d.text((W // 2, H - FOOTER_H // 2), sec.get("footer", ""),
           font=ImageFont.truetype(fonts["r"], 14),
           fill=pal["subtitle"], anchor="mm")
    return c
