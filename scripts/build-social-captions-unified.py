#!/usr/bin/env python3
"""Build a unified-hashtag variant of campaign-captions.json.

Replaces the existing trailing hashtag line in every caption with a
campaign-wide pair: #TePāTūwatawata #TeManaRaraunga.
Recomputes char_count and data_copy_text. Verifies 280-char budget.
"""
import json
import re
from copy import deepcopy
from pathlib import Path

# Repo-relative paths (script lives at <repo>/scripts/)
ROOT = Path(__file__).resolve().parent.parent
CAPTIONS_DIR = ROOT / "social-kit" / "captions"
SRC = CAPTIONS_DIR / "campaign-captions.json"
DST = CAPTIONS_DIR / "campaign-captions-unified.json"

UNIFIED_TAGS = ["#TePāTūwatawata", "#TeManaRaraunga"]
UNIFIED_LINE = " ".join(UNIFIED_TAGS)

with open(SRC) as f:
    data = json.load(f)

out = deepcopy(data)
out["schema_version"] = "1.0-unified-hashtags"
out["hashtag_policy"] = {
    "mode": "unified",
    "tags": UNIFIED_TAGS,
    "rationale": "Campaign-wide hashtag pair across all cards × languages for cross-post cohesion.",
}

def strip_trailing_hashtag_line(text: str) -> str:
    """Drop the final line of text if it begins with '#'."""
    lines = text.rstrip("\n").split("\n")
    while lines and lines[-1].lstrip().startswith("#"):
        lines.pop()
    # Also drop any trailing blank line we just exposed
    while lines and lines[-1].strip() == "":
        lines.pop()
    return "\n".join(lines)

issues = []
for card in out["cards"]:
    for lang, cap in card["captions"].items():
        body = strip_trailing_hashtag_line(cap["text"])
        new_text = body + "\n\n" + UNIFIED_LINE
        cap["text"] = new_text
        cap["data_copy_text"] = new_text.replace("\n", "&#10;")
        cap["char_count"] = len(new_text)
        cap["hashtags"] = list(UNIFIED_TAGS)
        if cap["char_count"] > 280:
            issues.append(f"{card['card_id']}:{lang} = {cap['char_count']}")

# Refresh the summary
out["char_count_summary"] = {
    card["card_id"]: {lang: cap["char_count"] for lang, cap in card["captions"].items()}
    for card in out["cards"]
}

with open(DST, "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

# Report
mx = 0
print(f"Wrote: {DST}")
print(f"Unified tags: {UNIFIED_LINE}")
print()
print("Per-card char counts:")
for cid, langs in out["char_count_summary"].items():
    parts = "  ".join(f"{l}={c}" for l, c in langs.items())
    print(f"  {cid:20s}  {parts}")
    for c in langs.values():
        if c > mx: mx = c
print()
print(f"Max char count: {mx} (limit 280)")
print(f"Over budget: {len(issues)}")
for i in issues:
    print(f"  - {i}")
