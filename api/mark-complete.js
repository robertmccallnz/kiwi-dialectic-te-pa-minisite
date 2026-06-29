// POST /api/mark-complete
// Body: { access_token, module_number: 1..6 }
// Records that the authenticated learner has finished a module.
// Returns the updated badge list.

import { userClient } from './_supabase.js';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'method not allowed' });
  }

  const { access_token, module_number } = req.body || {};
  if (!access_token || !Number.isInteger(module_number)) {
    return res.status(400).json({ error: 'access_token and module_number required' });
  }
  if (module_number < 1 || module_number > 6) {
    return res.status(400).json({ error: 'module_number must be between 1 and 6' });
  }

  const u = userClient(access_token);
  const { data: userResp, error: userErr } = await u.auth.getUser(access_token);
  if (userErr || !userResp?.user) {
    return res.status(401).json({ error: 'invalid session' });
  }
  const learner_id = userResp.user.id;

  // Insert ignoring duplicates (already complete is fine)
  const { error: insErr } = await u
    .from('completions')
    .insert({ learner_id, module_number })
    .select()
    .maybeSingle();

  if (insErr && insErr.code !== '23505') {
    return res.status(500).json({ error: 'insert failed', detail: insErr.message });
  }

  // Re-read all completions for the response
  const { data: comps, error: readErr } = await u
    .from('completions')
    .select('module_number, completed_at')
    .eq('learner_id', learner_id)
    .order('module_number');

  if (readErr) {
    return res.status(500).json({ error: 'read failed', detail: readErr.message });
  }

  return res.status(200).json({ ok: true, completions: comps });
}
