from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

# Auth schemas
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role_id: int
    store_id: Optional[int] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Store schemas
class StoreBase(BaseModel):
    name: str
    location: Optional[str] = None

class StoreCreate(StoreBase):
    pass

class Store(StoreBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Product schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    sku: str

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Inventory schemas
class InventoryBase(BaseModel):
    store_id: int
    product_id: int
    quantity: int
    min_stock_level: int = 10

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    quantity: Optional[int] = None
    min_stock_level: Optional[int] = None

class Inventory(InventoryBase):
    id: int
    last_updated: datetime
    version: int
    vector_clock: Dict[str, int] = {}

    class Config:
        from_attributes = True

# Transaction schemas
class TransactionItemBase(BaseModel):
    product_id: int
    quantity: int
    price: float

class TransactionCreate(BaseModel):
    store_id: int
    user_id: int
    items: List[TransactionItemBase]
    external_id: Optional[str] = None

class Transaction(TransactionCreate):
    id: int
    total_amount: float
    status: str
    created_at: datetime
    updated_at: datetime
    version: int
    vector_clock: Dict[str, int] = {}

    class Config:
        from_attributes = True

# Replenishment schemas
class ReplenishmentRequestBase(BaseModel):
    from_store_id: int
    to_store_id: int
    product_id: int
    quantity: int

class ReplenishmentRequestCreate(ReplenishmentRequestBase):
    requested_by: int

class ReplenishmentRequest(ReplenishmentRequestBase):
    id: int
    status: str
    requested_by: int
    approved_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Sync schemas for offline
class SyncData(BaseModel):
    inventories: List[Inventory]
    transactions: List[Transaction]

class SyncResponse(BaseModel):
    conflicts: List[dict]  # list of conflicting items

# AI schemas
class ForecastResponse(BaseModel):
    forecast: List[float]

class AnomalyResponse(BaseModel):
    anomalies: List[Dict]

class RecommendationResponse(BaseModel):
    recommendations: List[Dict]

class ConversationalResponse(BaseModel):
    response: str
    confidence: Optional[float] = None
    details: Optional[Dict] = None