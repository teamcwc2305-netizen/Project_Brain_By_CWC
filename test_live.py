import asyncio
from app.db.database import SessionLocal
from app.services.import_service import ImportService

async def main():
    db = SessionLocal()
    url = "https://github.com/pallets/flask"
    print(f"🚀 Testing live GitHub import for: {url}")
    service = ImportService(db)
    repo = await service.import_repository(url)
    print(f"✅ LIVE IMPORT SUCCESS! Repo ID: {repo.id}, Status: {repo.import_status}")
    db.close()

if __name__ == "__main__":
    asyncio.run(main())