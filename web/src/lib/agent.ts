import OpenAI from "openai";
import { anthropicMessagesCreate, type AnthropicMessage } from "./anthropic-http";
import { callTool, listTools, type OrchestratorTool } from "./orchestrator-client";
import { resolveModel, type ModelKey } from "./models";

export type ChatMessage = { role: "user" | "assistant"; content: string };

const SYSTEM_PROMPT = `You are a home IoT assistant (Jarvis-style). You control lights, relays, alarms, calendar, and sensors via tools.
Always use tools for device actions. Reply in Korean briefly after actions.
If a tool fails, explain and suggest manual dashboard control.`;

function toOpenAiTools(tools: OrchestratorTool[]): OpenAI.Chat.ChatCompletionTool[] {
  return tools.map((t) => ({
    type: "function" as const,
    function: {
      name: t.name,
      description: t.description,
      parameters: t.inputSchema,
    },
  }));
}

function toAnthropicTools(tools: OrchestratorTool[]) {
  return tools.map((t) => ({
    name: t.name,
    description: t.description,
    input_schema: t.inputSchema,
  }));
}

export async function runAgentChat(params: {
  modelKey: ModelKey;
  messages: ChatMessage[];
  maxSteps?: number;
}): Promise<{ reply: string; toolCalls: { name: string; result: unknown }[] }> {
  const model = resolveModel(params.modelKey);
  const tools = await listTools();
  const toolCalls: { name: string; result: unknown }[] = [];
  const maxSteps = params.maxSteps ?? 6;

  if (model.provider === "openai") {
    const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
    const oaiMessages: OpenAI.Chat.ChatCompletionMessageParam[] = [
      { role: "system", content: SYSTEM_PROMPT },
      ...params.messages.map((m) => ({ role: m.role, content: m.content })),
    ];
    const oaiTools = toOpenAiTools(tools);

    for (let step = 0; step < maxSteps; step += 1) {
      const completion = await openai.chat.completions.create({
        model: model.apiModel,
        messages: oaiMessages,
        tools: oaiTools,
      });
      const choice = completion.choices[0];
      const msg = choice.message;
      if (msg.tool_calls?.length) {
        oaiMessages.push(msg);
        for (const tc of msg.tool_calls) {
          if (tc.type !== "function") continue;
          const name = tc.function.name;
          const args = JSON.parse(tc.function.arguments || "{}");
          const result = await callTool(name, args);
          toolCalls.push({ name, result });
          oaiMessages.push({
            role: "tool",
            tool_call_id: tc.id,
            content: JSON.stringify(result),
          });
        }
        continue;
      }
      return { reply: msg.content ?? "", toolCalls };
    }
    return { reply: "도구 호출 한도에 도달했습니다.", toolCalls };
  }

  const anthropicMessages: AnthropicMessage[] = params.messages.map((m) => ({
    role: m.role as "user" | "assistant",
    content: m.content,
  }));

  for (let step = 0; step < maxSteps; step += 1) {
    const response = await anthropicMessagesCreate({
      model: model.apiModel,
      fallbackModel: model.fallbackApiModel,
      system: SYSTEM_PROMPT,
      tools: toAnthropicTools(tools),
      messages: anthropicMessages,
    });

    const textBlocks = response.content.filter((b) => b.type === "text");
    const toolUseBlocks = response.content.filter((b) => b.type === "tool_use");

    if (toolUseBlocks.length === 0) {
      const text = textBlocks.map((b) => (b.type === "text" ? b.text : "")).join("");
      return { reply: text, toolCalls };
    }

    anthropicMessages.push({ role: "assistant", content: response.content });
    const toolResults: { type: "tool_result"; tool_use_id: string; content: string }[] = [];
    for (const block of toolUseBlocks) {
      if (block.type !== "tool_use") continue;
      const result = await callTool(block.name, block.input);
      toolCalls.push({ name: block.name, result });
      toolResults.push({
        type: "tool_result",
        tool_use_id: block.id,
        content: JSON.stringify(result),
      });
    }
    anthropicMessages.push({ role: "user", content: toolResults });
  }

  return { reply: "도구 호출 한도에 도달했습니다.", toolCalls };
}

export async function analyzeVision(params: {
  modelKey: ModelKey;
  imageBase64: string;
  mimeType: string;
  prompt?: string;
}): Promise<{ analysis: string; suggestedActions: string[]; toolCalls: { name: string; result: unknown }[] }> {
  const userText =
    params.prompt ??
    "Describe the room scene. Recommend IoT actions (lights, AC, alarm) in Korean. If obvious, list tool names to call.";

  const visionModel = resolveModel(params.modelKey).visionApiModel;

  if (params.modelKey === "gpt-5.4-nano") {
    const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
    const completion = await openai.chat.completions.create({
      model: visionModel,
      messages: [
        {
          role: "user",
          content: [
            { type: "text", text: userText },
            {
              type: "image_url",
              image_url: { url: `data:${params.mimeType};base64,${params.imageBase64}` },
            },
          ],
        },
      ],
    });
    const analysis = completion.choices[0].message.content ?? "";
    return { analysis, suggestedActions: [], toolCalls: [] };
  }

  // May 2026: multimodal vision via GPT-5.4 nano (Haiku chat may be text-only on API).
  const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
  const completion = await openai.chat.completions.create({
    model: visionModel,
    messages: [
      {
        role: "user",
        content: [
          { type: "text", text: userText },
          {
            type: "image_url",
            image_url: { url: `data:${params.mimeType};base64,${params.imageBase64}` },
          },
        ],
      },
    ],
  });
  const analysis = completion.choices[0].message.content ?? "";
  return { analysis, suggestedActions: [], toolCalls: [] };
}
