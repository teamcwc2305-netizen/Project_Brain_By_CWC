from typing import List, Optional
from pydantic import BaseModel

class SearchRequest(BaseModel):
    query: str

class SourceReference(BaseModel):
    type: str  # Commit, Issue, PullRequest, File
    identifier: str
    url: str
    summary: str

class SearchResponse(BaseModel):
    query: str
    intent_detected: str
    summary_answer: str
    sources: List[SourceReference] = []
    found: bool