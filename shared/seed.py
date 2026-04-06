import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database import async_session, engine
from shared.models import Base, Role, Store, User, Product
from shared.auth import get_password_hash

async def seed_data():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as session:
        # Seed roles
        roles = [
            Role(name="Admin"),
            Role(name="Store Supervisor"),
            Role(name="Cashier"),
            Role(name="Inventory Coordinator")
        ]
        for role in roles:
            session.add(role)
        await session.commit()

        # Seed stores
        stores = [
            Store(name="Store 1", location="Location 1"),
            Store(name="Store 2", location="Location 2"),
            # Add more stores up to 86, but for demo, 2
        ]
        for store in stores:
            session.add(store)
        await session.commit()

        # Seed users
        admin_role = await session.get(Role, 1)
        supervisor_role = await session.get(Role, 2)
        cashier_role = await session.get(Role, 3)
        inventory_role = await session.get(Role, 4)

        users = [
            User(username="admin", email="admin@example.com", hashed_password=get_password_hash("admin123"), role_id=admin_role.id),
            User(username="supervisor1", email="supervisor1@example.com", hashed_password=get_password_hash("pass123"), role_id=supervisor_role.id, store_id=1),
            User(username="cashier1", email="cashier1@example.com", hashed_password=get_password_hash("pass123"), role_id=cashier_role.id, store_id=1),
            User(username="inventory1", email="inventory1@example.com", hashed_password=get_password_hash("pass123"), role_id=inventory_role.id, store_id=1),
        ]
        for user in users:
            session.add(user)
        await session.commit()

        # Seed products
        products = [
            Product(name="Product A", description="Description A", category="Category 1", sku="SKU001"),
            Product(name="Product B", description="Description B", category="Category 1", sku="SKU002"),
            Product(name="Product C", description="Description C", category="Category 2", sku="SKU003"),
        ]
        for product in products:
            session.add(product)
        await session.commit()

if __name__ == "__main__":
    asyncio.run(seed_data())