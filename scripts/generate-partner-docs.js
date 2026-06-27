#!/usr/bin/env node
/**
 * Te Pā — Partner Onboarding Doc Generator
 * ==========================================
 * Reads: partner-onboarding/_template.json
 * Writes: partner-onboarding/te-pa-partner-onboarding-{lang}.md  (per language)
 *         partner-onboarding/index.md                             (language index)
 *
 * Run manually:          node scripts/generate-partner-docs.js
 * Run for one language:  node scripts/generate-partner-docs.js --lang=pt
 * Add new language:      Add block to _template.json languages, then re-run
 *
 * This script is called automatically by add-language.js when a new
 * language is added to the motif bank. It regenerates ALL docs so the
 * index always reflects every available language.
 *
 * Upload to R2:          node scripts/generate-partner-docs.js --upload
 * (Requires CF_ACCOUNT, CF_R2_TOKEN env vars)
 */

const fs   = require('fs');
const path = require('path');

const ROOT     = path.resolve(__dirname, '..');
const TEMPLATE = path.join(ROOT, 'partner-onboarding', '_template.json');
const OUT_DIR  = path.join(ROOT, 'partner-onboarding');

const CDN      = 'https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev';
const API_BASE = 'https://te-pa-analytics.sketchschool.workers.dev';
const SITE     = 'https://te-pa.org';

// ── CLI args ────────────────────────────────────────────────────────────────
const args       = process.argv.slice(2);
const langFilter = (args.find(a => a.startsWith('--lang=')) || '').replace('--lang=', '') || null;
const doUpload   = args.includes('--upload');

// ── Load template ────────────────────────────────────────────────────────────
const tpl    = JSON.parse(fs.readFileSync(TEMPLATE, 'utf8'));
const langs  = Object.values(tpl.languages).filter(l => !langFilter || l.code === langFilter);

if (!langs.length) {
  console.error(`Language '${langFilter}' not found in template. Available:`, Object.keys(tpl.languages).join(', '));
  process.exit(1);
}

// ── Markdown renderer ─────────────────────────────────────────────────────────
function renderDoc(lang) {
  const d   = lang.doc;
  const rtl = lang.direction === 'rtl';
  const dir = rtl ? ' (right-to-left)' : '';

  const hashtagStr = lang.hashtags.join('  ');

  const endpointRows = d.api_endpoints.map(e =>
    `| \`${e.endpoint}\` | ${e.description} | \`${API_BASE}${e.example}\` |`
  ).join('\n');

  const assetRows = d.asset_paths.map(a =>
    `| ${a.label} | \`${a.path}\` |`
  ).join('\n');

  const contactLinks = d.contact_links.map(l =>
    `- [${l.label}](${l.url})`
  ).join('\n');

  const whatYouGet = d.what_you_get.map(i => `- ${i}`).join('\n');

  return `# ${d.title}

> **${d.subtitle}**${dir}

---

${d.welcome}

---

## ${d.about_heading}

${d.about_body}

---

## ${d.what_you_get_heading}

${whatYouGet}

---

## ${d.api_heading}

${d.api_intro}

**${d.api_base_label}:** \`${API_BASE}\`

| Endpoint | ${lang.code === 'ar' ? 'الوصف' : lang.code === 'mi' ? 'Whakamārama' : lang.code === 'gn' ? 'Mombe\'u' : lang.code === 'sm' ? 'Fa\'amatala' : 'Description'} | Example |
|---|---|---|
${endpointRows}

> ${d.api_courtesy}

### ${d.rate_limit_heading}

${d.rate_limit_body}

---

## ${d.assets_heading}

${d.assets_cdn}

| ${lang.code === 'ar' ? 'النوع' : 'Type'} | URL Pattern |
|---|---|
${assetRows}

---

## ${d.attribution_heading}

${d.attribution_body}

> **${d.attribution_example}**

${d.attribution_note}

---

## ${d.social_heading}

${d.social_body}

\`\`\`
${hashtagStr}
\`\`\`

${d.social_note}

---

## ${d.code_example_heading}

\`\`\`javascript
${d.code_example}
\`\`\`

---

## ${d.contact_heading}

${d.contact_body}

${contactLinks}

---

*${d.footer}*
`;
}

