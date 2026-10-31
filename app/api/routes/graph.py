from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.graph_service import GraphService

router = APIRouter(prefix="/api/repositories/{repo_id}/graph", tags=["Graph"])

@router.get("")
def get_full_graph(repo_id: int, db: Session = Depends(get_db)):
    """Return the complete dependency graph payload for a repository."""
    service = GraphService(db, repo_id)
    return service.get_graph_export()