import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
});

// ── Types ──────────────────────────────────────────────────────────────────

export interface GenerateRequest {
  repo_url: string;
  platform?: string;
  auto_approve?: boolean;
  constraints?: Record<string, unknown>;
}

export interface GenerateResponse {
  session_id: string;
  status: string;
  message: string;
}

export interface PipelineStatus {
  session_id: string;
  status: string;
  current_stage: string;
  execution_logs: string[];
  generated_files?: { path: string; content: string }[];
  validation_passed?: boolean;
  error_message?: string;
}

// ── Pipeline endpoints ─────────────────────────────────────────────────────

export async function generatePipeline(
  req: GenerateRequest
): Promise<GenerateResponse> {
  const res = await api.post<GenerateResponse>("/pipelines/generate", req);
  return res.data;
}

export async function getPipelineStatus(
  sessionId: string
): Promise<PipelineStatus> {
  const res = await api.get<PipelineStatus>(`/pipelines/status/${sessionId}`);
  return res.data;
}

export async function pollUntilDone(
  sessionId: string,
  onUpdate?: (status: PipelineStatus) => void,
  maxAttempts = 60
): Promise<PipelineStatus> {
  for (let i = 0; i < maxAttempts; i++) {
    const status = await getPipelineStatus(sessionId);
    onUpdate?.(status);

    if (status.status === "completed" || status.status === "failed") {
      return status;
    }

    await new Promise((r) => setTimeout(r, 1000));
  }
  throw new Error("Pipeline generation timed out");
}

export default api;
