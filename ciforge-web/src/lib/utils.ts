import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatRelativeTime(date: Date | string): string {
  const d = new Date(date);
  const now = new Date();
  const diff = Math.floor((now.getTime() - d.getTime()) / 1000);

  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

export function truncate(str: string, max: number): string {
  return str.length > max ? str.slice(0, max) + "..." : str;
}

export function extractRepoName(url: string): string {
  return url.replace(/^https?:\/\/(github|gitlab)\.com\//, "").replace(/\.git$/, "");
}

export function getPlatformLabel(platform: string): string {
  const map: Record<string, string> = {
    github_actions: "GitHub Actions",
    gitlab_ci: "GitLab CI",
    jenkins: "Jenkins",
    circleci: "CircleCI",
    azure_devops: "Azure DevOps",
  };
  return map[platform] || platform;
}

export function getPlatformFile(platform: string): string {
  const map: Record<string, string> = {
    github_actions: ".github/workflows/ci-cd.yml",
    gitlab_ci: ".gitlab-ci.yml",
    jenkins: "Jenkinsfile",
    circleci: ".circleci/config.yml",
    azure_devops: "azure-pipelines.yml",
  };
  return map[platform] || "pipeline";
}

export function getPlatformIcon(platform: string): string {
  const map: Record<string, string> = {
    github_actions: "🐙",
    gitlab_ci: "🦊",
    jenkins: "⚙️",
    circleci: "⭕",
    azure_devops: "🔷",
  };
  return map[platform] || "📄";
}
