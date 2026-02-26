from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from typing import Annotated
from fastapi import Depends
import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_SYNC_URL = os.getenv("DATABASE_SYNC_URL")

engine = create_async_engine(DATABASE_URL)
sync_engine = create_engine(DATABASE_SYNC_URL)

AsyncSessionLocal = async_sessionmaker(bind=engine)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

Base = declarative_base()

async def get_db_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        
def get_sync_session():
    return SyncSessionLocal()

SessionDep = Annotated[AsyncSession, Depends(get_db_session)]