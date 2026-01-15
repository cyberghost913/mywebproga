from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from typing import Annotated
from fastapi import Depends

DATABASE_URL = "postgresql+asyncpg://user:admin@localhost:5433/webdev"

engine = create_async_engine(DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(bind=engine)

Base = declarative_base()

async def get_db_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e

SessionDep = Annotated[AsyncSession, Depends(get_db_session)]