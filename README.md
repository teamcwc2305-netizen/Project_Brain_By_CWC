# 🧠 Project Brain
### Delivery Memory & Blast Radius Engine

> **Preserving institutional knowledge. Understanding code ownership. Predicting the impact of every change.**
>
> Project Brain is a deterministic software intelligence platform that transforms GitHub repository history into actionable engineering knowledge. It helps development teams understand code ownership, discover historical dependencies, identify potential risks, and make informed engineering decisions — backed by verifiable Git history rather than fabricated explanations.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" />
  <img src="https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi" />
  <img src="https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?logo=streamlit" />
  <img src="https://img.shields.io/badge/Graph-NetworkX-005C8A" />
  <img src="https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite" />
  <img src="https://img.shields.io/badge/AI-Optional-purple" />
  <img src="https://img.shields.io/badge/License-MIT-green" />
</p>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [The Problem](#-the-problem)
- [Our Solution](#-our-solution)
- [Core Features](#-core-features)
- [How Project Brain Works](#-how-project-brain-works)
- [System Architecture](#️-system-architecture)
- [Technology Stack](#️-technology-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Environment Configuration](#-environment-configuration)
- [Running the Application](#-running-the-application)
- [Application Modules](#-application-modules)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [Testing](#-testing)
- [Security](#-security)
- [Future Improvements & Roadmap](#-future-improvements--roadmap)
- [Engineering Team](#-engineering-team)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🚀 Overview

Software development teams continuously generate valuable knowledge through commits, pull requests, issues, code changes, and collaboration.

However, this knowledge is often scattered across repositories and individual developers.

When experienced developers leave, teams switch ownership, or projects undergo major refactoring, important architectural knowledge disappears.

**Project Brain** addresses this challenge by building a repository intelligence system that extracts, connects, and analyzes historical development information.

It creates a relational knowledge graph connecting:

- Developers and contributors
- Git commits
- Source code files
- Pull requests
- Issues
- Historical file dependencies

Using this information, Project Brain helps answer critical engineering questions:

- Who has worked on this file?
- Who understands this module best?
- What other files might be affected if I modify this component?
- Which developers should review a particular change?
- Which test suites should be considered before deployment?
- Where does the project have knowledge concentration risks?
- What is the development history of a particular component?

**Our core philosophy: Deterministic intelligence first, optional AI assistance second.**

All ownership, history, and impact analysis is grounded in verifiable repository information. Optional AI providers are used for additional architectural insights.

---

## ❗ The Problem

Modern software teams face several challenges that negatively affect development speed, software quality, and project continuity.

### 1. Institutional Amnesia

When developers leave an organization or move to another team, their understanding of the architecture and codebase often leaves with them.

### 2. Invisible Code Dependencies

A change in one source file can unexpectedly affect other files that have historically changed alongside it.

Traditional code navigation does not necessarily reveal these historical relationships.

### 3. Unclear Code Ownership

Teams frequently struggle to identify developers who have the most experience with particular modules or components.

### 4. Regression Risks

Developers may modify critical files without understanding their historical dependencies or associated test coverage.

### 5. Knowledge Concentration

Some important components may depend heavily on the knowledge of a single contributor, creating operational bottlenecks.

### 6. Unreliable AI-generated Explanations

LLM-based development tools can generate convincing but unsupported explanations about code ownership, historical decisions, and dependencies.

Project Brain aims to solve these challenges using traceable, evidence-based engineering intelligence.

---

## 💡 Our Solution

Project Brain converts repository history into a structured knowledge system.

It collects available GitHub information, processes repository relationships, and builds a graph using NetworkX.

The resulting intelligence powers multiple analytical modules:

| Module | Purpose |
|---|---|
| Knowledge Graph | Visualizes relationships between developers, commits, files, issues, and PRs |
| Impact Analysis | Identifies potentially affected files and historical dependencies |
| Ownership Intelligence | Identifies contributors with relevant file history |
| Knowledge Risk | Detects files with concentrated contributor ownership |
| Project Search | Provides evidence-backed answers to repository queries |
| AI Architecture Analyzer | Generates optional architectural summaries and directory explanations |

---

## ⚡ Core Features

### 🕸️ 1. Deterministic Knowledge Graph

Project Brain builds an interactive repository knowledge graph using NetworkX.

It connects different repository entities through their actual relationships.

**Graph entities include:**

- Developers
- Commits
- Files
- Issues
- Pull Requests

**Key capabilities:**

- Interactive graph exploration
- Relationship visualization
- Developer-to-file mapping
- Historical contribution tracking
- 2D/3D graph visualization

### 💥 2. Blast Radius & Impact Analysis

Understand the potential consequences of modifying a particular file before making changes.

Project Brain analyzes:

- Historical co-change relationships
- Files frequently modified together
- Relevant contributors
- Potentially associated test files
- Historical dependency patterns

Users can provide:

- A single file path
- A proposed set of changed files
- A unified Git diff

The engine evaluates available historical evidence and identifies potentially affected components.

**Goal:** Help developers make safer changes and reduce unexpected regressions.

### 🚨 3. Knowledge Concentration & Bus-Factor Analysis

Identify critical project components that depend heavily on a small number of contributors.

The system analyzes:

- Single-contributor files
- Knowledge concentration
- Critical ownership bottlenecks
- Files requiring knowledge sharing
- Potential maintenance risks

This helps engineering leads understand where knowledge transfer and documentation are most important.

### 🔍 4. Ground-Truth Project Search

Search repository information using natural-language-style queries.

Example queries:

```text
Who worked on auth.py?

Show the history of app/main.py.

Who contributed to the database module?

Find PR #12.

Show commit fa79561.

Which files frequently change together?
```

Project Brain returns available repository evidence, including relevant authors, commits, file references, and GitHub URLs.

It does not invent missing commits or contributor relationships.

### 🤖 5. Optional AI Architectural Intelligence

Project Brain also supports optional AI-assisted architectural analysis.

**Supported providers:**

- Google Gemini
- Groq (Llama 3.3)
- OpenAI

The AI module can assist with:

- Architectural overviews
- Directory structure explanations
- Module descriptions
- High-level project summaries
- Developer onboarding guidance

AI-generated architectural explanations are separate from the deterministic ownership and impact-analysis engine.

AI provider credentials are optional.

### 🔐 6. Secure Authentication

The application includes local user registration and session management.

Security mechanisms include:

- Password hashing using `hashlib.scrypt`
- Constant-time HMAC validation
- Session management
- Environment-based configuration

### 📊 7. Project History & Repository Intelligence

Explore historical repository activity through a centralized dashboard.

Analyze available:

- Commit history
- Developer contributions
- Issues
- Pull requests
- File activity
- Knowledge concentration

---

## ⚙️ How Project Brain Works

The application follows a repository ingestion and intelligence pipeline.

**Step 1: Repository Input**

The user provides a GitHub repository URL.

**Step 2: GitHub Data Collection**

The GitHub Collector retrieves available repository information through the GitHub REST API.

**Step 3: Data Processing**

The Import Service processes collected information, normalizes entities, and extracts relationships.

**Step 4: Knowledge Graph Construction**

NetworkX constructs a directed graph connecting contributors, commits, files, issues, and pull requests.

**Step 5: Persistent Storage**

Repository information and application data are stored using SQLite and SQLAlchemy.

**Step 6: Intelligence Processing**

The application executes deterministic analysis for:

- Ownership mapping
- Historical co-change relationships
- Blast radius estimation
- Knowledge concentration
- Project search

**Step 7: Interactive Visualization**

The Streamlit frontend displays the results through interactive dashboards, search interfaces, and graph visualizations.

**Step 8: Optional AI Analysis**

When configured, an AI provider can generate additional architectural insights.

---

## 🏗️ System Architecture

```text
                  USER
                   |
                   v
        +----------------------+
        |   Streamlit Frontend |
        |      Port 8501       |
        +----------------------+
                   |
             Internal REST
                   |
                   v
        +----------------------+
        |    FastAPI Backend   |
        |      Port 8000       |
        +----------------------+
                   |
       +-----------+-----------+
       |           |           |
       v           v           v
  GitHub       Import      Search &
 Collector     Service     Impact
       |           |           |
       +-----------+-----------+
                   |
                   v
        +----------------------+
        |   NetworkX Graph     |
        |  Repository Mapping  |
        +----------------------+
                   |
                   v
        +----------------------+
        |    SQLite Database   |
        |   Persistent Storage |
        +----------------------+
                   |
                   v
        +----------------------+
        |  Intelligence Output |
        | Graph / Risk / Search|
        +----------------------+
                   |
                   v
        +----------------------+
        |  Optional AI Layer   |
        | Gemini / Groq / OpenAI|
        +----------------------+
```

### Architecture Components

| Component | Responsibility |
|---|---|
| GitHub Collector | Retrieves repository information asynchronously |
| Import Service | Processes and normalizes repository data |
| Graph Service | Constructs and manages NetworkX relationships |
| Impact Service | Performs historical change-impact analysis |
| Search Service | Retrieves relevant repository evidence |
| Database Layer | Stores repository and application information |
| FastAPI | Exposes backend functionality through REST APIs |
| Streamlit | Provides the interactive user interface |
| AI Integration | Provides optional architectural analysis |

---

## 🛠️ Technology Stack

### Backend

| Technology | Usage |
|---|---|
| Python 3.10+ | Core programming language |
| FastAPI | REST API development |
| Uvicorn | ASGI application server |
| SQLAlchemy | Database ORM |
| SQLite | Persistent database |
| HTTPX | Asynchronous HTTP communication |
| Pydantic | Data validation |

### Frontend

| Technology | Usage |
|---|---|
| Streamlit | Interactive web application |
| HTML / CSS / JavaScript | Custom interface components |
| Vis.js | Interactive graph visualization |
| Three.js | 3D visualization |

### Graph & Data Processing

| Technology | Usage |
|---|---|
| NetworkX | Graph construction and analysis |
| Python AST | Python source structure analysis |
| Regular Expressions | Text and token normalization |

### AI Integration

- Google Gemini
- Groq
- OpenAI

### Database & Infrastructure

- SQLite
- SQLAlchemy
- GitHub REST API
- Render
- Git and GitHub

---

## 📂 Project Structure

```text
Project_Brain_By_CWC/
│
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── repositories.py
│   │       ├── history.py
│   │       ├── impact.py
│   │       ├── graph.py
│   │       └── search.py
│   │
│   ├── collectors/
│   │   └── collector.py
│   │
│   ├── core/
│   │   └── config.py
│   │
│   ├── db/
│   │   ├── models.py
│   │   └── session.py
│   │
│   ├── schemas/
│   │
│   ├── services/
│   │   ├── graph_service.py
│   │   ├── impact_service.py
│   │   └── search_service.py
│   │
│   ├── utils/
│   │
│   └── main.py
│
├── frontend/
│   ├── pages/
│   │   ├── 0_Description.py
│   │   ├── 1_Project_History.py
│   │   ├── 2_Project_Search.py
│   │   ├── 3_Impact_Analysis.py
│   │   ├── 4_Knowledge_Graph.py
│   │   └── 5_About_Us.py
│   │
│   ├── auth.py
│   ├── repo_manager.py
│   ├── sidebar_nav.py
│   └── streamlit_app.py
│
├── tests/
│
├── .env.example
├── .gitignore
├── requirements.txt
├── test_live.py
└── README.md
```

*Note: The tree represents the intended logical organization. Individual filenames can vary with the actual implementation.*

---

## 🚀 Getting Started

Follow these steps to run Project Brain locally.

### 1. Prerequisites

Make sure you have the following installed:

- Python 3.10 or higher
- Git
- pip
- A GitHub account

**Recommended:** A GitHub Personal Access Token to avoid unauthenticated API rate limits.

### 2. Clone the Repository

```bash
git clone https://github.com/teamcwc2305-netizen/Project_Brain_By_CWC.git

cd Project_Brain_By_CWC
```

### 3. Create a Virtual Environment

**Windows:**

```bash
python -m venv venv

venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv venv

source venv/bin/activate
```

### 4. Install Dependencies

```bash
python -m pip install --upgrade pip

pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root directory.

Use the following configuration:

```env
# Application Configuration
APP_NAME="Project Brain"

# Database
DATABASE_URL="sqlite:///./project_brain.db"

# Backend Configuration
API_HOST="127.0.0.1"
API_PORT=8000

# Frontend Backend Connection
BACKEND_URL="http://127.0.0.1:8000"

# GitHub Integration
GITHUB_TOKEN=""

# Optional AI Provider Configuration
GEMINI_API_KEY=""
GROQ_API_KEY=""
OPENAI_API_KEY=""
```

**Important:**

- Add your GitHub token to `GITHUB_TOKEN`.
- AI API keys are optional.
- Never upload your actual `.env` file to GitHub.
- Keep all API credentials private.

---

## 💻 Running the Application

Project Brain consists of two main processes: the FastAPI backend and the Streamlit frontend.

Open two separate terminals in the project root directory.

### Terminal 1: Start the Backend

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend:

```text
http://127.0.0.1:8000
```

Interactive Swagger Documentation:

```text
http://127.0.0.1:8000/docs
```

Health Check:

```text
http://127.0.0.1:8000/health
```

### Terminal 2: Start the Frontend

```bash
python -m streamlit run frontend/streamlit_app.py
```

Frontend:

```text
http://localhost:8501
```

Once both services are running, open the frontend in your browser.

---

## 🖥️ Application Modules

### 1. Project Overview

Provides an introduction to the repository and its architectural information.

### 2. Project History

Explore historical repository activity, commits, issues, pull requests, contributor activity, and knowledge risks.

### 3. Project Search

Search repository information and retrieve evidence-backed results.

### 4. Impact Analysis

Analyze proposed changes and identify historically related files, relevant contributors, and potential test targets.

### 5. Knowledge Graph

Explore the interactive relationship graph connecting contributors, files, commits, issues, and pull requests.

### 6. About Us

Learn about the engineering team, project mission, and development background.

---

## 🔌 API Documentation

Project Brain uses FastAPI to expose backend functionality through REST endpoints.

Once the backend is running, access the automatically generated API documentation:

**Swagger UI:**

http://127.0.0.1:8000/docs

**ReDoc:**

http://127.0.0.1:8000/redoc

The backend is organized around repository management, history, impact analysis, graph operations, and project search.

Refer to the actual API documentation for available endpoints, request formats, and response schemas.

---

## 🌐 Deployment on Render

Project Brain can be deployed using Render.

The recommended production configuration is to deploy the backend and frontend as separate web services. This allows each process to receive its own port, environment variables, and health monitoring.

### Backend Deployment

**Runtime:** Python 3

**Build Command:**

```bash
pip install -r requirements.txt
```

**Start Command:**

```bash
gunicorn -w 1 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT
```

Configure the following environment variables:

```env
PYTHONPATH=.
GITHUB_TOKEN=your_github_token
DATABASE_URL=your_database_url
```

### Frontend Deployment

**Runtime:** Python 3

**Build Command:**

```bash
pip install -r requirements.txt
```

**Start Command:**

```bash
python -m streamlit run frontend/streamlit_app.py --server.port $PORT --server.address 0.0.0.0
```

Configure:

```env
BACKEND_URL=https://your-backend-service.onrender.com
```

Replace the backend URL with your actual deployed backend address.

**Deployment Notes:**

- Configure persistent storage for SQLite if using local database files in production.
- Use a persistent database service when required.
- Configure CORS appropriately for the frontend origin.
- Keep GitHub and AI credentials in Render environment variables.
- Ensure the backend is accessible from the frontend service.

---

## 🧪 Testing

Project Brain includes automated tests for validating core functionality.

Run the test suite from the project root:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Testing focuses on areas such as:

- Repository data processing
- Graph construction
- Duplicate handling
- Relationship management
- Risk calculation
- Core service functionality

Run the tests after making changes to ensure existing functionality remains stable.

---

## 🔐 Security

Security is an important consideration in Project Brain.

The application follows several security practices:

- Password hashing with `hashlib.scrypt`.
- Constant-time HMAC comparison.
- Environment-based secret management.
- Separation of authentication and application configuration.
- No hardcoded API credentials.
- GitHub token-based API authentication.

**Recommended security practices:**

1. Never commit `.env` files.
2. Use read-only GitHub permissions wherever possible.
3. Avoid exposing API credentials in frontend code.
4. Restrict production CORS origins.
5. Use HTTPS for deployed services.
6. Configure persistent and secure session handling.

---

## 🔮 Future Improvements & Roadmap

While **Project Brain** delivers a robust, deterministic institutional memory engine, the next phase focuses on evolving it into a comprehensive, enterprise-grade software delivery intelligence platform.

The following engineering enhancements are planned:

### 1. 🧬 Multi-Language AST Parsing & Semantic Call-Graphs

**Moving beyond file-level relationships to function-level code intelligence.**

- **Multi-Language Static Code Analysis:** Extend the existing Python AST-based analysis using [Tree-sitter](https://tree-sitter.github.io/tree-sitter/) to support Python, TypeScript, Java, and Go.
- **Semantic Call-Graphs:** Build relationships between functions, classes, methods, and modules to understand actual code execution dependencies.
- **Function-Level Blast Radius:** Identify exactly which functions and classes may be affected by a proposed code change rather than analyzing entire file paths.
- **Cross-Module Dependency Mapping:** Track relationships across different modules and packages to improve impact analysis precision.

**Expected Outcome:** More granular dependency intelligence and more accurate change-impact analysis.

### 2. ⚡ Real-Time Webhook & CI/CD Integrations

**Bringing Project Brain directly into the development workflow.**

- **GitHub Actions Integration:** Develop a native GitHub Action that automatically analyzes incoming Pull Requests.
- **Automated PR Risk Reports:** Add a PR bot that comments on proposed changes with:
  - Detected blast radius.
  - Recommended historical code reviewers.
  - Potentially affected modules.
  - Recommended regression test suites.
  - Knowledge concentration warnings.
- **Live Event Ingestion:** Replace periodic polling and batch imports with real-time GitHub Webhook listeners.
- **Webhook Event Support:** Process events such as `push`, `pull_request`, and `issues`.
- **Continuous Repository Synchronization:** Keep repository intelligence updated as development activity occurs.

**Expected Outcome:** Project Brain becomes an active participant in the software development lifecycle instead of just a standalone analysis dashboard.

### 3. 🗄️ Enterprise Graph Database & Data Scaling

**Preparing Project Brain for large repositories and enterprise monorepos.**

- **Neo4j / Memgraph Integration:** Introduce native graph database support for scalable relationship storage and advanced graph queries.
- **Cypher Query Support:** Enable expressive graph traversal and relationship analysis using Cypher.
- **Scalable Storage Architecture:** Gradually migrate large-scale repository graph data beyond local SQLite and in-memory NetworkX processing.
- **Background Task Workers:** Introduce Celery and Redis-based task queues to handle intensive repository imports and analysis asynchronously.
- **Large Repository Support:** Optimize ingestion and graph processing for enterprise repositories containing 100,000+ commits.
- **Incremental Graph Updates:** Process newly available commits and repository changes without repeatedly rebuilding the entire graph.

**Expected Outcome:** Better performance, scalability, and reliability when handling large and complex codebases.

### 4. 🔒 Multi-Tenant Role-Based Access Control (RBAC)

**Transforming Project Brain into a secure, organization-ready engineering intelligence platform.**

- **Organization Workspaces:** Introduce multi-tenant accounts where different companies and development teams can manage their own projects.
- **Repository Isolation:** Ensure private repository data and graph analyses remain isolated between organizations.
- **Role-Based Access Control:** Introduce roles such as:
  - Organization Admin
  - Engineering Lead
  - Developer
  - Viewer
- **GitHub OAuth 2.0:** Enable secure authentication through GitHub accounts.
- **Google Workspace SSO:** Support enterprise single sign-on through Google Workspace.
- **Access Permissions:** Provide configurable permissions for repositories, project history, impact analysis, and administrative operations.

**Expected Outcome:** A secure, collaborative platform suitable for organizations managing multiple development teams and private repositories.

### 5. 📊 Advanced Delivery Metrics (DORA & Team Health)

**Connecting repository intelligence with engineering performance and organizational resilience.**

- **DORA Metrics Dashboard:** Introduce engineering delivery metrics to understand software delivery performance.
- **Lead Time for Changes:** Measure the time between code changes and production deployment.
- **Deployment Frequency:** Track how frequently software is deployed to production.
- **Change Failure Rate:** Measure the proportion of deployments that result in failures or require remediation.
- **Time to Restore Service:** Track how quickly services recover after production incidents, when incident data is available.
- **Knowledge Silo Detection:** Identify critical modules that depend heavily on a limited number of contributors.
- **Burnout & Knowledge Concentration Alerts:** Provide proactive warnings about contributor bottlenecks and concentrated ownership patterns.
- **Team Health Insights:** Help engineering leads identify areas where knowledge sharing, documentation, and ownership distribution should improve.

**Expected Outcome:** Help engineering teams understand not only how their codebase evolves, but also how sustainably their engineering organization operates.

### 🗺️ Roadmap Summary

| Enhancement | Planned Direction | Priority |
|---|---|---|
| Multi-Language AST | Tree-sitter and semantic call-graphs | High |
| Function-Level Impact | Function and class dependency mapping | High |
| GitHub Actions | Automated PR risk analysis | High |
| Real-Time Webhooks | Continuous repository synchronization | High |
| Graph Database | Neo4j / Memgraph integration | Medium |
| Background Workers | Celery and Redis | Medium |
| Enterprise RBAC | Organization workspaces and permissions | High |
| OAuth / SSO | GitHub and Google Workspace | Medium |
| DORA Metrics | Engineering delivery dashboard | Medium |
| Team Health | Knowledge silo and concentration alerts | Medium |

*These are planned enhancements and are not represented as currently implemented features.*

---

## 👥 Engineering Team — Code with Caos

Built with collaboration, creativity, and engineering innovation.

| Team Member | Responsibility |
|---|---|
| **Divyanshu Mehta** | Core Architecture & Project Lead |
| **Vivek Joshi** | Backend Development & Graph Algorithms |
| **Neelabh Raj Singh** | Frontend Development & UI Engineering |
| **Kamal Pandey** | Data Collection & Integrations |
| **Ashish Pandey** | Quality Assurance & Infrastructure |

---

## 🤝 Contributing

Contributions, suggestions, and improvements are welcome.

To contribute:

1. Fork the repository.
2. Create a feature branch.
3. Implement your changes.
4. Test your implementation.
5. Commit your changes.
6. Submit a Pull Request.

Example:

```bash
git checkout -b feature/new-feature

git add .

git commit -m "Add new feature"

git push origin feature/new-feature
```

---

## 📄 License

This project is licensed under the **MIT License**.

You are free to use, modify, distribute, and contribute to this project under the terms of the MIT License.

---

## ⭐ Support the Project

If you find Project Brain useful or interesting:

- Give the repository a ⭐ Star.
- Fork the repository.
- Share your feedback.
- Contribute new features.
- Report bugs and suggest improvements.

**GitHub Repository:**

https://github.com/teamcwc2305-netizen/Project_Brain_By_CWC

---

<p align="center">

### 🧠 Project Brain

**Because engineering knowledge should never leave with the developer.**

*Built with ❤️ by Code with Caos.*

</p>
