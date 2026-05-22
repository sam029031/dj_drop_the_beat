from pathlib import Path

ROOT = Path(__file__).resolve().parent

def write(rel_path: str, content: str):
    path = ROOT / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"updated: {rel_path}")

# 0. 全專案 import 統一：from project.app... -> from app...
for path in ROOT.rglob("*.py"):
    if path.name == Path(__file__).name:
        continue
    text = path.read_text(encoding="utf-8", errors="replace")
    text = text.replace("project.app", "app")
    path.write_text(text, encoding="utf-8")

write("main.py", r'''
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
''')

write("app/core/config.py", r'''
"""應用程式配置。"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME: str = "DJ 器材預購與入門學習平台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:@127.0.0.1:3306/dj_platform?charset=utf8mb4",
    )

    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-secret-key")
    SESSION_SECRET: str = os.getenv("SESSION_SECRET", "change-this-session-secret")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))

    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./static/uploads")
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))
    TIMEZONE: str = os.getenv("TIMEZONE", "Asia/Taipei")

    CONTACT_PHONE: str = os.getenv("CONTACT_PHONE", "0967-676-767")
    CONTACT_EMAIL: str = os.getenv("CONTACT_EMAIL", "contact@dj-platform.local")
    CONTACT_ADDRESS: str = os.getenv("CONTACT_ADDRESS", "台灣台中市南區興大路145號")
    BUSINESS_HOURS: str = os.getenv("BUSINESS_HOURS", "週一至週五 09:00 - 18:00")
    INSTAGRAM_URL: str = os.getenv("INSTAGRAM_URL", "https://www.instagram.com/nchu_karaok/")

    ALLOWED_ORIGINS: list[str] = [
        "http://localhost",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    SMTP_SERVER: Optional[str] = os.getenv("SMTP_SERVER")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")

    PREORDER_SETS_COUNT: int = 3
    PAYMENT_DEADLINE_DAYS: int = 7
    REGISTRATION_DEADLINE_BUFFER_HOURS: int = 1

settings = Settings()
''')

write("app/core/dependencies.py", r'''
"""依賴注入。"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Cookie
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User

def _get_user_from_cookie(session: Session, session_id: Optional[str]) -> Optional[User]:
    if not session_id:
        return None
    payload = verify_token(session_id)
    if not payload:
        return None
    user_id = payload.get("sub")
    if user_id is None:
        return None
    return session.query(User).filter(User.id == int(user_id)).first()

def get_optional_current_user(
    session: Session = Depends(get_db),
    session_id: Optional[str] = Cookie(None),
) -> Optional[User]:
    return _get_user_from_cookie(session, session_id)

def get_current_user(
    session: Session = Depends(get_db),
    session_id: Optional[str] = Cookie(None),
) -> User:
    user = _get_user_from_cookie(session, session_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="請先登入")
    return user

def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理員權限")
    return current_user

# 舊程式碼相容名稱
require_admin = get_current_admin
''')

write("app/services/product_service.py", r'''
"""商品業務邏輯。"""
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.preorder_set import PreorderSet
from app.models.ddj import DDJ
from app.models.audio import Audio
from app.models.wire import Wire
from app.models.music import Music

class ProductService:
    MODEL_MAP = {
        "dj": DDJ,
        "ddj": DDJ,
        "audio": Audio,
        "wire": Wire,
        "music": Music,
    }

    @staticmethod
    def get_featured_preorder_sets(db: Session, limit: int = 3) -> list[PreorderSet]:
        return (
            db.query(PreorderSet)
            .filter(PreorderSet.is_active == True)
            .order_by(PreorderSet.sort_order.asc(), PreorderSet.id.asc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_all_preorder_sets(db: Session, page: int = 1, page_size: int = 20) -> tuple[list[PreorderSet], int]:
        skip = (page - 1) * page_size
        query = db.query(PreorderSet).filter(PreorderSet.is_active == True)
        total = query.count()
        sets = query.order_by(PreorderSet.sort_order.asc(), PreorderSet.id.asc()).offset(skip).limit(page_size).all()
        return sets, total

    @staticmethod
    def get_preorder_set_by_id(db: Session, set_id: int) -> PreorderSet | None:
        return db.query(PreorderSet).filter(PreorderSet.id == set_id, PreorderSet.is_active == True).first()

    @staticmethod
    def get_product(db: Session, instrument: str, product_id: int):
        model = ProductService.MODEL_MAP.get(instrument, DDJ)
        return db.query(model).filter(model.id == product_id).first()

    @staticmethod
    def search_products(db: Session, q: str = "", instrument: str = "", brand: str = "", price_min: float = 0, price_max: float = 999999) -> list[tuple[object, str]]:
        selected = [instrument] if instrument in ProductService.MODEL_MAP else ["ddj", "audio", "wire", "music"]
        results = []
        for key in selected:
            model = ProductService.MODEL_MAP[key]
            query = db.query(model)
            if q:
                if key == "music":
                    query = query.filter(or_(Music.title.ilike(f"%{q}%"), Music.artist.ilike(f"%{q}%"), Music.description.ilike(f"%{q}%")))
                else:
                    query = query.filter(or_(model.name.ilike(f"%{q}%"), model.description.ilike(f"%{q}%")))
            if brand and hasattr(model, "brand"):
                query = query.filter(model.brand.ilike(f"%{brand}%"))
            query = query.filter(model.price >= price_min, model.price <= price_max)
            results.extend((item, key) for item in query.all())
        return results
''')

write("app/routers/home.py", r'''
"""首頁路由。"""
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
from app.services.product_service import ProductService

router = APIRouter(tags=["Home"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[2] / "templates"))

@router.get("/", response_class=HTMLResponse)
async def get_home(
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_current_user),
):
    preorder_sets = ProductService.get_featured_preorder_sets(db, limit=3)
    latest_products = []
    for model, inst_type in [(DDJ, "ddj"), (Audio, "audio"), (Wire, "wire"), (Music, "music")]:
        latest_products.extend((p, inst_type) for p in db.query(model).order_by(model.id.asc()).limit(2).all())
    return templates.TemplateResponse("home.html", {
        "request": request,
        "user": user,
        "preorder_sets": preorder_sets,
        "latest_products": latest_products[:8],
    })
''')

