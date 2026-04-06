from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from shared.database import get_db
from shared.models import ReplenishmentRequest, User
from shared.schemas import ReplenishmentRequestCreate, ReplenishmentRequest as ReplenishmentRequestSchema
from shared.auth import has_permission
from services.auth.routers.auth import get_current_user
from typing import List
import structlog

logger = structlog.get_logger()
router = APIRouter()

@router.post("/", response_model=ReplenishmentRequestSchema)
async def create_replenishment_request(request: ReplenishmentRequestCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not has_permission(current_user.role.name, "write"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_request = ReplenishmentRequest(**request.dict())
    db.add(db_request)
    await db.commit()
    await db.refresh(db_request)
    logger.info("Replenishment request created", request_id=db_request.id)
    return db_request

@router.put("/{request_id}/approve")
async def approve_request(request_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not has_permission(current_user.role.name, "approve"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    await db.execute(update(ReplenishmentRequest).where(ReplenishmentRequest.id == request_id).values(status="approved", approved_by=current_user.id))
    await db.commit()
    logger.info("Replenishment request approved", request_id=request_id)
    return {"message": "Approved"}

@router.get("/", response_model=List[ReplenishmentRequestSchema])
async def get_requests(store_id: int = None, status: str = None, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not has_permission(current_user.role.name, "read"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    query = select(ReplenishmentRequest)
    if store_id:
        query = query.where((ReplenishmentRequest.from_store_id == store_id) | (ReplenishmentRequest.to_store_id == store_id))
    if status:
        query = query.where(ReplenishmentRequest.status == status)
    
    result = await db.execute(query)
    requests = result.scalars().all()
    return requests