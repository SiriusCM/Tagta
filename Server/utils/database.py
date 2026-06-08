from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings as config

# 使用 PostgreSQL 配置
DATABASE_URL = config.DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()