write("app/routers/auth.py", r'''
"""會員登入與註冊路由。"""
from fastapi import APIRouter, Depends, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import UserRegister

router = APIRouter(tags=["Authentication"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[2] / "templates"))

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "user": None})

@router.post("/login")
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        user = AuthService.authenticate_user(db, username, password)
        token = AuthService.create_user_token(user)
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie("session_id", token, httponly=True, max_age=86400 * 7, samesite="lax")
        return response
    except ValueError as exc:
        return templates.TemplateResponse("login.html", {"request": request, "error": str(exc), "user": None}, status_code=400)

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "user": None})

@router.post("/register")
async def register_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    full_name: str = Form(""),
    phone: str = Form(""),
    address: str = Form(""),
    db: Session = Depends(get_db),
):
    if password != password_confirm:
        return templates.TemplateResponse("register.html", {"request": request, "error": "兩次輸入的密碼不一致", "user": None}, status_code=400)
    try:
        data = UserRegister(username=username, email=email, password=password, full_name=full_name or None, phone=phone or None)
        user = AuthService.register_user(db, data)
        if address:
            user.address = address
            db.commit()
        token = AuthService.create_user_token(user)
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie("session_id", token, httponly=True, max_age=86400 * 7, samesite="lax")
        return response
    except Exception as exc:
        return templates.TemplateResponse("register.html", {"request": request, "error": str(exc), "user": None}, status_code=400)

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("session_id")
    return response

# 舊網址相容：避免模板或舊連結壞掉
@router.get("/auth/login")
async def old_login_redirect():
    return RedirectResponse(url="/login", status_code=303)

@router.get("/auth/register")
async def old_register_redirect():
    return RedirectResponse(url="/register", status_code=303)

@router.get("/auth/logout")
async def old_logout_redirect():
    return await logout()
''')

write("app/models/cart.py", r'''
"""購物車模型。"""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    total_price = Column(Float, default=0)
    item_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", backref="cart")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False, index=True)
    preorder_set_id = Column(Integer, ForeignKey("preorder_sets.id"), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    added_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    cart = relationship("Cart", back_populates="items")
    preorder_set = relationship("PreorderSet")
''')

write("app/services/cart_service.py", r'''
"""購物車業務邏輯。"""
from sqlalchemy.orm import Session

from app.models.cart import Cart, CartItem
from app.models.preorder_set import PreorderSet

class CartService:
    @staticmethod
    def get_or_create_cart(db: Session, user_id: int) -> Cart:
        cart = db.query(Cart).filter(Cart.user_id == user_id).first()
        if not cart:
            cart = Cart(user_id=user_id, total_price=0, item_count=0)
            db.add(cart)
            db.commit()
            db.refresh(cart)
        return cart

    @staticmethod
    def add_to_cart(db: Session, user_id: int, set_id: int, quantity: int) -> CartItem:
        if quantity < 1:
            raise ValueError("數量至少為 1")
        cart = CartService.get_or_create_cart(db, user_id)
        preorder_set = db.query(PreorderSet).filter(PreorderSet.id == set_id, PreorderSet.is_active == True).first()
        if not preorder_set:
            raise ValueError("預購 SET 不存在")
        if preorder_set.available_quantity < quantity:
            raise ValueError("庫存不足")

        price = preorder_set.discount_price or preorder_set.price
        cart_item = db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.preorder_set_id == set_id).first()
        if cart_item:
            cart_item.quantity += quantity
            cart_item.unit_price = price
            cart_item.subtotal = cart_item.quantity * price
        else:
            cart_item = CartItem(cart_id=cart.id, preorder_set_id=set_id, quantity=quantity, unit_price=price, subtotal=quantity * price)
            db.add(cart_item)
        CartService._update_cart_totals(db, cart)
        db.commit()
        db.refresh(cart_item)
        return cart_item

    @staticmethod
    def update_item(db: Session, user_id: int, item_id: int, quantity: int) -> CartItem:
        if quantity < 1:
            raise ValueError("數量至少為 1")
        cart = CartService.get_or_create_cart(db, user_id)
        item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
        if not item:
            raise ValueError("購物車項目不存在")
        item.quantity = quantity
        item.subtotal = item.unit_price * quantity
        CartService._update_cart_totals(db, cart)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def remove_item(db: Session, user_id: int, item_id: int) -> None:
        cart = CartService.get_or_create_cart(db, user_id)
        item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
        if item:
            db.delete(item)
            CartService._update_cart_totals(db, cart)
            db.commit()

    @staticmethod
    def _update_cart_totals(db: Session, cart: Cart) -> None:
        db.flush()
        items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
        cart.total_price = sum(float(item.subtotal or 0) for item in items)
        cart.item_count = sum(int(item.quantity or 0) for item in items)
''')

write("app/routers/cart.py", r'''
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
''')

write("app/services/order_service.py", r'''
"""訂單業務邏輯。"""
from datetime import timedelta
from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem, OrderStatusEnum
from app.models.cart import Cart, CartItem
from app.models.preorder_set import PreorderSet
from app.core.utils import generate_order_number, get_current_datetime

class OrderService:
    @staticmethod
    def create_order_from_cart(
        db: Session,
        user_id: int,
        buyer_name: str,
        buyer_email: str,
        buyer_phone: str,
        buyer_address: str,
        notes: str | None = None,
    ) -> Order:
        cart = db.query(Cart).filter(Cart.user_id == user_id).first()
        if not cart or cart.item_count == 0:
            raise ValueError("購物車為空")

        now = get_current_datetime()
        order = Order(
            order_number=generate_order_number(),
            user_id=user_id,
            buyer_name=buyer_name,
            buyer_email=buyer_email,
            buyer_phone=buyer_phone,
            buyer_address=buyer_address,
            total_price=cart.total_price,
            final_price=cart.total_price,
            payment_deadline=now + timedelta(days=7),
            status=OrderStatusEnum.PENDING,
            notes=notes,
            items=[],
        )
        db.add(order)
        db.flush()

        cart_items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
        order_items_json = []
        for cart_item in cart_items:
            preorder_set = db.query(PreorderSet).filter(PreorderSet.id == cart_item.preorder_set_id).first()
            set_name = preorder_set.name if preorder_set else f"SET #{cart_item.preorder_set_id}"
            order_item = OrderItem(
                order_id=order.id,
                preorder_set_id=cart_item.preorder_set_id,
                set_name=set_name,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                subtotal=cart_item.subtotal,
            )
            db.add(order_item)
            if preorder_set:
                preorder_set.available_quantity = max((preorder_set.available_quantity or 0) - cart_item.quantity, 0)
                preorder_set.ordered_quantity = (preorder_set.ordered_quantity or 0) + cart_item.quantity
            order_items_json.append({
                "set_id": cart_item.preorder_set_id,
                "set_name": set_name,
                "quantity": cart_item.quantity,
                "unit_price": cart_item.unit_price,
                "subtotal": cart_item.subtotal,
            })

        order.items = order_items_json
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        cart.total_price = 0
        cart.item_count = 0
        db.commit()
        db.refresh(order)
        return order
''')

