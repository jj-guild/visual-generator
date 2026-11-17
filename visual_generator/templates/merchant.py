#!/usr/bin/env python3
"""Template: merchant — product sheets side by side.

A titled row of product cards: art window, name, short description,
price on a gold band — several sheets côte à côte. Built for shop
posts (the traveling merchant, the seasonal market).

JSON schema::

    {
      "template": "merchant",
      "output": "examples/merchant.jpg",
      "sections": {
        "title": "THE MERCHANT — Week 3",
        "columns": 3,
        "products": [
          {"art": "path/to/product_art.jpg",
           "name": "Old Map",
           "description": "Reveals one unexplored territory.",
           "price": "120 gears"}
        ],
        "footer": "Demo Game — one purchase per player per week"
      }
    }

``columns`` defaults to 3 (max 4); extra products wrap onto a second
row. Keep descriptions short (≈ 2 lines per card).
"""
from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont

DEFAULT_PALETTE = {
    "bg": (24, 20, 16), "band": (52, 40, 24), "gold": (176, 141, 74),
    "card": (34, 28, 20), "text_light": (238, 220, 168),
    "subtitle": (205, 180, 130), "price_band": (92, 74, 40),
    "price_txt": (255, 226, 160),
}

W, H = 576, 384
TITLE_H = 44
FOOTER_H = 24
MARGIN, GAP = 14, 10

STRUCTURE = {
    "canvas": {"width": W, "height": H},
    "target": "discord-embed",
    "zones": {
        "title": {"kind": "text", "rect": [0, 0, W, TITLE_H],
                  "note": "shop title, centered in the top band"},
        "products": {"kind": "image+text", "rect": [MARGIN, TITLE_H + 8, W - MARGIN, H - FOOTER_H],
                     "note": "grid of product cards (columns per JSON): "
                             "art window, name, description, price band"},
        "footer": {"kind": "text", "rect": [0, H - FOOTER_H, W, H],
                   "note": "footer line, centered"},
    },
}


def _crop_to(art, w, h):
    aw, ah = art.size
    scale = max(w / aw, h / ah)
    big = art.resize((int(aw * scale), int(ah * scale)))
    x, y = (big.width - w) // 2, (big.height - h) // 2
    return big.crop((x, y, x + w, y + h))


def _wrap(draw, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def render(data, fonts):
    sec = data["sections"]
    pal = resolve_palette(DEFAULT_PALETTE, data.get("palette"))
    c = Image.new("RGB", (W, H), pal["bg"])
    d = ImageDraw.Draw(c)

    d.rectangle([0, 0, W - 1, H - 1], outline=pal["gold"], width=4)
    d.rectangle([0, 0, W - 1, TITLE_H], fill=pal["band"], outline=pal["gold"], width=2)
    d.text((W // 2, TITLE_H // 2), sec["title"],
           font=ImageFont.truetype(fonts["b"], 22),
           fill=pal["text_light"], anchor="mm")

    products = sec["products"]
    cols = min(sec.get("columns", 3), 4, len(products))
    rows = (len(products) + cols - 1) // cols
    grid_w = W - 2 * MARGIN
    card_w = (grid_w - (cols - 1) * GAP) // cols
    grid_h = H - TITLE_H - FOOTER_H - 8
    card_h = (grid_h - (rows - 1) * GAP) // rows

    name_f = ImageFont.truetype(fonts["b"], 16)
    desc_f = ImageFont.truetype(fonts["r"], 13)
    price_f = ImageFont.truetype(fonts["b"], 16)

    for i, product in enumerate(products):
        r, col = divmod(i, cols)
        x0 = MARGIN + col * (card_w + GAP)
        y0 = TITLE_H + 8 + r * (card_h + GAP)
        d.rounded_rectangle([x0, y0, x0 + card_w - 1, y0 + card_h - 1],
                            radius=8, fill=pal["card"], outline=pal["gold"], width=2)

        art_h = int(card_h * 0.42)
        art = _crop_to(Image.open(product["art"]).convert("RGB"), card_w - 8, art_h)
        c.paste(art, (x0 + 4, y0 + 4))
        d.rectangle([x0 + 4, y0 + 4, x0 + card_w - 5, y0 + 4 + art_h],
                    outline=pal["gold"], width=1)

        ty = y0 + 8 + art_h
        d.text((x0 + card_w // 2, ty + 10), product["name"],
               font=name_f, fill=pal["text_light"], anchor="mm")
        ty += 24
        for ln in _wrap(d, product.get("description", ""), desc_f, card_w - 16)[:3]:
            d.text((x0 + 8, ty), ln, font=desc_f, fill=pal["subtitle"])
            ty += 16

        d.rectangle([x0 + 3, y0 + card_h - 26, x0 + card_w - 4, y0 + card_h - 4],
                    fill=pal["price_band"])
        d.text((x0 + card_w // 2, y0 + card_h - 15), product["price"],
               font=price_f, fill=pal["price_txt"], anchor="mm")

    d.rectangle([0, H - FOOTER_H, W - 1, H - 1], fill=pal["band"])
    d.text((W // 2, H - FOOTER_H // 2), sec.get("footer", ""),
           font=ImageFont.truetype(fonts["r"], 13),
           fill=pal["subtitle"], anchor="mm")
    return c
