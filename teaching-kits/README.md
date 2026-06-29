# Te Pā Teaching Kit Repository

> **AI Data Sovereignty Education for Indigenous Communities**
> Aotearoa New Zealand · Oceania · South America

---

## What Is This?

This repository contains structured teaching materials for the Te Pā platform — a multilingual, community-led curriculum teaching **AI data sovereignty** through Indigenous motifs, storytelling, and the CARE Principles (Collective Benefit, Authority, Responsibility, Ethics).

Each language folder contains a `kit-manifest.json` linking:
- The pedagogical PDF teaching kit
- All relevant motif assets (PNG files via R2 CDN)
- Meme graphics for social media sharing
- Module titles in the local language
- Hashtags for amplification in that language community

---

## Folder Structure

```
teaching-kits/
├── manifest.json              ← Master manifest (all languages)
├── README.md                  ← This file
├── EDUCATOR-GUIDE.md          ← Classroom adaptation guide
├── en/
│   └── kit-manifest.json      ← English — 30 motifs, 6 modules
├── mi/
│   └── kit-manifest.json      ← Te Reo Māori — 9 motifs, 6 modules
├── pt/
│   └── kit-manifest.json      ← Português — 10 motifs, 6 modules
├── gn/
│   └── kit-manifest.json      ← Avañe'ẽ (Guaraní) — 4 motifs, 6 modules
└── sm/
    └── kit-manifest.json      ← Gagana Samoa — 11 motifs, 6 modules
```

---

## Languages Supported

| Code | Language | Region | Motifs | Kit PDF |
|------|----------|--------|--------|---------|
| `en` | English | Global / Pacific | 30 | [Download](https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/teaching-kits/te-pa-teaching-kit-en.pdf) |
| `mi` | Te Reo Māori | Aotearoa New Zealand | 9 | [Download](https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/teaching-kits/te-pa-teaching-kit-mi.pdf) |
| `pt` | Português | Brazil / South America | 10 | [Download](https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/teaching-kits/te-pa-teaching-kit-pt.pdf) |
| `gn` | Avañe'ẽ (Guaraní) | Paraguay / Brazil / Argentina | 4 | [Download](https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/teaching-kits/te-pa-teaching-kit-gn.pdf) |
| `sm` | Gagana Samoa | Oceania / Pacific | 11 | [Download](https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/teaching-kits/te-pa-teaching-kit-sm.pdf) |

---

## How to Use the Kit Manifests

Each `kit-manifest.json` is a machine-readable file you can load in your own application or website to automatically serve the correct assets for a user's language.

**Example: fetching the Guaraní kit manifest**

```js
const lang = 'gn'; // from user language selection
const manifest = await fetch(
  `https://te-pa.org/teaching-kits/${lang}/kit-manifest.json`
).then(r => r.json());

// Teaching kit PDF
console.log(manifest.assets.teaching_kit_pdf);

// Motifs with meanings in Guaraní
manifest.motifs.forEach(m => console.log(m.id, m.meaning));

// Meme graphics ready to share
manifest.social_graphics.forEach(g => console.log(g.meme_url, g.caption));

// Hashtags to include in posts
console.log(manifest.hashtags.join(' '));
```

---

## Motif Cultures

| Culture | Language Focus | Motif Count |
|---------|----------------|-------------|
| Māori | mi, en | 9 |
| Samoan | sm, en | 7 |
| Pacific (general) | sm, en | 1 |
| Tongan | sm, en | 1 |
| Fijian | sm, en | 2 |
| Guaraní | gn, pt, en | 4 |
| Shipibo | pt, en | 2 |
| Guna | pt, en | 1 |
| Kayapó | pt, en | 1 |
| Yanomami | pt, en | 1 |
| Amazonian | pt, en | 1 |

---

## Adding a New Language

1. Create `teaching-kits/{lang_code}/kit-manifest.json` following the schema in any existing manifest
2. Add `meaning_{lang_code}` fields to `data/motif-bank-master.json` for each motif
3. Add title translations to `data/motif-course-map.json` for each module
4. Add the language button to `rhizome-mapper.html` language selector
5. Update `teaching-kits/manifest.json` master languages block
6. Build the teaching kit PDF using `build_teaching_kits.py`
7. Upload the PDF to R2: `teaching-kits/te-pa-teaching-kit-{lang}.pdf`

---

## CARE Principles

All materials in this repository are built around the **CARE Principles for Indigenous Data Governance**:

- **C** — Collective Benefit: Data ecosystems must enable Indigenous peoples to benefit from their data
- **A** — Authority to Control: Indigenous peoples' rights and interests in their data must be recognised
- **R** — Responsibility: Those working with Indigenous data have a responsibility to share how data is used
- **E** — Ethics: Indigenous peoples' rights and wellbeing must be the primary concern in all data decisions

Learn more at [Global Indigenous Data Alliance](https://www.gida-global.org/care)

---

## Live Platform

- **Site:** [te-pa.org](https://te-pa.org)
- **Rhizome Mapper:** [/rhizome-mapper.html](https://te-pa.org/rhizome-mapper.html)
- **Analytics API:** [te-pa-analytics.sketchschool.workers.dev](https://te-pa-analytics.sketchschool.workers.dev/stats)

---

*Maintained by Te Pā Tūwatawata · 2 Mount Street, Port Chalmers, Dunedin 9023, Aotearoa New Zealand*

---

## Translations

### Te Reo Māori — Mō tēnei kohinga

Ko tēnei kohinga he kaupeka akoranga mō te mana motuhake raraunga AI, i hangaia mō ngā hapori Māori, o Te Moananui-a-Kiwa me Amerika ki te Tonga. Ko ia motif he tohu o te mātauranga tūāhuatanga, e hono ana ki ia akoranga, ki ia reo anō. Tikiakehia ngā kete akoranga mā ia reo, tukuna ngā ātea pāpori mā ngā tūmau e hono ana ki ō hapori.

### Português — Sobre este repositório

Este repositório contém materiais pedagógicos para o ensino de **soberania de dados indígena com IA**, desenvolvidos para comunidades indígenas do Brasil, do Pacífico e da América do Sul. Cada pasta de idioma contém os ativos digitais vinculados ao currículo de seis módulos baseado nos Princípios CARE. Baixe os kits de ensino em PDF e use os motivos e memes para compartilhar nas redes sociais com as hashtags específicas de cada idioma.

### Avañe'ẽ — Ko'ã tembiapo rehegua

Ko tembiapo ome'ẽ mbo'esyry guarã **ñane rekove porã tembiasakuépe AI ndive**, oñemboguapyva'erã Guaraní, Samoan ha Māori retãme. Peteĩ peteĩ ñe'ẽme oĩ kit ñombyhy, kuarahy ra'ãnga, ha meme osẽva'erã tenda pĩhombre rupi. Emoñepyrũ ne aranduhare koty ndive ha eikundaha tembiapo ñe'ẽnguéra mbo'ekuaa ape guive.

### Gagana Samoa — Mo lenei faletusi

O lenei faletusi o lo'o i ai mea fa'aa'oa'oina mo le a'oa'oina o le **pule fa'asinomaga o fa'amaumauga AI**, ua fausia mo nu'u Samoa, Pasefika, ma Amerika i Saute. O fa'ailoga motif uma o lo'o fesooti ma le a'oa'oga e fa-vasega-lua-mataupu, e tusa ai ma Mataupu CARE. Sii le PDF kit a'oa'oina ma faasoa ata motif i faasalalauga fa'aagafesootai i le hashtag o le gagana.
