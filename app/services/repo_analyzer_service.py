"""
Repository Analyzer and AI Intelligence Service for Project Brain.
Provides:
1. Deep GitHub repository metadata, README, and tree fetching.
2. Directory structure parsing and hierarchy generation.
3. Offline heuristic purpose and architectural analysis.
4. Multi-provider AI API integration (Google Gemini, Groq, OpenAI).
"""

import os
import re
import base64
from typing import Dict, Any, List, Optional
import httpx
from app.core.config import settings


class RepoAnalyzerService:
    def __init__(self, owner: str, repo: str, token: Optional[str] = None):
        self.owner = owner.strip().strip("/")
        clean_repo = repo.strip().strip("/")
        if clean_repo.endswith(".git"):
            clean_repo = clean_repo[:-4]
        self.repo = clean_repo

        token = token or (settings.GITHUB_TOKEN or os.getenv("GITHUB_TOKEN", "")).strip().strip("'\"")
        self.headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "Project-Brain-Delivery-Memory/1.0",
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    async def fetch_full_details(self, db_files: Optional[List[str]] = None) -> Dict[str, Any]:
        """Fetch repo metadata, readme, and file tree."""
        metadata = await self._fetch_repo_metadata()
        default_branch = metadata.get("default_branch", "main")
        readme = await self._fetch_readme()
        tree_paths = await self._fetch_tree_paths(default_branch)

        # Fallback to database files if GitHub tree is empty
        if not tree_paths and db_files:
            tree_paths = db_files

        tree_hierarchy = self.build_tree_hierarchy(tree_paths)
        top_directories = self.analyze_top_directories(tree_paths)
        heuristic = self.generate_heuristic_purpose(metadata, tree_paths, readme)

        return {
            "owner": self.owner,
            "repo": self.repo,
            "full_name": f"{self.owner}/{self.repo}",
            "description": metadata.get("description") or heuristic.get("inferred_description", "No description provided."),
            "has_native_description": bool(metadata.get("description")),
            "default_branch": default_branch,
            "language": metadata.get("language") or heuristic.get("primary_language", "Unknown"),
            "topics": metadata.get("topics", []),
            "stars": metadata.get("stargazers_count", 0),
            "forks": metadata.get("forks_count", 0),
            "html_url": metadata.get("html_url", f"https://github.com/{self.owner}/{self.repo}"),
            "readme": readme,
            "total_files": len(tree_paths),
            "file_paths": tree_paths,
            "tree_hierarchy": tree_hierarchy,
            "top_directories": top_directories,
            "heuristic": heuristic,
        }

    async def _fetch_repo_metadata(self) -> Dict[str, Any]:
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}"
        try:
            async with httpx.AsyncClient(timeout=15.0, headers=self.headers) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    return resp.json()
        except Exception as e:
            print(f"[WARN] fetch_repo_metadata error: {e}")
        return {}

    async def _fetch_readme(self) -> str:
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/readme"
        try:
            headers = dict(self.headers)
            headers["Accept"] = "application/vnd.github.raw+json"
            async with httpx.AsyncClient(timeout=15.0, headers=headers) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    return resp.text
        except Exception as e:
            print(f"[WARN] fetch_readme raw error: {e}")

        try:
            async with httpx.AsyncClient(timeout=15.0, headers=self.headers) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    content = resp.json().get("content", "")
                    if content:
                        return base64.b64decode(content).decode("utf-8", errors="replace")
        except Exception:
            pass
        return ""

    async def _fetch_tree_paths(self, branch: str) -> List[str]:
        """Fetch recursive Git tree list."""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/trees/{branch}?recursive=1"
        try:
            async with httpx.AsyncClient(timeout=20.0, headers=self.headers) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    items = resp.json().get("tree", [])
                    return [item["path"] for item in items if item.get("type") in ("blob", "tree")]
        except Exception as e:
            print(f"[WARN] fetch_tree_paths error: {e}")
        return []

    @staticmethod
    def build_tree_hierarchy(paths: List[str], max_items: int = 400) -> Dict[str, Any]:
        """Construct a nested tree dict representing the directory structure."""
        root: Dict[str, Any] = {}
        for path in sorted(paths)[:max_items]:
            parts = path.strip("/").split("/")
            curr = root
            for part in parts[:-1]:
                if part not in curr or not isinstance(curr[part], dict):
                    curr[part] = {}
                curr = curr[part]
            leaf = parts[-1]
            if leaf not in curr:
                curr[leaf] = None
        return root

    @staticmethod
    def analyze_top_directories(paths: List[str]) -> List[Dict[str, Any]]:
        """Summarize top-level directories, counts, and likely responsibilities."""
        dir_counts: Dict[str, int] = {}
        dir_extensions: Dict[str, set] = {}

        for p in paths:
            parts = p.strip("/").split("/")
            if len(parts) > 1:
                top_dir = parts[0]
                dir_counts[top_dir] = dir_counts.get(top_dir, 0) + 1
                ext = os.path.splitext(p)[1].lower()
                if ext:
                    dir_extensions.setdefault(top_dir, set()).add(ext)

        known_roles = {
            ".github": "CI/CD workflows, GitHub Actions, and issue/PR templates",
            ".devcontainer": "Dev container and Codespaces development environment",
            ".vscode": "Visual Studio Code editor workspace configuration",
            "src": "Primary application source code implementation",
            "app": "Application core backend, routes, or framework entrypoints",
            "frontend": "Frontend user interface, pages, and components",
            "backend": "Backend server API, services, and database models",
            "dist": "Built production distribution bundles and compiled artifacts",
            "query": "CodeQL query packs, query definitions, and AST inspection",
            "script": "Automation scripts, tooling, and build utilities",
            "scripts": "Automation scripts, tooling, and build utilities",
            "test": "Unit tests, integration suites, and test fixtures",
            "tests": "Unit tests, integration suites, and test fixtures",
            "testdata": "Test fixtures, mock payloads, and sample repositories",
            "docs": "Project documentation, architecture diagrams, and guides",
            "public": "Static assets, favicon, images, and public web resources",
            "components": "Modular UI components and presentation widgets",
            "models": "Database ORM schemas, data transfer objects, and types",
            "routes": "HTTP API route endpoints and controller definitions",
        }

        results = []
        for d, count in sorted(dir_counts.items(), key=lambda x: x[1], reverse=True):
            exts = list(dir_extensions.get(d, set()))[:4]
            role = known_roles.get(d, f"Contains {count} project files ({', '.join(exts) if exts else 'mixed'})")
            results.append({
                "directory": d,
                "file_count": count,
                "extensions": exts,
                "role": role,
            })
        return results

    @staticmethod
    def generate_heuristic_purpose(metadata: Dict[str, Any], paths: List[str], readme: str) -> Dict[str, Any]:
        """Infer project type, purpose, and key technologies without an AI key."""
        lower_paths = [p.lower() for p in paths]
        repo_name = metadata.get("name", "").lower()
        desc = metadata.get("description", "")

        # Detect project category
        is_action = "action.yml" in lower_paths or "action.yaml" in lower_paths or "action" in repo_name
        is_react = any("react" in p or p.endswith((".tsx", ".jsx")) for p in lower_paths)
        is_python = any(p.endswith((".py", "requirements.txt", "pyproject.toml")) for p in lower_paths)
        is_node = any(p in lower_paths for p in ["package.json", "tsconfig.json"])
        is_codeql = any("codeql" in p for p in lower_paths) or "codeql" in repo_name

        tech_stack = []
        if is_codeql: tech_stack.append("CodeQL Variant Analysis")
        if is_action: tech_stack.append("GitHub Actions")
        if is_python: tech_stack.append("Python")
        if is_react: tech_stack.append("React / TypeScript")
        if is_node: tech_stack.append("Node.js")

        # Inferred Purpose
        if is_action and is_codeql:
            purpose = (
                "Automated GitHub Action designed to run large-scale CodeQL Multi-Repository Variant Analysis (MRVA). "
                "It enables security engineers to detect vulnerabilities, analyze queries across thousands of target repositories, "
                "and aggregate security findings automatically in CI/CD pipelines."
            )
        elif is_action:
            purpose = "Reusable GitHub Action automated workflow component for continuous integration, delivery, or repository task management."
        elif is_react and is_python:
            purpose = "Full-stack application combining a Python backend with a reactive web user interface."
        elif is_node:
            purpose = "Node.js application or library providing modular software services, tooling, or runtime components."
        elif is_python:
            purpose = "Python software package for data analysis, automation, or backend services."
        else:
            purpose = "Software repository providing tools, architectural components, and automated scripts."

        # Extract first 2-3 sentences of README if available
        readme_summary = ""
        if readme:
            lines = [l.strip() for l in readme.split("\n") if l.strip() and not l.startswith("#") and not l.startswith("[!") and not l.startswith("```")]
            if lines:
                readme_summary = " ".join(lines[:3])
                if len(readme_summary) > 280:
                    readme_summary = readme_summary[:277] + "..."

        return {
            "inferred_description": purpose,
            "detected_stack": tech_stack,
            "readme_summary": readme_summary,
            "is_action": is_action,
            "is_codeql": is_codeql,
            "is_python": is_python,
            "is_node": is_node,
        }

    async def call_ai_analyzer(
        self,
        provider: str,
        api_key: str,
        metadata: Dict[str, Any],
        paths: List[str],
        readme: str,
        recent_commits: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Call Gemini, Groq, or OpenAI to generate a deep project analysis."""
        provider = provider.lower().strip()
        api_key = api_key.strip()
        if not api_key:
            raise ValueError("API Key is required to run AI analysis.")

        # Construct concise context
        files_sample = "\n".join(paths[:120])
        commits_sample = ""
        if recent_commits:
            commits_sample = "\n".join(
                [f"- {c.get('sha', '')[:7]}: {c.get('message', '').splitlines()[0]}" for c in recent_commits[:8]]
            )

        readme_snippet = readme[:1500] if readme else "No README available."

        prompt = f"""You are an elite principal software architect and technical lead.
Analyze this GitHub repository based on its structure, files, commits, and documentation:

Repository: {self.owner}/{self.repo}
GitHub Description: {metadata.get('description', 'None')}
Primary Language: {metadata.get('language', 'Unknown')}
Topics: {', '.join(metadata.get('topics', [])) or 'None'}

README Snippet:
\"\"\"
{readme_snippet}
\"\"\"

Recent Commits:
{commits_sample or 'None recorded'}

File Tree (Sample of first 120 files):
{files_sample}

Provide an exhaustive, highly structured architectural analysis with these exact 4 sections in GitHub Flavored Markdown:

### 1. 🎯 Executive Purpose & Problem Solved
Clearly define:
- What does this project do?
- What real-world problem does it solve and why was it created?
- Who is the target audience (e.g., security researchers, frontend devs, DevOps)?

### 2. 🏗️ System Architecture & Core Technology Stack
Break down:
- Architecture pattern (e.g., CI/CD Action, Monorepo, Microservice, Client-Server)
- Core languages, runtime, and frameworks
- How major components communicate

### 3. 📂 Annotated Directory Structure
Create a formatted Markdown table detailing each key folder and its architectural responsibility:
| Directory / File | Type | Architectural Responsibility |
| :--- | :--- | :--- |
(Explain all significant top-level folders like .github, src, query, dist, etc.)

### 4. ⚡ Key Capabilities & Developer Entry Points
- Core features and workflows
- The exact entry point files where execution begins (e.g. index.ts, action.yml)
- How to get started or run tests
"""

        if provider in ("gemini", "google"):
            return await self._call_gemini(api_key, prompt)
        elif provider in ("groq",):
            return await self._call_groq(api_key, prompt)
        elif provider in ("openai",):
            return await self._call_openai(api_key, prompt)
        else:
            # Default to gemini if unrecognized
            return await self._call_gemini(api_key, prompt)

    async def _call_gemini(self, api_key: str, prompt: str) -> Dict[str, Any]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2048}
        }
        async with httpx.AsyncClient(timeout=40.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return {"success": True, "analysis": text, "provider": "Google Gemini 1.5 Flash"}
            else:
                error_msg = resp.text
                try:
                    error_msg = resp.json().get("error", {}).get("message", resp.text)
                except Exception:
                    pass
                return {"success": False, "error": f"Gemini API Error ({resp.status_code}): {error_msg}"}

    async def _call_groq(self, api_key: str, prompt: str) -> Dict[str, Any]:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
        async with httpx.AsyncClient(timeout=40.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                text = resp.json()["choices"][0]["message"]["content"]
                return {"success": True, "analysis": text, "provider": "Groq Llama 3.3 70B"}
            else:
                return {"success": False, "error": f"Groq API Error ({resp.status_code}): {resp.text}"}

    async def _call_openai(self, api_key: str, prompt: str) -> Dict[str, Any]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
        async with httpx.AsyncClient(timeout=40.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                text = resp.json()["choices"][0]["message"]["content"]
                return {"success": True, "analysis": text, "provider": "OpenAI GPT-4o Mini"}
            else:
                return {"success": False, "error": f"OpenAI API Error ({resp.status_code}): {resp.text}"}

