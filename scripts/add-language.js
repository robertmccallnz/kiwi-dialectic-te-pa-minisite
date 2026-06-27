#!/usr/bin/env node
/**
 * Te Pā — Add New Language Workflow
 * ===================================
 * Usage: node scripts/add-language.js --lang=sw --name="Swahili" --native="Kiswahili" --region="East Africa"
 *
 * What this does automatically:
 *  1. Validates the language block exists in partner-onboarding/_template.json
 *  2. Adds meaning_{lang} stub fields to all 30 motifs in data/motif-bank-master.json
 *  3. Adds the language entry to teaching-kits/manifest.json
 *  4. Regenerates all partner onboarding docs (calls generate-partner-docs.js)
 *  5. Prints a checklist of manual steps remaining (teaching kit PDF, meme generation)
 *
 * Manual steps after running this script:
 *  A) Translate meaning_{lang} stubs in motif-bank-master.json
 *  B) Generate teaching kit PDF and upload to R2
 *  C) Run: node scripts/generate-partner-docs.js --lang={code} --upload
 *  D) Run: python3 scripts/gen_meme_pngs.py --lang={code}   (upload memes to R2)
 *  E) Commit + push + deploy
 */

const fs   = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..');

// ── Parse args ────────────────────────────────────────────────────────────────
const args = Object.fromEntries(
  process.argv.slice(2)
    .filter(a => a.startsWith('--'))
    .map(a => { const [k, v] = a.slice(2).split('='); return [k, v || true]; })
);

const langCode   = args.lang;
const langName   = args.name   || langCode;
const nativeName = args.native || langCode;
const region     = args.region || 'Global';

if (!langCode) {
  console.error('Usage: node scripts/add-language.js --lang=sw --name="Swahili" --native="Kiswahili" --region="East Africa"');
  process.exit(1);
}

console.log(`\n🌐  Adding language: ${langCode} (${nativeName})\n`);

// ── Step 1: Check template has the language block ─────────────────────────────
const tplPath = path.join(ROOT, 'partner-onboarding', '_template.json');
const tpl     = JSON.parse(fs.readFileSync(tplPath, 'utf8'));

if (!tpl.languages[langCode]) {
  console.error(`✗  Language '${langCode}' not found in partner-onboarding/_template.json`);
  console.error(`   Add the full language + doc block first, then re-run this script.`);
  console.error(`   See an existing language block (e.g. 'en') as a template.`);
  process.exit(1);
}
console.log(`✓  Language block found in _template.json`);

// ── Step 2: Add meaning stub to motif bank ────────────────────────────────────
const bankPath = path.join(ROOT, 'data', 'motif-bank-master.json');
const bank     = JSON.parse(fs.readFileSync(bankPath, 'utf8'));
const motifs   = bank.motifs || bank;
const mlist    = Array.isArray(motifs) ? motifs : Object.values(motifs);

let stubsAdded = 0;
for (const m of mlist) {
  const field = `meaning_${langCode}`;
  if (!m[field]) {
    // Create a stub from English meaning — translator fills this in
    m[field] = `[TRANSLATE] ${m.meaning_en || ''}`;
    stubsAdded++;
  }
}

if (Array.isArray(bank)) {
  fs.writeFileSync(bankPath, JSON.stringify(bank, null, 2), 'utf8');
} else {
  fs.writeFileSync(bankPath, JSON.stringify(bank, null, 2), 'utf8');
}

console.log(`✓  Added meaning_${langCode} stub to ${stubsAdded} motifs in motif-bank-master.json`);

// ── Step 3: Add to teaching-kits/manifest.json ───────────────────────────────
const manifestPath = path.join(ROOT, 'teaching-kits', 'manifest.json');
const manifest     = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
const CDN = 'https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev';

if (!manifest.languages[langCode]) {
  manifest.languages[langCode] = {
    code:             langCode,
    name:             langName,
    native_name:      nativeName,
    region,
    direction:        tpl.languages[langCode].direction || 'ltr',
    teaching_kit_pdf: `${CDN}/teaching-kits/te-pa-teaching-kit-${langCode}.pdf`,
    student_activity_pdf: `${CDN}/teaching-kits/te-pa-student-activity-sheets.pdf`,
    social_media_kit_pdf: `${CDN}/teaching-kits/te-pa-social-media-kit.pdf`,
    motif_count:      mlist.length,
    kit_manifest:     `https://te-pa.org/teaching-kits/${langCode}/kit-manifest.json`,
    hashtags:         tpl.languages[langCode].hashtags || [`#TePa`, `#IndigenousSovereignty`],
    status:           'pending_translation',
  };
  manifest.generated_at = new Date().toISOString();
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2), 'utf8');
  console.log(`✓  Added '${langCode}' to teaching-kits/manifest.json`);
} else {
  console.log(`ℹ  '${langCode}' already in manifest.json — skipped`);
}

// ── Step 4: Regenerate all partner onboarding docs ────────────────────────────
console.log(`\n📄  Regenerating partner onboarding docs...`);
try {
  execSync(`node ${path.join(ROOT, 'scripts', 'generate-partner-docs.js')}`, { stdio: 'inherit' });
} catch (e) {
  console.error('✗  generate-partner-docs.js failed:', e.message);
}

// ── Step 5: Print remaining manual checklist ──────────────────────────────────
console.log(`
╔══════════════════════════════════════════════════════════════════╗
║  Language '${langCode}' (${nativeName}) added — manual steps remaining   
╚══════════════════════════════════════════════════════════════════╝

 A) Translate meaning_${langCode} stubs in:
      data/motif-bank-master.json
    Search for [TRANSLATE] — 30 entries to fill in.

 B) Write the teaching kit PDF in ${nativeName} and upload to R2:
      https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev/teaching-kits/te-pa-teaching-kit-${langCode}.pdf

 C) Upload the finished partner onboarding doc to R2:
      CF_R2_TOKEN=your_token node scripts/generate-partner-docs.js --lang=${langCode} --upload

 D) Generate language-specific meme PNGs:
      python3 scripts/gen_meme_pngs.py  (update LANGS dict to include '${langCode}')
    Then upload to R2:
      motifs/memes/meme_{id}_${langCode}.png  (30 files)

 E) Add social kit SVGs for new language in:
      social-kit/motifs/{motif_id}/${langCode}-*.svg

 F) Update teaching-kits/manifest.json — change 'status' from 'pending_translation' to 'active'

 G) Commit, push, deploy:
      git add -A && git commit -m "feat: add ${langCode} (${nativeName}) language support"
      git push origin main
      npx vercel --scope aiartworks --prod --yes

Done. Partner docs auto-regenerated at: partner-onboarding/te-pa-partner-onboarding-${langCode}.md
`);
