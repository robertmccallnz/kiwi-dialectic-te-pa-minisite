#!/usr/bin/env python3
"""
Generate translated variants of the 8 Unaunahi stickers and 7 wheatpaste posters.

The te reo Māori name stays sacred (mana of the word — not translated).
Only the gloss / supporting line is translated, into:
  - sm : Gagana Sāmoa
  - pt : Português
  - gn : Avañe'ẽ (Guaraní)
  - ar : العربية (Arabic, RTL)

en is the source (already present). mi (te reo) is the primary text and is
already on every asset.

Run from repo root:
    python3 scripts/generate-i18n-stickers.py
"""

import os, re, json, pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
SRC_STICKERS = REPO / "social-kit/stickers"
SRC_POSTERS  = REPO / "social-kit/posters"
OUT_STICKERS = REPO / "stickers/i18n"
OUT_POSTERS  = REPO / "stickers/i18n-posters"
OUT_STICKERS.mkdir(parents=True, exist_ok=True)
OUT_POSTERS.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Sticker translations.
# Key = source English gloss (must match exactly). Each entry maps to the four
# target glosses. Translations crafted to fit similar character count so that
# the existing font size still renders within the bounds.
# ─────────────────────────────────────────────────────────────────────────────

STICKER_TR = {
    "WE ARE ARMOUR": {
        "sm": "O MATOU O FAATALITALI",
        "pt": "SOMOS A ARMADURA",
        "gn": "ÑANDE PYHARE",          # we are the night/cover
        "ar": "نَحْنُ الدِّرْعُ",
    },
    "BUILD YOUR OWN SYSTEMS": {
        "sm": "FAU AU LAVA FAIGAOGANA",
        "pt": "CONSTRUA SEUS SISTEMAS",
        "gn": "EMOPU'Ã NE REMBIPORU",
        "ar": "ابْنِ أنظِمَتَكَ",
    },
    "HOLD YOUR CONSENT": {
        "sm": "TAOFI LOU IOEGA",
        "pt": "MANTENHA SEU CONSENTIMENTO",
        "gn": "EMOMBA NE PY'APY",
        "ar": "احْفَظْ مُوافقَتَكَ",
    },
    "MAORI DATA SOVEREIGNTY": {
        "sm": "PULEAGA O TUSITUSIGA MAORI",
        "pt": "SOBERANIA DE DADOS MĀORI",
        "gn": "TETÃ MĀORI MARANDU REKO",
        "ar": "سِيادَةُ بَياناتِ الماوْري",
    },
    "SOVEREIGN FUTURES": {
        "sm": "LUMANA'I PULEA",
        "pt": "FUTUROS SOBERANOS",
        "gn": "TENONDERÃ TETÃ",
        "ar": "مُستَقبَلٌ سَيِّدٌ",
    },
    "STRENGTH IN LAYERS": {
        "sm": "MALOSI I LAPALAPA",
        "pt": "FORÇA EM CAMADAS",
        "gn": "MBARETE OJUEHEGUI",
        "ar": "قُوَّةٌ مُتَطَبِّقَةٌ",
    },
    "STAND FIRM": {
        "sm": "TŪ MAU",
        "pt": "MANTENHA-SE FIRME",
        "gn": "EÑEMBO'Y MBARETE",
        "ar": "اِثْبُتْ",
    },
    "ABSOLUTE SOVEREIGNTY": {
        "sm": "PULEA ATOATOA",
        "pt": "SOBERANIA ABSOLUTA",
        "gn": "TETÃREKO TUVICHA",
        "ar": "السِّيادَةُ الكامِلَةُ",
    },
}

# Map of sticker slug → (source gloss to find and replace)
STICKER_FILES = {
    "sticker-una-armour.svg":  "WE ARE ARMOUR",
    "sticker-una-build.svg":   "BUILD YOUR OWN SYSTEMS",
    "sticker-una-consent.svg": "HOLD YOUR CONSENT",
    "sticker-una-data.svg":    "MAORI DATA SOVEREIGNTY",
    "sticker-una-future.svg":  "SOVEREIGN FUTURES",
    "sticker-una-layers.svg":  "STRENGTH IN LAYERS",
    "sticker-una-resist.svg":  "STAND FIRM",
    "sticker-una-tino.svg":    "ABSOLUTE SOVEREIGNTY",
}

