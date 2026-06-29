-- ────────────────────────────────────────────────────────────────────────────
-- Te Pā Tūwatawata — learner login + named badges schema
-- Run this in your Supabase project SQL editor.
-- Free tier is more than enough for the foreseeable cohort.
-- ────────────────────────────────────────────────────────────────────────────

-- ─── Learners ────────────────────────────────────────────────────────────────
-- One row per person who signs up. Linked to Supabase auth.users via id.
create table if not exists public.learners (
  id            uuid primary key references auth.users(id) on delete cascade,
  email         text unique not null,
  display_name  text not null,
  slug          text unique not null,              -- e.g. 'jane-doe' for /learners/jane-doe
  pepeha        text,                              -- optional whakapapa / where they're from
  substack_confirmed boolean not null default false,  -- honour-system "yes I subscribed"
  profile_public boolean not null default true,   -- public-by-default badge wall
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

create index if not exists learners_slug_idx on public.learners(slug);
create index if not exists learners_public_idx on public.learners(profile_public) where profile_public = true;

-- ─── Module completions ─────────────────────────────────────────────────────
-- One row per (learner, module) pair when they mark a module complete.
-- Badges are derived from this table — no separate badge table needed.
create table if not exists public.completions (
  id            bigserial primary key,
  learner_id    uuid not null references public.learners(id) on delete cascade,
  module_number int  not null check (module_number between 1 and 6),
  completed_at  timestamptz not null default now(),
  unique (learner_id, module_number)
);

create index if not exists completions_learner_idx on public.completions(learner_id);

-- ─── Magic-link tokens ──────────────────────────────────────────────────────
-- We let Supabase Auth handle the actual magic-link flow (built in, free).
-- No custom token table needed.

-- ─── Row-level security ─────────────────────────────────────────────────────
alter table public.learners    enable row level security;
alter table public.completions enable row level security;

-- Anyone can read a public learner profile (for /learners/[slug])
drop policy if exists "learners are publicly readable if opted in" on public.learners;
create policy "learners are publicly readable if opted in"
  on public.learners for select
  using (profile_public = true);

-- A learner can always read their own row
drop policy if exists "learners can read own row" on public.learners;
create policy "learners can read own row"
  on public.learners for select
  using (auth.uid() = id);

-- A learner can update their own row (display_name, pepeha, profile_public, substack_confirmed)
drop policy if exists "learners can update own row" on public.learners;
create policy "learners can update own row"
  on public.learners for update
  using (auth.uid() = id);

-- A learner can insert their own row at signup
drop policy if exists "learners can insert own row" on public.learners;
create policy "learners can insert own row"
  on public.learners for insert
  with check (auth.uid() = id);

-- Completions are public-readable only when the linked learner is public
drop policy if exists "completions readable when learner is public" on public.completions;
create policy "completions readable when learner is public"
  on public.completions for select
  using (
    exists (
      select 1 from public.learners l
      where l.id = completions.learner_id and l.profile_public = true
    )
    or auth.uid() = learner_id
  );

-- A learner can only insert their own completions
drop policy if exists "learners can mark own modules complete" on public.completions;
create policy "learners can mark own modules complete"
  on public.completions for insert
  with check (auth.uid() = learner_id);

-- ─── Admin view (for you, Robert) ───────────────────────────────────────────
-- Easy roster query: every learner + how many modules they've finished + which.
create or replace view public.learner_roster as
select
  l.id,
  l.email,
  l.display_name,
  l.slug,
  l.substack_confirmed,
  l.profile_public,
  l.created_at,
  count(c.id) as modules_completed,
  array_agg(c.module_number order by c.module_number) filter (where c.id is not null) as modules
from public.learners l
left join public.completions c on c.learner_id = l.id
group by l.id;

-- ─── Slug uniqueness helper ────────────────────────────────────────────────
-- Generates a slug from display_name; appends -2, -3, etc. on collision.
create or replace function public.make_unique_slug(base text)
returns text language plpgsql as $$
declare
  candidate text;
  n int := 1;
begin
  candidate := regexp_replace(lower(base), '[^a-z0-9]+', '-', 'g');
  candidate := trim(both '-' from candidate);
  if candidate = '' then candidate := 'kaitiaki'; end if;
  while exists (select 1 from public.learners where slug = candidate) loop
    n := n + 1;
    candidate := regexp_replace(lower(base), '[^a-z0-9]+', '-', 'g') || '-' || n;
    candidate := trim(both '-' from candidate);
  end loop;
  return candidate;
end $$;
