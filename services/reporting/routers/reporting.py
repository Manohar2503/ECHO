from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from shared.database import get_db
from shared.models import Transaction, TransactionItem, Inventory, User
from shared.auth import has_permission
from services.auth.routers.auth import get_current_user
import structlog

logger = structlog.get_logger()
router = APIRouter()

@router.get("/sales/{store_id}")
async def get_sales_analytics(store_id: int, start_date: str = None, end_date: str = None, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not has_permission(current_user.role.name, "read"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    query = select(func.sum(Transaction.total_amount), func.count(Transaction.id)).where(Transaction.store_id == store_id, Transaction.status == 'completed')
    if start_date and end_date:
        query = query.where(Transaction.created_at.between(start_date, end_date))
    
    result = await db.execute(query)
    total_sales, transaction_count = result.first()
    return {"total_sales": total_sales or 0, "transaction_count": transaction_count or 0}

@router.get("/performance/{store_id}")
async def get_store_performance(store_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not has_permission(current_user.role.name, "read"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Simple metrics
    sales_result = await db.execute(select(func.sum(Transaction.total_amount)).where(Transaction.store_id == store_id, Transaction.status == 'completed'))
    total_sales = sales_result.scalar() or 0
    
    inventory_result = await db.execute(select(func.sum(Inventory.quantity)).where(Inventory.store_id == store_id))
    total_inventory = inventory_result.scalar() or 0
    
    return {"total_sales": total_sales, "total_inventory_value": total_inventory}  # Assuming value = quantity for simplicity

@router.get("/shrinkage/{store_id}")
async def get_shrinkage(store_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not has_permission(current_user.role.name, "read"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Shrinkage: expected vs actual, but simplified
    sold_result = await db.execute(select(func.sum(TransactionItem.quantity)).join(Transaction).where(Transaction.store_id == store_id, Transaction.status == 'completed'))
    total_sold = sold_result.scalar() or 0
    
    inventory_result = await db.execute(select(func.sum(Inventory.quantity)).where(Inventory.store_id == store_id))
    total_inventory = inventory_result.scalar() or 0
    
    shrinkage = total_inventory - total_sold  # Simplified
    return {"shrinkage": shrinkage}