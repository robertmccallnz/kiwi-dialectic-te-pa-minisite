#!/usr/bin/env python3
"""
Generate-campaign-memes v2 — culturally-mapped, per-language motifs.

Changes vs. v1:
  • Per-language top/bottom border motif:
      en  → niho-taniwha (Māori — anchor; campaign is from Aotearoa)
      mi  → niho-taniwha
      pt  → Wajãpi parallel-line / fish-bone (Pan-Amazonian Indigenous)
      gn  → takua vertical bamboo bars (Guaraní ceremonial)
      sm  → siapo fa'a'aliao trochus-shell triangles (Sāmoan tapa cloth)
  • Every card retains a single te reo Māori line as the kaupapa-Māori solidarity
    anchor, but headlines, eyebrows, and question text are translated into the
    target language. The te reo line sits below as anchor + gloss.
  • Generates real bilingual covers `campaign-{meme}.png`: top half EN, bottom MI.
    (Previously these were byte-identical copies of -en.png.)
  • Unaunahi fish-scale background pattern is retained across all variants as
    the brand anchor (the campaign is *about* Māori data sovereignty — the
    Māori frame is central; per-language borders are the gesture of solidarity).

Reference research (motifs):
  - Niho taniwha:   teeth-of-the-taniwha, threshold warning. (motifs/niho-taniwha.html)
  - Siapo (Sāmoa):  13 canonical motifs; fa'a'aliao (trochus shell) reads as
                    a triangle band echoing niho-taniwha geometrically.
                    https://anthromuseum.missouri.edu/e-exhibits/siapo-tapa-cloths-samoa
  - Takua (Guaraní): bamboo ceremonial percussion struck on earth during jeroky;
                    visually a row of vertical bars / verticals.
                    https://seer.ufu.br/index.php/revistaeducaopoliticas
  - Wajãpi (Brazil): UNESCO-listed graphic system; fine parallel & fish-bone lines.
                    https://artsandculture.google.com/asset/oral-and-graphic-expressions-of-the-wajapi-unesco-world-heritage-list/

Output: social-kit/campaign-{meme_id}-{lang}.png  (30 files)
        social-kit/campaign-{meme_id}.png         (6 bilingual covers)
"""
import os, sys
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
GREY_MUTED = (180, 174, 162)

# ─── Fonts ──────────────────────────────────────────────────────────────
FONT_DIR = "/usr/share/fonts/truetype/noto"
F_SERIF_REG       = f"{FONT_DIR}/NotoSerif-Regular.ttf"
F_SERIF_BOLD      = f"{FONT_DIR}/NotoSerif-Bold.ttf"
F_SERIF_ITALIC    = f"{FONT_DIR}/NotoSerif-Italic.ttf"
F_SERIF_BOLDITALIC= f"{FONT_DIR}/NotoSerif-BoldItalic.ttf"
F_SANS_REG        = f"{FONT_DIR}/NotoSans-Regular.ttf"
F_SANS_BOLD       = f"{FONT_DIR}/NotoSans-Bold.ttf"

def font(path, size): return ImageFont.truetype(path, size)

# ─── Measurement helpers ────────────────────────────────────────────────
def measure(draw, text, fnt):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def wrap_lines(draw, text, fnt, max_w):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if measure(draw, trial, fnt)[0] <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

# ─── PER-LANGUAGE BORDER MOTIFS ════════════════════════════════════════
# Each takes (draw, side, color, bg, band_h) and paints the border band.

def _niho(draw, side, color, bg, band_h=60, tooth_w=36, tooth_h=44):
    """Māori niho-taniwha — sharp triangular teeth."""
    if side == "top":
        y0, y1 = 0, band_h
    else:
        y0, y1 = H - band_h, H
    draw.rectangle([0, y0, W, y1], fill=bg)
    n = W // tooth_w + 1
    for i in range(n):
        x = i * tooth_w
        if side == "top":
            # teeth pointing DOWN from the band
            draw.polygon([(x, y1 - tooth_h), (x + tooth_w / 2, y1),
                          (x + tooth_w, y1 - tooth_h)], fill=color)
            # smaller inverted teeth at the very top edge
            draw.polygon([(x, y0), (x + tooth_w / 2, y0 + tooth_h * 0.45),
                          (x + tooth_w, y0)], fill=color)
        else:
            draw.polygon([(x, y0 + tooth_h), (x + tooth_w / 2, y0),
                          (x + tooth_w, y0 + tooth_h)], fill=color)
            draw.polygon([(x, y1), (x + tooth_w / 2, y1 - tooth_h * 0.45),
                          (x + tooth_w, y1)], fill=color)

