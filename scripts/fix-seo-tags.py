#!/usr/bin/env python3
"""Apply SEO fixes to te-pa.org HTML pages.

Adds missing og: / twitter: / canonical tags; trims overlong meta descriptions;
adds noindex to print-only pages. Idempotent — safe to re-run.

Driven by a small per-page config table below.
"""
import re, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_OG_IMG = "https://te-pa.org/og-image.png"
SITE_TITLE = "Te Pā Tūwatawata"

# (relative_path, canonical_url, og_title, og_description, og_image, options)
# - canonical: None means don't add (already has one or root-level set elsewhere)
# - og_description: shorter, used for both og:description and re-written meta description if too long
# - options: dict — 'trim_desc' (replace meta description), 'noindex' (add robots noindex)
PAGES = [
    # --- Motif subpages (missing og + canonical + twitter:card) ---
    ("motifs/koru.html",
        "https://te-pa.org/motifs/koru.html",
        "Koru — Māori Motif",
        "The unfurling silver fern frond — new life, growth, renewal. Tīmatanga · Tipu · Perpetual movement.",
        DEFAULT_OG_IMG, {}),
    ("motifs/kowhaiwhai.html",
        "https://te-pa.org/motifs/kowhaiwhai.html",
        "Kōwhaiwhai — Māori Motif",
        "Painted rafter patterns inside the wharenui — whakapapa, lineage, the connective rhythm of generations.",
        DEFAULT_OG_IMG, {}),
    ("motifs/niho-taniwha.html",
        "https://te-pa.org/motifs/niho-taniwha.html",
        "Niho Taniwha — Māori Motif",
        "Taniwha's teeth — protection, vigilance, the boundary that defends. A guardian motif.",
        DEFAULT_OG_IMG, {}),
    ("motifs/pa-tuwatawata.html",
        "https://te-pa.org/motifs/pa-tuwatawata.html",
        "Pā Tūwatawata — Māori Motif",
        "The fortified pā — sovereign space, defended ground, the threshold between worlds. Te Pā Tūwatawata.",
        DEFAULT_OG_IMG, {}),
    ("motifs/takarangi.html",
        "https://te-pa.org/motifs/takarangi.html",
        "Takarangi — Māori Motif",
        "The double spiral — Rangi and Papa, the cosmic dance, two forces interwoven across time and space.",
        DEFAULT_OG_IMG, {}),
    ("motifs/unaunahi.html",
        "https://te-pa.org/motifs/unaunahi.html",
        "Unaunahi — Māori Motif",
        "Fish scales — abundance, plenty, the ocean's gift. A motif of sustenance and Pacific connection.",
        DEFAULT_OG_IMG, {}),
    # --- Motifs index — has canonical but missing og:title / og:image / twitter:card ---
    ("motifs/index.html",
        None,  # already has canonical
        "Ngā Tohu Māori — The Six Motifs",
        "Six Māori motifs — Koru, Pā Tūwatawata, Niho Taniwha, Kōwhaiwhai, Unaunahi, Takarangi — with full cultural context.",
        DEFAULT_OG_IMG, {}),
    # --- Modules (have og but missing canonical) ---
    ("modules/module-1.html",
        "https://te-pa.org/modules/module-1.html",
        None, None, None, {}),
    ("modules/module-2.html",
        "https://te-pa.org/modules/module-2.html",
        None, None, None, {}),
    ("modules/module-3.html",
        "https://te-pa.org/modules/module-3.html",
        None, None, None, {}),
    ("modules/module-4.html",
        "https://te-pa.org/modules/module-4.html",
        None, None, None, {}),
    ("modules/module-5.html",
        "https://te-pa.org/modules/module-5.html",
        None, None, None, {}),
    ("modules/module-6.html",
        "https://te-pa.org/modules/module-6.html",
        None, None, None, {}),
    # --- modules/rhizome.html (title and desc too long, missing canonical) ---
    ("modules/rhizome.html",
        "https://te-pa.org/modules/rhizome.html",
        None, None, None,
        {"trim_title": "Te Pakiaka — The Rhizome — Te Pā Tūwatawata",
         "trim_desc": "Underground activism, te reo Māori, and the rhizomatic theory of resistance. A bonus module of Te Pā Tūwatawata."}),
    # --- Rhizome mapper — missing og:title / og:image / twitter:card; desc too long ---
    ("rhizome-mapper.html",
        None,  # already has canonical
        "Rhizome Mapper — Indigenous Connections",
        "Interactive map of indigenous sovereignty, land rights, data sovereignty and environmental justice movements worldwide.",
        DEFAULT_OG_IMG,
        {"trim_desc": "Interactive map of indigenous sovereignty, land rights, data sovereignty and environmental justice movements worldwide."}),
    # --- Long-description pages (desc too long, otherwise OK) ---
    ("campaign-generator/index.html", None, None, None, None,
        {"trim_desc": "Generate posters, stickers, and street-campaign assets for protest, organising, and grassroots education. Free, multilingual."}),
    ("launch-mediakit/index.html", None, None, None, None,
        {"trim_desc": "Launch-day media kit for journalists, partners, and educators: assets, thread copy in 6 languages, and one-page bundles."}),
    ("social-kit/index.html", None, None, None, None,
        {"trim_desc": "768 culturally-rooted SVG cards across 6 languages, ready for Facebook, Instagram, TikTok and X — with captions and meme kits."}),
    ("stickers/index.html", None, None, None, None,
        {"trim_desc": "Print-ready sticker pack for street activism — QR-coded designs, motif lineage, and a full distribution toolkit."}),
    ("stickers/gallery/index.html",
        "https://te-pa.org/stickers/gallery/",
        "Campaign Gallery — Te Pā Tūwatawata",
        "Browse the full campaign sticker gallery — print-ready designs, motifs, and downloads.",
        DEFAULT_OG_IMG,
        {"trim_desc": "Browse the full campaign sticker gallery — print-ready designs, motifs, and downloads."}),
    ("teaching-kits/index.html", None, None, None, None,
        {"trim_desc": "Teaching kits for educators — six languages, full lesson plans, activity sheets, and a teacher's handbook."}),
    ("solidarity/australia/index.html",
        None,  # already has canonical/og:title etc, just need og:image
        None, None, DEFAULT_OG_IMG,
        {"trim_desc": "Solidarity with Australian First Nations — protocol map, partner directory, Indigenous data sovereignty references, and outreach scaffold."}),
    ("partner-onboarding/index.html",
        None, None, None, DEFAULT_OG_IMG, {}),
    # --- Social kit captions ---
    ("social-kit/captions/index.html",
        "https://te-pa.org/social-kit/captions/",
        "Ready-to-copy Captions — Te Pā Tūwatawata Social Kit",
        "Ready-to-copy captions for every motif × platform × language combination — Facebook, Instagram, TikTok, X.",
        DEFAULT_OG_IMG, {}),
    ("social-kit/captions/print.html",
        None, None, None, None,
        {"noindex": True}),  # print view, should not be indexed
    # --- Unaunahi art series ---
    ("social-kit/unaunahi/index.html",
        "https://te-pa.org/social-kit/unaunahi/",
        "Unaunahi Art Series — The Kiwi Dialectic",
        "The Unaunahi art series — fish-scale motif art for social media and street activism.",
        DEFAULT_OG_IMG,
        {"add_desc": "The Unaunahi art series — fish-scale motif art for social media and street activism."}),
]

