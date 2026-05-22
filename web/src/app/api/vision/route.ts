import { NextResponse } from "next/server";
import { analyzeVision, runAgentChat } from "@/lib/agent";
import type { ModelKey } from "@/lib/models";

export async function POST(request: Request) {
  try {
    const form = await request.formData();
    const image = form.get("image");
    const modelKey = (String(form.get("model") ?? "claude-haiku-4.6")) as ModelKey;
    const autoAct = form.get("autoAct") === "true";
    const prompt = form.get("prompt") ? String(form.get("prompt")) : undefined;

    if (!(image instanceof Blob)) {
      return NextResponse.json({ error: "image required" }, { status: 400 });
    }

    const buffer = Buffer.from(await image.arrayBuffer());
    const base64 = buffer.toString("base64");
    const mimeType = image.type || "image/jpeg";

    const vision = await analyzeVision({ modelKey, imageBase64: base64, mimeType, prompt });

    let toolCalls: { name: string; result: unknown }[] = [];
    if (autoAct && vision.analysis) {
      const followUp = await runAgentChat({
        modelKey,
        messages: [
          {
            role: "user",
            content: `Vision analysis:\n${vision.analysis}\n\nExecute appropriate home tools now.`,
          },
        ],
        maxSteps: 4,
      });
      toolCalls = followUp.toolCalls;
      return NextResponse.json({
        analysis: vision.analysis,
        reply: followUp.reply,
        toolCalls,
      });
    }

    return NextResponse.json({
      analysis: vision.analysis,
      toolCalls: vision.toolCalls,
    });
  } catch (error) {
    const msg = error instanceof Error ? error.message : "vision failed";
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
