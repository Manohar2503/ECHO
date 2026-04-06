from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.replenishment.routers import replenishment
import structlog

logger = structlog.get_logger()

app = FastAPI(title="Replenishment Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(replenishment.router, prefix="/replenishment", tags=["replenishment"])

@app.on_event("startup")
async def startup_event():
    logger.info("Replenishment service started")

@app.get("/health")
async def health():
    return {"status": "ok"}