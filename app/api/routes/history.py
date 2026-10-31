from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.history import CommitResponse, IssueResponse, PullRequestResponse, KnowledgeRiskItem
from app.services.history_service import HistoryService

router = APIRouter(prefix="/api/repositories/{repo_id}/history", tags=["History"])

@router.get("/commits", response_model=list[CommitResponse])
def get_commits(repo_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """Fetch recent commits up to the requested limit."""
    return HistoryService(db, repo_id).list_commits(limit)

@router.get("/issues", response_model=list[IssueResponse])
def get_issues(repo_id: int, db: Session = Depends(get_db)):
    """Fetch all tracked issues for this repository."""
    return HistoryService(db, repo_id).list_issues()

@router.get("/pull-requests", response_model=list[PullRequestResponse])
def get_pull_requests(repo_id: int, db: Session = Depends(get_db)):
    """Fetch all pull requests recorded for this repository."""
    return HistoryService(db, repo_id).list_pull_requests()

@router.get("/knowledge-risk", response_model=list[KnowledgeRiskItem])
def get_knowledge_risk(repo_id: int, db: Session = Depends(get_db)):
    """Calculate single-contributor dependencies and bus-factor risks."""
    return HistoryService(db, repo_id).get_knowledge_risks()