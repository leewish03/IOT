import type { SupabaseClient } from "@supabase/supabase-js";

export async function persistChatTurn(
  supabase: SupabaseClient,
  userId: string,
  modelKey: string,
  userContent: string,
  assistantContent: string,
  toolCalls?: unknown,
) {
  await supabase.from("chat_messages").insert([
    { user_id: userId, role: "user", content: userContent, model_key: modelKey },
    {
      user_id: userId,
      role: "assistant",
      content: assistantContent,
      model_key: modelKey,
      tool_calls: toolCalls ?? null,
    },
  ]);
}

export async function persistSceneEvent(
  supabase: SupabaseClient,
  userId: string,
  scene: Record<string, unknown>,
) {
  await supabase.from("scene_events").insert({ user_id: userId, scene_json: scene });
}
