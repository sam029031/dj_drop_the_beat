"""商品詳情頁路由。"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.models.user import User
from app.models.preorder_set import PreorderSet
from app.services.product_service import ProductService

router = APIRouter(prefix="/detail", tags=["Detail"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[2] / "templates"))

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def detail_page(
    request: Request,
    instrument: str = "ddj",
    id: int = 1,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_current_user),
):
    product = ProductService.get_product(db, instrument, id)
    if not product:
        return templates.TemplateResponse("404.html", {"request": request, "user": user}, status_code=404)
    preorder_sets = db.query(PreorderSet).filter(PreorderSet.is_active == True).order_by(PreorderSet.sort_order.asc()).all()
    return templates.TemplateResponse("detail.html", {
        "request": request,
        "user": user,
        "instrument": instrument,
        "product": product,
        "preorder_sets": preorder_sets,
    })
