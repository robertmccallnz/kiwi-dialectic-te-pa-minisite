# Motif API — Public Reference

A read-only HTTP API that any Indigenous-culture site, classroom, or research project
can consume. CORS-enabled, no auth, JSON only, attribution + license in every response.

**Base URL**

```
https://te-pa-analytics.sketchschool.workers.dev/api
```

> Worker source: [`worker/analytics-worker-v3.js`](../worker/analytics-worker-v3.js)
> · Canonical data: [`data/motif-bank-master.json`](../data/README.md)

## Index — `GET /api`

Returns a hypertext index of every endpoint with one example each.

```bash
curl https://te-pa-analytics.sketchschool.workers.dev/api
```

## Cultures — `GET /api/cultures`

Lists all cultures with motif counts and dominant palette.

```bash
curl https://te-pa-analytics.sketchschool.workers.dev/api/cultures
```

**Response**

```json
{
  "cultures": [
    {
      "culture": "maori",
      "region": "maori",
      "motif_count": 9,
      "colours": "#2ecc71,#3498db,#e74c3c,#f39c12,…"
    }
  ],
  "attribution": "Te Pā Tūwatawata — The Kiwi Dialectic",
  "license": "CC BY-NC-SA 4.0",
  "generated_at": "2026-…"
}
```

## Motifs — `GET /api/motifs`

Filter by culture, theme, region, and translation language.

| Query param | Example | Notes |
|---|---|---|
| `culture` | `maori`, `samoan`, `guarani` | one of the 11 cultures |
| `theme` | `language`, `renewal`, `protection` | matches `political_themes[]` |
| `region` | `oceania`, `amazonia` | rhizome region |
| `lang` | `en`, `mi`, `sm`, `pt`, `gn`, `ar` | which translated `meaning_*` to surface as `meaning` |
| `limit` | `10` | default 100 |

```bash
curl "https://te-pa-analytics.sketchschool.workers.dev/api/motifs?culture=maori&lang=mi"
```

**Response**

```json
{
  "motifs": [
    {
      "id": "koru",
      "name_en": "Koru",
      "name_indigenous": "Koru",
      "culture": "maori",
      "region": "maori",
      "colour_primary": "#2ecc71",
      "meaning": "…",            // selected by ?lang=
      "meanings": { "en": "…", "mi": "…", … },
      "political_themes": ["renewal", "education", …],
      "svg_url": "https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/motifs/maori/koru.svg",
      "png_url": "https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/motifs/maori/koru.png"
    }
  ],
  "count": 9,
  "filter": { "culture": "maori", "lang": "mi" },
  "attribution": "…",
  "license": "CC BY-NC-SA 4.0",
  "generated_at": "…"
}
```

## Single motif — `GET /api/motifs/{id}`

```bash
curl https://te-pa-analytics.sketchschool.workers.dev/api/motifs/koru
```

Returns the full motif object including all `meaning_*` translations, `form_geometry`,
`visual_description`, `colour_traditional`, `resistance_use`, and `sources[]`.

## Meme — `GET /api/meme`

Resolves a meme image URL for a motif + language combination.

```bash
curl "https://te-pa-analytics.sketchschool.workers.dev/api/meme?id=koru&lang=pt"
```

Returns `{ url: ".../motifs/memes/meme_koru_pt.png", motif: {…} }`.

## Teaching kit — `GET /api/kit`

Resolves a teaching-kit PDF URL for a language.

```bash
curl "https://te-pa-analytics.sketchschool.workers.dev/api/kit?lang=gn"
```

Returns `{ url: ".../teaching-kits/te-pa-teaching-kit-gn.pdf", lang: "gn" }`.

## Errors

All errors are JSON with `{ "error": "message" }` and the appropriate HTTP status:

- `400` — bad query (e.g. unknown `lang`)
- `404` — motif id not found
- `429` — rate limited (per IP, generous limits for educational use)
- `5xx` — Worker / D1 error; retry with backoff

## CORS

`Access-Control-Allow-Origin: *` on every response. Safe to call from any browser app.

## Rate limits

There is a per-IP soft cap for abuse prevention. If you are running a classroom or a
high-traffic Indigenous-language site and expect sustained traffic, please email the
maintainers via the kaitiaki page on te-pa.org and we will allowlist your origin.

## Example: consume from another site

```html
<!-- on yoursite.org -->
<div id="motif-strip"></div>
<script type="module">
const r = await fetch('https://te-pa-analytics.sketchschool.workers.dev/api/motifs?culture=maori&lang=mi');
const { motifs, attribution } = await r.json();
const html = motifs.map(m => `
  <figure style="border-left:4px solid ${m.colour_primary};padding:.5rem 1rem">
    <img src="${m.svg_url}" alt="${m.name_en}" width="80" height="80" loading="lazy"/>
    <figcaption>
      <strong>${m.name_indigenous}</strong> — ${m.meaning}
    </figcaption>
  </figure>
`).join('');
document.getElementById('motif-strip').innerHTML = html
  + `<p style="opacity:.7;font-size:.8rem">${attribution} · CC BY-NC-SA 4.0</p>`;
</script>
```

A full standalone HTML example lives at
[`../examples/motif-consumer.html`](../examples/motif-consumer.html).

## Versioning

The Worker reads `data/motif-bank-master.json` at deploy time. The `version` field in
that file is your contract — bumps follow semver:

- **patch** — translation fixes, source additions, palette tweaks
- **minor** — new motifs, new optional fields, new cultures
- **major** — schema breaks (rare; will be coordinated via the calendar repo + GitHub
  Discussions before release)

Pinning a version is supported by hitting a tagged ref directly on GitHub:

```
https://raw.githubusercontent.com/robertmccallnz/kiwi-dialectic-te-pa-minisite/v1.0/data/motif-bank-master.json
```
