from sqlalchemy.ext.asyncio import AsyncSession

from database import AsyncSessionLocal, Base, engine


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
        await session.close()
