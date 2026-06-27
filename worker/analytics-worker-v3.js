/**
 * Te Pā Analytics Worker — v3.0
 *
 * ── PRIVATE ENDPOINTS (te-pa.org only) ─────────────────────────────────────
 *   POST /track             — record an event
 *   GET  /stats             — aggregated counts per org + global totals
 *   GET  /kits              — kit download breakdown by language, country, date
 *   GET  /heatmap           — geo breakdown (country → event counts)
 *   GET  /live              — last 50 events (for live feed)
 *   GET  /connections       — social network: which orgs are shared together
 *   GET  /motifs            — motif bank (?culture=&region=&id=&lang=)
 *   GET  /motifs/cultures   — list all cultures with counts
 *
 * ── PUBLIC READ-ONLY API (open CORS, rate limited 100 req/hr/IP) ────────────
 *   GET  /api               — API index / docs
 *   GET  /api/motifs        — all 30 motifs (?culture=&region=&id=&lang=en|mi|pt|gn|sm|ar)
 *   GET  /api/motifs/:id    — single motif by ID
 *   GET  /api/cultures      — list cultures with motif counts
 *   GET  /api/meme          — meme CDN URLs (?id=koru&lang=pt)
 *   GET  /api/kit           — teaching kit PDF CDN URLs (?lang=en)
 *
 * Rate limit: 100 requests per hour per IP (tracked in D1)
 * Attribution: X-TePa-Use header encouraged (logged but not required)
 */

const CDN = 'https://pub-bf8eea881c1e44d88eda5192c3b92291.r2.dev';
const KIT_CDN = `${CDN}/teaching-kits`;
const RATE_LIMIT = 100; // requests per hour per IP

const CORS_HEADERS = (origin) => ({
  'Access-Control-Allow-Origin': origin || '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, X-TePa-Use',
  'Access-Control-Max-Age': '86400',
});

const PUBLIC_CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, X-TePa-Use',
};

function jsonResponse(data, status = 200, origin = '*') {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...CORS_HEADERS(origin),
      'Cache-Control': 'no-store',
    },
  });
}

function publicJsonResponse(data, status = 200, cacheSeconds = 300) {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...PUBLIC_CORS,
      'Cache-Control': `public, max-age=${cacheSeconds}`,
      'X-TePa-API': 'v1',
      'X-TePa-Attribution': 'CC BY-NC-SA 4.0 — te-pa.org',
    },
  });
}

function errorResponse(message, status = 400) {
  return new Response(JSON.stringify({ error: message, docs: 'https://te-pa-analytics.sketchschool.workers.dev/api' }), {
    status,
    headers: { 'Content-Type': 'application/json', ...PUBLIC_CORS },
  });
}

/** Rate limit: returns { allowed: bool, remaining: int, reset_at: string } */
async function checkRateLimit(env, ip) {
  const hourKey = new Date().toISOString().slice(0, 13); // "2026-06-27T14"
  const key = `rl:${ip}:${hourKey}`;

  try {
    const row = await env.DB.prepare(
      `SELECT count FROM rate_limits WHERE key = ?`
    ).bind(key).first();

    const count = row ? row.count : 0;

    if (count >= RATE_LIMIT) {
      const reset = new Date();
      reset.setMinutes(0, 0, 0);
      reset.setHours(reset.getHours() + 1);
      return { allowed: false, remaining: 0, reset_at: reset.toISOString() };
    }

    // Upsert counter
    await env.DB.prepare(`
      INSERT INTO rate_limits (key, count, expires_at)
      VALUES (?, 1, datetime('now', '+2 hours'))
      ON CONFLICT(key) DO UPDATE SET count = count + 1
    `).bind(key).run();

    return { allowed: true, remaining: RATE_LIMIT - count - 1, reset_at: null };
  } catch (_) {
    // If rate_limits table doesn't exist yet, allow through
    return { allowed: true, remaining: 99, reset_at: null };
  }
}

