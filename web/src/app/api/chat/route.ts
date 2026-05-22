import { NextResponse } from "next/server";
import { runAgentChat } from "@/lib/agent";
import type { ModelKey } from "@/lib/models";
import { createClient } from "@/lib/supabase/server";

export async function POST(request: Request) {
  try {
    const hasSupabase =
      Boolean(process.env.NEXT_PUBLIC_SUPABASE_URL) &&
      Boolean(process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY);

    let supabase: Awaited<ReturnType<typeof createClient>> | null = null;
    let userId: string | null = null;

    if (hasSupabase) {
      supabase = await createClient();
      const {
        data: { user },
      } = await supabase.auth.getUser();
      if (!user) {
        return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
      }
      userId = user.id;
    }

    const body = await request.json();
    const message = String(body.message ?? "").trim();
    const modelKey = (body.model ?? "claude-haiku-4.6") as ModelKey;
    const history = Array.isArray(body.history) ? body.history : [];

    if (!message) {
      return NextResponse.json({ error: "message is required" }, { status: 400 });
    }

    if (!process.env.OPENAI_API_KEY && modelKey === "gpt-5.4-nano") {
      return NextResponse.json({ error: "OPENAI_API_KEY not configured" }, { status: 503 });
    }
    if (!process.env.ANTHROPIC_API_KEY && modelKey === "claude-haiku-4.6") {
      return NextResponse.json({ error: "ANTHROPIC_API_KEY not configured" }, { status: 503 });
    }

    const messages = [
      ...history.map((m: { role: string; content: string }) => ({
        role: m.role as "user" | "assistant",
        content: String(m.content),
      })),
      { role: "user" as const, content: message },
    ];

    const result = await runAgentChat({ modelKey, messages });

    if (supabase && userId) {
      await supabase.from("chat_messages").insert([
        {
          role: "user",
          content: message,
          model_key: modelKey,
          user_id: userId,
        },
        {
          role: "assistant",
          content: result.reply,
          model_key: modelKey,
          tool_calls: result.toolCalls,
          user_id: userId,
        },
      ]);
    }

    return NextResponse.json(result);
  } catch (error) {
    const msg = error instanceof Error ? error.message : "chat failed";
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
