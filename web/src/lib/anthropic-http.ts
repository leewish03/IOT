type AnthropicContentBlock =
  | { type: "text"; text: string }
  | {
      type: "image";
      source: { type: "base64"; media_type: string; data: string };
    }
  | { type: "tool_use"; id: string; name: string; input: Record<string, unknown> }
  | { type: "tool_result"; tool_use_id: string; content: string };

export type AnthropicMessage = {
  role: "user" | "assistant";
  content: string | AnthropicContentBlock[];
};

export async function anthropicMessagesCreate(params: {
  model: string;
  fallbackModel?: string;
  system: string;
  tools: { name: string; description: string; input_schema: Record<string, unknown> }[];
  messages: AnthropicMessage[];
  max_tokens?: number;
}): Promise<{ content: AnthropicContentBlock[] }> {
  const rawKey = process.env.ANTHROPIC_API_KEY;
  if (!rawKey) {
    throw new Error("ANTHROPIC_API_KEY not configured");
  }
  const anthropicKey: string = rawKey;

  async function request(model: string) {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "x-api-key": anthropicKey,
      "anthropic-version": "2023-06-01",
    };
    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers,
      body: JSON.stringify({
        model,
        max_tokens: params.max_tokens ?? 1024,
        system: params.system,
        ...(params.tools.length > 0 ? { tools: params.tools } : {}),
        messages: params.messages,
      }),
    });
    const body = await response.json();
    return { response, body };
  }

  const primary = await request(params.model);
  if (primary.response.ok) {
    return { content: primary.body.content as AnthropicContentBlock[] };
  }

  const fallback = params.fallbackModel;
  const notFound =
    primary.response.status === 404 ||
    String(primary.body.error?.message ?? "").toLowerCase().includes("model");
  if (fallback && notFound) {
    const second = await request(fallback);
    if (second.response.ok) {
      return { content: second.body.content as AnthropicContentBlock[] };
    }
    throw new Error(second.body.error?.message ?? `Anthropic HTTP ${second.response.status}`);
  }

  throw new Error(primary.body.error?.message ?? `Anthropic HTTP ${primary.response.status}`);
}