# ─────────────────────────────────────────────────────────────────────────────
# Wheatpaste poster translations.
# Each poster has a tagline (the "Stand firm. Your data. Your terms. Always."
# style English line). The te reo and motif name stay; the tagline rotates.
# ─────────────────────────────────────────────────────────────────────────────

POSTER_TR = {
    # ── A3 posters
    "Our data. Our terms. Our future.": {
        "sm": "A matou tusitusiga. A matou tulafono. Lumana'i.",
        "pt": "Nossos dados. Nossas regras. Nosso futuro.",
        "gn": "Ñande marandu. Ñande py'apy. Ñande tenondegua.",
        "ar": "بَياناتُنا. شُروطُنا. مُستَقبَلُنا.",
    },
    "We are layered. We are armoured. We endure.": {
        "sm": "Ua matou faaopoopo. Ua matou aautu. Ua matou tūmau.",
        "pt": "Somos camadas. Somos armadura. Permanecemos.",
        "gn": "Ñande ipara, ñande pyhare, ñande hekove.",
        "ar": "نَحْنُ طَبَقاتٌ. نَحْنُ دِرْعٌ. نَحْنُ نَدومُ.",
    },
    # ── A4 posters
    "AI does not own you. Stand firm.": {
        "sm": "E le pulea oe e le AI. Tū maluō.",
        "pt": "A IA não te possui. Resiste firme.",
        "gn": "AI ndoiporúi ndéve. Eñembo'y mbarete.",
        "ar": "الذَّكاءُ الاصطِناعيُّ لا يَملِكُكَ. اِثْبُتْ.",
    },
    "The future is ours to build.": {
        "sm": "O le lumana'i o le ā matou faufau.",
        "pt": "O futuro é nosso para construir.",
        "gn": "Tenondegua ñande mba'e jajapo haĝua.",
        "ar": "المُستَقبَلُ لَنا نَبْنيهِ.",
    },
    "Together we stand. Together we govern.": {
        "sm": "Tā tatou tutū fa'atasi. Tā tatou pule fa'atasi.",
        "pt": "Juntos estamos. Juntos governamos.",
        "gn": "Oñondive ñañemboʼy. Oñondive ñasãmbyhy.",
        "ar": "نَقومُ مَعًا. نَحكُمُ مَعًا.",
    },
    "Layer upon layer of sovereignty.": {
        "sm": "Lapalapa ma lapalapa o le puleaga.",
        "pt": "Camada após camada de soberania.",
        "gn": "Pe pe rehe tetãreko.",
        "ar": "طَبَقَةٌ فَوْقَ طَبَقَةٍ مِنَ السِّيادَةِ.",
    },
    "Stand firm. Your data. Your terms. Always.": {
        "sm": "Tū maluō. Au tusitusiga. Au tulafono. I taimi uma.",
        "pt": "Resiste firme. Seus dados. Suas regras. Sempre.",
        "gn": "Eñembo'y mbarete. Ne marandu. Ne reko. Akóinte.",
        "ar": "اِثْبُتْ. بَياناتُكَ. شُروطُكَ. دائِمًا.",
    },
}

POSTER_FILES = {
    "una-poster-a3-data-sovereignty.svg": "Our data. Our terms. Our future.",
    "una-poster-a3-we-are-armour.svg":    "We are layered. We are armoured. We endure.",
    "una-poster-a4-ai-resist.svg":        "AI does not own you. Stand firm.",
    "una-poster-a4-future.svg":           "The future is ours to build.",
    "una-poster-a4-kotahitanga.svg":      "Together we stand. Together we govern.",
    "una-poster-a4-layers.svg":           "Layer upon layer of sovereignty.",
    "una-poster-a4-stand-firm.svg":       "Stand firm. Your data. Your terms. Always.",
}