def _siapo(draw, side, color, bg, band_h=60):
    """Sāmoan fa'a'aliao (trochus shell) — diamond/triangle composites with
    a tusili'i wavy line above. Echoes niho-taniwha visually but is distinctly
    Pacific."""
    if side == "top":
        y0, y1 = 0, band_h
    else:
        y0, y1 = H - band_h, H
    draw.rectangle([0, y0, W, y1], fill=bg)
    # Diamond row (two triangles back-to-back) — trochus shell motif
    dw, dh = 44, band_h - 10
    n = W // dw + 1
    base_y = y1 - 6 if side == "top" else y0 + 6
    apex_y = (y0 + 4) if side == "top" else (y1 - 4)
    for i in range(n):
        x = i * dw
        # outer diamond (filled)
        draw.polygon([(x, base_y), (x + dw / 2, apex_y),
                      (x + dw, base_y)], fill=color)
        # inner cream pinpoint to read as "shell"
        cx = x + dw / 2
        cy = (base_y + apex_y) / 2
        r = 3
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CREAM)
    # tusili'i wavy band — single sinuous line
    wave_y = y0 + 4 if side == "top" else y1 - 4
    step = 16
    pts = []
    for i in range(0, W + step, step):
        pts.append((i, wave_y + (3 if (i // step) % 2 else -3)))
    draw.line(pts, fill=color, width=2)

def _takua(draw, side, color, bg, band_h=60):
    """Guaraní takua — bamboo ceremonial percussion. Vertical bars of varying
    height, struck on earth in jeroky. Each bar = a takua."""
    if side == "top":
        y0, y1 = 0, band_h
    else:
        y0, y1 = H - band_h, H
    draw.rectangle([0, y0, W, y1], fill=bg)
    bar_w = 7
    gap = 11
    span = bar_w + gap
    n = W // span + 1
    # alternate tall / short bars; some carry a horizontal node-line (bamboo node)
    for i in range(n):
        x = i * span + 4
        tall = (i % 3 != 0)
        h = (band_h - 14) if tall else (band_h - 28)
        if side == "top":
            top = y0 + 6
            bot = top + h
        else:
            bot = y1 - 6
            top = bot - h
        draw.rectangle([x, top, x + bar_w, bot], fill=color)
        # bamboo node
        node_y = top + h // 2
        draw.rectangle([x - 1, node_y - 1, x + bar_w + 1, node_y + 1], fill=CREAM)
    # base/cap line
    edge_y = y1 - 3 if side == "top" else y0 + 2
    draw.line([(0, edge_y), (W, edge_y)], fill=color, width=2)

def _wajapi(draw, side, color, bg, band_h=60):
    """Wajãpi (Amazonian) parallel + fish-bone lines. Fine parallel diagonals
    with a single horizontal anchor line. UNESCO-recognised graphic system."""
    if side == "top":
        y0, y1 = 0, band_h
    else:
        y0, y1 = H - band_h, H
    draw.rectangle([0, y0, W, y1], fill=bg)
    # diagonal hash marks — alternating directions in groups (fish-bone)
    group_w = 26
    n = W // group_w + 1
    for i in range(n):
        gx = i * group_w
        # 3 diagonals per group, alternating direction
        for j in range(3):
            x0 = gx + j * 7 + 2
            if i % 2 == 0:
                draw.line([(x0, y0 + 8), (x0 + 12, y1 - 8)],
                          fill=color, width=3)
            else:
                draw.line([(x0 + 12, y0 + 8), (x0, y1 - 8)],
                          fill=color, width=3)
    # horizontal anchor line
    mid = (y0 + y1) // 2
    draw.line([(0, mid), (W, mid)], fill=color, width=2)
    # small dots
    for i in range(0, W, 26):
        cx = i + 13
        r = 2
        draw.ellipse([cx - r, mid - r, cx + r, mid + r], fill=CREAM)

LANG_MOTIF = {
    "en": _niho,
    "mi": _niho,
    "pt": _wajapi,
    "gn": _takua,
    "sm": _siapo,
}

def draw_lang_border(draw, lang, side, color, bg, band_h=60):
    """Dispatch to the per-language border motif."""
    LANG_MOTIF[lang](draw, side, color, bg, band_h)

# ─── Unaunahi (fish-scale) background — Māori brand anchor ─────────────
def draw_unaunahi_motif(img, x0=0, y0=0, x1=None, y1=None, base_color=BLACK,
                       scale=92, alpha=22, line_width=2):
    if x1 is None: x1 = img.width
    if y1 is None: y1 = img.height
    w, h = x1 - x0, y1 - y0
    if w <= 0 or h <= 0: return
    hi = (255, 230, 200, alpha) if base_color == RED else (244, 237, 224, alpha)
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    r = scale // 2
    row_step = int(r * 1.05)
    rows = h // row_step + 2
    cols = w // scale + 2
    for ri in range(-1, rows):
        cy = ri * row_step
        offset = (r if ri % 2 else 0)
        for ci in range(-1, cols):
            cx = ci * scale + offset
            od.arc([cx, cy - r, cx + scale, cy + r],
                   start=180, end=360, fill=hi, width=line_width)
    img.paste(overlay, (x0, y0), overlay)

# ─── Canvas + footer ────────────────────────────────────────────────────
def base_canvas(bg=BLACK, motif=True):
    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)
    if motif:
        draw_unaunahi_motif(img, 0, 0, W, H, base_color=bg)
        draw = ImageDraw.Draw(img)
    return img, draw

def add_footer(draw, color=CREAM):
    """Single, deduplicated footer just above the bottom motif band."""
    f1 = font(F_SANS_BOLD, 26)
    f2 = font(F_SANS_REG, 18)
    draw.text((48, H - 130), "Te Pā Tūwatawata  ·  kiwidialectic.com", font=f1, fill=color)
    draw.text((48, H - 96), "Created by The Kiwi Dialectic", font=f2, fill=color)

# ═══════════════════════════════════════════════════════════════════════
# TEMPLATES — every template takes `lang` for motif dispatch
# ═══════════════════════════════════════════════════════════════════════

# --- A: Slogan (Raupatu) --------------------------------------------------
def template_slogan(lang, slogan_lines, italic_caption, accent_line, body, cta):
    img, draw = base_canvas(bg=RED)
    # bottom half black
    draw.rectangle([0, H // 2 + 30, W, H], fill=BLACK)
    draw_unaunahi_motif(img, 0, H // 2 + 30, W, H, base_color=BLACK)
    draw = ImageDraw.Draw(img)

    # mid niho divider (always niho — it IS the divider for this template)
    band_y = H // 2 - 20
    band_h = 70
    draw.rectangle([0, band_y, W, band_y + band_h], fill=RED)
    tooth_w, tooth_h = 36, 40
    n = W // tooth_w + 1
    for i in range(n):
        x = i * tooth_w
        draw.polygon([(x, band_y + band_h - tooth_h),
                      (x + tooth_w / 2, band_y + band_h),
                      (x + tooth_w, band_y + band_h - tooth_h)], fill=BLACK)

    # slogan
    candidate = 100
    while candidate > 56:
        f_slogan = font(F_SANS_BOLD, candidate)
        max_tw = max(measure(draw, ln, f_slogan)[0] for ln in slogan_lines)
        if max_tw <= W - 120: break
        candidate -= 6
    f_slogan = font(F_SANS_BOLD, candidate)
    line_h = candidate + 18
    total_h = line_h * len(slogan_lines)
    sy = max(90, (H // 2 - 20 - total_h) // 2 + 20)
    last_baseline, last_width = sy, 0
    for line in slogan_lines:
        tw, th = measure(draw, line, f_slogan)
        draw.text(((W - tw) / 2, sy), line, font=f_slogan, fill=CREAM)
        last_baseline = sy + th
        last_width = max(last_width, tw)
        sy += line_h
    bar_w = min(160, max(80, last_width // 3))
    bar_x = (W - bar_w) // 2
    bar_y = max(last_baseline + 22, band_y - 24)
    if bar_y + 4 < band_y - 6:
        draw.rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + 4], fill=CREAM)

    # bottom-half copy
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
    if body:
        for ln in wrap_lines(draw, body, f_body, W - 120):
            tw, th = measure(draw, ln, f_body)
            draw.text(((W - tw) / 2, cy), ln, font=f_body, fill=CREAM)
            cy += th + 6
        cy += 18
    if cta:
        tw, th = measure(draw, cta, f_cta)
        draw.text(((W - tw) / 2, cy), cta, font=f_cta, fill=RED)

    # bottom border — per-language motif
    draw_lang_border(draw, lang, "bottom", color=BLACK, bg=RED, band_h=60)
    add_footer(draw)
    return img

# --- B: List (3 Questions) ------------------------------------------------
def template_list(lang, small_italic, headline, items, footer_line, cta_line, hashtags):
    img, draw = base_canvas(bg=BLACK)
    draw_lang_border(draw, lang, "top", color=RED, bg=BLACK, band_h=60)
    x, cy = 60, 110
    if small_italic:
        f = font(F_SERIF_ITALIC, 30)
        draw.text((x, cy), small_italic, font=f, fill=CREAM); cy += 40
    if headline:
        f = font(F_SANS_BOLD, 50)
        for ln in wrap_lines(draw, headline, f, W - 2 * x):
            draw.text((x, cy), ln, font=f, fill=RED)
            cy += measure(draw, ln, f)[1] + 4
        cy += 8
        draw.rectangle([x, cy, W - x, cy + 3], fill=RED)
        cy += 30
    f_num = font(F_SANS_BOLD, 28)
    f_q   = font(F_SERIF_BOLDITALIC, 36)
    f_a   = font(F_SANS_REG, 24)
    for i, (q, a) in enumerate(items, start=1):
        num = f"{i:02d}"
        circ_d = 56
        draw.ellipse([x, cy, x + circ_d, cy + circ_d], fill=RED)
        tw, th = measure(draw, num, f_num)
        draw.text((x + (circ_d - tw) / 2, cy + (circ_d - th) / 2 - 4),
                  num, font=f_num, fill=CREAM)
        qx = x + circ_d + 22
        # question (target language)
        q_lines = wrap_lines(draw, q, f_q, W - qx - 40)
        ay_q = cy - 6
        for ln in q_lines:
            draw.text((qx, ay_q), ln, font=f_q, fill=CREAM)
            ay_q += measure(draw, ln, f_q)[1] + 2
        # answer/gloss
        ay = ay_q + 4
        for ln in wrap_lines(draw, a, f_a, W - qx - 60):
            draw.text((qx, ay), ln, font=f_a, fill=GREY_MUTED)
            ay += measure(draw, ln, f_a)[1] + 4
        cy = max(ay, cy + circ_d) + 22
        draw.line([(x, cy - 12), (W - x, cy - 12)], fill=(60, 55, 50), width=1)
    cy += 8
    if footer_line:
        f_fl = font(F_SANS_BOLD, 30)
        for ln in wrap_lines(draw, footer_line, f_fl, W - 2 * x):
            draw.text((x, cy), ln, font=f_fl, fill=CREAM)
            cy += measure(draw, ln, f_fl)[1] + 4
        cy += 8
    if cta_line:
        f_cta = font(F_SANS_BOLD, 26)
        draw.text((x, cy), cta_line, font=f_cta, fill=RED); cy += 40
    if hashtags:
        f_h = font(F_SANS_REG, 18)
        hx, hy = x, H - 200
        for tag in hashtags:
            tw, _ = measure(draw, tag, f_h)
            if hx + tw > W - x: break
            draw.text((hx, hy), tag, font=f_h, fill=GREY_MUTED)
            hx += tw + 20
    draw_lang_border(draw, lang, "bottom", color=RED, bg=BLACK, band_h=60)
    add_footer(draw)
    return img

# --- C: Quote (Te Mana Raraunga) -----------------------------------------
def template_quote(lang, eyebrow, quote, attribution, body, native_line, english_line, cta, hashtags):
    img, draw = base_canvas(bg=BLACK)
    draw_lang_border(draw, lang, "top", color=RED, bg=BLACK, band_h=70)
    x, cy = 60, 120
    if eyebrow:
        f = font(F_SANS_BOLD, 22)
        draw.text((x, cy), eyebrow, font=f, fill=RED); cy += 36
    qbar_top = cy
    f_q = font(F_SERIF_BOLDITALIC, 48)
    qlines = wrap_lines(draw, f"\u201c{quote}\u201d", f_q, W - 2 * x - 30)
    qy = cy
    for ln in qlines:
        draw.text((x + 22, qy), ln, font=f_q, fill=CREAM)
        qy += measure(draw, ln, f_q)[1] + 6
    qy += 8
    if attribution:
        f_at = font(F_SANS_REG, 24)
        draw.text((x + 22, qy), f"\u2014 {attribution}", font=f_at, fill=RED)
        qy += measure(draw, attribution, f_at)[1] + 18
    draw.rectangle([x, qbar_top, x + 6, qy - 8], fill=RED)
    cy = qy + 8
    draw.line([(x, cy), (W - x, cy)], fill=(70, 65, 60), width=2); cy += 26
    if body:
        f_b = font(F_SANS_REG, 26)
        for ln in wrap_lines(draw, body, f_b, W - 2 * x):
            draw.text((x, cy), ln, font=f_b, fill=CREAM)
            cy += measure(draw, ln, f_b)[1] + 6
        cy += 18
    if native_line:
        f_n = font(F_SERIF_ITALIC, 38)
        draw.text((x, cy), native_line, font=f_n, fill=CREAM)
        cy += measure(draw, native_line, f_n)[1] + 8
    if english_line:
        f_e = font(F_SANS_BOLD, 30)
        draw.text((x, cy), english_line, font=f_e, fill=RED)
        cy += measure(draw, english_line, f_e)[1] + 22
    if cta:
        f_c = font(F_SANS_BOLD, 26)
        draw.text((x, cy), cta, font=f_c, fill=CREAM); cy += 40
    if hashtags:
        f_h = font(F_SANS_REG, 18); hx, hy = x, H - 200
        for tag in hashtags:
            tw, _ = measure(draw, tag, f_h)
            if hx + tw > W - x: break
            draw.text((hx, hy), tag, font=f_h, fill=GREY_MUTED)
            hx += tw + 20
    draw_lang_border(draw, lang, "bottom", color=RED, bg=BLACK, band_h=60)
    add_footer(draw)
    return img

# --- D: Principles (Data Sovereignty) ------------------------------------
def template_principles(lang, small_italic, headline, body, bullets, footer_line, cta, hashtags):
    img, draw = base_canvas(bg=BLACK)
    draw_lang_border(draw, lang, "top", color=RED, bg=BLACK, band_h=60)
    x, cy = 60, 100
    if small_italic:
        f = font(F_SERIF_ITALIC, 34)
        draw.text((x, cy), small_italic, font=f, fill=CREAM); cy += 50
    if headline:
        f = font(F_SANS_BOLD, 50)
        for ln in wrap_lines(draw, headline, f, W - 2 * x):
            draw.text((x, cy), ln, font=f, fill=RED)
            cy += measure(draw, ln, f)[1] + 4
        draw.rectangle([x, cy + 4, W - x, cy + 7], fill=RED); cy += 30
    if body:
        f = font(F_SANS_REG, 26)
        for ln in wrap_lines(draw, body, f, W - 2 * x):
            draw.text((x, cy), ln, font=f, fill=CREAM)
            cy += measure(draw, ln, f)[1] + 6
        cy += 16
        draw.line([(x, cy), (W - x, cy)], fill=(70, 65, 60), width=1); cy += 28
    f_label = font(F_SANS_BOLD, 30); f_desc = font(F_SANS_REG, 22)
    for label, desc in bullets:
        d = 14
        draw.ellipse([x, cy + 12, x + d, cy + 12 + d], fill=RED)
        lx = x + d + 14
        draw.text((lx, cy), label, font=f_label, fill=CREAM)
        cy += measure(draw, label, f_label)[1] + 4
        for ln in wrap_lines(draw, desc, f_desc, W - lx - 60):
            draw.text((lx, cy), ln, font=f_desc, fill=GREY_MUTED)
            cy += measure(draw, ln, f_desc)[1] + 4
        cy += 12
    cy += 4
    if footer_line:
        f = font(F_SANS_BOLD, 26)
        for ln in wrap_lines(draw, footer_line, f, W - 2 * x):
            draw.text((x, cy), ln, font=f, fill=RED)
            cy += measure(draw, ln, f)[1] + 4
        cy += 6
    if cta:
        f = font(F_SANS_BOLD, 26)
        draw.text((x, cy), cta, font=f, fill=CREAM); cy += 36
    if hashtags:
        f = font(F_SANS_REG, 18); hx, hy = x, H - 200
        for tag in hashtags:
            tw, _ = measure(draw, tag, f)
            if hx + tw > W - x: break
            draw.text((hx, hy), tag, font=f, fill=GREY_MUTED)
            hx += tw + 20
    draw_lang_border(draw, lang, "bottom", color=RED, bg=BLACK, band_h=60)
    add_footer(draw)
    return img

# --- E: CTA (Enrol) -------------------------------------------------------
def template_cta(lang, big_headline_lines, italic_sub, italic_brand, body_lines, url, modules_lines):
    img, draw = base_canvas(bg=RED)
    draw_lang_border(draw, lang, "top", color=BLACK, bg=RED, band_h=60)
    cy = 110
    candidate = 110
    while candidate > 56:
        f_big = font(F_SANS_BOLD, candidate)
        max_tw = max(measure(draw, ln, f_big)[0] for ln in big_headline_lines)
        if max_tw <= W - 120: break
        candidate -= 6
    f_big = font(F_SANS_BOLD, candidate)
    line_h = candidate + 18
    for ln in big_headline_lines:
        tw, _ = measure(draw, ln, f_big)
        draw.text(((W - tw) / 2, cy), ln, font=f_big, fill=CREAM)
        cy += line_h
    cy += 14
    if italic_sub:
        f = font(F_SERIF_ITALIC, 46)
        tw, th = measure(draw, italic_sub, f)
        draw.text(((W - tw) / 2, cy), italic_sub, font=f, fill=BLACK); cy += th + 8
    if italic_brand:
        f = font(F_SERIF_ITALIC, 32)
        tw, th = measure(draw, italic_brand, f)
        draw.text(((W - tw) / 2, cy), italic_brand, font=f, fill=BLACK); cy += th + 18
    draw.line([(120, cy), (W - 120, cy)], fill=BLACK, width=3); cy += 28
    f_b = font(F_SANS_REG, 28)
    for ln in body_lines:
        tw, th = measure(draw, ln, f_b)
        draw.text(((W - tw) / 2, cy), ln, font=f_b, fill=BLACK); cy += th + 4
    cy += 24
    if url:
        f_u = font(F_SANS_BOLD, 54)
        tw, th = measure(draw, url, f_u)
        draw.text(((W - tw) / 2, cy), url, font=f_u, fill=CREAM); cy += th + 28
    f_m = font(F_SANS_BOLD, 22)
    for ln in modules_lines:
        tw, th = measure(draw, ln, f_m)
        draw.text(((W - tw) / 2, cy), ln, font=f_m, fill=BLACK); cy += th + 4
    f_foot = font(F_SANS_REG, 20)
    foot = "Te Kiwi Dialectic  ·  kiwidialectic.com"
    tw, _ = measure(draw, foot, f_foot)
    draw.text(((W - tw) / 2, H - 95), foot, font=f_foot, fill=BLACK)
    draw_lang_border(draw, lang, "bottom", color=BLACK, bg=RED, band_h=60)
    return img

# --- F: Anamata ----------------------------------------------------------
def template_anamata(lang, eyebrow, italic_native, english_sub, italic_quote_native,
                     italic_quote_red, eng_caption, body, hashtags):
    img, draw = base_canvas(bg=BLACK)
    draw_lang_border(draw, lang, "top", color=RED, bg=BLACK, band_h=60)
    x, cy = 60, 100
    if eyebrow:
        f = font(F_SANS_BOLD, 22)
        draw.text((x, cy), eyebrow, font=f, fill=RED); cy += 36
    f_big = font(F_SERIF_BOLDITALIC, 60)
    for ln in wrap_lines(draw, italic_native, f_big, W - 2 * x):
        tw, th = measure(draw, ln, f_big)
        draw.text(((W - tw) / 2, cy), ln, font=f_big, fill=CREAM)
        cy += th + 6
    cy += 14
    f_eng = font(F_SANS_BOLD, 42)
    for ln in wrap_lines(draw, english_sub, f_eng, W - 2 * x):
        tw, th = measure(draw, ln, f_eng)
        draw.text(((W - tw) / 2, cy), ln, font=f_eng, fill=RED)
        cy += th + 4
    cy += 24
    draw.line([(x, cy), (W - x, cy)], fill=RED, width=2); cy += 30
    if italic_quote_native:
        f_qn = font(F_SERIF_ITALIC, 30)
        for ln in wrap_lines(draw, italic_quote_native, f_qn, W - 2 * x):
            tw, th = measure(draw, ln, f_qn)
            draw.text(((W - tw) / 2, cy), ln, font=f_qn, fill=CREAM); cy += th + 4
    if italic_quote_red:
        f_qr = font(F_SERIF_BOLDITALIC, 36)
        tw, th = measure(draw, italic_quote_red, f_qr)
        draw.text(((W - tw) / 2, cy), italic_quote_red, font=f_qr, fill=RED); cy += th + 10
    if eng_caption:
        f_e = font(F_SANS_REG, 24)
        for ln in wrap_lines(draw, eng_caption, f_e, W - 2 * x):
            tw, th = measure(draw, ln, f_e)
            draw.text(((W - tw) / 2, cy), ln, font=f_e, fill=GREY_MUTED); cy += th + 4
        cy += 20
    draw.line([(x, cy), (W - x, cy)], fill=(70, 65, 60), width=1); cy += 26
    if body:
        f_b = font(F_SANS_REG, 24)
        for ln in wrap_lines(draw, body, f_b, W - 2 * x):
            tw, th = measure(draw, ln, f_b)
            draw.text(((W - tw) / 2, cy), ln, font=f_b, fill=CREAM); cy += th + 4
    if hashtags:
        f = font(F_SANS_REG, 18); hx, hy = x, H - 200
        for tag in hashtags:
            tw, _ = measure(draw, tag, f)
            if hx + tw > W - x: break
            draw.text((hx, hy), tag, font=f, fill=GREY_MUTED)
            hx += tw + 20
    draw_lang_border(draw, lang, "bottom", color=RED, bg=BLACK, band_h=60)
    add_footer(draw)
    return img

# ═══════════════════════════════════════════════════════════════════════
# CONTENT — language-correct, te reo only as deliberate solidarity anchor
# ═══════════════════════════════════════════════════════════════════════

# Te reo anchor questions kept the same across languages (the kaupapa-Māori
# tikanga line); the BOLD display question is in the target language;
# the small gloss line is also in target language.

QUESTIONS = {
    "en": [
        ("Who built it?",     "And whose knowledge did they train on?"),
        ("Who controls it?",  "And who is accountable when it harms?"),
        ("Who benefits?",     "And who carries the cost?"),
    ],
    "mi": [
        ("Nā wai i hanga?",   "Nā wai te mātauranga i whakamahia?"),
        ("Nā wai e whakahaere?", "Nā wai te takohanga i te mamae?"),
        ("Nā wai te painga?", "Nā wai te utu e mau ana?"),
    ],
    "pt": [
        ("Quem o construiu?",  "E em qual conhecimento foi treinado?"),
        ("Quem o controla?",   "E quem responde quando causa dano?"),
        ("Quem se beneficia?", "E quem paga o preço?"),
    ],
    "gn": [
        ("Mávapa ojapo?",      "Ha mávape arandúgui oñembokatupyry?"),
        ("Mávapa omotenonde?", "Ha mávapa hekoviarã oñembyaívo?"),
        ("Mávapa oĩporãve?",   "Ha mávapa ogueraha pe hepy?"),
    ],
    "sm": [
        ("O ai na faia?",          "Ma o le poto o ai na aoao'ina ai?"),
        ("O ai e pulea?",          "Ma o ai e nafa pe a faia se afaina?"),
        ("O ai e maua se aoga?",   "Ma o ai e tauave le tau?"),
    ],
}

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
            "small_italic": "3 Pātai Mō Ngā Pūnaha AI",
            "headline": "3 Questions to Ask About Any AI System",
            "items": QUESTIONS["en"],
            "footer_line": "Te Pā Tūwatawata teaches you how to answer these.",
            "cta_line": "Free course · kiwidialectic.com",
            "hashtags": ["#DataSovereignty", "#TinoRangatiratanga", "#AotearoaAI", "#KaupapaMāori"],
        },
        "mi": {
            "small_italic": "He mātauranga, he mana — mā tātou te kōrero.",
            "headline": "3 Pātai Mō Ngā Pūnaha AI Katoa",
            "items": QUESTIONS["mi"],
            "footer_line": "Mā Te Pā Tūwatawata koe e whakaako ki te whakautu.",
            "cta_line": "Akoranga kore utu · kiwidialectic.com",
            "hashtags": ["#ManaRaraunga", "#TinoRangatiratanga", "#AotearoaAI", "#KaupapaMāori"],
        },
        "pt": {
            "small_italic": "3 Pātai — perguntas em te reo Māori",
            "headline": "3 Perguntas Para Fazer Sobre Qualquer Sistema de IA",
            "items": QUESTIONS["pt"],
            "footer_line": "Te Pā Tūwatawata ensina como respondê-las.",
            "cta_line": "Curso gratuito · kiwidialectic.com",
            "hashtags": ["#SoberaniaDeDados", "#PovosOriginários", "#IAÉtica", "#TinoRangatiratanga"],
        },
        "gn": {
            "small_italic": "3 Pātai — porandu te reo Māori-pe",
            "headline": "3 Porandu Eñeporandu Va'erã Opaite IA-pe",
            "items": QUESTIONS["gn"],
            "footer_line": "Te Pā Tūwatawata nembo'e mba'éichapa rembohovái.",
            "cta_line": "Mbo'esyry rei · kiwidialectic.com",
            "hashtags": ["#MboriahuRekoApo", "#TekoIndígena", "#IAEthica", "#TinoRangatiratanga"],
        },
        "sm": {
            "small_italic": "3 Pātai — fesili i le gagana Māori",
            "headline": "3 Fesili e Tatau Ona Fai i So'o Se AI",
            "items": QUESTIONS["sm"],
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
            "attribution": "Te Mana Raraunga — Māori Data Sovereignty Principles",
            "body": "Te Mana Raraunga is the Māori Data Sovereignty Network. Their principles assert that Māori communities have the right to govern data about them — not corporations, not the state.",
            "native_line": "Ko tō mātou raraunga — māku anō e tiaki.",
            "english_line": "Our data — we will govern it ourselves.",
            "cta": "Free course  ·  kiwidialectic.com",
            "hashtags": ["#MāoriDataSovereignty", "#TeManaRaraunga", "#KaupapaMāori", "#AotearoaAI"],
        },
        "mi": {
            "eyebrow": "MĀTĀPONO MANA RARAUNGA",
            "quote": "Me tiaki e te Māori ngā raraunga Māori.",
            "attribution": "Te Mana Raraunga — Ngā Mātāpono Mana Raraunga Māori",
            "body": "Ko Te Mana Raraunga te whatunga Mana Raraunga Māori. E mea ana ā rātou mātāpono he tika tā ngā hapori Māori ki te whakahaere i ngā raraunga e pā ana ki a rātou — kaua mā ngā kamupene, kaua mā te kāwanatanga.",
            "native_line": "Ko tō mātou raraunga — māku anō e tiaki.",
            "english_line": "Mā mātou anō e whakahaere.",
            "cta": "Akoranga kore utu  ·  kiwidialectic.com",
            "hashtags": ["#ManaRaraungaMāori", "#TeManaRaraunga", "#KaupapaMāori", "#AotearoaAI"],
        },
        "pt": {
            "eyebrow": "PRINCÍPIO DE SOBERANIA DE DADOS MĀORI",
            "quote": "Os dados Māori devem estar sujeitos à governança Māori.",
            "attribution": "Te Mana Raraunga — Princípios de Soberania de Dados Māori",
            "body": "Te Mana Raraunga é a Rede Māori de Soberania de Dados. Seus princípios afirmam que as comunidades Māori têm o direito de governar os dados sobre si mesmas — não as corporações, nem o Estado.",
            "native_line": "Ko tō mātou raraunga — māku anō e tiaki.",
            "english_line": "Nossos dados — nós mesmos os governaremos.",
            "cta": "Curso gratuito  ·  kiwidialectic.com",
            "hashtags": ["#SoberaniaDeDados", "#TeManaRaraunga", "#PovosOriginários", "#AotearoaAI"],
        },
        "gn": {
            "eyebrow": "MĀORI MBA'E TENDU REKO PYPUKU MOMARANDU",
            "quote": "Māori-kuéra mba'e tendu oĩva'erã Māori poguýpe.",
            "attribution": "Te Mana Raraunga — Māori Mba'e Tendu Reko Pypuku",
            "body": "Te Mana Raraunga ha'e Māori Mba'e Tendu Reko Pypuku Rejã. Hembiapouka he'i Māori-kuéra atyhápe ipu'aka oñangareko mba'e tendu hesegua — ndaha'éi kamupĩ ha noĩri mburuvicha-pegua.",
            "native_line": "Ko tō mātou raraunga — māku anō e tiaki.",
            "english_line": "Ñande mba'e tendu — ñañangarekóta ñande voi.",
            "cta": "Mbo'esyry rei  ·  kiwidialectic.com",
            "hashtags": ["#MboriahuRekoApo", "#TeManaRaraunga", "#TekoIndígena", "#AotearoaAI"],
        },
        "sm": {
            "eyebrow": "FA'AVAE PULE FA'AMĀORI I FA'AMAUMAUGA",
            "quote": "O fa'amaumauga a Māori e tatau ona pulea e Māori.",
            "attribution": "Te Mana Raraunga — Fa'avae Pule Fa'amāori",
            "body": "O Te Mana Raraunga o le sui o le va o Māori mo le Pule i Fa'amaumauga. Fai mai a latou fa'avae e iai le aiā tatau o nu'u Māori e pulea fa'amaumauga e uiga ia i latou — ae lē o kamupani po o le malo.",
            "native_line": "Ko tō mātou raraunga — māku anō e tiaki.",
            "english_line": "O a tatou fa'amaumauga — o le a tatou pulea e i tatou lava.",
            "cta": "A'oa'oga fua  ·  kiwidialectic.com",
            "hashtags": ["#PuleFa'amaumauga", "#TeManaRaraunga", "#KaupapaMāori", "#PasifikaAI"],
        },
    },

    # ── 4. DATA SOVEREIGNTY ───────────────────────────────────────
    "data-sovereignty": {
        "tpl": "principles",
        "en": {
            "small_italic": "He aha te mana raraunga?",
            "headline": "What is data sovereignty?",
            "body": "Data sovereignty is the right of a people to govern data about them — who collects it, who uses it, who profits, and who is harmed.",
            "bullets": [
                ("Tino rangatiratanga", "Self-determination over data — full stop."),
                ("Whakapapa",           "Data has genealogy. It comes from someone."),
                ("Kaitiakitanga",       "Guardianship, not ownership — stewardship."),
                ("Mana",                "Data about Māori carries Māori mana."),
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
                ("Whakapapa",           "He whakapapa tō ngā raraunga. Nō tētahi mai."),
                ("Kaitiakitanga",       "He kaitiakitanga, ehara i te kainga noa."),
                ("Mana",                "He mana Māori tō ngā raraunga Māori."),
            ],
            "footer_line": "Ka tirohia tēnei i te Wāhanga 4 o Te Pā Tūwatawata.",
            "cta": "Akoranga kore utu · kiwidialectic.com",
            "hashtags": ["#Tikanga", "#ManaRaraunga", "#TaketakeRaraunga", "#TinoRangatiratanga"],
        },
        "pt": {
            "small_italic": "He aha te mana raraunga? — em te reo",
            "headline": "O que é soberania de dados?",
            "body": "Soberania de dados é o direito de um povo de governar os dados sobre si — quem coleta, quem usa, quem lucra e a quem podem prejudicar.",
            "bullets": [
                ("Autodeterminação",  "Tino rangatiratanga — autogoverno sobre os dados."),
                ("Whakapapa (linhagem)", "Os dados têm genealogia. Vêm de alguém."),
                ("Kaitiakitanga",     "Tutela — não propriedade. Cuidado coletivo."),
                ("Mana",              "Dados Māori carregam mana Māori."),
            ],
            "footer_line": "O Módulo 4 de Te Pā Tūwatawata aprofunda este tema.",
            "cta": "Curso gratuito · kiwidialectic.com",
            "hashtags": ["#Tikanga", "#SoberaniaDeDados", "#DadosIndígenas", "#Autodeterminação"],
        },
        "gn": {
            "small_italic": "He aha te mana raraunga? — te reo-pe",
            "headline": "Mba'épa mba'e tendu reko pypuku?",
            "body": "Mba'e tendu reko pypuku ha'e peteĩ tetãygua puguáke oñangareko mba'e tendu hesegua — máva ombyaty, máva oipuru, máva oñemonguera, ha mávape ombyai.",
            "bullets": [
                ("Tekoñemoñe'ẽrã", "Tino rangatiratanga — oñemoñe'ẽ mba'e tenduére."),
                ("Whakapapa",      "Mba'e tendu oguereko iñypyrũ. Oúgui peteĩva."),
                ("Kaitiakitanga",  "Ñañangareko — ndaha'éi ñande mba'e."),
                ("Mana",           "Māori-kuéra mba'e tendu ogueraha Māori mana."),
            ],
            "footer_line": "Te Pā Tūwatawata Mbo'ekuatia 4 ohesa'ỹijo upéichagua mba'e.",
            "cta": "Mbo'esyry rei · kiwidialectic.com",
            "hashtags": ["#Tikanga", "#MbaeTenduReko", "#TekoIndígena", "#Tekoñemoñe'ẽ"],
        },
        "sm": {
            "small_italic": "He aha te mana raraunga? — i le gagana Māori",
            "headline": "O ā le pule i fa'amaumauga?",
            "body": "O le pule i fa'amaumauga o le aiā tatau lea o se atunu'u e pulea fa'amaumauga e uiga ia i latou — o ai e aoina, o ai e fa'aaogā, o ai e maua se tupe, ma o ai e a'afia.",
            "bullets": [
                ("Tino rangatiratanga", "Pule iā te oe lava i au fa'amaumauga."),
                ("Whakapapa",           "E iai le gafa o fa'amaumauga. E sau mai i se tasi."),
                ("Kaitiakitanga",       "Tausiga — ae lē o le umiaina."),
                ("Mana",                "O fa'amaumauga e uiga i Māori e iai le mana o Māori."),
            ],
            "footer_line": "O lo'o va'aia lenei mea i le Vāega 4 o Te Pā Tūwatawata.",
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
                "Teaching kit PDFs  ·  social kit  ·  free",
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
                "PDF whakaako  ·  pouaka pāpori  ·  utu kore",
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
                "6 módulos  ·  bilíngue te reo / inglês",
                "Freire · Graeber · Kropotkin · Kaupapa Māori",
                "PDFs de ensino  ·  kit de redes  ·  gratuito",
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
                "PDF a'oa'oga  ·  pusa fa'asalalau  ·  fua",
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
    # Editorial rule: BIG italic native = te reo whakataukī (anchor, all langs).
    # Bold "english_sub" = target language. eng_caption = target-language gloss.
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
            "body": "Um futuro digital soberano não é um destino. É uma prática — de consentimento, de responsabilidade, e de construir tecnologia que responde ao povo que serve.",
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
            "body": "O se lumana'i fa'akomepiuta pulea, e lē o se nofoaga e taunu'u i ai. O se faiga — o le fa'atagaga, o le tali atu, ma le fauina o tekonolosi e tali atu i tagata o lo'o tautua i ai.",
            "hashtags": ["#KaupapaMāori", "#PuleFa'amaumauga", "#PasifikaAI", "#Anamata"],
        },
    },
}

# ─── Dispatch ───────────────────────────────────────────────────────────
TEMPLATES = {
    "slogan":     template_slogan,
    "list":       template_list,
    "quote":      template_quote,
    "principles": template_principles,
    "cta":        template_cta,
    "anamata":    template_anamata,
}
LANGS = ["en", "mi", "pt", "gn", "sm"]


# ─── Bilingual cover: top half EN, bottom half MI ──────────────────────
def render_bilingual_cover(meme_id, en_img, mi_img):
    """Compose a 1080×1080 cover.
    Take the CONTENT region (between top and bottom motif bands) from each
    source image, downscale to half-height, and stack:
      top half  = EN headline/content (downscaled)
      bottom    = MI headline/content (downscaled)
    A niho-taniwha band sits across the middle as the cultural divider, and
    niho bands frame top and bottom. EN/MI badges in corners.
    """
    cover = Image.new("RGB", (W, H), BLACK)
    draw_unaunahi_motif(cover, 0, 0, W, H, base_color=BLACK)

    # source content region: between top motif (y=60) and bottom motif (y=H-60)
    src_top, src_bot = 60, H - 60
    src_h = src_bot - src_top
    # destination: each language gets ~430px of vertical space
    # top band:    60..490   (430px)
    # middle niho: 490..570  (80px)
    # bot band:    570..1000 (430px)
    # bottom motif:1000..1080
    top_y0, top_y1 = 70, 490
    bot_y0, bot_y1 = 590, 1010
    target_h_top = top_y1 - top_y0
    target_h_bot = bot_y1 - bot_y0

    en_content = en_img.crop((0, src_top, W, src_bot))
    mi_content = mi_img.crop((0, src_top, W, src_bot))
    # Downscale to target heights while preserving width
    en_scaled = en_content.resize((W, target_h_top), Image.LANCZOS)
    mi_scaled = mi_content.resize((W, target_h_bot), Image.LANCZOS)

    cover.paste(en_scaled, (0, top_y0))
    cover.paste(mi_scaled, (0, bot_y0))

    draw = ImageDraw.Draw(cover)
    # Top + bottom motif bands (niho)
    _niho(draw, "top", color=RED, bg=BLACK, band_h=60)
    _niho(draw, "bottom", color=RED, bg=BLACK, band_h=60)

    # Mid divider — niho on red
    band_y, band_h = 500, 70
    draw.rectangle([0, band_y, W, band_y + band_h], fill=RED)
    tooth_w, tooth_h = 32, 30
    n = W // tooth_w + 1
    for i in range(n):
        x = i * tooth_w
        draw.polygon([(x, band_y + band_h - tooth_h),
                      (x + tooth_w / 2, band_y + band_h),
                      (x + tooth_w, band_y + band_h - tooth_h)], fill=BLACK)
        draw.polygon([(x, band_y + tooth_h), (x + tooth_w / 2, band_y),
                      (x + tooth_w, band_y + tooth_h)], fill=BLACK)

    # Language badges in cream pill — top-left for EN, top-left of MI for MI
    def badge(text, x, y):
        f = font(F_SANS_BOLD, 20)
        tw, th = measure(draw, text, f)
        pad_x, pad_y = 12, 6
        draw.rectangle([x, y, x + tw + 2 * pad_x, y + th + 2 * pad_y], fill=RED)
        draw.text((x + pad_x, y + pad_y - 2), text, font=f, fill=CREAM)
    # Place badges in the top-right of each half so they don't overlap text
    badge("EN", W - 90, 78)
    badge("MI", W - 90, 598)
    return cover


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    total = 0
    rendered = {}  # (meme, lang) -> image (kept so we can build the cover)
    for meme_id, spec in CONTENT.items():
        if only and only != meme_id:
            continue
        tpl_fn = TEMPLATES[spec["tpl"]]
        for lang in LANGS:
            payload = dict(spec[lang])
            payload["lang"] = lang
            img = tpl_fn(**payload)
            out = os.path.join(OUT_DIR, f"campaign-{meme_id}-{lang}.png")
            img.save(out, "PNG", optimize=True)
            rendered[(meme_id, lang)] = img
            print(f"  ✓ {out}")
            total += 1
        # Build true bilingual cover from EN+MI renders
        cover = render_bilingual_cover(meme_id,
                                       rendered[(meme_id, "en")],
                                       rendered[(meme_id, "mi")])
        cover_out = os.path.join(OUT_DIR, f"campaign-{meme_id}.png")
        cover.save(cover_out, "PNG", optimize=True)
        print(f"  ✓ {cover_out}   (bilingual cover)")
        total += 1
    print(f"\nGenerated {total} files.")


if __name__ == "__main__":
    main()