// ── Render index doc ──────────────────────────────────────────────────────────
function renderIndex(allLangs) {
  const rows = allLangs.map(l => {
    const dir = l.direction === 'rtl' ? ' ←' : '';
    return `| ${l.native_name}${dir} | \`${l.code}\` | ${l.region} | [te-pa-partner-onboarding-${l.code}.md](te-pa-partner-onboarding-${l.code}.md) | [PDF](${CDN}/partner-onboarding/te-pa-partner-onboarding-${l.code}.pdf) |`;
  }).join('\n');

  const apiRows = [
    `| All motifs | \`${API_BASE}/api/motifs\` | \`?lang={code}&culture={name}\` |`,
    `| Single motif | \`${API_BASE}/api/motifs/:id\` | \`/api/motifs/koru?lang=pt\` |`,
    `| Cultures | \`${API_BASE}/api/cultures\` | — |`,
    `| Meme image | \`${API_BASE}/api/meme\` | \`?id=koru&lang=sm\` |`,
    `| Teaching kit | \`${API_BASE}/api/kit\` | \`?lang=ar\` |`,
  ].join('\n');

  return `# Te Pā Tūwatawata — Partner Onboarding Docs

> Indigenous Data Sovereignty · AI Education · Motif Access API  
> CC BY-NC-SA 4.0 — [te-pa.org](${SITE})

---

## Available Languages

| Language | Code | Region | Markdown | PDF |
|---|---|---|---|---|
${rows}

---

## Quick API Reference

Base URL: \`${API_BASE}\`

| Resource | Endpoint | Query Params |
|---|---|---|
${apiRows}

Rate limit: **100 requests/hour per IP** — no key required.  
Courtesy header: \`X-TePa-Use: <your-project-name>\`

---

## Adding a New Language

1. Add a new language block to \`partner-onboarding/_template.json\`
2. Add the matching \`meaning_{code}\` field to every motif in \`data/motif-bank-master.json\`
3. Run \`node scripts/generate-partner-docs.js\` — all onboarding docs regenerate automatically
4. Run \`node scripts/add-language.js --lang={code}\` to generate memes + teaching kit assets

This index is regenerated every time the script runs.

---

## Attribution

All Te Pā motifs, images, and teaching materials are published under  
**CC BY-NC-SA 4.0** — free to use and adapt with attribution:

> Te Pā Tūwatawata (te-pa.org) — CC BY-NC-SA 4.0

---

*Generated automatically by \`scripts/generate-partner-docs.js\`*  
*Te Pā Tūwatawata Charitable Trust — 2 Mount Street, Port Chalmers, Dunedin 9023, Aotearoa New Zealand*
`;
}

// ── Write files ───────────────────────────────────────────────────────────────
let generated = 0;
for (const lang of langs) {
  const md   = renderDoc(lang);
  const file = path.join(OUT_DIR, `te-pa-partner-onboarding-${lang.code}.md`);
  fs.writeFileSync(file, md, 'utf8');
  console.log(`✓  ${file}`);
  generated++;
}

// Always regenerate index with ALL languages (not just filtered ones)
const allLangs = Object.values(tpl.languages);
const indexMd  = renderIndex(allLangs);
fs.writeFileSync(path.join(OUT_DIR, 'index.md'), indexMd, 'utf8');
console.log(`✓  ${path.join(OUT_DIR, 'index.md')}`);

console.log(`\nGenerated ${generated} onboarding doc(s) + index.`);

// ── Upload to R2 if --upload flag ─────────────────────────────────────────────
if (doUpload) {
  const { execSync } = require('child_process');
  const ACCOUNT = process.env.CF_ACCOUNT || '063ea8fc4f5e84d72b9a09933215d0e1';
  const TOKEN   = process.env.CF_R2_TOKEN;
  if (!TOKEN) {
    console.error('\n⚠  CF_R2_TOKEN env var not set — skipping R2 upload.');
    console.error('   Set it with: export CF_R2_TOKEN=your_token');
    process.exit(0);
  }
  const BASE = `https://api.cloudflare.com/client/v4/accounts/${ACCOUNT}/r2/buckets/te-pa-rhizome/objects`;
  for (const lang of langs) {
    const file = path.join(OUT_DIR, `te-pa-partner-onboarding-${lang.code}.md`);
    const key  = `partner-onboarding/te-pa-partner-onboarding-${lang.code}.md`;
    try {
      execSync(`curl -s -o /dev/null -w "%{http_code}" -X PUT "${BASE}/${key}" -H "Authorization: Bearer ${TOKEN}" -H "Content-Type: text/markdown" --data-binary @"${file}"`);
      console.log(`↑  R2: ${key}`);
    } catch (e) {
      console.error(`✗  R2 upload failed: ${key}`, e.message);
    }
  }
}
