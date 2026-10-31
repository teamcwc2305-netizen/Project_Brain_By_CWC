import os
import re
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
import httpx
from app.core.config import settings
from app.utils.text_normalization import extract_issue_numbers

class GitHubCollector:
    def __init__(self, owner: str, repo: str):
        self.owner = owner.strip().strip("/")
        
        clean_repo = repo.strip().strip("/")
        if clean_repo.endswith(".git"):
            clean_repo = clean_repo[:-4]
        self.repo = clean_repo
        
        self.base_url = f"https://api.github.com/repos/{self.owner}/{self.repo}"
        
        token = (settings.GITHUB_TOKEN or os.getenv("GITHUB_TOKEN", "")).strip().strip("'\"")
        
        self.headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "Project-Brain-Delivery-Memory/1.0",
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    @staticmethod
    def _parse_timestamp(ts: Optional[str]) -> datetime:
        """Parse ISO timestamps from GitHub into naive UTC datetimes."""
        if not ts:
            return datetime.utcnow()
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=None)
        except Exception:
            try:
                return datetime.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S")
            except Exception:
                return datetime.utcnow()

    async def fetch_repo_overview(self) -> Dict[str, int]:
        """Fetch total commit, open issue, and open PR counts for the repo."""
        overview = {"total_commits": 0, "open_issues": 0, "open_prs": 0}
        async with httpx.AsyncClient(timeout=20.0, headers=self.headers) as client:
            try:
                c_resp = await client.get(f"{self.base_url}/commits", params={"per_page": 1})
                if c_resp.status_code == 200:
                    link = c_resp.headers.get("link", "")
                    pages = re.findall(r"page=(\d+)", link)
                    if pages:
                        overview["total_commits"] = int(pages[-1])
                    elif isinstance(c_resp.json(), list):
                        overview["total_commits"] = len(c_resp.json())
            except Exception as e:
                print(f"[WARN] fetch_repo_overview commits error: {e}")

            try:
                iss_resp = await client.get(
                    "https://api.github.com/search/issues",
                    params={"q": f"repo:{self.owner}/{self.repo} is:issue is:open", "per_page": 1}
                )
                if iss_resp.status_code == 200:
                    overview["open_issues"] = iss_resp.json().get("total_count", 0)
            except Exception as e:
                print(f"[WARN] fetch_repo_overview issues error: {e}")

            try:
                pr_resp = await client.get(f"{self.base_url}/pulls", params={"state": "open", "per_page": 1})
                if pr_resp.status_code == 200:
                    link = pr_resp.headers.get("link", "")
                    pages = re.findall(r"page=(\d+)", link)
                    if pages:
                        overview["open_prs"] = int(pages[-1])
                    elif isinstance(pr_resp.json(), list):
                        overview["open_prs"] = len(pr_resp.json())
            except Exception as e:
                print(f"[WARN] fetch_repo_overview prs error: {e}")

        return overview

    # Commit collection

    async def fetch_commits(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch recent commits along with changed file paths."""
        async with httpx.AsyncClient(timeout=25.0, headers=self.headers) as client:
            try:
                resp = await client.get(f"{self.base_url}/commits", params={"per_page": min(limit, 100)})
            except Exception as e:
                print(f"[WARN] fetch_commits network error for {self.owner}/{self.repo}: {e}")
                return []

            if resp.status_code != 200:
                print(f"[WARN] GitHub commits API returned {resp.status_code}: {resp.text[:150]}")
                return []

            commits_data = resp.json()
            if not isinstance(commits_data, list):
                return []

            # Limit parallel detail requests to prevent hitting secondary rate limits
            semaphore = asyncio.Semaphore(5)

            async def get_detail_with_fallback(c_item: Dict[str, Any]) -> Dict[str, Any]:
                sha = c_item.get("sha", "")
                commit_block = c_item.get("commit", {}) or {}
                author_block = commit_block.get("author", {}) or {}
                author_login = (c_item.get("author") or {}).get("login") or author_block.get("name") or "Unknown"

                # Keep list-level metadata so the commit is recorded even if detail fetching fails
                fallback = {
                    "sha": sha,
                    "message": commit_block.get("message", "No commit message"),
                    "author": author_login,
                    "author_login": author_login,
                    "timestamp": self._parse_timestamp(author_block.get("date")),
                    "source_url": c_item.get("html_url", f"https://github.com/{self.owner}/{self.repo}/commit/{sha}"),
                    "files": [],
                }

                # Attempt to retrieve changed file list for blast-radius tracking
                try:
                    async with semaphore:
                        detail = await self._fetch_commit_details(client, sha)
                        if detail:
                            return detail
                except Exception:
                    pass

                return fallback

            # Fetch individual commit details concurrently
            results = await asyncio.gather(*[get_detail_with_fallback(c) for c in commits_data[:limit] if "sha" in c])
            return [r for r in results if r is not None]

    async def _fetch_commit_details(self, client: httpx.AsyncClient, sha: str) -> Optional[Dict[str, Any]]:
        """Fetch individual commit payload to extract modified file names."""
        try:
            resp = await client.get(f"{self.base_url}/commits/{sha}")
            if resp.status_code != 200:
                return None
            data = resp.json()
            commit_block = data.get("commit", {}) or {}
            author_block = commit_block.get("author", {}) or {}
            author_login = (data.get("author") or {}).get("login") or author_block.get("name") or "Unknown"

            return {
                "sha": data["sha"],
                "message": commit_block.get("message", "No commit message"),
                "author": author_login,
                "author_login": author_login,
                "timestamp": self._parse_timestamp(author_block.get("date")),
                "source_url": data.get("html_url", f"https://github.com/{self.owner}/{self.repo}/commit/{data['sha']}"),
                "files": [f["filename"] for f in data.get("files", []) if f.get("filename")],
            }
        except Exception:
            return None

    # Issue collection

    async def fetch_issues(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch issues with pagination, excluding pull requests."""
        results: List[Dict[str, Any]] = []
        seen_numbers = set()

        async with httpx.AsyncClient(timeout=25.0, headers=self.headers) as client:
            try:
                page = 1
                while len(results) < limit:
                    per_page = min(limit - len(results), 100)
                    resp = await client.get(
                        "https://api.github.com/search/issues",
                        params={
                            "q": f"repo:{self.owner}/{self.repo} is:issue",
                            "sort": "created",
                            "order": "desc",
                            "per_page": per_page,
                            "page": page,
                        }
                    )
                    if resp.status_code != 200:
                        break
                    data = resp.json()
                    items = data.get("items", []) if isinstance(data, dict) else []
                    total_count = data.get("total_count", float("inf")) if isinstance(data, dict) else float("inf")
                    if not items:
                        break
                    for item in items:
                        if "pull_request" in item:
                            continue
                        num = item.get("number")
                        if num and num not in seen_numbers:
                            seen_numbers.add(num)
                            results.append({
                                "issue_number": num,
                                "title": item.get("title", ""),
                                "description": item.get("body") or "",
                                "state": item.get("state", "open"),
                                "source_url": item.get("html_url", ""),
                                "author": (item.get("user") or {}).get("login", "Unknown"),
                            })
                            if len(results) >= limit:
                                break
                    if len(results) >= total_count or len(results) >= limit or page >= 10:
                        break
                    page += 1
            except Exception as e:
                print(f"[WARN] Search API issues error for {self.owner}/{self.repo}: {e}")

            if len(results) < limit:
                try:
                    page = 1
                    max_pages = 15
                    while len(results) < limit and page <= max_pages:
                        per_page = min(100, max(limit, 30))
                        resp = await client.get(
                            f"{self.base_url}/issues",
                            params={"state": "all", "per_page": per_page, "page": page}
                        )
                        if resp.status_code != 200:
                            break
                        items = resp.json()
                        if not isinstance(items, list) or not items:
                            break
                        for item in items:
                            if "pull_request" in item:
                                continue
                            num = item.get("number")
                            if num and num not in seen_numbers:
                                seen_numbers.add(num)
                                results.append({
                                    "issue_number": num,
                                    "title": item.get("title", ""),
                                    "description": item.get("body") or "",
                                    "state": item.get("state", "open"),
                                    "source_url": item.get("html_url", ""),
                                    "author": (item.get("user") or {}).get("login", "Unknown"),
                                })
                                if len(results) >= limit:
                                    break
                        if len(items) < per_page:
                            break
                        page += 1
                except Exception as e:
                    print(f"[WARN] Standard issues endpoint pagination error: {e}")

        return results[:limit]

    # Pull request collection

    async def fetch_pull_requests(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch pull requests and extract referenced issue numbers."""
        results: List[Dict[str, Any]] = []
        seen_numbers = set()

        async with httpx.AsyncClient(timeout=25.0, headers=self.headers) as client:
            page = 1
            # NOTE: hardcoded cap at page 5 (max 500 items), ignoring higher limits
            while len(results) < limit and page <= 5:
                per_page = min(limit - len(results), 100)
                try:
                    resp = await client.get(
                        f"{self.base_url}/pulls",
                        params={"state": "all", "per_page": per_page, "page": page}
                    )
                    if resp.status_code != 200:
                        break
                    items = resp.json()
                    if not isinstance(items, list) or not items:
                        break
                    for item in items:
                        pr_num = item.get("number")
                        if pr_num and pr_num not in seen_numbers:
                            seen_numbers.add(pr_num)
                            title = item.get("title", "") or ""
                            body = item.get("body", "") or ""
                            results.append({
                                "pr_number": pr_num,
                                "title": title,
                                "description": body,
                                "state": item.get("state", "open"),
                                "source_url": item.get("html_url", ""),
                                "author": (item.get("user") or {}).get("login", "Unknown"),
                                "merge_commit_sha": item.get("merge_commit_sha"),
                                "head_sha": (item.get("head") or {}).get("sha"),
                                "linked_issues": extract_issue_numbers(f"{title} {body}"),
                            })
                            if len(results) >= limit:
                                break
                    if len(items) < per_page:
                        break
                    page += 1
                except Exception as e:
                    print(f"[WARN] fetch_pull_requests error: {e}")
                    break

        return results[:limit]

    # Pull request file changes

    async def fetch_pr_files(self, pr_number: int) -> List[str]:
        """Fetch changed file paths for a pull request."""
        async with httpx.AsyncClient(timeout=25.0, headers=self.headers) as client:
            try:
                # NOTE: GitHub caps unpaginated responses at 30 files
                resp = await client.get(f"{self.base_url}/pulls/{pr_number}/files")
                if resp.status_code == 200:
                    return [f["filename"] for f in resp.json() if "filename" in f]
            except Exception as e:
                print(f"[WARN] fetch_pr_files error: {e}")
            return []