LANGS = ["sm", "pt", "gn", "ar"]

def is_rtl(lang):
    return lang == "ar"

def translate_sticker(svg_text, source_en, lang):
    """Replace just the English gloss line in a sticker SVG."""
    translation = STICKER_TR[source_en][lang]
    # The gloss is a single-line <text>…WE ARE ARMOUR</text> element.
    # Use a tolerant regex that matches the exact gloss in any case.
    pattern = re.compile(
        r'(<text[^>]*>)' + re.escape(source_en) + r'(</text>)',
        re.IGNORECASE,
    )
    new_svg = pattern.sub(lambda m: m.group(1) + translation + m.group(2), svg_text, count=1)
    if is_rtl(lang):
        # Add dir/lang attributes on <svg> root for Arabic; also force RTL on
        # the gloss text element so it shapes correctly when opened in a browser
        new_svg = re.sub(
            r'<svg\b',
            '<svg lang="ar" dir="rtl"',
            new_svg,
            count=1,
        )
        # Switch the gloss font-family to one that has Arabic glyphs
        new_svg = new_svg.replace(
            'font-family="Arial, sans-serif"',
            'font-family="Noto Naskh Arabic, Tahoma, Arial, sans-serif"',
            1,  # only the first occurrence (the gloss line)
        )
    return new_svg

def translate_poster(svg_text, source_en, lang):
    translation = POSTER_TR[source_en][lang]
    new_svg = svg_text.replace(source_en, translation)
    if is_rtl(lang):
        new_svg = re.sub(
            r'<svg\b',
            '<svg lang="ar" dir="rtl"',
            new_svg,
            count=1,
        )
        new_svg = new_svg.replace(
            'font-family="Arial, sans-serif"',
            'font-family="Noto Naskh Arabic, Tahoma, Arial, sans-serif"',
            1,
        )
    return new_svg

def main():
    n_sticker = n_poster = 0
    for slug, source_en in STICKER_FILES.items():
        src = (SRC_STICKERS / slug).read_text()
        # Always emit a copy of the english source under stickers/i18n/ so all 6
        # languages live in the same place
        base = slug.rsplit(".svg", 1)[0]
        (OUT_STICKERS / f"{base}-en.svg").write_text(src)
        (OUT_STICKERS / f"{base}-mi.svg").write_text(src)  # mi == sacred reo, same file
        for lang in LANGS:
            out = translate_sticker(src, source_en, lang)
            (OUT_STICKERS / f"{base}-{lang}.svg").write_text(out)
            n_sticker += 1

    for slug, source_en in POSTER_FILES.items():
        src = (SRC_POSTERS / slug).read_text()
        base = slug.rsplit(".svg", 1)[0]
        (OUT_POSTERS / f"{base}-en.svg").write_text(src)
        (OUT_POSTERS / f"{base}-mi.svg").write_text(src)
        for lang in LANGS:
            out = translate_poster(src, source_en, lang)
            (OUT_POSTERS / f"{base}-{lang}.svg").write_text(out)
            n_poster += 1

    # Write a manifest for the page to consume
    manifest = {
        "stickers": {
            slug.rsplit(".svg", 1)[0]: {
                "source_gloss": gloss,
                "languages": {
                    "en": gloss,
                    "mi": "sacred — te reo source unchanged",
                    **{l: STICKER_TR[gloss][l] for l in LANGS},
                }
            } for slug, gloss in STICKER_FILES.items()
        },
        "posters": {
            slug.rsplit(".svg", 1)[0]: {
                "source_tagline": tagline,
                "languages": {
                    "en": tagline,
                    "mi": "sacred — te reo source unchanged",
                    **{l: POSTER_TR[tagline][l] for l in LANGS},
                }
            } for slug, tagline in POSTER_FILES.items()
        }
    }
    (OUT_STICKERS / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(f"✓ generated {n_sticker} translated stickers in {OUT_STICKERS}")
    print(f"✓ generated {n_poster} translated posters in {OUT_POSTERS}")
    print(f"✓ manifest written")

if __name__ == "__main__":
    main()
