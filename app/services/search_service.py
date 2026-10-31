import re
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.db.models import Commit, File, Issue, PullRequest, CommitFile
from app.schemas.search import SearchResponse, SourceReference
from app.utils.text_normalization import tokenize
from app.services.answer_templates import (
    NOT_FOUND_MESSAGE,
    format_file_history_answer,
    format_author_files_answer,
    format_issue_answer,
    format_keyword_search_answer
)

class SearchService:
    def __init__(self, db: Session, repo_id: int):
        self.db = db
        self.repo_id = repo_id

    def execute_query(self, query: str) -> SearchResponse:
        norm_q = query.strip()
        if not norm_q:
            return SearchResponse(query=query, intent_detected="EMPTY", summary_answer=NOT_FOUND_MESSAGE, found=False)

        # Direct Author Detection
        all_authors = (
            self.db.query(Commit.author)
            .filter(Commit.repository_id == self.repo_id)
            .distinct()
            .all()
        )
        for (author_name,) in all_authors:
            if not author_name:
                continue
            if re.search(r'\b' + re.escape(author_name.lower()) + r'\b', norm_q.lower()) or author_name.lower() in norm_q.lower():
                author_commits = (
                    self.db.query(Commit)
                    .filter(Commit.repository_id == self.repo_id, Commit.author == author_name)
                    .order_by(Commit.timestamp.desc())
                    .all()
                )
                if author_commits:
                    files = (
                        self.db.query(File.path)
                        .join(CommitFile, File.id == CommitFile.file_id)
                        .join(Commit, CommitFile.commit_id == Commit.id)
                        .filter(Commit.author == author_name)
                        .distinct()
                        .all()
                    )
                    file_paths = [f[0] for f in files]
                    commit_shas = [c.sha[:7] for c in author_commits]

                    summary = (
                        f"Developer '{author_name}' has authored {len(author_commits)} recorded commit(s) "
                        f"({', '.join(commit_shas)}), modifying {len(file_paths)} file(s)."
                    )

                    sources = [
                        SourceReference(
                            type="Commit",
                            identifier=c.sha[:7],
                            url=c.source_url,
                            summary=f"{c.message.strip()[:90]} ({c.timestamp.strftime('%Y-%m-%d')})"
                        )
                        for c in author_commits
                    ]

                    return SearchResponse(
                        query=query,
                        intent_detected="AUTHOR_LOOKUP",
                        summary_answer=summary,
                        sources=sources,
                        found=True
                    )

        # Pull Request
        
        pr_match = re.search(r"(?:pr|pull\s*request)\s*#?\s*(\d+)", norm_q, re.IGNORECASE)
        if pr_match:
            pr_num = int(pr_match.group(1))
            pr = self.db.query(PullRequest).filter(
                PullRequest.repository_id == self.repo_id,
                PullRequest.pr_number == pr_num
            ).first()
            if pr:
                summary = f"Pull Request #{pr.pr_number} ('{pr.title}') is [{pr.state.upper()}]."
                sources = [SourceReference(type="PullRequest", identifier=f"PR #{pr.pr_number}", url=pr.source_url, summary=pr.title)]
                return SearchResponse(
                    query=query,
                    intent_detected="PR_LOOKUP",
                    summary_answer=summary,
                    sources=sources,
                    found=True
                )

        # Commit SHA
        
        sha_match = re.search(r"\b([0-9a-fA-F]{7,40})\b", norm_q)
        if sha_match:
            candidate_sha = sha_match.group(1).lower()
            commit = self.db.query(Commit).filter(
                Commit.repository_id == self.repo_id,
                Commit.sha.ilike(f"{candidate_sha}%")
            ).first()
            if commit:
                changed_files = [cf.file.path for cf in commit.commit_files if cf.file]
                files_str = ", ".join(changed_files[:4]) + ("..." if len(changed_files) > 4 else "")
                summary = (
                    f"Commit {commit.sha[:7]} by {commit.author} on {commit.timestamp.strftime('%Y-%m-%d')}: "
                    f"\"{commit.message.strip()}\". Modified files: {files_str or 'None recorded'}."
                )
                sources = [SourceReference(type="Commit", identifier=commit.sha[:7], url=commit.source_url, summary=commit.message)]
                return SearchResponse(
                    query=query,
                    intent_detected="COMMIT_LOOKUP",
                    summary_answer=summary,
                    sources=sources,
                    found=True
                )

        # Issue Lookup
        
        issue_match = re.search(r"(?:issue|ticket|\#)\s*(\d+)", norm_q, re.IGNORECASE)
        if issue_match:
            issue_num = int(issue_match.group(1))
            issue = self.db.query(Issue).filter(
                Issue.repository_id == self.repo_id,
                Issue.issue_number == issue_num
            ).first()
            if issue:
                commits = self.db.query(Commit).filter(
                    Commit.repository_id == self.repo_id,
                    Commit.message.ilike(f"%#{issue_num}%")
                ).all()
                commit_shas = [c.sha for c in commits]
                sources = [SourceReference(type="Issue", identifier=f"#{issue.issue_number}", url=issue.source_url, summary=issue.title)]
                for c in commits:
                    sources.append(SourceReference(type="Commit", identifier=c.sha[:7], url=c.source_url, summary=c.message))

                return SearchResponse(
                    query=query,
                    intent_detected="ISSUE_LOOKUP",
                    summary_answer=format_issue_answer(issue.issue_number, issue.title, issue.state, commit_shas),
                    sources=sources,
                    found=True
                )

        # File History
        
        file_match = re.search(r"([\w\/\.-]+\.[a-zA-Z0-9]+)", norm_q)
        if file_match:
            target_path = file_match.group(1).replace("\\", "/")
            target_name = target_path.split("/")[-1]
            file_rec = self.db.query(File).filter(
                File.repository_id == self.repo_id,
                (File.path.ilike(f"%{target_path}%")) | (File.path.ilike(f"%{target_name}%"))
            ).first()

            if file_rec:
                commit_links = (
                    self.db.query(Commit)
                    .join(CommitFile, Commit.id == CommitFile.commit_id)
                    .filter(CommitFile.file_id == file_rec.id)
                    .order_by(Commit.timestamp.desc())
                    .all()
                )
                if commit_links:
                    latest = commit_links[0]
                    sources = [
                        SourceReference(type="Commit", identifier=c.sha[:7], url=c.source_url, summary=c.message)
                        for c in commit_links[:5]
                    ]
                    return SearchResponse(
                        query=query,
                        intent_detected="FILE_HISTORY",
                        summary_answer=format_file_history_answer(file_rec.path, len(commit_links), latest.sha, latest.message, latest.author),
                        sources=sources,
                        found=True
                    )

        # Fallback Token Search

        raw_tokens = tokenize(norm_q)
        ignored_tokens = {"pr", "prs", "commit", "commits", "issue", "issues", "file", "files", "the"}
        clean_tokens = [t for t in raw_tokens if t not in ignored_tokens and len(t) > 2]

        if not clean_tokens:
            return SearchResponse(query=query, intent_detected="UNKNOWN", summary_answer=NOT_FOUND_MESSAGE, found=False)

        search_filter = or_(*[Commit.message.ilike(f"%{t}%") for t in clean_tokens])
        matching_commits = self.db.query(Commit).filter(Commit.repository_id == self.repo_id, search_filter).limit(5).all()

        issue_filter = or_(*[Issue.title.ilike(f"%{t}%") for t in clean_tokens])
        matching_issues = self.db.query(Issue).filter(Issue.repository_id == self.repo_id, issue_filter).limit(3).all()

        sources = []
        for c in matching_commits:
            sources.append(SourceReference(type="Commit", identifier=c.sha[:7], url=c.source_url, summary=c.message))
        for iss in matching_issues:
            sources.append(SourceReference(type="Issue", identifier=f"#{iss.issue_number}", url=iss.source_url, summary=iss.title))

        if sources:
            return SearchResponse(
                query=query,
                intent_detected="KEYWORD_SEARCH",
                summary_answer=format_keyword_search_answer(query, len(sources)),
                sources=sources,
                found=True
            )

        return SearchResponse(
            query=query,
            intent_detected="NOT_FOUND",
            summary_answer=NOT_FOUND_MESSAGE,
            sources=[],
            found=False
        )