/** Strip private/internal fields from motif rows before public response */
function publicMotif(m, lang = 'en') {
  const meaning = m[`meaning_${lang}`] || m.meaning_en || '';
  let themes = [], sources = [];
  try { themes  = JSON.parse(m.political_themes || '[]'); } catch (_) {}
  try { sources = JSON.parse(m.sources          || '[]'); } catch (_) {}

  return {
    id:              m.id,
    name_en:         m.name_en,
    name_indigenous: m.name_indigenous,
    culture:         m.culture,
    region:          m.rhizome_region,
    colour_primary:  m.colour_primary,
    meaning:         meaning,
    meanings: {
      en: m.meaning_en || '',
      pt: m.meaning_pt || '',
      sm: m.meaning_sm || '',
      gn: m.meaning_gn || '',
      ar: m.meaning_ar || '',
    },
    political_themes: themes,
    resistance_use:   m.resistance_use || '',
    course_module:    m.course_module  || '',
    assets: {
      motif_png: `${CDN}/motifs/${m.culture}/${m.id}.png`,
      motif_svg: `${CDN}/motifs/${m.culture}/${m.id}.svg`,
      meme_png:  `${CDN}/motifs/memes/meme_${m.id}.png`,
      memes_by_language: {
        en: `${CDN}/motifs/memes/meme_${m.id}_en.png`,
        mi: `${CDN}/motifs/memes/meme_${m.id}_mi.png`,
        pt: `${CDN}/motifs/memes/meme_${m.id}_pt.png`,
        gn: `${CDN}/motifs/memes/meme_${m.id}_gn.png`,
        sm: `${CDN}/motifs/memes/meme_${m.id}_sm.png`,
        ar: `${CDN}/motifs/memes/meme_${m.id}_ar.png`,
      },
    },
    sources,
    license: 'CC BY-NC-SA 4.0',
    attribution: 'Te Pā Tūwatawata — te-pa.org',
  };
}

const TEACHING_KITS = {
  en: { language: 'English',          pdf: `${KIT_CDN}/te-pa-teaching-kit-en.pdf` },
  mi: { language: 'Te Reo Māori',     pdf: `${KIT_CDN}/te-pa-teaching-kit-mi.pdf` },
  pt: { language: 'Português',        pdf: `${KIT_CDN}/te-pa-teaching-kit-pt.pdf` },
  gn: { language: "Avañe'ẽ (Guaraní)",pdf: `${KIT_CDN}/te-pa-teaching-kit-gn.pdf` },
  sm: { language: 'Gagana Samoa',     pdf: `${KIT_CDN}/te-pa-teaching-kit-sm.pdf` },
  ar: { language: 'العربية',          pdf: `${KIT_CDN}/te-pa-teaching-kit-ar.pdf` },
};

