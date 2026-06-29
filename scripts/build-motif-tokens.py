#!/usr/bin/env python3
"""Generate assets/css/motif-tokens.css — per-culture CSS custom properties.

Sibling sites import this file and get `[data-culture="maori"] { --motif-primary: ... }`
selectors plus an `:root` default. Single source of truth = motif-bank-master.json.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "motif-bank-master.json"
OUT = ROOT / "assets" / "css" / "motif-tokens.css"


def main() -> int:
    bank = json.load(DATA.open())
    by_culture: dict[str, list[dict]] = {}
    for m in bank["motifs"]:
        by_culture.setdefault(m["culture"], []).append(m)

    lines = [
        "/* motif-tokens.css — generated from data/motif-bank-master.json */",
        "/* DO NOT EDIT BY HAND. Run scripts/build-motif-tokens.py. */",
        "/* License: CC BY-NC-SA 4.0 — Te Pā Tūwatawata */",
        "",
        ":root {",
        "  /* default ecosystem palette (Te Pā / Māori) */",
        "  --motif-primary: #2ecc71;",
        "  --motif-secondary: #1a9e55;",
        "  --motif-accent: #c0392b;",
        "  --motif-attribution: 'Te Pā Tūwatawata · CC BY-NC-SA 4.0';",
        "}",
        "",
    ]

    for cult in sorted(by_culture):
        motifs = by_culture[cult]
        # Pick dominant + secondary from first motif with both
        primary = motifs[0].get("colour_primary", "#2ecc71")
        secondary = motifs[0].get("colour_secondary") or primary
        # Accent = next distinct colour_primary in the culture
        accent = primary
        seen = {primary}
        for m in motifs[1:]:
            c = m.get("colour_primary")
            if c and c not in seen:
                accent = c
                break
        lines.append(f"[data-culture=\"{cult}\"] {{")
        lines.append(f"  --motif-primary: {primary};")
        lines.append(f"  --motif-secondary: {secondary};")
        lines.append(f"  --motif-accent: {accent};")
        lines.append(f"  --motif-culture: \"{cult}\";")
        lines.append("}")
        lines.append("")

    # Helper utility classes for sibling sites
    lines.extend([
        "/* utility classes — opt-in */",
        ".motif-stripe-bg { background: var(--motif-primary); }",
        ".motif-stripe-border { border-color: var(--motif-primary); }",
        ".motif-stripe-text { color: var(--motif-primary); }",
        ".motif-accent-text { color: var(--motif-accent); }",
        "",
        ".motif-card {",
        "  border-left: 4px solid var(--motif-primary);",
        "  padding: 1rem 1.25rem;",
        "  background: color-mix(in srgb, var(--motif-primary) 6%, transparent);",
        "}",
        "",
    ])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines))
    print(f"Wrote {OUT.relative_to(ROOT)} ({len(by_culture)} cultures)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