write("app/routers/checkout.py", r'''
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
''')

write("app/routers/category.py", r'''
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
''')

write("app/routers/search.py", r'''
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
''')

write("app/routers/detail.py", r'''
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
''')

write("app/routers/course.py", r'''
"""課程路由。"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.models.user import User
from app.models.course import Course
from app.services.course_service import CourseService

router = APIRouter(prefix="/course", tags=["Course"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[2] / "templates"))

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def course_list(request: Request, page: int = 1, db: Session = Depends(get_db), user: User | None = Depends(get_optional_current_user)):
    query = db.query(Course).filter(Course.is_active == True).order_by(Course.created_at.desc(), Course.difficulty.asc())
    total = query.count()
    courses = query.offset((page - 1) * 12).limit(12).all()
    return templates.TemplateResponse("course_list.html", {"request": request, "user": user, "courses": courses, "page": page, "total_pages": (total + 11) // 12})

@router.get("/detail", response_class=HTMLResponse)
async def course_detail(request: Request, id: int, db: Session = Depends(get_db), user: User | None = Depends(get_optional_current_user)):
    course = db.query(Course).filter(Course.id == id).first()
    if not course:
        return templates.TemplateResponse("404.html", {"request": request, "user": user}, status_code=404)
    return templates.TemplateResponse("course_detail.html", {"request": request, "user": user, "course": course})

@router.post("/register")
async def register_course(request: Request, db: Session = Depends(get_db), user: User | None = Depends(get_optional_current_user)):
    form_data = await request.form()
    course_id = int(form_data.get("course_id"))
    registration = CourseService.register_course(
        db=db,
        user_id=user.id if user else None,
        course_id=course_id,
        name=form_data.get("name"),
        email=form_data.get("email"),
        phone=form_data.get("phone"),
        notes=form_data.get("notes"),
    )
    return RedirectResponse(url=f"/course/detail?id={course_id}&registered={registration.registration_number}", status_code=303)
''')

write("app/models/course.py", r'''
"""課程模型。"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Enum, Boolean, ForeignKey
from sqlalchemy.sql import func
import enum

from app.core.database import Base

class DifficultyEnum(str, enum.Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    instructor = Column(String(100), nullable=False)
    difficulty = Column(Enum(DifficultyEnum), nullable=False, index=True)
    price = Column(Float, nullable=False)
    duration_hours = Column(Float, nullable=False)
    max_students = Column(Integer, default=30)
    current_students = Column(Integer, default=0)
    syllabus = Column(Text, nullable=True)
    prerequisites = Column(Text, nullable=True)
    learning_outcomes = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=False, index=True)
    end_date = Column(DateTime, nullable=False)
    class_schedule = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)
    is_featured = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    registration_deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    @property
    def name(self):
        return self.title

    @property
    def hours(self):
        return self.duration_hours

    @property
    def lessons(self):
        return max(1, int(round((self.duration_hours or 0) / 2)))

    @property
    def location(self):
        return "DJ 教室 / 線下課程"

    @property
    def requirements(self):
        return self.prerequisites

class CourseRegistration(Base):
    __tablename__ = "course_registrations"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    registration_number = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False)
    phone = Column(String(20), nullable=False)
    notes = Column(Text, nullable=True)
    status = Column(String(20), default="Active")
    paid = Column(Boolean, default=False)
    registered_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
''')

write("app/services/course_service.py", r'''
"""課程業務邏輯。"""
from sqlalchemy.orm import Session
import uuid

from app.models.course import Course, CourseRegistration
from app.core.utils import get_current_datetime

class CourseService:
    @staticmethod
    def register_course(db: Session, user_id: int | None, course_id: int, name: str, email: str, phone: str, notes: str | None = None) -> CourseRegistration:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise ValueError("課程不存在")
        if course.current_students >= course.max_students:
            raise ValueError("課程已滿員")
        now = get_current_datetime()
        if course.registration_deadline and now > course.registration_deadline:
            raise ValueError("報名已截止")
        if user_id:
            existing = db.query(CourseRegistration).filter(CourseRegistration.course_id == course_id, CourseRegistration.user_id == user_id).first()
            if existing:
                raise ValueError("已報名此課程")
        registration = CourseRegistration(
            course_id=course_id,
            user_id=user_id,
            registration_number=f"CRS-{uuid.uuid4().hex[:8].upper()}",
            name=name,
            email=email,
            phone=phone,
            notes=notes,
        )
        course.current_students += 1
        db.add(registration)
        db.commit()
        db.refresh(registration)
        return registration
''')

write("app/routers/contest.py", r'''
"""比賽路由。"""
from datetime import datetime
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.models.user import User
from app.models.contest import Contest
from app.services.contest_service import ContestService

router = APIRouter(prefix="/contest", tags=["Contest"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[2] / "templates"))

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def contest_list(request: Request, page: int = 1, db: Session = Depends(get_db), user: User | None = Depends(get_optional_current_user)):
    now = datetime.utcnow()
    query = db.query(Contest).filter(Contest.is_active == True, Contest.event_date > now).order_by(Contest.event_date.asc())
    total = query.count()
    contests = query.offset((page - 1) * 12).limit(12).all()
    return templates.TemplateResponse("contest_list.html", {"request": request, "user": user, "contests": contests, "page": page, "total_pages": (total + 11) // 12, "now": now})

@router.get("/detail", response_class=HTMLResponse)
async def contest_detail(request: Request, id: int, db: Session = Depends(get_db), user: User | None = Depends(get_optional_current_user)):
    contest = db.query(Contest).filter(Contest.id == id).first()
    if not contest:
        return templates.TemplateResponse("404.html", {"request": request, "user": user}, status_code=404)
    now = datetime.utcnow()
    is_registration_closed = contest.registration_deadline < now
    return templates.TemplateResponse("contest_detail.html", {"request": request, "user": user, "contest": contest, "is_registration_closed": is_registration_closed})

@router.post("/register")
async def register_contest(request: Request, db: Session = Depends(get_db), user: User | None = Depends(get_optional_current_user)):
    form_data = await request.form()
    contest_id = int(form_data.get("contest_id"))
    registration = ContestService.register_contest(
        db=db,
        user_id=user.id if user else None,
        contest_id=contest_id,
        name=form_data.get("name"),
        email=form_data.get("email"),
        phone=form_data.get("phone"),
        notes=form_data.get("notes"),
    )
    return RedirectResponse(url=f"/contest/detail?id={contest_id}&registered={registration.registration_number}", status_code=303)
''')

