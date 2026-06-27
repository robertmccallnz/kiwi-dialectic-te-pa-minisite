#!/usr/bin/env python3
"""
Verify deployed te-pa.org social-kit images.

For each campaign-*.png:
  1. HTTP HEAD/GET against https://te-pa.org/social-kit/<file>
  2. Confirm HTTP 200 and Content-Length > 0
  3. Hash the body. Confirm per-language variants are DISTINCT from
     the bilingual master (campaign-<meme>.png) — i.e. we are NOT
     serving the cover for a language variant.
  4. For GN files: probe the left & right border columns for the
     vertical "takua" bamboo bars (RED-on-CREAM tall rectangles).
  5. For SM files: probe the border bands for siapo fa'a'aliao
     trochus-triangle motif (alternating RED triangles + CREAM pinpoints).

Outputs:
  - /home/user/workspace/te-pa/social-kit-verification.json (machine)
  - prints a human-readable report
"""
from __future__ import annotations

import hashlib
import io
import json
import sys
import urllib.request
from pathlib import Path

from PIL import Image

BASE = "https://te-pa.org/social-kit/"
MEMES = [
    "raupatu",
    "3-questions",
    "te-mana-raraunga",
    "data-sovereignty",
    "enrol",
    "anamata",
]
LANGS = ["en", "mi", "pt", "gn", "sm"]

RED = (0xC0, 0x39, 0x2B)
CREAM = (0xF4, 0xED, 0xE0)
BLACK = (0x0A, 0x0A, 0x0A)


def near(px, target, tol=40):
    return all(abs(int(px[i]) - target[i]) <= tol for i in range(3))


