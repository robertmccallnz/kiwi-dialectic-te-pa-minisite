#!/usr/bin/env python3
"""
Generate per-language campaign memes for Te Pā minisite.

Produces 6 memes × 5 languages = 30 PNGs at 1080×1080.

Languages:
  en — English
  mi — Te Reo Māori
  pt — Português
  gn — Guaraní
  sm — Gagana Sāmoa

Output: social-kit/campaign-{meme_id}-{lang}.png

Brand:
  - 1080×1080
  - Red (#c0392b) & Black (#0a0a0a)
  - Cream text (#f4ede0)
  - Niho-taniwha triangular borders (top/bottom)
  - Noto Serif (italic for te reo / native lines) + Noto Sans (display)
  - Footer: "Te Pā Tūwatawata · kiwidialectic.com"
"""
import os
import sys
import math
from PIL import Image, ImageDraw, ImageFont

# ─── Paths ──────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "social-kit")
os.makedirs(OUT_DIR, exist_ok=True)

# ─── Brand constants ────────────────────────────────────────────────────
W, H = 1080, 1080
RED = (192, 57, 43)
BLACK = (10, 10, 10)
CREAM = (244, 237, 224)
CREAM_MUTED = (244, 237, 224, 200)  # used selectively
GREY_MUTED = (180, 174, 162)

# ─── Fonts ──────────────────────────────────────────────────────────────
FONT_DIR = "/usr/share/fonts/truetype/noto"
F_SERIF_REG = f"{FONT_DIR}/NotoSerif-Regular.ttf"
F_SERIF_BOLD = f"{FONT_DIR}/NotoSerif-Bold.ttf"
F_SERIF_ITALIC = f"{FONT_DIR}/NotoSerif-Italic.ttf"
F_SERIF_BOLDITALIC = f"{FONT_DIR}/NotoSerif-BoldItalic.ttf"
F_SANS_REG = f"{FONT_DIR}/NotoSans-Regular.ttf"
F_SANS_BOLD = f"{FONT_DIR}/NotoSans-Bold.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

# ─── Niho-taniwha border (triangular teeth) ────────────────────────────
def draw_niho_border(draw, side="top", color=BLACK, bg=RED, tooth_w=36, tooth_h=44, band_h=64):
    """Draw a row of triangular teeth at the top or bottom."""
    if side == "top":
        y0 = 0
        # background band
        draw.rectangle([0, y0, W, y0 + band_h], fill=bg)
        # teeth pointing down
        n = W // tooth_w + 1
        for i in range(n):
            x = i * tooth_w
            draw.polygon(
                [(x, y0 + band_h - tooth_h), (x + tooth_w / 2, y0 + band_h), (x + tooth_w, y0 + band_h - tooth_h)],
                fill=color,
            )
        # also a small inverted line at the very top so it reads as a notched edge
        for i in range(n):
            x = i * tooth_w
            draw.polygon(
                [(x, y0), (x + tooth_w / 2, y0 + tooth_h * 0.45), (x + tooth_w, y0)],
                fill=color,
            )
    else:  # bottom
        y1 = H
        draw.rectangle([0, y1 - band_h, W, y1], fill=bg)
        n = W // tooth_w + 1
        for i in range(n):
            x = i * tooth_w
            draw.polygon(
                [(x, y1 - band_h + tooth_h), (x + tooth_w / 2, y1 - band_h), (x + tooth_w, y1 - band_h + tooth_h)],
                fill=color,
            )
        for i in range(n):
            x = i * tooth_w
            draw.polygon(
                [(x, y1), (x + tooth_w / 2, y1 - tooth_h * 0.45), (x + tooth_w, y1)],
                fill=color,
            )

# ─── Text helpers ───────────────────────────────────────────────────────
def measure(draw, text, fnt):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def wrap_lines(draw, text, fnt, max_w):
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        tw, _ = measure(draw, trial, fnt)
        if tw <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def draw_text_block(draw, text, fnt, x, y, color=CREAM, max_w=None, line_gap=8, align="left"):
    """Render wrapped text block; return (final_y, height_used)."""
    if max_w is None:
        max_w = W - 100
    lines = wrap_lines(draw, text, fnt, max_w)
    cy = y
    for ln in lines:
        tw, th = measure(draw, ln, fnt)
        if align == "center":
            cx = (W - tw) / 2
        elif align == "right":
            cx = W - x - tw
        else:
            cx = x
        draw.text((cx, cy), ln, font=fnt, fill=color)
        cy += th + line_gap
    return cy

# ─── Unaunahi (fish-scale) motif background ───────────────────────────
def draw_unaunahi_motif(img, x0=0, y0=0, x1=None, y1=None, base_color=BLACK,
                       scale=92, alpha=22, line_width=2):
    """
    Paint a low-opacity unaunahi (fish-scale) pattern across a region.
    Uses a transparent overlay so the underlying flat color shows through.

    Args:
        img: PIL.Image (RGB) to paint onto
        x0,y0,x1,y1: region bounds (defaults to full canvas)
        base_color: BLACK or RED — controls highlight color used for arcs
        scale: arc diameter in px (bigger = larger scales)
        alpha: line opacity (0–255) — lower = more subtle
        line_width: stroke thickness in px
    """
    if x1 is None:
        x1 = img.width
    if y1 is None:
        y1 = img.height
    w = x1 - x0
    h = y1 - y0
    if w <= 0 or h <= 0:
        return
    # Choose highlight color: on red use cream, on black use cream as well
    # (subtle warm highlight reads as carved/painted texture either way)
    if base_color == RED:
        hi = (255, 230, 200, alpha)  # warm cream on red
    else:
        hi = (244, 237, 224, alpha)  # cream on black

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    r = scale // 2
    # Stagger rows so scales overlap (each row offset by r horizontally)
    row_step = int(r * 1.05)  # slight vertical compression so scales nest
    rows = h // row_step + 2
    cols = w // scale + 2
    for ri in range(-1, rows):
        cy_arc = ri * row_step
        offset = (r if ri % 2 else 0)
        for ci in range(-1, cols):
            cx_arc = ci * scale + offset
            # Draw the upper arc of the scale (a half-circle opening down)
            bbox = [cx_arc, cy_arc - r, cx_arc + scale, cy_arc + r]
            od.arc(bbox, start=180, end=360, fill=hi, width=line_width)
    # Composite onto base image
    img.paste(overlay, (x0, y0), overlay)

# ─── Layout templates ──────────────────────────────────────────────────
def base_canvas(bg=BLACK, motif=True):
    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)
    if motif:
        draw_unaunahi_motif(img, 0, 0, W, H, base_color=bg)
        # re-bind draw to the same image (paste doesn't invalidate, but be safe)
        draw = ImageDraw.Draw(img)
    return img, draw

