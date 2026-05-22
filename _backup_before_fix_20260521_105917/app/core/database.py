"""
資料庫連接和會話管理
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import logging

from .config import settings

logger = logging.getLogger(__name__)

# 建立資料庫引擎
# 轉換 MySQL URL 格式
database_url = settings.DATABASE_URL
if database_url.startswith("mysql://"):
    database_url = database_url.replace("mysql://", "mysql+pymysql://")

engine = create_engine(
    database_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=3600,  # 連接回收時間
    connect_args={"charset": "utf8mb4"}
)

# 建立會話工廠
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 基礎模型類
Base = declarative_base()


def get_db() -> Session:
    """
    取得資料庫會話
    用於依賴注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    內容管理器形式的資料庫會話
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化資料庫表格"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("資料庫表格初始化完成")
    except Exception as e:
        logger.error(f"資料庫初始化失敗: {e}")
        raise
