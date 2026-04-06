from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.inventory.routers import inventory
import structlog

logger = structlog.get_logger()

app = FastAPI(title="Inventory Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(inventory.router, prefix="/inventory", tags=["inventory"])

@app.on_event("startup")
async def startup_event():
    logger.info("Inventory service started")

@app.get("/health")
async def health():
    return {"status": "ok"}