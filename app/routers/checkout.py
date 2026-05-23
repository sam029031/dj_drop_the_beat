"""結帳路由"""
from pathlib import Path
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.services.cart_service import CartService
from app.services.order_service import OrderService

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent.parent / "templates"))

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def checkout_page(request: Request, db: Session = Depends(get_db), user=Depends(get_optional_current_user)):
    if not user:
        return RedirectResponse(url="/login?next=/checkout", status_code=303)
    cart_view = CartService.get_cart_view(db, user.id)
    if not cart_view["items"]:
        return RedirectResponse(url="/cart", status_code=303)
    return templates.TemplateResponse("checkout.html", {"request": request, "user": user, **cart_view})

@router.post("")
@router.post("/")
async def checkout_submit(
    request: Request,
    buyer_name: str = Form(...),
    buyer_email: str = Form(...),
    buyer_phone: str = Form(...),
    buyer_address: str = Form(...),
    notes: str = Form(None),
    db: Session = Depends(get_db),
    user=Depends(get_optional_current_user),
):
    if not user:
        return RedirectResponse(url="/login?next=/checkout", status_code=303)
    try:
        order = OrderService.create_order_from_cart(
            db,
            user.id,
            buyer_name=buyer_name,
            buyer_email=buyer_email,
            buyer_phone=buyer_phone,
            buyer_address=buyer_address,
            notes=notes
        )
        return RedirectResponse(url="/?order_success=1", status_code=303)
    except ValueError as exc:
        cart_view = CartService.get_cart_view(db, user.id)
        return templates.TemplateResponse(
            "checkout.html",
            {"request": request, "user": user, "error": str(exc), **cart_view},
            status_code=400
        )
