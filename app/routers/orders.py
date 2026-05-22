"""訂單成功頁"""
from pathlib import Path
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.models.order import Order

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent.parent / "templates"))

@router.get("/order-success", response_class=HTMLResponse)
async def order_success(request: Request, order_id: int = 0, db: Session = Depends(get_db), user=Depends(get_optional_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first() if order_id else None
    if not order:
        return templates.TemplateResponse("404.html", {"request": request, "user": user}, status_code=404)
    return templates.TemplateResponse("order_success.html", {"request": request, "user": user, "order": order})
