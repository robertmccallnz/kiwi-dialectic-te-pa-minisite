// GET /api/learners?limit=24&offset=0
// Public list of public-opt-in learners for /learners directory.

import { adminClient } from './_supabase.js';

export default async function handler(req, res) {
  if (req.method !== 'GET') return res.status(405).json({ error: 'method not allowed' });

  const limit  = Math.min(100, parseInt(req.query.limit  || '24', 10));
  const offset = Math.max(0,   parseInt(req.query.offset || '0',  10));

  const admin = adminClient();

  // List of public learners with their module count
  const { data, error } = await admin
    .from('learner_roster')
    .select('slug, display_name, modules_completed, modules')
    .eq('profile_public', true)
    .order('modules_completed', { ascending: false })
    .order('created_at', { ascending: false })
    .range(offset, offset + limit - 1);

  if (error) return res.status(500).json({ error: error.message });
  return res.status(200).json({ learners: data || [] });
}
