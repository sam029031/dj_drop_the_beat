"""購物車路由。"""
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.cart_service import CartService

router = APIRouter(prefix="/cart", tags=["Cart"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[2] / "templates"))

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def cart_page(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = CartService.get_or_create_cart(db, current_user.id)
    return templates.TemplateResponse("cart.html", {
        "request": request,
        "user": current_user,
        "cart": cart,
        "items": cart.items,
        "total": cart.total_price or 0,
    })

@router.post("/add")
async def add_to_cart(
    request: Request,
    preorder_set_id: int = Form(None),
    set_id: int = Form(None),
    quantity: int = Form(1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    actual_set_id = preorder_set_id or set_id
    if not actual_set_id:
        raise HTTPException(status_code=400, detail="缺少預購 SET ID")
    CartService.add_to_cart(db, current_user.id, int(actual_set_id), int(quantity))
    accept = request.headers.get("accept", "")
    if "application/json" in accept:
        return {"message": "已加入購物車"}
    return RedirectResponse(url="/cart", status_code=303)

@router.post("/update/{item_id}")
async def update_cart_item(item_id: int, quantity: int = Form(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    CartService.update_item(db, current_user.id, item_id, quantity)
    return RedirectResponse(url="/cart", status_code=303)

@router.post("/remove/{item_id}")
async def remove_cart_item(item_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    CartService.remove_item(db, current_user.id, item_id)
    return RedirectResponse(url="/cart", status_code=303)