write("app/models/contest.py", r'''
"""比賽模型。"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func

from app.core.database import Base

class Contest(Base):
    __tablename__ = "contests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    venue = Column(String(200), nullable=False)
    entry_fee = Column(Float, default=0)
    prize_pool = Column(Float, nullable=True)
    rules = Column(Text, nullable=True)
    judging_criteria = Column(Text, nullable=True)
    registration_start = Column(DateTime, nullable=False)
    registration_deadline = Column(DateTime, nullable=False, index=True)
    event_date = Column(DateTime, nullable=False, index=True)
    event_start_time = Column(String(10), nullable=True)
    max_participants = Column(Integer, default=100)
    current_participants = Column(Integer, default=0)
    min_age = Column(Integer, nullable=True)
    image_url = Column(String(255), nullable=True)
    is_featured = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    @property
    def name(self):
        return self.title

    @property
    def location(self):
        return self.venue

    @property
    def contest_date(self):
        return self.event_date

    @property
    def notes(self):
        return self.judging_criteria

class ContestRegistration(Base):
    __tablename__ = "contest_registrations"

    id = Column(Integer, primary_key=True, index=True)
    contest_id = Column(Integer, ForeignKey("contests.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    registration_number = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False)
    phone = Column(String(20), nullable=False)
    dj_name = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String(20), default="Registered")
    paid = Column(Boolean, default=False)
    rank = Column(Integer, nullable=True)
    registered_at = Column(DateTime, server_default=func.now())
    participated_at = Column(DateTime, nullable=True)
''')

write("app/services/contest_service.py", r'''
"""比賽業務邏輯。"""
from sqlalchemy.orm import Session
import uuid

from app.models.contest import Contest, ContestRegistration
from app.core.utils import get_current_datetime

class ContestService:
    @staticmethod
    def register_contest(db: Session, user_id: int | None, contest_id: int, name: str, email: str, phone: str, dj_name: str | None = None, notes: str | None = None) -> ContestRegistration:
        contest = db.query(Contest).filter(Contest.id == contest_id).first()
        if not contest:
            raise ValueError("比賽不存在")
        if contest.current_participants >= contest.max_participants:
            raise ValueError("比賽已滿員")
        if get_current_datetime() > contest.registration_deadline:
            raise ValueError("報名已截止")
        if user_id:
            existing = db.query(ContestRegistration).filter(ContestRegistration.contest_id == contest_id, ContestRegistration.user_id == user_id).first()
            if existing:
                raise ValueError("已報名此比賽")
        registration = ContestRegistration(
            contest_id=contest_id,
            user_id=user_id,
            registration_number=f"CTT-{uuid.uuid4().hex[:8].upper()}",
            name=name,
            email=email,
            phone=phone,
            dj_name=dj_name,
            notes=notes,
        )
        contest.current_participants += 1
        db.add(registration)
        db.commit()
        db.refresh(registration)
        return registration
''')

write("app/routers/contact.py", r'''
"""聯絡我們路由。"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.models.user import User
from app.services.contact_service import ContactService
from app.core.config import settings

router = APIRouter(prefix="/contact", tags=["Contact"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[2] / "templates"))

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def contact_page(request: Request, success: bool = False, user: User | None = Depends(get_optional_current_user)):
    return templates.TemplateResponse("contact.html", {
        "request": request,
        "user": user,
        "success": success,
        "contact_email": settings.CONTACT_EMAIL,
        "contact_phone": settings.CONTACT_PHONE,
        "contact_address": settings.CONTACT_ADDRESS,
        "business_hours": settings.BUSINESS_HOURS,
        "instagram_url": settings.INSTAGRAM_URL,
    })

@router.post("/submit")
async def submit_contact(request: Request, db: Session = Depends(get_db), user: User | None = Depends(get_optional_current_user)):
    form_data = await request.form()
    contact_method = form_data.get("contact_method") or form_data.get("email") or form_data.get("phone") or "未提供"
    message_type = form_data.get("message_type") or "personal_feedback"
    unit_or_person = form_data.get("unit_or_person") or "個人"
    ContactService.create_contact_message(
        db=db,
        name=form_data.get("name"),
        email=contact_method if "@" in contact_method else f"no-email-{contact_method}@local.invalid",
        phone=contact_method,
        message_type=message_type,
        subject=unit_or_person,
        message=form_data.get("message"),
    )
    return RedirectResponse(url="/contact?success=true", status_code=303)
''')

write("app/routers/orders.py", r'''
"""訂單成功頁。"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.core.database import get_db
from app.models.order import Order

router = APIRouter(tags=["Orders"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[2] / "templates"))

@router.get("/order-success", response_class=HTMLResponse)
async def order_success(request: Request, order_id: int = 0, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first() if order_id else None
    if not order:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    return templates.TemplateResponse("order_success.html", {"request": request, "order": order})
''')

