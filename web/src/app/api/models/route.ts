import { NextResponse } from "next/server";
import { MODEL_CATALOG_AS_OF, MODEL_OPTIONS } from "@/lib/models";

export async function GET() {
  return NextResponse.json({
    catalogAsOf: MODEL_CATALOG_AS_OF,
    models: MODEL_OPTIONS.map((m) => ({
      key: m.key,
      label: m.label,
      provider: m.provider,
      apiModel: m.apiModel,
      fallbackApiModel: m.fallbackApiModel,
      visionApiModel: m.visionApiModel,
      note: m.catalogNote,
    })),
  });
}
