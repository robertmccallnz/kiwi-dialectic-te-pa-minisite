// Shared Supabase client factory for serverless functions.
// Reads env vars from Vercel:
//   SUPABASE_URL                — public, project URL
//   SUPABASE_ANON_KEY           — public, anon key (used for user-context calls)
//   SUPABASE_SERVICE_ROLE_KEY   — secret, server-only (used for admin actions)

import { createClient } from '@supabase/supabase-js';

export function userClient(accessToken) {
  // Uses the visitor's JWT so RLS policies apply correctly.
  const client = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_ANON_KEY,
    {
      global: accessToken
        ? { headers: { Authorization: `Bearer ${accessToken}` } }
        : {},
      auth: { persistSession: false, autoRefreshToken: false },
    }
  );
  return client;
}

export function adminClient() {
  // Bypasses RLS. Use only for slug generation / roster reads.
  return createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_SERVICE_ROLE_KEY,
    { auth: { persistSession: false, autoRefreshToken: false } }
  );
}

export function bearerFrom(req) {
  const h = req.headers.authorization || req.headers.Authorization || '';
  return h.startsWith('Bearer ') ? h.slice(7) : null;
}
