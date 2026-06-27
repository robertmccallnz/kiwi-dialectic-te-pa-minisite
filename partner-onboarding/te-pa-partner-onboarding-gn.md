# Te Pā Tūwatawata — Ñorairõ Rehegua Mba'eporu

> **Soberanía Datos Ñande reko rehegua · Mbo'esyry IA rehegua · API Motivo Jeike**

---

Eguahẽ porã Te Pā Tūwatawata ñorairõ peteĩ aty-pe. Ko mba'eporu oñeme'ẽva ndéve mba'e oñeikotevẽva oñemoarandu haguã ñande motivo raity, mbo'e jehayhu, ha API tūmatanui — ha oñemongu'e haguã nde atypy, moñe'ẽrã, térã mbo'epyrã-pe.

---

## Mba'épa Te Pā Tūwatawata

Te Pā Tūwatawata he'i peteĩ Tōpūtanga Aroha oikóva Port Chalmers-pe, Aotearoa Nueva Zelanda. Ojapo mba'eporu mbo'e hepyme'ẽva soberanía datos ñande reko rehegua, alfabetización AI rehegua, ha teko arandu ko'ã rehegua — oñemopyenda umi arandupykuéra Māori, Samoa, Pasifiko, Guaraní, Shipibo, Guna, Kayapó, Yanomami, Fijiano, Tonga, ha Amazónico rembiporu tauirã culturalpegua.

---

## Mba'e Oñeme'ẽva Ñorairõháme

- Oñeike 30 motivo cultural ñande reko rehegua — PNG ñomongeta, SVG vector, ha imagen meme kaiwhakaaro
- Mbo'e jehayhu reo 6-pe (Inglés, Te Reo Māori, Português, Avañe'ẽ, Gagana Samoa, Árabe)
- API tūmatanui ohecha añoite — tono 100 hepyme'ẽ'ỹ ia hóra, ndaha'éi ñe'ẽsã oñeikotevẽva
- Mbo'eporu papaho pāpori — SVG 624 Facebook, Instagram, TikTok, X-pe
- PNG meme reo motuhake 30 motivo × reo 6 katupyry
- Raihana CC BY-NC-SA 4.0 — hepyme'ẽ'ỹ oñeikuaa ha oñemyatyrõ oñembohovái rire

---

## API Tūmatanui

Ñande API ohecha añoite ndoikotevẽi autenticación. Pytyvõ oñemboguejy JSON oñemboyvéva ñorairõ mbohovái rehe.

**URL Yvypóra:** `https://te-pa-analytics.sketchschool.workers.dev`

| Endpoint | Mombe'u | Example |
|---|---|---|
| `GET /api/motifs` | Motivo 30 katupyry ñe'ẽ, CDN URL, ha meme hononga ndive | `https://te-pa-analytics.sketchschool.workers.dev/api/motifs?culture=guarani&lang=gn` |
| `GET /api/motifs/:id` | Motivo peteĩ ID ndive — rawa rārangi katupyry | `https://te-pa-analytics.sketchschool.workers.dev/api/motifs/yvy_mara_ey` |
| `GET /api/cultures` | Ahurea 11 katupyry tatau motivo ndive | `https://te-pa-analytics.sketchschool.workers.dev/api/cultures` |
| `GET /api/meme` | CDN URL meme PNG reo motuhake | `https://te-pa-analytics.sketchschool.workers.dev/api/meme?id=yvy_mara_ey&lang=gn` |
| `GET /api/kit` | PDF URL mbo'e jehayhu reo peteĩhápe | `https://te-pa-analytics.sketchschool.workers.dev/api/kit?lang=gn` |

> Tēnā embojoapy mātāmua X-TePa-Use: <nde mba'apo réra> ñe mboguejy-pe. Ko'ã oñemoñe'ẽva ndéve oñeikuaava mba'éichapa API ojeporúva ha oipytyvõva pĩ'a poteĩ ypykuéra.

### Límite Mboguejy

100 mboguejy ia hóra IP peteĩhápe. Emongakuaa tereho te-pa.org-pe mba'éicharõ eikotevẽ límite tuichave peteĩ mba'apo rehegua.

---

## Eñemohu'ã Rawa

Rawa katupyry oguejy CDN Cloudflare R2 ñande-gui:

| Type | URL Pattern |
|---|---|
| PNG motivo ñomongeta | `https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/motifs/{ahurea}/{id}.png` |
| SVG motivo vector | `https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/motifs/{ahurea}/{id}.svg` |
| Meme reo motuhake | `https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/motifs/memes/meme_{id}_{reo}.png` |
| PDF mbo'e jehayhu | `https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/teaching-kits/te-pa-teaching-kit-{reo}.pdf` |

---

## Mbohovái ha Raihana

Motivo, imagen, ha mbo'epyrã katupyry Te Pā oñepyrũva CC BY-NC-SA 4.0 ndive. Ikatu eike ha emyatyrõ arumoni'ỹ rehe, emoñe'ẽ porã ko'ãicha:

> **Te Pā Tūwatawata (te-pa.org) — CC BY-NC-SA 4.0**

Arumoni rehegua jeporúpegua oñeikotevẽ acuerdo peteĩ. Emoñe'ẽ ñandéve.

---

## Papaho Pāpori Ñembojoaju

Motivo peteĩháme oĩ kit social katupyry kāri oñemopyendáva plataforma peteĩhápe. Hashtag oñeporúva porã tūāhono-pe:

```
#TekoteviPorãvéva  #ÑanderuviPorã  #TePa  #Guaraní  #SoberaniadeDados
```

Embohovái rire, e'ata @KiwiDialectic ha eñe'ẽ te-pa.org/rhizome-mapper.html-pe kia āhei ai ō hunga whai i te tūhura i te whatunga katoa.

---

## Tīmatanga Tere — Tauira Waehere

```javascript
// Eñemohu'ã motivo Guaraní katupyry Avañe'ẽ-pe
fetch('https://te-pa-analytics.sketchschool.workers.dev/api/motifs?culture=guarani&lang=gn', {
  headers: { 'X-TePa-Use': 'NdeMba'apoRéra' }
})
.then(r => r.json())
.then(mba'e => {
  mba'e.motifs.forEach(m => {
    console.log(m.name_en, m.assets.meme_png);
  });
});
```

---

## Emoñe'ẽ Ñandéve

Te Pā Tūwatawata
2 Mount Street, Port Chalmers, Dunedin 9023, Aotearoa Nueva Zelanda

- [Tenda Yvypóra](https://te-pa.org)
- [Mapa Rizoma](https://te-pa.org/rhizome-mapper.html)
- [GitHub](https://github.com/robertmccallnz/kiwi-dialectic-te-pa-minisite)
- [API Mboepyrã](https://te-pa-analytics.sketchschool.workers.dev/api)

---

*Te Pā Tūwatawata Tōpūtanga Aroha — te-pa.org — CC BY-NC-SA 4.0 — Oñemoheñói aunoa*
