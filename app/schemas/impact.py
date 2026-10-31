from typing import List, Optional
from pydantic import BaseModel

class ImpactRequest(BaseModel):
    diff_text: Optional[str] = None
    changed_files: Optional[List[str]] = None

class AffectedComponent(BaseModel):
    component_name: str
    impact_category: str  # Direct, Recorded co-change, Inferred test
    impact_level: str     # HIGH, MEDIUM, LOW
    reason: str
    relationship_type: str
    classification: str   # CONFIRMED or INFERRED
    supporting_evidence: List[str] = []

class ImpactAnalysisResponse(BaseModel):
    directly_modified_files: List[str]
    affected_components: List[AffectedComponent]
    suggested_tests: List[str]
    summary: str