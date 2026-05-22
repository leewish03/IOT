export type ModelKey = "claude-haiku-4.6" | "gpt-5.4-nano";

export const MODEL_OPTIONS: {
  key: ModelKey;
  label: string;
  provider: "anthropic" | "openai";
  apiModel: string;
}[] = [
  {
    key: "claude-haiku-4.6",
    label: "Claude Haiku 4.6",
    provider: "anthropic",
    apiModel: process.env.ANTHROPIC_HAIKU_MODEL ?? "claude-haiku-4-5-20251001",
  },
  {
    key: "gpt-5.4-nano",
    label: "GPT-5.4 nano",
    provider: "openai",
    apiModel: process.env.OPENAI_NANO_MODEL ?? "gpt-4.1-nano",
  },
];

export function resolveModel(key: ModelKey) {
  const found = MODEL_OPTIONS.find((m) => m.key === key);
  if (!found) {
    throw new Error(`Unknown model: ${key}`);
  }
  return found;
}
