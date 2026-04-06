from sqlalchemy import Column, Integer, String, Text, Boolean, DECIMAL, TIMESTAMP, ForeignKey, JSON, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

class Store(Base):
    __tablename__ = 'stores'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    location = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'))
    store_id = Column(Integer, ForeignKey('stores.id'))
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    role = relationship("Role")
    store = relationship("Store")

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(50))
    sku = Column(String(50), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

class Inventory(Base):
    __tablename__ = 'inventory'
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey('stores.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False, default=0)
    min_stock_level = Column(Integer, default=10)
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    version = Column(Integer, default=1)
    vector_clock = Column(JSON, default={})

    store = relationship("Store")
    product = relationship("Product")

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey('stores.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    total_amount = Column(DECIMAL(10,2), nullable=False)
    status = Column(String(20), default='pending')
    external_id = Column(String(100), unique=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    version = Column(Integer, default=1)
    vector_clock = Column(JSON, default={})

    store = relationship("Store")
    user = relationship("User")
    items = relationship("TransactionItem", back_populates="transaction")

class TransactionItem(Base):
    __tablename__ = 'transaction_items'
    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False)
    price = Column(DECIMAL(10,2), nullable=False)

    transaction = relationship("Transaction", back_populates="items")
    product = relationship("Product")

class ReplenishmentRequest(Base):
    __tablename__ = 'replenishment_requests'
    id = Column(Integer, primary_key=True)
    from_store_id = Column(Integer, ForeignKey('stores.id'))
    to_store_id = Column(Integer, ForeignKey('stores.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False)
    status = Column(String(20), default='pending')
    requested_by = Column(Integer, ForeignKey('users.id'))
    approved_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    from_store = relationship("Store", foreign_keys=[from_store_id])
    to_store = relationship("Store", foreign_keys=[to_store_id])
    product = relationship("Product")
    requester = relationship("User", foreign_keys=[requested_by])
    approver = relationship("User", foreign_keys=[approved_by])

class EventLog(Base):
    __tablename__ = 'event_log'
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey('stores.id'))
    event_type = Column(String(50), nullable=False)
    aggregate_id = Column(Integer, nullable=False)
    aggregate_type = Column(String(50), nullable=False)
    event_data = Column(JSON, nullable=False)
    vector_clock = Column(JSON, default={})
    timestamp = Column(TIMESTAMP, server_default=func.now())
    sequence_number = Column(Integer, autoincrement=True)

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String(50), nullable=False)
    resource = Column(String(50), nullable=False)
    resource_id = Column(Integer)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    details = Column(JSON)

    user = relationship("User")