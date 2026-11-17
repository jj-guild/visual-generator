#!/usr/bin/env python3
"""Template: entity card — one entity's sheet, collector-card style.

The proven collector-card anatomy: outer frame, colored name banner
with a badge, a large art window over a translucent backdrop, parchment
plates for the content (light box, dark ink — the OCR-winning
contrast), an optional linked-value box, and a dark footer. Built for
the "one entity per post" visuals: territory sheet, civilization
sheet, player profile — any entity with a visual and a description.

JSON schema::

    {
      "template": "entity_card",
      "output": "examples/entity_territory.jpg",
      "canvas": {"width": 576, "height": 800},          # optional (default)
      "palette": {"gold": "#5c8a4e", "band": "#22301e"},  # kind colors
      "art": "path/to/entity_art.jpg",                  # the art window
      "backdrop": "path/to/scene.jpg",                 # optional background
      "badge": "r3",                                   # round badge, optional
      "sections": {
        "title": "Northern Keep",
        "type_line": "Defensive territory",
        "plates": [
          {"head": "Territory bonus",
           "lines": ["Buildings +10/20/30/40 % HP", "..."]}
        ],
        "extra_label": "Unique unit",                  # optional linked box
        "extra_value": "Shieldbearer",
        "footer_left": "demo:territory:northern-keep",
        "footer_right": "Demo Game"
      }
    }

The optional ``backdrop`` is a scene art stretched behind the whole
card and lightly veiled (18% toward the band color), barely blurred:
the scene stays readable — it is a backdrop, not a wash.

Anatomy (fractions of the canvas — never moved by the art):

    0.00–0.10  outer frame + name banner (badge on the right)
    0.10–0.55  art window (full-bleed, center-cropped)
    0.55–0.58  italic type line
    0.58–0.86  parchment plate: section heads + lines
    0.86–0.94  linked-value box (banner color, when extra is set)
    0.94–1.00  footer

All metrics scale with the ``canvas`` (default 576×800, Discord embed
target).
"""

from __future__ import annotations

from PIL import Image, ImageDraw, ImageFilter, ImageFont

DEFAULT_PALETTE = {
    "bg": (30, 38, 26), "band": (34, 48, 30), "gold": (92, 138, 78),
    "gold2": (66, 96, 58), "text_light": (224, 238, 210),
    "subtitle": (200, 216, 190), "box": (238, 232, 208), "ink": (30, 40, 22),
    "badge": (52, 92, 44), "badge_ring": (224, 238, 210),
    "badge_txt": (240, 250, 235), "footer": (34, 48, 30),
    "footer_txt": (200, 216, 190),
}

F_NAME = 0.10
F_ART = 0.55
F_TYPE = 0.58
F_RULE = 0.86
F_EXTRA = 0.94

DEFAULT_W, DEFAULT_H = 576, 800
REF_W = 744

STRUCTURE = {
    "canvas": {"width": DEFAULT_W, "height": DEFAULT_H},
    "target": "discord-embed",
    "zones": {
        "backdrop": {"kind": "image", "rect": [0, 0, DEFAULT_W, DEFAULT_H],
                     "note": "optional scene behind the whole card, veiled"},
        "title": {"kind": "text", "rect": [26, 26, DEFAULT_W - 96, 80],
                  "note": "entity name in the top banner"},
        "badge": {"kind": "text", "rect": [DEFAULT_W - 106, 33, DEFAULT_W - 30, 73],
                  "note": "round badge on the banner right (optional)"},
        "art": {"kind": "image", "rect": [49, 84, 526, 440],
                "note": "entity art window, center-cropped or fitted"},
        "type_line": {"kind": "text", "rect": [0, 440, DEFAULT_W, 464],
                      "note": "italic type line, centered"},
        "plates": {"kind": "text", "rect": [43, 470, 533, 648],
                   "note": "parchment plate: section heads + lines"},
        "extra_label": {"kind": "text", "rect": [43, 660, 533, 690],
                        "note": "linked-value box label (optional)"},
        "extra_value": {"kind": "text", "rect": [43, 690, 533, 730],
                        "note": "linked-value box value"},
        "footer_left": {"kind": "text", "rect": [37, 760, 300, 785],
                        "note": "footer, left-aligned"},
        "footer_right": {"kind": "text", "rect": [276, 760, 539, 785],
                         "note": "footer, right-aligned"},
    },
}


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