write("app/routers/admin.py", r'''
"""管理後台路由。"""
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.user import User
from app.models.ddj import DDJ
from app.models.audio import Audio
from app.models.wire import Wire
from app.models.music import Music
from app.models.order import Order
from app.models.course import Course, CourseRegistration
from app.models.contest import Contest, ContestRegistration

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[2] / "templates"))
MODEL_MAP = {"ddj": DDJ, "audio": Audio, "wire": Wire, "music": Music}

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    stats = {"products": sum(db.query(m).count() for m in MODEL_MAP.values()), "orders": db.query(Order).count(), "courses": db.query(Course).count(), "contests": db.query(Contest).count()}
    return templates.TemplateResponse("admin.html", {"request": request, "user": current_user, "stats": stats})

@router.get("/products", response_class=HTMLResponse)
async def admin_products(request: Request, instrument: str = "ddj", current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    model = MODEL_MAP.get(instrument, DDJ)
    products = db.query(model).order_by(model.id.desc()).all()
    return templates.TemplateResponse("admin_products.html", {"request": request, "user": current_user, "instrument": instrument, "products": products})

@router.post("/products/create")
async def create_product(instrument: str = Form(...), name: str = Form(...), description: str = Form(""), price: float = Form(...), stock: int = Form(0), brand: str = Form("Other"), db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    model = MODEL_MAP.get(instrument, DDJ)
    if instrument == "music":
        item = Music(title=name, artist=brand or "Various", genre="Other", price=price, description=description, in_stock=stock)
    elif instrument == "audio":
        item = Audio(name=name, audio_type="Speaker", brand=brand or "Other", price=price, description=description, in_stock=stock)
    elif instrument == "wire":
        item = Wire(name=name, wire_type="Other", brand=brand or "Other", price=price, description=description, in_stock=stock)
    else:
        item = DDJ(name=name, brand=brand or "Other", model=name, price=price, description=description, in_stock=stock)
    db.add(item)
    db.commit()
    return RedirectResponse(url=f"/admin/products?instrument={instrument}", status_code=303)

@router.post("/products/{instrument}/{product_id}/update")
async def update_product(
    instrument: str,
    product_id: int,
    name: str = Form(...),
    description: str = Form(""),
    price: float = Form(...),
    stock: int = Form(0),
    brand: str = Form("Other"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    model = MODEL_MAP.get(instrument, DDJ)
    item = db.query(model).filter(model.id == product_id).first()
    if item:
        if instrument == "music":
            item.title = name
            item.artist = brand or item.artist
        else:
            item.name = name
            if hasattr(item, "brand"):
                item.brand = brand or item.brand
        item.description = description
        item.price = price
        if hasattr(item, "in_stock"):
            item.in_stock = stock
        db.commit()
    return RedirectResponse(url=f"/admin/products?instrument={instrument}", status_code=303)

@router.post("/products/{instrument}/{product_id}/delete")
async def delete_product(instrument: str, product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    model = MODEL_MAP.get(instrument, DDJ)
    item = db.query(model).filter(model.id == product_id).first()
    if item:
        db.delete(item)
        db.commit()
    return RedirectResponse(url=f"/admin/products?instrument={instrument}", status_code=303)

@router.get("/orders", response_class=HTMLResponse)
async def admin_orders(request: Request, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    orders = db.query(Order).order_by(Order.created_at.desc()).all()
    return templates.TemplateResponse("admin_orders.html", {"request": request, "user": current_user, "orders": orders})

@router.get("/courses", response_class=HTMLResponse)
async def admin_courses(request: Request, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    courses = db.query(Course).order_by(Course.created_at.desc()).all()
    return templates.TemplateResponse("admin_courses.html", {"request": request, "user": current_user, "courses": courses})

@router.get("/courses/{course_id}/registrations", response_class=HTMLResponse)
async def admin_course_registrations(request: Request, course_id: int, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    registrations = db.query(CourseRegistration).filter(CourseRegistration.course_id == course_id).all()
    return templates.TemplateResponse("admin_courses.html", {"request": request, "user": current_user, "courses": db.query(Course).all(), "selected_course": course, "registrations": registrations})

@router.get("/contests", response_class=HTMLResponse)
async def admin_contests(request: Request, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    contests = db.query(Contest).order_by(Contest.event_date.desc()).all()
    return templates.TemplateResponse("admin_contests.html", {"request": request, "user": current_user, "contests": contests})

@router.get("/contests/{contest_id}/registrations", response_class=HTMLResponse)
async def admin_contest_registrations(request: Request, contest_id: int, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    registrations = db.query(ContestRegistration).filter(ContestRegistration.contest_id == contest_id).all()
    return templates.TemplateResponse("admin_contests.html", {"request": request, "user": current_user, "contests": db.query(Contest).all(), "selected_contest": contest, "registrations": registrations})
''')

# 模板修正
write("templates/partials/head_meta.html", r'''
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="description" content="DJ 器材預購與入門學習平台 - 提供 DJ 器材、課程、比賽等完整服務" />
<meta name="theme-color" content="#000000" />
<link rel="stylesheet" href="/static/css/variables.css" />
<link rel="stylesheet" href="/static/css/base.css" />
<link rel="stylesheet" href="/static/css/layout.css" />
<link rel="stylesheet" href="/static/css/components.css" />
<link rel="stylesheet" href="/static/css/forms.css" />
<link rel="stylesheet" href="/static/css/pages/navbar.css" />
<link rel="stylesheet" href="/static/css/pages/footer.css" />
<link rel="stylesheet" href="/static/css/pages/home.css" />
<link rel="stylesheet" href="/static/css/pages/search.css" />
<link rel="stylesheet" href="/static/css/pages/detail.css" />
<link rel="stylesheet" href="/static/css/pages/cart.css" />
<link rel="stylesheet" href="/static/css/pages/checkout.css" />
<link rel="stylesheet" href="/static/css/pages/auth.css" />
<link rel="stylesheet" href="/static/css/pages/course-contest.css" />
<link rel="stylesheet" href="/static/css/pages/contact.css" />
<link rel="stylesheet" href="/static/css/pages/admin.css" />
<link rel="stylesheet" href="/static/css/pages/order-success.css" />
<link rel="stylesheet" href="/static/css/pages/error.css" />
''')

write("templates/partials/navbar.html", r'''
<nav class="navbar">
    <div class="navbar-container container">
        <div class="navbar-brand"><a href="/" class="navbar-logo">🎛️ DJ 器材平台</a></div>
        <button class="navbar-toggle" id="navbar-toggle" aria-label="切換導覽菜單"><span></span><span></span><span></span></button>
        <ul class="navbar-menu" id="navbar-menu">
            <li><a href="/">首頁</a></li>
            <li><a href="/category?instrument=ddj">商品分類</a></li>
            <li><a href="/search">商品搜尋</a></li>
            <li><a href="/course">課程報名</a></li>
            <li><a href="/contest">比賽資訊</a></li>
            <li><a href="/contact">聯絡我們</a></li>
            <li><a href="/cart" class="navbar-icon">🛒 購物車</a></li>
            {% if user %}
                <li><a href="#">👤 {{ user.username }}</a></li>
                {% if user.is_admin %}<li><a href="/admin" class="navbar-admin">⚙️ 管理後台</a></li>{% endif %}
                <li><a href="/logout">登出</a></li>
            {% else %}
                <li><a href="/login" class="navbar-login">🔐 登入</a></li>
            {% endif %}
        </ul>
    </div>
</nav>
<script>
const toggle = document.getElementById('navbar-toggle');
if (toggle) toggle.addEventListener('click', () => document.getElementById('navbar-menu').classList.toggle('active'));
</script>
''')

write("templates/login.html", r'''
{% extends "base.html" %}
{% block title %}會員登入 - DJ 器材預購與入門學習平台{% endblock %}
{% block content %}
<section class="auth-section"><div class="auth-container"><div class="auth-card">
    <h1>會員登入</h1><p class="auth-subtitle">使用帳號和密碼登入系統</p>
    {% if error %}<div class="alert alert-error">{{ error }}</div>{% endif %}
    <form method="POST" action="/login" class="auth-form">
        <div class="form-group"><label for="username">帳號</label><input type="text" id="username" name="username" required autofocus minlength="3" /></div>
        <div class="form-group"><label for="password">密碼</label><input type="password" id="password" name="password" required minlength="8" /></div>
        <button type="submit" class="btn btn-primary btn-block">登入</button>
    </form>
    <div class="auth-links"><p>沒有會員？<a href="/register">前往註冊</a></p></div>
</div></div></section>
{% endblock %}
{% block scripts %}<script src="/static/js/auth.js"></script>{% endblock %}
''')

