/**
 * Model catalog — pinned for May 2026 (2026-05).
 * UI labels match product names; apiModel values match provider docs.
 */
export type ModelKey = "claude-haiku-4.6" | "gpt-5.4-nano";

export type ModelOption = {
  key: ModelKey;
  /** Display name in dashboard */
  label: string;
  provider: "anthropic" | "openai";
  /** Primary API model ID (May 2026) */
  apiModel: string;
  /** Used when primary ID is not yet on the account (e.g. Haiku 4.6 rollout) */
  fallbackApiModel?: string;
  /** Vision / image analysis (OpenAI multimodal) */
  visionApiModel: string;
  catalogNote: string;
};

/** May 2026 — OpenAI: gpt-5.4-nano (snapshot 2026-03-17). Anthropic Haiku line: 4.5 GA; 4.6 ID reserved. */
export const MODEL_CATALOG_AS_OF = "2026-05";

export const MODEL_OPTIONS: ModelOption[] = [
  {
    key: "claude-haiku-4.6",
    label: "Claude Haiku 4.6",
    provider: "anthropic",
    apiModel: process.env.ANTHROPIC_HAIKU_MODEL ?? "claude-haiku-4-6",
    fallbackApiModel: process.env.ANTHROPIC_HAIKU_FALLBACK_MODEL ?? "claude-haiku-4-5-20251001",
    visionApiModel: process.env.OPENAI_VISION_MODEL ?? "gpt-5.4-nano",
    catalogNote: "Anthropic API (May 2026): Haiku GA is 4.5; 4.6 ID used when available, else 4.5 fallback.",
  },
  {
    key: "gpt-5.4-nano",
    label: "GPT-5.4 nano",
    provider: "openai",
    apiModel: process.env.OPENAI_NANO_MODEL ?? "gpt-5.4-nano",
    fallbackApiModel: process.env.OPENAI_NANO_FALLBACK_MODEL ?? "gpt-5.4-nano-2026-03-17",
    visionApiModel: process.env.OPENAI_VISION_MODEL ?? "gpt-5.4-nano",
    catalogNote: "OpenAI API (May 2026): gpt-5.4-nano alias; pin snapshot gpt-5.4-nano-2026-03-17 for production.",
  },
];

export function resolveModel(key: ModelKey): ModelOption {
  const found = MODEL_OPTIONS.find((m) => m.key === key);
  if (!found) {
    throw new Error(`Unknown model: ${key}`);
  }
  return found;
}

/** Pinned snapshot IDs for stable production deploys (May 2026). */
export function pinnedApiModel(key: ModelKey, useSnapshot = false): string {
  const m = resolveModel(key);
  if (!useSnapshot) {
    return m.apiModel;
  }
  if (key === "gpt-5.4-nano") {
    return m.fallbackApiModel ?? m.apiModel;
  }
  return m.fallbackApiModel ?? m.apiModel;
}
