#!/usr/bin/env python3
"""
Recreate the 16 legacy stickers + the A4 sheet as clean, native SVG so
they no longer carry "kiwidialectic.com" baked into the pixels.

Design rules honoured
---------------------
- Typography-led (no AI-generated motifs, no aboriginal/TSI text).
- Slogans preserved VERBATIM from the original artwork.  We are only
  re-rendering the typography on a black canvas and swapping the
  footer URL from kiwidialectic.com -> te-pa.org.
- Motifs from the original set are recreated as simple geometric
  paths (spirals, scallops, lashings, kūmara mounds, fish-scale wave)
  using the same line-art style as the curated Unaunahi family.
- CC BY-NC-SA 4.0 retained.

Each sticker produces:
  social-kit/stickers/sticker-<slug>.svg   (native vector, no embedded raster)
  social-kit/stickers/png/sticker-<slug>.png  (1200px preview render)

The A4 sheet stacks all 12 general stickers in a 3×4 grid at A4 scale
ready for kiss-cut printing.
"""

from __future__ import annotations

import math
from pathlib import Path

import cairosvg

REPO = Path(__file__).resolve().parent.parent
STICKERS_DIR = REPO / "social-kit" / "stickers"
PNG_DIR = STICKERS_DIR / "png"
PNG_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Design tokens (match the Unaunahi family's typographic feel)
# ---------------------------------------------------------------------------
BG = "#0e0e0e"           # near-black canvas
INK = "#f4f0e8"          # cream
MUTED = "#6c6a63"        # muted label / body
RULE = "#3a3a3a"         # divider rule
ACCENT = "#c0392b"       # red accent reserved for emphasis

# Typography stacks
FONT_HEAD = "'Inter', 'Helvetica Neue', Arial, sans-serif"
FONT_BODY = "'Lora', 'Georgia', serif"

FOOTER = "te-pa.org"

LICENSE_LINE = (
    "Te Pā Tūwatawata · te-pa.org · CC BY-NC-SA 4.0"
)


# ---------------------------------------------------------------------------
# Sticker catalogue.  Slogans copied verbatim from the originals.
# Layout key:  "wide" = 1063×591, "square" = 1004×1004, "circle" = 945×945
# ---------------------------------------------------------------------------
STICKERS = [
    # --- General s01-s12 ---
    dict(slug="s01",  layout="wide",   eyebrow="TOITŪ",        head="TE WHENUA",      body="The land endures.",                   motif="spiral"),
    dict(slug="s02",  layout="wide",   eyebrow="RARAUNGA",     head="HEI TAONGA",     body="Data is a treasure.",                 motif="kumara"),
    dict(slug="s03",  layout="wide",   eyebrow="TINO",         head="RANGATIRATANGA", body="Absolute sovereignty.",               motif="lashing"),
    dict(slug="s04",  layout="wide",   eyebrow="KO TE REO",    head="TE MAURI",       body="The language is the life force.",     motif="beads"),
    dict(slug="s05",  layout="square", eyebrow="KA NGARO",     head=("TE REO","KA NGARO","TE IWI"),                              motif="koru_circles"),
    dict(slug="s06",  layout="square", eyebrow="IHUMĀTAO",     head=("E KORE","E MUTU"),                                          motif="spiral_large"),
    dict(slug="s07",  layout="square", eyebrow="HE RARAUNGA",  head=("NŌ WHAI","AO MĀORI"),                                       motif="unaunahi_band"),
    dict(slug="s08",  layout="square", eyebrow="KA WHAWHAI",   head=("TONU","MĀTOU"),                                             motif="pou_band"),
    dict(slug="s09",  layout="circle", eyebrow="TOITŪ",        head="TE TIRITI",      body="The Treaty endures.",                 motif="beads_band"),
    dict(slug="s10",  layout="circle", eyebrow="WHAI AO",      head="KAITIAKI",       body=("Guardians of the","digital world."), motif="koru_circles_top"),
    dict(slug="s11",  layout="circle", eyebrow="AI",           head=("KĀORE","E TIKA"),                                           motif="kumara_band"),
    dict(slug="s12",  layout="circle", eyebrow="HE WAKA",      head="EKE NOA",        body=("A canoe we're","all in together."), motif="unaunahi_top"),
    # --- Rhizome family ---
    dict(slug="rhizome-s01", layout="square", eyebrow="HE PAKIAKA", head=("KAI RARO","E TUPU","ANA"),       motif="rhizome_top"),
    dict(slug="rhizome-s02", layout="wide",   eyebrow="KIA WHAKATŌMURI", head=("TE HAERE","WHAKAMUA"),
         body=("Walk backwards","into the future."), motif="rhizome_left"),
    dict(slug="rhizome-s03", layout="circle", eyebrow="RAINA RERE", head=("LINES OF","FLIGHT"),             motif="rhizome_top"),
    dict(slug="rhizome-s04", layout="square", eyebrow="HE AHO", head=("TUKUTUKU","KAI RARO"),               motif="rhizome_top"),
]


# ---------------------------------------------------------------------------
# Motif builders — all line-art, no AI imagery
# ---------------------------------------------------------------------------
def motif_spiral(cx, cy, r):
    pts = []
    for i in range(0, 360 * 3, 6):
        t = math.radians(i)
        rad = r * (i / (360 * 3))
        pts.append(f"{cx + rad * math.cos(t):.1f},{cy + rad * math.sin(t):.1f}")
    return (
        f'<polyline points="{" ".join(pts)}" fill="none" stroke="{INK}" '
        f'stroke-width="3" stroke-linecap="round"/>'
        f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{cx:.1f}" y2="{cy + r * 1.3:.1f}" '
        f'stroke="{INK}" stroke-width="3"/>'
    )


def motif_kumara_row(x0, y0, count=8, w=30, h=42):
    """Triangular kūmara-mound row."""
    paths = []
    for i in range(count):
        x = x0 + i * w
        paths.append(
            f'<polygon points="{x:.1f},{y0:.1f} {x + w / 2:.1f},{y0 - h:.1f} '
            f'{x + w:.1f},{y0:.1f}" fill="{INK}"/>'
        )
    return "".join(paths)


def motif_pou_row(x0, y0, count=9, gap=20, w=12, h=85):
    """Pou (palisade post) row with cross-lashing."""
    posts = []
    for i in range(count):
        x = x0 + i * gap
        posts.append(
            f'<rect x="{x:.1f}" y="{y0 - h:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{INK}"/>'
        )
    # Horizontal lashing rails
    posts.append(
        f'<rect x="{x0 - 4:.1f}" y="{y0 - h * 0.55:.1f}" width="{count * gap + 8:.1f}" '
        f'height="3.5" fill="{INK}"/>'
    )
    posts.append(
        f'<rect x="{x0 - 4:.1f}" y="{y0 - h * 0.20:.1f}" width="{count * gap + 8:.1f}" '
        f'height="3.5" fill="{INK}"/>'
    )
    return "".join(posts)


def motif_beads_row(x0, y0, count=18, r=11, gap=22):
    """Open circles (te reo bead motif)."""
    return "".join(
        f'<circle cx="{x0 + i * gap:.1f}" cy="{y0:.1f}" r="{r:.1f}" '
        f'fill="none" stroke="{INK}" stroke-width="2.4"/>'
        for i in range(count)
    )


def motif_unaunahi_band(x0, y0, w, rows=3, scale_w=44, scale_h=22):
    """Fish-scale wave band."""
    paths = []
    cols = int(w / scale_w) + 2
    for r in range(rows):
        offset = (scale_w / 2) if r % 2 else 0
        for c in range(cols):
            cx = x0 + c * scale_w + offset
            cy = y0 + r * (scale_h * 0.95)
            paths.append(
                f'<path d="M {cx - scale_w / 2:.1f} {cy:.1f} '
                f'A {scale_w / 2:.1f} {scale_h:.1f} 0 0 1 {cx + scale_w / 2:.1f} {cy:.1f}" '
                f'fill="none" stroke="{INK}" stroke-width="1.6"/>'
            )
    return "".join(paths)


def motif_koru_circles(cx, cy, sizes=(85, 55, 30, 12)):
    """Concentric koru-evoking rings with a dot center."""
    out = []
    for r in sizes:
        out.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
            f'fill="none" stroke="{INK}" stroke-width="2"/>'
        )
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.5" fill="{INK}"/>')
    return "".join(out)


