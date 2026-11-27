#!/usr/bin/env python3
"""Light CLI for the avatar pipeline (human-facing; agents import engine.avatar).

Workflow, one command per step::

    # 1. prepare the background: square crop + blur from a sharp scene
    python tools/make_avatar.py bg \\
        --src examples/assets/scenes/lan/raw_bg_LAN.png \\
        --out examples/assets/scenes/lan/bg_LAN_blurry.png --blur 5

    # 2. cut out the character from its raw render (flat background)
    python tools/make_avatar.py cutout \\
        --src examples/assets/personnages/jeanjack/raw_JeanJack.png \\
        --out examples/assets/personnages/jeanjack/cutout_JeanJack.png

    # 3. compose the avatar (anchor auto-detected on the nameplate)
    python tools/make_avatar.py compose \\
        --bg examples/assets/scenes/lan/bg_LAN_blurry.png \\
        --character examples/assets/personnages/jeanjack/cutout_JeanJack.png \\
        --out examples/avatars/avatar_JeanJack.png

Every step fails closed with an explicit message. The final avatar is
a square PNG under 1 MB (ask the user for the size bound and the final
aspect if they are not specified — defaults: square, 896px, 1 MB).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine import avatar  # noqa: E402


def cmd_bg(args: argparse.Namespace) -> None:
    avatar.prepare_background(args.src, args.out, size=args.size,
                              blur=args.blur, brightness=args.brightness)
    print("ok", args.out)


def cmd_cutout(args: argparse.Namespace) -> None:
    avatar.cutout_character(args.src, args.out)
    print("ok", args.out)


def cmd_anchor(args: argparse.Namespace) -> None:
    cx, bottom = avatar.detect_anchor(args.character)
    print(f"anchor cx_fraction={cx:.4f} bottom_fraction={bottom:.4f}")


def cmd_compose(args: argparse.Namespace) -> None:
    anchor = None
    if args.anchor and args.anchor != "auto":
        try:
            cx, bottom = (float(v) for v in args.anchor.split(","))
        except ValueError:
            sys.exit("avatar: --anchor expects 'cx_fraction,bottom_fraction'")
        anchor = (cx, bottom)
    out = avatar.build_avatar(args.bg, args.character, args.out, size=args.size,
                              headroom=args.headroom, plate_bottom=args.plate_bottom,
                              anchor=anchor, dx=args.dx, dy=args.dy,
                              max_bytes=(args.max_kb * 1024 if args.max_kb else None))
    print("ok", out)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("bg", help="square-crop + blur a sharp scene into a background")
    b.add_argument("--src", required=True, help="sharp source scene (e.g. bg_LAN_raw.png)")
    b.add_argument("--out", required=True, help="prepared background output")
    b.add_argument("--size", type=int, default=1024, help="square output size (default 1024)")
    b.add_argument("--blur", type=float, default=avatar.DEFAULT_BLUR,
                   help="Gaussian blur radius (default 5, 0 disables)")
    b.add_argument("--brightness", type=float, default=1.0,
                   help="brightness factor (1.0 = untouched)")
    b.set_defaults(func=cmd_bg)

    c = sub.add_parser("cutout", help="extract a character with a transparent background")
    c.add_argument("--src", required=True, help="raw render on a flat background")
    c.add_argument("--out", required=True, help="transparent cutout output")
    c.set_defaults(func=cmd_cutout)

    a = sub.add_parser("anchor", help="detect the nameplate anchor of a cutout")
    a.add_argument("--character", required=True, help="transparent cutout")
    a.set_defaults(func=cmd_anchor)

    m = sub.add_parser("compose", help="compose bg + character into the final avatar")
    m.add_argument("--bg", required=True, help="prepared background (square)")
    m.add_argument("--character", required=True, help="transparent character cutout")
    m.add_argument("--out", required=True, help="avatar output (PNG)")
    m.add_argument("--size", type=int, default=avatar.DEFAULT_SIZE,
                   help="square canvas size (default 896)")
    m.add_argument("--headroom", type=float, default=avatar.DEFAULT_HEADROOM,
                   help="free space above the head (default 0.15)")
    m.add_argument("--plate-bottom", type=float, default=avatar.DEFAULT_PLATE_BOTTOM,
                   help="anchor height in the frame (default 0.85)")
    m.add_argument("--anchor", default="auto",
                   help="'auto' (nameplate detection) or 'cx_fraction,bottom_fraction'")
    m.add_argument("--dx", type=int, default=0, help="nudge character right by N pixels (negative: left)")
    m.add_argument("--dy", type=int, default=0, help="nudge character down by N pixels (negative: up)")
    m.add_argument("--max-kb", type=int, default=None,
                   help="size bound in KiB — per-case constraint, ask the user "
                        "when absent (omit for no bound)")
    m.set_defaults(func=cmd_compose)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
