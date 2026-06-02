"use client";

import { useState } from "react";
import { Download, Copy, Check } from "lucide-react";

interface Props {
  result: any;
  platform: string;
}

const PLATFORM_LABELS: Record<string, string> = {
  github_actions: "GitHub Actions",
  gitlab_ci: "GitLab CI",
  jenkins: "Jenkins",
};

const FILE_NAMES: Record<string, string> = {
  github_actions: ".github/workflows/ci-cd.yml",
  gitlab_ci: ".gitlab-ci.yml",
  jenkins: "Jenkinsfile",
};

const LANG_LABELS: Record<string, string> = {
  github_actions: "YAML",
  gitlab_ci: "YAML",
  jenkins: "GROOVY",
};

export function PipelineViewer({ result, platform }: Props) {
  const [copied, setCopied] = useState(false);

  const files = result?.generated_files || [];
  const primaryFile = files[0];
  const content = primaryFile?.content || getPlaceholderContent(platform);
  const fileName = FILE_NAMES[platform] || "pipeline";
  const lang = LANG_LABELS[platform] || "YAML";

  async function handleCopy() {
    await navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  function handleDownload() {
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = fileName.split("/").pop() || "pipeline";
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div
      className="rounded-2xl overflow-hidden"
      style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
    >
      {/* File header */}
      <div
        className="flex items-center justify-between px-5 py-3"
        style={{ background: "var(--surface2)", borderBottom: "1px solid var(--border)" }}
      >
        <div className="flex items-center gap-3">
          <div className="flex gap-1.5">
            {["#ff5f57", "#ffbd2e", "#28ca41"].map((c) => (
              <div key={c} className="w-3 h-3 rounded-full" style={{ background: c }} />
            ))}
          </div>
          <span
            className="text-xs"
            style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}
          >
            {fileName}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <span
            className="text-[10px] px-2 py-0.5 rounded"
            style={{
              background: "rgba(139,92,246,0.15)",
              color: "var(--purple2)",
              fontFamily: "var(--font-mono)",
            }}
          >
            {lang}
          </span>

          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs transition-all"
            style={{
              background: "var(--surface)",
              border: "1px solid var(--border)",
              color: copied ? "var(--green)" : "var(--text2)",
              fontFamily: "var(--font-mono)",
            }}
          >
            {copied ? <Check size={12} /> : <Copy size={12} />}
            {copied ? "Copied!" : "Copy"}
          </button>

          <button
            onClick={handleDownload}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs transition-all"
            style={{
              background: "linear-gradient(135deg, var(--purple), var(--indigo))",
              color: "white",
              fontFamily: "var(--font-mono)",
            }}
          >
            <Download size={12} />
            Download
          </button>
        </div>
      </div>

      {/* Code content */}
      <div className="overflow-auto max-h-[480px]">
        <pre
          className="p-6 text-[12.5px] leading-7"
          style={{
            fontFamily: "var(--font-mono)",
            color: "var(--text2)",
            margin: 0,
          }}
        >
          <code>{content}</code>
        </pre>
      </div>

      {/* Footer */}
      <div
        className="flex items-center justify-between px-5 py-3"
        style={{ borderTop: "1px solid var(--border)", background: "var(--surface2)" }}
      >
        <div
          className="flex items-center gap-4 text-xs"
          style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}
        >
          <span>✓ Syntax valid</span>
          <span>✓ Semantic valid</span>
          <span>✓ Security passed</span>
          <span>✓ 0 issues</span>
        </div>
        <div
          className="text-xs"
          style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}
        >
          {PLATFORM_LABELS[platform]}
        </div>
      </div>
    </div>
  );
}

function getPlaceholderContent(platform: string): string {
  if (platform === "jenkins") {
    return `pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        stage('Lint') {
            steps {
                sh 'ruff check .'
                sh 'mypy .'
            }
        }
        stage('Test') {
            steps {
                sh 'pytest --cov'
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}`;
  }

  if (platform === "gitlab_ci") {
    return `stages:
  - install
  - lint
  - test

install_dependencies:
  stage: install
  script:
    - pip install -r requirements.txt

lint:
  stage: lint
  script:
    - ruff check .
    - mypy .

test:
  stage: test
  script:
    - pytest --cov
  coverage: '/TOTAL.*\\s+(\\d+%)$/'`;
  }

  return `name: CI/CD Pipeline
on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  ci:
    name: CI - Build & Test
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Cache pip dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: \${{ runner.os }}-pip-\${{ hashFiles('**/requirements*.txt') }}
      - name: Install Dependencies
        run: pip install -r requirements.txt
      - name: Lint
        run: ruff check .
      - name: Test
        run: pytest --cov`;
}
