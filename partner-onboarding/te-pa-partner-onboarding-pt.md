# Te Pā Tūwatawata — Guia de Integração para Parceiros

> **Soberania de Dados Indígena · Educação em IA · Acesso à API de Motivos**

---

Bem-vindo à rede de parceiros da Te Pā Tūwatawata. Este guia oferece tudo o que você precisa para acessar nossa biblioteca de motivos, kits de ensino e API pública — e integrá-los em suas próprias plataformas, publicações ou programas educacionais.

---

## Sobre a Te Pā Tūwatawata

A Te Pā Tūwatawata é um Trust Charitable sediado em Port Chalmers, Aotearoa Nova Zelândia. Construímos infraestrutura educacional aberta para soberania de dados indígena, alfabetização em IA e sistemas de conhecimento decoloniais — enraizados nas tradições de motivos culturais dos povos Māori, Samoano, Pacífico, Guaraní, Shipibo, Guna, Kayapó, Yanomami, Fijiano, Tonganês e Amazônico.

---

## O Que os Parceiros Recebem

- Acesso a 30 motivos culturais indígenas — arte PNG, arquivos vetoriais SVG e imagens meme ativistas
- Kits de ensino em 6 idiomas (Inglês, Te Reo Māori, Português, Avañe'ẽ, Gagana Samoa, Árabe)
- API pública somente leitura — 100 solicitações gratuitas/hora, sem chave necessária
- Kit de mídia social — 624 cards SVG otimizados para Facebook, Instagram, TikTok, X
- PNGs de meme específicos por idioma para todos os 30 motivos × 6 idiomas
- Licença CC BY-NC-SA 4.0 — livre para usar e adaptar com atribuição

---

## API Pública

Nossa API somente leitura não requer autenticação. Todos os endpoints retornam JSON com atribuição completa integrada.

**URL Base:** `https://te-pa-analytics.sketchschool.workers.dev`

| Endpoint | Description | Example |
|---|---|---|
| `GET /api/motifs` | Todos os 30 motivos com significados, URLs de CDN e links de meme | `https://te-pa-analytics.sketchschool.workers.dev/api/motifs?culture=guarani&lang=pt` |
| `GET /api/motifs/:id` | Motivo único por ID — listagem completa de assets | `https://te-pa-analytics.sketchschool.workers.dev/api/motifs/yvy_mara_ey` |
| `GET /api/cultures` | Listar todas as 11 culturas com contagens de motivos | `https://te-pa-analytics.sketchschool.workers.dev/api/cultures` |
| `GET /api/meme` | URL CDN para PNG de meme específico por idioma | `https://te-pa-analytics.sketchschool.workers.dev/api/meme?id=yvy_mara_ey&lang=pt` |
| `GET /api/kit` | URL PDF do kit de ensino para um idioma | `https://te-pa-analytics.sketchschool.workers.dev/api/kit?lang=pt` |

> Por favor, inclua o cabeçalho X-TePa-Use: <nome do seu projeto> em suas solicitações. Isso nos ajuda a entender como a API está sendo usada e apoia futuras solicitações de financiamento.

### Limites de Taxa

100 solicitações por hora por endereço IP. Se você precisar de limites mais altos para um projeto específico, entre em contato conosco em te-pa.org.

---

## Download de Assets

Todos os assets são servidos pelo nosso CDN Cloudflare R2:

| Type | URL Pattern |
|---|---|
| Arte PNG do motivo | `https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/motifs/{cultura}/{id}.png` |
| Vetor SVG do motivo | `https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/motifs/{cultura}/{id}.svg` |
| Meme ativista (idioma) | `https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/motifs/memes/meme_{id}_{lang}.png` |
| PDF do kit de ensino | `https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/teaching-kits/te-pa-teaching-kit-{lang}.pdf` |

---

## Atribuição e Licença

Todos os motivos, imagens e materiais de ensino da Te Pā são publicados sob CC BY-NC-SA 4.0. Você pode compartilhar e adaptar para uso não comercial, desde que dê crédito da seguinte forma:

> **Te Pā Tūwatawata (te-pa.org) — CC BY-NC-SA 4.0**

O uso comercial requer um acordo separado. Entre em contato conosco para discutir arranjos de parceria.

---

## Integração com Mídias Sociais

Cada motivo tem um kit social completo com cards otimizados por plataforma. Hashtags recomendadas para suas postagens:

```
#SoberaniadeDados  #PovosIndígenas  #TePa  #AIIndígena  #CARE
```

Ao postar, marque @KiwiDialectic e adicione um link para te-pa.org/rhizome-mapper.html para que seu público explore a rede completa.

---

## Início Rápido — Exemplo de Código

```javascript
// Buscar todos os motivos Guaraní em Português
fetch('https://te-pa-analytics.sketchschool.workers.dev/api/motifs?culture=guarani&lang=pt', {
  headers: { 'X-TePa-Use': 'NomeDoSeuProjeto' }
})
.then(r => r.json())
.then(dados => {
  dados.motifs.forEach(m => {
    console.log(m.name_en, m.assets.meme_png);
  });
});
```

---

## Contato e Comunidade

Te Pā Tūwatawata
2 Mount Street, Port Chalmers, Dunedin 9023, Aotearoa Nova Zelândia

- [Site](https://te-pa.org)
- [Mapa Rizoma](https://te-pa.org/rhizome-mapper.html)
- [GitHub](https://github.com/robertmccallnz/kiwi-dialectic-te-pa-minisite)
- [Documentação da API](https://te-pa-analytics.sketchschool.workers.dev/api)

---

*Trust Charitable Te Pā Tūwatawata — te-pa.org — CC BY-NC-SA 4.0 — Gerado automaticamente*
