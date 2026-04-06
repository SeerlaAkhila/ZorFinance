from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.config import settings
from app.db import Base, SessionLocal, engine
from app.routers.records import router as records_router
from app.routers.summaries import router as summaries_router
from app.routers.users import router as users_router
from app.seed import seed_users


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_users(session)
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend service for finance record management, analytics, and role-based access.",
    docs_url="/docs" if settings.enable_docs else None,
    redoc_url="/redoc" if settings.enable_docs else None,
    openapi_url="/openapi.json" if settings.enable_docs else None,
    lifespan=lifespan,
)

app.include_router(users_router)
app.include_router(records_router)
app.include_router(summaries_router)


@app.get("/", tags=["health"])
def health():
    return FileResponse("app/static/index.html")
