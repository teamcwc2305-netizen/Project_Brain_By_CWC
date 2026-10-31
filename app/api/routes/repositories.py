import asyncio
import traceback
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from app.db.database import get_db, SessionLocal
from app.db.models import Repository, Commit, File, CommitFile, Issue, PullRequest, RelationshipRecord
from app.schemas.repository import RepositoryImportRequest, RepositoryResponse, RepositoryStatsResponse
from app.services.import_service import ImportService
from app.utils.github_urls import parse_github_url

router = APIRouter(prefix="/api/repositories", tags=["Repositories"])


def _run_import_in_background(url: str):
    """Background task worker; runs the async importer in its own thread event loop."""
    db = SessionLocal()
    try:
        service = ImportService(db)
        asyncio.run(service.import_repository(url))
        print(f"[Background Import Success] Finished importing {url}")
    except Exception as e:
        print(f"[Background Import Error] {url}: {e}")
        traceback.print_exc()
    finally:
        db.close()


@router.post("/import", response_model=RepositoryResponse)
def import_repo(req: RepositoryImportRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Queue a repository for background cloning and AST/commit ingestion."""
    parsed = parse_github_url(req.url)
    if not parsed:
        raise HTTPException(status_code=400, detail=f"Invalid public GitHub URL: {req.url}")
    owner, repo_name = parsed
    canonical_url = f"https://github.com/{owner}/{repo_name}"

    # Match existing repo across common URL variants to avoid duplicates
    repo = db.query(Repository).filter(
        (Repository.url == req.url) |
        (Repository.url == canonical_url) |
        (Repository.url == f"{canonical_url}.git") |
        ((Repository.owner == owner) & (Repository.name == repo_name))
    ).first()

    if not repo:
        repo = Repository(owner=owner, name=repo_name, url=canonical_url, import_status="QUEUED")
        db.add(repo)
        db.commit()
        db.refresh(repo)
    else:
        repo.import_status = "QUEUED"
        db.commit()
        db.refresh(repo)

    background_tasks.add_task(_run_import_in_background, req.url)
    return repo


@router.get("", response_model=list[RepositoryResponse])
def list_repositories(db: Session = Depends(get_db)):
    """List all repositories ordered by most recently imported or updated."""
    return db.query(Repository).order_by(
        Repository.last_imported_at.desc().nullslast(),
        Repository.id.desc()
    ).all()


@router.get("/{repo_id}", response_model=RepositoryResponse)
def get_repository(repo_id: int, db: Session = Depends(get_db)):
    """Fetch a single repository's metadata and ingestion status."""
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    return repo


@router.get("/{repo_id}/stats", response_model=RepositoryStatsResponse)
def get_repository_stats(repo_id: int, db: Session = Depends(get_db)):
    """Aggregate commit, file, issue, PR, and relationship totals for dashboard views."""
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    c_count = db.query(func.count(Commit.id)).filter(Commit.repository_id == repo_id).scalar() or 0
    f_count = db.query(func.count(File.id)).filter(File.repository_id == repo_id).scalar() or 0
    i_count = db.query(func.count(distinct(Issue.issue_number))).filter(Issue.repository_id == repo_id).scalar() or 0
    pr_count = db.query(func.count(distinct(PullRequest.pr_number))).filter(PullRequest.repository_id == repo_id).scalar() or 0
    r_count = db.query(func.count(RelationshipRecord.id)).filter(RelationshipRecord.repository_id == repo_id).scalar() or 0

    open_i = db.query(func.count(Issue.id)).filter(Issue.repository_id == repo_id, Issue.state == "open").scalar() or 0
    closed_i = db.query(func.count(Issue.id)).filter(Issue.repository_id == repo_id, Issue.state == "closed").scalar() or 0
    open_prs = db.query(func.count(PullRequest.id)).filter(PullRequest.repository_id == repo_id, PullRequest.state == "open").scalar() or 0

    # NOTE: check this - truthy checks override cached 0 counts with live query counts
    return RepositoryStatsResponse(
        repository_id=repo_id,
        commits_count=c_count,
        files_count=f_count,
        issues_count=i_count,
        pull_requests_count=pr_count,
        relationships_count=r_count,
        distinct_issues_count=i_count,
        open_issues_count=repo.open_issues if repo.open_issues else open_i,
        closed_issues_count=closed_i,
        total_commits=repo.total_commits if repo.total_commits else c_count,
        open_prs_count=repo.open_prs if repo.open_prs else open_prs
    )


@router.delete("/{repo_id}")
def delete_repository(repo_id: int, db: Session = Depends(get_db)):
    """Delete a repository and manually purge all dependent child records."""
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    repo_full_name = f"{repo.owner}/{repo.name}"

    # Clear junction rows by commit ID
    commit_ids = [c_id for (c_id,) in db.query(Commit.id).filter(Commit.repository_id == repo_id).all()]
    if commit_ids:
        db.query(CommitFile).filter(CommitFile.commit_id.in_(commit_ids)).delete(synchronize_session=False)

    # Clear remaining junction rows by file ID
    file_ids = [f_id for (f_id,) in db.query(File.id).filter(File.repository_id == repo_id).all()]
    if file_ids:
        db.query(CommitFile).filter(CommitFile.file_id.in_(file_ids)).delete(synchronize_session=False)

    # Clear dependency and call graph edges
    db.query(RelationshipRecord).filter(RelationshipRecord.repository_id == repo_id).delete(synchronize_session=False)

    # Clear tracker entities
    db.query(Issue).filter(Issue.repository_id == repo_id).delete(synchronize_session=False)
    db.query(PullRequest).filter(PullRequest.repository_id == repo_id).delete(synchronize_session=False)

    # Clear source tree and git history records
    db.query(Commit).filter(Commit.repository_id == repo_id).delete(synchronize_session=False)
    db.query(File).filter(File.repository_id == repo_id).delete(synchronize_session=False)

    # Delete repository root record
    db.delete(repo)
    db.commit()

    return {
        "status": "success",
        "message": f"Repository '{repo_full_name}' and all associated records removed successfully.",
        "id": repo_id
    }


class AIAnalysisRequest(BaseModel):
    provider: str = "gemini"
    api_key: str
    model: Optional[str] = None


@router.get("/{repo_id}/description")
async def get_repository_description(repo_id: int, db: Session = Depends(get_db)):
    """Collect repository tree and details to construct an architectural overview."""
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    db_files = [f.path for f in db.query(File.path).filter(File.repository_id == repo_id).all()]

    from app.services.repo_analyzer_service import RepoAnalyzerService
    analyzer = RepoAnalyzerService(repo.owner, repo.name)
    details = await analyzer.fetch_full_details(db_files=db_files)
    details["repository_id"] = repo_id
    return details


@router.post("/{repo_id}/ai-analyze")
async def run_repository_ai_analysis(repo_id: int, req: AIAnalysisRequest, db: Session = Depends(get_db)):
    """Trigger external LLM analysis over repository metadata, README, and recent commits."""
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    db_files = [f.path for f in db.query(File.path).filter(File.repository_id == repo_id).all()]
    recent_commits = [
        {"sha": c.sha, "message": c.message}
        for c in db.query(Commit.sha, Commit.message).filter(Commit.repository_id == repo_id).order_by(Commit.timestamp.desc()).limit(10).all()
    ]

    from app.services.repo_analyzer_service import RepoAnalyzerService
    analyzer = RepoAnalyzerService(repo.owner, repo.name)
    details = await analyzer.fetch_full_details(db_files=db_files)

    result = await analyzer.call_ai_analyzer(
        provider=req.provider,
        api_key=req.api_key,
        metadata={
            "description": details.get("description"),
            "language": details.get("language"),
            "topics": details.get("topics"),
        },
        paths=details.get("file_paths", []),
        readme=details.get("readme", ""),
        recent_commits=recent_commits
    )
    return result