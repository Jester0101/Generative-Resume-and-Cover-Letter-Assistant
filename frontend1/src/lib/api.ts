import { PipelineResponse, RunRequest } from "@/types/pipeline";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE?.replace(/\/$/, "") ||
  "http://localhost:8000";

const RUN_ENDPOINT = `${API_BASE}/run`;

export async function runPipeline(payload: RunRequest): Promise<PipelineResponse> {
  const response = await fetch(RUN_ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with status ${response.status}`);
  }

  return (await response.json()) as PipelineResponse;
}

