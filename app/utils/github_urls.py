# app/utils/github_urls.py
import re
from typing import Tuple, Optional

def parse_github_url(url: str) -> Optional[Tuple[str, str]]:
    if not url:
        return None

    clean_url = url.strip().rstrip("/")
    if clean_url.endswith(".git"):
        clean_url = clean_url[:-4]

    pattern = r"github\.com[/:](?P<owner>[^/]+)/(?P<repo>[^/]+)"
    match = re.search(pattern, clean_url, re.IGNORECASE)
    if match:
        owner = match.group("owner").strip()
        repo = match.group("repo").strip()
        return owner, repo

    return None

def build_github_commit_url(owner: str, repo: str, sha: str) -> str:
    return f"https://github.com/{owner}/{repo}/commit/{sha}"

def build_github_issue_url(owner: str, repo: str, issue_number: int) -> str:
    return f"https://github.com/{owner}/{repo}/issues/{issue_number}"