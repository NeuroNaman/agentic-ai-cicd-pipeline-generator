// ── Auth ──────────────────────────────────────────────────────────────────

declare module "next-auth" {
  interface Session {
    user: {
      id: string;
      name?: string | null;
      email?: string | null;
      image?: string | null;
    };
  }
}

// ── Pipeline ──────────────────────────────────────────────────────────────

export type Platform =
  | "github_actions"
  | "gitlab_ci"
  | "jenkins"
  | "circleci"
  | "azure_devops";

export type PipelineStatus =
  | "passed"
  | "running"
  | "failed"
  | "pending"
  | "generating";

export interface GeneratedFile {
  path: string;
  content: string;
  description: string;
  is_primary: boolean;
}

export interface ValidationIssue {
  severity: "error" | "warning" | "info";
  category: string;
  message: string;
  file_path?: string;
  line_number?: number;
  suggestion?: string;
}

export interface ValidationReport {
  passed: boolean;
  issues: ValidationIssue[];
  syntax_valid: boolean;
  semantic_valid: boolean;
  security_passed: boolean;
  duration_seconds: number;
}

export interface RepoAnalysis {
  repo_url: string;
  repo_name: string;
  languages: { name: string; percentage: number }[];
  frameworks: string[];
  package_managers: string[];
  containerization: {
    has_dockerfile: boolean;
    has_compose: boolean;
    multi_stage: boolean;
  };
  infrastructure: {
    has_kubernetes: boolean;
    has_terraform: boolean;
  };
  existing_ci: {
    has_ci: boolean;
    platform?: string;
  };
}

export interface PipelineSession {
  id: string;
  repo_url: string;
  platform: Platform;
  status: PipelineStatus;
  generated_files: GeneratedFile[];
  validation_report?: ValidationReport;
  repo_analysis?: RepoAnalysis;
  execution_logs: string[];
  created_at: string;
  duration_ms?: number;
}

// ── API ───────────────────────────────────────────────────────────────────

export interface ApiError {
  error: string;
  details?: string;
  status: number;
}
