"use client";

import { useState } from "react";

const TABS = [
  {
    id: "gha", label: "GitHub Actions", file: ".github/workflows/ci-cd.yml", lang: "YAML",
    code: `name: CI/CD Pipeline
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
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: \${{ runner.os }}-pip
      - name: Install Dependencies
        run: pip install -r requirements.txt
      - name: Lint
        run: ruff check .
      - name: Test
        run: pytest --cov`,
  },
  {
    id: "jenkins", label: "Jenkins", file: "Jenkinsfile", lang: "GROOVY",
    code: `pipeline {
    agent any
    stages {
        stage('Install') {
            steps { sh 'pip install -r requirements.txt' }
        }
        stage('Lint') {
            steps {
                sh 'ruff check .'
                sh 'mypy .'
            }
        }
        stage('Test') {
            steps { sh 'pytest --cov' }
        }
    }
    post {
        always { cleanWs() }
        failure { echo 'Pipeline failed!' }
    }
}`,
  },
  {
    id: "gitlab", label: "GitLab CI", file: ".gitlab-ci.yml", lang: "YAML",
    code: `stages:
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
  coverage: '/TOTAL.*\\s+(\\d+%)$/'`,
  },
];

export function CodeDemo() {
  const [active, setActive] = useState("gha");
  const tab = TABS.find((t) => t.id === active)!;

  return (
    <section id="demo" className="relative z-10 py-24" style={{ background: "var(--bg2)" }}>
      <div className="max-w-[1200px] mx-auto px-6">
        <p className="text-xs mb-4"
          style={{ color: "var(--purple)", fontFamily: "var(--font-mono)", letterSpacing: "0.15em" }}>
          // generated output
        </p>
        <h2 className="font-bold leading-tight mb-16"
          style={{ fontFamily: "var(--font-display)", fontSize: "clamp(32px,4vw,52px)", letterSpacing: "-1.5px" }}>
          Real pipelines.<br />Real repositories.
        </h2>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          {/* Left */}
          <div>
            <p className="text-[17px] font-light leading-relaxed mb-8" style={{ color: "var(--text2)" }}>
              CIForge generated this pipeline by analyzing the real Flask repository — detecting
              Python, pip, pytest — and creating the correct pipeline with caching, linting,
              and testing, with zero human input.
            </p>
            <div className="flex gap-3 flex-wrap mb-10">
              {[
                { label: "GitHub Actions", color: "var(--green)" },
                { label: "GitLab CI", color: "var(--purple2)" },
                { label: "Jenkins", color: "var(--cyan)" },
              ].map((p) => (
                <div key={p.label} className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm"
                  style={{ background: "var(--surface)", border: "1px solid var(--border)", color: "var(--text2)", fontFamily: "var(--font-mono)" }}>
                  <span className="w-2 h-2 rounded-full" style={{ background: p.color }} />
                  {p.label}
                </div>
              ))}
            </div>
            <div className="rounded-xl p-6" style={{ background: "var(--surface)", border: "1px solid var(--border)" }}>
              <div className="text-xs mb-4" style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}>
                // repository analysis output
              </div>
              {[
                { key: "Languages", val: "Python 98.8%", color: "var(--purple2)" },
                { key: "Framework", val: "Flask ✓", color: "var(--green)" },
                { key: "Validation", val: "PASSED ✓", color: "var(--green)" },
                { key: "Generation time", val: "2.56s", color: "var(--cyan)" },
              ].map((row) => (
                <div key={row.key} className="flex justify-between items-center py-2"
                  style={{ borderBottom: "1px solid var(--border)" }}>
                  <span className="text-xs" style={{ color: "var(--text2)", fontFamily: "var(--font-mono)" }}>{row.key}</span>
                  <span className="text-xs" style={{ color: row.color, fontFamily: "var(--font-mono)" }}>{row.val}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Right */}
          <div>
            <div className="flex gap-1 p-1 rounded-lg w-fit mb-4"
              style={{ background: "var(--surface)", border: "1px solid var(--border)" }}>
              {TABS.map((t) => (
                <button key={t.id} onClick={() => setActive(t.id)}
                  className="px-3 py-1.5 rounded-md text-xs transition-all"
                  style={{
                    fontFamily: "var(--font-mono)",
                    background: active === t.id ? "rgba(139,92,246,0.15)" : "transparent",
                    color: active === t.id ? "var(--purple2)" : "var(--text3)",
                  }}>
                  {t.label}
                </button>
              ))}
            </div>
            <div className="rounded-2xl overflow-hidden"
              style={{ background: "var(--surface)", border: "1px solid var(--border)" }}>
              <div className="flex items-center justify-between px-5 py-3"
                style={{ background: "var(--surface2)", borderBottom: "1px solid var(--border)" }}>
                <span className="text-xs" style={{ color: "var(--text3)", fontFamily: "var(--font-mono)" }}>
                  {tab.file}
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded"
                  style={{ background: "rgba(139,92,246,0.15)", color: "var(--purple2)", fontFamily: "var(--font-mono)" }}>
                  {tab.lang}
                </span>
              </div>
              <pre className="p-6 text-[12.5px] leading-7 overflow-x-auto"
                style={{ fontFamily: "var(--font-mono)", color: "var(--text2)", margin: 0 }}>
                <code>{tab.code}</code>
              </pre>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
