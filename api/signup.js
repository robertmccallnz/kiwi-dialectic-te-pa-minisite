// POST /api/signup
// Body: { access_token, display_name, pepeha?, substack_confirmed }
// Creates the learners row for a freshly-authenticated user.
//
// Flow:
//   1. Visitor enters email on /auth/signup → Supabase sends magic link.
//   2. Visitor clicks link → lands on /auth/callback with a session.
//   3. /auth/callback collects display_name + Substack confirm + pepeha,
//      then calls this endpoint with their access_token to write the
//      learners row (with a generated slug).

import { userClient, adminClient } from './_supabase.js';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'method not allowed' });
  }

  const { access_token, display_name, pepeha, substack_confirmed } = req.body || {};

  if (!access_token || !display_name) {
    return res.status(400).json({ error: 'access_token and display_name required' });
  }
  if (!substack_confirmed) {
    return res.status(400).json({
      error: 'substack_confirmed must be true — please confirm you have subscribed to The Kiwi Dialectic',
    });
  }

  // Get the authenticated user from their JWT
  const u = userClient(access_token);
  const { data: userResp, error: userErr } = await u.auth.getUser(access_token);
  if (userErr || !userResp?.user) {
    return res.status(401).json({ error: 'invalid session' });
  }
  const { id, email } = userResp.user;

  // Generate a unique slug via the admin client (RLS would block a self-read otherwise)
  const admin = adminClient();
  const { data: slugRow, error: slugErr } = await admin.rpc('make_unique_slug', {
    base: display_name,
  });
  if (slugErr) {
    return res.status(500).json({ error: 'slug generation failed', detail: slugErr.message });
  }

  // Insert the learners row using the user's client so RLS sees auth.uid() = id
  const { data, error } = await u
    .from('learners')
    .insert({
      id,
      email,
      display_name,
      slug: slugRow,
      pepeha: pepeha || null,
      substack_confirmed: !!substack_confirmed,
      profile_public: true,
    })
    .select()
    .single();

  if (error) {
    if (error.code === '23505') {
      return res.status(409).json({ error: 'learner already exists', already_exists: true });
    }
    return res.status(500).json({ error: 'insert failed', detail: error.message });
  }

  return res.status(200).json({ ok: true, learner: data });
}
