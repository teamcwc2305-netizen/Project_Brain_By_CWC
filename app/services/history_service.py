from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models import Commit, File, Issue, PullRequest, CommitFile
from app.schemas.history import CommitResponse, IssueResponse, PullRequestResponse, KnowledgeRiskItem

class HistoryService:
    def __init__(self, db: Session, repo_id: int):
        self.db = db
        self.repo_id = repo_id

    def list_commits(self, limit: int = 50) -> List[CommitResponse]:
        commits = (
            self.db.query(Commit)
            .filter(Commit.repository_id == self.repo_id)
            .order_by(Commit.timestamp.desc())
            .limit(limit)
            .all()
        )
        results = []
        for c in commits:
            changed_files = [cf.file.path for cf in c.commit_files if cf.file]
            results.append(CommitResponse(
                sha=c.sha,
                message=c.message,
                author=c.author,
                timestamp=c.timestamp,
                source_url=c.source_url,
                changed_files=changed_files
            ))
        return results

    def list_issues(self) -> List[IssueResponse]:
        issues = self.db.query(Issue).filter(Issue.repository_id == self.repo_id).all()
        return [IssueResponse.model_validate(i) for i in issues]

    def list_pull_requests(self) -> List[PullRequestResponse]:
        prs = self.db.query(PullRequest).filter(PullRequest.repository_id == self.repo_id).all()
        return [PullRequestResponse.model_validate(p) for p in prs]

    def get_knowledge_risks(self) -> List[KnowledgeRiskItem]:
        """Calculates single-contributor bottlenecks across recorded files."""
        files = self.db.query(File).filter(File.repository_id == self.repo_id).all()
        risks = []
        for f in files:
            # Query authors who modified this file
            authors = (
                self.db.query(Commit.author)
                .join(CommitFile, Commit.id == CommitFile.commit_id)
                .filter(CommitFile.file_id == f.id)
                .distinct()
                .all()
            )
            total_commits = (
                self.db.query(func.count(CommitFile.id))
                .filter(CommitFile.file_id == f.id)
                .scalar() or 0
            )
            distinct_authors = [a[0] for a in authors if a[0]]
            count_authors = len(distinct_authors)

            if count_authors == 1:
                risks.append(KnowledgeRiskItem(
                    file_path=f.path,
                    commit_count=total_commits,
                    unique_authors_count=1,
                    sole_contributor=distinct_authors[0],
                    risk_level="HIGH (Single Contributor)"
                ))
            elif count_authors > 1:
                risks.append(KnowledgeRiskItem(
                    file_path=f.path,
                    commit_count=total_commits,
                    unique_authors_count=count_authors,
                    sole_contributor=None,
                    risk_level="LOW (Distributed)"
                ))
            elif count_authors == 0 and total_commits == 0:
                # File recorded without linked commit details
                risks.append(KnowledgeRiskItem(
                    file_path=f.path,
                    commit_count=0,
                    unique_authors_count=0,
                    sole_contributor=None,
                    risk_level="UNKNOWN (No History)"
                ))
        return risks