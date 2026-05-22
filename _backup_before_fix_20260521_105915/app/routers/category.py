"""分類頁路由。"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.models.user import User
from app.models.ddj import DDJ
from app.models.audio import Audio
from app.models.wire import Wire
from app.models.music import Music

router = APIRouter(prefix="/category", tags=["Category"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[2] / "templates"))

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def category_page(
    request: Request,
    instrument: str = "ddj",
    brand: str = "",
    price_min: float = 0,
    price_max: float = 999999,
    page: int = 1,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_current_user),
):
    model_map = {"dj": DDJ, "ddj": DDJ, "audio": Audio, "wire": Wire, "music": Music}
    model = model_map.get(instrument, DDJ)
    query = db.query(model)
    if brand and hasattr(model, "brand"):
        query = query.filter(model.brand.ilike(f"%{brand}%"))
    query = query.filter(model.price >= price_min, model.price <= price_max)
    total = query.count()
    products = query.offset((page - 1) * 12).limit(12).all()
    return templates.TemplateResponse("category.html", {
        "request": request,
        "user": user,
        "instrument": instrument,
        "products": products,
        "brand_filter": brand,
        "price_min": price_min,
        "price_max": price_max,
        "page": page,
        "total": total,
        "total_pages": (total + 11) // 12,
    })
