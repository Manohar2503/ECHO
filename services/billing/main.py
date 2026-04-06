from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.billing.routers import billing
import structlog

logger = structlog.get_logger()

app = FastAPI(title="Billing Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(billing.router, prefix="/billing", tags=["billing"])

@app.on_event("startup")
async def startup_event():
    logger.info("Billing service started")

@app.get("/health")
async def health():
    return {"status": "ok"}