import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.database import check_database, initialize_database
from app.routers import api, web

logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)
settings = get_settings()
BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Starting %s in %s environment", settings.app_name, settings.app_env)
    try:
        initialize_database()
        logger.info("Database connection and initialization succeeded")
    except Exception:
        logger.exception("Database initialization failed")
        raise
    yield
    logger.info("Shutting down %s", settings.app_name)


app = FastAPI(title="Atlas API", version=settings.app_version, lifespan=lifespan)
app.state.templates = Jinja2Templates(directory=BASE_DIR / "templates")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.include_router(web.router)
app.include_router(api.router)


@app.get("/health/live", tags=["health"])
def liveness():
    return {"status": "alive", "application": settings.app_name}


@app.get("/health/ready", tags=["health"])
def readiness():
    if not check_database():
        return JSONResponse(status_code=503, content={"status": "not ready", "application": settings.app_name, "database": "disconnected"})
    return {"status": "ready", "application": settings.app_name, "database": "connected"}


@app.get("/health", tags=["health"])
def health():
    return readiness()
