#C:\xampp\mysql\bin\mysqladmin.exe -u root shutdown  關MySQL

"""主應用程式入口"""
from pathlib import Path
import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text

from app.core.config import settings
from app.core.database import init_db, engine, SessionLocal
from app.core.middleware import setup_middleware
from app.services.auth_service import AuthService
from app.routers import (
    home,
    auth,
    category,
    search,
    detail,
    cart,
    checkout,
    course,
    contest,
    contact,
    admin,
    orders,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

setup_middleware(app)

static_dir = BASE_DIR / "static"
templates_dir = BASE_DIR / "templates"

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    logger.info(f"靜態文件目錄已掛載: {static_dir}")

templates = Jinja2Templates(directory=str(templates_dir))

def run_startup_migrations():
    """補齊既有 MySQL 資料庫和目前程式碼需要的欄位/型別。"""
    statements = [
        "ALTER TABLE course_registrations MODIFY user_id INT NULL",
        "ALTER TABLE contest_registrations MODIFY user_id INT NULL",
        "ALTER TABLE preorder_sets MODIFY set_type VARCHAR(50) NOT NULL",
        "ALTER TABLE ddj MODIFY brand VARCHAR(50)",
        "ALTER TABLE audio MODIFY audio_type VARCHAR(50) NOT NULL",
        "ALTER TABLE music MODIFY genre VARCHAR(50) NOT NULL",
        "ALTER TABLE orders MODIFY status VARCHAR(50)",
        "ALTER TABLE orders MODIFY payment_method VARCHAR(50) NULL",
    ]
    with engine.begin() as conn:
        for sql in statements:
            try:
                conn.execute(text(sql))
            except Exception as exc:
                logger.info(f"略過資料表修補：{sql} ({exc})")

@app.on_event("startup")
async def startup_event():
    logger.info(f"正在啟動 {settings.APP_NAME}...")
    try:
        init_db()
        run_startup_migrations()
        db = SessionLocal()
        try:
            AuthService.ensure_default_admin(db)
        finally:
            db.close()
        logger.info("資料庫初始化成功")
    except Exception as exc:
        logger.error(f"資料庫初始化失敗: {exc}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"正在關閉 {settings.APP_NAME}...")

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

app.include_router(home.router)
app.include_router(auth.router)
app.include_router(category.router, prefix="/category")
app.include_router(search.router, prefix="/search")
app.include_router(detail.router, prefix="/detail")
app.include_router(cart.router, prefix="/cart")
app.include_router(checkout.router, prefix="/checkout")
app.include_router(course.router, prefix="/course")
app.include_router(contest.router, prefix="/contest")
app.include_router(contact.router, prefix="/contact")
app.include_router(admin.router, prefix="/admin")
app.include_router(orders.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
