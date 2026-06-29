// ─── Te Pā Tūwatawata — auth + completions client ──────────────────────────
// Lightweight wrapper around Supabase Auth (magic link) + the /api routes.
//
// Loaded by /auth/signup, /auth/login, /auth/callback, /profile, /learners/,
// and every modules/module-*.html "Mark complete" button.
//
// Expects window.TE_PA_PUBLIC_CONFIG set inline before this script loads:
//   window.TE_PA_PUBLIC_CONFIG = {
//     supabaseUrl: 'https://xxxx.supabase.co',
//     supabaseAnonKey: 'eyJ...'
//   };

(() => {
  const cfg = window.TE_PA_PUBLIC_CONFIG;
  if (!cfg || !cfg.supabaseUrl || !cfg.supabaseAnonKey) {
    console.warn('[te-pa-auth] missing TE_PA_PUBLIC_CONFIG — auth disabled');
    return;
  }

  // Lazy-load supabase-js from a pinned CDN. CSP allows cdn.jsdelivr.net.
  const loadSupabase = () => new Promise((resolve, reject) => {
    if (window.supabase?.createClient) return resolve(window.supabase);
    const s = document.createElement('script');
    s.src = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.0/dist/umd/supabase.js';
    s.onload = () => resolve(window.supabase);
    s.onerror = () => reject(new Error('supabase-js failed to load'));
    document.head.appendChild(s);
  });

  let clientPromise = null;
  function client() {
    if (!clientPromise) {
      clientPromise = loadSupabase().then(({ createClient }) =>
        createClient(cfg.supabaseUrl, cfg.supabaseAnonKey, {
          auth: {
            persistSession: true,
            autoRefreshToken: true,
            detectSessionInUrl: true,
            storage: window.localStorage,
            storageKey: 'te-pa-auth',
          },
        })
      );
    }
    return clientPromise;
  }

  // ─── Public API ──────────────────────────────────────────────────────────
  window.TePa = {
    // Returns { session, user } or { session: null, user: null }
    async getSession() {
      const c = await client();
      const { data: { session } } = await c.auth.getSession();
      return { session, user: session?.user || null };
    },

    // Send magic link to email. redirectTo defaults to /auth/callback.
    async sendMagicLink(email, redirectTo = '/auth/callback') {
      const c = await client();
      const { error } = await c.auth.signInWithOtp({
        email,
        options: {
          emailRedirectTo: new URL(redirectTo, window.location.origin).toString(),
          shouldCreateUser: true,
        },
      });
      if (error) throw error;
      return { ok: true };
    },

    async signOut() {
      const c = await client();
      await c.auth.signOut();
    },

    // Completes signup by writing the learners row.
    async finishSignup({ display_name, pepeha, substack_confirmed }) {
      const { session } = await this.getSession();
      if (!session) throw new Error('not signed in');
      const r = await fetch('/api/signup', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          access_token: session.access_token,
          display_name,
          pepeha,
          substack_confirmed,
        }),
      });
      const j = await r.json();
      if (!r.ok && !j.already_exists) throw new Error(j.error || 'signup failed');
      return j;
    },

    async myProfile() {
      const { session } = await this.getSession();
      if (!session) return null;
      const r = await fetch('/api/profile?me=1', {
        headers: { authorization: `Bearer ${session.access_token}` },
      });
      if (!r.ok) return null;
      return r.json();
    },

    async updateProfile({ display_name, pepeha, profile_public }) {
      const { session } = await this.getSession();
      if (!session) throw new Error('not signed in');
      const r = await fetch('/api/profile', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          access_token: session.access_token,
          display_name,
          pepeha,
          profile_public,
        }),
      });
      const j = await r.json();
      if (!r.ok) throw new Error(j.error || 'update failed');
      return j;
    },

    async markComplete(module_number) {
      const { session } = await this.getSession();
      if (!session) throw new Error('not signed in');
      const r = await fetch('/api/mark-complete', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          access_token: session.access_token,
          module_number,
        }),
      });
      const j = await r.json();
      if (!r.ok) throw new Error(j.error || 'mark failed');
      return j;
    },

    async publicProfile(slug) {
      const r = await fetch(`/api/profile?slug=${encodeURIComponent(slug)}`);
      if (!r.ok) return null;
      return r.json();
    },

    async listLearners({ limit = 24, offset = 0 } = {}) {
      const r = await fetch(`/api/learners?limit=${limit}&offset=${offset}`);
      if (!r.ok) return { learners: [] };
      return r.json();
    },
  };

  // ─── Nav helper: shows "Sign in" or "Profile" link ───────────────────────
  document.addEventListener('DOMContentLoaded', async () => {
    const slots = document.querySelectorAll('[data-te-pa-auth-slot]');
    if (!slots.length) return;
    const { user } = await window.TePa.getSession();
    slots.forEach((slot) => {
      slot.innerHTML = user
        ? '<a href="/profile/">My profile</a>'
        : '<a href="/auth/login/">Sign in</a>';
    });
  });
})();
