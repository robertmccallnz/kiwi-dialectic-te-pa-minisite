#!/usr/bin/env python3
"""
Ensure every sticker / poster / banner offers BOTH SVG and PNG so users
can either print at vector scale or load directly into social-media tools.

This script handles the formats that were missing after PR #11:

  1. Raster-only stickers (rhizome x4, general s01-s12, sheet-a4)
     → wrap the PNG in a clean SVG container (PNG embedded as base64
       data URI). Lets users open the asset in any SVG-aware tool
       (Inkscape, Figma, Illustrator) while preserving the original
       artwork exactly.

  2. SVG-only banners (Facebook/LinkedIn cover, X/Twitter banner)
     → render PNG versions via cairosvg for direct upload to social
       platforms that accept raster only.

Idempotent: re-running just overwrites the wrappers / re-renders PNGs.
"""

from __future__ import annotations

import base64
import sys
from pathlib import Path
from PIL import Image

try:
    import cairosvg
except ImportError:
    print("ERROR: cairosvg is required.  pip install cairosvg", file=sys.stderr)
    sys.exit(1)

REPO = Path(__file__).resolve().parent.parent
STICKERS_DIR = REPO / "social-kit" / "stickers"
BANNERS_DIR = REPO / "social-kit" / "banners"
BANNERS_PNG_DIR = BANNERS_DIR / "png"

# PNG stickers that lack an SVG.  We synthesise a vector wrapper for each.
RASTER_ONLY = [
    "sticker-rhizome-s01", "sticker-rhizome-s02",
    "sticker-rhizome-s03", "sticker-rhizome-s04",
    "sticker-s01", "sticker-s02", "sticker-s03", "sticker-s04",
    "sticker-s05", "sticker-s06", "sticker-s07", "sticker-s08",
    "sticker-s09", "sticker-s10", "sticker-s11", "sticker-s12",
    "sticker-sheet-a4",
]

# SVG-only banners.  We render PNGs alongside.
BANNERS = [
    "una-facebook-linkedin-cover-1640x624",
    "una-twitter-banner-1500x500",
]


SVG_WRAPPER_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!--
  Te Pā Tūwatawata — {slug}
  Vector wrapper around the original raster artwork.
  Open in Inkscape / Figma / Illustrator, or print at any size.
  Source PNG embedded as base64 data URI to keep the file self-contained.
  CC BY-NC-SA 4.0 · te-pa.org
-->
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{w}" height="{h}"
     viewBox="0 0 {w} {h}"
     preserveAspectRatio="xMidYMid meet">
  <title>{slug}</title>
  <desc>Te Pā Tūwatawata sticker — te-pa.org · CC BY-NC-SA 4.0</desc>
  <image x="0" y="0" width="{w}" height="{h}"
         xlink:href="data:image/png;base64,{b64}"/>
</svg>
"""


def wrap_png_in_svg(slug: str) -> bool:
    png_path = STICKERS_DIR / f"{slug}.png"
    svg_path = STICKERS_DIR / f"{slug}.svg"
    if not png_path.exists():
        print(f"  ✗ {slug}: source PNG missing")
        return False
    with Image.open(png_path) as im:
        w, h = im.size
    b64 = base64.b64encode(png_path.read_bytes()).decode("ascii")
    svg_path.write_text(
        SVG_WRAPPER_TEMPLATE.format(slug=slug, w=w, h=h, b64=b64),
        encoding="utf-8",
    )
    kb = svg_path.stat().st_size / 1024
    print(f"  ✓ {slug}.svg  ({w}×{h}, {kb:.0f} KB)")
    return True


def render_banner_png(slug: str) -> bool:
    svg_path = BANNERS_DIR / f"{slug}.svg"
    png_path = BANNERS_PNG_DIR / f"{slug}.png"
    if not svg_path.exists():
        print(f"  ✗ {slug}: source SVG missing")
        return False
    BANNERS_PNG_DIR.mkdir(parents=True, exist_ok=True)
    # Banners have explicit pixel dimensions in their filename;
    # render at native resolution.
    cairosvg.svg2png(
        bytestring=svg_path.read_bytes(),
        write_to=str(png_path),
        output_width=int(slug.rsplit("-", 1)[1].split("x")[0])
        if "x" in slug.rsplit("-", 1)[1]
        else None,
    )
    kb = png_path.stat().st_size / 1024
    print(f"  ✓ {slug}.png  ({kb:.0f} KB)")
    return True


def main() -> int:
    print("Wrapping raster-only stickers into SVG containers:")
    ok = 0
    for slug in RASTER_ONLY:
        if wrap_png_in_svg(slug):
            ok += 1
    print(f"\n  → {ok}/{len(RASTER_ONLY)} SVG wrappers written\n")

    print("Rendering PNG versions of SVG-only banners:")
    ok2 = 0
    for slug in BANNERS:
        if render_banner_png(slug):
            ok2 += 1
    print(f"\n  → {ok2}/{len(BANNERS)} banner PNGs written")
    return 0 if (ok == len(RASTER_ONLY) and ok2 == len(BANNERS)) else 1


if __name__ == "__main__":
    raise SystemExit(main())
