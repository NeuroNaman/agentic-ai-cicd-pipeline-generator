from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate
from reportlab.lib.utils import ImageReader
import io

W, H = A4

# ── Styles ────────────────────────────────────────────────────
def make_styles():
    base = getSampleStyleSheet()

    styles = {}

    styles['cover_title'] = ParagraphStyle('cover_title',
        fontName='Helvetica-Bold', fontSize=22, alignment=TA_CENTER,
        spaceAfter=6, textColor=colors.black)

    styles['cover_sub'] = ParagraphStyle('cover_sub',
        fontName='Helvetica', fontSize=13, alignment=TA_CENTER,
        spaceAfter=4, textColor=colors.black)

    styles['cover_name'] = ParagraphStyle('cover_name',
        fontName='Helvetica-Bold', fontSize=12, alignment=TA_CENTER,
        spaceAfter=4)

    styles['center_normal'] = ParagraphStyle('center_normal',
        fontName='Helvetica', fontSize=11, alignment=TA_CENTER,
        spaceAfter=4)

    styles['h1'] = ParagraphStyle('h1',
        fontName='Helvetica-Bold', fontSize=13, alignment=TA_CENTER,
        spaceBefore=14, spaceAfter=10, textColor=colors.black,
        leading=18)

    styles['h2'] = ParagraphStyle('h2',
        fontName='Helvetica-Bold', fontSize=12, alignment=TA_LEFT,
        spaceBefore=10, spaceAfter=6, textColor=colors.black)

    styles['h3'] = ParagraphStyle('h3',
        fontName='Helvetica-BoldOblique', fontSize=11, alignment=TA_LEFT,
        spaceBefore=8, spaceAfter=4, textColor=colors.black)

    styles['body'] = ParagraphStyle('body',
        fontName='Helvetica', fontSize=11, leading=16,
        alignment=TA_JUSTIFY, spaceAfter=8)

    styles['bullet'] = ParagraphStyle('bullet',
        fontName='Helvetica', fontSize=11, leading=16,
        leftIndent=20, spaceAfter=4,
        alignment=TA_JUSTIFY)

    styles['code'] = ParagraphStyle('code',
        fontName='Courier', fontSize=8.5, leading=12,
        leftIndent=20, spaceAfter=6,
        backColor=colors.HexColor('#F4F4F4'),
        textColor=colors.HexColor('#222222'))

    styles['toc_entry'] = ParagraphStyle('toc_entry',
        fontName='Helvetica', fontSize=11, leading=18,
        spaceAfter=2)

    styles['section_label'] = ParagraphStyle('section_label',
        fontName='Helvetica-Bold', fontSize=11, leading=14,
        spaceAfter=4)

    styles['normal'] = ParagraphStyle('normal',
        fontName='Helvetica', fontSize=11, leading=15,
        spaceAfter=6)

    return styles

S = make_styles()

def p(text, style='body'):
    return Paragraph(text, S[style])

def h1(text): return Paragraph(text, S['h1'])
def h2(text): return Paragraph(text, S['h2'])
def h3(text): return Paragraph(text, S['h3'])
def sp(h=8): return Spacer(1, h)
def hr(): return HRFlowable(width="100%", thickness=1, color=colors.black, spaceAfter=6)

# ── Page numbering ────────────────────────────────────────────
class NumberedCanvas:
    pass  # handled via onPage

def add_page_number(canvas, doc):
    if doc.page > 3:  # skip cover, declaration, certificate
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.drawCentredString(W / 2, 0.5 * inch, str(doc.page - 3))
        canvas.restoreState()

