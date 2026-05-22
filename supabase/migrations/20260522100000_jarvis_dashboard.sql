-- Jarvis dashboard: settings + chat log (optional persistence)

create table if not exists public.user_settings (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users (id) on delete cascade,
  preferred_model text not null default 'claude-haiku-4.6',
  ai_auto_mode boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.chat_messages (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users (id) on delete set null,
  role text not null check (role in ('user', 'assistant', 'system')),
  content text not null,
  model_key text,
  tool_calls jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.vision_events (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users (id) on delete set null,
  analysis text,
  tool_calls jsonb,
  created_at timestamptz not null default now()
);

alter table public.user_settings enable row level security;
alter table public.chat_messages enable row level security;
alter table public.vision_events enable row level security;

create policy "user_settings_own" on public.user_settings
  for all using (auth.uid() = user_id);

create policy "chat_messages_own" on public.chat_messages
  for all using (auth.uid() = user_id);

create policy "vision_events_own" on public.vision_events
  for all using (auth.uid() = user_id);

-- Service role bypasses RLS; anon cannot read without auth.