def _fit(img, w, h):
    """Scale to fit inside w×h (contain), centered, transparency kept."""
    img = img.copy()
    img.thumbnail((w - 24, h - 24))
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    layer.paste(img, ((w - img.width) // 2, (h - img.height) // 2))
    return layer


def _crop(art, w, h, bg=(30, 38, 26)):
    """Center-crop art to the w:h window; transparency composites on bg."""
    if art.mode in ("P", "LA", "RGBA"):
        rgba = art.convert("RGBA")
        base = Image.new("RGBA", rgba.size, bg + (255,))
        art = Image.alpha_composite(base, rgba).convert("RGB")
    else:
        art = art.convert("RGB")
    scale = max(w / art.width, h / art.height)
    big = art.resize((int(art.width * scale), int(art.height * scale)))
    x, y = (big.width - w) // 2, (big.height - h) // 2
    return big.crop((x, y, x + w, y + h))


def render(data, fonts):
    sec = data["sections"]
    pal = resolve_palette(DEFAULT_PALETTE, data.get("palette"))
    cw = data.get("canvas", {}).get("width", DEFAULT_W)
    ch = data.get("canvas", {}).get("height", DEFAULT_H)
    s = cw / REF_W  # all metrics scale with the canvas
    c = Image.new("RGBA", (cw, ch), pal["bg"] + (255,))
    backdrop = data.get("backdrop")
    if backdrop:
        bd = Image.open(backdrop).convert("RGB").resize((cw, ch))
        bd = bd.filter(ImageFilter.GaussianBlur(max(1, int(2 * s))))
        veil = Image.new("RGB", (cw, ch), pal["band"])
        c.paste(Image.blend(bd, veil, 0.18).convert("RGBA"), (0, 0))
    d = ImageDraw.Draw(c)

    name_b = int(ch * F_NAME)
    art_b = int(ch * F_ART)
    type_b = int(ch * F_TYPE)
    rule_b = int(ch * F_RULE)
    extra_b = int(ch * F_EXTRA)

    # --- outer frame + name banner (the deck's double frame) ---
    d.rectangle([0, 0, cw - 1, ch - 1], outline=pal["gold"], width=max(2, int(10 * s)))
    d.rectangle([int(16 * s), int(16 * s), cw - int(17 * s), ch - int(17 * s)],
                outline=pal["gold2"], width=max(1, int(3 * s)))
    d.rectangle([int(26 * s), int(26 * s), cw - int(27 * s), name_b],
                fill=pal["band"], outline=pal["gold"], width=max(1, int(3 * s)))
    nf = ImageFont.truetype(fonts["b"], int((48 if len(sec["title"]) <= 12 else 40) * s))
    d.text((int(72 * s), (int(26 * s) + name_b) // 2), sec["title"], font=nf,
           fill=pal["text_light"], anchor="lm")

    badge = data.get("badge")
    if badge:
        r = int(40 * s)
        cx, cy = cw - int(96 * s), (int(26 * s) + name_b) // 2
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=pal["badge"],
                  outline=pal["badge_ring"], width=max(2, int(4 * s)))
        cf = ImageFont.truetype(fonts["b"], int((30 if len(str(badge)) > 3 else 48) * s))
        d.text((cx, cy), str(badge), font=cf, fill=pal["badge_txt"], anchor="mm")

    # --- art window ---
    # The window itself stays translucent (the backdrop shows through);
    # transparent art (crests) composites over the backdrop, never on an
    # opaque fill — a transparent crest must let the scene breathe.
    win_w = cw - int(128 * s)
    win_h = art_b - name_b - int(18 * s)
    win_plate = Image.new("RGBA", (win_w, win_h), (0, 0, 0, 0))
    art = Image.open(data["art"])
    if art.mode in ("P", "LA", "RGBA"):
        rgba = art.convert("RGBA")
        fitted = _fit(rgba, win_w, win_h)
        win_plate = Image.alpha_composite(win_plate, fitted)
    else:
        win_plate = _crop(art.convert("RGB"), win_w, win_h).convert("RGBA")
    c.alpha_composite(win_plate, (int(64 * s), name_b + int(4 * s)))
    d.rectangle([int(64 * s), name_b + int(4 * s),
                 int(64 * s) + win_w - 1, name_b + int(4 * s) + win_h - 1],
                outline=pal["gold2"], width=max(1, int(3 * s)))

    # --- italic type line ---
    d.text((cw // 2, (art_b + type_b) // 2 + int(2 * s)), sec.get("type_line", ""),
           font=ImageFont.truetype(fonts["i"], int(28 * s)),
           fill=pal["subtitle"], anchor="mm")

    # --- parchment plate: heads + lines (the deck's rule box) ---
    margin_x = int(56 * s)
    has_extra = bool(sec.get("extra_label"))
    r_bottom = int(ch * 0.81) if has_extra else rule_b
    r_top = type_b + int(6 * s)
    plate = Image.new("RGBA", (cw, r_bottom - r_top), (0, 0, 0, 0))
    pd = ImageDraw.Draw(plate)
    pd.rounded_rectangle([margin_x, 0, cw - margin_x - 1, r_bottom - r_top - 1],
                         radius=max(4, int(14 * s)),
                         fill=tuple(pal["box"]) + (206,),
                         outline=pal["gold2"] + (255,), width=max(1, int(3 * s)))
    c.alpha_composite(plate, (0, r_top))
    d = ImageDraw.Draw(c)
    head_f = ImageFont.truetype(fonts["b"], int(24 * s))
    body_f = ImageFont.truetype(fonts["r"], int(21 * s))
    lh_head = int(32 * s)
    lh_body = int(26 * s)
    y = r_top + int(16 * s)
    for plate in sec.get("plates", []):
        d.text((int(60 * s), y), plate.get("head", ""), font=head_f, fill=pal["gold2"])
        y += lh_head
        for item in plate.get("lines", []):
            for ln in _wrap(d, f"• {item}" if not str(item).startswith("•") else str(item),
                            body_f, cw - 2 * margin_x - int(44 * s))[:4]:
                d.text((int(66 * s), y), ln, font=body_f, fill=pal["ink"])
                y += lh_body
        y += int(8 * s)

    # --- linked-value box (banner color) ---
    if has_extra:
        box = Image.new("RGBA", (cw, extra_b - r_bottom - int(12 * s)), (0, 0, 0, 0))
        bd2 = ImageDraw.Draw(box)
        bd2.rounded_rectangle([margin_x, 0, cw - margin_x - 1,
                               extra_b - r_bottom - int(13 * s)],
                              radius=max(4, int(14 * s)),
                              fill=tuple(pal["band"]) + (216,),
                              outline=pal["gold"] + (255,), width=max(1, int(3 * s)))
        c.alpha_composite(box, (0, r_bottom + int(12 * s)))
        d = ImageDraw.Draw(c)
        mid = (r_bottom + int(12 * s) + extra_b) // 2
        d.text((cw // 2, mid - int(16 * s)), sec["extra_label"],
               font=ImageFont.truetype(fonts["r"], int(26 * s)),
               fill=pal["subtitle"], anchor="mm")
        d.text((cw // 2, mid + int(18 * s)), sec["extra_value"],
               font=ImageFont.truetype(fonts["b"], int(32 * s)),
               fill=pal["text_light"], anchor="mm")

    # --- footer ---
    foot_t = extra_b + int(8 * s)
    d.rectangle([int(26 * s), foot_t, cw - int(27 * s), ch - int(27 * s)],
                fill=pal["footer"], outline=pal["gold"], width=max(1, int(3 * s)))
    ff = ImageFont.truetype(fonts["r"], int(24 * s))
    d.text((int(48 * s), (foot_t + ch - int(27 * s)) // 2), sec.get("footer_left", ""),
           font=ff, fill=pal["footer_txt"], anchor="lm")
    d.text((cw - int(48 * s), (foot_t + ch - int(27 * s)) // 2), sec.get("footer_right", ""),
           font=ff, fill=pal["footer_txt"], anchor="rm")
    return c
