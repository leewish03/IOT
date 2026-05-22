import { NextResponse } from "next/server";
import OpenAI from "openai";
import { runAgentChat } from "@/lib/agent";
import type { ModelKey } from "@/lib/models";

export async function POST(request: Request) {
  try {
    const form = await request.formData();
    const audio = form.get("audio");
    const modelKey = (String(form.get("model") ?? "claude-haiku-4.6")) as ModelKey;

    if (!(audio instanceof Blob)) {
      return NextResponse.json({ error: "audio file required" }, { status: 400 });
    }
    if (!process.env.OPENAI_API_KEY) {
      return NextResponse.json({ error: "OPENAI_API_KEY required for speech-to-text" }, { status: 503 });
    }

    const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
    const file = new File([await audio.arrayBuffer()], "voice.webm", { type: audio.type || "audio/webm" });
    const transcription = await openai.audio.transcriptions.create({
      file,
      model: process.env.OPENAI_STT_MODEL ?? "whisper-1",
    });

    const text = transcription.text?.trim() ?? "";
    if (!text) {
      return NextResponse.json({ error: "empty transcription" }, { status: 400 });
    }

    const agent = await runAgentChat({
      modelKey,
      messages: [{ role: "user", content: text }],
    });

    return NextResponse.json({
      transcript: text,
      reply: agent.reply,
      toolCalls: agent.toolCalls,
    });
  } catch (error) {
    const msg = error instanceof Error ? error.message : "voice failed";
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
