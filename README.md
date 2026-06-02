<div align="center">

# ⚡ Agentic AI CI/CD Pipeline Generator

**An intelligent multi-agent system that analyzes any GitHub repository and automatically generates production-ready CI/CD pipelines — no DevOps expertise required.**

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js)](https://nextjs.org)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker)](https://docker.com)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-2088FF?style=for-the-badge&logo=github-actions)](https://github.com/features/actions)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

[🚀 Live Demo](#demo) · [📖 Docs](#api-reference) · [🐛 Report Bug](https://github.com/NeuroNaman/agentic-ai-cicd-pipeline-generator/issues)

</div>

---

## 📋 Table of Contents

- [About The Project](#about-the-project)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Docker Deployment](#docker-deployment)
- [GitHub Actions CI/CD](#github-actions-cicd)
- [DevOps Concepts Covered](#devops-concepts-covered)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

---

## 🎯 About The Project

The **Agentic AI CI/CD Pipeline Generator** is a full-stack AI-powered DevOps tool that eliminates the need for manual CI/CD pipeline configuration. Simply paste any GitHub repository URL, and the system will:

1. 🔍 **Analyze** the repository — detect language, framework, build tools, Docker, Kubernetes
2. 📋 **Plan** — determine optimal pipeline stages and deployment strategy
3. ⚙️ **Generate** — produce valid, production-grade pipeline configuration files
4. ✅ **Validate** — check syntax, semantics, security, and best practices

**Supported Platforms:**
| Platform | Output File |
|---|---|
| GitHub Actions | `.github/workflows/ci-cd.yml` |
| GitLab CI | `.gitlab-ci.yml` |
| Jenkins | `Jenkinsfile` |

---

## ✨ Features

- 🤖 **Multi-Agent AI Architecture** — 4 specialized agents orchestrated by LangGraph
- 🔍 **Smart Repository Analysis** — detects 15+ languages, 20+ frameworks automatically
- ⚡ **Fast Generation** — complete pipeline in under 60 seconds
- 🛡️ **4-Layer Validation** — syntax + semantic + security + best practices
- 🌐 **Web Dashboard** — beautiful dark-themed Next.js UI
- 💻 **CLI Interface** — Rich-powered terminal tool for developers
- 🐳 **Fully Containerized** — Docker + Docker Compose ready
- 🔄 **Self-Healing** — auto-fix on validation failure
- 👤 **Human-in-the-Loop** — optional approval gates

---

## 🛠️ Tech Stack

### Backend
| Technology | Version | Purpose |
|---|---|---|
| Python | 3.12 | Core language |
| FastAPI | 0.115 | REST API server |
| LangChain | 0.3 | AI agent framework |
| LangGraph | 0.2 | Multi-agent orchestration |
| GitPython | 3.1 | Repository cloning |
| PyYAML | 6.0 | YAML generation |
| Jinja2 | 3.1 | Pipeline templating |
| Structlog | 24.4 | Structured logging |

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| Next.js | 14.2 | React framework |
| TypeScript | 5 | Type safety |
| Tailwind CSS | 3.4 | Styling |
| NextAuth.js | 5 | Authentication |

### DevOps
| Technology | Purpose |
|---|---|
| Docker | Container runtime |
| Docker Compose | Multi-container orchestration |
| GitHub Actions | CI/CD automation |
| GHCR | Container registry |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│    Next.js Web Dashboard        CLI (Typer + Rich)           │
│        (Port 3000)              python -m src.cli.main       │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│                  FastAPI Server (Port 8000)                  │
│   POST /api/v1/generate    GET /api/v1/status/{id}           │
│   GET  /api/v1/sessions    GET /health                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                       AGENT LAYER                            │
│  ┌─────────────┐ ┌─────────┐ ┌───────────┐ ┌────────────┐  │
│  │RepoAnalysis │→│ Planner │→│ Generator │→│ Validation │  │
│  │   Agent     │ │  Agent  │ │   Agent   │ │   Agent    │  │
│  └─────────────┘ └─────────┘ └───────────┘ └────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Node.js 20+
- Poetry (`pip install poetry`)
- Git

### Local Development (Recommended)

**1. Clone the repository**
```bash
git clone https://github.com/NeuroNaman/agentic-ai-cicd-pipeline-generator.git
cd agentic-ai-cicd-pipeline-generator
```

**2. Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

**3. Start the Backend**
```bash
# Activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

# Install dependencies
poetry install

# Run the server
poetry run uvicorn src.api.server:create_api --factory --host 0.0.0.0 --port 8000 --reload
```

**4. Start the Frontend**
```bash
cd ciforge-web
npm install
npm run dev
```

**5. Open in browser**
- 🌐 Web UI: http://localhost:3000
- 📄 API Docs: http://localhost:8000/docs

---

## 💻 Usage

### Web Dashboard

1. Open http://localhost:3000
2. Sign in with demo credentials:
   - Email: `demo@ciforge.dev`
   - Password: `demo123`
3. Paste a GitHub repository URL
4. Select your target CI/CD platform
5. Click **Generate Pipeline**
6. Download the generated configuration file

### CLI Interface

```bash
# Generate GitHub Actions pipeline
python -m src.cli.main generate https://github.com/pallets/flask --platform github_actions --auto-approve

# Generate GitLab CI pipeline
python -m src.cli.main generate https://github.com/pallets/flask --platform gitlab_ci --auto-approve

# Generate Jenkinsfile
python -m src.cli.main generate https://github.com/pallets/flask --platform jenkins --auto-approve

# List available options
python -m src.cli.main --help
```

### Example Output (GitHub Actions)

```yaml
name: CI/CD Pipeline
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
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
      - run: pip install -r requirements.txt
      - run: pytest --cov
  docker:
    needs: [ci]
    if: github.ref == 'refs/heads/main'
    # ... Docker build & push stages
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/generate` | Start pipeline generation |
| `GET` | `/api/v1/status/{session_id}` | Poll generation status |
| `GET` | `/api/v1/sessions` | List all sessions |
| `GET` | `/health` | Health check |

### Generate Pipeline Request

```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/pallets/flask",
    "platform": "github_actions",
    "auto_approve": true
  }'
```

Full API docs available at: **http://localhost:8000/docs**

---

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Building Images Manually

```bash
# Build backend
docker build -t ciforge-backend:latest .

# Build frontend
docker build -t ciforge-frontend:latest ./ciforge-web

# Run backend
docker run -p 8000:8000 --env-file .env ciforge-backend:latest

# Run frontend
docker run -p 3000:3000 ciforge-frontend:latest
```

---

## ⚙️ GitHub Actions CI/CD

This project uses its own GitHub Actions workflow (`.github/workflows/ci.yml`) demonstrating all key CI/CD concepts:

```
Push to main
    │
    ▼
┌─────────┐     ┌──────────────┐     ┌───────────────┐
│  lint   │────▶│ test-backend │────▶│    docker     │
│         │     │ (Python 3.11 │     │ (build+push   │
└─────────┘     │  & 3.12)     │     │  to GHCR)     │
                └──────────────┘     └───────────────┘
                ┌──────────────┐
                │test-frontend │────▶│    summary    │
                │  (Node 20)   │     │               │
                └──────────────┘     └───────────────┘
```

**Concepts demonstrated:**

| Concept | Implementation |
|---|---|
| Triggers | `push`, `pull_request`, `schedule`, `workflow_dispatch` |
| Matrix Strategy | Python 3.11 + 3.12 tested simultaneously |
| Caching | `actions/cache@v4` for pip and npm |
| Marketplace Actions | checkout, setup-python, setup-node, cache |
| Docker in CI | Build and push to GHCR |
| Job Dependencies | `needs:` for sequential execution |
| Environment Protection | `environment: production` gate |

---

## 📚 DevOps Concepts Covered

### Unit I — GitHub Actions
- ✅ Workflow triggers (push, pull_request, schedule, workflow_dispatch)
- ✅ Jobs and job dependencies (`needs:`)
- ✅ Matrix strategy (multi-version testing)
- ✅ GitHub-hosted runners (`ubuntu-latest`)
- ✅ Marketplace actions (checkout, setup-python, cache)
- ✅ Caching (pip and npm)
- ✅ Docker image building in CI
- ✅ Pushing to GitHub Container Registry (GHCR)
- ✅ Environment secrets and variables
- ✅ Artifacts upload/download

### Unit II — Docker
- ✅ Multi-stage Dockerfiles (builder → runtime)
- ✅ Image layering and build optimization
- ✅ `.dockerignore` for build context optimization
- ✅ `HEALTHCHECK` instruction
- ✅ Non-root user security (`USER` instruction)
- ✅ Named volumes
- ✅ Environment variables (`ENV`, `ARG`)
- ✅ Port exposure (`EXPOSE`)

### Unit III — Docker Compose & Microservices
- ✅ Multi-container orchestration
- ✅ Custom bridge networks
- ✅ Service DNS resolution (`http://backend:8000`)
- ✅ Named volumes for data persistence
- ✅ Service dependency ordering (`depends_on`)
- ✅ Environment variable injection
- ✅ Health check integration
- ✅ Port mapping

---

## 📁 Project Structure

```
agentic-ai-cicd-pipeline-generator/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions workflow (Unit I)
│
├── src/
│   ├── agents/                 # AI agent implementations
│   │   ├── repo_analysis.py    # RepoAnalysisAgent
│   │   ├── planner.py          # PlannerAgent
│   │   ├── generator.py        # PipelineGeneratorAgent
│   │   └── validation.py       # ValidationAgent
│   ├── api/
│   │   └── server.py           # FastAPI application
│   └── cli/
│       └── main.py             # CLI interface
│
├── ciforge-web/                # Next.js frontend
│   ├── src/
│   │   ├── app/                # App Router pages
│   │   └── components/         # React components
│   ├── Dockerfile              # Frontend Docker image (Unit II)
│   └── package.json
│
├── tests/                      # pytest test suite
│
├── Dockerfile                  # Backend Docker image (Unit II)
├── docker-compose.yml          # Multi-service orchestration (Unit III)
├── pyproject.toml              # Python dependencies (Poetry)
├── .gitignore
└── README.md
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">

**Made with ❤️ by [NeuroNaman](https://github.com/NeuroNaman)**

⭐ Star this repo if it helped you!

</div>