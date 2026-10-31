from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base


class Repository(Base):
    """Tracked GitHub repository root and high-level sync metrics."""
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    owner = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    url = Column(String(255), unique=True, nullable=False, index=True)
    default_branch = Column(String(50), default="main")
    import_status = Column(String(50), default="PENDING")
    last_imported_at = Column(DateTime, default=None)
    total_commits = Column(Integer, default=0)
    open_issues = Column(Integer, default=0)
    open_prs = Column(Integer, default=0)

    commits = relationship("Commit", back_populates="repository", cascade="all, delete-orphan")
    files = relationship("File", back_populates="repository", cascade="all, delete-orphan")
    issues = relationship("Issue", back_populates="repository", cascade="all, delete-orphan")
    pull_requests = relationship("PullRequest", back_populates="repository", cascade="all, delete-orphan")
    relationships = relationship("RelationshipRecord", back_populates="repository", cascade="all, delete-orphan")

    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.name}"


class Author(Base):
    """Contributor identity table."""
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=True)


class Commit(Base):
    """Git commit record scoped to a repository."""
    __tablename__ = "commits"
    __table_args__ = (
        UniqueConstraint("repository_id", "sha", name="uq_repo_commit_sha"),
    )

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False, index=True)
    sha = Column(String(40), nullable=False, index=True)
    message = Column(Text, nullable=False)
    author = Column(String(100), nullable=False, index=True)
    author_login = Column(String(100), nullable=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    source_url = Column(String(255), nullable=False)

    repository = relationship("Repository", back_populates="commits")
    commit_files = relationship("CommitFile", back_populates="commit", cascade="all, delete-orphan")


class File(Base):
    """Tracked source or resource file in the repository tree."""
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False, index=True)
    path = Column(String(500), nullable=False, index=True)
    file_type = Column(String(50), nullable=True)

    repository = relationship("Repository", back_populates="files")
    commit_files = relationship("CommitFile", back_populates="file", cascade="all, delete-orphan")


class CommitFile(Base):
    """Junction table mapping commits to files modified in that revision."""
    __tablename__ = "commit_files"

    id = Column(Integer, primary_key=True, index=True)
    commit_id = Column(Integer, ForeignKey("commits.id"), nullable=False, index=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False, index=True)
    change_status = Column(String(20), default="modified")

    commit = relationship("Commit", back_populates="commit_files")
    file = relationship("File", back_populates="commit_files")


class Issue(Base):
    """Tracked issue ticket from GitHub."""
    __tablename__ = "issues"
    __table_args__ = (
        UniqueConstraint("repository_id", "issue_number", name="uq_repo_issue_number"),
    )

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False, index=True)
    issue_number = Column(Integer, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    author = Column(String(100), nullable=True)
    state = Column(String(20), default="open")
    source_url = Column(String(255), nullable=False)

    repository = relationship("Repository", back_populates="issues")


class PullRequest(Base):
    """Tracked pull request record and associated merge metadata."""
    __tablename__ = "pull_requests"
    __table_args__ = (
        UniqueConstraint("repository_id", "pr_number", name="uq_repo_pr_number"),
    )

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False, index=True)
    pr_number = Column(Integer, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    author = Column(String(100), nullable=True)
    state = Column(String(20), default="open")
    source_url = Column(String(255), nullable=False)
    head_sha = Column(String(40), nullable=True)
    merge_commit_sha = Column(String(40), nullable=True)
    linked_issues_json = Column(Text, default="[]")

    repository = relationship("Repository", back_populates="pull_requests")


class RelationshipRecord(Base):
    """Graph edge capturing code dependencies, imports, and cross-file references."""
    __tablename__ = "relationships"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False, index=True)
    source_type = Column(String(50), nullable=False)
    source_id = Column(String(100), nullable=False)
    target_type = Column(String(50), nullable=False)
    target_id = Column(String(100), nullable=False)
    relationship_type = Column(String(50), nullable=False)
    provenance = Column(String(255), nullable=False)
    classification = Column(String(20), default="CONFIRMED")

    repository = relationship("Repository", back_populates="relationships")