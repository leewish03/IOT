/** OpenCV scene snapshot from orchestrator (no raw image to LLM). */
export type PersonSceneInfo = {
  bbox: [number, number, number, number];
  centroid: { x: number; y: number };
  posture: "standing" | "sitting" | "unknown";
  activity: "moving" | "still";
  zone: string;
};

export type SceneSnapshot = {
  person_count: number;
  persons: PersonSceneInfo[];
  motion: "moving" | "still";
  summary_ko: string;
  analyzed_at: string;
  frame_width: number;
  frame_height: number;
};
