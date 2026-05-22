const baseUrl = process.env.ORCHESTRATOR_URL ?? "http://127.0.0.1:8080";
const token = process.env.ORCHESTRATOR_TOKEN ?? "change-me";

function headers(): HeadersInit {
  const h: HeadersInit = { "Content-Type": "application/json" };
  if (token && token !== "change-me") {
    h.Authorization = `Bearer ${token}`;
  }
  return h;
}

export type OrchestratorTool = {
  name: string;
  description: string;
  inputSchema: Record<string, unknown>;
};

export async function listTools(): Promise<OrchestratorTool[]> {
  const res = await fetch(`${baseUrl}/tools`, { headers: headers(), cache: "no-store" });
  if (!res.ok) {
    throw new Error(`listTools failed: ${res.status}`);
  }
  return res.json();
}

export async function callTool(name: string, args: Record<string, unknown>) {
  const res = await fetch(`${baseUrl}/tools/${encodeURIComponent(name)}`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify(args),
  });
  const body = await res.json();
  if (!res.ok) {
    return { success: false, error: body.detail ?? res.statusText, data: body };
  }
  return body;
}

export async function readResource(uri: string) {
  const res = await fetch(`${baseUrl}/resource?uri=${encodeURIComponent(uri)}`, {
    headers: headers(),
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`readResource failed: ${res.status}`);
  }
  return res.json();
}

export async function healthCheck() {
  const res = await fetch(`${baseUrl}/health`, { cache: "no-store" });
  return res.json();
}

export async function analyzeSceneImage(file: Blob): Promise<Record<string, unknown>> {
  const form = new FormData();
  form.append("file", file);
  const h: HeadersInit = {};
  if (token && token !== "change-me") {
    h.Authorization = `Bearer ${token}`;
  }
  const res = await fetch(`${baseUrl}/scene/analyze`, {
    method: "POST",
    headers: h,
    body: form,
  });
  const body = await res.json();
  if (!res.ok) {
    throw new Error((body as { detail?: string }).detail ?? `scene analyze ${res.status}`);
  }
  return body;
}

export async function getSceneLatest(): Promise<Record<string, unknown> | null> {
  const res = await fetch(`${baseUrl}/scene/latest`, { headers: headers(), cache: "no-store" });
  if (res.status === 404) return null;
  if (!res.ok) {
    throw new Error(`scene latest ${res.status}`);
  }
  return res.json();
}
