import { useState, useCallback } from "react";
import useSWR from "swr";
import { generatePipeline, getPipelineStatus, GenerateRequest, PipelineStatus } from "@/lib/api";
import { usePipelineStore } from "@/store/pipeline-store";
import { toast } from "@/components/ui/toaster";

// ── useGenerate hook ────────────────────────────────────────────────────────

export type GenerationStage = "idle" | "generating" | "done" | "error";

interface UseGenerateReturn {
  stage: GenerationStage;
  currentAgent: number;
  doneAgents: number[];
  sessionId: string;
  result: PipelineStatus | null;
  error: string;
  generate: (req: GenerateRequest) => Promise<void>;
  reset: () => void;
}

export function useGenerate(): UseGenerateReturn {
  const [stage, setStage] = useState<GenerationStage>("idle");
  const [currentAgent, setCurrentAgent] = useState(-1);
  const [doneAgents, setDoneAgents] = useState<number[]>([]);
  const [sessionId, setSessionId] = useState("");
  const [result, setResult] = useState<PipelineStatus | null>(null);
  const [error, setError] = useState("");

  const addPipeline = usePipelineStore((s) => s.addPipeline);

  const AGENT_DELAYS = [900, 700, 800, 600];

  const generate = useCallback(async (req: GenerateRequest) => {
    setStage("generating");
    setCurrentAgent(0);
    setDoneAgents([]);
    setError("");
    setResult(null);

    try {
      const startTime = Date.now();

      // Start generation
      const genRes = await generatePipeline(req);
      setSessionId(genRes.session_id);

      // Animate agent steps
      for (let i = 0; i < 4; i++) {
        setCurrentAgent(i);
        await new Promise((r) => setTimeout(r, AGENT_DELAYS[i]));
        setDoneAgents((prev) => [...prev, i]);
      }

      // Get final status
      const status = await getPipelineStatus(genRes.session_id);
      setResult(status);
      setStage("done");

      const duration = Date.now() - startTime;

      // Save to store
      addPipeline({
        id: genRes.session_id,
        sessionId: genRes.session_id,
        repoUrl: req.repo_url,
        platform: req.platform || "github_actions",
        status: "done",
        generatedFiles: status.generated_files || [],
        validationPassed: status.validation_passed ?? true,
        createdAt: new Date().toISOString(),
        duration,
      });

      toast("success", "Pipeline generated!", `${req.repo_url.split("/").slice(-2).join("/")} · Validation passed`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Generation failed";
      setError(msg);
      setStage("error");
      toast("error", "Generation failed", msg);
    }
  }, [addPipeline]);

  const reset = useCallback(() => {
    setStage("idle");
    setCurrentAgent(-1);
    setDoneAgents([]);
    setSessionId("");
    setResult(null);
    setError("");
  }, []);

  return { stage, currentAgent, doneAgents, sessionId, result, error, generate, reset };
}

// ── usePipelineStatus hook ──────────────────────────────────────────────────

const fetcher = (url: string) => fetch(url).then((r) => r.json());

export function usePipelineStatus(sessionId: string | null) {
  const { data, error, isLoading } = useSWR(
    sessionId ? `/api/pipelines/status/${sessionId}` : null,
    fetcher,
    { refreshInterval: 2000 }
  );

  return {
    status: data as PipelineStatus | undefined,
    isLoading,
    isError: !!error,
  };
}

// ── usePipelines hook ───────────────────────────────────────────────────────

export function usePipelines() {
  const pipelines = usePipelineStore((s) => s.pipelines);
  const removePipeline = usePipelineStore((s) => s.removePipeline);

  return { pipelines, removePipeline };
}
