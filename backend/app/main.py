import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.api.router import api_router
from app.core.config import get_settings
from app.db.session import Base, engine
from app import models  # Ensure SQLAlchemy models are registered.

logging.basicConfig(level=logging.INFO)
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        with engine.begin() as connection:
            connection.execute(text("SELECT 1"))
            Base.metadata.create_all(bind=connection)
        logging.getLogger(__name__).info("Connected to configured Supabase PostgreSQL database")
    except SQLAlchemyError as exc:
        logging.getLogger(__name__).exception("Supabase PostgreSQL connection or schema initialization failed")
        raise RuntimeError("Unable to connect to the configured Supabase PostgreSQL database.") from exc
    yield


app = FastAPI(title="AIVOA Deviation Intake API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(api_router)


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(_: Request, exc: SQLAlchemyError):
    logging.getLogger(__name__).exception("Database request failed", exc_info=exc)
    return JSONResponse(
        status_code=503,
        content={"detail": "Database unavailable. Verify the backend Supabase DATABASE_URL."},
    )


@app.get("/api/health")
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        logging.getLogger(__name__).exception("Database health check failed")
        raise HTTPException(503, "Database unavailable. Verify the backend Supabase DATABASE_URL.") from exc
    return {"status": "healthy", "service": "aivoa-deviation-intake", "database": "connected"}