write("templates/register.html", r'''
{% extends "base.html" %}
{% block title %}建立帳號 - DJ 器材預購與入門學習平台{% endblock %}
{% block content %}
<section class="auth-section"><div class="auth-container"><div class="auth-card auth-card-large">
    <h1>建立新帳號</h1>
    {% if error %}<div class="alert alert-error">{{ error }}</div>{% endif %}
    <form method="POST" action="/register" class="auth-form">
        <div class="form-group"><label for="username">帳號 *</label><input type="text" id="username" name="username" required minlength="3" maxlength="50" /></div>
        <div class="form-group"><label for="email">電子郵件 *</label><input type="email" id="email" name="email" required /></div>
        <div class="form-group"><label for="password">密碼 *</label><input type="password" id="password" name="password" required minlength="8" /><small>至少 8 個字元</small></div>
        <div class="form-group"><label for="password_confirm">確認密碼 *</label><input type="password" id="password_confirm" name="password_confirm" required minlength="8" /></div>
        <div class="form-group"><label for="full_name">姓名</label><input type="text" id="full_name" name="full_name" /></div>
        <div class="form-group"><label for="phone">電話</label><input type="tel" id="phone" name="phone" /></div>
        <div class="form-group"><label for="address">地址</label><textarea id="address" name="address"></textarea></div>
        <button type="submit" class="btn btn-primary btn-block">建立帳號</button>
    </form>
    <div class="auth-links"><p>已有會員？<a href="/login">前往登入</a></p></div>
</div></div></section>
{% endblock %}
{% block scripts %}<script src="/static/js/auth.js"></script>{% endblock %}
''')

write("templates/cart.html", r'''
{% extends "base.html" %}
{% block title %}購物車 - DJ 器材預購與入門學習平台{% endblock %}
{% block content %}
<section class="cart-section"><div class="container">
    <h1 class="section-title">購物車</h1>
    {% if items %}
    <div class="cart-content">
        <div class="cart-items"><table class="cart-table"><thead><tr><th>SET 名稱</th><th>數量</th><th>單價</th><th>小計</th><th>動作</th></tr></thead><tbody>
            {% for item in items %}
            <tr>
                <td>{{ item.preorder_set.name }}</td>
                <td>
                    <form method="POST" action="/cart/update/{{ item.id }}" class="inline-form">
                        <input type="number" name="quantity" class="qty-input" value="{{ item.quantity }}" min="1" max="99" />
                        <button class="btn btn-secondary btn-sm" type="submit">修改</button>
                    </form>
                </td>
                <td>NT${{ "%.0f"|format(item.unit_price) }}</td>
                <td>NT${{ "%.0f"|format(item.subtotal) }}</td>
                <td><form method="POST" action="/cart/remove/{{ item.id }}"><button class="btn btn-danger btn-sm" type="submit">移除</button></form></td>
            </tr>
            {% endfor %}
        </tbody></table></div>
        <aside class="cart-summary"><h3>訂單摘要</h3><div class="summary-total"><span>總計：</span><span>NT${{ "%.0f"|format(total) }}</span></div><div class="cart-actions"><a href="/category?instrument=ddj" class="btn btn-secondary">繼續購物</a><a href="/checkout" class="btn btn-primary">前往結帳</a></div></aside>
    </div>
    <section class="cart-notes"><h3>購物須知</h3><ul><li>本平台提供 DJ 器材預購 SET 購買服務。</li><li>可修改數量或移除購物車商品。</li><li>送出訂單後請依指示完成付款。</li><li>確認付款後 3-5 工作天內安排出貨。</li></ul></section>
    {% else %}
    <div class="empty-cart"><p>您的購物車是空的</p><a href="/category?instrument=ddj" class="btn btn-primary">前往分類瀏覽</a></div>
    {% endif %}
</div></section>
{% endblock %}
{% block scripts %}<script src="/static/js/cart.js"></script>{% endblock %}
''')

write("templates/checkout.html", r'''
{% extends "base.html" %}
{% block title %}結帳 - DJ 器材預購與入門學習平台{% endblock %}
{% block content %}
<section class="checkout-section"><div class="container">
    <h1 class="section-title">完成購買</h1>
    <div class="checkout-layout">
        <aside class="checkout-summary"><h3>訂單概要</h3><div class="summary-items">
            {% for item in items %}<div class="summary-item"><div class="item-name">{{ item.preorder_set.name }}</div><div class="item-qty">數量：{{ item.quantity }}</div><div class="item-price">NT${{ "%.0f"|format(item.subtotal) }}</div></div>{% endfor %}
        </div><div class="summary-total"><span>總金額：</span><span class="total-amount">NT${{ "%.0f"|format(total) }}</span></div></aside>
        <main class="checkout-form"><h3>購買人資料</h3>{% if error %}<div class="alert alert-error">{{ error }}</div>{% endif %}
            <form method="POST" action="/checkout" class="form-large">
                <div class="form-group"><label for="buyer_name">姓名 *</label><input type="text" id="buyer_name" name="buyer_name" value="{{ user.full_name or '' }}" required /></div>
                <div class="form-group"><label for="buyer_phone">電話 *</label><input type="tel" id="buyer_phone" name="buyer_phone" value="{{ user.phone or '' }}" required /></div>
                <div class="form-group"><label for="buyer_email">信箱 *</label><input type="email" id="buyer_email" name="buyer_email" value="{{ user.email or '' }}" required /></div>
                <div class="form-group"><label for="buyer_address">地址 *</label><textarea id="buyer_address" name="buyer_address" required>{{ user.address or '' }}</textarea></div>
                <div class="form-group"><label for="notes">備註</label><textarea id="notes" name="notes" rows="3"></textarea></div>
                <div class="checkout-actions"><a href="/cart" class="btn btn-secondary">返回購物車</a><button type="submit" class="btn btn-primary">送出訂單</button></div>
            </form>
        </main>
    </div>
</div></section>
{% endblock %}
{% block scripts %}<script src="/static/js/checkout.js"></script>{% endblock %}
''')

write("templates/course_list.html", r'''
{% extends "base.html" %}
{% block title %}課程報名 - DJ 器材預購與入門學習平台{% endblock %}
{% block content %}
<section class="course-section"><div class="container"><h1 class="section-title">DJ 課程列表</h1><p class="section-subtitle">依上架時間與難度排列，選擇適合你的課程。</p>
{% if courses %}<div class="courses-grid">{% for course in courses %}<div class="course-card"><div class="course-header"><h3>{{ course.title }}</h3><span class="difficulty-badge">{{ course.difficulty.value if course.difficulty.value else course.difficulty }}</span></div><div class="course-info"><p><strong>講師：</strong>{{ course.instructor }}</p><p><strong>時數：</strong>{{ course.duration_hours }} 小時 / {{ course.lessons }} 堂課</p><p><strong>費用：</strong>NT${{ "%.0f"|format(course.price) }}</p></div><p class="course-description">{{ (course.description or '')[:100] }}...</p><div class="course-actions"><a href="/course/detail?id={{ course.id }}" class="btn btn-secondary">查看詳情</a><a href="/course/detail?id={{ course.id }}#form" class="btn btn-primary">立即報名</a></div></div>{% endfor %}</div>{% else %}<p class="no-courses">目前沒有可報名的課程</p>{% endif %}
</div></section>
{% endblock %}
{% block scripts %}<script src="/static/js/course.js"></script>{% endblock %}
''')

