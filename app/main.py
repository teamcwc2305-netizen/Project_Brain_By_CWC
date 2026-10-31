import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.db.database import engine, Base
from app.api.routes import repositories, history, search, impact, graph

# Ensure all database tables exist on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="Deterministic Delivery Memory and Institutional Amnesia Protection Engine (LLM-Free)",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(repositories.router)
app.include_router(history.router)
app.include_router(search.router)
app.include_router(impact.router)
app.include_router(graph.router)

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "engine": "Deterministic / NetworkX / SQLite / WebGL Neural Core",
        "version": "2.0.0"
    }

# Mount WebGL Frontend directory
web_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web")
if not os.path.exists(web_dir):
    os.makedirs(web_dir, exist_ok=True)

app.mount("/", StaticFiles(directory=web_dir, html=True), name="static_web")