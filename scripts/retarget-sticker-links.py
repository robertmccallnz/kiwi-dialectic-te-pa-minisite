#!/usr/bin/env python3
"""
Retarget all kiwidialectic.com references inside the sticker + poster SVGs
to topical te-pa.org pages.

Runs over:
  - social-kit/stickers/sticker-una-*.svg        (8 sources)
  - social-kit/posters/una-poster-*.svg          (7 sources)
  - stickers/i18n/sticker-una-*.svg              (49 translated)
  - stickers/i18n-posters/una-poster-*.svg       (42 translated)

For each slug, the embedded footer text gets rewritten:
  * "kiwidialectic.com"         -> te-pa.org/<topical>
  * "www.kiwidialectic.com"     -> te-pa.org/<topical>
  * "THE KIWI DIALECTIC"        -> "TE PĀ TŪWATAWATA"

Then it renders PNG previews of the 15 source SVGs into
  - social-kit/stickers/png/  (stickers, 1200px wide)
  - social-kit/posters/png/   (posters, 1200px on the long side)

Usage:
    python3 scripts/retarget-sticker-links.py
"""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Map slug stem -> topical te-pa.org page (no leading https://, no trailing slash needed)
SLUG_TARGET = {
    # Stickers
    "sticker-una-armour":  "te-pa.org/motifs/unaunahi.html",
    "sticker-una-build":   "te-pa.org/modules/module-6.html",
    "sticker-una-consent": "te-pa.org/modules/module-3.html",
    "sticker-una-data":    "te-pa.org/modules/module-3.html",
    "sticker-una-future":  "te-pa.org/launch-mediakit/",
    "sticker-una-layers":  "te-pa.org/motifs/unaunahi.html",
    "sticker-una-resist":  "te-pa.org/modules/rhizome.html",
    "sticker-una-tino":    "te-pa.org/modules/module-4.html",
    # Posters
    "una-poster-a3-data-sovereignty": "te-pa.org/modules/module-3.html",
    "una-poster-a3-we-are-armour":    "te-pa.org/motifs/unaunahi.html",
    "una-poster-a4-ai-resist":        "te-pa.org/modules/rhizome.html",
    "una-poster-a4-future":           "te-pa.org/launch-mediakit/",
    "una-poster-a4-kotahitanga":      "te-pa.org/solidarity/australia/",
    "una-poster-a4-layers":           "te-pa.org/motifs/unaunahi.html",
    "una-poster-a4-stand-firm":       "te-pa.org/modules/rhizome.html",
}


def slug_for_path(p: Path) -> str:
    """Strip language suffix ('-en','-mi',…) and .svg extension to get base slug."""
    stem = p.stem  # e.g. sticker-una-armour-mi
    # Strip a trailing -<2 letter lang>
    return re.sub(r"-(en|mi|sm|pt|gn|ar)$", "", stem)


def retarget(svg_text: str, target_url: str) -> str:
    """Replace kiwidialectic references with the topical te-pa.org URL."""
    # Order matters: do longer/more-specific patterns first
    replacements = [
        (r"www\.kiwidialectic\.com", target_url),
        (r"kiwidialectic\.com",      target_url),
        (r"THE KIWI DIALECTIC",      "TE PĀ TŪWATAWATA"),
        (r"<!--\s*kiwidialectic[^>]*-->", "<!-- credit -->"),
    ]
    out = svg_text
    for pat, repl in replacements:
        out = re.sub(pat, repl, out)
    return out


def walk(dirpath: Path, label: str):
    count_changed = 0
    count_skipped = 0
    if not dirpath.exists():
        print(f"  (skip — {dirpath} does not exist)")
        return 0, 0
    for f in sorted(dirpath.glob("*.svg")):
        slug = slug_for_path(f)
        target = SLUG_TARGET.get(slug)
        if not target:
            print(f"  ! no mapping for slug={slug} ({f.name}); skipped")
            count_skipped += 1
            continue
        original = f.read_text(encoding="utf-8")
        rewritten = retarget(original, target)
        if rewritten != original:
            f.write_text(rewritten, encoding="utf-8")
            count_changed += 1
        else:
            count_skipped += 1
    print(f"  {label}: rewrote {count_changed}, skipped {count_skipped}")
    return count_changed, count_skipped


def render_pngs():
    """Render 1200px-wide PNGs for the 15 source SVGs (for website previews)."""
    try:
        import cairosvg
    except ImportError:
        print("\n[!] cairosvg not installed — skipping PNG export.")
        print("    Install with: pip install cairosvg")
        return 0

    sticker_out = REPO / "social-kit" / "stickers" / "png"
    poster_out  = REPO / "social-kit" / "posters"  / "png"
    sticker_out.mkdir(parents=True, exist_ok=True)
    poster_out.mkdir(parents=True, exist_ok=True)

    rendered = 0

    for svg in sorted((REPO / "social-kit" / "stickers").glob("sticker-una-*.svg")):
        out = sticker_out / (svg.stem + ".png")
        cairosvg.svg2png(url=str(svg), write_to=str(out), output_width=1200)
        rendered += 1

    for svg in sorted((REPO / "social-kit" / "posters").glob("una-poster-*.svg")):
        # A3 are landscape, A4 are portrait — use width=1200 for both
        out = poster_out / (svg.stem + ".png")
        cairosvg.svg2png(url=str(svg), write_to=str(out), output_width=1200)
        rendered += 1

    print(f"  PNG previews: rendered {rendered} files")
    return rendered


def main():
    print("Retargeting kiwidialectic.com references → te-pa.org topical pages:\n")

    total_changed = 0
    total_skipped = 0

    for label, p in [
        ("social-kit/stickers (source)",     REPO / "social-kit/stickers"),
        ("social-kit/posters (source)",      REPO / "social-kit/posters"),
        ("stickers/i18n (translated)",       REPO / "stickers/i18n"),
        ("stickers/i18n-posters (translated)", REPO / "stickers/i18n-posters"),
    ]:
        print(f"-- {label}: {p}")
        c, s = walk(p, label)
        total_changed += c
        total_skipped += s

    print(f"\nTotal: {total_changed} files rewritten, {total_skipped} skipped/no-op\n")

    print("Rendering PNG previews:")
    render_pngs()


if __name__ == "__main__":
    main()