def motif_rhizome(cx, cy, r=60):
    """Stylised rhizome cluster: central node with radiating tipped stems."""
    out = [f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3" fill="{INK}"/>']
    angles = [-95, -75, -55, -35, -20, -8, 4, 18, 36, 60]
    for i, a in enumerate(angles):
        length = r * (0.8 + 0.04 * (i % 5))
        t = math.radians(a)
        x2 = cx + length * math.cos(t)
        y2 = cy + length * math.sin(t)
        # gentle curve
        mx = cx + length * 0.55 * math.cos(t + 0.18)
        my = cy + length * 0.55 * math.sin(t + 0.18)
        out.append(
            f'<path d="M {cx:.1f} {cy:.1f} Q {mx:.1f} {my:.1f} {x2:.1f} {y2:.1f}" '
            f'fill="none" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>'
        )
        out.append(f'<circle cx="{x2:.1f}" cy="{y2:.1f}" r="3" fill="{INK}"/>')
    return "".join(out)


# ---------------------------------------------------------------------------
# Composition helpers
# ---------------------------------------------------------------------------
def footer_band(w, h, target_url=FOOTER):
    """Bottom credit band: subtle rule + small URL."""
    return (
        f'<line x1="{w * 0.04:.1f}" y1="{h - 48:.1f}" '
        f'x2="{w * 0.96:.1f}" y2="{h - 48:.1f}" stroke="{RULE}" stroke-width="1"/>'
        f'<text x="{w / 2:.1f}" y="{h - 22:.1f}" font-family="{FONT_HEAD}" '
        f'font-size="20" font-weight="500" fill="{MUTED}" '
        f'text-anchor="middle" letter-spacing="1.2">{target_url}</text>'
    )


def head_text(x, y, head, size, line_h=None):
    """Render head text — string or tuple of lines."""
    if isinstance(head, str):
        lines = [head]
    else:
        lines = list(head)
    if line_h is None:
        line_h = int(size * 1.0)
    out = []
    for i, ln in enumerate(lines):
        out.append(
            f'<text x="{x:.1f}" y="{y + i * line_h:.1f}" font-family="{FONT_HEAD}" '
            f'font-size="{size}" font-weight="800" fill="{INK}" '
            f'letter-spacing="-1">{ln}</text>'
        )
    return "".join(out), len(lines) * line_h


def body_text(x, y, body, size=26):
    """Italic serif body line(s)."""
    if isinstance(body, str):
        lines = [body]
    else:
        lines = list(body)
    line_h = int(size * 1.25)
    out = []
    for i, ln in enumerate(lines):
        out.append(
            f'<text x="{x:.1f}" y="{y + i * line_h:.1f}" font-family="{FONT_BODY}" '
            f'font-size="{size}" font-style="italic" fill="{MUTED}">{ln}</text>'
        )
    return "".join(out)


def eyebrow_text(x, y, eyebrow, size=22):
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT_HEAD}" '
        f'font-size="{size}" font-weight="700" fill="{MUTED}" '
        f'letter-spacing="2.4">{eyebrow}</text>'
    )


