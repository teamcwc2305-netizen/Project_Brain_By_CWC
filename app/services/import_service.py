import re
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models import Repository, Commit, File, CommitFile, Issue, PullRequest, RelationshipRecord
from app.collectors.github_collector import GitHubCollector
from app.utils.github_urls import parse_github_url
from app.utils.text_normalization import extract_issue_numbers, extract_pr_numbers

class ImportService:
    def __init__(self, db: Session):
        self.db = db
        self.seen_rels = set()

    async def import_repository(
        self,
        url: str,
        commits_limit: int = 50,
        issues_limit: int = 50,
        prs_limit: int = 50
    ) -> Repository:
        parsed = parse_github_url(url)
        if not parsed:
            raise ValueError(f"Invalid public GitHub URL: {url}")
        owner, repo_name = parsed
        canonical_url = f"https://github.com/{owner}/{repo_name}"

        # Match existing repository by canonical URL or owner/name to avoid duplicates
        repo = self.db.query(Repository).filter(
            (Repository.url == url) | 
            (Repository.url == canonical_url) |
            (Repository.url == f"{canonical_url}.git") |
            ((Repository.owner == owner) & (Repository.name == repo_name))
        ).first()

        if not repo:
            repo = Repository(owner=owner, name=repo_name, url=url, import_status="IMPORTING")
            self.db.add(repo)
            self.db.commit()
            self.db.refresh(repo)
        else:
            repo.import_status = "IMPORTING"
            self.db.commit()

        # Refresh repository relationships on import to avoid stale or misclassified ghost links
        self.db.query(RelationshipRecord).filter(RelationshipRecord.repository_id == repo.id).delete()
        self.db.flush()
        self.seen_rels = set()

        collector = GitHubCollector(owner, repo_name)

        try:
            # 0. Fetch high-level repository overview directly matching GitHub's header tabs
            try:
                overview = await collector.fetch_repo_overview()
                if overview.get("total_commits"):
                    repo.total_commits = overview["total_commits"]
                if overview.get("open_issues") is not None:
                    repo.open_issues = overview["open_issues"]
                if overview.get("open_prs") is not None:
                    repo.open_prs = overview["open_prs"]
                self.db.flush()
            except Exception as e:
                print(f"[WARN] fetch_repo_overview error: {e}")

            # 1. Fetch & Store Commits and Files (up to 50 commits)
            raw_commits = await collector.fetch_commits(limit=commits_limit)
            seen_shas = set()

            for c_data in raw_commits:
                sha = c_data["sha"]
                if sha in seen_shas:
                    continue
                seen_shas.add(sha)

                author_val = c_data.get("author") or "Unknown"
                author_login_val = c_data.get("author_login") or author_val

                commit = self.db.query(Commit).filter(
                    Commit.repository_id == repo.id,
                    Commit.sha == sha
                ).first()

                if not commit:
                    commit = Commit(
                        repository_id=repo.id,
                        sha=sha,
                        message=c_data.get("message", "No commit message"),
                        author=author_val,
                        author_login=author_login_val,
                        timestamp=c_data.get("timestamp"),
                        source_url=c_data.get("source_url", f"https://github.com/{owner}/{repo_name}/commit/{sha}")
                    )
                    self.db.add(commit)
                    self.db.flush()
                else:
                    commit.message = c_data.get("message", commit.message)
                    commit.author = author_val
                    commit.author_login = author_login_val
                    commit.timestamp = c_data.get("timestamp", commit.timestamp)
                    commit.source_url = c_data.get("source_url", commit.source_url)
                    self.db.flush()

                self._record_rel(
                    repo.id, "Author", commit.author, "Commit", commit.sha,
                    "AUTHORED", "Git commit metadata", "CONFIRMED"
                )

                for f_path in c_data.get("files", []):
                    clean_path = f_path.strip().replace("\\", "/")
                    file_rec = self.db.query(File).filter(
                        File.repository_id == repo.id,
                        File.path == clean_path
                    ).first()
                    if not file_rec:
                        file_rec = File(repository_id=repo.id, path=clean_path)
                        self.db.add(file_rec)
                        self.db.flush()

                    link = self.db.query(CommitFile).filter(
                        CommitFile.commit_id == commit.id,
                        CommitFile.file_id == file_rec.id
                    ).first()
                    if not link:
                        self.db.add(CommitFile(commit_id=commit.id, file_id=file_rec.id))
                        self.db.flush()

                    self._record_rel(
                        repo.id, "Commit", commit.sha, "File", file_rec.path,
                        "MODIFIES", "Git commit diff", "CONFIRMED"
                    )

            # Fetch & Store Issues (Paginated across pages, PRs excluded, open/closed preserved)
            raw_issues = await collector.fetch_issues(limit=issues_limit)
            for i_data in raw_issues:
                issue = self.db.query(Issue).filter(
                    Issue.repository_id == repo.id,
                    Issue.issue_number == i_data["issue_number"]
                ).first()
                if not issue:
                    issue = Issue(
                        repository_id=repo.id,
                        issue_number=i_data["issue_number"],
                        title=i_data["title"],
                        description=i_data["description"],
                        author=i_data.get("author") or "Unknown",
                        state=i_data.get("state", "open"),
                        source_url=i_data["source_url"]
                    )
                    self.db.add(issue)
                    self.db.flush()
                else:
                    # Idempotent update: refresh existing issue fields
                    issue.title = i_data["title"]
                    issue.description = i_data["description"]
                    issue.state = i_data.get("state", issue.state)
                    issue.source_url = i_data["source_url"]
                    if i_data.get("author") and i_data["author"] != "Unknown":
                        issue.author = i_data["author"]
                    self.db.flush()

                if i_data.get("author") and i_data["author"] != "Unknown":
                    self._record_rel(
                        repo.id, "Author", i_data["author"], "Issue", str(issue.issue_number),
                        "OPENED_ISSUE", "GitHub issue metadata", "CONFIRMED"
                    )

            # Fetch & Store Pull Requests (Paginated, distinct from Issues)
            raw_prs = await collector.fetch_pull_requests(limit=prs_limit)
            for pr_data in raw_prs:
                pr = self.db.query(PullRequest).filter(
                    PullRequest.repository_id == repo.id,
                    PullRequest.pr_number == pr_data["pr_number"]
                ).first()
                if not pr:
                    pr = PullRequest(
                        repository_id=repo.id,
                        pr_number=pr_data["pr_number"],
                        title=pr_data["title"],
                        description=pr_data["description"],
                        author=pr_data.get("author") or "Unknown",
                        state=pr_data.get("state", "open"),
                        source_url=pr_data["source_url"],
                        head_sha=pr_data.get("head_sha"),
                        merge_commit_sha=pr_data.get("merge_commit_sha")
                    )
                    self.db.add(pr)
                    self.db.flush()
                else:
                    pr.title = pr_data["title"]
                    pr.description = pr_data["description"]
                    pr.state = pr_data.get("state", pr.state)
                    pr.source_url = pr_data["source_url"]
                    pr.head_sha = pr_data.get("head_sha") or pr.head_sha
                    pr.merge_commit_sha = pr_data.get("merge_commit_sha") or pr.merge_commit_sha
                    if pr_data.get("author") and pr_data["author"] != "Unknown":
                        pr.author = pr_data["author"]
                    self.db.flush()

                if pr_data.get("author") and pr_data["author"] != "Unknown":
                    self._record_rel(
                        repo.id, "Author", pr_data["author"], "PullRequest", str(pr.pr_number),
                        "OPENED_PR", "GitHub PR metadata", "CONFIRMED"
                    )

                for candidate_sha in [pr_data.get("merge_commit_sha"), pr_data.get("head_sha")]:
                    if candidate_sha:
                        c_match = self.db.query(Commit).filter(
                            Commit.repository_id == repo.id,
                            Commit.sha == candidate_sha
                        ).first()
                        if c_match:
                            self._record_rel(
                                repo.id, "PullRequest", str(pr.pr_number), "Commit", c_match.sha,
                                "MERGED_IN", "PR merge/head SHA", "CONFIRMED"
                            )

                for iss_num in pr_data.get("linked_issues", []):
                    self._record_rel(
                        repo.id, "PullRequest", str(pr.pr_number), "Issue", str(iss_num),
                        "CLOSES_OR_REFERENCES", "PR description reference", "CONFIRMED"
                    )

            # Pattern Linkages (Commit messages to PRs and Issues)
            all_commits = self.db.query(Commit).filter(Commit.repository_id == repo.id).all()
            for c in all_commits:
                pr_refs = extract_pr_numbers(c.message)
                for pr_num in pr_refs:
                    self._record_rel(
                        repo.id, "PullRequest", str(pr_num), "Commit", c.sha,
                        "MERGED_IN", "Commit message merge pattern", "CONFIRMED"
                    )

                # Pure issue extraction excluding PR references
                iss_refs = extract_issue_numbers(c.message, exclude_pr_numbers=pr_refs)
                for iss_num in iss_refs:
                    self._record_rel(
                        repo.id, "Commit", c.sha, "Issue", str(iss_num),
                        "CLOSES_OR_REFERENCES", "Commit issue reference", "CONFIRMED"
                    )

            # Mark COMPLETED
            repo.import_status = "COMPLETED"
            repo.last_imported_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(repo)

        except Exception as e:
            self.db.rollback()
            repo.import_status = "FAILED"
            self.db.commit()
            raise e

        return repo

    def _record_rel(self, repo_id: int, s_type: str, s_id: str, t_type: str, t_id: str, r_type: str, prov: str, classification: str):
        key = (s_type, str(s_id), t_type, str(t_id), r_type)
        if key in self.seen_rels:
            return

        self.db.add(RelationshipRecord(
            repository_id=repo_id,
            source_type=s_type,
            source_id=str(s_id),
            target_type=t_type,
            target_id=str(t_id),
            relationship_type=r_type,
            provenance=prov,
            classification=classification
        ))
        self.seen_rels.add(key)
