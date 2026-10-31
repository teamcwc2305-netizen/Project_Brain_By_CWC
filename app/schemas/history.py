from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class CommitResponse(BaseModel):
    """Commit payload returned by repository history endpoints."""
    sha: str
    message: str
    author: str
    timestamp: datetime
    source_url: str
    changed_files: List[str] = []

    class Config:
        from_attributes = True

class IssueResponse(BaseModel):
    """Issue summary payload for history listings."""
    issue_number: int
    title: str
    description: Optional[str]
    state: str
    source_url: str

    class Config:
        from_attributes = True

class PullRequestResponse(BaseModel):
    """Pull request summary payload for history listings."""
    pr_number: int
    title: str
    description: Optional[str]
    state: str
    source_url: str

    class Config:
        from_attributes = True

class KnowledgeRiskItem(BaseModel):
    """Bus-factor assessment identifying files dependent on a single contributor."""
    file_path: str
    commit_count: int
    unique_authors_count: int
    sole_contributor: Optional[str]
    risk_level: str