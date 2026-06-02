import { create } from "zustand";
import { persist } from "zustand/middleware";

export type PipelineStatus = "idle" | "generating" | "done" | "error";

export interface Pipeline {
  id: string;
  sessionId: string;
  repoUrl: string;
  platform: string;
  status: PipelineStatus;
  generatedFiles: { path: string; content: string }[];
  validationPassed: boolean;
  createdAt: string;
  duration?: number;
}

interface PipelineStore {
  pipelines: Pipeline[];
  activePipeline: Pipeline | null;

  addPipeline: (pipeline: Pipeline) => void;
  updatePipeline: (id: string, updates: Partial<Pipeline>) => void;
  setActivePipeline: (pipeline: Pipeline | null) => void;
  removePipeline: (id: string) => void;
  clearAll: () => void;
}

export const usePipelineStore = create<PipelineStore>()(
  persist(
    (set) => ({
      pipelines: [],
      activePipeline: null,

      addPipeline: (pipeline) =>
        set((state) => ({
          pipelines: [pipeline, ...state.pipelines],
        })),

      updatePipeline: (id, updates) =>
        set((state) => ({
          pipelines: state.pipelines.map((p) =>
            p.id === id ? { ...p, ...updates } : p
          ),
          activePipeline:
            state.activePipeline?.id === id
              ? { ...state.activePipeline, ...updates }
              : state.activePipeline,
        })),

      setActivePipeline: (pipeline) =>
        set({ activePipeline: pipeline }),

      removePipeline: (id) =>
        set((state) => ({
          pipelines: state.pipelines.filter((p) => p.id !== id),
          activePipeline:
            state.activePipeline?.id === id ? null : state.activePipeline,
        })),

      clearAll: () =>
        set({ pipelines: [], activePipeline: null }),
    }),
    {
      name: "ciforge-pipelines",
      partialize: (state) => ({ pipelines: state.pipelines }),
    }
  )
);
