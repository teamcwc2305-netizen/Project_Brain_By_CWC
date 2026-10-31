from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.search import SearchRequest, SearchResponse
from app.services.search_service import SearchService

router = APIRouter(prefix="/api/repositories/{repo_id}", tags=["Search"])

@router.post("/search", response_model=SearchResponse)
def execute_search(repo_id: int, req: SearchRequest, db: Session = Depends(get_db)):
    """Search indexed symbols, file paths, and commit messages for a repository."""
    service = SearchService(db, repo_id)
    return service.execute_query(req.query)