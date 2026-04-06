from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from shared.database import get_db
from shared.models import Transaction, TransactionItem, Inventory, User
from shared.schemas import TransactionCreate, Transaction as TransactionSchema, SyncData
from shared.auth import has_permission
from shared.events import EventStore, increment_vector_clock
from services.auth.routers.auth import get_current_user
from typing import List
import structlog

logger = structlog.get_logger()
router = APIRouter()

async def process_sale_event(db: AsyncSession, transaction_id: int, store_id: int):
    # Append SALE_COMPLETED event
    vector_clock = {"store": 1}  # Simplified
    await EventStore.append_event(
        store_id=store_id,
        event_type="SALE_COMPLETED",
        aggregate_id=transaction_id,
        aggregate_type="transaction",
        event_data={"transaction_id": transaction_id},
        vector_clock=increment_vector_clock(vector_clock, "store")
    )
    # Update inventory via event replay (simplified direct update for demo)
    result = await db.execute(select(TransactionItem).where(TransactionItem.transaction_id == transaction_id))
    items = result.scalars().all()
    for item in items:
        inv_result = await db.execute(select(Inventory).where(Inventory.store_id == store_id, Inventory.product_id == item.product_id))
        inv = inv_result.scalars().first()
        if inv:
            new_quantity = inv.quantity - item.quantity
            await db.execute(update(Inventory).where(Inventory.id == inv.id).values(quantity=new_quantity, version=inv.version + 1))
    await db.commit()

@router.post("/", response_model=TransactionSchema)
async def create_transaction(transaction: TransactionCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not has_permission(current_user.role.name, "write"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Idempotency check
    if transaction.external_id:
        result = await db.execute(select(Transaction).where(Transaction.external_id == transaction.external_id))
        if result.scalars().first():
            raise HTTPException(status_code=409, detail="Transaction already exists")
    
    total_amount = sum(item.quantity * item.price for item in transaction.items)
    db_transaction = Transaction(store_id=transaction.store_id, user_id=transaction.user_id, total_amount=total_amount, external_id=transaction.external_id)
    db.add(db_transaction)
    await db.commit()
    await db.refresh(db_transaction)
    
    for item in transaction.items:
        db_item = TransactionItem(transaction_id=db_transaction.id, product_id=item.product_id, quantity=item.quantity, price=item.price)
        db.add(db_item)
    await db.commit()
    
    # Process sale event in background
    background_tasks.add_task(process_sale_event, db, db_transaction.id, transaction.store_id)
    
    logger.info("Transaction created", transaction_id=db_transaction.id)
    return db_transaction

@router.get("/{store_id}", response_model=List[TransactionSchema])
async def get_transactions(store_id: int, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not has_permission(current_user.role.name, "read"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    result = await db.execute(select(Transaction).where(Transaction.store_id == store_id).offset(skip).limit(limit))
    transactions = result.scalars().all()
    return transactions

@router.put("/{transaction_id}/status")
async def update_transaction_status(transaction_id: int, status: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not has_permission(current_user.role.name, "write"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    await db.execute(update(Transaction).where(Transaction.id == transaction_id).values(status=status, version=Transaction.version + 1))
    await db.commit()
    logger.info("Transaction status updated", transaction_id=transaction_id, status=status)
    return {"message": "Status updated"}

@router.post("/sync")
async def sync_transactions(sync_data: SyncData, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not has_permission(current_user.role.name, "write"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    conflicts = []
    for tx in sync_data.transactions:
        result = await db.execute(select(Transaction).where(Transaction.external_id == tx.external_id))
        existing = result.scalars().first()
        if existing:
            # Use vector clock comparison
            from shared.events import compare_vector_clocks
            cmp = compare_vector_clocks(tx.vector_clock, existing.vector_clock)
            if cmp > 0:
                # Update
                update_data = tx.dict(exclude_unset=True)
                await db.execute(update(Transaction).where(Transaction.id == existing.id).values(**update_data))
            else:
                conflicts.append({"type": "transaction", "id": existing.id, "conflict": "vector_clock"})
        else:
            db_tx = Transaction(**tx.dict(exclude={"items"}))
            db.add(db_tx)
            await db.commit()
            await db.refresh(db_tx)
            for item in tx.items:
                db_item = TransactionItem(transaction_id=db_tx.id, **item.dict())
                db.add(db_item)
            await db.commit()
    
    await EventStore.replay_events(sync_data.transactions[0].store_id if sync_data.transactions else 1)
    logger.info("Transactions synced", conflicts=len(conflicts))
    return {"conflicts": conflicts}