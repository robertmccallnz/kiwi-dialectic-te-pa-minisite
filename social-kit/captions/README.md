# Social Kit — Captions

Multilingual social-media captions for the six campaign memes in `../`.

**Live page:** [te-pa.org/social-kit/captions/](https://te-pa.org/social-kit/captions/)

## What's here

| File | Purpose |
|---|---|
| `index.html` | Interactive captions page — language switcher (MI/EN/PT/GN/SM), per-card copy buttons, char-budget meter (X/Bluesky/Mastodon), hashtag-variant toggle |
| `print.html` | PDF render template (reads `?lang=xx&variant=per_card\|unified`) — source of the PDFs in `../../pdfs/te-pa-social-kit-{lang}.pdf` |
| `campaign-captions.json` | 30 captions (6 cards × 5 languages) with per-card hashtags. Schema `1.0` |
| `campaign-captions-unified.json` | Same 30 captions with unified hashtag pair `#TePāTūwatawata #TeManaRaraunga`. Schema `1.0-unified-hashtags` |
| `campaign-captions-long.csv` | 60 rows = 30 captions × 2 hashtag variants. One row per card × language × variant |
| `campaign-captions-wide.csv` | 12 rows = 6 cards × 2 variants. All 5 languages side-by-side per row |

## Cards

`raupatu` · `3-questions` · `te-mana-raraunga` · `data-sovereignty` · `enrol` · `anamata`

## Languages

`mi` Te Reo Māori (primary) · `en` English · `pt` Português · `gn` Avañe'ẽ (Guaraní) · `sm` Gagana Sāmoa

## Regenerating outputs

`campaign-captions.json` is the source of truth. Everything else is derived:

```bash
# Regenerate unified-hashtag JSON from per-card JSON
python3 scripts/build-social-captions-unified.py

# Regenerate both CSVs from the two JSON files
python3 scripts/build-social-captions-csv.py
```

Run from the repo root.

## Char-budget notes

All 30 per-card captions fit X's 280-char limit. The unified-hashtag variant adds +6 to +19 chars per caption; max is 239 (`3-questions:sm`). Still well under 280.

## Register notes (translation softening)

- **Sāmoan** uses `aveeseina` ("being taken away") rather than `faoa` ("armed seizure") in `raupatu` + `enrol`. `gaoia` retained in `anamata` where harder verb suits "built — or stolen — in code".
- **Guaraní** uses `ñemboyke` ("dispossession") rather than `ñemonda` ("theft") in `raupatu` + `enrol`. `oñembyaíta` ("will be undone") replaces `oñemondáta` in `anamata`.
- Te reo Māori lines have been drafted with care but a final kaitiaki reo review is recommended before high-visibility posting (particularly cards 1, 3, 6).

## License

Captions, copy, and PDFs released under **Creative Commons Attribution-ShareAlike 4.0** (CC BY-SA 4.0). Code (HTML, build scripts) released under MIT.

See the [main project README](../../README.md) for full project context and licensing details.
