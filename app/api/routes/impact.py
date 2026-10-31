from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.impact import ImpactRequest, ImpactAnalysisResponse
from app.services.impact_service import ImpactService

router = APIRouter(prefix="/api/repositories/{repo_id}", tags=["Impact"])

@router.post("/impact", response_model=ImpactAnalysisResponse)
def analyze_impact(repo_id: int, req: ImpactRequest, db: Session = Depends(get_db)):
    """Evaluate blast radius and affected dependencies from a diff or file list."""
    service = ImpactService(db, repo_id)
    return service.analyze_impact(diff_text=req.diff_text, explicit_files=req.changed_files)