def patch_head(html: str, *, canonical=None, og_title=None, og_description=None,
               og_image=None, trim_desc=None, trim_title=None, noindex=False,
               add_desc=None) -> tuple[str, list[str]]:
    """Patch the <head>. Returns (new_html, list_of_changes)."""
    changes = []
    head_match = re.search(r"(<head[^>]*>)(.*?)(</head>)", html, re.S | re.I)
    if not head_match:
        return html, ["no <head> found, skipped"]
    head_open, head_inner, head_close = head_match.groups()

    # --- Trim overlong meta description ---
    if trim_desc:
        new_inner, n = re.subn(
            r'<meta\s+name="description"\s+content="[^"]*"\s*/?>',
            f'<meta name="description" content="{trim_desc}"/>',
            head_inner, count=1)
        if n:
            head_inner = new_inner
            changes.append(f"trimmed meta description ({len(trim_desc)} chars)")
        else:
            # no existing desc — add one
            head_inner = head_inner.rstrip() + f'\n  <meta name="description" content="{trim_desc}"/>\n'
            changes.append(f"added meta description ({len(trim_desc)} chars)")

    # --- Add meta description if missing ---
    if add_desc and 'name="description"' not in head_inner:
        head_inner = head_inner.rstrip() + f'\n  <meta name="description" content="{add_desc}"/>\n'
        changes.append(f"added meta description ({len(add_desc)} chars)")

    # --- Trim overlong title ---
    if trim_title:
        new_inner, n = re.subn(r'<title>[^<]*</title>',
                               f'<title>{trim_title}</title>',
                               head_inner, count=1)
        if n:
            head_inner = new_inner
            changes.append(f"trimmed <title> ({len(trim_title)} chars)")

    # --- Add canonical if missing ---
    if canonical and not re.search(r'<link\s+rel="canonical"', head_inner, re.I):
        head_inner = head_inner.rstrip() + f'\n  <link rel="canonical" href="{canonical}"/>\n'
        changes.append("added canonical")

    # --- Add og:title if missing ---
    if og_title and not re.search(r'<meta\s+property="og:title"', head_inner, re.I):
        full_title = f"{og_title} — {SITE_TITLE}" if SITE_TITLE not in og_title else og_title
        head_inner = head_inner.rstrip() + f'\n  <meta property="og:title" content="{full_title}"/>\n'
        changes.append("added og:title")

    # --- Add og:description if missing ---
    if og_description and not re.search(r'<meta\s+property="og:description"', head_inner, re.I):
        head_inner = head_inner.rstrip() + f'\n  <meta property="og:description" content="{og_description}"/>\n'
        changes.append("added og:description")

    # --- Add og:image if missing ---
    if og_image and not re.search(r'<meta\s+property="og:image"', head_inner, re.I):
        head_inner = head_inner.rstrip() + (
            f'\n  <meta property="og:image" content="{og_image}"/>'
            f'\n  <meta property="og:image:width" content="1200"/>'
            f'\n  <meta property="og:image:height" content="630"/>'
            f'\n  <meta property="og:type" content="website"/>'
            f'\n  <meta property="og:url" content="{canonical or ""}"/>'
        ).replace('og:url" content=""/>', '') + '\n'
        changes.append("added og:image (+ og:type/url)")

    # --- Add twitter:card if missing ---
    if og_image and not re.search(r'<meta\s+name="twitter:card"', head_inner, re.I):
        head_inner = head_inner.rstrip() + (
            f'\n  <meta name="twitter:card" content="summary_large_image"/>'
            f'\n  <meta name="twitter:image" content="{og_image}"/>'
        ) + '\n'
        changes.append("added twitter:card")

    # --- noindex robots ---
    if noindex and not re.search(r'<meta\s+name="robots"', head_inner, re.I):
        head_inner = head_inner.rstrip() + '\n  <meta name="robots" content="noindex"/>\n'
        changes.append("added noindex")

    new_html = html[:head_match.start()] + head_open + head_inner + head_close + html[head_match.end():]
    return new_html, changes

def main():
    total = 0
    for rel, canonical, og_title, og_desc, og_image, opts in PAGES:
        p = ROOT / rel
        if not p.exists():
            print(f"  SKIP (missing): {rel}")
            continue
        original = p.read_text(encoding='utf-8')
        new, changes = patch_head(
            original,
            canonical=canonical,
            og_title=og_title,
            og_description=og_desc,
            og_image=og_image,
            **opts,
        )
        if changes and new != original:
            p.write_text(new, encoding='utf-8')
            total += 1
            print(f"  {rel}")
            for c in changes: print(f"      • {c}")
        else:
            print(f"  - {rel} (no changes)")
    print(f"\nUpdated {total} files.")

if __name__ == "__main__":
    main()
