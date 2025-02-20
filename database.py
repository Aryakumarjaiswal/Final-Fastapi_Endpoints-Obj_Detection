from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base = declarative_base()

# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker, declarative_base
# from dotenv import load_dotenv
# import os

# load_dotenv()

# SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL").replace("postgresql://", "postgresql+asyncpg://")  # Ensure async driver

# # Create async engine
# engine = create_async_engine(SQLALCHEMY_DATABASE_URL, future=True, echo=True)

# # Async session factory
# AsyncSessionLocal = sessionmaker(
#     bind=engine,
#     class_=AsyncSession,
#     expire_on_commit=False,
# )

# async def get_async_db():
#     async with AsyncSessionLocal() as db:
#         yield db

# Base = declarative_base()