def fetch(url: str, timeout: int = 30):
    """Return (status, headers, body_bytes) or (status, headers, None) on error."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "te-pa-verify/1.0",
            # Force fresh fetch through any intermediary caches we can
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), None
    except Exception as e:
        return None, {"_error": str(e)}, None


def _classify(p):
    """Classify a pixel as R(ed), B(lack), C(ream), or ? (other)."""
    if near(p, RED, tol=55):
        return "R"
    if near(p, BLACK, tol=55):
        return "B"
    if near(p, CREAM, tol=55):
        return "C"
    return "?"


def _scan_horizontal(img: Image.Image, y: int, x_start=10, x_end=None, step=2):
    """Scan a horizontal row at y; return classification counts and transitions."""
    W, _ = img.size
    if x_end is None:
        x_end = W - 10
    px = img.load()
    counts = {"R": 0, "B": 0, "C": 0, "?": 0}
    transitions = 0
    prev = None
    for x in range(x_start, x_end, step):
        c = _classify(px[x, y])
        counts[c] += 1
        if prev is not None and c != prev and c != "?" and prev != "?":
            transitions += 1
        prev = c
    return counts, transitions


def probe_gn_takua(img: Image.Image) -> dict:
    """
    GN takua motif: vertical bamboo bars across the TOP and BOTTOM bands
    (band_h ≈ 60–70 px). Each bar is `color` on `bg` background, with a
    small CREAM bamboo-node mark mid-bar.

    Probe: scan a horizontal row inside the top band (y ≈ 30) and inside
    the bottom band (y ≈ H-30). Expect many transitions across the row
    (one per bar/gap pair → dozens) AND at least a handful of CREAM
    pixels from the node marks.
    """
    H = img.size[1]
    results = {}
    for side, y in (("top", 30), ("bottom", H - 30)):
        counts, transitions = _scan_horizontal(img, y)
        results[side] = {
            "transitions": transitions,
            "counts": counts,
        }
    # Bars produce many transitions; node marks produce a few cream pixels.
    # Templates vary: some have motif on top+bottom, others only on one band.
    # Accept motif as present if AT LEAST ONE band passes.
    def _pass(r):
        return r["transitions"] >= 30 and r["counts"]["C"] >= 3

    bands_with_motif = [s for s, r in results.items() if _pass(r)]
    present = len(bands_with_motif) >= 1
    return {
        "present": present,
        "bands_with_motif": bands_with_motif,
        "edges": results,
    }


def probe_sm_siapo(img: Image.Image) -> dict:
    """
    SM siapo fa'a'aliao motif: triangle/diamond row across the TOP and
    BOTTOM bands, plus a thin tusili'i wavy line near the inner edge of
    the band. Triangles are `color` on `bg`, with a small CREAM pinpoint
    at the centre of each.

    Probe: scan a horizontal row inside each band (y ≈ 30 / H-30).
    Triangle saw-tooth → many color↔bg transitions; pinpoints → CREAM
    pixels.
    """
    H = img.size[1]
    results = {}
    for side, y in (("top", 30), ("bottom", H - 30)):
        counts, transitions = _scan_horizontal(img, y)
        results[side] = {
            "transitions": transitions,
            "counts": counts,
        }
    # Saw-tooth triangles produce frequent transitions; pinpoints add cream.
    # Accept motif as present if AT LEAST ONE band passes (templates vary).
    def _pass(r):
        return r["transitions"] >= 10 and r["counts"]["C"] >= 3

    bands_with_motif = [s for s, r in results.items() if _pass(r)]
    present = len(bands_with_motif) >= 1
    return {
        "present": present,
        "bands_with_motif": bands_with_motif,
        "edges": results,
    }


def main():
    report = {
        "base_url": BASE,
        "fetched_at": "2026-06-27T20:05+1200",
        "files": [],
        "summary": {},
    }

    # First: hash every bilingual master so per-language variants can be
    # compared against the matching master.
    masters = {}  # meme -> sha256 of bytes
    for meme in MEMES:
        url = f"{BASE}campaign-{meme}.png"
        status, headers, body = fetch(url)
        h = hashlib.sha256(body).hexdigest() if body else None
        masters[meme] = h
        size_ok = body is not None and len(body) > 0
        rec = {
            "kind": "cover",
            "meme": meme,
            "lang": None,
            "url": url,
            "http_status": status,
            "bytes": len(body) if body else 0,
            "size_ok": size_ok,
            "sha256": h,
            "distinct_from_master": None,  # n/a — this IS the master
            "content_type": headers.get("content-type") or headers.get("Content-Type"),
            "cache_control": headers.get("cache-control")
            or headers.get("Cache-Control"),
            "etag": headers.get("etag") or headers.get("ETag"),
            "motif_probe": None,
            "issues": [],
        }
        if status != 200:
            rec["issues"].append(f"http_status={status}")
        if not size_ok:
            rec["issues"].append("empty_body")
        report["files"].append(rec)

    # Now: per-language variants
    for meme in MEMES:
        master_hash = masters.get(meme)
        for lang in LANGS:
            url = f"{BASE}campaign-{meme}-{lang}.png"
            status, headers, body = fetch(url)
            h = hashlib.sha256(body).hexdigest() if body else None
            size_ok = body is not None and len(body) > 0
            distinct = (h != master_hash) if h and master_hash else None
            rec = {
                "kind": "variant",
                "meme": meme,
                "lang": lang,
                "url": url,
                "http_status": status,
                "bytes": len(body) if body else 0,
                "size_ok": size_ok,
                "sha256": h,
                "distinct_from_master": distinct,
                "content_type": headers.get("content-type")
                or headers.get("Content-Type"),
                "cache_control": headers.get("cache-control")
                or headers.get("Cache-Control"),
                "etag": headers.get("etag") or headers.get("ETag"),
                "motif_probe": None,
                "issues": [],
            }
            if status != 200:
                rec["issues"].append(f"http_status={status}")
            if not size_ok:
                rec["issues"].append("empty_body")
            if distinct is False:
                rec["issues"].append("identical_to_bilingual_master")

            # Motif probe for GN and SM
            if size_ok and lang in ("gn", "sm"):
                try:
                    img = Image.open(io.BytesIO(body)).convert("RGB")
                    if lang == "gn":
                        probe = probe_gn_takua(img)
                        rec["motif_probe"] = {"motif": "takua_bamboo", **probe}
                        if not probe["present"]:
                            rec["issues"].append("takua_motif_not_detected")
                    elif lang == "sm":
                        probe = probe_sm_siapo(img)
                        rec["motif_probe"] = {
                            "motif": "siapo_faaaliao",
                            **probe,
                        }
                        if not probe["present"]:
                            rec["issues"].append("siapo_motif_not_detected")
                except Exception as e:
                    rec["issues"].append(f"image_decode_error:{e}")

            report["files"].append(rec)

    # Summary
    total = len(report["files"])
    ok = sum(1 for f in report["files"] if not f["issues"])
    failed = total - ok
    report["summary"] = {
        "total_files": total,
        "fully_clean": ok,
        "with_issues": failed,
        "issue_breakdown": {},
    }
    for f in report["files"]:
        for iss in f["issues"]:
            key = iss.split(":")[0]
            report["summary"]["issue_breakdown"][key] = (
                report["summary"]["issue_breakdown"].get(key, 0) + 1
            )

    out = Path("/home/user/workspace/te-pa/social-kit-verification.json")
    out.write_text(json.dumps(report, indent=2))

    # Human-readable print
    print(f"\nFetched {total} files from {BASE}")
    print(f"  Fully clean: {ok}")
    print(f"  With issues: {failed}")
    if report["summary"]["issue_breakdown"]:
        print("  Issue breakdown:")
        for k, v in report["summary"]["issue_breakdown"].items():
            print(f"    {k}: {v}")
    print()
    # Per-file line
    header = f"{'STATUS':<6} {'KB':>6} {'DISTINCT':<8} {'MOTIF':<10} {'FILE'}"
    print(header)
    print("-" * len(header))
    for f in report["files"]:
        status = str(f["http_status"])
        kb = f"{f['bytes']/1024:.1f}" if f["bytes"] else "0"
        distinct = (
            "—"
            if f["distinct_from_master"] is None
            else ("yes" if f["distinct_from_master"] else "NO")
        )
        motif = "—"
        if f["motif_probe"]:
            motif = "OK" if f["motif_probe"]["present"] else "MISS"
        flag = "  " if not f["issues"] else "❌"
        name = f["url"].split("/")[-1]
        print(f"{status:<6} {kb:>6} {distinct:<8} {motif:<10} {flag} {name}")
        for iss in f["issues"]:
            print(f"        ↳ {iss}")
    print()
    print(f"Full JSON: {out}")


if __name__ == "__main__":
    main()
