#!/usr/bin/env node
/**
 * Te Pā — Add New Language Workflow
 * ===================================
 * Usage: node scripts/add-language.js --lang=sw --name="Swahili" --native="Kiswahili" --region="East Africa"
 *
 * CI mode (GitHub Actions):
 *   node scripts/add-language.js --lang=sw --name="Swahili" --native="Kiswahili" --region="East Africa" --ci
 *
 *   In CI mode:
 *     - Suppresses the interactive checklist printout
 *     - Does NOT call execSync to invoke generate-partner-docs.js
 *       (the workflow runs that script as a separate step)
 *     - Only performs: validate template block, add meaning stubs to motif bank,
 *       update manifest.json — then exits cleanly with code 0
 *     - Outputs machine-readable summary lines (CI-ADDED, CI-SKIPPED, CI-STUBS)
 *       so the workflow can parse what happened
 *
 * What this does automatically (both modes):
 *  1. Validates the language block exists in partner-onboarding/_template.json
 *  2. Adds meaning_{lang} stub fields to all 30 motifs in data/motif-bank-master.json
 *  3. Adds the language entry to teaching-kits/manifest.json
 *  4. [interactive only] Regenerates all partner onboarding docs (calls generate-partner-docs.js)
 *  5. [interactive only] Prints a checklist of manual steps remaining
 *
 * Manual steps after running (interactive mode):
 *  A) Translate meaning_{lang} stubs in motif-bank-master.json
 *  B) Generate teaching kit PDF and upload to R2
 *  C) Run: node scripts/generate-partner-docs.js --lang={code} --upload
 *  D) Run: python3 scripts/gen_meme_pngs.py --lang={code}   (upload memes to R2)
 *  E) Commit + push + deploy
 */

const fs   = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');

// ── Parse args ────────────────────────────────────────────────────────────────
const args = Object.fromEntries(
  process.argv.slice(2)
    .filter(a => a.startsWith('--'))
    .map(a => { const [k, v] = a.slice(2).split('='); return [k, v === undefined ? true : v]; })
);

const langCode   = args.lang;
const langName   = args.name   || langCode;
const nativeName = args.native || langCode;
const region     = args.region || 'Global';
const CI         = args.ci === true || args.ci === 'true';

if (!langCode) {
  console.error('Usage: node scripts/add-language.js --lang=sw --name="Swahili" --native="Kiswahili" --region="East Africa" [--ci]');
  process.exit(1);
}

if (!CI) {
  console.log(`\n🌐  Adding language: ${langCode} (${nativeName})\n`);
}

// ── Step 1: Check template has the language block ─────────────────────────────
const tplPath = path.join(ROOT, 'partner-onboarding', '_template.json');
const tpl     = JSON.parse(fs.readFileSync(tplPath, 'utf8'));

if (!tpl.languages[langCode]) {
  console.error(`✗  Language '${langCode}' not found in partner-onboarding/_template.json`);
  console.error(`   Add the full language + doc block first, then re-run this script.`);
  console.error(`   See an existing language block (e.g. 'en') as a template.`);
  process.exit(1);
}

if (CI) {
  console.log(`CI-VALIDATED: ${langCode}`);
} else {
  console.log(`✓  Language block found in _template.json`);
}

// ── Step 2: Add meaning stub to motif bank ────────────────────────────────────
const bankPath = path.join(ROOT, 'data', 'motif-bank-master.json');
const bank     = JSON.parse(fs.readFileSync(bankPath, 'utf8'));
const motifs   = bank.motifs || bank;
const mlist    = Array.isArray(motifs) ? motifs : Object.values(motifs);

let stubsAdded = 0;
for (const m of mlist) {
  const field = `meaning_${langCode}`;
  if (!m[field]) {
    m[field] = `[TRANSLATE] ${m.meaning_en || ''}`;
    stubsAdded++;
  }
}

fs.writeFileSync(bankPath, JSON.stringify(bank, null, 2), 'utf8');

if (CI) {
  console.log(`CI-STUBS: ${langCode}=${stubsAdded}`);
} else {
  console.log(`✓  Added meaning_${langCode} stub to ${stubsAdded} motifs in motif-bank-master.json`);
}

// ── Step 3: Add to teaching-kits/manifest.json ───────────────────────────────
const manifestPath = path.join(ROOT, 'teaching-kits', 'manifest.json');
const manifest     = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
const CDN = 'https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev';

if (!manifest.languages[langCode]) {
  manifest.languages[langCode] = {
    code:                langCode,
    name:                langName,
    native_name:         nativeName,
    region,
    direction:           tpl.languages[langCode].direction || 'ltr',
    teaching_kit_pdf:    `${CDN}/teaching-kits/te-pa-teaching-kit-${langCode}.pdf`,
    student_activity_pdf:`${CDN}/teaching-kits/te-pa-student-activity-sheets.pdf`,
    social_media_kit_pdf:`${CDN}/teaching-kits/te-pa-social-media-kit.pdf`,
    motif_count:         mlist.length,
    kit_manifest:        `https://te-pa.org/teaching-kits/${langCode}/kit-manifest.json`,
    hashtags:            tpl.languages[langCode].hashtags || [`#TePa`, `#IndigenousSovereignty`],
    status:              'pending_translation',
  };
  manifest.generated_at = new Date().toISOString();
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2), 'utf8');

  if (CI) {
    console.log(`CI-ADDED: ${langCode}`);
  } else {
    console.log(`✓  Added '${langCode}' to teaching-kits/manifest.json`);
  }
} else {
  if (CI) {
    console.log(`CI-SKIPPED: ${langCode} already in manifest`);
  } else {
    console.log(`ℹ  '${langCode}' already in manifest.json — skipped`);
  }
}

// ── Step 4 (interactive only): Regenerate partner docs ────────────────────────
if (!CI) {
  const { execSync } = require('child_process');
  console.log(`\n📄  Regenerating partner onboarding docs...`);
  try {
    execSync(`node ${path.join(ROOT, 'scripts', 'generate-partner-docs.js')}`, { stdio: 'inherit' });
  } catch (e) {
    console.error('✗  generate-partner-docs.js failed:', e.message);
  }
}

// ── Step 5 (interactive only): Print checklist ────────────────────────────────
if (!CI) {
  console.log(`
╔══════════════════════════════════════════════════════════════════╗
║  Language '${langCode}' (${nativeName}) added — manual steps remaining   
╚══════════════════════════════════════════════════════════════════╝

 A) Translate meaning_${langCode} stubs in:
      data/motif-bank-master.json
    Search for [TRANSLATE] — ${stubsAdded} entries to fill in.

 B) Write the teaching kit PDF in ${nativeName} and upload to R2:
      ${CDN}/teaching-kits/te-pa-teaching-kit-${langCode}.pdf

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
}
