# Te Pā Tūwatawata — Partner Onboarding Docs

> Indigenous Data Sovereignty · AI Education · Motif Access API  
> CC BY-NC-SA 4.0 — [te-pa.org](https://te-pa.org)

---

## Available Languages

| Language | Code | Region | Markdown | PDF |
|---|---|---|---|---|
| English | `en` | Global / Pacific | [te-pa-partner-onboarding-en.md](te-pa-partner-onboarding-en.md) | [PDF](https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/partner-onboarding/te-pa-partner-onboarding-en.pdf) |
| Te Reo Māori | `mi` | Aotearoa New Zealand | [te-pa-partner-onboarding-mi.md](te-pa-partner-onboarding-mi.md) | [PDF](https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/partner-onboarding/te-pa-partner-onboarding-mi.pdf) |
| Português | `pt` | Brasil / América do Sul | [te-pa-partner-onboarding-pt.md](te-pa-partner-onboarding-pt.md) | [PDF](https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/partner-onboarding/te-pa-partner-onboarding-pt.pdf) |
| Avañe'ẽ | `gn` | Paraguay / Brasil / Argentina | [te-pa-partner-onboarding-gn.md](te-pa-partner-onboarding-gn.md) | [PDF](https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/partner-onboarding/te-pa-partner-onboarding-gn.pdf) |
| Gagana Samoa | `sm` | Oceania / Pasefika | [te-pa-partner-onboarding-sm.md](te-pa-partner-onboarding-sm.md) | [PDF](https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/partner-onboarding/te-pa-partner-onboarding-sm.pdf) |
| العربية ← | `ar` | الشرق الأوسط وشمال أفريقيا / عالمي | [te-pa-partner-onboarding-ar.md](te-pa-partner-onboarding-ar.md) | [PDF](https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/partner-onboarding/te-pa-partner-onboarding-ar.pdf) |

---

## Quick API Reference

Base URL: `https://te-pa-analytics.sketchschool.workers.dev`

| Resource | Endpoint | Query Params |
|---|---|---|
| All motifs | `https://te-pa-analytics.sketchschool.workers.dev/api/motifs` | `?lang={code}&culture={name}` |
| Single motif | `https://te-pa-analytics.sketchschool.workers.dev/api/motifs/:id` | `/api/motifs/koru?lang=pt` |
| Cultures | `https://te-pa-analytics.sketchschool.workers.dev/api/cultures` | — |
| Meme image | `https://te-pa-analytics.sketchschool.workers.dev/api/meme` | `?id=koru&lang=sm` |
| Teaching kit | `https://te-pa-analytics.sketchschool.workers.dev/api/kit` | `?lang=ar` |

Rate limit: **100 requests/hour per IP** — no key required.  
Courtesy header: `X-TePa-Use: <your-project-name>`

---

## Adding a New Language

1. Add a new language block to `partner-onboarding/_template.json`
2. Add the matching `meaning_{code}` field to every motif in `data/motif-bank-master.json`
3. Run `node scripts/generate-partner-docs.js` — all onboarding docs regenerate automatically
4. Run `node scripts/add-language.js --lang={code}` to generate memes + teaching kit assets

This index is regenerated every time the script runs.

---

## Attribution

All Te Pā motifs, images, and teaching materials are published under  
**CC BY-NC-SA 4.0** — free to use and adapt with attribution:

> Te Pā Tūwatawata (te-pa.org) — CC BY-NC-SA 4.0

---

*Generated automatically by `scripts/generate-partner-docs.js`*  
*Te Pā Tūwatawata Charitable Trust — 2 Mount Street, Port Chalmers, Dunedin 9023, Aotearoa New Zealand*
