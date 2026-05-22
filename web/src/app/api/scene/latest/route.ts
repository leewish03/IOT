import { NextResponse } from "next/server";
import { getSceneLatest } from "@/lib/orchestrator-client";

export async function GET() {
  try {
    const scene = await getSceneLatest();
    if (!scene) {
      return NextResponse.json({ scene: null }, { status: 404 });
    }
    return NextResponse.json({ scene });
  } catch (error) {
    const msg = error instanceof Error ? error.message : "scene latest failed";
    return NextResponse.json({ error: msg }, { status: 502 });
  }
}
