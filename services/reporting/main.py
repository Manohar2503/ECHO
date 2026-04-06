from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.reporting.routers import reporting
import structlog

logger = structlog.get_logger()

app = FastAPI(title="Reporting Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reporting.router, prefix="/reporting", tags=["reporting"])

@app.on_event("startup")
async def startup_event():
    logger.info("Reporting service started")

@app.get("/health")
async def health():
    return {"status": "ok"}