"""結帳路由。"""
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.cart_service import CartService
from app.services.order_service import OrderService

router = APIRouter(prefix="/checkout", tags=["Checkout"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[2] / "templates"))

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def checkout_page(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = CartService.get_or_create_cart(db, current_user.id)
    return templates.TemplateResponse("checkout.html", {
        "request": request,
        "user": current_user,
        "cart": cart,
        "total": cart.total_price or 0,
        "items": cart.items,
    })

@router.post("")
@router.post("/")
async def checkout_submit(
    request: Request,
    buyer_name: str = Form(...),
    buyer_email: str = Form(...),
    buyer_phone: str = Form(...),
    buyer_address: str = Form(...),
    notes: str = Form(""),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        order = OrderService.create_order_from_cart(
            db,
            current_user.id,
            buyer_name,
            buyer_email,
            buyer_phone,
            buyer_address,
            notes or None,
        )
        return RedirectResponse(url=f"/order-success?order_id={order.id}", status_code=303)
    except ValueError as exc:
        cart = CartService.get_or_create_cart(db, current_user.id)
        return templates.TemplateResponse("checkout.html", {
            "request": request,
            "user": current_user,
            "cart": cart,
            "total": cart.total_price or 0,
            "items": cart.items,
            "error": str(exc),
        }, status_code=400)