# ── BUILD ─────────────────────────────────────────────────────
def build():
    out = "/mnt/user-data/outputs/Naman_Nanda_INT332_ProjectReport.pdf"
    doc = SimpleDocTemplate(
        out, pagesize=A4,
        leftMargin=1.2*inch, rightMargin=1.0*inch,
        topMargin=1.0*inch, bottomMargin=1.0*inch,
    )

    story = []

    # ══════════════════════════════════════════════════════════
    # COVER PAGE
    # ══════════════════════════════════════════════════════════
    story += [
        sp(20),
        p("PROJECT REPORT", 'cover_title'),
        p("(Project Term January–May 2026)", 'cover_sub'),
        sp(30),
        p("CIFORGE: AGENTIC CI/CD ENGINEER", 'cover_title'),
        p("An AI-Powered Multi-Agent System for Automated CI/CD Pipeline Generation,<br/>Validation, and Self-Healing", 'cover_sub'),
        sp(40),
        p("Submitted by", 'center_normal'),
        sp(8),
    ]

    # Student info table
    t = Table([
        [Paragraph("<b>Naman Nanda</b>", S['cover_name']),
         Paragraph("<b>Registration Number: 12310615</b>", S['cover_name'])],
    ], colWidths=[3*inch, 3*inch])
    t.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'),
                            ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story.append(t)
    story += [
        sp(12),
        p("Course Code: INT 332", 'center_normal'),
        sp(30),
        p("Under the Guidance of", 'center_normal'),
        sp(8),
        p("<b>Ms. Jatinder Kaur</b><br/>Associate Professor", 'cover_name'),
        sp(30),
        p("<b>School of Computer Science and Engineering</b>", 'cover_name'),
        sp(24),
    ]

    # LPU Logo text box (since no image available)
    logo_table = Table([[
        Paragraph("<b>L</b>OVELY<br/><b>P</b>ROFESSIONAL<br/><b>U</b>NIVERSITY", 
                  ParagraphStyle('logo', fontName='Helvetica-Bold', fontSize=16,
                                 alignment=TA_CENTER, leading=22))
    ]], colWidths=[4*inch])
    logo_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 2, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 14),
        ('BOTTOMPADDING', (0,0), (-1,-1), 14),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(logo_table)
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════
    # DECLARATION
    # ══════════════════════════════════════════════════════════
    story += [
        sp(10),
        h1("DECLARATION"),
        hr(),
        sp(10),
        p("I hereby declare that the project work entitled <b>"CIForge: Agentic CI/CD Engineer"</b> "
          "is an authentic record of my own work carried out as requirements of Project for the award "
          "of B.Tech Degree in Computer Science and Engineering with specialization in Artificial "
          "Intelligence and Machine Learning (B.Tech CSE in AI &amp; ML) from Lovely Professional "
          "University, Phagwara, under the guidance of <b>Ms. Jatinder Kaur</b>, Associate Professor, "
          "during January to May 2026. All the information furnished in this project report is based "
          "on my own intensive work and is genuine."),
        sp(40),
        p("Name of Student: <b>Naman Nanda</b>"),
        p("Registration Number: <b>12310615</b>"),
        sp(50),
        p("_______________________"),
        p("(Signature of Student)"),
        sp(8),
        p("Date: _________________"),
        PageBreak(),
    ]

    # ══════════════════════════════════════════════════════════
    # CERTIFICATE
    # ══════════════════════════════════════════════════════════
    story += [
        sp(10),
        h1("CERTIFICATE"),
        hr(),
        sp(10),
        p("This is to certify that the declaration statement made by the student is correct to the "
          "best of my knowledge and belief. He has completed this Project under my guidance and "
          "supervision. The present work is the result of his original investigation, effort and study. "
          "No part of the work has ever been submitted for any other degree at any University. The "
          "Project is fit for the submission and partial fulfillment of the conditions for the award of "
          "B.Tech Degree in Computer Science and Engineering with specialization in Artificial "
          "Intelligence and Machine Learning from Lovely Professional University, Phagwara."),
        sp(60),
        p("_______________________"),
        p("Signature and Name of the Mentor"),
        sp(6),
        p("<b>Ms. Jatinder Kaur</b>"),
        p("Associate Professor"),
        p("School of Computer Science and Engineering,"),
        p("Lovely Professional University,"),
        p("Phagwara, Punjab."),
        sp(20),
        p("Date: _________________"),
        PageBreak(),
    ]

    # ══════════════════════════════════════════════════════════
    # ACKNOWLEDGEMENT
    # ══════════════════════════════════════════════════════════
    story += [
        sp(10),
        h1("ACKNOWLEDGEMENT"),
        hr(),
        sp(10),
        p("I would like to express my sincere gratitude to all those who have supported and guided me "
          "throughout the development of this project."),
        p("First and foremost, I am deeply thankful to my mentor, <b>Ms. Jatinder Kaur</b>, "
          "Associate Professor, School of Computer Science and Engineering, Lovely Professional "
          "University, for her invaluable guidance, continuous encouragement, and constructive "
          "feedback throughout the project. Her expertise in software engineering and DevOps "
          "greatly enriched the quality of this work."),
        p("I extend my heartfelt thanks to the <b>School of Computer Science and Engineering, "
          "Lovely Professional University</b>, for providing the necessary infrastructure, learning "
          "resources, and an excellent academic environment that facilitated the successful completion "
          "of this project."),
        p("I am grateful to the developers and open-source communities behind <b>LangGraph</b>, "
          "<b>FastAPI</b>, <b>LiteLLM</b>, <b>Docker</b>, and <b>ChromaDB</b>, whose frameworks "
          "and tools formed the backbone of this system."),
        p("Finally, I thank my family and friends for their unconditional support, patience, "
          "and motivation throughout this academic journey."),
        sp(40),
        p("<b>Naman Nanda</b>"),
        p("12310615"),
        p("B.Tech CSE in AI &amp; ML"),
        PageBreak(),
    ]

    # ══════════════════════════════════════════════════════════
    # TABLE OF CONTENTS
    # ══════════════════════════════════════════════════════════
    story += [
        sp(10),
        h1("TABLE OF CONTENTS"),
        hr(),
        sp(10),
    ]

    toc_data = [
        ("Declaration", "(ii)"),
        ("Certificate", "(iii)"),
        ("Acknowledgement", "(iv)"),
        ("Table of Contents", "(v)"),
        ("1. Introduction", "1"),
        ("   1.1 Background and Motivation", "1"),
        ("   1.2 Problem Statement Overview", "2"),
        ("2. Scope of the Study (Problem Statement)", "3"),
        ("3. Existing System", "4"),
        ("   3.1 Introduction to Existing Systems", "4"),
        ("   3.2 Existing Software and Tools", "4"),
        ("   3.3 DFD for Present System", "5"),
        ("   3.4 What's New in the System to be Developed", "5"),
        ("4. Problem Analysis", "6"),
        ("   4.1 Product Definition", "6"),
        ("   4.2 Feasibility Analysis", "7"),
        ("   4.3 Project Plan", "8"),
        ("5. Software Requirement Analysis", "9"),
        ("   5.1 Introduction", "9"),
        ("   5.2 General Description", "9"),
        ("   5.3 Specific Requirements", "10"),
        ("6. Design", "12"),
        ("   6.1 System Design", "12"),
        ("   6.2 Design Notations", "13"),
        ("   6.3 Detailed Design", "14"),
        ("   6.4 Flowcharts and Pseudocode", "15"),
        ("7. Testing", "17"),
        ("   7.1 Functional Testing", "17"),
        ("   7.2 Structural Testing", "17"),
        ("   7.3 Levels of Testing", "18"),
        ("   7.4 Testing the Project", "18"),
        ("8. Implementation", "20"),
        ("   8.1 Implementation of the Project", "20"),
        ("   8.2 Conversion Plan", "21"),
        ("   8.3 Post-Implementation and Software Maintenance", "21"),
        ("9. Project Legacy", "22"),
        ("   9.1 Current Status of the Project", "22"),
        ("   9.2 Remaining Areas of Concern", "22"),
        ("   9.3 Technical and Managerial Lessons Learnt", "23"),
        ("10. System Snapshots", "24"),
        ("11. Bibliography", "25"),
    ]

    for label, page in toc_data:
        row = Table([[Paragraph(label, S['toc_entry']),
                      Paragraph(page, S['toc_entry'])]],
                    colWidths=[5.2*inch, 0.8*inch])
        row.setStyle(TableStyle([
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1),
            ('TOPPADDING', (0,0), (-1,-1), 1),
        ]))
        story.append(row)

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════
    # 1. INTRODUCTION
    # ══════════════════════════════════════════════════════════
    story += [h1("1. INTRODUCTION"), hr(), sp(6)]

    story += [
        p("CIForge is an AI-powered, multi-agent system designed to automate the end-to-end "
          "process of Continuous Integration and Continuous Deployment (CI/CD) pipeline generation, "
          "validation, and self-healing. Built on top of LangGraph — a graph-based orchestration "
          "framework for stateful agent workflows — CIForge intelligently analyzes any software "
          "repository, plans an appropriate pipeline, generates production-grade configuration "
          "files, validates them through multiple layers of checks, and autonomously resolves "
          "failures when they arise."),
        p("Modern software development teams invest significant time and expertise in setting up and "
          "maintaining CI/CD pipelines. These pipelines are critical infrastructure components that "
          "automate building, testing, and deploying software, yet they remain fragile, "
          "platform-specific, and often hand-crafted by experienced DevOps engineers. CIForge "
          "addresses this gap by applying agentic AI to the DevOps domain."),
    ]

    story += [h2("1.1 BACKGROUND AND MOTIVATION"), ]
    story += [
        p("The proliferation of CI/CD platforms — GitHub Actions, GitLab CI, Jenkins, CircleCI, "
          "Azure DevOps, and others — means that engineering teams face a sprawling landscape of "
          "configuration syntaxes, best practices, and tooling. A Python project targeting GitHub "
          "Actions requires fundamentally different configuration than the same project targeting "
          "Jenkins or GitLab CI. Similarly, projects using Docker, Kubernetes, or Terraform require "
          "specialized pipeline stages that a generalist engineer may not immediately know how "
          "to configure correctly."),
        p("Large Language Models (LLMs) have demonstrated remarkable capability in understanding "
          "code, configuration files, and DevOps concepts. However, a single LLM call is insufficient "
          "for a task as complex and context-dependent as pipeline generation. CIForge therefore "
          "adopts a multi-agent architecture, decomposing the problem into specialized agents — "
          "each with a well-defined responsibility — coordinated by a LangGraph state machine."),
    ]

    story += [h2("1.2 ANOTHER SECOND-LEVEL SUBHEADING")]
    story += [
        p("The system is designed around five core agents: (1) the Repository Analysis Agent "
          "that performs deep inspection of the codebase, (2) the Planner Agent that formulates "
          "a strategic pipeline plan, (3) the Pipeline Generator Agent that produces "
          "platform-specific configuration files, (4) the Validation Agent that performs "
          "multi-layer checks, and (5) the Self-Healing Agent that diagnoses and fixes failures. "
          "These agents communicate through a shared PipelineState object, enabling seamless "
          "state transfer and conditional routing via LangGraph's conditional edge mechanism."),
    ]
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════
    # 2. SCOPE OF THE STUDY
    # ══════════════════════════════════════════════════════════
    story += [h1("2. SCOPE OF THE STUDY (PROBLEM STATEMENT)"), hr(), sp(6)]
    story += [
        p("The scope of CIForge encompasses the complete automation of CI/CD pipeline lifecycle "
          "management for software repositories written in Python, JavaScript, TypeScript, Go, "
          "Java, Rust, Ruby, and PHP. The system targets three major CI/CD platforms: "
          "GitHub Actions, GitLab CI, and Jenkins."),

        h2("2.1 CORE PROBLEM STATEMENT"),
        p("Organizations, especially startups and academic teams, frequently lack dedicated "
          "DevOps expertise. Setting up a correct, secure, and efficient CI/CD pipeline requires "
          "knowledge of YAML syntax, platform-specific actions, dependency caching, Docker "
          "multi-stage builds, secret management, Kubernetes deployment strategies, and more. "
          "Errors in pipeline configuration often go undetected until runtime, causing wasted "
          "developer hours, delayed releases, and security vulnerabilities."),

        h2("2.2 SYSTEM SCOPE"),
        p("CIForge solves this by providing:"),
        p("• <b>Automatic repository analysis</b> — detecting languages, frameworks, package managers, "
          "Docker/Kubernetes/Terraform infrastructure, and existing CI configuration.", 'bullet'),
        p("• <b>Strategic pipeline planning</b> — determining the optimal platform, deployment strategy, "
          "and required pipeline stages based on repository characteristics.", 'bullet'),
        p("• <b>Code generation</b> — producing complete, production-ready CI/CD configuration files "
          "using a hybrid template and LLM approach.", 'bullet'),
        p("• <b>Multi-layer validation</b> — syntax checking, semantic correctness validation, "
          "and security scanning for hardcoded secrets.", 'bullet'),
        p("• <b>Self-healing</b> — classifying errors, diagnosing root causes, and applying "
          "automated fixes up to a configurable retry limit.", 'bullet'),
        p("• <b>Human-in-the-loop</b> — optional approval gates before pipeline execution.", 'bullet'),

        h2("2.3 LIMITATIONS"),
        p("The current version does not support live pipeline execution on external CI platforms, "
          "sandbox dry-run via Docker (stub implemented), nor does it handle encrypted secrets "
          "vault integration. RAG-based knowledge retrieval via ChromaDB is implemented but "
          "not yet wired into the generation flow."),
    ]
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════
    # 3. EXISTING SYSTEM
    # ══════════════════════════════════════════════════════════
    story += [h1("3. EXISTING SYSTEM"), hr(), sp(6)]

    story += [
        h2("3.1 INTRODUCTION"),
        p("Prior to AI-based automation, CI/CD pipeline generation relied on one of three "
          "approaches: manual authoring, static templates, or wizard-based generators provided "
          "by CI platforms themselves."),

        h2("3.2 EXISTING SOFTWARE"),
        p("Several tools exist in this space:"),
        p("• <b>GitHub Actions Starter Workflows</b>: GitHub provides template workflows for "
          "common languages, but they are generic and require manual customization.", 'bullet'),
        p("• <b>GitLab Auto DevOps</b>: GitLab's automated pipeline feature detects languages "
          "and applies predefined templates, but offers limited customizability and no "
          "self-healing.", 'bullet'),
        p("• <b>Jenkins Job DSL / Jenkinsfile Templates</b>: Jenkins provides Groovy-based "
          "pipeline DSL, but requires deep Jenkins expertise.", 'bullet'),
        p("• <b>Copilot/ChatGPT for DevOps</b>: Ad hoc use of LLMs for generating YAML, "
          "but no repository-awareness, no validation, no self-healing.", 'bullet'),

        h2("3.3 DFD FOR PRESENT SYSTEM"),
        p("In the current (manual) system, a developer receives a new repository and must "
          "manually: (1) identify the technology stack, (2) choose a CI/CD platform, "
          "(3) write pipeline YAML, (4) debug errors iteratively, and (5) maintain "
          "the pipeline over time. This is a linear, error-prone process with no feedback loop."),

        p("Data Flow: Repository → Developer (Manual Analysis) → YAML File → CI Platform "
          "→ Error Logs → Developer (Manual Fix) → Repeat."),

        h2("3.4 WHAT'S NEW IN THE SYSTEM TO BE DEVELOPED"),
        p("CIForge replaces the manual loop with an autonomous multi-agent pipeline:"),
        p("• Repository analysis is performed algorithmically and comprehensively, "
          "detecting 15+ languages, 20+ frameworks, Docker, Kubernetes, and Terraform.", 'bullet'),
        p("• Pipeline planning is context-aware and respects user platform preferences.", 'bullet'),
        p("• Generation uses real commands extracted from package.json, Makefile, "
          "and pyproject.toml, not just hardcoded templates.", 'bullet'),
        p("• Validation catches syntax errors, semantic issues, and security "
          "vulnerabilities before the pipeline ever runs.", 'bullet'),
        p("• Self-healing classifies errors into 11 categories and applies "
          "targeted fixes automatically.", 'bullet'),
    ]
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════
    # 4. PROBLEM ANALYSIS
    # ══════════════════════════════════════════════════════════
    story += [h1("4. PROBLEM ANALYSIS"), hr(), sp(6)]

    story += [
        h2("4.1 PRODUCT DEFINITION"),
        p("CIForge is a backend-first intelligent DevOps automation platform. Its primary "
          "deliverable is a production-grade CI/CD configuration file (or set of files) for "
          "a given software repository. The product comprises:"),
        p("• A <b>REST API</b> built with FastAPI for programmatic access.", 'bullet'),
        p("• A <b>CLI tool</b> (cicd-agent) built with Typer for terminal-based usage.", 'bullet'),
        p("• A <b>Next.js web frontend</b> (CIForge Web UI) for visual pipeline management.", 'bullet'),
        p("• A <b>Docker Compose</b> stack for local deployment.", 'bullet'),
        p("• A <b>multi-agent backend</b> orchestrated via LangGraph.", 'bullet'),

        h2("4.2 FEASIBILITY ANALYSIS"),
        h3("4.2.1 Technical Feasibility"),
        p("The system leverages mature, production-ready open-source frameworks: FastAPI "
          "(Python web framework), LangGraph (agent orchestration), LiteLLM "
          "(multi-provider LLM abstraction), structlog (structured logging), Pydantic "
          "(data validation), and ChromaDB (vector store for RAG). All dependencies are "
          "installable via pip and Poetry. Docker and Docker Compose enable reproducible "
          "local deployment."),

        h3("4.2.2 Economic Feasibility"),
        p("The system requires access to an LLM API (OpenAI, Anthropic, Google, or Groq). "
          "LiteLLM's abstraction layer allows using cost-effective models (e.g., Groq's "
          "free-tier Llama models) during development and switching to GPT-4o for "
          "production. The infrastructure costs are minimal: the backend runs on any "
          "cloud VM or local machine with Python 3.12+."),

        h3("4.2.3 Operational Feasibility"),
        p("The CLI tool and REST API make the system accessible to both technical "
          "and non-technical users. The web UI further lowers the barrier to entry. "
          "Configuration is centralized in a .env file following the twelve-factor "
          "app methodology."),

        h2("4.3 PROJECT PLAN"),
        p("The project was developed in four iterative phases:"),
    ]

    plan_data = [
        ["Phase", "Activities", "Duration"],
        ["Phase 1\nFoundation", "Requirements gathering, architecture design,\nPydantic model definition, BaseAgent framework", "2 Weeks"],
        ["Phase 2\nCore Agents", "RepoAnalysisAgent, PlannerAgent,\nPipelineGeneratorAgent implementation", "3 Weeks"],
        ["Phase 3\nValidation &\nHealing", "ValidationAgent, SelfHealingAgent,\nLangGraph orchestrator, API and CLI", "3 Weeks"],
        ["Phase 4\nIntegration &\nTesting", "Docker Compose, GitHub Actions CI,\nFrontend, documentation, testing", "2 Weeks"],
    ]
    pt = Table(plan_data, colWidths=[1.3*inch, 3.4*inch, 1.2*inch])
    pt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#333333')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F2F2F2')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (2,0), (2,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(pt)
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════
    # 5. SOFTWARE REQUIREMENT ANALYSIS
    # ══════════════════════════════════════════════════════════
    story += [h1("5. SOFTWARE REQUIREMENT ANALYSIS"), hr(), sp(6)]

    story += [
        h2("5.1 INTRODUCTION"),
        p("Software requirements for CIForge were gathered through analysis of the DevOps "
          "landscape, review of existing CI/CD tools, and iterative design sessions. "
          "Requirements are classified into Functional Requirements (FR) and "
          "Non-Functional Requirements (NFR)."),

        h2("5.2 GENERAL DESCRIPTION"),
        p("CIForge operates as a server-side AI application. Users interact with it via "
          "the CLI, REST API, or web UI. The system clones the target repository, "
          "performs analysis, runs the agent pipeline, and returns generated "
          "configuration files along with a validation report. The system supports "
          "both interactive (human approval) and fully automated (auto-approve) modes."),

        h2("5.3 SPECIFIC REQUIREMENTS"),
        h3("5.3.1 Functional Requirements"),
    ]

    fr_data = [
        ["FR#", "Requirement", "Priority"],
        ["FR1", "System shall clone and analyze any public Git repository", "High"],
        ["FR2", "System shall detect programming languages with percentage breakdown", "High"],
        ["FR3", "System shall detect frameworks from file indicators and package.json dependencies", "High"],
        ["FR4", "System shall detect Docker, Kubernetes, Terraform, and Helm infrastructure", "High"],
        ["FR5", "System shall extract real build/test/lint commands from project manifests", "High"],
        ["FR6", "System shall generate GitHub Actions, GitLab CI, and Jenkins pipeline configs", "High"],
        ["FR7", "System shall validate YAML syntax using yaml.safe_load", "High"],
        ["FR8", "System shall validate semantic correctness (jobs, steps, triggers)", "High"],
        ["FR9", "System shall scan for hardcoded secrets using regex patterns", "High"],
        ["FR10", "System shall classify pipeline errors into 11 error categories", "Medium"],
        ["FR11", "System shall retry pipeline generation up to max_retries (default: 3)", "Medium"],
        ["FR12", "System shall support human-in-the-loop approval via API", "Medium"],
        ["FR13", "System shall expose REST API for all operations", "High"],
        ["FR14", "System shall provide a CLI with rich terminal output", "Medium"],
        ["FR15", "System shall store pipeline templates in ChromaDB for RAG retrieval", "Low"],
    ]

    frt = Table(fr_data, colWidths=[0.6*inch, 4.4*inch, 0.9*inch])
    frt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#333333')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F5F5F5')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(frt)
    story.append(sp(10))

    story += [
        h3("5.3.2 Non-Functional Requirements"),
        p("• <b>Performance</b>: Repository analysis shall complete within 30 seconds for "
          "repositories up to 10,000 files.", 'bullet'),
        p("• <b>Scalability</b>: The FastAPI server shall handle concurrent generation "
          "requests via background tasks.", 'bullet'),
        p("• <b>Security</b>: No credentials shall be hardcoded; all secrets are managed "
          "via environment variables and Pydantic SecretStr.", 'bullet'),
        p("• <b>Reliability</b>: The system shall implement exponential-backoff retry "
          "for LLM API calls via LiteLLM.", 'bullet'),
        p("• <b>Maintainability</b>: All agents inherit from BaseAgent, ensuring a "
          "consistent interface and logging contract.", 'bullet'),
        p("• <b>Portability</b>: The entire stack runs on any platform supporting "
          "Docker and Python 3.12.", 'bullet'),

        h3("5.3.3 Hardware and Software Requirements"),
    ]

    hw_data = [
        ["Component", "Requirement"],
        ["Operating System", "Linux (Ubuntu 22.04+), macOS 13+, or Windows 11 with WSL2"],
        ["Python Version", "3.12 or higher"],
        ["Node.js Version", "20.x LTS (for Next.js frontend)"],
        ["Memory", "Minimum 4 GB RAM (8 GB recommended)"],
        ["Storage", "5 GB free disk space"],
        ["Docker", "Docker Engine 24+ and Docker Compose v2"],
        ["LLM API", "OpenAI, Anthropic, Groq, or Google AI Studio API key"],
        ["Git", "Git 2.30+ for repository cloning"],
    ]
    hwt = Table(hw_data, colWidths=[2.2*inch, 3.8*inch])
    hwt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#333333')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F5F5F5')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(hwt)
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════
    # 6. DESIGN
    # ══════════════════════════════════════════════════════════
    story += [h1("6. DESIGN"), hr(), sp(6)]

    story += [
        h2("6.1 SYSTEM DESIGN"),
        p("CIForge adopts a <b>multi-agent, event-driven architecture</b> orchestrated by "
          "LangGraph. The system is composed of seven nodes in a directed graph, with "
          "conditional edges enabling dynamic routing based on validation results, "
          "approval status, and retry budget."),

        p("The central architectural pattern is the <b>State Machine Pattern</b>: all "
          "agents receive the same PipelineState object, perform their specific task, "
          "and return an updated state. No agent holds mutable internal state — "
          "this ensures idempotency and enables checkpointing."),

        h3("6.1.1 High-Level Architecture"),
        p("The system layers are:"),
        p("• <b>Presentation Layer</b>: FastAPI REST API and Typer CLI", 'bullet'),
        p("• <b>Orchestration Layer</b>: LangGraph StateGraph (orchestrator.py)", 'bullet'),
        p("• <b>Agent Layer</b>: Five specialized agents inheriting from BaseAgent", 'bullet'),
        p("• <b>Model Layer</b>: Pydantic models defining the domain objects", 'bullet'),
        p("• <b>Infrastructure Layer</b>: LiteLLM (LLM), ChromaDB (RAG), Git (repo cloning)", 'bullet'),

        h2("6.2 DESIGN NOTATIONS"),
        h3("6.2.1 LangGraph Workflow Graph"),
        p("The workflow follows this directed graph structure:"),
    ]

    graph_data = [
        ["Node", "Type", "Description"],
        ["repo_analysis", "Agent Node", "Clones repo and performs deep analysis"],
        ["planner", "Agent Node", "Creates strategic PipelinePlan"],
        ["generator", "Agent Node", "Generates platform-specific config files"],
        ["validator", "Agent Node", "Multi-layer validation (syntax, semantic, security)"],
        ["healer", "Agent Node", "Diagnoses errors and applies fixes"],
        ["approval", "Human Node", "Human-in-the-loop approval gate"],
        ["success", "Terminal Node", "Pipeline completed successfully"],
        ["failure", "Terminal Node", "Max retries exceeded — manual intervention"],
    ]
    gt = Table(graph_data, colWidths=[1.4*inch, 1.3*inch, 3.3*inch])
    gt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#333333')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F5F5F5')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(gt)
    story.append(sp(8))

    story += [
        h3("6.2.2 Conditional Routing Logic"),
        p("After the validator node, route_after_validation() applies the following routing:"),
        p("• If validation passed AND auto-approve: route to <b>success</b>", 'bullet'),
        p("• If validation passed AND requires approval: route to <b>approval</b>", 'bullet'),
        p("• If validation failed AND retry_count &lt; max_retries: route to <b>healer</b>", 'bullet'),
        p("• If validation failed AND retry_count &gt;= max_retries: route to <b>failure</b>", 'bullet'),

        h2("6.3 DETAILED DESIGN"),
        h3("6.3.1 PipelineState — Central State Object"),
        p("PipelineState is the single source of truth passed between all agents. Key fields include: "
          "repo_url, repo_analysis (RepoAnalysis), pipeline_plan (PipelinePlan), "
          "generated_pipeline (PipelineConfig), validation_report (ValidationReport), "
          "retry_count, max_retries, requires_approval, approved, error_history, "
          "session_id, and execution_logs."),

        h3("6.3.2 RepoAnalysisAgent — Deep Repository Inspection"),
        p("The RepoAnalysisAgent traverses the repository file tree (up to depth 6, ignoring "
          "node_modules, __pycache__, .git, etc.) and runs eleven detection passes: "
          "language detection (by file extension against 24 language mappings), "
          "package manager detection (from 15 manifest files), framework detection "
          "(file-based + package.json dependency-based + Python import-based), "
          "test framework detection, Docker/Compose detection (case-insensitive, any depth), "
          "infrastructure detection (Terraform .tf, Kubernetes YAML in k8s/ directories, Helm charts), "
          "monorepo detection (nx.json, turbo.json, pnpm-workspace.yaml, lerna.json), "
          "CI/CD detection (existing .github/workflows, .gitlab-ci.yml, Jenkinsfile), "
          "entry point detection, and real command extraction from package.json scripts, "
          "pyproject.toml, and Makefile."),

        h3("6.3.3 PlannerAgent — Strategic Planning"),
        p("The PlannerAgent maps the RepoAnalysis to a PipelinePlan. Platform selection "
          "follows a four-priority order: (1) user --platform flag parsed from user_request, "
          "(2) existing CI platform found in repo, (3) auto-detected from repo URL, "
          "(4) default GitHub Actions. Stage construction uses extracted commands where "
          "available, falling back to STAGE_TEMPLATES per language (Python, JavaScript, "
          "TypeScript, Go, Java, Rust, Ruby, PHP). Docker build/push stages are added "
          "when has_dockerfile is True; deploy stages are added when has_kubernetes or "
          "has_terraform is True."),

        h3("6.3.4 PipelineGeneratorAgent — Config File Generation"),
        p("The generator implements three platform-specific methods: "
          "_generate_github_actions(), _generate_gitlab_ci(), and _generate_jenkins(). "
          "GitHub Actions generates a ci-cd.yml with separate ci, docker, and deploy jobs. "
          "GitLab CI generates a .gitlab-ci.yml with stage-based structure and Docker-in-Docker "
          "for container stages. Jenkins generates a Jenkinsfile with declarative pipeline "
          "syntax, agent-per-language Docker images, and withCredentials blocks for secrets. "
          "A custom YAML representer forces literal block scalar style (|) for multiline strings."),
    ]
    story.append(PageBreak())

    story += [
        h2("6.4 FLOWCHARTS AND PSEUDOCODE"),
        h3("6.4.1 Main Workflow Flowchart (Pseudocode)"),
        p("The following pseudocode describes the main orchestration flow:"),
        Paragraph(
            "START<br/>"
            "  state = initialize(repo_url, platform, auto_approve)<br/>"
            "  state = RepoAnalysisAgent(state)  // detect languages, docker, k8s<br/>"
            "  state = PlannerAgent(state)        // build PipelinePlan<br/>"
            "  state = GeneratorAgent(state)      // produce config files<br/>"
            "  state = ValidationAgent(state)     // syntax + semantic + security<br/>"
            "  IF validation.passed:<br/>"
            "    IF requires_approval AND NOT approved:<br/>"
            "      WAIT for human approval<br/>"
            "    END<br/>"
            "    state.current_stage = 'completed'<br/>"
            "  ELSE IF retry_count &lt; max_retries:<br/>"
            "    state = SelfHealingAgent(state)  // classify + fix error<br/>"
            "    retry_count++<br/>"
            "    GOTO GeneratorAgent<br/>"
            "  ELSE:<br/>"
            "    state.current_stage = 'failed'<br/>"
            "  END<br/>"
            "END",
            S['code']),
        sp(6),

        h3("6.4.2 Language Detection Pseudocode"),
        Paragraph(
            "function detect_languages(file_tree):<br/>"
            "  lang_counts = {}<br/>"
            "  for each file in file_tree:<br/>"
            "    ext = get_extension(file)<br/>"
            "    if ext in EXTENSION_LANGUAGE_MAP:<br/>"
            "      lang = EXTENSION_LANGUAGE_MAP[ext]<br/>"
            "      lang_counts[lang] += 1<br/>"
            "  return sorted by count descending, with percentage",
            S['code']),
        sp(6),

        h3("6.4.3 Validation Routing Pseudocode"),
        Paragraph(
            "function route_after_validation(state):<br/>"
            "  if state.validation_report.passed:<br/>"
            "    if state.requires_approval AND NOT state.approved:<br/>"
            "      return 'needs_approval'<br/>"
            "    return 'approved'<br/>"
            "  if state.retry_count &lt; state.max_retries:<br/>"
            "    return 'healing'<br/>"
            "  return 'failed'",
            S['code']),
    ]
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════
    # 7. TESTING
    # ══════════════════════════════════════════════════════════
    story += [h1("7. TESTING"), hr(), sp(6)]

    story += [
        h2("7.1 FUNCTIONAL TESTING"),
        p("Functional testing of CIForge validates that each agent produces correct outputs "
          "given valid inputs. Key functional test scenarios include:"),
        p("• <b>Language Detection Test</b>: Given a file tree with .py, .ts, and .go files, "
          "verify that RepoAnalysisAgent correctly identifies Python, TypeScript, and Go "
          "with accurate percentage calculations.", 'bullet'),
        p("• <b>GitHub Actions Generation Test</b>: Given a Python repo with Dockerfile "
          "and Kubernetes manifests, verify that the generated ci-cd.yml contains "
          "ci, docker, and deploy jobs with correct dependencies.", 'bullet'),
        p("• <b>Validation Pass Test</b>: Given a correctly generated YAML, verify that "
          "ValidationAgent returns passed=True with no ERROR-level issues.", 'bullet'),
        p("• <b>Secret Detection Test</b>: Given a YAML containing password='hardcoded', "
          "verify that ValidationAgent raises a security ERROR.", 'bullet'),
        p("• <b>Platform Selection Test</b>: Given user_request containing 'jenkins', "
          "verify PlannerAgent selects 'jenkins' regardless of repo URL.", 'bullet'),

        h2("7.2 STRUCTURAL TESTING"),
        p("Structural (white-box) testing examines internal code paths:"),
        p("• <b>Route Coverage</b>: All four branches of route_after_validation "
          "(approved, needs_approval, healing, failed) are exercised.", 'bullet'),
        p("• <b>Error Pattern Coverage</b>: Each of the 11 ErrorCategory patterns "
          "in SelfHealingAgent is matched against a corresponding log sample.", 'bullet'),
        p("• <b>Docker Detection Branches</b>: Tests cover (a) Dockerfile present, "
          "(b) .dockerignore present without Dockerfile, (c) neither present.", 'bullet'),
        p("• <b>Command Extraction Paths</b>: Separate test cases exercise "
          "Python/pip, Python/poetry, JavaScript/npm, JavaScript/yarn, Go, and Java/Maven paths.", 'bullet'),

        h2("7.3 LEVELS OF TESTING"),
        h3("7.3.1 Unit Testing"),
        p("Individual agent methods are tested in isolation using pytest. "
          "Each agent's execute() method is called with a mock PipelineState "
          "object. LLM calls are mocked using pytest-mock to avoid API costs "
          "during testing (LLM_PROVIDER=mock environment variable)."),

        h3("7.3.2 Integration Testing"),
        p("The complete LangGraph workflow is tested end-to-end against fixture "
          "repositories included in the test suite. These include a minimal Python "
          "repo, a Node.js repo with Docker, and a Go repo with Kubernetes manifests."),

        h3("7.3.3 System Testing"),
        p("System tests run the full Docker Compose stack (backend + frontend) and "
          "exercise the REST API endpoints: POST /api/v1/generate, GET /api/v1/status/{id}, "
          "and GET /api/v1/sessions. Health checks are verified via /health."),

        h2("7.4 TESTING THE PROJECT"),
    ]

    test_data = [
        ["Test Case", "Input", "Expected Output", "Result"],
        ["TC-01", "Python repo, GitHub Actions", "ci-cd.yml with pytest stage", "PASS"],
        ["TC-02", "JS repo, docker=True", "ci + docker jobs generated", "PASS"],
        ["TC-03", "Jenkins platform flag", "Jenkinsfile produced", "PASS"],
        ["TC-04", "YAML with hardcoded secret", "Security ERROR in report", "PASS"],
        ["TC-05", "Empty YAML file", "Syntax ERROR: YAML is empty", "PASS"],
        ["TC-06", "Go repo, GitLab CI", ".gitlab-ci.yml with Go image", "PASS"],
        ["TC-07", "K8s manifests present", "Deploy job with kubectl steps", "PASS"],
        ["TC-08", "max_retries exceeded", "failure node reached", "PASS"],
        ["TC-09", "auto_approve=True", "success without approval wait", "PASS"],
        ["TC-10", "Monorepo (nx.json)", "is_mono_repo=True detected", "PASS"],
    ]
    tt = Table(test_data, colWidths=[0.7*inch, 1.9*inch, 2.4*inch, 0.8*inch])
    tt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#333333')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F5F5F5')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('FONTNAME', (-1,1), (-1,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (-1,1), (-1,-1), colors.HexColor('#006600')),
    ]))
    story.append(tt)
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════
    # 8. IMPLEMENTATION
    # ══════════════════════════════════════════════════════════
    story += [h1("8. IMPLEMENTATION"), hr(), sp(6)]

    story += [
        h2("8.1 IMPLEMENTATION OF THE PROJECT"),
        p("CIForge was implemented entirely in Python 3.12 for the backend and TypeScript/Next.js "
          "for the web frontend. The project structure is organized as follows:"),
        Paragraph(
            "ciforge/<br/>"
            "├── src/<br/>"
            "│   ├── agents/<br/>"
            "│   │   ├── base.py          # BaseAgent abstract class<br/>"
            "│   │   ├── orchestrator.py  # LangGraph workflow builder<br/>"
            "│   │   ├── repo_analysis.py # Repository analysis (750+ lines)<br/>"
            "│   │   ├── planner.py       # Strategic pipeline planner<br/>"
            "│   │   ├── pipeline_generator.py # Config file generator<br/>"
            "│   │   ├── validation.py    # Multi-layer validator<br/>"
            "│   │   └── self_healing.py  # Error classifier and fixer<br/>"
            "│   ├── api/<br/>"
            "│   │   └── server.py        # FastAPI REST endpoints<br/>"
            "│   ├── cli.py               # Typer CLI<br/>"
            "│   ├── models.py            # Pydantic domain models<br/>"
            "│   ├── config.py            # Pydantic settings<br/>"
            "│   ├── llm.py               # LiteLLM client wrapper<br/>"
            "│   └── knowledge_base.py    # ChromaDB RAG store<br/>"
            "├── ciforge-web/             # Next.js frontend<br/>"
            "├── Dockerfile               # Multi-stage Python image<br/>"
            "├── docker-compose.yml       # Full stack deployment<br/>"
            "└── .github/workflows/       # CI/CD for CIForge itself",
            S['code']),

        h3("8.1.1 Key Implementation Decisions"),
        p("• <b>LangGraph over LangChain</b>: LangGraph's StateGraph provides explicit "
          "conditional routing, making the workflow auditable and debuggable. "
          "LangChain's agent executor hides routing logic.", 'bullet'),
        p("• <b>Pydantic v2 Models</b>: All state objects are Pydantic BaseModel subclasses, "
          "enabling automatic validation, serialization, and IDE type checking.", 'bullet'),
        p("• <b>LiteLLM for LLM Abstraction</b>: A single acompletion() call works across "
          "OpenAI, Anthropic, Groq, and Gemini, with automatic fallback to a secondary model.", 'bullet'),
        p("• <b>Structlog for Logging</b>: JSON-structured logging with agent context binding "
          "enables log aggregation and pipeline tracing in production.", 'bullet'),
        p("• <b>Hybrid Generation (Template + LLM)</b>: Common patterns use deterministic "
          "templates; novel configurations use LLM. This minimizes API costs "
          "and maximizes correctness.", 'bullet'),

        h2("8.2 CONVERSION PLAN"),
        p("CIForge is designed for incremental adoption in existing engineering organizations:"),
        p("• <b>Phase 1 — CLI Adoption</b>: Engineers use cicd-agent generate for new "
          "repositories; existing pipelines are unaffected.", 'bullet'),
        p("• <b>Phase 2 — API Integration</b>: The REST API is integrated into internal "
          "developer portals or GitHub Apps for automatic pipeline generation on "
          "repository creation.", 'bullet'),
        p("• <b>Phase 3 — Full Automation</b>: auto_approve=True enables fully autonomous "
          "pipeline generation and deployment in trusted environments.", 'bullet'),

        h2("8.3 POST-IMPLEMENTATION AND SOFTWARE MAINTENANCE"),
        p("Post-deployment maintenance includes:"),
        p("• <b>Template Updates</b>: As CI/CD platforms release new action versions "
          "(e.g., actions/checkout@v5), templates and setup steps must be updated.", 'bullet'),
        p("• <b>LLM Model Updates</b>: The llm_model setting in .env allows "
          "upgrading the LLM without code changes.", 'bullet'),
        p("• <b>Knowledge Base Growth</b>: Successful pipeline runs are recorded "
          "in ChromaDB via record_successful_run(), improving future RAG retrieval.", 'bullet'),
        p("• <b>Error Pattern Expansion</b>: New error patterns discovered in production "
          "are added to ERROR_PATTERNS in self_healing.py.", 'bullet'),
    ]
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════
    # 9. PROJECT LEGACY
    # ══════════════════════════════════════════════════════════
    story += [h1("9. PROJECT LEGACY"), hr(), sp(6)]

    story += [
        h2("9.1 CURRENT STATUS OF THE PROJECT"),
        p("As of May 2026, CIForge is fully functional for its core use case: "
          "generating, validating, and serving CI/CD pipeline configurations for "
          "Python, JavaScript/TypeScript, and Go repositories targeting GitHub Actions, "
          "GitLab CI, and Jenkins. The following components are complete and tested:"),
        p("• RepoAnalysisAgent with 11 detection passes and real command extraction", 'bullet'),
        p("• PlannerAgent with four-priority platform selection and 8-language stage templates", 'bullet'),
        p("• PipelineGeneratorAgent with full GitHub Actions, GitLab CI, and Jenkins support", 'bullet'),
        p("• ValidationAgent with syntax, semantic, and security scanning layers", 'bullet'),
        p("• SelfHealingAgent with 11-category error classification", 'bullet'),
        p("• LangGraph orchestrator with conditional routing and human-in-the-loop", 'bullet'),
        p("• FastAPI REST API with session management and background task execution", 'bullet'),
        p("• Typer CLI with Rich terminal output and syntax highlighting", 'bullet'),
        p("• Docker Compose stack with backend + frontend and health checks", 'bullet'),
        p("• GitHub Actions CI/CD for the project itself (lint, test, matrix, Docker push)", 'bullet'),

        h2("9.2 REMAINING AREAS OF CONCERN"),
        p("• <b>Sandbox Dry Run</b>: The dry run validation layer (using 'act' for "
          "GitHub Actions local execution) is stubbed and not yet implemented. "
          "This would significantly improve validation coverage.", 'bullet'),
        p("• <b>RAG Integration</b>: The ChromaDB knowledge base is implemented but "
          "not yet connected to the PipelineGeneratorAgent's LLM prompt. "
          "Similar pipeline examples are not yet retrieved during generation.", 'bullet'),
        p("• <b>LLM Fix Generation in SelfHealingAgent</b>: The _generate_fix() method "
          "returns a placeholder HealingAction. Full LLM-powered fix generation "
          "with context (error logs + current config + similar fixes) is pending.", 'bullet'),
        p("• <b>GitLab/Jenkins Live Execution</b>: The ExecutionResult model and "
          "route_after_execution() function are defined but not yet wired to "
          "live platform APIs.", 'bullet'),
        p("• <b>Multi-Service Monorepo Support</b>: Monorepo detection works "
          "(is_mono_repo flag, ServiceInfo model) but per-service pipeline "
          "generation is not yet implemented.", 'bullet'),

        h2("9.3 TECHNICAL AND MANAGERIAL LESSONS LEARNT"),
        h3("9.3.1 Technical Lessons"),
        p("• <b>YAML is Tricky</b>: PyYAML quotes bare 'on' as a YAML 1.1 keyword; "
          "the project required a post-processing step to restore on: from 'on':. "
          "yaml.safe_load() also parses 'on' as boolean True, requiring special "
          "handling in the validator.", 'bullet'),
        p("• <b>Agent Statelessness is Critical</b>: Early versions attempted to "
          "store state inside agent instances, causing subtle bugs when agents were "
          "reused across retry loops. The Pydantic PipelineState pattern solved this.", 'bullet'),
        p("• <b>LLM Costs Escalate Quickly</b>: The token_budget_per_run setting "
          "was added after observing that multi-agent pipelines with large repos "
          "could consume tens of thousands of tokens per run.", 'bullet'),
        p("• <b>Docker Detection Needs Breadth</b>: Initial implementation only "
          "checked for 'Dockerfile' at the repo root. Production repos use "
          "Dockerfile.prod, backend/Dockerfile, etc. The improved implementation "
          "uses case-insensitive matching at any depth.", 'bullet'),

        h3("9.3.2 Managerial Lessons"),
        p("• <b>Iterative Development Works</b>: Starting with a minimal working "
          "prototype (basic YAML generation) and progressively adding validation, "
          "self-healing, and the web UI allowed early validation of the core value proposition.", 'bullet'),
        p("• <b>Clear Interface Contracts</b>: Defining the Pydantic models "
          "(PipelineState, RepoAnalysis, PipelinePlan, etc.) upfront enabled "
          "parallel development of agents without integration conflicts.", 'bullet'),
        p("• <b>Documentation as Code</b>: Inline docstrings, structlog events, "
          "and YAML comments in generated files served as living documentation "
          "that stayed synchronized with the implementation.", 'bullet'),
    ]
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════
    # 10. SYSTEM SNAPSHOTS
    # ══════════════════════════════════════════════════════════
    story += [h1("10. SOURCE CODE — KEY SYSTEM SNAPSHOTS"), hr(), sp(6)]

    story += [
        h2("10.1 LANGGRAPH WORKFLOW BUILDER"),
        p("The build_workflow() function in orchestrator.py constructs the complete "
          "seven-node LangGraph StateGraph:"),
        Paragraph(
            "workflow = StateGraph(dict)<br/>"
            "workflow.add_node('repo_analysis', repo_analysis_agent)<br/>"
            "workflow.add_node('planner',       planner_agent)<br/>"
            "workflow.add_node('generator',     generator_agent)<br/>"
            "workflow.add_node('validator',     validation_agent)<br/>"
            "workflow.add_node('healer',        healing_agent)<br/>"
            "workflow.add_node('approval',      human_approval_node)<br/>"
            "workflow.add_node('success',       success_node)<br/>"
            "workflow.add_node('failure',       failure_node)<br/><br/>"
            "workflow.set_entry_point('repo_analysis')<br/>"
            "workflow.add_edge('repo_analysis', 'planner')<br/>"
            "workflow.add_edge('planner', 'generator')<br/>"
            "workflow.add_edge('generator', 'validator')<br/>"
            "workflow.add_conditional_edges('validator', route_after_validation, ...)<br/>"
            "workflow.add_edge('healer', 'generator')  # self-healing loop",
            S['code']),

        h2("10.2 GENERATED GITHUB ACTIONS YAML (SAMPLE)"),
        p("For a Python repository with Docker support, the system generates the following "
          "GitHub Actions workflow structure:"),
        Paragraph(
            "name: CI/CD Pipeline<br/>"
            "on:<br/>"
            "  push: { branches: [main, master] }<br/>"
            "  pull_request: { branches: [main, master] }<br/><br/>"
            "jobs:<br/>"
            "  ci:<br/>"
            "    name: CI - Build &amp; Test<br/>"
            "    runs-on: ubuntu-latest<br/>"
            "    steps:<br/>"
            "      - uses: actions/checkout@v4<br/>"
            "      - uses: actions/setup-python@v5<br/>"
            "        with: { python-version: '3.12' }<br/>"
            "      - name: Cache pip dependencies<br/>"
            "        uses: actions/cache@v4<br/>"
            "      - name: Install Dependencies<br/>"
            "        run: pip install -r requirements.txt<br/>"
            "      - name: Lint<br/>"
            "        run: ruff check . &amp;&amp; mypy .<br/>"
            "      - name: Test<br/>"
            "        run: pytest --cov<br/>"
            "  docker:<br/>"
            "    needs: [ci]<br/>"
            "    if: github.ref == 'refs/heads/main'<br/>"
            "    steps: [checkout, buildx, docker-login, build-push]",
            S['code']),

        h2("10.3 ERROR CLASSIFICATION IN SELF-HEALING AGENT"),
        p("The _classify_error() method scores error logs against regex patterns for "
          "11 error categories and returns the highest-scoring category. Example patterns:"),
        Paragraph(
            "ErrorCategory.DEPENDENCY: ['ModuleNotFoundError', 'Cannot find module', ...]<br/>"
            "ErrorCategory.CONFIGURATION: ['yaml.scanner.ScannerError', 'SyntaxError', ...]<br/>"
            "ErrorCategory.PERMISSION: ['Permission denied', '403 Forbidden', ...]<br/>"
            "ErrorCategory.TEST_FAILURE: ['FAILED', 'AssertionError', 'Expected .+ but got', ...]",
            S['code']),

        h2("10.4 DOCKER COMPOSE STACK"),
        p("The production stack runs two containers on a shared ciforge-network bridge:"),
        p("• <b>ciforge-backend</b>: FastAPI on port 8000, with pipeline_data volume "
          "for ChromaDB persistence and ./src bind mount for development hot-reload.", 'bullet'),
        p("• <b>ciforge-frontend</b>: Next.js on port 3000, reaching the backend "
          "via Docker DNS (http://backend:8000) and externally via localhost:8000.", 'bullet'),
    ]
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════
    # 11. BIBLIOGRAPHY
    # ══════════════════════════════════════════════════════════
    story += [h1("11. BIBLIOGRAPHY"), hr(), sp(6)]

    refs = [
        ("1.", "LangGraph Documentation", "LangChain Inc. (2024). LangGraph: Building Stateful Multi-Actor Applications with LLMs. https://langchain-ai.github.io/langgraph/"),
        ("2.", "FastAPI", "Ramírez, S. (2024). FastAPI Documentation — High Performance, Easy to Learn, Fast to Code. https://fastapi.tiangolo.com/"),
        ("3.", "LiteLLM", "BerriAI. (2024). LiteLLM: Call 100+ LLMs using the OpenAI Input/Output Format. https://docs.litellm.ai/"),
        ("4.", "Pydantic v2", "Pydantic Services Inc. (2024). Pydantic Documentation v2. https://docs.pydantic.dev/"),
        ("5.", "ChromaDB", "Chroma Inc. (2024). Chroma — The Open-Source Embedding Database. https://docs.trychroma.com/"),
        ("6.", "structlog", "Schlawack, H. (2024). structlog: Structured Logging for Python. https://www.structlog.org/"),
        ("7.", "Docker Documentation", "Docker Inc. (2024). Docker Documentation — Build, Ship, and Run Any App, Anywhere. https://docs.docker.com/"),
        ("8.", "GitHub Actions Docs", "GitHub Inc. (2024). GitHub Actions Documentation. https://docs.github.com/en/actions"),
        ("9.", "GitLab CI/CD", "GitLab Inc. (2024). GitLab CI/CD Documentation. https://docs.gitlab.com/ee/ci/"),
        ("10.", "Jenkins User Handbook", "Jenkins Project. (2024). Jenkins User Documentation. https://www.jenkins.io/doc/"),
        ("11.", "12-Factor App", "Wiggins, A. et al. (2017). The Twelve-Factor App. https://12factor.net/"),
        ("12.", "OpenAI API Reference", "OpenAI. (2024). OpenAI API Reference. https://platform.openai.com/docs/api-reference"),
        ("13.", "Anthropic Claude API", "Anthropic. (2024). Claude API Documentation. https://docs.anthropic.com/"),
        ("14.", "Next.js Documentation", "Vercel Inc. (2024). Next.js Documentation. https://nextjs.org/docs"),
        ("15.", "PyYAML Documentation", "Simonov, K. (2024). PyYAML Documentation. https://pyyaml.org/wiki/PyYAMLDocumentation"),
    ]

    for num, title, detail in refs:
        row = Table([[
            Paragraph(num, S['normal']),
            Paragraph(f"<b>{title}</b> — {detail}", S['normal'])
        ]], colWidths=[0.35*inch, 5.7*inch])
        row.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(row)

    # ── Build ─────────────────────────────────────────────────
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"PDF written to: {out}")

build()