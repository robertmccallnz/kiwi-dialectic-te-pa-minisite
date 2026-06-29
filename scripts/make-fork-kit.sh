#!/usr/bin/env bash
# make-fork-kit.sh — Bundle a starter site for an Indigenous community to self-host.
#
# Usage:
#   ./scripts/make-fork-kit.sh --culture <slug> --name "Community Name" [--domain <example.org>]
#   ./scripts/make-fork-kit.sh --culture maori --name "Te Pā Tūwatawata" --domain te-pa.org
#   ./scripts/make-fork-kit.sh --in-place --culture samoan --name "Le Va Tapuia"
#
# Flags:
#   --culture <slug>   Required. One of: maori, samoan, pacific, tongan, fijian,
#                      guarani, shipibo, guna, kayapo, yanomami, amazonian, mixed
#   --name "Name"      Required. Display name for the new community site.
#   --domain <domain>  Optional. The site will use this for canonical URLs.
#   --in-place         Optional. Modify the current checkout instead of writing
#                      a separate ./out/<slug>-pa.zip.
#   --languages <list> Optional comma-separated locale codes to keep
#                      (default: en,mi,sm,pt,gn,ar — all of them).
#
# Output:  ./out/<community-slug>-pa.zip   (unless --in-place)

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CULTURE=""
NAME=""
DOMAIN=""
IN_PLACE=0
LANGUAGES="en,mi,sm,pt,gn,ar"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --culture) CULTURE="$2"; shift 2 ;;
    --name) NAME="$2"; shift 2 ;;
    --domain) DOMAIN="$2"; shift 2 ;;
    --in-place) IN_PLACE=1; shift ;;
    --languages) LANGUAGES="$2"; shift 2 ;;
    -h|--help)
      sed -n '2,25p' "$0"; exit 0 ;;
    *) echo "Unknown flag: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$CULTURE" || -z "$NAME" ]]; then
  echo "ERROR: --culture and --name are required." >&2
  echo "Try: $0 --help" >&2
  exit 1
fi

VALID_CULTURES="maori samoan pacific tongan fijian guarani shipibo guna kayapo yanomami amazonian mixed"
if ! echo "$VALID_CULTURES" | tr ' ' '\n' | grep -qx "$CULTURE"; then
  echo "ERROR: --culture must be one of: $VALID_CULTURES" >&2
  exit 1
fi

# Derive slug from name (lowercase, hyphenate)
SLUG="$(echo "$NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]\+/-/g' | sed 's/^-\|-$//g')"
[[ -z "$SLUG" ]] && SLUG="community-pa"

echo "→ Building fork kit"
echo "  culture:   $CULTURE"
echo "  name:      $NAME"
echo "  slug:      $SLUG"
echo "  domain:    ${DOMAIN:-<none, will use *.pages.dev>}"
echo "  languages: $LANGUAGES"
echo "  in-place:  $IN_PLACE"

if [[ $IN_PLACE -eq 1 ]]; then
  WORK="$ROOT"
else
  WORK="$ROOT/out/${SLUG}-pa"
  rm -rf "$WORK"
  mkdir -p "$WORK"
  echo "→ Copying source tree to $WORK"
  # Copy everything except git, node_modules, out, and the source's own .github CI
  rsync -a \
    --exclude '.git/' \
    --exclude 'node_modules/' \
    --exclude 'out/' \
    --exclude '.next/' \
    --exclude '.vercel/' \
    --exclude '__pycache__/' \
    --exclude 'pdfs/' \
    --exclude 'assets/social/' \
    --exclude 'assets/social-webp/' \
    --exclude 'launch-mediakit/visuals/' \
    --exclude '*.zip' \
    --exclude '*.mp4' \
    --exclude '*.mov' \
    "$ROOT/" "$WORK/"
fi

# 1. Filter motif-bank-master.json to selected culture
echo "→ Filtering motifs to culture=$CULTURE"
python3 - <<PY
import json, pathlib
work = pathlib.Path("$WORK")
src = json.load(open(work / "data" / "motif-bank-master.json"))
if "$CULTURE" == "mixed":
    motifs = src["motifs"]
else:
    motifs = [m for m in src["motifs"] if m["culture"] == "$CULTURE"]
out = {
    "version": src["version"],
    "total": len(motifs),
    "cultures": sorted(set(m["culture"] for m in motifs)),
    "motifs": motifs,
}
target = work / "data" / "motif-bank.json"
with target.open("w") as fh:
    json.dump(out, fh, indent=2, ensure_ascii=False)
print(f"  → {len(motifs)} motifs retained")
PY

