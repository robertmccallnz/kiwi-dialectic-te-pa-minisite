#!/usr/bin/env python3
"""Build assets/motifs/manifest.json mapping every local SVG to its motif metadata.

Usage:  python3 scripts/build-motif-manifest.py
Writes: assets/motifs/manifest.json
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "motif-bank-master.json"
SVG_DIR = ROOT / "assets" / "motifs"
OUT = SVG_DIR / "manifest.json"

R2_BASE = "https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev"


def main() -> int:
    with DATA.open() as fh:
        bank = json.load(fh)

    motifs_by_id = {m["id"]: m for m in bank["motifs"]}

    # Discover every local SVG
    svgs = sorted(p.name for p in SVG_DIR.glob("*.svg"))

    entries = []
    for svg in svgs:
        stem = svg[:-4]  # strip .svg
        # Strip variant suffixes to find base motif id
        base = stem
        for suffix in (
            "-dark-square", "-dark-wide",
            "-light-square", "-light-wide",
            "-red-square", "-band",
        ):
            if base.endswith(suffix):
                base = base[: -len(suffix)]
                break

        motif = motifs_by_id.get(base)
        entry = {
            "file": svg,
            "stem": stem,
            "motif_id": base if motif else None,
            "variant": stem[len(base) + 1:] if stem != base else "default",
            "local_path": f"assets/motifs/{svg}",
        }
        if motif:
            entry.update({
                "culture": motif["culture"],
                "name_en": motif["name_en"],
                "name_indigenous": motif["name_indigenous"],
                "colour_primary": motif["colour_primary"],
                "r2_url": f"{R2_BASE}/{motif['svg_r2_key']}",
            })
        entries.append(entry)

    manifest = {
        "version": bank.get("version", "1.0"),
        "generated_for": "Te Pā Tūwatawata + sibling sites",
        "license": "CC BY-NC-SA 4.0",
        "attribution": "Te Pā Tūwatawata — The Kiwi Dialectic",
        "r2_base": R2_BASE,
        "total": len(entries),
        "assets": entries,
    }

    with OUT.open("w") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(f"Wrote {OUT.relative_to(ROOT)} — {len(entries)} assets, "
          f"{sum(1 for e in entries if e['motif_id'])} matched to motifs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
