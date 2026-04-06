from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.ai.routers import ai
import structlog

logger = structlog.get_logger()

app = FastAPI(title="AI Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai.router, prefix="/ai", tags=["ai"])

@app.on_event("startup")
async def startup_event():
    logger.info("AI service started")

@app.get("/health")
async def health():
    return {"status": "ok"}