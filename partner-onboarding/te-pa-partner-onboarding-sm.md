# Te Pā Tūwatawata — Fa'amatalaga mo Paaga fou

> **Pule Fa'apitoa i Faamaumauga Tuto'atasi · A'oa'oga AI · Fa'aogaina o le API Motif**

---

Afio mai i le fesoasoani a Te Pā Tūwatawata. O lenei fa'amatalaga e tu'uina atu ai mea uma e te mana'omia e fa'aogaina ai la matou faletusi o motif, seti a'oa'oga, ma le API fa'alaua'itele — ma fa'afesoota'i i lou lava platformi, fa'asalalauga, po'o polokalame a'oa'oga.

---

## O ai Te Pā Tūwatawata

O Te Pā Tūwatawata o se Fa'alapotopotoga Alofa e nofo i Port Chalmers, Aotearoa Niu Sila. Matou te fausia atiina'e a'oa'oga tatala mo pule fa'apitoa i faamaumauga tuto'atasi, iloa AI, ma faiga o malamalama fa'a-decolonial — e aʻafia ai tu ma aga o Māori, Samoa, Pasifika, Guaraní, Shipibo, Guna, Kayapó, Yanomami, Fijiano, Tonga, ma Amazonian.

---

## O le a Maua e Paaga

- Fa'aogaina o motif faaleaganuu 30 — ata PNG, faila vector SVG, ma ata meme fa'aalia
- Seti a'oa'oga i gagana e 6 (Igilisi, Te Reo Māori, Português, Avañe'ẽ, Gagana Samoa, Arapi)
- API fa'alaua'itele faitau-na'o — talosaga 100 fua ia itula, e le mana'omia se ki
- Seti fa'asalalauga fa'aagafesootai — SVG 624 mo Facebook, Instagram, TikTok, X
- PNG meme fa'a-gagana mo motif uma 30 × gagana 6
- Laisene CC BY-NC-SA 4.0 — saoloto e fa'aoga ma fa'aleleia ma fa'amaonia

---

## Le API Fa'alaua'itele

O la matou API faitau-na'o e le mana'omia se fa'amaonia. O endpoint uma e toe fo'i JSON ma fa'amaonia atoatoa i totonu.

**URL Autu:** `https://te-pa-analytics.sketchschool.workers.dev`

| Endpoint | Fa'amatala | Example |
|---|---|---|
| `GET /api/motifs` | Motif uma 30 ma uiga, URL CDN, ma feso'ota'iga meme | `https://te-pa-analytics.sketchschool.workers.dev/api/motifs?culture=samoan&lang=sm` |
| `GET /api/motifs/:id` | Motif tasi e ala i le ID — lisi atoatoa o kolekita | `https://te-pa-analytics.sketchschool.workers.dev/api/motifs/niho_mano` |
| `GET /api/cultures` | Lisi aganuu uma 11 ma fuainumera o motif | `https://te-pa-analytics.sketchschool.workers.dev/api/cultures` |
| `GET /api/meme` | URL CDN mo le PNG meme fa'a-gagana | `https://te-pa-analytics.sketchschool.workers.dev/api/meme?id=niho_mano&lang=sm` |
| `GET /api/kit` | URL PDF o seti a'oa'oga mo se gagana | `https://te-pa-analytics.sketchschool.workers.dev/api/kit?lang=sm` |

> Fa'amolemole fa'aopoopo le ulutala X-TePa-Use: <igoa o lau poloketi> i au talosaga. E fesoasoani tele lenei ia matou malamalama pe fa'afefea ona fa'aogaina le API ma lagolagoina talosaga mo tupe.

### Tumau o Talosaga

Talosaga 100 ia itula ia IP. Afai e te mana'omia fa'atupuina mo se poloketi fa'apitoa, fa'afesoota'i mai ia i matou i te-pa.org.

---

## Soo'ia Kolekita

Kolekita uma e tu'uina atu mai le CDN Cloudflare R2 a matou:

| Type | URL Pattern |
|---|---|
| Ata PNG motif | `https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/motifs/{aganuu}/{id}.png` |
| Vector SVG motif | `https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/motifs/{aganuu}/{id}.svg` |
| Meme fa'a-gagana | `https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/motifs/memes/meme_{id}_{gagana}.png` |
| PDF seti a'oa'oga | `https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/teaching-kits/te-pa-teaching-kit-{gagana}.pdf` |

---

## Fa'amaonia ma Laisene

Motif uma, ata, ma mea a'oa'oga a Te Pā e fa'asalalauina i lalo o CC BY-NC-SA 4.0. E mafai ona e fa'asoa ma fa'aleleia mo fa'aoga e le fa'apisinisi, ae tu'uina atu le fa'amaonia fa'apea:

> **Te Pā Tūwatawata (te-pa.org) — CC BY-NC-SA 4.0**

Mo fa'aoga fa'apisinisi e mana'omia se maliega eseese. Fa'afesoota'i mai ia i matou.

---

## Fa'afesoota'iga i Fa'asalalauga Fa'aagafesootai

O motif ta'itasi e iai seti fa'aagafesootai atoatoa ma kata fa'aaogaina mo platformi ta'itasi. Hashtag fautuaina mo au fa'asalalauga:

```
#TaofiFaaSamoa  #GaganaOLomuamua  #TePa  #DataSovereignty  #Oceania
```

A e fa'asoa ai, fa'ailoa @KiwiDialectic ma fa'aopoopo le feso'ota'iga i te-pa.org/rhizome-mapper.html ina ia mafai e lau au ona su'esu'e le fesoasoani atoatoa.

---

## Amata Vave — Fa'ata'ita'iga Koti

```javascript
// Maua motif Samoa uma i le Gagana Samoa
fetch('https://te-pa-analytics.sketchschool.workers.dev/api/motifs?culture=samoan&lang=sm', {
  headers: { 'X-TePa-Use': 'IgoaPoloketi' }
})
.then(r => r.json())
.then(faamaumauga => {
  faamaumauga.motifs.forEach(m => {
    console.log(m.name_en, m.assets.meme_png);
  });
});
```

---

## Fa'afesoota'i Mai

Te Pā Tūwatawata
2 Mount Street, Port Chalmers, Dunedin 9023, Aotearoa Niu Sila

- [Upega Tafaʻilagi](https://te-pa.org)
- [Fa'amaufa'ailoga Rizome](https://te-pa.org/rhizome-mapper.html)
- [GitHub](https://github.com/robertmccallnz/kiwi-dialectic-te-pa-minisite)
- [Fa'amatalaga API](https://te-pa-analytics.sketchschool.workers.dev/api)

---

*Fa'alapotopotoga Alofa Te Pā Tūwatawata — te-pa.org — CC BY-NC-SA 4.0 — Gaosia otometi*
