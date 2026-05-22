import { NextResponse } from "next/server";
import { analyzeSceneImage } from "@/lib/orchestrator-client";

export async function POST(request: Request) {
  try {
    const form = await request.formData();
    const file = form.get("file") ?? form.get("image");
    if (!(file instanceof Blob)) {
      return NextResponse.json({ error: "file or image required" }, { status: 400 });
    }
    const scene = await analyzeSceneImage(file);
    return NextResponse.json({ scene });
  } catch (error) {
    const msg = error instanceof Error ? error.message : "scene analyze failed";
    return NextResponse.json({ error: msg }, { status: 502 });
  }
}
