from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from src.conf.config import settings

engine = create_async_engine(settings.database_url)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
