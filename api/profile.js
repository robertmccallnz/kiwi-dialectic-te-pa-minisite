// GET /api/profile?slug=jane-doe   — public profile (only if profile_public)
// GET /api/profile?me=1            — own profile (requires bearer token)
// POST /api/profile                — update own profile (display_name, pepeha, profile_public)
//   Body: { access_token, display_name?, pepeha?, profile_public? }

import { userClient, adminClient, bearerFrom } from './_supabase.js';

export default async function handler(req, res) {
  if (req.method === 'GET') {
    const { slug, me } = req.query;

    if (me === '1') {
      const token = bearerFrom(req);
      if (!token) return res.status(401).json({ error: 'bearer token required' });
      const u = userClient(token);
      const { data: ur } = await u.auth.getUser(token);
      if (!ur?.user) return res.status(401).json({ error: 'invalid session' });

      const { data: learner } = await u
        .from('learners').select('*').eq('id', ur.user.id).maybeSingle();
      const { data: comps } = await u
        .from('completions').select('module_number, completed_at')
        .eq('learner_id', ur.user.id).order('module_number');

      return res.status(200).json({ learner, completions: comps || [] });
    }

    if (!slug) return res.status(400).json({ error: 'slug or me=1 required' });

    // Public read — uses admin client so we can include private check + 404 cleanly
    const admin = adminClient();
    const { data: learner } = await admin
      .from('learners')
      .select('display_name, slug, pepeha, profile_public, created_at')
      .eq('slug', slug)
      .maybeSingle();
    if (!learner || !learner.profile_public) {
      return res.status(404).json({ error: 'not found' });
    }
    const { data: comps } = await admin
      .from('completions')
      .select('module_number, completed_at')
      .eq('learner_id', (await admin.from('learners').select('id').eq('slug', slug).single()).data.id)
      .order('module_number');

    return res.status(200).json({ learner, completions: comps || [] });
  }

  if (req.method === 'POST') {
    const { access_token, display_name, pepeha, profile_public } = req.body || {};
    if (!access_token) return res.status(400).json({ error: 'access_token required' });

    const u = userClient(access_token);
    const { data: ur } = await u.auth.getUser(access_token);
    if (!ur?.user) return res.status(401).json({ error: 'invalid session' });

    const update = { updated_at: new Date().toISOString() };
    if (typeof display_name === 'string' && display_name.trim()) update.display_name = display_name.trim();
    if (typeof pepeha === 'string') update.pepeha = pepeha || null;
    if (typeof profile_public === 'boolean') update.profile_public = profile_public;

    const { data, error } = await u
      .from('learners').update(update).eq('id', ur.user.id).select().single();

    if (error) return res.status(500).json({ error: error.message });
    return res.status(200).json({ ok: true, learner: data });
  }

  return res.status(405).json({ error: 'method not allowed' });
}
