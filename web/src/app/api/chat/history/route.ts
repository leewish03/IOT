import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

export async function GET(request: Request) {
  if (!process.env.NEXT_PUBLIC_SUPABASE_URL || !process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY) {
    return NextResponse.json({ messages: [] });
  }

  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const limit = Math.min(Number(new URL(request.url).searchParams.get("limit") ?? "40"), 100);

  const { data, error } = await supabase
    .from("chat_messages")
    .select("role, content, created_at")
    .eq("user_id", user.id)
    .order("created_at", { ascending: true })
    .limit(limit);

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  const messages = (data ?? []).map((row) => ({
    role: row.role as "user" | "assistant",
    content: row.content as string,
  }));

  return NextResponse.json({ messages });
}