# ---------------------------------------------------------------------------
# Layout functions per shape
# ---------------------------------------------------------------------------
def render_motif(name, w, h):
    """Position a motif on the canvas appropriately for the layout."""
    cx, cy = w / 2, h / 2
    if name == "spiral":
        return motif_spiral(w * 0.16, h * 0.55, 75)
    if name == "spiral_large":
        return motif_spiral(cx, h * 0.27, 110)
    if name == "kumara":
        return motif_kumara_row(w * 0.05, h * 0.55, count=8)
    if name == "kumara_band":
        return motif_kumara_row(w * 0.08, h * 0.22, count=20, w=int(w * 0.04), h=int(h * 0.07))
    if name == "lashing":
        return motif_pou_row(w * 0.05, h * 0.6)
    if name == "pou_band":
        return motif_pou_row(w * 0.18, h * 0.32, count=15, gap=int(w * 0.045))
    if name == "beads":
        return motif_beads_row(w * 0.02, h * 0.5)
    if name == "beads_band":
        return motif_beads_row(w * 0.08, h * 0.25, count=22, r=14, gap=int(w * 0.039))
    if name == "unaunahi_band":
        return motif_unaunahi_band(0, h * 0.10, w, rows=4)
    if name == "unaunahi_top":
        return motif_unaunahi_band(0, h * 0.12, w, rows=3)
    if name == "koru_circles":
        return motif_koru_circles(cx, h * 0.27)
    if name == "koru_circles_top":
        return motif_koru_circles(cx, h * 0.22, sizes=(70, 45, 25, 10))
    if name == "rhizome_top":
        return motif_rhizome(cx, h * 0.22, r=int(min(w, h) * 0.07))
    if name == "rhizome_left":
        return motif_rhizome(w * 0.16, h * 0.55, r=int(h * 0.16))
    return ""


