"""FastAPI 主入口：集中註冊所有路由與靜態資源。"""
import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.core.database import init_db
from app.core.middleware import setup_middleware
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
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
static_dir = BASE_DIR / "static"
templates_dir = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

setup_middleware(app)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.on_event("startup")
async def startup_event():
    logger.info(f"正在啟動 {settings.APP_NAME}...")
    try:
        init_db()
        logger.info("資料庫初始化成功")
    except Exception as exc:
        logger.error(f"資料庫初始化失敗：{exc}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"正在關閉 {settings.APP_NAME}...")

@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return templates.TemplateResponse("500.html", {"request": request}, status_code=500)

# 頁面路由
app.include_router(home.router)
app.include_router(auth.router)
app.include_router(category.router)
app.include_router(search.router)
app.include_router(detail.router)
app.include_router(cart.router)
app.include_router(checkout.router)
app.include_router(course.router)
app.include_router(contest.router)
app.include_router(contact.router)
app.include_router(admin.router)
app.include_router(orders.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
