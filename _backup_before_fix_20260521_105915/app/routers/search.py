"""搜尋路由。"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.models.user import User
from app.services.product_service import ProductService

router = APIRouter(prefix="/search", tags=["Search"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[2] / "templates"))

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def search_page(
    request: Request,
    q: str = "",
    instrument: str = "",
    brand: str = "",
    price_min: float = 0,
    price_max: float = 999999,
    page: int = 1,
    id: int | None = None,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_current_user),
):
    # 如果帶 /search?instrument=ddj&id=1，直接視為查看詳情的 query 入口
    if id is not None and instrument:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=f"/detail?instrument={instrument}&id={id}", status_code=303)

    results = ProductService.search_products(db, q=q, instrument=instrument, brand=brand, price_min=price_min, price_max=price_max)
    total = len(results)
    results_page = results[(page - 1) * 12: page * 12]
    return templates.TemplateResponse("search.html", {
        "request": request,
        "user": user,
        "q": q,
        "instrument": instrument,
        "brand_filter": brand,
        "price_min": price_min,
        "price_max": price_max,
        "results": results_page,
        "total": total,
        "page": page,
        "total_pages": (total + 11) // 12,
    })