def add_footer(draw, footer="Te Pā Tūwatawata  ·  kiwidialectic.com",
               subfooter="Created by www.kiwidialectic.com"):
    # Place footer ABOVE the bottom niho band (band_h=60)
    f1 = font(F_SANS_BOLD, 26)
    f2 = font(F_SANS_REG, 18)
    draw.text((48, H - 130), footer, font=f1, fill=CREAM)
    draw.text((48, H - 95), subfooter, font=f2, fill=CREAM)

# ─── Template A: Big slogan over a coloured field (Raupatu) ────────────
def template_slogan(slogan_lines, italic_caption, accent_line, body, cta):
    """
    Layout (matches campaign-raupatu.png):
      - Top half RED with big white slogan
      - Niho divider
      - Bottom half BLACK with italic caption (cream), accent line (red),
        body (cream), CTA (red)
    """
    img, draw = base_canvas(bg=RED)
    # bottom black half
    draw.rectangle([0, H // 2 + 30, W, H], fill=BLACK)
    # re-apply unaunahi motif on the black bottom half (covered by the rectangle)
    draw_unaunahi_motif(img, 0, H // 2 + 30, W, H, base_color=BLACK)
    draw = ImageDraw.Draw(img)
    # niho divider in middle
    band_y = H // 2 - 20
    draw_niho_border_at(draw, y=band_y, color=BLACK, bg=RED, tooth_w=36, tooth_h=40, band_h=70, point="down")
    # Slogan — auto-size based on longest line so it never overlaps
    candidate = 100
    while candidate > 60:
        f_slogan = font(F_SANS_BOLD, candidate)
        max_tw = max(measure(draw, ln, f_slogan)[0] for ln in slogan_lines)
        if max_tw <= W - 120:
            break
        candidate -= 6
    f_slogan = font(F_SANS_BOLD, candidate)
    # vertically center slogan in top red half (top ~ y0..H/2-20)
    line_h = candidate + 18
    total_h = line_h * len(slogan_lines)
    sy = (H // 2 - 20 - total_h) // 2 + 20
    if sy < 90:
        sy = 90
    last_baseline = sy
    last_width = 0
    for line in slogan_lines:
        tw, th = measure(draw, line, f_slogan)
        draw.text(((W - tw) / 2, sy), line, font=f_slogan, fill=CREAM)
        last_baseline = sy + th
        last_width = max(last_width, tw)
        sy += line_h
    # Typography accent: short cream bar centered below the slogan, just above
    # the niho divider band (band_y = H//2 - 20). Clamp so it never overlaps text.
    bar_w = min(160, max(80, last_width // 3))
    bar_x = (W - bar_w) // 2
    # niho band starts at band_y; place bar 24px above it but at least 20px below text
    bar_y_target = band_y - 24
    bar_y_min = last_baseline + 22
    bar_y = max(bar_y_min, bar_y_target)
    if bar_y + 4 < band_y - 6:
        draw.rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + 4], fill=CREAM)
    # Italic caption
    f_italic = font(F_SERIF_ITALIC, 40)
    f_accent = font(F_SERIF_BOLDITALIC, 44)
    f_body = font(F_SANS_REG, 28)
    f_cta = font(F_SANS_BOLD, 28)

    cy = H // 2 + 90
    if italic_caption:
        tw, th = measure(draw, italic_caption, f_italic)
        draw.text(((W - tw) / 2, cy), italic_caption, font=f_italic, fill=CREAM)
        cy += th + 16
    if accent_line:
        tw, th = measure(draw, accent_line, f_accent)
        draw.text(((W - tw) / 2, cy), accent_line, font=f_accent, fill=RED)
        cy += th + 28

    # body wrapped, centered
    if body:
        lines = wrap_lines(draw, body, f_body, W - 120)
        for ln in lines:
            tw, th = measure(draw, ln, f_body)
            draw.text(((W - tw) / 2, cy), ln, font=f_body, fill=CREAM)
            cy += th + 6
        cy += 18

    if cta:
        tw, th = measure(draw, cta, f_cta)
        draw.text(((W - tw) / 2, cy), cta, font=f_cta, fill=RED)

    # bottom niho border
    draw_niho_border(draw, side="bottom", color=BLACK, bg=RED, tooth_w=36, tooth_h=38, band_h=60)
    add_footer(draw)
    return img

def draw_niho_border_at(draw, y, color=BLACK, bg=RED, tooth_w=36, tooth_h=40, band_h=60, point="down"):
    """Niho border at arbitrary y; teeth point up or down."""
    draw.rectangle([0, y, W, y + band_h], fill=bg)
    n = W // tooth_w + 1
    if point == "down":
        for i in range(n):
            x = i * tooth_w
            draw.polygon(
                [(x, y + band_h - tooth_h), (x + tooth_w / 2, y + band_h), (x + tooth_w, y + band_h - tooth_h)],
                fill=color,
            )
    else:
        for i in range(n):
            x = i * tooth_w
            draw.polygon(
                [(x, y + tooth_h), (x + tooth_w / 2, y), (x + tooth_w, y + tooth_h)],
                fill=color,
            )

# ─── Template B: Headline + numbered list (3 Questions) ───────────────
def template_list(small_italic, headline, items, footer_line, cta_line, hashtags):
    img, draw = base_canvas(bg=BLACK)
    draw_niho_border(draw, side="top", color=RED, bg=BLACK, tooth_w=32, tooth_h=46, band_h=60)

    x = 60
    cy = 110
    if small_italic:
        f = font(F_SERIF_ITALIC, 30)
        draw.text((x, cy), small_italic, font=f, fill=CREAM)
        cy += 40
    if headline:
        f = font(F_SANS_BOLD, 50)
        lines = wrap_lines(draw, headline, f, W - 2 * x)
        for ln in lines:
            draw.text((x, cy), ln, font=f, fill=RED)
            _, th = measure(draw, ln, f)
            cy += th + 4
        cy += 8
        # underline
        draw.rectangle([x, cy, W - x, cy + 3], fill=RED)
        cy += 30

    # items
    f_num = font(F_SANS_BOLD, 28)
    f_q = font(F_SERIF_BOLDITALIC, 36)
    f_a = font(F_SANS_REG, 24)
    for i, (q, a) in enumerate(items, start=1):
        num = f"{i:02d}"
        # red circle
        circ_d = 56
        cx = x + circ_d // 2
        draw.ellipse([x, cy, x + circ_d, cy + circ_d], fill=RED)
        tw, th = measure(draw, num, f_num)
        draw.text((x + (circ_d - tw) / 2, cy + (circ_d - th) / 2 - 4), num, font=f_num, fill=CREAM)
        # question
        qx = x + circ_d + 22
        draw.text((qx, cy - 6), q, font=f_q, fill=CREAM)
        # answer
        _, qh = measure(draw, q, f_q)
        a_lines = wrap_lines(draw, a, f_a, W - qx - 60)
        ay = cy + qh + 4
        for ln in a_lines:
            draw.text((qx, ay), ln, font=f_a, fill=GREY_MUTED)
            _, ath = measure(draw, ln, f_a)
            ay += ath + 4
        cy = max(ay, cy + circ_d) + 28
        # separator
        draw.line([(x, cy - 14), (W - x, cy - 14)], fill=(60, 55, 50), width=1)

    cy += 8
    if footer_line:
        f_fl = font(F_SANS_BOLD, 30)
        draw.text((x, cy), footer_line, font=f_fl, fill=CREAM)
        cy += 44
    if cta_line:
        f_cta = font(F_SANS_BOLD, 26)
        draw.text((x, cy), cta_line, font=f_cta, fill=RED)
        cy += 40

    if hashtags:
        f_h = font(F_SANS_REG, 18)
        hx = x
        for tag in hashtags:
            tw, _ = measure(draw, tag, f_h)
            if hx + tw > W - x:
                break
            draw.text((hx, H - 200), tag, font=f_h, fill=GREY_MUTED)
            hx += tw + 20

    draw_niho_border(draw, side="bottom", color=RED, bg=BLACK, tooth_w=32, tooth_h=46, band_h=60)
    # red footer band-ish — draw a thin red band underneath the niho
    add_footer(draw)
    return img

# ─── Template C: Pull-quote (Te Mana Raraunga) ─────────────────────────
def template_quote(eyebrow, quote, attribution, body, native_line, english_line, cta, hashtags):
    img, draw = base_canvas(bg=BLACK)
    # top decorative band — niho with circles look (approx with niho border)
    draw_niho_border(draw, side="top", color=RED, bg=BLACK, tooth_w=32, tooth_h=46, band_h=70)
    # cream draw circles inside the red — small accent dots
    for i in range(0, W, 64):
        draw.ellipse([i + 16, 6, i + 36, 26], outline=CREAM, width=2)

    x = 60
    cy = 110
    if eyebrow:
        f = font(F_SANS_BOLD, 22)
        draw.text((x, cy), eyebrow, font=f, fill=RED)
        cy += 36
    # red left bar + quote
    qbar_top = cy
    f_q = font(F_SERIF_BOLDITALIC, 48)
    qlines = wrap_lines(draw, f"“{quote}”", f_q, W - 2 * x - 30)
    qy = cy
    for ln in qlines:
        draw.text((x + 22, qy), ln, font=f_q, fill=CREAM)
        _, th = measure(draw, ln, f_q)
        qy += th + 6
    qy += 8
    if attribution:
        f_at = font(F_SANS_REG, 24)
        draw.text((x + 22, qy), f"— {attribution}", font=f_at, fill=RED)
        _, ath = measure(draw, attribution, f_at)
        qy += ath + 18
    # left bar height
    draw.rectangle([x, qbar_top, x + 6, qy - 8], fill=RED)

    cy = qy + 8
    draw.line([(x, cy), (W - x, cy)], fill=(70, 65, 60), width=2)
    cy += 26

    if body:
        f_b = font(F_SANS_REG, 26)
        b_lines = wrap_lines(draw, body, f_b, W - 2 * x)
        for ln in b_lines:
            draw.text((x, cy), ln, font=f_b, fill=CREAM)
            _, th = measure(draw, ln, f_b)
            cy += th + 6
        cy += 18

    if native_line:
        f_n = font(F_SERIF_ITALIC, 38)
        draw.text((x, cy), native_line, font=f_n, fill=CREAM)
        _, th = measure(draw, native_line, f_n)
        cy += th + 8
    if english_line:
        f_e = font(F_SANS_BOLD, 30)
        draw.text((x, cy), english_line, font=f_e, fill=RED)
        _, th = measure(draw, english_line, f_e)
        cy += th + 22

    if cta:
        f_c = font(F_SANS_BOLD, 26)
        draw.text((x, cy), cta, font=f_c, fill=CREAM)
        cy += 40

    if hashtags:
        f_h = font(F_SANS_REG, 18)
        hx = x
        hy = H - 200
        for tag in hashtags:
            tw, _ = measure(draw, tag, f_h)
            if hx + tw > W - x:
                break
            draw.text((hx, hy), tag, font=f_h, fill=GREY_MUTED)
            hx += tw + 20

    draw_niho_border(draw, side="bottom", color=RED, bg=BLACK, tooth_w=32, tooth_h=46, band_h=60)
    add_footer(draw)
    return img

# ─── Template D: Bullet principles (Data Sovereignty) ─────────────────
def template_principles(small_italic, headline, body, bullets, footer_line, cta, hashtags):
    img, draw = base_canvas(bg=BLACK)
    draw_niho_border(draw, side="top", color=RED, bg=BLACK, tooth_w=32, tooth_h=46, band_h=60)
    x = 60
    cy = 100
    if small_italic:
        f = font(F_SERIF_ITALIC, 34)
        draw.text((x, cy), small_italic, font=f, fill=CREAM)
        cy += 50
    if headline:
        f = font(F_SANS_BOLD, 50)
        lines = wrap_lines(draw, headline, f, W - 2 * x)
        for ln in lines:
            draw.text((x, cy), ln, font=f, fill=RED)
            _, th = measure(draw, ln, f)
            cy += th + 4
        # red underline
        draw.rectangle([x, cy + 4, W - x, cy + 7], fill=RED)
        cy += 30

    if body:
        f = font(F_SANS_REG, 26)
        lines = wrap_lines(draw, body, f, W - 2 * x)
        for ln in lines:
            draw.text((x, cy), ln, font=f, fill=CREAM)
            _, th = measure(draw, ln, f)
            cy += th + 6
        cy += 16
        draw.line([(x, cy), (W - x, cy)], fill=(70, 65, 60), width=1)
        cy += 28

    f_label = font(F_SANS_BOLD, 30)
    f_desc = font(F_SANS_REG, 22)
    for label, desc in bullets:
        # red bullet dot
        bullet_d = 14
        draw.ellipse([x, cy + 12, x + bullet_d, cy + 12 + bullet_d], fill=RED)
        lx = x + bullet_d + 14
        draw.text((lx, cy), label, font=f_label, fill=CREAM)
        _, lh = measure(draw, label, f_label)
        cy += lh + 4
        # description, wrapped
        dlines = wrap_lines(draw, desc, f_desc, W - lx - 60)
        for ln in dlines:
            draw.text((lx, cy), ln, font=f_desc, fill=GREY_MUTED)
            _, th = measure(draw, ln, f_desc)
            cy += th + 4
        cy += 14

    cy += 8
    if footer_line:
        f = font(F_SANS_BOLD, 26)
        lines = wrap_lines(draw, footer_line, f, W - 2 * x)
        for ln in lines:
            draw.text((x, cy), ln, font=f, fill=RED)
            _, th = measure(draw, ln, f)
            cy += th + 4
        cy += 6
    if cta:
        f = font(F_SANS_BOLD, 26)
        draw.text((x, cy), cta, font=f, fill=CREAM)
        cy += 36

    if hashtags:
        f = font(F_SANS_REG, 18)
        hx = x
        hy = H - 200
        for tag in hashtags:
            tw, _ = measure(draw, tag, f)
            if hx + tw > W - x:
                break
            draw.text((hx, hy), tag, font=f, fill=GREY_MUTED)
            hx += tw + 20

    draw_niho_border(draw, side="bottom", color=RED, bg=BLACK, tooth_w=32, tooth_h=46, band_h=60)
    add_footer(draw)
    return img

# ─── Template E: CTA card (Enrol) — red bg, big text ──────────────────
def template_cta(big_headline_lines, italic_sub, italic_brand, body_lines, url, modules_lines):
    img, draw = base_canvas(bg=RED)
    draw_niho_border(draw, side="top", color=BLACK, bg=RED, tooth_w=36, tooth_h=44, band_h=60)
    cy = 110
    # Auto-size headline so longest line fits
    candidate = 110
    while candidate > 60:
        f_big = font(F_SANS_BOLD, candidate)
        max_tw = max(measure(draw, ln, f_big)[0] for ln in big_headline_lines)
        if max_tw <= W - 120:
            break
        candidate -= 6
    f_big = font(F_SANS_BOLD, candidate)
    line_h = candidate + 18
    for ln in big_headline_lines:
        tw, th = measure(draw, ln, f_big)
        draw.text(((W - tw) / 2, cy), ln, font=f_big, fill=CREAM)
        cy += line_h
    cy += 14
    if italic_sub:
        f = font(F_SERIF_ITALIC, 46)
        tw, th = measure(draw, italic_sub, f)
        draw.text(((W - tw) / 2, cy), italic_sub, font=f, fill=BLACK)
        cy += th + 8
    if italic_brand:
        f = font(F_SERIF_ITALIC, 32)
        tw, th = measure(draw, italic_brand, f)
        draw.text(((W - tw) / 2, cy), italic_brand, font=f, fill=BLACK)
        cy += th + 18
    # divider line
    draw.line([(120, cy), (W - 120, cy)], fill=BLACK, width=3)
    cy += 28

    f_b = font(F_SANS_REG, 28)
    for ln in body_lines:
        tw, th = measure(draw, ln, f_b)
        draw.text(((W - tw) / 2, cy), ln, font=f_b, fill=BLACK)
        cy += th + 4
    cy += 24

    if url:
        f_u = font(F_SANS_BOLD, 54)
        tw, th = measure(draw, url, f_u)
        draw.text(((W - tw) / 2, cy), url, font=f_u, fill=CREAM)
        cy += th + 28

    f_m = font(F_SANS_BOLD, 22)
    for ln in modules_lines:
        tw, th = measure(draw, ln, f_m)
        draw.text(((W - tw) / 2, cy), ln, font=f_m, fill=BLACK)
        cy += th + 4

    # cream small footer above the niho band
    f_foot = font(F_SANS_REG, 20)
    foot = "Created by www.kiwidialectic.com"
    tw, _ = measure(draw, foot, f_foot)
    draw.text(((W - tw) / 2, H - 95), foot, font=f_foot, fill=BLACK)
    # bottom niho border in black on red
    draw_niho_border(draw, side="bottom", color=BLACK, bg=RED, tooth_w=36, tooth_h=44, band_h=60)
    return img

# ─── Template F: Anamata — italic native + body, with motif watermark ──
def template_anamata(eyebrow, italic_native, english_sub, italic_quote_native, italic_quote_red, eng_caption, body, hashtags):
    img, draw = base_canvas(bg=BLACK)
    draw_niho_border(draw, side="top", color=RED, bg=BLACK, tooth_w=32, tooth_h=46, band_h=60)
    x = 60
    cy = 100
    if eyebrow:
        f = font(F_SANS_BOLD, 22)
        draw.text((x, cy), eyebrow, font=f, fill=RED)
        cy += 36

    # large italic
    f_big = font(F_SERIF_BOLDITALIC, 60)
    lines = wrap_lines(draw, italic_native, f_big, W - 2 * x)
    for ln in lines:
        tw, th = measure(draw, ln, f_big)
        draw.text(((W - tw) / 2, cy), ln, font=f_big, fill=CREAM)
        cy += th + 6
    cy += 14
    f_eng = font(F_SANS_BOLD, 42)
    lines = wrap_lines(draw, english_sub, f_eng, W - 2 * x)
    for ln in lines:
        tw, th = measure(draw, ln, f_eng)
        draw.text(((W - tw) / 2, cy), ln, font=f_eng, fill=RED)
        cy += th + 4
    cy += 24
    draw.line([(x, cy), (W - x, cy)], fill=RED, width=2)
    cy += 30

    f_qn = font(F_SERIF_ITALIC, 30)
    f_qr = font(F_SERIF_BOLDITALIC, 36)
    f_e = font(F_SANS_REG, 24)
    if italic_quote_native:
        lines = wrap_lines(draw, italic_quote_native, f_qn, W - 2 * x)
        for ln in lines:
            tw, th = measure(draw, ln, f_qn)
            draw.text(((W - tw) / 2, cy), ln, font=f_qn, fill=CREAM)
            cy += th + 4
    if italic_quote_red:
        tw, th = measure(draw, italic_quote_red, f_qr)
        draw.text(((W - tw) / 2, cy), italic_quote_red, font=f_qr, fill=RED)
        cy += th + 10
    if eng_caption:
        lines = wrap_lines(draw, eng_caption, f_e, W - 2 * x)
        for ln in lines:
            tw, th = measure(draw, ln, f_e)
            draw.text(((W - tw) / 2, cy), ln, font=f_e, fill=GREY_MUTED)
            cy += th + 4
        cy += 20
    draw.line([(x, cy), (W - x, cy)], fill=(70, 65, 60), width=1)
    cy += 26

    if body:
        f_b = font(F_SANS_REG, 24)
        lines = wrap_lines(draw, body, f_b, W - 2 * x)
        for ln in lines:
            tw, th = measure(draw, ln, f_b)
            draw.text(((W - tw) / 2, cy), ln, font=f_b, fill=CREAM)
            cy += th + 4

    if hashtags:
        f = font(F_SANS_REG, 18)
        hx = x
        hy = H - 200
        for tag in hashtags:
            tw, _ = measure(draw, tag, f)
            if hx + tw > W - x:
                break
            draw.text((hx, hy), tag, font=f, fill=GREY_MUTED)
            hx += tw + 20

    draw_niho_border(draw, side="bottom", color=RED, bg=BLACK, tooth_w=32, tooth_h=46, band_h=60)
    add_footer(draw)
    return img


# ═══ CONTENT — 6 memes × 5 languages ═══════════════════════════════════
# en, mi, pt, gn, sm

CONTENT = {
    # ── 1. RAUPATU ─────────────────────────────────────────────────
    "raupatu": {
        "tpl": "slogan",
        "en": {
            "slogan_lines": ["RAUPATU", "IS NOT", "HISTORY."],
            "italic_caption": "He raupatu matihiko tēnei.",
            "accent_line": "It became digital.",
            "body": "AI companies extract te reo Māori, mātauranga Māori, and Indigenous knowledge — without consent, without return. The mechanism is new. The logic is the same.",
            "cta": "Learn more — Te Pā Tūwatawata · Free course",
        },
        "mi": {
            "slogan_lines": ["EHARA", "TE RAUPATU", "I NGĀ RĀ O MUA."],
            "italic_caption": "He raupatu matihiko tēnei.",
            "accent_line": "Kua hangaia matihikotia.",
            "body": "Kei te tangohia e ngā kamupene AI te reo Māori, te mātauranga Māori, me ngā mōhiotanga taketake — kāore he whakaae, kāore he whakahokinga. He hou te tikanga. He rite tonu te aronga.",
            "cta": "Akona atu — Te Pā Tūwatawata · Akoranga kore utu",
        },
        "pt": {
            "slogan_lines": ["A USURPAÇÃO", "NÃO É", "HISTÓRIA."],
            "italic_caption": "É uma usurpação digital.",
            "accent_line": "Tornou-se digital.",
            "body": "Empresas de IA extraem o te reo Māori, o conhecimento Māori e os saberes Indígenas — sem consentimento, sem retorno. O mecanismo é novo. A lógica é a mesma.",
            "cta": "Saiba mais — Te Pā Tūwatawata · Curso gratuito",
        },
        "gn": {
            "slogan_lines": ["MBA'EJOPY", "NDAHA'EI", "TEMBIASAKUE."],
            "italic_caption": "Ko'ãva ha'e mba'ejopy digital.",
            "accent_line": "Oñembohape digital-pe.",
            "body": "Umi mba'apohára IA omonguera Indígena-kuéra rembikuaa, iñe'ẽ ha imba'éva — herapegua'ỹre, ndoñembohovái avave. Pyahu pe tape. Peteĩchante upe apopyre.",
            "cta": "Eikuaave — Te Pā Tūwatawata · Mbo'esyry rei",
        },
        "sm": {
            "slogan_lines": ["O LE FAOA", "E LĒ SE", "TALAFAASOLOPITO."],
            "italic_caption": "O se faoa fa'akomepiuta lenei.",
            "accent_line": "Ua faia i le ata fa'atekonolosi.",
            "body": "O kamupani AI o lo'o aveese gagana Māori, le poto masani a Māori, ma le poto a tagata Moni Aboriginal — e aunoa ma se fa'atagaga, e aunoa ma se toe foa'iina mai. Ua fou le auala. Ua tutusa pea le mafua'aga.",
            "cta": "A'oa'o atili — Te Pā Tūwatawata · A'oa'oga fua",
        },
    },

    # ── 2. 3 QUESTIONS ────────────────────────────────────────────
    "3-questions": {
        "tpl": "list",
        "en": {
            "small_italic": "3 Pātai Mō Ia AI Pūnaha",
            "headline": "3 Questions to Ask About Any AI System",
            "items": [
                ("Ko wai nāu i hanga?", "Who built it — and whose knowledge did they use?"),
                ("Ko wai e tiaki ana?", "Who controls it — and who is accountable?"),
                ("Ko wai e painga ana?", "Who benefits — and who is harmed?"),
            ],
            "footer_line": "Te Pā Tūwatawata teaches you how to answer these.",
            "cta_line": "Free course · kiwidialectic.com",
            "hashtags": ["#DataSovereignty", "#TinoRangatiratanga", "#AotearoaAI", "#KaupapaMāori"],
        },
        "mi": {
            "small_italic": "3 Pātai Mō Ia AI Pūnaha",
            "headline": "3 Pātai Mō Ngā Pūnaha AI Katoa",
            "items": [
                ("Nā wai i hanga?", "Nā wai i hanga — ā, nā wai te mātauranga?"),
                ("Nā wai e tiaki?", "Nā wai e whakahaere — nā wai e takohanga?"),
                ("Nā wai te painga?", "Nā wai e whiwhi painga — nā wai e mamae?"),
            ],
            "footer_line": "Mā Te Pā Tūwatawata koe e whakaako ki te whakautu.",
            "cta_line": "Akoranga kore utu · kiwidialectic.com",
            "hashtags": ["#ManaRaraunga", "#TinoRangatiratanga", "#AotearoaAI", "#KaupapaMāori"],
        },
        "pt": {
            "small_italic": "3 Pātai Mō Ia AI Pūnaha",
            "headline": "3 Perguntas Para Fazer Sobre Qualquer Sistema de IA",
            "items": [
                ("Ko wai nāu i hanga?", "Quem construiu — e usou o conhecimento de quem?"),
                ("Ko wai e tiaki ana?", "Quem controla — e quem responde por isso?"),
                ("Ko wai e painga ana?", "Quem se beneficia — e quem é prejudicado?"),
            ],
            "footer_line": "Te Pā Tūwatawata ensina como responder.",
            "cta_line": "Curso gratuito · kiwidialectic.com",
            "hashtags": ["#SoberaniaDeDados", "#PovosOriginários", "#IAÉtica", "#TinoRangatiratanga"],
        },
        "gn": {
            "small_italic": "3 Pātai Mō Ia AI Pūnaha",
            "headline": "3 Porandu Eñeporandu Va'erã Opaite IA-pe",
            "items": [
                ("Ko wai nāu i hanga?", "Mávapa ojapo — ha mávape arandu oipuru?"),
                ("Ko wai e tiaki ana?", "Mávapa omotenonde — ha mávapa hekoviarã?"),
                ("Ko wai e painga ana?", "Mávapa oĩporãve — ha mávape oñembyai?"),
            ],
            "footer_line": "Te Pā Tūwatawata nembo'e mba'éichapa rembohovái.",
            "cta_line": "Mbo'esyry rei · kiwidialectic.com",
            "hashtags": ["#MboriahuRekoApo", "#TekoIndígena", "#IAEthica", "#TinoRangatiratanga"],
        },
        "sm": {
            "small_italic": "3 Pātai Mō Ia AI Pūnaha",
            "headline": "3 Fesili e Tatau Ona Fai i So'o Se AI",
            "items": [
                ("Ko wai nāu i hanga?", "O ai na faia — ma o le poto a ai na fa'aaogaina?"),
                ("Ko wai e tiaki ana?", "O ai e pulea — ma o ai e nafa atu?"),
                ("Ko wai e painga ana?", "O ai e maua se aoga — ma o ai e a'afia?"),
            ],
            "footer_line": "E a'oa'o atu Te Pā Tūwatawata pe fa'apefea ona tali.",
            "cta_line": "A'oa'oga fua · kiwidialectic.com",
            "hashtags": ["#PuleFa'aleAtunu'u", "#TinoRangatiratanga", "#PasifikaAI", "#KaupapaMāori"],
        },
    },

    # ── 3. TE MANA RARAUNGA ───────────────────────────────────────
    "te-mana-raraunga": {
        "tpl": "quote",
        "en": {
            "eyebrow": "MĀORI DATA SOVEREIGNTY PRINCIPLE",
            "quote": "Māori data should be subject to Māori governance.",
            "attribution": "Te Mana Raraunga, Māori Data Sovereignty Principles",
            "body": "Te Mana Raraunga is the Māori Data Sovereignty Network. Their principles assert that Māori communities have the right to govern data about them — not corporations, not the state.",
            "native_line": "Ko tō mātou raraunga — māku anō e tiaki.",
            "english_line": "Our data — we will govern it ourselves.",
            "cta": "Free course  ·  kiwidialectic.com",
            "hashtags": ["#MāoriDataSovereignty", "#TeManaRaraunga", "#KaupapaMāori", "#AotearoaAI"],
        },
        "mi": {
            "eyebrow": "MĀTĀPONO MANA RARAUNGA",
            "quote": "Me tiaki e te Māori ngā raraunga Māori.",
            "attribution": "Te Mana Raraunga, Ngā Mātāpono Mana Raraunga Māori",
            "body": "Ko Te Mana Raraunga te whatunga Mana Raraunga Māori. E mea ana ā rātou mātāpono he tika tā ngā hapori Māori ki te whakahaere i ngā raraunga e pā ana ki a rātou — kaua mā ngā kamupene, kaua mā te kāwanatanga.",
            "native_line": "Ko tō mātou raraunga — māku anō e tiaki.",
            "english_line": "Mā mātou anō e whakahaere.",
            "cta": "Akoranga kore utu  ·  kiwidialectic.com",
            "hashtags": ["#ManaRaraungaMāori", "#TeManaRaraunga", "#KaupapaMāori", "#AotearoaAI"],
        },
        "pt": {
            "eyebrow": "PRINCÍPIO DE SOBERANIA DE DADOS MĀORI",
            "quote": "Os dados Māori devem estar sujeitos à governança Māori.",
            "attribution": "Te Mana Raraunga, Princípios de Soberania de Dados Māori",
            "body": "Te Mana Raraunga é a Rede Māori de Soberania de Dados. Seus princípios afirmam que as comunidades Māori têm o direito de governar os dados sobre si mesmas — não as corporações, nem o Estado.",
            "native_line": "Ko tō mātou raraunga — māku anō e tiaki.",
            "english_line": "Nossos dados — nós mesmos os governaremos.",
            "cta": "Curso gratuito  ·  kiwidialectic.com",
            "hashtags": ["#SoberaniaDeDados", "#TeManaRaraunga", "#PovosOriginários", "#AotearoaAI"],
        },
        "gn": {
            "eyebrow": "MĀORI MBA'E REKO PYPUKU MOMARANDU",
            "quote": "Māori-kuéra mba'e tendu oĩva'erã Māori poguýpe.",
            "attribution": "Te Mana Raraunga, Māori Mba'e Reko Pypuku Tembiapoukapy",
            "body": "Te Mana Raraunga ha'e Māori Mba'e Reko Pypuku Rejã. Hembiapouka he'i Māori-kuéra atyhápe ipu'aka oñangareko mba'e tendu hesegua — ndaha'éi kamupĩ ha noĩri mburuvicha-pegua.",
            "native_line": "Ko tō mātou raraunga — māku anō e tiaki.",
            "english_line": "Ñande mba'e tendu — ñañangarekóta ñande voi.",
            "cta": "Mbo'esyry rei  ·  kiwidialectic.com",
            "hashtags": ["#MboriahuRekoApo", "#TeManaRaraunga", "#TekoIndígena", "#AotearoaAI"],
        },
        "sm": {
            "eyebrow": "FA'AVAE PULE FA'AMĀORI I FA'AMAUMAUGA",
            "quote": "O fa'amaumauga a Māori e tatau ona pulea e Māori.",
            "attribution": "Te Mana Raraunga, Fa'avae Pule Fa'amāori i Fa'amaumauga",
            "body": "O Te Mana Raraunga o le sui o le va o Māori mo le Pule i Fa'amaumauga. Fai mai a latou fa'avae e iai le aiā tatau o nu'u Māori e pulea fa'amaumauga e uiga ia i latou — ae lē o kamupani po o le malo.",
            "native_line": "Ko tō mātou raraunga — māku anō e tiaki.",
            "english_line": "O a tatou fa'amaumauga — o le a tatou pulea e i tatou lava.",
            "cta": "A'oa'oga fua  ·  kiwidialectic.com",
            "hashtags": ["#PuleFa'amaumauga", "#TeManaRaraunga", "#KaupapaMāori", "#PasifikaAI"],
        },
    },

    # ── 4. DATA SOVEREIGNTY (4 PRINCIPLES) ────────────────────────
    "data-sovereignty": {
        "tpl": "principles",
        "en": {
            "small_italic": "He aha te mana raraunga?",
            "headline": "What is data sovereignty?",
            "body": "Data sovereignty is the right of a people to govern data about them — who collects it, who uses it, who profits from it, and who it can harm.",
            "bullets": [
                ("Tino rangatiratanga", "Self-determination over data — full stop."),
                ("Whakapapa", "Data has genealogy. It comes from someone."),
                ("Kaitiakitanga", "Guardianship. Not ownership — stewardship."),
                ("Mana", "Data about Māori carries Māori mana."),
            ],
            "footer_line": "Module 4 of Te Pā Tūwatawata explores this in depth.",
            "cta": "Free course · kiwidialectic.com",
            "hashtags": ["#Tikanga", "#DataGovernance", "#IndigenousData", "#TinoRangatiratanga"],
        },
        "mi": {
            "small_italic": "He aha te mana raraunga?",
            "headline": "He aha te mana raraunga?",
            "body": "Ko te mana raraunga ko te mana o tētahi iwi ki te whakahaere i ngā raraunga e pā ana ki a rātou — ko wai e kohi, ko wai e whakamahi, ko wai e whiwhi painga, ko wai e mamae.",
            "bullets": [
                ("Tino rangatiratanga", "Ko te mana motuhake ki runga i te raraunga."),
                ("Whakapapa", "He whakapapa tō ngā raraunga. Nō tētahi mai."),
                ("Kaitiakitanga", "He kaitiakitanga, ehara i te kainga noa."),
                ("Mana", "He mana Māori tō ngā raraunga Māori."),
            ],
            "footer_line": "Ka tirohia tēnei i te Wāhanga 4 o Te Pā Tūwatawata.",
            "cta": "Akoranga kore utu · kiwidialectic.com",
            "hashtags": ["#Tikanga", "#ManaRaraunga", "#TaketakeRaraunga", "#TinoRangatiratanga"],
        },
        "pt": {
            "small_italic": "He aha te mana raraunga?",
            "headline": "O que é soberania de dados?",
            "body": "Soberania de dados é o direito de um povo de governar os dados sobre si — quem os coleta, quem os usa, quem lucra com eles e a quem podem prejudicar.",
            "bullets": [
                ("Autodeterminação", "Tino rangatiratanga — autogoverno sobre os dados."),
                ("Whakapapa (linhagem)", "Dados têm genealogia. Vêm de alguém."),
                ("Kaitiakitanga", "Tutela — não propriedade. Cuidado coletivo."),
                ("Mana", "Dados Māori carregam mana Māori."),
            ],
            "footer_line": "O Módulo 4 de Te Pā Tūwatawata aprofunda esse tema.",
            "cta": "Curso gratuito · kiwidialectic.com",
            "hashtags": ["#Tikanga", "#SoberaniaDeDados", "#DadosIndígenas", "#Autodeterminação"],
        },
        "gn": {
            "small_italic": "He aha te mana raraunga?",
            "headline": "Mba'épa mba'e tendu reko pypuku?",
            "body": "Mba'e tendu reko pypuku ha'e peteĩ tetãygua puguáke oñangareko mba'e tendu hesegua — máva ombyaty, máva oipuru, máva oñemonguera, ha mávape ombyai.",
            "bullets": [
                ("Tekoñemoñe'ẽrã", "Tino rangatiratanga — oñemoñe'ẽ mba'e tenduére."),
                ("Whakapapa", "Mba'e tendu oguereko iñypyrũ. Oúgui peteĩva."),
                ("Kaitiakitanga", "Ñañangareko — ndaha'éi ñande mba'e. Ñañongatuhápe."),
                ("Mana", "Māori-kuéra mba'e tendu ogueraha Māori mana."),
            ],
            "footer_line": "Te Pā Tūwatawata Mbo'ekuatia 4 ohesa'ỹijo upéichagua mba'e.",
            "cta": "Mbo'esyry rei · kiwidialectic.com",
            "hashtags": ["#Tikanga", "#MbaeTenduReko", "#TekoIndígena", "#Tekoñemoñe'ẽ"],
        },
        "sm": {
            "small_italic": "He aha te mana raraunga?",
            "headline": "O ā le pule i fa'amaumauga?",
            "body": "O le pule i fa'amaumauga o le aiā tatau lea o se atunu'u e pulea fa'amaumauga e uiga ia i latou — o ai e aoina, o ai e fa'aaogā, o ai e maua se tupe, ma o ai e a'afia.",
            "bullets": [
                ("Tino rangatiratanga", "Pule iā te oe lava i au fa'amaumauga."),
                ("Whakapapa", "E iai le gafa o fa'amaumauga. E sau mai i se tasi."),
                ("Kaitiakitanga", "Tausiga — ae lē o le umiaina."),
                ("Mana", "O fa'amaumauga e uiga i Māori e iai le mana o Māori."),
            ],
            "footer_line": "O loʻo va'aia lenei mea i le Vāega 4 o Te Pā Tūwatawata.",
            "cta": "A'oa'oga fua · kiwidialectic.com",
            "hashtags": ["#Tikanga", "#PuleFa'amaumauga", "#PasifikaData", "#TinoRangatiratanga"],
        },
    },

    # ── 5. ENROL ───────────────────────────────────────────────────
    "enrol": {
        "tpl": "cta",
        "en": {
            "big_headline_lines": ["FREE", "COURSE."],
            "italic_sub": "AI and Māori Data Sovereignty",
            "italic_brand": "Te Pā Tūwatawata",
            "body_lines": [
                "6 modules  ·  bilingual te reo / English",
                "Freire · Graeber · Kropotkin · Kaupapa Māori",
                "Teaching kit PDFs  ·  social media kit  ·  free",
            ],
            "url": "kiwidialectic.com",
            "modules_lines": [
                "1. Whakapapa o te raraunga  ·  2. Te Pā Tūwatawata hei tauira",
                "3. AI me te raupatu matihiko  ·  4. Tikanga, ture, mana whakahaere",
                "5. Hoahoa tika  ·  6. He anamata rangatira",
            ],
        },
        "mi": {
            "big_headline_lines": ["AKORANGA", "KORE UTU."],
            "italic_sub": "AI me te Mana Raraunga Māori",
            "italic_brand": "Te Pā Tūwatawata",
            "body_lines": [
                "6 wāhanga  ·  reo rua: te reo / Pākehā",
                "Freire · Graeber · Kropotkin · Kaupapa Māori",
                "PDF whakaako  ·  pouaka pāpāho pāpori  ·  utu kore",
            ],
            "url": "kiwidialectic.com",
            "modules_lines": [
                "1. Whakapapa o te raraunga  ·  2. Te Pā Tūwatawata hei tauira",
                "3. AI me te raupatu matihiko  ·  4. Tikanga, ture, mana whakahaere",
                "5. Hoahoa tika  ·  6. He anamata rangatira",
            ],
        },
        "pt": {
            "big_headline_lines": ["CURSO", "GRATUITO."],
            "italic_sub": "IA e Soberania de Dados Māori",
            "italic_brand": "Te Pā Tūwatawata",
            "body_lines": [
                "6 módulos  ·  bilingue te reo / inglês",
                "Freire · Graeber · Kropotkin · Kaupapa Māori",
                "PDFs de ensino  ·  kit de redes sociais  ·  gratuito",
            ],
            "url": "kiwidialectic.com",
            "modules_lines": [
                "1. Whakapapa dos dados  ·  2. Te Pā Tūwatawata como modelo",
                "3. IA e usurpação digital  ·  4. Tikanga, lei, governança",
                "5. Design ético  ·  6. Um futuro soberano",
            ],
        },
        "gn": {
            "big_headline_lines": ["MBO'ESYRY", "REI."],
            "italic_sub": "IA ha Māori Mba'e Tendu Reko Pypuku",
            "italic_brand": "Te Pā Tūwatawata",
            "body_lines": [
                "6 mbo'ekuatia  ·  mokõi ñe'ẽ: te reo / inglés",
                "Freire · Graeber · Kropotkin · Kaupapa Māori",
                "PDF ñembo'e  ·  ata pyahu  ·  reípe",
            ],
            "url": "kiwidialectic.com",
            "modules_lines": [
                "1. Mba'e tendu ypy  ·  2. Te Pā Tūwatawata techapyrã",
                "3. IA ha mba'ejopy digital  ·  4. Tikanga, léi, ñemotenonde",
                "5. Hoahoa heko-porã  ·  6. Tetãygua tenondegua",
            ],
        },
        "sm": {
            "big_headline_lines": ["A'OA'OGA", "FUA."],
            "italic_sub": "AI ma le Pule i Fa'amaumauga a Māori",
            "italic_brand": "Te Pā Tūwatawata",
            "body_lines": [
                "6 vāega  ·  gagana lua: te reo / Igilisi",
                "Freire · Graeber · Kropotkin · Kaupapa Māori",
                "PDF a'oa'oga  ·  pusa ala mea fa'asalalau  ·  fua",
            ],
            "url": "kiwidialectic.com",
            "modules_lines": [
                "1. Gafa o fa'amaumauga  ·  2. Te Pā Tūwatawata o se fa'ata'ita'iga",
                "3. AI ma le faoa fa'akomepiuta  ·  4. Tikanga, tulafono, pule",
                "5. Mamanu sa'o  ·  6. O se lumana'i pulea",
            ],
        },
    },

    # ── 6. ANAMATA ─────────────────────────────────────────────────
    "anamata": {
        "tpl": "anamata",
        "en": {
            "eyebrow": "THE KIWI DIALECTIC",
            "italic_native": "Ko tātou te anamata.",
            "english_sub": "We are the future.",
            "italic_quote_native": "Ko ngā tīpuna, ko ngā uri —",
            "italic_quote_red": "kotahi anō te ara.",
            "eng_caption": "Ancestors and descendants — one spiral, one path.",
            "body": "A sovereign digital future is not a destination. It is a practice — of consent, accountability, and building technology that answers to the people it serves.",
            "hashtags": ["#KaupapaMāori", "#DataSovereignty", "#AotearoaAI", "#Anamata"],
        },
        "mi": {
            "eyebrow": "TE KIWI DIALECTIC",
            "italic_native": "Ko tātou te anamata.",
            "english_sub": "Ko tātou tonu te anamata.",
            "italic_quote_native": "Ko ngā tīpuna, ko ngā uri —",
            "italic_quote_red": "kotahi anō te ara.",
            "eng_caption": "Ko ngā tūpuna me ngā mokopuna — kotahi te takarangi, kotahi te ara.",
            "body": "Ehara te anamata matihiko rangatira i te wāhi e tae atu ai. He mahi tonu — o te whakaae, o te takohanga, o te hanga hangarau e takohanga ana ki te iwi.",
            "hashtags": ["#KaupapaMāori", "#ManaRaraunga", "#AotearoaAI", "#Anamata"],
        },
        "pt": {
            "eyebrow": "THE KIWI DIALECTIC",
            "italic_native": "Ko tātou te anamata.",
            "english_sub": "Nós somos o futuro.",
            "italic_quote_native": "Ko ngā tīpuna, ko ngā uri —",
            "italic_quote_red": "kotahi anō te ara.",
            "eng_caption": "Ancestrais e descendentes — uma espiral, um único caminho.",
            "body": "Um futuro digital soberano não é um destino. É uma prática — de consentimento, de responsabilidade, e de construir tecnologia que responda ao povo a quem serve.",
            "hashtags": ["#KaupapaMāori", "#SoberaniaDeDados", "#PovosOriginários", "#Anamata"],
        },
        "gn": {
            "eyebrow": "THE KIWI DIALECTIC",
            "italic_native": "Ko tātou te anamata.",
            "english_sub": "Ñande ha'e ko tenondegua.",
            "italic_quote_native": "Ko ngā tīpuna, ko ngā uri —",
            "italic_quote_red": "kotahi anō te ara.",
            "eng_caption": "Ypykuéra ha tendotagua — peteĩnte tape pyharyre.",
            "body": "Tetãygua tenondegua digital ndaha'éi peteĩ paha. Ha'e tembiapo — ñembojevy, ñañongareko, ha ojejapo tembipuru oñerespondéva tetãyguápe.",
            "hashtags": ["#KaupapaMāori", "#MboriahuRekoApo", "#TekoIndígena", "#Anamata"],
        },
        "sm": {
            "eyebrow": "THE KIWI DIALECTIC",
            "italic_native": "Ko tātou te anamata.",
            "english_sub": "O i tatou o le lumana'i.",
            "italic_quote_native": "Ko ngā tīpuna, ko ngā uri —",
            "italic_quote_red": "kotahi anō te ara.",
            "eng_caption": "Tua'ā ma fanau — e tasi le tā'amilo, e tasi le ala.",
            "body": "O se lumana'i fa'akomepiuta pulea, e le o se nofoaga e taunu'u i ai. O se faiga — o le fa'atagaga, o le tali atu, ma le fauina o tekonolosi e tali atu i tagata o lo'o tautua i ai.",
            "hashtags": ["#KaupapaMāori", "#PuleFa'amaumauga", "#PasifikaAI", "#Anamata"],
        },
    },
}


# ─── Dispatch ──────────────────────────────────────────────────────────
TEMPLATES = {
    "slogan": template_slogan,
    "list": template_list,
    "quote": template_quote,
    "principles": template_principles,
    "cta": template_cta,
    "anamata": template_anamata,
}

LANGS = ["en", "mi", "pt", "gn", "sm"]


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    total = 0
    for meme_id, spec in CONTENT.items():
        if only and only != meme_id:
            continue
        tpl_name = spec["tpl"]
        tpl_fn = TEMPLATES[tpl_name]
        for lang in LANGS:
            payload = spec[lang]
            img = tpl_fn(**payload)
            out_path = os.path.join(OUT_DIR, f"campaign-{meme_id}-{lang}.png")
            img.save(out_path, "PNG", optimize=True)
            print(f"  ✓ {out_path}")
            total += 1
    print(f"\nGenerated {total} memes.")


if __name__ == "__main__":
    main()
