import { NextResponse } from "next/server";
import { judgeSceneFromMetadata, runAgentChat } from "@/lib/agent";
import { analyzeSceneImage } from "@/lib/orchestrator-client";
import type { ModelKey } from "@/lib/models";
import { createClient } from "@/lib/supabase/server";

async function supabaseOptional() {
  if (!process.env.NEXT_PUBLIC_SUPABASE_URL || !process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY) {
    return null;
  }
  return createClient();
}

export async function POST(request: Request) {
  try {
    const form = await request.formData();
    const image = form.get("image");
    const modelKey = (String(form.get("model") ?? "claude-haiku-4.6")) as ModelKey;
    const autoAct = form.get("autoAct") === "true";
    const prompt = form.get("prompt") ? String(form.get("prompt")) : undefined;

    let scene: Record<string, unknown>;

    if (image instanceof Blob && image.size > 0) {
      scene = await analyzeSceneImage(image);
    } else {
      const useLive = form.get("live") === "true";
      if (!useLive) {
        return NextResponse.json({ error: "image required or set live=true" }, { status: 400 });
      }
      const { getSceneLatest } = await import("@/lib/orchestrator-client");
      const latest = await getSceneLatest();
      if (!latest) {
        return NextResponse.json(
          { error: "No live scene yet. Enable CAMERA_DEVICE on Pi or upload a photo." },
          { status: 404 },
        );
      }
      scene = latest;
    }

    const judgment = await judgeSceneFromMetadata({ modelKey, scene, prompt });

    const supabase = await supabaseOptional();
    if (supabase) {
      const {
        data: { user },
      } = await supabase.auth.getUser();
      if (user) {
        await supabase.from("vision_events").insert({
          user_id: user.id,
          analysis: judgment.analysis,
          tool_calls: null,
          scene_json: scene,
        });
      }
    }

    let toolCalls: { name: string; result: unknown }[] = [];
    if (autoAct && judgment.analysis) {
      const followUp = await runAgentChat({
        modelKey,
        messages: [
          {
            role: "user",
            content: `OpenCV 장면 메타:\n${JSON.stringify(scene, null, 2)}\n\nAI 판단:\n${judgment.analysis}\n\n적절한 home 도구를 실행하세요.`,
          },
        ],
        maxSteps: 4,
      });
      toolCalls = followUp.toolCalls;
      return NextResponse.json({
        scene,
        analysis: judgment.analysis,
        reply: followUp.reply,
        toolCalls,
      });
    }

    return NextResponse.json({
      scene,
      analysis: judgment.analysis,
      toolCalls: judgment.toolCalls,
    });
  } catch (error) {
    const msg = error instanceof Error ? error.message : "vision failed";
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
