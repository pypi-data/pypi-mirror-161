from sqlalchemy import create_engine, Column, Integer, DateTime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

engine = create_engine("sqlite:///./test.db")
async_engine = create_async_engine("sqlite+aiosqlite:///./test.db")

TestingSessionLocal = sessionmaker(bind=engine)
TestingSessionLocalAsync = sessionmaker(bind=async_engine, class_=AsyncSession)

Base = declarative_base()


class SimpleTestOrm(Base):
    __tablename__ = 'test_database'

    id: int = Column(Integer, primary_key=True, index=True)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