def shell(w, h, content, *, shape="rect"):
    """Wrap content in the canvas chrome (background + optional circle clip)."""
    if shape == "circle":
        # 945x945 → circular outline + rounded rect background
        clip = (
            f'<defs><clipPath id="cl"><circle cx="{w/2:.1f}" cy="{h/2:.1f}" '
            f'r="{min(w,h)/2 - 14:.1f}"/></clipPath></defs>'
        )
        bg = (
            f'<rect width="{w}" height="{h}" fill="{BG}" rx="14"/>'
            f'<circle cx="{w/2:.1f}" cy="{h/2:.1f}" r="{min(w,h)/2 - 14:.1f}" '
            f'fill="{BG}" stroke="{INK}" stroke-width="2"/>'
        )
        inner = f'<g clip-path="url(#cl)">{content}</g>'
        return clip + bg + inner
    # rectangular
    return (
        f'<rect width="{w}" height="{h}" fill="{BG}" rx="14"/>' + content
    )


def compose_sticker(spec):
    layout = spec["layout"]
    if layout == "wide":
        w, h = 1063, 591
    elif layout == "square":
        w, h = 1004, 1004
    else:  # circle
        w, h = 945, 945

    parts = []
    # Eyebrow + head + body block
    if layout == "wide":
        text_x = w * 0.34
        parts.append(eyebrow_text(text_x, h * 0.16, spec["eyebrow"], size=24))
        # Auto-fit head size: shrink for long single-line heads on wide layout
        head = spec["head"]
        if isinstance(head, str):
            max_chars = len(head)
        else:
            max_chars = max(len(ln) for ln in head)
        # available width ≈ w - text_x - right margin (40px)
        avail = w - text_x - 40
        # Empirical: at size 78, uppercase char width ≈ 50px in Inter/Helvetica.
        # Pick the largest size that fits.
        head_size = 78
        for candidate in (78, 72, 66, 60, 56, 52, 48):
            if max_chars * (candidate * 0.62) <= avail:
                head_size = candidate
                break
        else:
            head_size = 48
        head_svg, head_h = head_text(text_x, h * 0.30, spec["head"], size=head_size)
        parts.append(head_svg)
        # Divider line under head
        parts.append(
            f'<line x1="{text_x:.1f}" y1="{h * 0.30 + head_h - 14:.1f}" '
            f'x2="{w - 70:.1f}" y2="{h * 0.30 + head_h - 14:.1f}" '
            f'stroke="{RULE}" stroke-width="1"/>'
        )
        if "body" in spec:
            parts.append(body_text(text_x, h * 0.30 + head_h + 30, spec["body"], size=28))
        # Vertical separator between motif and text
        parts.append(
            f'<line x1="{w * 0.30:.1f}" y1="{h * 0.10:.1f}" '
            f'x2="{w * 0.30:.1f}" y2="{h * 0.85:.1f}" stroke="{RULE}" stroke-width="1"/>'
        )

    elif layout == "square":
        # Centered head, motif anchored top
        text_x = w * 0.08
        # Horizontal divider under the motif (~mid)
        parts.append(
            f'<line x1="{w * 0.08:.1f}" y1="{h * 0.46:.1f}" '
            f'x2="{w * 0.92:.1f}" y2="{h * 0.46:.1f}" stroke="{RULE}" stroke-width="1"/>'
        )
        parts.append(eyebrow_text(text_x, h * 0.52, spec["eyebrow"], size=26))
        # Auto-fit head size for square
        head = spec["head"]
        max_chars = len(head) if isinstance(head, str) else max(len(ln) for ln in head)
        avail = w * 0.84
        head_size = 92
        for candidate in (92, 84, 76, 70, 64, 58):
            if max_chars * (candidate * 0.62) <= avail:
                head_size = candidate
                break
        else:
            head_size = 58
        head_svg, head_h = head_text(text_x, h * 0.60, spec["head"], size=head_size, line_h=int(head_size * 1.06))
        parts.append(head_svg)
        if "body" in spec:
            parts.append(body_text(text_x, h * 0.60 + head_h + 24, spec["body"], size=28))
        # Lower divider above footer
        parts.append(
            f'<line x1="{w * 0.08:.1f}" y1="{h * 0.85:.1f}" '
            f'x2="{w * 0.92:.1f}" y2="{h * 0.85:.1f}" stroke="{RULE}" stroke-width="1"/>'
        )

    else:  # circle
        text_x = w * 0.13
        parts.append(
            f'<line x1="{w * 0.13:.1f}" y1="{h * 0.45:.1f}" '
            f'x2="{w * 0.87:.1f}" y2="{h * 0.45:.1f}" stroke="{RULE}" stroke-width="1"/>'
        )
        parts.append(eyebrow_text(text_x, h * 0.51, spec["eyebrow"], size=24))
        # Auto-fit head size for circle
        head = spec["head"]
        max_chars = len(head) if isinstance(head, str) else max(len(ln) for ln in head)
        avail = w * 0.74
        head_size = 86
        for candidate in (86, 78, 72, 66, 60, 54):
            if max_chars * (candidate * 0.62) <= avail:
                head_size = candidate
                break
        else:
            head_size = 54
        head_svg, head_h = head_text(text_x, h * 0.59, spec["head"], size=head_size, line_h=int(head_size * 1.06))
        parts.append(head_svg)
        if "body" in spec:
            parts.append(body_text(text_x, h * 0.59 + head_h + 22, spec["body"], size=26))
        parts.append(
            f'<line x1="{w * 0.13:.1f}" y1="{h * 0.83:.1f}" '
            f'x2="{w * 0.87:.1f}" y2="{h * 0.83:.1f}" stroke="{RULE}" stroke-width="1"/>'
        )

    # Motif on top
    parts.append(render_motif(spec["motif"], w, h))

    # Footer URL
    parts.append(footer_band(w, h))

    shape = "circle" if layout == "circle" else "rect"
    body = shell(w, h, "".join(parts), shape=shape)

    svg = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
        f'<title>Te Pā Tūwatawata — {spec["slug"]}</title>\n'
        f'<desc>{LICENSE_LINE}</desc>\n'
        f'{body}\n'
        f'</svg>\n'
    )
    return svg, w, h


