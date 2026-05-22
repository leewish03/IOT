alter table public.vision_events
  add column if not exists scene_json jsonb;
