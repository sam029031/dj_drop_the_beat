"""購物車路由"""
from pathlib import Path
from fastapi import APIRouter, Depends, Request, Body, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.services.cart_service import CartService

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent.parent / "templates"))

def _login_redirect(next_url="/cart"):
    return RedirectResponse(url=f"/login?next={next_url}", status_code=303)

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def cart_page(request: Request, db: Session = Depends(get_db), user=Depends(get_optional_current_user)):
    if not user:
        return _login_redirect("/cart")
    cart_view = CartService.get_cart_view(db, user.id)
    return templates.TemplateResponse("cart.html", {"request": request, "user": user, **cart_view})

@router.post("/add")
async def add_to_cart(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_optional_current_user),
):
    if not user:
        if request.headers.get("content-type", "").startswith("application/json"):
            raise HTTPException(status_code=401, detail="請先登入")
        return _login_redirect("/cart")

    data = {}
    if request.headers.get("content-type", "").startswith("application/json"):
        data = await request.json()
    else:
        form = await request.form()
        data = dict(form)

    set_id = data.get("preorder_set_id") or data.get("set_id")
    quantity = int(data.get("quantity") or 1)
    try:
        CartService.add_to_cart(db, user.id, int(set_id), quantity)
    except ValueError as exc:
        if request.headers.get("content-type", "").startswith("application/json"):
            raise HTTPException(status_code=400, detail=str(exc))
        return RedirectResponse(url="/cart?error=1", status_code=303)

    if request.headers.get("content-type", "").startswith("application/json"):
        return {"success": True}
    return RedirectResponse(url="/cart", status_code=303)

@router.post("/update/{item_id}")
async def update_item(item_id: int, quantity: int = Form(...), db: Session = Depends(get_db), user=Depends(get_optional_current_user)):
    if not user:
        return _login_redirect("/cart")
    CartService.update_quantity(db, user.id, item_id, quantity)
    return RedirectResponse(url="/cart", status_code=303)

@router.post("/remove/{item_id}")
async def remove_item(item_id: int, db: Session = Depends(get_db), user=Depends(get_optional_current_user)):
    if not user:
        return _login_redirect("/cart")
    CartService.remove_item(db, user.id, item_id)
    return RedirectResponse(url="/cart", status_code=303)

@router.post("/clear")
async def clear_cart(db: Session = Depends(get_db), user=Depends(get_optional_current_user)):
    if not user:
        return _login_redirect("/cart")
    CartService.clear_cart(db, user.id)
    return RedirectResponse(url="/cart", status_code=303)

@router.get("/count")
async def cart_count(db: Session = Depends(get_db), user=Depends(get_optional_current_user)):
    if not user:
        return {"count": 0}
    cart_view = CartService.get_cart_view(db, user.id)
    return {"count": cart_view["cart"].item_count}
