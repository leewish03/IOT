import { NextResponse } from "next/server";
import { callTool, healthCheck, readResource } from "@/lib/orchestrator-client";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const action = searchParams.get("action");
  try {
    if (action === "health") {
      return NextResponse.json(await healthCheck());
    }
    const uri = searchParams.get("uri");
    if (uri) {
      return NextResponse.json(await readResource(uri));
    }
    return NextResponse.json({ error: "uri or action=health required" }, { status: 400 });
  } catch (error) {
    const msg = error instanceof Error ? error.message : "request failed";
    return NextResponse.json({ error: msg }, { status: 502 });
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const name = String(body.tool ?? "");
    const args = (body.args ?? {}) as Record<string, unknown>;
    if (!name) {
      return NextResponse.json({ error: "tool name required" }, { status: 400 });
    }
    return NextResponse.json(await callTool(name, args));
  } catch (error) {
    const msg = error instanceof Error ? error.message : "tool call failed";
    return NextResponse.json({ error: msg }, { status: 502 });
  }
}
