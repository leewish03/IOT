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
  system: string;
  tools: { name: string; description: string; input_schema: Record<string, unknown> }[];
  messages: AnthropicMessage[];
  max_tokens?: number;
}): Promise<{ content: AnthropicContentBlock[] }> {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    throw new Error("ANTHROPIC_API_KEY not configured");
  }

  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify({
      model: params.model,
      max_tokens: params.max_tokens ?? 1024,
      system: params.system,
      tools: params.tools,
      messages: params.messages,
    }),
  });

  const body = await response.json();
  if (!response.ok) {
    throw new Error(body.error?.message ?? `Anthropic HTTP ${response.status}`);
  }
  return { content: body.content as AnthropicContentBlock[] };
}