write("templates/course_detail.html", r'''
{% extends "base.html" %}
{% block title %}{{ course.title }} - DJ 器材預購與入門學習平台{% endblock %}
{% block content %}
<section class="course-detail-section"><div class="container"><nav class="breadcrumb"><a href="/">首頁</a> / <a href="/course">課程</a> / <span>{{ course.title }}</span></nav>
<div class="course-detail-layout"><aside class="course-detail-sidebar"><div class="course-image"><div class="image-placeholder">📚</div></div><div class="course-basics"><div class="basic-item"><span class="label">時數</span><span class="value">{{ course.duration_hours }} 小時 / {{ course.lessons }} 堂課</span></div><div class="basic-item"><span class="label">推薦對象</span><span class="value">{{ course.prerequisites or '對 DJ 有興趣者' }}</span></div><div class="basic-item"><span class="label">講師</span><span class="value">{{ course.instructor }}</span></div><div class="course-price-large">NT${{ "%.0f"|format(course.price) }}</div></div></aside>
<main class="course-detail-main"><h1>{{ course.title }}</h1><section class="course-section"><h3>課程詳情</h3><p>{{ course.description }}</p></section>{% if course.syllabus %}<section class="course-section"><h3>課程大綱</h3><ul>{% for line in course.syllabus.split('\n') %}{% if line.strip() %}<li>{{ line.strip() }}</li>{% endif %}{% endfor %}</ul></section>{% endif %}</main></div>
<section class="course-registration" id="form"><h2 class="section-title">課程報名表單</h2><form method="POST" action="/course/register" class="registration-form"><input type="hidden" name="course_id" value="{{ course.id }}" /><div class="form-group"><label>姓名 *</label><input name="name" value="{{ user.full_name if user else '' }}" required /></div><div class="form-group"><label>郵件 *</label><input type="email" name="email" value="{{ user.email if user else '' }}" required /></div><div class="form-group"><label>電話 *</label><input type="tel" name="phone" value="{{ user.phone if user else '' }}" required /></div><div class="form-group"><label>選擇課程</label><select name="course_id"><option value="{{ course.id }}">{{ course.title }}</option></select></div><div class="form-group"><label>備註</label><textarea name="notes" rows="4"></textarea></div><button type="submit" class="btn btn-primary btn-large">確認報名</button></form></section>
</div></section>
{% endblock %}
{% block scripts %}<script src="/static/js/course.js"></script>{% endblock %}
''')

write("templates/contest_list.html", r'''
{% extends "base.html" %}
{% block title %}比賽資訊 - DJ 器材預購與入門學習平台{% endblock %}
{% block content %}
<section class="contest-section"><div class="container"><h1 class="section-title">DJ 比賽資訊</h1><p class="section-subtitle">依比賽時間由近到遠排列。</p>
{% if contests %}<div class="contests-grid">{% for contest in contests %}<div class="contest-card"><div class="contest-header"><h3>{{ contest.title }}</h3><span class="contest-date">📅 {{ contest.event_date.strftime('%Y-%m-%d') }}</span></div><div class="contest-info"><p><strong>地點：</strong>{{ contest.venue }}</p><p><strong>報名截止：</strong>{{ contest.registration_deadline.strftime('%Y-%m-%d') }}</p>{% if contest.prize_pool %}<p><strong>獎金：</strong>NT${{ "%.0f"|format(contest.prize_pool) }}</p>{% endif %}</div><p class="contest-description">{{ (contest.description or '')[:100] }}...</p><div class="contest-actions"><a href="/contest/detail?id={{ contest.id }}" class="btn btn-secondary">查看詳情</a>{% if contest.registration_deadline > now %}<a href="/contest/detail?id={{ contest.id }}#form" class="btn btn-primary">立即報名</a>{% else %}<button class="btn btn-disabled" disabled>報名已截止</button>{% endif %}</div></div>{% endfor %}</div>{% else %}<p class="no-contests">目前沒有進行中的比賽</p>{% endif %}
</div></section>
{% endblock %}
{% block scripts %}<script src="/static/js/contest.js"></script>{% endblock %}
''')

write("templates/contest_detail.html", r'''
{% extends "base.html" %}
{% block title %}{{ contest.title }} - DJ 器材預購與入門學習平台{% endblock %}
{% block content %}
<section class="contest-detail-section"><div class="container"><nav class="breadcrumb"><a href="/">首頁</a> / <a href="/contest">比賽</a> / <span>{{ contest.title }}</span></nav>
<div class="contest-detail-layout"><aside class="contest-detail-sidebar"><div class="contest-image"><div class="image-placeholder">🏆</div></div><div class="contest-basics"><div class="basic-item"><span class="label">報名時間</span><span class="value">{{ contest.registration_start.strftime('%Y-%m-%d') }} ~ {{ contest.registration_deadline.strftime('%Y-%m-%d') }}</span></div><div class="basic-item"><span class="label">比賽日期</span><span class="value">{{ contest.event_date.strftime('%Y-%m-%d') }}</span></div><div class="basic-item"><span class="label">地點</span><span class="value">{{ contest.venue }}</span></div></div></aside><main class="contest-detail-main"><h1>{{ contest.title }}</h1><section><h3>賽事簡介</h3><p>{{ contest.description }}</p></section>{% if contest.rules %}<section><h3>比賽規則</h3><p>{{ contest.rules }}</p></section>{% endif %}<section><h3>比賽相關注意事項</h3><p>{{ contest.judging_criteria or '請遵守現場工作人員指示，並於報到時間內完成報到。' }}</p></section></main></div>
{% if not is_registration_closed %}<section class="contest-registration" id="form"><h2 class="section-title">比賽報名表單</h2><form method="POST" action="/contest/register" class="registration-form"><input type="hidden" name="contest_id" value="{{ contest.id }}" /><div class="form-group"><label>姓名 *</label><input name="name" value="{{ user.full_name if user else '' }}" required /></div><div class="form-group"><label>郵件 *</label><input type="email" name="email" value="{{ user.email if user else '' }}" required /></div><div class="form-group"><label>電話 *</label><input type="tel" name="phone" value="{{ user.phone if user else '' }}" required /></div><div class="form-group"><label>選擇賽事</label><select name="contest_id"><option value="{{ contest.id }}">{{ contest.title }}</option></select></div><div class="form-group"><label>備註</label><textarea name="notes" rows="4"></textarea></div><button type="submit" class="btn btn-primary btn-large">確認報名</button></form></section>{% else %}<div class="alert alert-warning">報名已截止</div>{% endif %}
</div></section>
{% endblock %}
{% block scripts %}<script src="/static/js/contest.js"></script>{% endblock %}
''')

