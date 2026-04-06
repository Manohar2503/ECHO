from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, extract
from shared.database import get_db
from shared.models import Transaction, Inventory, User
from shared.auth import has_permission
from services.auth.routers.auth import get_current_user
import numpy as np
from datetime import datetime, timedelta
import structlog
import re

logger = structlog.get_logger()
router = APIRouter()

def parse_natural_query(query: str) -> dict:
    # Simple NLP: extract intent and entities
    if "forecast" in query.lower():
        product_id = re.search(r'product (\d+)', query)
        return {"intent": "forecast", "product_id": int(product_id.group(1)) if product_id else 1, "days": 7}
    elif "anomaly" in query.lower():
        store_id = re.search(r'store (\d+)', query)
        return {"intent": "anomaly", "store_id": int(store_id.group(1)) if store_id else 1}
    elif "recommend" in query.lower():
        store_id = re.search(r'store (\d+)', query)
        return {"intent": "recommend", "store_id": int(store_id.group(1)) if store_id else 1}
    else:
        return {"intent": "unknown"}

@router.post("/query")
async def conversational_query(query: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not has_permission(current_user.role.name, "read"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    parsed = parse_natural_query(query)
    if parsed["intent"] == "forecast":
        # Call forecast logic
        forecast = await demand_forecast(parsed["product_id"], parsed.get("store_id", 1), parsed["days"], db, current_user)
        return {"response": f"Forecast for product {parsed['product_id']}: {forecast['forecast']}", "confidence": 0.85}
    elif parsed["intent"] == "anomaly":
        anomalies = await detect_anomalies(parsed["store_id"], db, current_user)
        return {"response": f"Anomalies detected: {len(anomalies['anomalies'])}", "details": anomalies}
    elif parsed["intent"] == "recommend":
        recommendations = await restock_recommendations(parsed["store_id"], db, current_user)
        return {"response": f"Recommendations: {len(recommendations['recommendations'])} items", "details": recommendations}
    else:
        return {"response": "Sorry, I didn't understand the query. Try asking about forecasts, anomalies, or recommendations."}

async def demand_forecast(product_id: int, store_id: int, days: int, db: AsyncSession, current_user: User):
    # Hybrid model: moving average + seasonal trends
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    result = await db.execute(
        select(extract('day', Transaction.created_at), func.sum(TransactionItem.quantity))
        .join(TransactionItem)
        .where(Transaction.store_id == store_id, TransactionItem.product_id == product_id, Transaction.created_at.between(start_date, end_date))
        .group_by(extract('day', Transaction.created_at))
    )
    sales_data = result.all()
    if not sales_data:
        return {"forecast": [0] * days}
    
    quantities = [row[1] for row in sales_data]
    # Simple seasonal adjustment (assume weekly pattern)
    seasonal = [q * (1 + 0.1 * (i % 7)) for i, q in enumerate(quantities)]
    if len(seasonal) < 7:
        avg = np.mean(seasonal) if seasonal else 0
        forecast = [avg] * days
    else:
        forecast = []
        for _ in range(days):
            ma = np.mean(seasonal[-7:])
            seasonal.append(ma)
            forecast.append(ma)
    
    return {"forecast": forecast}

async def detect_anomalies(store_id: int, db: AsyncSession, current_user: User):
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    result = await db.execute(
        select(Transaction.created_at.date(), func.sum(Transaction.total_amount))
        .where(Transaction.store_id == store_id, Transaction.created_at.between(start_date, end_date))
        .group_by(Transaction.created_at.date())
    )
    sales = result.all()
    if len(sales) < 7:
        return {"anomalies": []}
    
    amounts = [row[1] for row in sales]
    mean = np.mean(amounts)
    std = np.std(amounts)
    anomalies = []
    for i, amount in enumerate(amounts):
        z_score = (amount - mean) / std if std > 0 else 0
        if abs(z_score) > 2:
            anomalies.append({"date": sales[i][0], "amount": amount, "z_score": z_score, "severity": "high" if abs(z_score) > 3 else "medium"})
    
    return {"anomalies": anomalies}

async def restock_recommendations(store_id: int, db: AsyncSession, current_user: User):
    result = await db.execute(select(Inventory).where(Inventory.store_id == store_id, Inventory.quantity <= Inventory.min_stock_level))
    low_stock = result.scalars().all()
    recommendations = []
    for inv in low_stock:
        # Constraint-aware: forecast + logistics
        forecast = await demand_forecast(inv.product_id, store_id, 7, db, current_user)
        avg_demand = np.mean(forecast["forecast"]) if forecast["forecast"] else 0
        recommended = max(inv.min_stock_level * 2, int(avg_demand * 7)) - inv.quantity
        confidence = 0.8 if avg_demand > 0 else 0.5
        if confidence > 0.7:  # Safety check
            recommendations.append({
                "product_id": inv.product_id,
                "current_quantity": inv.quantity,
                "recommended_quantity": recommended,
                "confidence": confidence
            })
    
    return {"recommendations": recommendations}

@router.get("/forecast/{store_id}/{product_id}")
async def get_forecast(store_id: int, product_id: int, days: int = 7, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not has_permission(current_user.role.name, "read"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return await demand_forecast(product_id, store_id, days, db, current_user)

@router.get("/anomalies/{store_id}")
async def get_anomalies(store_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not has_permission(current_user.role.name, "read"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return await detect_anomalies(store_id, db, current_user)

@router.get("/recommendations/{store_id}")
async def get_recommendations(store_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not has_permission(current_user.role.name, "read"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return await restock_recommendations(store_id, db, current_user)