export default {
  async fetch(request, env, ctx) {
    const url    = new URL(request.url);
    const origin = request.headers.get('Origin') || '*';
    const ip     = request.headers.get('CF-Connecting-IP') || '0.0.0.0';

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: CORS_HEADERS(origin) });
    }

    // ════════════════════════════════════════════════════════════════════
    // PUBLIC READ-ONLY API  /api/*
    // ════════════════════════════════════════════════════════════════════
    if (url.pathname === '/api' || url.pathname.startsWith('/api/')) {

      // Rate limit check
      const rl = await checkRateLimit(env, ip);
      if (!rl.allowed) {
        return new Response(JSON.stringify({
          error: 'Rate limit exceeded — 100 requests per hour per IP',
          reset_at: rl.reset_at,
          docs: 'https://te-pa-analytics.sketchschool.workers.dev/api',
        }), {
          status: 429,
          headers: {
            'Content-Type': 'application/json',
            ...PUBLIC_CORS,
            'Retry-After': '3600',
            'X-RateLimit-Limit': String(RATE_LIMIT),
            'X-RateLimit-Remaining': '0',
            'X-RateLimit-Reset': rl.reset_at,
          },
        });
      }

      const rlHeaders = {
        'X-RateLimit-Limit':     String(RATE_LIMIT),
        'X-RateLimit-Remaining': String(rl.remaining),
      };

      // Log X-TePa-Use header if provided (non-blocking)
      const useHeader = request.headers.get('X-TePa-Use');
      if (useHeader && env.DB) {
        ctx.waitUntil(
          env.DB.prepare(
            `INSERT INTO events (type, org_id, referrer, ua, created_at)
             VALUES ('api_request', ?, ?, ?, datetime('now'))`
          ).bind(useHeader.slice(0, 200), url.pathname, request.headers.get('User-Agent') || null).run().catch(() => {})
        );
      }

      // ── GET /api  — docs ──────────────────────────────────────────────
      if (url.pathname === '/api' || url.pathname === '/api/') {
        return publicJsonResponse({
          name: 'Te Pā Tūwatawata — Public Motif API',
          version: 'v1',
          description: 'Read-only access to the Te Pā indigenous motif bank and teaching kit assets. 30 motifs across 11 cultures — Māori, Samoan, Pacific, Tongan, Fijian, Guaraní, Shipibo-Conibo, Guna, Kayapó, Yanomami, Amazonian.',
          base_url: 'https://te-pa-analytics.sketchschool.workers.dev',
          rate_limit: '100 requests per hour per IP',
          attribution: 'Please credit: Te Pā Tūwatawata (te-pa.org) — CC BY-NC-SA 4.0',
          courtesy_header: 'Include X-TePa-Use: <your-project-description> to help us understand how the API is used',
          license: 'CC BY-NC-SA 4.0 — free to use, share, adapt with attribution. Not for commercial use.',
          endpoints: {
            'GET /api/motifs': {
              description: 'All 30 motifs with meanings, CDN image URLs, and meme links',
              params: {
                lang:    'en | mi | pt | gn | sm | ar — response language for meaning field (default: en)',
                culture: 'maori | samoan | pacific | tongan | fijian | guarani | shipibo | guna | kayapo | yanomami | amazonian',
                region:  'maori | oceania | south_america | global',
                id:      'motif ID e.g. koru, niho_mano, yvy_mara_ey',
              },
              example: '/api/motifs?culture=maori&lang=mi',
            },
            'GET /api/motifs/:id': {
              description: 'Single motif by ID — full asset listing',
              example: '/api/motifs/koru',
            },
            'GET /api/cultures': {
              description: 'List all 11 cultures with motif counts and primary colours',
              example: '/api/cultures',
            },
            'GET /api/meme': {
              description: 'Direct CDN URL for a motif meme image in a specific language',
              params: {
                id:   'motif ID (required)',
                lang: 'en | mi | pt | gn | sm | ar (default: en)',
              },
              example: '/api/meme?id=koru&lang=pt',
            },
            'GET /api/kit': {
              description: 'Teaching kit PDF CDN URL for a given language',
              params: { lang: 'en | mi | pt | gn | sm | ar (default: en)' },
              example: '/api/kit?lang=gn',
            },
          },
          cultures: ['maori','samoan','pacific','tongan','fijian','guarani','shipibo','guna','kayapo','yanomami','amazonian'],
          languages: { en:'English', mi:'Te Reo Māori', pt:'Português', gn:"Avañe'ẽ (Guaraní)", sm:'Gagana Samoa', ar:'العربية' },
          site: 'https://te-pa.org',
          github: 'https://github.com/robertmccallnz/kiwi-dialectic-te-pa-minisite',
          contact: 'te-pa.org/contact',
        }, 200, 3600);
      }

      // ── GET /api/cultures ─────────────────────────────────────────────
      if (url.pathname === '/api/cultures') {
        try {
          const rows = await env.DB.prepare(`
            SELECT culture, rhizome_region as region,
                   COUNT(*) as motif_count,
                   GROUP_CONCAT(DISTINCT colour_primary) as colours
            FROM motifs GROUP BY culture ORDER BY region, culture
          `).all();
          return publicJsonResponse({
            cultures: rows.results,
            total_cultures: rows.results.length,
            attribution: 'Te Pā Tūwatawata — te-pa.org — CC BY-NC-SA 4.0',
          }, 200, 3600);
        } catch (e) {
          return errorResponse(e.message, 500);
        }
      }

      // ── GET /api/motifs/:id ───────────────────────────────────────────
      const motifIdMatch = url.pathname.match(/^\/api\/motifs\/([a-z0-9_]+)$/);
      if (motifIdMatch) {
        const mid  = motifIdMatch[1];
        const lang = url.searchParams.get('lang') || 'en';
        try {
          const m = await env.DB.prepare(`SELECT * FROM motifs WHERE id = ?`).bind(mid).first();
          if (!m) return errorResponse(`Motif '${mid}' not found`, 404);
          return publicJsonResponse({ motif: publicMotif(m, lang), attribution: 'Te Pā Tūwatawata — te-pa.org — CC BY-NC-SA 4.0' }, 200, 3600);
        } catch (e) {
          return errorResponse(e.message, 500);
        }
      }

      // ── GET /api/motifs ───────────────────────────────────────────────
      if (url.pathname === '/api/motifs') {
        const lang    = url.searchParams.get('lang')    || 'en';
        const culture = url.searchParams.get('culture') || null;
        const region  = url.searchParams.get('region')  || null;
        const id      = url.searchParams.get('id')      || null;

        try {
          let sql, bindings;
          if (id) {
            sql = `SELECT * FROM motifs WHERE id = ?`;
            bindings = [id];
          } else if (culture) {
            sql = `SELECT * FROM motifs WHERE culture = ? ORDER BY name_en`;
            bindings = [culture];
          } else if (region) {
            sql = `SELECT * FROM motifs WHERE rhizome_region = ? ORDER BY culture, name_en`;
            bindings = [region];
          } else {
            sql = `SELECT * FROM motifs ORDER BY rhizome_region, culture, name_en`;
            bindings = [];
          }

          const rows = bindings.length
            ? await env.DB.prepare(sql).bind(...bindings).all()
            : await env.DB.prepare(sql).all();

          const motifs = (rows.results || []).map(m => publicMotif(m, lang));

          return publicJsonResponse({
            motifs,
            count: motifs.length,
            filter: { culture, region, id, lang },
            attribution: 'Te Pā Tūwatawata — te-pa.org — CC BY-NC-SA 4.0',
            license: 'CC BY-NC-SA 4.0',
            generated_at: new Date().toISOString(),
          }, 200, 300);
        } catch (e) {
          return errorResponse(e.message, 500);
        }
      }

      // ── GET /api/meme ─────────────────────────────────────────────────
      if (url.pathname === '/api/meme') {
        const id   = url.searchParams.get('id');
        const lang = url.searchParams.get('lang') || 'en';
        if (!id) return errorResponse('Missing required param: id');
        const validLangs = ['en','mi','pt','gn','sm','ar'];
        const safeLang = validLangs.includes(lang) ? lang : 'en';
        const memeUrl = `${CDN}/motifs/memes/meme_${id}_${safeLang}.png`;
        return publicJsonResponse({
          motif_id: id,
          lang: safeLang,
          url: memeUrl,
          download_filename: `tepa-${id}-${safeLang}.png`,
          attribution: 'Te Pā Tūwatawata — te-pa.org — CC BY-NC-SA 4.0',
          share_text: `#TePa #IndigenousSovereignty #DataBack — te-pa.org`,
        }, 200, 3600);
      }

      // ── GET /api/kit ──────────────────────────────────────────────────
      if (url.pathname === '/api/kit') {
        const lang = url.searchParams.get('lang') || 'en';
        const kit  = TEACHING_KITS[lang] || TEACHING_KITS['en'];
        return publicJsonResponse({
          lang,
          language: kit.language,
          pdf_url: kit.pdf,
          all_kits: TEACHING_KITS,
          attribution: 'Te Pā Tūwatawata — te-pa.org — CC BY-NC-SA 4.0',
          license: 'CC BY-NC-SA 4.0 — free to use in educational contexts with attribution',
        }, 200, 3600);
      }

      return errorResponse('Unknown API endpoint. See /api for documentation.', 404);
    }

    // ════════════════════════════════════════════════════════════════════
    // PRIVATE ENDPOINTS — te-pa.org origin only
    // ════════════════════════════════════════════════════════════════════

    // ── POST /track ──────────────────────────────────────────────────────────
    if (request.method === 'POST' && url.pathname === '/track') {
      try {
        const body = await request.json();
        const {
          type = 'view',
          org_id = null,
          org_name = null,
          region = null,
          platform = null,
          lang = 'en',
          motif_key = null,
          session_id = null,
          kit_language = null,
        } = body;

        const kit_lang = kit_language || (type === 'kit_download' ? lang : null);

        const country   = request.cf?.country   || null;
        const cf_region = request.cf?.region    || null;
        const continent = request.cf?.continent || null;
        const latitude  = request.cf?.latitude  || null;
        const longitude = request.cf?.longitude || null;
        const city      = request.cf?.city      || null;
        const timezone  = request.cf?.timezone  || null;
        const referrer  = request.headers.get('Referer')    || null;
        const ua        = request.headers.get('User-Agent') || null;

        await env.DB.prepare(`
          INSERT INTO events
            (type, org_id, org_name, region, platform, lang, motif_key, kit_language,
             country, cf_region, continent, latitude, longitude, city,
             timezone, referrer, session_id, ua, created_at)
          VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        `).bind(
          type, org_id, org_name, region, platform, lang, motif_key, kit_lang,
          country, cf_region, continent, latitude, longitude, city,
          timezone, referrer, session_id, ua
        ).run();

        return jsonResponse({ ok: true }, 200, origin);
      } catch (e) {
        return jsonResponse({ error: e.message }, 500, origin);
      }
    }

    // ── GET /stats ───────────────────────────────────────────────────────────
    if (request.method === 'GET' && url.pathname === '/stats') {
      try {
        const days = parseInt(url.searchParams.get('days') || '30');

        const totals = await env.DB.prepare(`
          SELECT
            COUNT(*) as total,
            SUM(CASE WHEN type='view'         THEN 1 ELSE 0 END) as views,
            SUM(CASE WHEN type='copy'         THEN 1 ELSE 0 END) as copies,
            SUM(CASE WHEN type='share_x'      THEN 1 ELSE 0 END) as shares_x,
            SUM(CASE WHEN type='share_ig'     THEN 1 ELSE 0 END) as shares_ig,
            SUM(CASE WHEN type='share_fb'     THEN 1 ELSE 0 END) as shares_fb,
            SUM(CASE WHEN type='share_tt'     THEN 1 ELSE 0 END) as shares_tt,
            SUM(CASE WHEN type='motif_run'    THEN 1 ELSE 0 END) as motif_runs,
            SUM(CASE WHEN type='download'     THEN 1 ELSE 0 END) as downloads,
            SUM(CASE WHEN type='kit_download' THEN 1 ELSE 0 END) as kit_downloads,
            COUNT(DISTINCT country)    as countries,
            COUNT(DISTINCT session_id) as sessions
          FROM events
          WHERE created_at >= datetime('now', '-' || ? || ' days')
        `).bind(days).first();

        const byOrg = await env.DB.prepare(`
          SELECT org_id, org_name, region,
            COUNT(*) as total,
            SUM(CASE WHEN type='view'         THEN 1 ELSE 0 END) as views,
            SUM(CASE WHEN type='copy'         THEN 1 ELSE 0 END) as copies,
            SUM(CASE WHEN type LIKE 'share_%' THEN 1 ELSE 0 END) as shares
          FROM events
          WHERE org_id IS NOT NULL
            AND created_at >= datetime('now', '-' || ? || ' days')
          GROUP BY org_id ORDER BY total DESC LIMIT 50
        `).bind(days).all();

        const byPlatform = await env.DB.prepare(`
          SELECT platform, COUNT(*) as count FROM events
          WHERE platform IS NOT NULL
            AND created_at >= datetime('now', '-' || ? || ' days')
          GROUP BY platform ORDER BY count DESC
        `).bind(days).all();

        const byLang = await env.DB.prepare(`
          SELECT lang, COUNT(*) as count FROM events
          WHERE lang IS NOT NULL
            AND created_at >= datetime('now', '-' || ? || ' days')
          GROUP BY lang ORDER BY count DESC
        `).bind(days).all();

        const trend = await env.DB.prepare(`
          SELECT strftime('%Y-%m-%dT%H:00:00', created_at) as hour, COUNT(*) as count
          FROM events
          WHERE created_at >= datetime('now', '-2 days')
          GROUP BY hour ORDER BY hour ASC
        `).all();

        return jsonResponse({
          totals,
          by_org:      byOrg.results,
          by_platform: byPlatform.results,
          by_lang:     byLang.results,
          trend:       trend.results,
          generated_at: new Date().toISOString(),
        }, 200, origin);
      } catch (e) {
        return jsonResponse({ error: e.message }, 500, origin);
      }
    }

    // ── GET /kits ────────────────────────────────────────────────────────────
    if (request.method === 'GET' && url.pathname === '/kits') {
      try {
        const days = parseInt(url.searchParams.get('days') || '90');

        const byLang = await env.DB.prepare(`
          SELECT kit_language, lang,
            COUNT(*) as downloads,
            COUNT(DISTINCT country) as countries,
            COUNT(DISTINCT session_id) as sessions
          FROM events
          WHERE type='kit_download' AND created_at >= datetime('now', '-' || ? || ' days')
          GROUP BY kit_language ORDER BY downloads DESC
        `).bind(days).all();

        const byCountry = await env.DB.prepare(`
          SELECT country, continent,
            COUNT(*) as downloads,
            COUNT(DISTINCT kit_language) as kits_accessed
          FROM events
          WHERE type='kit_download' AND created_at >= datetime('now', '-' || ? || ' days')
          GROUP BY country ORDER BY downloads DESC LIMIT 30
        `).bind(days).all();

        const recent = await env.DB.prepare(`
          SELECT kit_language, lang, country, city, continent, created_at, session_id
          FROM events
          WHERE type='kit_download' AND created_at >= datetime('now', '-' || ? || ' days')
          ORDER BY created_at DESC LIMIT 30
        `).bind(days).all();

        const trend = await env.DB.prepare(`
          SELECT strftime('%Y-%m-%d', created_at) as date, kit_language, COUNT(*) as count
          FROM events
          WHERE type='kit_download' AND created_at >= datetime('now', '-' || ? || ' days')
          GROUP BY date, kit_language ORDER BY date DESC
        `).bind(days).all();

        const total = await env.DB.prepare(`
          SELECT COUNT(*) as total FROM events
          WHERE type='kit_download' AND created_at >= datetime('now', '-' || ? || ' days')
        `).bind(days).first();

        return jsonResponse({
          total_kit_downloads: total.total,
          by_language: byLang.results,
          by_country: byCountry.results,
          recent: recent.results,
          trend: trend.results,
          days,
          generated_at: new Date().toISOString(),
        }, 200, origin);
      } catch (e) {
        return jsonResponse({ error: e.message }, 500, origin);
      }
    }

    // ── GET /heatmap ─────────────────────────────────────────────────────────
    if (request.method === 'GET' && url.pathname === '/heatmap') {
      try {
        const days = parseInt(url.searchParams.get('days') || '30');
        const rows = await env.DB.prepare(`
          SELECT country, continent,
            AVG(CAST(latitude  AS REAL)) as lat,
            AVG(CAST(longitude AS REAL)) as lon,
            COUNT(*) as count,
            SUM(CASE WHEN type LIKE 'share_%' OR type='copy' THEN 1 ELSE 0 END) as shares
          FROM events
          WHERE country IS NOT NULL
            AND created_at >= datetime('now', '-' || ? || ' days')
          GROUP BY country ORDER BY count DESC
        `).bind(days).all();
        return jsonResponse({ points: rows.results }, 200, origin);
      } catch (e) {
        return jsonResponse({ error: e.message }, 500, origin);
      }
    }

    // ── GET /live ────────────────────────────────────────────────────────────
    if (request.method === 'GET' && url.pathname === '/live') {
      try {
        const rows = await env.DB.prepare(`
          SELECT type, org_name, region, country, city, platform, lang, kit_language, created_at
          FROM events ORDER BY created_at DESC LIMIT 50
        `).all();
        return jsonResponse({ events: rows.results }, 200, origin);
      } catch (e) {
        return jsonResponse({ error: e.message }, 500, origin);
      }
    }

    // ── GET /connections ─────────────────────────────────────────────────────
    if (request.method === 'GET' && url.pathname === '/connections') {
      try {
        const days = parseInt(url.searchParams.get('days') || '30');
        const rows = await env.DB.prepare(`
          SELECT a.org_id as source_id, a.org_name as source_name,
                 b.org_id as target_id, b.org_name as target_name,
                 COUNT(*) as weight
          FROM events a
          JOIN events b ON a.session_id = b.session_id AND a.org_id < b.org_id
          WHERE a.org_id IS NOT NULL AND b.org_id IS NOT NULL
            AND a.session_id IS NOT NULL
            AND a.created_at >= datetime('now', '-' || ? || ' days')
          GROUP BY a.org_id, b.org_id HAVING weight >= 1
          ORDER BY weight DESC LIMIT 200
        `).bind(days).all();
        return jsonResponse({ connections: rows.results }, 200, origin);
      } catch (e) {
        return jsonResponse({ error: e.message }, 500, origin);
      }
    }

    // ── GET /motifs/cultures ─────────────────────────────────────────────────
    if (request.method === 'GET' && url.pathname === '/motifs/cultures') {
      try {
        const rows = await env.DB.prepare(`
          SELECT culture, rhizome_region,
                 COUNT(*) as count,
                 GROUP_CONCAT(DISTINCT colour_primary) as colours
          FROM motifs GROUP BY culture ORDER BY rhizome_region, culture
        `).all();
        return jsonResponse({ cultures: rows.results }, 200, origin);
      } catch (e) {
        return jsonResponse({ error: e.message }, 500, origin);
      }
    }

    // ── GET /motifs ──────────────────────────────────────────────────────────
    if (request.method === 'GET' && url.pathname === '/motifs') {
      try {
        const culture = url.searchParams.get('culture');
        const region  = url.searchParams.get('region');
        const id      = url.searchParams.get('id');
        const lang    = url.searchParams.get('lang') || 'en';

        let sql, bindings;
        if (id) {
          sql = `SELECT * FROM motifs WHERE id = ?`;
          bindings = [id];
        } else if (culture) {
          sql = `SELECT * FROM motifs WHERE culture = ? ORDER BY name_en`;
          bindings = [culture];
        } else if (region) {
          sql = `SELECT * FROM motifs WHERE rhizome_region = ? ORDER BY culture, name_en`;
          bindings = [region];
        } else {
          sql = `SELECT * FROM motifs ORDER BY rhizome_region, culture, name_en`;
          bindings = [];
        }

        const rows = bindings.length
          ? await env.DB.prepare(sql).bind(...bindings).all()
          : await env.DB.prepare(sql).all();

        const results = (rows.results || []).map(m => {
          const meaning = m[`meaning_${lang}`] || m.meaning_en || '';
          let themes  = [];
          let sources = [];
          try { themes  = JSON.parse(m.political_themes || '[]'); } catch (_) {}
          try { sources = JSON.parse(m.sources          || '[]'); } catch (_) {}
          return { ...m, meaning_active: meaning, political_themes: themes, sources };
        });

        return jsonResponse({
          motifs: results,
          count:  results.length,
          filter: { culture, region, id, lang },
          generated_at: new Date().toISOString(),
        }, 200, origin);
      } catch (e) {
        return jsonResponse({ error: e.message }, 500, origin);
      }
    }

    return jsonResponse({ error: 'Not found' }, 404, origin);
  },
};