# ---------------------------------------------------------------------------
# A4 sheet — 3×4 grid of s01..s12 at print scale
# ---------------------------------------------------------------------------
def compose_sheet(stickers_by_slug):
    """A4 portrait sheet, 12-up.  Native A4 at 300dpi = 2480×3508."""
    W, H = 2480, 3508
    cols, rows = 3, 4
    margin = 80
    cell_w = (W - margin * 2) / cols
    cell_h = (H - margin * 2 - 220) / rows  # leave 220px header
    gap = 30

    parts = [f'<rect width="{W}" height="{H}" fill="white"/>']
    # Header band
    parts.append(
        f'<text x="{margin}" y="{margin + 70}" font-family="{FONT_HEAD}" '
        f'font-size="64" font-weight="800" fill="#111">Te Pā Tūwatawata</text>'
        f'<text x="{margin}" y="{margin + 120}" font-family="{FONT_HEAD}" '
        f'font-size="28" font-weight="500" fill="#555" letter-spacing="2">'
        f'A4 STICKER SHEET · 12-UP · KISS-CUT</text>'
        f'<text x="{W - margin}" y="{margin + 120}" font-family="{FONT_HEAD}" '
        f'font-size="22" font-weight="500" fill="#777" letter-spacing="1.4" '
        f'text-anchor="end">{FOOTER} · CC BY-NC-SA 4.0</text>'
        f'<line x1="{margin}" y1="{margin + 160}" x2="{W - margin}" y2="{margin + 160}" '
        f'stroke="#bbb" stroke-width="2"/>'
    )

    # Place 12 stickers in grid
    grid_slugs = [f"s{i:02d}" for i in range(1, 13)]
    y_start = margin + 220
    for idx, slug in enumerate(grid_slugs):
        col = idx % cols
        row = idx // cols
        x = margin + col * cell_w + gap / 2
        y = y_start + row * cell_h + gap / 2
        w = cell_w - gap
        h = cell_h - gap
        # cut guide
        parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="none" stroke="#cccccc" stroke-dasharray="6 6" stroke-width="1"/>'
        )
        # Embed sticker via nested svg (preserves the source viewBox)
        inner_svg = stickers_by_slug[slug]
        # Strip the XML prolog & outer <svg> tags, replace with positioned <svg>
        inner = inner_svg
        if inner.startswith("<?xml"):
            inner = inner.split("?>", 1)[1].lstrip()
        # Replace outer svg tag with positioned one
        # Find the dimensions of the inner sticker
        spec = next(s for s in STICKERS if s["slug"] == slug)
        if spec["layout"] == "wide":
            sw, sh = 1063, 591
        elif spec["layout"] == "square":
            sw, sh = 1004, 1004
        else:
            sw, sh = 945, 945
        # Scale to fit cell while keeping aspect
        scale = min(w / sw, h / sh)
        sw_s = sw * scale
        sh_s = sh * scale
        ox = x + (w - sw_s) / 2
        oy = y + (h - sh_s) / 2
        parts.append(
            f'<svg x="{ox:.1f}" y="{oy:.1f}" width="{sw_s:.1f}" height="{sh_s:.1f}" '
            f'viewBox="0 0 {sw} {sh}" preserveAspectRatio="xMidYMid meet">'
        )
        # Remove the inner <svg ...> and </svg>
        start = inner.find(">", inner.find("<svg")) + 1
        end = inner.rfind("</svg>")
        parts.append(inner[start:end])
        parts.append("</svg>")

    svg = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}">\n'
        f'<title>Te Pā Tūwatawata — A4 sticker sheet</title>\n'
        f'<desc>{LICENSE_LINE}</desc>\n'
        + "".join(parts)
        + "\n</svg>\n"
    )
    return svg, W, H


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("Recreating legacy stickers as clean native SVG + PNG:\n")
    written = {}
    for spec in STICKERS:
        svg, w, h = compose_sticker(spec)
        svg_path = STICKERS_DIR / f"sticker-{spec['slug']}.svg"
        svg_path.write_text(svg, encoding="utf-8")
        # render PNG @1200px-wide preview
        png_path = PNG_DIR / f"sticker-{spec['slug']}.png"
        cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(png_path),
                         output_width=1200)
        written[spec["slug"]] = svg
        print(f"  ✓ sticker-{spec['slug']}.svg  ({w}×{h})  + PNG preview")

    # Build A4 sheet from the rendered s01..s12 SVGs
    sheet_svg, sw, sh = compose_sheet(written)
    sheet_svg_path = STICKERS_DIR / "sticker-sheet-a4.svg"
    sheet_svg_path.write_text(sheet_svg, encoding="utf-8")
    sheet_png_path = PNG_DIR / "sticker-sheet-a4.png"
    cairosvg.svg2png(bytestring=sheet_svg.encode("utf-8"), write_to=str(sheet_png_path),
                     output_width=1200)
    print(f"\n  ✓ sticker-sheet-a4.svg  (A4 portrait, 12-up) + PNG preview")

    # Replace the legacy PNGs at the original (non-png/) path so any external
    # links to /social-kit/stickers/sticker-s01.png get the clean version.
    for spec in STICKERS:
        legacy_png = STICKERS_DIR / f"sticker-{spec['slug']}.png"
        clean_png = PNG_DIR / f"sticker-{spec['slug']}.png"
        legacy_png.write_bytes(clean_png.read_bytes())
    legacy_sheet = STICKERS_DIR / "sticker-sheet-a4.png"
    legacy_sheet.write_bytes((PNG_DIR / "sticker-sheet-a4.png").read_bytes())
    print("\n  ✓ Legacy PNG locations overwritten with clean versions")

    print(f"\nTotal: {len(STICKERS)} stickers + A4 sheet recreated.")


if __name__ == "__main__":
    main()
