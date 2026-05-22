import { getSceneLatest } from "@/lib/orchestrator-client";

export const dynamic = "force-dynamic";

/** SSE proxy: polls orchestrator /scene/latest (Pi camera or last upload). */
export async function GET(request: Request) {
  const intervalMs = Number(new URL(request.url).searchParams.get("interval") ?? "1000");
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      const send = (event: string, data: unknown) => {
        controller.enqueue(encoder.encode(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`));
      };

      send("ready", { ok: true });

      const tick = async () => {
        try {
          const scene = await getSceneLatest();
          send("scene", { scene });
        } catch (e) {
          send("error", { message: e instanceof Error ? e.message : "poll failed" });
        }
      };

      await tick();
      const id = setInterval(tick, Math.max(500, intervalMs));

      request.signal.addEventListener("abort", () => {
        clearInterval(id);
        controller.close();
      });
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
    },
  });
}