# 2. Write community.json
echo "→ Writing data/community.json"
cat > "$WORK/data/community.json" <<JSON
{
  "name": "$NAME",
  "slug": "$SLUG",
  "culture": "$CULTURE",
  "domain": "${DOMAIN:-${SLUG}.pages.dev}",
  "languages": [$(echo "$LANGUAGES" | sed 's/,/","/g; s/^/"/; s/$/"/')],
  "license": "CC BY-NC-SA 4.0",
  "forked_from": "https://te-pa.org",
  "generated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
JSON

# 3. Trim locales/ to only requested languages
if [[ -d "$WORK/locales" ]]; then
  echo "→ Trimming locales to: $LANGUAGES"
  IFS=',' read -ra KEEP <<< "$LANGUAGES"
  for f in "$WORK/locales"/*.json; do
    [[ -f "$f" ]] || continue
    name="$(basename "$f" .json)"
    keep=0
    for k in "${KEEP[@]}"; do
      [[ "$name" == "$k" ]] && keep=1 && break
    done
    if [[ $keep -eq 0 ]]; then
      rm -f "$f"
    fi
  done
fi

# 4. Trim motif SVG assets to selected culture
if [[ "$CULTURE" != "mixed" && -d "$WORK/assets/motifs" ]]; then
  echo "→ Trimming motif SVGs to culture=$CULTURE"
  python3 - <<PY
import json, pathlib, os
work = pathlib.Path("$WORK")
bank = json.load(open(work / "data" / "motif-bank.json"))
keep_ids = {m["id"] for m in bank["motifs"]}
removed = 0
for svg in (work / "assets" / "motifs").glob("*.svg"):
    stem = svg.stem
    base = stem
    for suf in ("-dark-square","-dark-wide","-light-square","-light-wide","-red-square","-band"):
        if base.endswith(suf):
            base = base[:-len(suf)]; break
    if base not in keep_ids:
        svg.unlink()
        removed += 1
print(f"  → removed {removed} SVGs from other cultures")
PY
fi

# 5. Regenerate manifest + tokens from the filtered data
echo "→ Regenerating motif manifest and tokens CSS"
(cd "$WORK" && python3 scripts/build-motif-manifest.py 2>&1 | sed 's/^/  /') || true
(cd "$WORK" && python3 scripts/build-motif-tokens.py 2>&1 | sed 's/^/  /') || true

# 6. Write a DEPLOY.md tailored to the community
cat > "$WORK/DEPLOY.md" <<EOF
# Deploy ${NAME}

Your starter site is ready. Pick a host below — all three are free for small sites.

## Option A — Cloudflare Pages (recommended)

1. Push this directory to a new GitHub repo
2. Cloudflare dashboard → **Pages** → **Create project** → **Connect to Git**
3. Pick your repo, leave build command empty, set output dir to \`.\`
4. Click **Save and Deploy**
5. (Optional) Add custom domain ${DOMAIN:+(<$DOMAIN>)}: Pages → Custom domains → Set up

## Option B — Vercel

1. Push this directory to GitHub
2. [vercel.com/new](https://vercel.com/new) → Import → leave defaults → Deploy
3. (Optional) Add custom domain ${DOMAIN:+(<$DOMAIN>)}

## Option C — Netlify

1. Drag-and-drop this folder onto [app.netlify.com](https://app.netlify.com/drop)
2. (Optional) Connect a git repo for auto-deploys

## After your first deploy

- Edit \`data/community.json\` — confirm your name, kaitiaki, domain
- Edit \`data/motif-bank.json\` — add your own motifs
- Edit \`assets/css/motif-tokens.css\` — fine-tune your palette
- Run \`python3 scripts/build-motif-manifest.py\` to refresh after edits

## License

This fork is CC BY-NC-SA 4.0. You may adapt and redistribute non-commercially with
attribution to the original maintainers (Te Pā Tūwatawata) and to your own community.
EOF

# 7. Replace top-level README with a community-specific one
mv "$WORK/README.md" "$WORK/README.upstream.md" 2>/dev/null || true
cat > "$WORK/README.md" <<EOF
# ${NAME}

A digital pā for our community — built from the [Te Pā Tūwatawata](https://te-pa.org) starter kit.

- **Culture**: ${CULTURE}
- **Languages**: $(echo "$LANGUAGES" | tr ',' ' ')
- **Domain**: ${DOMAIN:-(not set)}
- **License**: CC BY-NC-SA 4.0
- **Upstream**: https://te-pa.org · https://github.com/robertmccallnz/kiwi-dialectic-te-pa-minisite

## Deploy

See [DEPLOY.md](DEPLOY.md).

## Customise

1. \`data/community.json\` — community metadata
2. \`data/motif-bank.json\` — your motifs (see [data/README.md](data/README.md) for schema)
3. \`assets/css/motif-tokens.css\` — your palette
4. \`locales/*.json\` — your language strings

## Original walkthrough

See [README.upstream.md](README.upstream.md) (the README from Te Pā Tūwatawata).
EOF

# 8. Zip if not in-place
if [[ $IN_PLACE -eq 0 ]]; then
  echo "→ Packaging zip"
  mkdir -p "$ROOT/out"
  ZIP="$ROOT/out/${SLUG}-pa.zip"
  (cd "$ROOT/out" && zip -qr "${SLUG}-pa.zip" "${SLUG}-pa")
  SIZE=$(du -h "$ZIP" | cut -f1)
  echo ""
  echo "✓ Done."
  echo "  Output: $ZIP ($SIZE)"
  echo "  Unzip + cd in, follow DEPLOY.md"
else
  echo ""
  echo "✓ Done (in-place)."
  echo "  Modified: $WORK"
fi
