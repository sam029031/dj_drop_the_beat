"""搜尋路由"""
from pathlib import Path
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.services.product_service import ProductService

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent.parent / "templates"))

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def search_page(
    request: Request,
    q: str = "",
    instrument: str = "",
    id: int | None = None,
    brand: str = "",
    price_min: float = 0,
    price_max: float = 999999,
    page: int = 1,
    db: Session = Depends(get_db),
    user=Depends(get_optional_current_user),
):
    if id is not None and instrument:
        return RedirectResponse(url=f"/detail?instrument={instrument}&id={id}", status_code=303)

    results = ProductService.search_products(
        db,
        query=q,
        category=(instrument or None),
        brand=brand,
        price_min=price_min,
        price_max=price_max
    )
    total = len(results)
    page_results = results[(page - 1) * 12: page * 12]
    return templates.TemplateResponse("search.html", {
        "request": request,
        "user": user,
        "q": q,
        "instrument": instrument,
        "brand_filter": brand,
        "price_min": price_min,
        "price_max": price_max,
        "results": page_results,
        "total": total,
        "page": page,
        "total_pages": (total + 11) // 12,
    })