write("templates/contact.html", r'''
{% extends "base.html" %}
{% block title %}聯絡我們 - DJ 器材預購與入門學習平台{% endblock %}
{% block content %}
<section class="contact-section"><div class="container"><h1 class="section-title">聯絡我們</h1><p class="section-subtitle">意見回饋、廠商贊助與合作洽詢都可以在此留言。</p>
<div class="contact-layout"><aside class="contact-info"><h3>聯絡資訊</h3><div class="info-item"><span class="label">📍 地址</span><p>{{ contact_address }}</p></div><div class="info-item"><span class="label">📱 電話</span><p><a href="tel:{{ contact_phone }}">{{ contact_phone }}</a></p></div><div class="info-item"><span class="label">📧 Email</span><p><a href="mailto:{{ contact_email }}">{{ contact_email }}</a></p></div><div class="info-item"><span class="label">⏰ 營業時間</span><p>{{ business_hours }}</p></div><div class="info-item"><span class="label">📸 IG</span><p><a href="{{ instagram_url }}" target="_blank">Instagram @nchu_karaok</a></p></div></aside>
<main class="contact-form-section"><h3>聯絡表單</h3>{% if success %}<div class="alert alert-success">感謝您的訊息，我們已收到。</div>{% endif %}<form method="POST" action="/contact/submit" class="contact-form"><div class="form-group"><label>姓名 *</label><input name="name" value="{{ user.full_name if user else '' }}" required /></div><div class="form-group"><label>單位或個人 *</label><input name="unit_or_person" placeholder="例如：個人 / XX廠商" required /></div><div class="form-group"><label>聯絡方式 *</label><input name="contact_method" value="{{ user.email if user else '' }}" placeholder="電話或 Email" required /></div><div class="form-group"><label>聯絡類型 *</label><div class="radio-group"><label><input type="radio" name="message_type" value="personal_feedback" checked /> 個人意見回饋</label><label><input type="radio" name="message_type" value="sponsor_inquiry" /> 廠商贊助</label></div></div><div class="form-group"><label>詳細內容 *</label><textarea name="message" rows="6" required minlength="10"></textarea></div><div class="form-actions"><button type="submit" class="btn btn-primary">送出訊息</button><button type="reset" class="btn btn-secondary">清除</button></div></form></main></div>
<section class="faq-section"><h3>意見回饋 / 廠商贊助說明</h3><p>個人意見回饋可由會員自動帶入資料；廠商贊助不須登入，也可以直接留下單位與聯絡方式。</p></section>
</div></section>
{% endblock %}
{% block scripts %}<script src="/static/js/contact.js"></script>{% endblock %}
''')

# 補強商品模型的模板相容屬性：以追加方式安全加入，不改資料表欄位
for rel, additions in {
    "app/models/ddj.py": """
\n# ---- template compatibility ----\nDDJ.image = property(lambda self: self.image_url)\nDDJ.stock = property(lambda self: self.in_stock)\nDDJ.features = property(lambda self: self.description)\n""",
    "app/models/audio.py": """
\n# ---- template compatibility ----\nAudio.image = property(lambda self: self.image_url)\nAudio.stock = property(lambda self: self.in_stock)\nAudio.form = property(lambda self: self.audio_type.value if hasattr(self.audio_type, 'value') else self.audio_type)\nAudio.size = property(lambda self: self.frequency_response)\nAudio.features = property(lambda self: self.description)\n""",
    "app/models/wire.py": """
\n# ---- template compatibility ----\nWire.image = property(lambda self: self.image_url)\nWire.stock = property(lambda self: self.in_stock)\nWire.type = property(lambda self: self.wire_type)\nWire.length = property(lambda self: f'{self.length_meters:g} 公尺' if self.length_meters else '')\n""",
    "app/models/music.py": """
\n# ---- template compatibility ----\nMusic.name = property(lambda self: self.title)\nMusic.brand = property(lambda self: self.artist)\nMusic.image = property(lambda self: self.image_url)\nMusic.stock = property(lambda self: self.in_stock)\nMusic.format = property(lambda self: 'FLAC / MP3 / 唱片')\n""",
}.items():
    p = ROOT / rel
    text = p.read_text(encoding="utf-8")
    if "# ---- template compatibility ----" not in text:
        p.write_text(text.rstrip() + additions + "\n", encoding="utf-8")
        print(f"patched compatibility: {rel}")

# CSS：結帳桌機左 1/3，手機摘要在上；字體補強。
css_path = ROOT / "static/css/variables.css"
if css_path.exists():
    css = css_path.read_text(encoding="utf-8")
    if "Noto Sans TC" not in css:
        css += '\n:root {\n  --font-family-base: "Microsoft JhengHei", "Noto Sans TC", "PingFang TC", "Segoe UI", Arial, sans-serif;\n}\nbody { font-family: var(--font-family-base); }\n.icon, .info-icon, .navbar-icon { width: 24px; height: 24px; line-height: 24px; }\n.btn { min-height: 44px; display: inline-flex; align-items: center; justify-content: center; }\n'
        css_path.write_text(css, encoding="utf-8")
        print("patched css variables")

checkout_css = ROOT / "static/css/pages/checkout.css"
if checkout_css.exists():
    css = checkout_css.read_text(encoding="utf-8")
    css += '\n/* checkout layout requirement patch */\n.checkout-layout { display: grid; grid-template-columns: minmax(280px, 1fr) 2fr; gap: 2rem; align-items: start; }\n.checkout-summary { max-height: calc(100vh - 180px); overflow-y: auto; position: sticky; top: 90px; }\n.summary-total { position: sticky; bottom: 0; padding: 1rem 0; }\n@media (max-width: 768px) { .checkout-layout { display: flex; flex-direction: column; } .checkout-summary { order: 1; position: static; max-height: none; overflow: visible; width: 100%; } .checkout-form { order: 2; width: 100%; } }\n'
    checkout_css.write_text(css, encoding="utf-8")
    print("patched checkout css")

print("\n完成。接著請執行：python -m compileall .")
