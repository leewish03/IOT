import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";
import type { ModelKey } from "@/lib/models";

async function requireUser() {
  if (!process.env.NEXT_PUBLIC_SUPABASE_URL || !process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY) {
    return { error: NextResponse.json({ error: "Supabase not configured" }, { status: 503 }) };
  }
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) {
    return { error: NextResponse.json({ error: "Unauthorized" }, { status: 401 }) };
  }
  return { supabase, user };
}

export async function GET() {
  const ctx = await requireUser();
  if ("error" in ctx && ctx.error) return ctx.error;
  const { supabase, user } = ctx as { supabase: Awaited<ReturnType<typeof createClient>>; user: { id: string } };

  const { data } = await supabase
    .from("user_settings")
    .select("preferred_model, ai_auto_mode")
    .eq("user_id", user.id)
    .maybeSingle();

  return NextResponse.json({
    preferred_model: (data?.preferred_model as ModelKey) ?? "claude-haiku-4.6",
    ai_auto_mode: data?.ai_auto_mode ?? false,
  });
}

export async function PATCH(request: Request) {
  const ctx = await requireUser();
  if ("error" in ctx && ctx.error) return ctx.error;
  const { supabase, user } = ctx as { supabase: Awaited<ReturnType<typeof createClient>>; user: { id: string } };

  const body = await request.json();
  const preferred_model = body.preferred_model ? String(body.preferred_model) : undefined;
  const ai_auto_mode = typeof body.ai_auto_mode === "boolean" ? body.ai_auto_mode : undefined;

  const { data: existing } = await supabase
    .from("user_settings")
    .select("id")
    .eq("user_id", user.id)
    .maybeSingle();

  const patch: Record<string, unknown> = { updated_at: new Date().toISOString() };
  if (preferred_model) patch.preferred_model = preferred_model;
  if (ai_auto_mode !== undefined) patch.ai_auto_mode = ai_auto_mode;

  if (existing?.id) {
    await supabase.from("user_settings").update(patch).eq("user_id", user.id);
  } else {
    await supabase.from("user_settings").insert({
      user_id: user.id,
      preferred_model: preferred_model ?? "claude-haiku-4.6",
      ai_auto_mode: ai_auto_mode ?? false,
    });
  }

  return NextResponse.json({ ok: true });
}
