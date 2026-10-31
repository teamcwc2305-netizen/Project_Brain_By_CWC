from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./project_brain.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={
        # Allow multi-threaded access across FastAPI worker threads
        "check_same_thread": False,
        "timeout": 20,
    },
    pool_pre_ping=True,
)

with engine.connect() as conn:
    conn.exec_driver_sql("PRAGMA journal_mode=WAL;")
    conn.exec_driver_sql("PRAGMA synchronous=NORMAL;")
    conn.exec_driver_sql("PRAGMA foreign_keys=ON;")


def auto_heal_columns():
    """Add required columns to existing SQLite tables when running without formal migrations."""
    with engine.connect() as conn:
        try:
            # Backfill author column for issue ownership tracking
            issue_cols = [c[1] for c in conn.exec_driver_sql("PRAGMA table_info('issues');").fetchall()]
            if issue_cols and "author" not in issue_cols:
                conn.exec_driver_sql("ALTER TABLE issues ADD COLUMN author VARCHAR(100);")
                conn.commit()

            # Backfill author login handle on commits
            commit_cols = [c[1] for c in conn.exec_driver_sql("PRAGMA table_info('commits');").fetchall()]
            if commit_cols and "author_login" not in commit_cols:
                conn.exec_driver_sql("ALTER TABLE commits ADD COLUMN author_login VARCHAR(100);")
                conn.commit()

            pr_cols = [c[1] for c in conn.exec_driver_sql("PRAGMA table_info('pull_requests');").fetchall()]
            if pr_cols and "author" not in pr_cols:
                conn.exec_driver_sql("ALTER TABLE pull_requests ADD COLUMN author VARCHAR(100);")
                conn.commit()
        except Exception:
            pass


auto_heal_columns()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Provide a transactional database session per request and close it on completion."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()