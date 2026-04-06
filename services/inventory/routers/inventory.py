from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from shared.database import get_db
from shared.models import Inventory, User
from shared.schemas import InventoryCreate, InventoryUpdate, Inventory as InventorySchema, SyncData
from shared.auth import has_permission
from services.auth.routers.auth import get_current_user
from typing import List
import structlog

logger = structlog.get_logger()
router = APIRouter()

@router.post("/", response_model=InventorySchema)
async def create_inventory(inventory: InventoryCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not has_permission(current_user.role.name, "write"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check if exists
    result = await db.execute(select(Inventory).where(Inventory.store_id == inventory.store_id, Inventory.product_id == inventory.product_id))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Inventory already exists")
    
    db_inventory = Inventory(**inventory.dict())
    db.add(db_inventory)
    await db.commit()
    await db.refresh(db_inventory)
    logger.info("Inventory created", inventory_id=db_inventory.id)
    return db_inventory

@router.get("/{store_id}", response_model=List[InventorySchema])
async def get_inventory(store_id: int, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not has_permission(current_user.role.name, "read"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    result = await db.execute(select(Inventory).where(Inventory.store_id == store_id).offset(skip).limit(limit))
    inventories = result.scalars().all()
    return inventories

@router.put("/{inventory_id}", response_model=InventorySchema)
async def update_inventory(inventory_id: int, inventory_update: InventoryUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not has_permission(current_user.role.name, "write"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    result = await db.execute(select(Inventory).where(Inventory.id == inventory_id))
    db_inventory = result.scalars().first()
    if not db_inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    
    update_data = inventory_update.dict(exclude_unset=True)
    update_data["version"] = db_inventory.version + 1
    await db.execute(update(Inventory).where(Inventory.id == inventory_id).values(**update_data))
    await db.commit()
    await db.refresh(db_inventory)
    logger.info("Inventory updated", inventory_id=inventory_id)
    return db_inventory

@router.get("/alerts/low-stock/{store_id}")
async def get_low_stock_alerts(store_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not has_permission(current_user.role.name, "read"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    result = await db.execute(select(Inventory).where(Inventory.store_id == store_id, Inventory.quantity <= Inventory.min_stock_level))
    alerts = result.scalars().all()
    return [{"product_id": alert.product_id, "quantity": alert.quantity, "min_level": alert.min_stock_level} for alert in alerts]

@router.post("/sync")
async def sync_inventory(sync_data: SyncData, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not has_permission(current_user.role.name, "write"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    conflicts = []
    for inv in sync_data.inventories:
        result = await db.execute(select(Inventory).where(Inventory.store_id == inv.store_id, Inventory.product_id == inv.product_id))
        existing = result.scalars().first()
        if existing:
            if inv.version > existing.version:
                # Update
                update_data = inv.dict(exclude_unset=True)
                await db.execute(update(Inventory).where(Inventory.id == existing.id).values(**update_data))
            else:
                conflicts.append({"type": "inventory", "id": existing.id, "local_version": existing.version, "remote_version": inv.version})
        else:
            db.add(Inventory(**inv.dict()))
    
    await db.commit()
    logger.info("Inventory synced", conflicts=len(conflicts))
    return {"conflicts": conflicts}