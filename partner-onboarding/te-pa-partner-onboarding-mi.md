# Te Pā Tūwatawata — Aratohu Mō Ngā Hoa Mahi

> **Mana Raraunga Ataura · Mātauranga AI · Āhei Tauira**

---

Nau mai ki te whatunga hoa mahi o Te Pā Tūwatawata. Ko tēnei aratohu he tūhonohono māu ki ā mātou kohinga tauira, kete ako, me te API tūmatanui — ā, ka āhei ai koe ki ēnei i roto i ō ake kaupeka, tānga, me ngā hōtaka ako.

---

## Ko Wai Te Pā Tūwatawata

He Tōpūtanga Aroha Te Pā Tūwatawata e noho ana i Te Pōhatu Tūhono, Ōtepoti, Aotearoa. Ka hanga mātou i ngā ara mātauranga tuwhera mō te mana raraunga ataura, te mōhiotanga AI, me ngā pūnaha mātauranga whakakoretia-āihe — e ūhia ana i ngā ahurea tauira o Māori, Samoa, Pasifika, Guaraní, Shipibo, Guna, Kayapó, Yanomami, Fijian, Tonga, me ngā tāngata Amazonian.

---

## He Aha Ngā Hua Mō Ngā Hoa Mahi

- Āhei ki ngā tauira ataura ataura 30 — PNG, SVG, me ngā āhua meme kaiwhakaaro
- Ngā kete ako i roto i ngā reo 6 (Ingarihi, Te Reo Māori, Português, Avañe'ẽ, Gagana Samoa, Arapi)
- API tūmatanui e pānui ana anake — 100 tono utu-kore ia hāora, kāore he kī e hiahiatia ana
- Kete pāpāho pāpori — SVG 624 i whakaritea mō Facebook, Instagram, TikTok, X
- Ngā PNG meme mō ngā tauira katoa × reo 6
- Raihana CC BY-NC-SA 4.0 — hei whakamahi, hei tūhono, me te tuku whakamana

---

## Te API Tūmatanui

Ko tō mātou API e pānui ana anake, kāore he tohu whakaurunga e hiahiatia ana. Ko ngā pātai katoa ka whakahoki JSON me ngā tuhinga whakamana i roto.

**URL Matua:** `https://te-pa-analytics.sketchschool.workers.dev`

| Endpoint | Whakamārama | Example |
|---|---|---|
| `GET /api/motifs` | Ngā tauira katoa 30 me ngā tikanga, URL CDN, me ngā hononga meme | `https://te-pa-analytics.sketchschool.workers.dev/api/motifs?culture=maori&lang=mi` |
| `GET /api/motifs/:id` | Tauira kotahi mā te ID — rārangi rawa katoa | `https://te-pa-analytics.sketchschool.workers.dev/api/motifs/koru` |
| `GET /api/cultures` | Ngā ahurea katoa 11 me ngā tatau tauira | `https://te-pa-analytics.sketchschool.workers.dev/api/cultures` |
| `GET /api/meme` | URL CDN mō te PNG meme reo-motuhake | `https://te-pa-analytics.sketchschool.workers.dev/api/meme?id=koru&lang=mi` |
| `GET /api/kit` | URL PDF kete ako mō ia reo | `https://te-pa-analytics.sketchschool.workers.dev/api/kit?lang=mi` |

> Tēnā, whakaurua te mātāmua X-TePa-Use: <ingoa kaupeka> ki ō tono. Ka āwhina tēnei i a mātou ki te mārama he aha ngā tikanga o te API me te tautoko i ngā tono pūtea.

### Ngā Tepe Tono

100 tono ia hāora ia IP. Mēnā e hiahia ana koe ki ētahi tepe nui ake mō tētahi kaupeka, whakapā mai ki a mātou i te-pa.org.

---

## Tikiake Rawa

Ko ngā rawa katoa ka tukuna mai i tō mātou CDN Cloudflare R2:

| Type | URL Pattern |
|---|---|
| PNG tauira | `https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/motifs/{ahurea}/{id}.png` |
| SVG tauira | `https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/motifs/{ahurea}/{id}.svg` |
| Meme reo-motuhake | `https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/motifs/memes/meme_{id}_{reo}.png` |
| PDF kete ako | `https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/teaching-kits/te-pa-teaching-kit-{reo}.pdf` |

---

## Whakamana me te Raihana

Ko ngā tauira, ngā āhua, me ngā rauemi ako katoa a Te Pā Tūwatawata ka tukuna i raro i CC BY-NC-SA 4.0. Ka āhei koe ki te toha me te whakarereke mō ngā tikanga kore-arumoni, me te tuku whakamana pēnei:

> **Te Pā Tūwatawata (te-pa.org) — CC BY-NC-SA 4.0**

Mō te whakamahi arumoni, me whiriwhiri me mātou. Whakapā mai ki a mātou.

---

## Hononga Pāpāho Pāpori

He kete pāpori tino mō ia tauira me ngā kāri i whakaritea mō ia paepae. Ko ngā tūtohu i tūtohungia mō ō tūāhono:

```
#ManaMotuhake  #ReoMāori  #TePa  #MātaurangaMāori  #DataSovereignty
```

I ō tūāhono, tūtohu @KiwiDialectic me te hononga ki te-pa.org/rhizome-mapper.html kia āhei ai ō hunga whai i te tūhura i te whatunga katoa.

---

## Tīmatanga Tere — Tauira Waehere

```javascript
// Tikina ngā tauira Māori katoa i roto i te Reo Māori
fetch('https://te-pa-analytics.sketchschool.workers.dev/api/motifs?culture=maori&lang=mi', {
  headers: { 'X-TePa-Use': 'IngoaKaupeka' }
})
.then(r => r.json())
.then(raraunga => {
  raraunga.motifs.forEach(m => {
    console.log(m.name_indigenous, m.assets.meme_png);
  });
});
```

---

## Whakapā Mai

Te Pā Tūwatawata
2 Mount Street, Te Pōhatu Tūhono, Ōtepoti 9023, Aotearoa

- [Paetukutuku](https://te-pa.org)
- [Mahere Rizome](https://te-pa.org/rhizome-mapper.html)
- [GitHub](https://github.com/robertmccallnz/kiwi-dialectic-te-pa-minisite)
- [Tuhinga API](https://te-pa-analytics.sketchschool.workers.dev/api)

---

*Tōpūtanga Aroha Te Pā Tūwatawata — te-pa.org — CC BY-NC-SA 4.0 — I hangaia aunoa*
