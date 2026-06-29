# Self-Host & Fork — A Walkthrough for Indigenous Communities

> *"Build your own pā. We will show you how the walls go up."*

This guide is for **any Indigenous community** that wants their own version of
[te-pa.org](https://te-pa.org) — a site that teaches your motifs, hosts your meanings,
runs in your language, and is **owned by you, not by us**.

The whole te-pa codebase is permissively licensed (CC BY-NC-SA 4.0). You can fork it,
re-skin it, and host it on any platform with zero ongoing cost for a small site.

---

## Three ways to fork

| Path | Best for | Cost | Time |
|---|---|---|---|
| **1. One-command starter** (this guide) | Communities ready to ship now | $0 | 30 min |
| **2. GitHub template** | Devs comfortable with git workflows | $0 | 1 hour |
| **3. Embed-only**: just consume our API | A page on an existing site | $0 | 10 min |

---

## Path 1 — One-command starter

Run the bundler to get a `your-community-pa.zip` containing a complete, ready-to-deploy
starter site pre-filled with your culture's motifs from the canonical motif bank.

### Prerequisites

- macOS, Linux, or WSL with bash + `zip` + `python3` (all standard)
- A free [Cloudflare account](https://dash.cloudflare.com/sign-up) (for Pages/Workers)
  **or** [Vercel](https://vercel.com/signup) **or** [Netlify](https://app.netlify.com/signup)
- A domain name (optional — every host gives you a free `.pages.dev` / `.vercel.app` URL)

### Step 1 — Generate the starter

```bash
git clone https://github.com/robertmccallnz/kiwi-dialectic-te-pa-minisite.git te-pa-source
cd te-pa-source
./scripts/make-fork-kit.sh --culture samoan --name "Le Va Tapuia" --domain le-va.org
```

Available `--culture` values: `maori`, `samoan`, `pacific`, `tongan`, `fijian`,
`guarani`, `shipibo`, `guna`, `kayapo`, `yanomami`, `amazonian`. The script also
accepts `--culture mixed` if your community draws from several traditions.

You'll get `./out/le-va-tapuia-pa.zip` containing:

```
le-va-tapuia-pa/
├── README.md              # walkthrough customised for your community
├── index.html             # homepage with your name + colours baked in
├── motifs/                # only your culture's motif explainer pages
├── locales/               # only the languages you opted into
├── assets/
│   ├── css/               # Hotere v0.3 retuned to your palette
│   └── motifs/            # only your culture's SVGs
├── data/
│   ├── motif-bank.json    # filtered to your culture (editable!)
│   └── community.json     # your name, domain, kaitiaki contact
├── worker/                # optional Cloudflare Worker (analytics + API)
├── .github/workflows/     # deploy-on-push to Cloudflare Pages / Vercel
└── DEPLOY.md              # 10-step host-specific deployment guide
```

### Step 2 — Customise

Open the unzipped folder. The three files you'll want to edit first:

1. **`data/community.json`** — your community name, kaitiaki / governance, contact
2. **`data/motif-bank.json`** — add your own motifs, edit meanings, add language translations
3. **`assets/css/motif-tokens.css`** — your dominant palette (the script seeded this)

Everything else cascades from those three files. The homepage, the colour stripes,
the social cards, and the meta tags all read from them.

### Step 3 — Deploy

`DEPLOY.md` in your zip has step-by-step instructions for **Cloudflare Pages**, **Vercel**,
and **Netlify**. The short version for Cloudflare:

```bash
cd le-va-tapuia-pa
git init && git add . && git commit -m "init"
# Create empty repo on GitHub, then:
git remote add origin git@github.com:YOUR-ORG/le-va-tapuia-pa.git
git push -u origin main
```

Then on Cloudflare Pages: **Create project → Connect repo → Deploy** (no build command,
output dir = `.`). You're live in under 2 minutes.

### Step 4 — Point your domain (optional)

In your domain registrar, add a CNAME to your Pages URL. Cloudflare/Vercel/Netlify
issue an SSL cert automatically.

### Step 5 — Add your motifs

Open `data/motif-bank.json` and add entries following the
[schema documented here](data/README.md). For each new motif:

1. Add a JSON entry (id, names, colours, meanings in your languages)
2. Place SVG artwork in `assets/motifs/<your-motif-id>.svg`
3. Run `python3 scripts/build-motif-manifest.py` to refresh the manifest
4. Optionally write an explainer page at `motifs/<your-motif-id>.html` (copy any te-pa
   motif page as a template)

Commit + push — your site rebuilds automatically.

---

## Path 2 — GitHub template (advanced)

If you want full git history + ability to pull upstream improvements:

1. Visit [te-pa repo](https://github.com/robertmccallnz/kiwi-dialectic-te-pa-minisite) →
   **Use this template** → **Create a new repository**
2. Clone your new repo locally
3. Run `./scripts/make-fork-kit.sh --in-place --culture <your-culture> --name <your-name>`
4. Commit and push

This preserves git history so you can later `git remote add upstream …` and
`git fetch upstream && git merge upstream/main` to pull in improvements to the engine.

---

## Path 3 — Embed-only

You don't need to host anything. Add this snippet to any existing webpage:

```html
<div id="motif-strip" data-culture="samoan" data-lang="sm"></div>
<link rel="stylesheet"
      href="https://te-pa.org/assets/css/motif-tokens.css"/>
<script type="module">
const el = document.getElementById('motif-strip');
const { culture, lang } = el.dataset;
const r = await fetch(`https://te-pa-analytics.sketchschool.workers.dev/api/motifs?culture=${culture}&lang=${lang}`);
const { motifs, attribution } = await r.json();
el.innerHTML = motifs.map(m => `
  <figure class="motif-card" style="--motif-primary:${m.colour_primary}">
    <img src="${m.svg_url}" alt="${m.name_en}" width="80" height="80" loading="lazy"/>
    <figcaption><strong>${m.name_indigenous}</strong> — ${m.meaning}</figcaption>
  </figure>
`).join('') + `<small>${attribution} · CC BY-NC-SA 4.0</small>`;
</script>
```

Done. The strip is fully styled, multilingual, and culturally attributed.

---

## What you should and shouldn't change

### ✅ Encouraged

- Your community's name, domain, kaitiaki info
- Your motifs, their meanings, their colours
- Your languages, translations, locale files
- Your social-kit text, your campaigns
- The visual design — colours, typography, layout

### ⚠️ Please don't

- Strip the CC BY-NC-SA 4.0 attribution from the footer (it's required by the licence)
- Remove the "data sovereignty" framing if you keep the kaitiaki page — that framing
  is a deliberate political commitment, not decoration
- Use this template for commercial / for-profit purposes without renegotiating the
  licence with the original maintainers

### 🚫 Please definitely don't

- Use cultural motifs from cultures other than your own without explicit kaitiaki
  permission — the `--culture` filter is there to make this default-safe

---

## Getting help

- **Technical**: open an issue at the [te-pa repo](https://github.com/robertmccallnz/kiwi-dialectic-te-pa-minisite/issues)
- **Cultural / governance**: contact via the kaitiaki page on te-pa.org
- **Translation**: see [`docs/i18n-audit.md`](docs/i18n-audit.md) for the current
  translation gaps — contributions in any language are welcome

---

## Why this exists

Every Indigenous community deserves a digital pā: a fortified, beautiful, multilingual
home for their motifs, meanings, and movements — that they own, that doesn't rent-seek
their data, that doesn't depend on a Silicon Valley company staying in business.

We built one. Here's the blueprint. **Build yours.**

— *The Kiwi Dialectic · Te Pā Tūwatawata*
