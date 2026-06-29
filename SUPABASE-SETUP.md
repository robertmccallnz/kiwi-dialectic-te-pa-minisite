# Te Pā Tūwatawata — Supabase setup (15 min, one-time)

The login + badge system uses **Supabase Auth** (free tier — no card needed,
50k MAUs included) for magic-link login and **Supabase Postgres** for storing
learners and module completions.

## 1 · Create the Supabase project

1. Sign in at <https://supabase.com> (use your Google / GitHub).
2. **New Project** → pick the closest region (Sydney = `ap-southeast-2`).
3. Set a strong database password and save it. You won't need it day-to-day.
4. Wait ~2 minutes for the project to provision.

## 2 · Run the schema

1. Open the new project → **SQL Editor** (left sidebar).
2. Open `db/schema.sql` from this repo and paste the contents into a new query.
3. Click **Run**. You should see "Success" with no errors.

## 3 · Configure Auth (magic link)

1. Go to **Authentication → Providers**.
2. **Email** is enabled by default — make sure:
   - "Enable email signups" is **on**.
   - "Confirm email" is **on**.
   - "Secure email change" can stay default.
3. Go to **Authentication → URL Configuration**.
   - **Site URL**: `https://te-pa.org`
   - **Redirect URLs** (add each):
     - `https://te-pa.org/auth/finish/`
     - `https://te-pa.org/auth/finish`
     - `https://te-pa.org/profile/`
     - `https://te-pa.org/profile`
     - For local testing: `http://localhost:3000/auth/finish/` etc.

## 4 · Customise the magic-link email (recommended)

**Authentication → Email Templates → Magic Link**

Replace the body with:

```html
<h2>Kia ora — sign in to Te Pā Tūwatawata</h2>
<p>Click below to finish signing in and pick up where you left off.</p>
<p><a href="{{ .ConfirmationURL }}">Open Te Pā Tūwatawata</a></p>
<p style="color:#666;font-size:.85rem">If you didn't request this, you can ignore it.</p>
```

## 5 · Grab the keys

**Settings → API**:

- **Project URL** → goes into `SUPABASE_URL`
- **anon public key** → goes into `SUPABASE_ANON_KEY` (safe to ship to browser)
- **service_role secret** → goes into `SUPABASE_SERVICE_ROLE_KEY` (server only — never put in browser!)

## 6 · Add to Vercel

In the Vercel dashboard for `te-pa.org`:

**Project Settings → Environment Variables**, add:

| Name                          | Value                  | Environments |
|-------------------------------|------------------------|--------------|
| `SUPABASE_URL`                | (from step 5)          | Production, Preview, Development |
| `SUPABASE_ANON_KEY`           | (from step 5)          | Production, Preview, Development |
| `SUPABASE_SERVICE_ROLE_KEY`   | (from step 5)          | Production, Preview, Development |

Then **wire the public anon values into the front-end** by editing the inline config block on each page. There are placeholders right now reading `TODO_SUPABASE_URL` / `TODO_SUPABASE_ANON_KEY` in:

- `index.html`
- `auth/signup/index.html`
- `auth/login/index.html`
- `auth/finish/index.html`
- `profile/index.html`
- `learners/index.html`
- `modules/module-1.html` … `module-6.html`

Replace those two strings with the real values.

> Why inline? The site is static (no SSR layer to inject values), and the anon key is safe to ship to browsers — RLS does the security.

## 7 · Test locally

```bash
npm install
npx vercel dev   # serves /api/* serverless functions + the static site
```

Open <http://localhost:3000/auth/signup/> and step through the flow.

## 8 · Deploy

`git push` to a branch and merge as usual. Vercel will rebuild.

## 9 · Find your roster

Back in Supabase SQL Editor:

```sql
select * from learner_roster order by created_at desc;
```

That's everyone who has signed up + how many modules they've finished + their slug.
