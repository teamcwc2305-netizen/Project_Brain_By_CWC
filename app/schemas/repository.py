from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class RepositoryImportRequest(BaseModel):
    url: str


class RepositoryResponse(BaseModel):
    id: int
    owner: str
    name: str
    url: str
    default_branch: str = "main"
    import_status: str
    last_imported_at: Optional[datetime] = None
    total_commits: Optional[int] = 0
    open_issues: Optional[int] = 0
    open_prs: Optional[int] = 0

    class Config:
        from_attributes = True


class RepositoryStatsResponse(BaseModel):
    repository_id: int
    commits_count: int
    files_count: int
    issues_count: int
    pull_requests_count: int
    relationships_count: int
    distinct_issues_count: Optional[int] = None
    open_issues_count: Optional[int] = None
    closed_issues_count: Optional[int] = None
    total_commits: Optional[int] = 0
    open_prs_count: Optional[int] = 0
