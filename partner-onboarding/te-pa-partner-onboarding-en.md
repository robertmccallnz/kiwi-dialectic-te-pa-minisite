# Te Pā Tūwatawata — Partner Onboarding Guide

> **Indigenous Data Sovereignty · AI Education · Motif Access API**

---

Welcome to the Te Pā Tūwatawata partner network. This guide gives you everything you need to access our motif library, teaching kits, and public API — and integrate them into your own platforms, publications, or educational programmes.

---

## About Te Pā Tūwatawata

Te Pā Tūwatawata is an open educational kaupapa published from Ōtepoti Dunedin (Port Chalmers), Aotearoa New Zealand. A charitable trust is being established — expressions of interest open for founding board / kaitiaki seats. We build open educational infrastructure for indigenous data sovereignty, AI literacy, and decolonial knowledge systems — rooted in the cultural motif traditions of Māori, Samoan, Pacific, Guaraní, Shipibo, Guna, Kayapó, Yanomami, Fijian, Tongan, and Amazonian peoples.

---

## What Partners Get

- Access to 30 indigenous cultural motifs — PNG artwork, SVG vector files, and activist meme images
- Teaching kits in 6 languages (English, Te Reo Māori, Português, Avañe'ẽ, Gagana Samoa, Arabic)
- Read-only public API — 100 free requests/hour, no key required
- Social media kit — 624 platform-optimised SVG cards across Facebook, Instagram, TikTok, X
- Language-specific meme PNGs for all 30 motifs × 6 languages
- CC BY-NC-SA 4.0 licence — free to use and adapt with attribution

---

## Public API

Our read-only API requires no authentication. All endpoints return JSON with full attribution built in.

**Base URL:** `https://te-pa-analytics.sketchschool.workers.dev`

| Endpoint | Description | Example |
|---|---|---|
| `GET /api/motifs` | All 30 motifs with meanings, CDN image URLs, and meme links | `https://te-pa-analytics.sketchschool.workers.dev/api/motifs?culture=maori&lang=en` |
| `GET /api/motifs/:id` | Single motif by ID — full asset listing | `https://te-pa-analytics.sketchschool.workers.dev/api/motifs/koru` |
| `GET /api/cultures` | List all 11 cultures with motif counts | `https://te-pa-analytics.sketchschool.workers.dev/api/cultures` |
| `GET /api/meme` | CDN URL for a language-specific meme PNG | `https://te-pa-analytics.sketchschool.workers.dev/api/meme?id=koru&lang=en` |
| `GET /api/kit` | Teaching kit PDF CDN URL for a given language | `https://te-pa-analytics.sketchschool.workers.dev/api/kit?lang=en` |

> Please include the header X-TePa-Use: <your project name> in your requests. This helps us understand how the API is used and supports future funding applications.

### Rate Limits

100 requests per hour per IP address. If you need higher limits for a specific project, contact us at te-pa.org.

---

## Downloading Assets

All assets are served from our Cloudflare R2 CDN:

| Type | URL Pattern |
|---|---|
| Motif PNG artwork | `https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/motifs/{culture}/{id}.png` |
| Motif SVG vector | `https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/motifs/{culture}/{id}.svg` |
| Activist meme (language) | `https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/motifs/memes/meme_{id}_{lang}.png` |
| Teaching kit PDF | `https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/teaching-kits/te-pa-teaching-kit-{lang}.pdf` |

---

## Attribution & Licence

All Te Pā motifs, images, and teaching materials are published under CC BY-NC-SA 4.0. You are free to share and adapt for non-commercial use, provided you give credit as follows:

> **Te Pā Tūwatawata (te-pa.org) — CC BY-NC-SA 4.0**

Commercial use requires a separate agreement. Contact us to discuss partnership arrangements.

---

## Social Media Integration

Each motif has a full social kit with platform-optimised cards. Recommended hashtags for your posts:

```
#DataSovereignty  #IndigenousAI  #TePa  #CARE  #AIRights
```

When posting, tag @KiwiDialectic and link back to te-pa.org/rhizome-mapper.html so your audience can explore the full network.

---

## Quick Start — Code Example

```javascript
// Fetch all Māori motifs in English
fetch('https://te-pa-analytics.sketchschool.workers.dev/api/motifs?culture=maori&lang=en', {
  headers: { 'X-TePa-Use': 'YourProjectName' }
})
.then(r => r.json())
.then(data => {
  data.motifs.forEach(m => {
    console.log(m.name_en, m.assets.meme_png);
  });
});
```

---

## Contact & Community

Te Pā Tūwatawata
2 Mount Street, Port Chalmers, Dunedin 9023, Aotearoa New Zealand

- [Website](https://te-pa.org)
- [Rhizome Mapper](https://te-pa.org/rhizome-mapper.html)
- [GitHub](https://github.com/robertmccallnz/kiwi-dialectic-te-pa-minisite)
- [API Docs](https://te-pa-analytics.sketchschool.workers.dev/api)

---

*Te Pā Tūwatawata — te-pa.org — CC BY-NC-SA 4.0 — Generated automatically*
