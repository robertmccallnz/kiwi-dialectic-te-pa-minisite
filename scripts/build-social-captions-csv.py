#!/usr/bin/env python3
"""Export campaign captions to CSV (long + wide formats, both hashtag variants)."""
import csv
import json
from pathlib import Path

# Repo-relative paths (script lives at <repo>/scripts/)
ROOT = Path(__file__).resolve().parent.parent
CAPTIONS_DIR = ROOT / "social-kit" / "captions"
SOURCES = [
    ("per_card", CAPTIONS_DIR / "campaign-captions.json"),
    ("unified",  CAPTIONS_DIR / "campaign-captions-unified.json"),
]
LANGS = ["mi", "en", "pt", "gn", "sm"]

# ---------- Long format (one row per card × language) ----------
long_rows = []
for variant, src in SOURCES:
    data = json.loads(src.read_text())
    for card in data["cards"]:
        for lang in LANGS:
            cap = card["captions"][lang]
            long_rows.append({
                "hashtag_variant":  variant,
                "card_id":          card["card_id"],
                "title_mi":         card["title_mi"],
                "title_en":         card["title_en"],
                "lang":             lang,
                "lang_name":        data["languages"][lang]["name"],
                "caption":          cap["text"],
                "char_count":       cap["char_count"],
                "hashtags":         " ".join(cap["hashtags"]),
                "image_bilingual":  card["image_bilingual"],
                "image_lang":       card["image_by_lang"][lang],
                "course_url":       data["course_url"],
                "fits_x_280":       "yes" if cap["char_count"] <= 280 else "no",
                "fits_bluesky_300": "yes" if cap["char_count"] <= 300 else "no",
                "fits_mastodon":    "yes" if cap["char_count"] <= 500 else "no",
            })

long_path = CAPTIONS_DIR / "campaign-captions-long.csv"
with long_path.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(long_rows[0].keys()), quoting=csv.QUOTE_ALL)
    w.writeheader()
    w.writerows(long_rows)

# ---------- Wide format (one row per card; one caption column per language) ----------
def make_wide(variant_key, src_path):
    data = json.loads(src_path.read_text())
    fields = ["card_id", "title_mi", "title_en", "image_bilingual"]
    for lang in LANGS:
        fields += [f"caption_{lang}", f"chars_{lang}", f"image_{lang}"]
    fields += ["hashtags", "course_url", "hashtag_variant"]
    rows = []
    for card in data["cards"]:
        row = {
            "card_id":          card["card_id"],
            "title_mi":         card["title_mi"],
            "title_en":         card["title_en"],
            "image_bilingual":  card["image_bilingual"],
            "course_url":       data["course_url"],
            "hashtag_variant":  variant_key,
        }
        for lang in LANGS:
            cap = card["captions"][lang]
            row[f"caption_{lang}"] = cap["text"]
            row[f"chars_{lang}"]   = cap["char_count"]
            row[f"image_{lang}"]   = card["image_by_lang"][lang]
        # Use first card's hashtags as the "row hashtags" — they're consistent across langs within a variant
        row["hashtags"] = " ".join(card["captions"][LANGS[0]]["hashtags"])
        rows.append(row)
    return fields, rows

# Combine both variants into one wide CSV (variant column distinguishes)
all_fields = None
all_rows = []
for variant, src in SOURCES:
    fields, rows = make_wide(variant, src)
    all_fields = fields  # same shape both times
    all_rows.extend(rows)

wide_path = CAPTIONS_DIR / "campaign-captions-wide.csv"
with wide_path.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=all_fields, quoting=csv.QUOTE_ALL)
    w.writeheader()
    w.writerows(all_rows)

# ---------- Report ----------
print(f"Long CSV:  {long_path}  ({len(long_rows)} rows)")
print(f"Wide CSV:  {wide_path}  ({len(all_rows)} rows)")
print()
print("Column groups (long):", list(long_rows[0].keys()))
print()
print("Column groups (wide):", all_fields)
