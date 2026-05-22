-- Scene snapshots from vision / room analysis (optional persistence)

create table if not exists public.scene_events (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users (id) on delete set null,
  scene_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

alter table public.scene_events enable row level security;

create policy "scene_events_own" on public.scene_events
  for all using (auth.uid() = user_id);
