
# -*- coding: utf-8 -*-
"""
fix_latest_dj_project.py
放在專案根目錄（與 main.py 同層）後執行：
    python fix_latest_dj_project.py
"""
from pathlib import Path
from datetime import datetime
import re

ROOT = Path(__file__).resolve().parent
BACKUP_DIR = ROOT / f"_backup_before_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def backup(path: Path):
    if path.exists():
        dst = BACKUP_DIR / path.relative_to(ROOT)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(path.read_bytes())

def write_file(rel: str, content: str):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    backup(path)
    path.write_text(content.strip() + "\n", encoding="utf-8", newline="\n")
    print(f"[WRITE] {rel}")

def patch_file(rel: str, replacements):
    path = ROOT / rel
    if not path.exists():
        print(f"[SKIP] {rel} 不存在")
        return
    backup(path)
    text = path.read_text(encoding="utf-8")
    old_text = text
    for old, new in replacements:
        text = text.replace(old, new)
    if text != old_text:
        path.write_text(text, encoding="utf-8", newline="\n")
        print(f"[PATCH] {rel}")
    else:
        print(f"[NOCHANGE] {rel}")

def global_import_patch():
    for path in ROOT.rglob("*.py"):
        if "venv" in path.parts or "_backup_before_fix_" in str(path):
            continue
        backup(path)
        text = path.read_text(encoding="utf-8")
        new = text.replace("from app.", "from app.").replace("import app.", "import app.")
        new = new.replace("__import__('app.", "__import__('app.")
        if new != text:
            path.write_text(new, encoding="utf-8", newline="\n")
            print(f"[IMPORT] {path.relative_to(ROOT)}")

def patch_enum_models_to_string():
    targets = {
        "app/models/ddj.py": [
            ("from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Enum",
             "from sqlalchemy import Column, Integer, String, Float, Text, DateTime"),
            ("brand = Column(Enum(BrandEnum), default=BrandEnum.PIONEER)",
             "brand = Column(String(50), default='Pioneer')")
        ],
        "app/models/audio.py": [
            ("from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Enum, Boolean",
             "from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean"),
            ("audio_type = Column(Enum(AudioTypeEnum), nullable=False)",
             "audio_type = Column(String(50), nullable=False)")
        ],
        "app/models/music.py": [
            ("from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Enum, Boolean",
             "from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean"),
            ("genre = Column(Enum(GenreEnum), nullable=False, index=True)",
             "genre = Column(String(50), nullable=False, index=True)")
        ],
        "app/models/preorder_set.py": [
            ("from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON, Enum, Boolean",
             "from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON, Boolean"),
            ("set_type = Column(Enum(SetTypeEnum), nullable=False, index=True)",
             "set_type = Column(String(50), nullable=False, index=True)")
        ],
        "app/models/course.py": [
            ("from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Enum, Boolean, ForeignKey",
             "from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey"),
            ("difficulty = Column(Enum(DifficultyEnum), nullable=False, index=True)",
             "difficulty = Column(String(50), nullable=False, index=True)"),
            ('user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)',
             'user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)')
        ],
        "app/models/contest.py": [
            ('user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)',
             'user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)')
        ],
        "app/models/order.py": [
            ("from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON, Enum, ForeignKey",
             "from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON, ForeignKey"),
            ("status = Column(Enum(OrderStatusEnum), default=OrderStatusEnum.PENDING, index=True)",
             "status = Column(String(50), default='Pending', index=True)"),
            ("payment_method = Column(Enum(PaymentMethodEnum), nullable=True)",
             "payment_method = Column(String(50), nullable=True)")
        ],
    }
    for rel, reps in targets.items():
        patch_file(rel, reps)

MAIN_PY = """
\"\"\"主應用程式入口\"\"\"
from pathlib import Path
import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text

from app.core.config import settings
from app.core.database import init_db, engine, SessionLocal
from app.core.middleware import setup_middleware
from app.services.auth_service import AuthService
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
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

setup_middleware(app)

static_dir = BASE_DIR / "static"
templates_dir = BASE_DIR / "templates"

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    logger.info(f"靜態文件目錄已掛載: {static_dir}")

templates = Jinja2Templates(directory=str(templates_dir))

def run_startup_migrations():
    \"\"\"補齊既有 MySQL 資料庫和目前程式碼需要的欄位/型別。\"\"\"
    statements = [
        "ALTER TABLE course_registrations MODIFY user_id INT NULL",
        "ALTER TABLE contest_registrations MODIFY user_id INT NULL",
        "ALTER TABLE preorder_sets MODIFY set_type VARCHAR(50) NOT NULL",
        "ALTER TABLE ddj MODIFY brand VARCHAR(50)",
        "ALTER TABLE audio MODIFY audio_type VARCHAR(50) NOT NULL",
        "ALTER TABLE music MODIFY genre VARCHAR(50) NOT NULL",
        "ALTER TABLE orders MODIFY status VARCHAR(50)",
        "ALTER TABLE orders MODIFY payment_method VARCHAR(50) NULL",
    ]
    with engine.begin() as conn:
        for sql in statements:
            try:
                conn.execute(text(sql))
            except Exception as exc:
                logger.info(f"略過資料表修補：{sql} ({exc})")

@app.on_event("startup")
async def startup_event():
    logger.info(f"正在啟動 {settings.APP_NAME}...")
    try:
        init_db()
        run_startup_migrations()
        db = SessionLocal()
        try:
            AuthService.ensure_default_admin(db)
        finally:
            db.close()
        logger.info("資料庫初始化成功")
    except Exception as exc:
        logger.error(f"資料庫初始化失敗: {exc}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"正在關閉 {settings.APP_NAME}...")

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

app.include_router(home.router)
app.include_router(auth.router)
app.include_router(category.router, prefix="/category")
app.include_router(search.router, prefix="/search")
app.include_router(detail.router, prefix="/detail")
app.include_router(cart.router, prefix="/cart")
app.include_router(checkout.router, prefix="/checkout")
app.include_router(course.router, prefix="/course")
app.include_router(contest.router, prefix="/contest")
app.include_router(contact.router, prefix="/contact")
app.include_router(admin.router, prefix="/admin")
app.include_router(orders.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
"""

CONFIG_PY = """
\"\"\"應用程式配置\"\"\"
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Settings:
    APP_NAME: str = "DJ 器材預購與入門學習平台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("1", "true", "yes", "on")

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:@127.0.0.1:3306/dj_platform?charset=utf8mb4"
    )

    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-secret-key")
    SESSION_SECRET: str = os.getenv("SESSION_SECRET", "change-this-session-secret")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))

    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./static/uploads")
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))

    TIMEZONE: str = os.getenv("TIMEZONE", "Asia/Taipei")

    CONTACT_EMAIL: str = os.getenv("CONTACT_EMAIL", "service@djequip.com")
    CONTACT_PHONE: str = os.getenv("CONTACT_PHONE", "0967-676-767")
    CONTACT_ADDRESS: str = os.getenv("CONTACT_ADDRESS", "台中市南區興大路145號")
    BUSINESS_HOURS: str = os.getenv("BUSINESS_HOURS", "週一至週五 09:00-18:00")
    INSTAGRAM_URL: str = os.getenv("INSTAGRAM_URL", "https://www.instagram.com/nchu_karaok/")

    ALLOWED_ORIGINS: list = [
        "http://localhost",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
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
"""

DEPENDENCIES_PY = """
\"\"\"依賴注入\"\"\"
from fastapi import Depends, HTTPException, status, Cookie
from sqlalchemy.orm import Session
from typing import Optional
import logging

from .database import get_db
from .security import verify_token
from ..models.user import User

logger = logging.getLogger(__name__)

def _user_from_cookie(session: Session, session_id: Optional[str]) -> Optional[User]:
    if not session_id:
        return None
    payload = verify_token(session_id)
    if not payload:
        return None
    user_id = payload.get("sub")
    try:
        user_id = int(user_id)
    except Exception:
        return None
    return session.query(User).filter(User.id == user_id, User.is_active == True).first()

def get_current_user(
    session: Session = Depends(get_db),
    session_id: Optional[str] = Cookie(None)
) -> User:
    user = _user_from_cookie(session, session_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登入或登入狀態已失效"
        )
    return user

def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限訪問，需要管理員帳號"
        )
    return current_user

def require_admin(current_user: User = Depends(get_current_admin)) -> User:
    return current_user

def get_optional_current_user(
    session: Session = Depends(get_db),
    session_id: Optional[str] = Cookie(None)
) -> Optional[User]:
    return _user_from_cookie(session, session_id)
"""

AUTH_SERVICE_PY = """
\"\"\"認證業務邏輯\"\"\"
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.auth import UserRegister
import logging

logger = logging.getLogger(__name__)

class AuthService:
    @staticmethod
    def ensure_default_admin(db: Session) -> User:
        admin = db.query(User).filter(User.username == "admin").first()
        hashed = hash_password("Admin@123456")
        if not admin:
            admin = User(
                username="admin",
                email="admin@dj-platform.com",
                password_hash=hashed,
                full_name="DJ Platform Admin",
                phone="0967-676-767",
                is_admin=True,
                is_active=True
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            logger.info("已建立預設管理員：admin / Admin@123456")
            return admin

        changed = False
        if not verify_password("Admin@123456", admin.password_hash):
            admin.password_hash = hashed
            changed = True
        if not admin.is_admin:
            admin.is_admin = True
            changed = True
        if not admin.is_active:
            admin.is_active = True
            changed = True
        if changed:
            db.commit()
            db.refresh(admin)
            logger.info("已修正預設管理員密碼與權限：admin / Admin@123456")
        return admin

    @staticmethod
    def register_user(db: Session, user_data: UserRegister, address: str | None = None) -> User:
        exists = db.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        if exists:
            raise ValueError("用戶名或郵箱已存在")

        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            full_name=user_data.full_name,
            phone=user_data.phone,
            address=address,
            is_admin=False,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> User:
        user = db.query(User).filter(User.username == username).first()

        if username == "admin" and password == "Admin@123456":
            user = AuthService.ensure_default_admin(db)
            return user

        if not user:
            raise ValueError("用戶名稱或密碼錯誤")

        if not verify_password(password, user.password_hash):
            raise ValueError("用戶名稱或密碼錯誤")

        if not user.is_active:
            raise ValueError("帳號已停用")

        return user

    @staticmethod
    def create_user_token(user: User) -> str:
        return create_access_token({"sub": str(user.id), "username": user.username})
"""

PRODUCT_SERVICE_PY = """
\"\"\"商品業務邏輯\"\"\"
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.preorder_set import PreorderSet
from app.models.ddj import DDJ
from app.models.audio import Audio
from app.models.wire import Wire
from app.models.music import Music

MODEL_MAP = {
    "dj": DDJ,
    "ddj": DDJ,
    "audio": Audio,
    "wire": Wire,
    "music": Music,
}

class ProductService:
    @staticmethod
    def get_featured_preorder_sets(db: Session, limit: int = 3) -> list:
        return db.query(PreorderSet).filter(
            PreorderSet.is_featured == True,
            PreorderSet.is_active == True
        ).order_by(PreorderSet.sort_order.asc(), PreorderSet.id.asc()).limit(limit).all()

    @staticmethod
    def get_all_preorder_sets(db: Session, page: int = 1, page_size: int = 20) -> tuple:
        skip = (page - 1) * page_size
        query = db.query(PreorderSet).filter(PreorderSet.is_active == True)
        total = query.count()
        sets = query.order_by(PreorderSet.sort_order.asc(), PreorderSet.id.asc()).offset(skip).limit(page_size).all()
        return sets, total

    @staticmethod
    def get_preorder_set_by_id(db: Session, set_id: int) -> PreorderSet | None:
        return db.query(PreorderSet).filter(
            PreorderSet.id == set_id,
            PreorderSet.is_active == True
        ).first()

    @staticmethod
    def get_product(db: Session, instrument: str, product_id: int):
        model = MODEL_MAP.get((instrument or "ddj").lower())
        if not model:
            return None
        return db.query(model).filter(model.id == product_id).first()

    @staticmethod
    def search_products(db: Session, query: str = "", category: str | None = None,
                        brand: str = "", price_min: float = 0, price_max: float = 999999) -> list:
        models = [MODEL_MAP[category]] if category in MODEL_MAP else [DDJ, Audio, Wire, Music]
        results = []
        for model in models:
            q = db.query(model)
            if query:
                if model is Music:
                    q = q.filter(or_(Music.title.ilike(f"%{query}%"), Music.artist.ilike(f"%{query}%"), Music.description.ilike(f"%{query}%")))
                else:
                    q = q.filter(or_(model.name.ilike(f"%{query}%"), model.description.ilike(f"%{query}%")))
            if brand and hasattr(model, "brand"):
                q = q.filter(model.brand.ilike(f"%{brand}%"))
            if hasattr(model, "price"):
                q = q.filter(model.price >= price_min, model.price <= price_max)
            inst = "music" if model is Music else model.__tablename__
            for item in q.all():
                results.append((item, inst))
        return results
"""

CART_SERVICE_PY = """
\"\"\"購物車業務邏輯\"\"\"
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
    def _price(preorder_set: PreorderSet) -> float:
        return float(preorder_set.discount_price or preorder_set.price or 0)

    @staticmethod
    def _update_item_subtotal(item: CartItem):
        item.subtotal = float(item.unit_price or 0) * int(item.quantity or 0)

    @staticmethod
    def _update_cart_totals(db: Session, cart: Cart):
        items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
        total = 0
        count = 0
        for item in items:
            CartService._update_item_subtotal(item)
            total += float(item.subtotal or 0)
            count += int(item.quantity or 0)
        cart.total_price = total
        cart.item_count = count
        db.add(cart)

    @staticmethod
    def add_to_cart(db: Session, user_id: int, set_id: int, quantity: int = 1) -> CartItem:
        quantity = max(1, int(quantity or 1))
        cart = CartService.get_or_create_cart(db, user_id)
        preorder_set = db.query(PreorderSet).filter(PreorderSet.id == set_id, PreorderSet.is_active == True).first()
        if not preorder_set:
            raise ValueError("預購 SET 不存在")
        if preorder_set.available_quantity is not None and preorder_set.available_quantity < quantity:
            raise ValueError("庫存不足")

        item = db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.preorder_set_id == set_id
        ).first()

        if item:
            item.quantity += quantity
            CartService._update_item_subtotal(item)
        else:
            item = CartItem(
                cart_id=cart.id,
                preorder_set_id=set_id,
                quantity=quantity,
                unit_price=CartService._price(preorder_set),
                subtotal=quantity * CartService._price(preorder_set)
            )
            db.add(item)

        CartService._update_cart_totals(db, cart)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def get_cart_view(db: Session, user_id: int) -> dict:
        cart = CartService.get_or_create_cart(db, user_id)
        rows = db.query(CartItem, PreorderSet).join(
            PreorderSet, CartItem.preorder_set_id == PreorderSet.id
        ).filter(CartItem.cart_id == cart.id).all()

        items = []
        total = 0
        for cart_item, preorder_set in rows:
            unit_price = float(cart_item.unit_price or preorder_set.discount_price or preorder_set.price or 0)
            subtotal = unit_price * int(cart_item.quantity or 0)
            total += subtotal
            items.append({
                "id": cart_item.id,
                "preorder_set_id": preorder_set.id,
                "name": preorder_set.name,
                "description": preorder_set.description,
                "included_items": preorder_set.included_items or [],
                "quantity": cart_item.quantity,
                "unit_price": unit_price,
                "subtotal": subtotal,
            })

        cart.total_price = total
        cart.item_count = sum(item["quantity"] for item in items)
        db.commit()
        return {"cart": cart, "items": items, "total": total}

    @staticmethod
    def update_quantity(db: Session, user_id: int, item_id: int, quantity: int):
        quantity = int(quantity)
        cart = CartService.get_or_create_cart(db, user_id)
        item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
        if not item:
            raise ValueError("購物車項目不存在")
        if quantity <= 0:
            db.delete(item)
        else:
            item.quantity = quantity
            CartService._update_item_subtotal(item)
        CartService._update_cart_totals(db, cart)
        db.commit()

    @staticmethod
    def remove_item(db: Session, user_id: int, item_id: int):
        cart = CartService.get_or_create_cart(db, user_id)
        item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
        if not item:
            raise ValueError("購物車項目不存在")
        db.delete(item)
        CartService._update_cart_totals(db, cart)
        db.commit()

    @staticmethod
    def clear_cart(db: Session, user_id: int):
        cart = CartService.get_or_create_cart(db, user_id)
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        cart.total_price = 0
        cart.item_count = 0
        db.commit()
"""

ORDER_SERVICE_PY = """
\"\"\"訂單業務邏輯\"\"\"
from sqlalchemy.orm import Session
from app.models.order import Order, OrderItem
from app.models.cart import Cart, CartItem
from app.models.preorder_set import PreorderSet
from app.core.utils import generate_order_number, get_current_datetime
from datetime import timedelta
import json

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

        cart_items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
        if not cart_items:
            raise ValueError("購物車為空")

        order = Order(
            order_number=generate_order_number(),
            user_id=user_id,
            buyer_name=buyer_name,
            buyer_email=buyer_email,
            buyer_phone=buyer_phone,
            buyer_address=buyer_address,
            total_price=cart.total_price,
            final_price=cart.total_price,
            payment_deadline=get_current_datetime() + timedelta(days=7),
            status="Pending",
            notes=notes
        )
        db.add(order)
        db.flush()

        order_items_data = []
        for cart_item in cart_items:
            preorder_set = db.query(PreorderSet).filter(PreorderSet.id == cart_item.preorder_set_id).first()
            if not preorder_set:
                continue

            order_item = OrderItem(
                order_id=order.id,
                preorder_set_id=cart_item.preorder_set_id,
                set_name=preorder_set.name,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                subtotal=cart_item.subtotal
            )
            db.add(order_item)

            if preorder_set.available_quantity is not None:
                preorder_set.available_quantity = max(0, preorder_set.available_quantity - cart_item.quantity)
            preorder_set.ordered_quantity = (preorder_set.ordered_quantity or 0) + cart_item.quantity

            order_items_data.append({
                "set_id": preorder_set.id,
                "set_name": preorder_set.name,
                "quantity": cart_item.quantity,
                "unit_price": cart_item.unit_price,
                "subtotal": cart_item.subtotal
            })

        order.items = order_items_data
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        cart.total_price = 0
        cart.item_count = 0
        db.commit()
        db.refresh(order)
        return order
"""

COURSE_SERVICE_PY = """
\"\"\"課程業務邏輯\"\"\"
from sqlalchemy.orm import Session
from app.models.course import Course, CourseRegistration
from app.core.utils import get_current_datetime
import uuid

class CourseService:
    @staticmethod
    def get_active_courses(db: Session, page: int = 1, page_size: int = 20, sort: str = "created") -> tuple:
        skip = (page - 1) * page_size
        query = db.query(Course).filter(Course.is_active == True)
        total = query.count()
        if sort == "difficulty":
            query = query.order_by(Course.difficulty.asc(), Course.created_at.desc())
        else:
            query = query.order_by(Course.created_at.desc())
        return query.offset(skip).limit(page_size).all(), total

    @staticmethod
    def register_course(db: Session, user_id: int | None, course_id: int, name: str, email: str, phone: str, notes: str | None = None) -> CourseRegistration:
        course = db.query(Course).filter(Course.id == course_id, Course.is_active == True).first()
        if not course:
            raise ValueError("課程不存在")
        if course.max_students and course.current_students >= course.max_students:
            raise ValueError("課程已滿員")
        now = get_current_datetime()
        if course.registration_deadline and now > course.registration_deadline:
            raise ValueError("報名已截止")
        if user_id:
            existing = db.query(CourseRegistration).filter(
                CourseRegistration.course_id == course_id,
                CourseRegistration.user_id == user_id
            ).first()
            if existing:
                raise ValueError("已報名此課程")

        registration = CourseRegistration(
            course_id=course_id,
            user_id=user_id,
            registration_number=f"CRS-{uuid.uuid4().hex[:8].upper()}",
            name=name,
            email=email,
            phone=phone,
            notes=notes
        )
        course.current_students = (course.current_students or 0) + 1
        db.add(registration)
        db.commit()
        db.refresh(registration)
        return registration
"""

CONTEST_SERVICE_PY = """
\"\"\"比賽業務邏輯\"\"\"
from sqlalchemy.orm import Session
from app.models.contest import Contest, ContestRegistration
from app.core.utils import get_current_datetime
import uuid

class ContestService:
    @staticmethod
    def get_active_contests(db: Session) -> list:
        now = get_current_datetime()
        return db.query(Contest).filter(
            Contest.is_active == True,
            Contest.event_date >= now
        ).order_by(Contest.event_date.asc()).all()

    @staticmethod
    def register_contest(db: Session, user_id: int | None, contest_id: int, name: str, email: str, phone: str, dj_name: str | None = None, notes: str | None = None) -> ContestRegistration:
        contest = db.query(Contest).filter(Contest.id == contest_id, Contest.is_active == True).first()
        if not contest:
            raise ValueError("比賽不存在")
        if contest.max_participants and contest.current_participants >= contest.max_participants:
            raise ValueError("比賽已滿員")
        now = get_current_datetime()
        if contest.registration_deadline and now > contest.registration_deadline:
            raise ValueError("報名已截止")
        if contest.event_date and now > contest.event_date:
            raise ValueError("比賽已結束")
        if user_id:
            existing = db.query(ContestRegistration).filter(
                ContestRegistration.contest_id == contest_id,
                ContestRegistration.user_id == user_id
            ).first()
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
            notes=notes
        )
        contest.current_participants = (contest.current_participants or 0) + 1
        db.add(registration)
        db.commit()
        db.refresh(registration)
        return registration
"""

CONTACT_SERVICE_PY = """
\"\"\"聯絡消息業務邏輯\"\"\"
from sqlalchemy.orm import Session
from app.models.contact import ContactMessage

class ContactService:
    @staticmethod
    def create_contact_message(db: Session, name: str, email: str, phone: str, message_type: str, subject: str, message: str) -> ContactMessage:
        contact = ContactMessage(
            name=name,
            email=email,
            phone=phone,
            message_type=message_type,
            subject=subject,
            message=message,
            status="New"
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
        return contact

    @staticmethod
    def submit_message(db: Session, name: str, email: str, phone: str, message_type: str, message: str, user_id: int | None = None, subject: str | None = None) -> ContactMessage:
        subject = subject or ("廠商贊助查詢" if message_type == "sponsor_inquiry" else "個人意見回饋")
        return ContactService.create_contact_message(db, name, email, phone, message_type, subject, message)
"""

AUTH_ROUTER_PY = """
\"\"\"會員登入 / 註冊路由\"\"\"
from fastapi import APIRouter, Depends, Form, Request, Response, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.services.auth_service import AuthService
from app.schemas.auth import UserRegister

router = APIRouter(tags=["Authentication"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent.parent / "templates"))

@router.get("/login", response_class=HTMLResponse)
@router.get("/auth/login", response_class=HTMLResponse)
async def login_page(request: Request, next: str = "/", user=Depends(get_optional_current_user)):
    if user:
        return RedirectResponse(url=next or "/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "next": next, "user": user})

@router.post("/login")
@router.post("/auth/login")
async def login_submit(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    next: str = Form("/"),
    db: Session = Depends(get_db)
):
    try:
        user = AuthService.authenticate_user(db, username, password)
        token = AuthService.create_user_token(user)
        redirect = RedirectResponse(url=next or "/", status_code=303)
        redirect.set_cookie(
            key="session_id",
            value=token,
            httponly=True,
            max_age=86400 * 7,
            samesite="lax",
            path="/"
        )
        return redirect
    except ValueError as exc:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": str(exc), "next": next, "user": None},
            status_code=400
        )

@router.get("/register", response_class=HTMLResponse)
@router.get("/auth/register", response_class=HTMLResponse)
async def register_page(request: Request, user=Depends(get_optional_current_user)):
    if user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("register.html", {"request": request, "user": user})

@router.post("/register")
@router.post("/auth/register")
async def register_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(""),
    full_name: str = Form(None),
    phone: str = Form(None),
    address: str = Form(None),
    db: Session = Depends(get_db)
):
    try:
        if password_confirm and password != password_confirm:
            raise ValueError("兩次輸入的密碼不一致")
        user_data = UserRegister(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            phone=phone
        )
        user = AuthService.register_user(db, user_data, address=address)
        token = AuthService.create_user_token(user)
        redirect = RedirectResponse(url="/", status_code=303)
        redirect.set_cookie(
            key="session_id",
            value=token,
            httponly=True,
            max_age=86400 * 7,
            samesite="lax",
            path="/"
        )
        return redirect
    except Exception as exc:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": str(exc), "user": None},
            status_code=400
        )

@router.get("/logout")
@router.get("/auth/logout")
async def logout():
    redirect = RedirectResponse(url="/", status_code=303)
    redirect.delete_cookie("session_id", path="/")
    return redirect

@router.post("/api/login")
async def api_login(payload: dict, response: Response, db: Session = Depends(get_db)):
    try:
        user = AuthService.authenticate_user(db, payload.get("username", ""), payload.get("password", ""))
        token = AuthService.create_user_token(user)
        response.set_cookie("session_id", token, httponly=True, max_age=86400 * 7, samesite="lax", path="/")
        return {"access_token": token, "token_type": "bearer", "user": {"id": user.id, "username": user.username, "is_admin": user.is_admin}}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
"""

HOME_ROUTER_PY = """
\"\"\"首頁路由\"\"\"
from pathlib import Path
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.services.product_service import ProductService
from app.models.ddj import DDJ
from app.models.audio import Audio
from app.models.wire import Wire
from app.models.music import Music

router = APIRouter(tags=["Home"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent.parent / "templates"))

@router.get("/", response_class=HTMLResponse)
async def get_home(request: Request, db: Session = Depends(get_db), user=Depends(get_optional_current_user)):
    preorder_sets = ProductService.get_featured_preorder_sets(db, limit=3)
    latest_products = []
    for model, instrument in [(DDJ, "ddj"), (Audio, "audio"), (Wire, "wire"), (Music, "music")]:
        rows = db.query(model).order_by(model.id.asc()).limit(2).all()
        latest_products.extend([(row, instrument) for row in rows])
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "user": user,
            "preorder_sets": preorder_sets,
            "latest_products": latest_products,
        }
    )
"""

CATEGORY_ROUTER_PY = """
\"\"\"分類頁路由\"\"\"
from pathlib import Path
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.models.ddj import DDJ
from app.models.audio import Audio
from app.models.wire import Wire
from app.models.music import Music

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent.parent / "templates"))

MODEL_MAP = {"dj": DDJ, "ddj": DDJ, "audio": Audio, "wire": Wire, "music": Music}

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
    user=Depends(get_optional_current_user),
):
    instrument = (instrument or "ddj").lower()
    model = MODEL_MAP.get(instrument, DDJ)
    query = db.query(model)

    if brand and hasattr(model, "brand"):
        query = query.filter(model.brand.ilike(f"%{brand}%"))
    if hasattr(model, "price"):
        query = query.filter(model.price >= price_min, model.price <= price_max)

    total = query.count()
    products = query.order_by(model.id.asc()).offset((page - 1) * 12).limit(12).all()
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
"""

SEARCH_ROUTER_PY = """
\"\"\"搜尋路由\"\"\"
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
"""

DETAIL_ROUTER_PY = """
\"\"\"詳情頁路由\"\"\"
from pathlib import Path
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.models.preorder_set import PreorderSet
from app.services.product_service import ProductService

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent.parent / "templates"))

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def detail_page(
    request: Request,
    instrument: str = "ddj",
    id: int = 1,
    db: Session = Depends(get_db),
    user=Depends(get_optional_current_user),
):
    product = ProductService.get_product(db, instrument, id)
    if not product:
        return templates.TemplateResponse("404.html", {"request": request, "user": user}, status_code=404)

    preorder_sets = db.query(PreorderSet).filter(PreorderSet.is_active == True).order_by(PreorderSet.sort_order.asc(), PreorderSet.id.asc()).all()
    return templates.TemplateResponse("detail.html", {
        "request": request,
        "user": user,
        "instrument": instrument,
        "product": product,
        "preorder_sets": preorder_sets,
    })
"""

CART_ROUTER_PY = """
\"\"\"購物車路由\"\"\"
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
"""

CHECKOUT_ROUTER_PY = """
\"\"\"結帳路由\"\"\"
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
        return RedirectResponse(url=f"/order-success?order_id={order.id}", status_code=303)
    except ValueError as exc:
        cart_view = CartService.get_cart_view(db, user.id)
        return templates.TemplateResponse(
            "checkout.html",
            {"request": request, "user": user, "error": str(exc), **cart_view},
            status_code=400
        )
"""

COURSE_ROUTER_PY = """
\"\"\"課程路由\"\"\"
from pathlib import Path
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.models.course import Course
from app.services.course_service import CourseService

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent.parent / "templates"))

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def course_list(
    request: Request,
    page: int = 1,
    sort: str = "created",
    db: Session = Depends(get_db),
    user=Depends(get_optional_current_user),
):
    courses, total = CourseService.get_active_courses(db, page=page, page_size=12, sort=sort)
    return templates.TemplateResponse("course_list.html", {
        "request": request,
        "user": user,
        "courses": courses,
        "page": page,
        "sort": sort,
        "total_pages": (total + 11) // 12,
    })

@router.get("/detail", response_class=HTMLResponse)
async def course_detail(
    request: Request,
    id: int,
    registered: str = "",
    db: Session = Depends(get_db),
    user=Depends(get_optional_current_user),
):
    course = db.query(Course).filter(Course.id == id).first()
    if not course:
        return templates.TemplateResponse("404.html", {"request": request, "user": user}, status_code=404)
    courses = db.query(Course).filter(Course.is_active == True).order_by(Course.created_at.desc()).all()
    return templates.TemplateResponse("course_detail.html", {
        "request": request,
        "user": user,
        "course": course,
        "courses": courses,
        "registered": registered,
    })

@router.post("/register")
async def register_course(
    request: Request,
    course_id: int = Form(...),
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    notes: str = Form(None),
    db: Session = Depends(get_db),
    user=Depends(get_optional_current_user),
):
    try:
        registration = CourseService.register_course(
            db,
            user.id if user else None,
            course_id,
            name,
            email,
            phone,
            notes
        )
        return RedirectResponse(url=f"/course/detail?id={course_id}&registered={registration.registration_number}#form", status_code=303)
    except ValueError as exc:
        return RedirectResponse(url=f"/course/detail?id={course_id}&error={str(exc)}#form", status_code=303)
"""

CONTEST_ROUTER_PY = """
\"\"\"比賽路由\"\"\"
from pathlib import Path
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.core.utils import get_current_datetime
from app.models.contest import Contest
from app.services.contest_service import ContestService

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent.parent / "templates"))

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def contest_list(
    request: Request,
    page: int = 1,
    db: Session = Depends(get_db),
    user=Depends(get_optional_current_user),
):
    contests = ContestService.get_active_contests(db)
    total = len(contests)
    contests = contests[(page - 1) * 12: page * 12]
    return templates.TemplateResponse("contest_list.html", {
        "request": request,
        "user": user,
        "contests": contests,
        "now": get_current_datetime(),
        "page": page,
        "total_pages": (total + 11) // 12,
    })

@router.get("/detail", response_class=HTMLResponse)
async def contest_detail(
    request: Request,
    id: int,
    registered: str = "",
    db: Session = Depends(get_db),
    user=Depends(get_optional_current_user),
):
    contest = db.query(Contest).filter(Contest.id == id).first()
    if not contest:
        return templates.TemplateResponse("404.html", {"request": request, "user": user}, status_code=404)
    now = get_current_datetime()
    is_registration_closed = bool(contest.registration_deadline and contest.registration_deadline < now)
    contests = db.query(Contest).filter(Contest.is_active == True).order_by(Contest.event_date.asc()).all()
    return templates.TemplateResponse("contest_detail.html", {
        "request": request,
        "user": user,
        "contest": contest,
        "contests": contests,
        "now": now,
        "registered": registered,
        "is_registration_closed": is_registration_closed,
    })

@router.post("/register")
async def register_contest(
    request: Request,
    contest_id: int = Form(...),
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    dj_name: str = Form(None),
    notes: str = Form(None),
    db: Session = Depends(get_db),
    user=Depends(get_optional_current_user),
):
    try:
        registration = ContestService.register_contest(
            db,
            user.id if user else None,
            contest_id,
            name,
            email,
            phone,
            dj_name,
            notes
        )
        return RedirectResponse(url=f"/contest/detail?id={contest_id}&registered={registration.registration_number}#form", status_code=303)
    except ValueError as exc:
        return RedirectResponse(url=f"/contest/detail?id={contest_id}&error={str(exc)}#form", status_code=303)
"""

CONTACT_ROUTER_PY = """
\"\"\"聯絡我們路由\"\"\"
from pathlib import Path
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.services.contact_service import ContactService

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent.parent / "templates"))

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def contact_page(request: Request, success: str = "", user=Depends(get_optional_current_user)):
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
async def submit_contact(
    name: str = Form(...),
    person_type: str = Form("個人"),
    email: str = Form(...),
    phone: str = Form(...),
    message_type: str = Form("personal_feedback"),
    subject: str = Form(None),
    message: str = Form(...),
    db: Session = Depends(get_db),
    user=Depends(get_optional_current_user),
):
    ContactService.submit_message(
        db,
        name=name,
        email=email,
        phone=phone,
        message_type=message_type,
        message=f"身份：{person_type}\\n{message}",
        user_id=user.id if user else None,
        subject=subject
    )
    return RedirectResponse(url="/contact?success=true", status_code=303)
"""

ADMIN_ROUTER_PY = """
\"\"\"管理後台路由\"\"\"
from pathlib import Path
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.models.ddj import DDJ
from app.models.audio import Audio
from app.models.wire import Wire
from app.models.music import Music
from app.models.order import Order
from app.models.course import Course, CourseRegistration
from app.models.contest import Contest, ContestRegistration

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent.parent / "templates"))

PRODUCT_MODELS = {"ddj": DDJ, "audio": Audio, "wire": Wire, "music": Music}

def _product_fields(model, form):
    data = {
        "price": float(form.get("price") or 0),
        "description": form.get("description") or "",
        "in_stock": int(form.get("stock") or form.get("in_stock") or 0),
        "preorder_available": int(form.get("preorder_available") or 0),
        "image_url": form.get("image_url") or None,
    }
    if model is Music:
        data["title"] = form.get("name") or form.get("title") or ""
        data["artist"] = form.get("artist") or "Unknown"
        data["genre"] = form.get("genre") or form.get("brand") or "Other"
    else:
        data["name"] = form.get("name") or ""
        if hasattr(model, "brand"):
            data["brand"] = form.get("brand") or "Other"
    if model is DDJ:
        data["model"] = form.get("model") or data["name"]
        data["channels"] = int(form.get("channels") or 2)
        data["effects_count"] = int(form.get("effects_count") or 8)
    if model is Audio:
        data["audio_type"] = form.get("audio_type") or "Speaker"
        data["watts"] = int(form.get("watts") or 0)
    if model is Wire:
        data["wire_type"] = form.get("wire_type") or "Cable"
        data["length_meters"] = float(form.get("length_meters") or 1)
    return data

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    stats = {
        "products": sum(db.query(model).count() for model in PRODUCT_MODELS.values()),
        "orders": db.query(Order).count(),
        "courses": db.query(Course).count(),
        "contests": db.query(Contest).count(),
    }
    return templates.TemplateResponse("admin.html", {"request": request, "user": current_user, "stats": stats})

@router.get("/products", response_class=HTMLResponse)
async def admin_products(request: Request, instrument: str = "ddj", current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    model = PRODUCT_MODELS.get(instrument, DDJ)
    products = db.query(model).order_by(model.id.desc()).all()
    return templates.TemplateResponse("admin_products.html", {
        "request": request,
        "user": current_user,
        "instrument": instrument,
        "products": products,
    })

@router.post("/products/create")
async def admin_product_create(request: Request, instrument: str = Form("ddj"), current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    form = await request.form()
    model = PRODUCT_MODELS.get(instrument, DDJ)
    obj = model(**_product_fields(model, form))
    db.add(obj)
    db.commit()
    return RedirectResponse(url=f"/admin/products?instrument={instrument}", status_code=303)

@router.post("/products/{instrument}/{product_id}/edit")
async def admin_product_edit(request: Request, instrument: str, product_id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    form = await request.form()
    model = PRODUCT_MODELS.get(instrument)
    if not model:
        raise HTTPException(404)
    obj = db.query(model).filter(model.id == product_id).first()
    if not obj:
        raise HTTPException(404)
    for key, value in _product_fields(model, form).items():
        if hasattr(obj, key):
            setattr(obj, key, value)
    db.commit()
    return RedirectResponse(url=f"/admin/products?instrument={instrument}", status_code=303)

@router.post("/products/{instrument}/{product_id}/delete")
async def admin_product_delete(instrument: str, product_id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    model = PRODUCT_MODELS.get(instrument)
    if not model:
        raise HTTPException(404)
    obj = db.query(model).filter(model.id == product_id).first()
    if obj:
        db.delete(obj)
        db.commit()
    return RedirectResponse(url=f"/admin/products?instrument={instrument}", status_code=303)

@router.get("/orders", response_class=HTMLResponse)
async def admin_orders(request: Request, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    orders = db.query(Order).order_by(Order.created_at.desc()).all()
    return templates.TemplateResponse("admin_orders.html", {"request": request, "user": current_user, "orders": orders})

@router.get("/orders/{order_id}")
async def admin_order_detail(order_id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404)
    return {
        "id": order.id,
        "order_number": order.order_number,
        "buyer_name": order.buyer_name,
        "buyer_email": order.buyer_email,
        "buyer_phone": order.buyer_phone,
        "final_price": order.final_price,
        "status": order.status,
        "items": order.items,
    }

@router.post("/orders/{order_id}/status")
async def admin_order_status(order_id: int, status: str = Form(...), current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.status = status
        db.commit()
    return RedirectResponse(url="/admin/orders", status_code=303)

@router.get("/courses", response_class=HTMLResponse)
async def admin_courses(request: Request, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    courses = db.query(Course).order_by(Course.created_at.desc()).all()
    return templates.TemplateResponse("admin_courses.html", {"request": request, "user": current_user, "courses": courses})

@router.get("/courses/{course_id}/registrations")
async def admin_course_registrations(course_id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    regs = db.query(CourseRegistration).filter(CourseRegistration.course_id == course_id).order_by(CourseRegistration.registered_at.desc()).all()
    return [{"name": r.name, "phone": r.phone, "email": r.email, "registration_number": r.registration_number} for r in regs]

@router.get("/contests", response_class=HTMLResponse)
async def admin_contests(request: Request, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    contests = db.query(Contest).order_by(Contest.event_date.desc()).all()
    return templates.TemplateResponse("admin_contests.html", {"request": request, "user": current_user, "contests": contests})

@router.get("/contests/{contest_id}/registrations")
async def admin_contest_registrations(contest_id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    regs = db.query(ContestRegistration).filter(ContestRegistration.contest_id == contest_id).order_by(ContestRegistration.registered_at.desc()).all()
    return [{"name": r.name, "phone": r.phone, "email": r.email, "dj_name": r.dj_name, "registration_number": r.registration_number} for r in regs]
"""

ORDERS_ROUTER_PY = """
\"\"\"訂單成功頁\"\"\"
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
"""

HEAD_META_HTML = """
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
<link rel="stylesheet" href="/static/css/pages/course-contest.css" />
<link rel="stylesheet" href="/static/css/pages/contact.css" />
<link rel="stylesheet" href="/static/css/pages/auth.css" />
<link rel="stylesheet" href="/static/css/pages/admin.css" />
"""

NAVBAR_HTML = """
<nav class="navbar">
    <div class="navbar-container container">
        <div class="navbar-brand">
            <a href="/" class="navbar-logo">🎛️ DJ 器材平台</a>
        </div>

        <button class="navbar-toggle" id="navbar-toggle" aria-label="切換導覽菜單">
            <span></span><span></span><span></span>
        </button>

        <ul class="navbar-menu" id="navbar-menu">
            <li><a href="/">首頁</a></li>
            <li><a href="/category?instrument=ddj">器材介紹</a></li>
            <li><a href="/search">商品搜尋</a></li>
            <li><a href="/course">課程報名</a></li>
            <li><a href="/contest">比賽資訊</a></li>
            <li><a href="/contact">聯絡我們</a></li>
            <li><a href="/cart" class="navbar-icon" aria-label="購物車">🛒 購物車</a></li>
            {% if user %}
                <li><span class="navbar-user">👤 {{ user.username }}</span></li>
                {% if user.is_admin %}
                <li><a href="/admin" class="navbar-admin">⚙️ 管理後台</a></li>
                {% endif %}
                <li><a href="/logout">登出</a></li>
            {% else %}
                <li><a href="/login" class="navbar-login">🔐 登入</a></li>
            {% endif %}
        </ul>
    </div>
</nav>
"""

LOGIN_HTML = """
{% extends "base.html" %}
{% block title %}會員登入 - DJ 器材預購與入門學習平台{% endblock %}
{% block content %}
<section class="auth-section">
    <div class="auth-container">
        <div class="auth-card">
            <h1>會員登入</h1>
            <p class="auth-subtitle">輸入帳號和密碼</p>

            {% if error %}
            <div class="alert alert-error">{{ error }}</div>
            {% endif %}

            <form method="POST" action="/login" class="auth-form">
                <input type="hidden" name="next" value="{{ next or '/' }}" />
                <div class="form-group">
                    <label for="username">帳號</label>
                    <input type="text" id="username" name="username" required autofocus minlength="3" />
                </div>
                <div class="form-group">
                    <label for="password">密碼</label>
                    <input type="password" id="password" name="password" required minlength="8" />
                </div>
                <button type="submit" class="btn btn-primary btn-block">登入</button>
            </form>

            <div class="auth-links">
                <p>沒有會員？<a href="/register">前往註冊</a></p>
            </div>
        </div>
    </div>
</section>
{% endblock %}
{% block scripts %}
<script src="/static/js/auth.js"></script>
{% endblock %}
"""

REGISTER_HTML = """
{% extends "base.html" %}
{% block title %}建立帳號 - DJ 器材預購與入門學習平台{% endblock %}
{% block content %}
<section class="auth-section">
    <div class="auth-container">
        <div class="auth-card auth-card-large">
            <h1>建立新帳號</h1>

            {% if error %}
            <div class="alert alert-error">{{ error }}</div>
            {% endif %}

            <form method="POST" action="/register" class="auth-form">
                <div class="form-group">
                    <label for="username">帳號 *</label>
                    <input type="text" id="username" name="username" required minlength="3" maxlength="50" />
                </div>
                <div class="form-group">
                    <label for="email">電子郵件 *</label>
                    <input type="email" id="email" name="email" required />
                </div>
                <div class="form-group">
                    <label for="password">密碼 *</label>
                    <input type="password" id="password" name="password" required minlength="8" />
                    <small>至少 8 個字元</small>
                </div>
                <div class="form-group">
                    <label for="password_confirm">確認密碼 *</label>
                    <input type="password" id="password_confirm" name="password_confirm" required minlength="8" />
                </div>
                <div class="form-group">
                    <label for="full_name">姓名</label>
                    <input type="text" id="full_name" name="full_name" />
                </div>
                <div class="form-group">
                    <label for="phone">電話</label>
                    <input type="tel" id="phone" name="phone" />
                </div>
                <div class="form-group">
                    <label for="address">地址</label>
                    <textarea id="address" name="address"></textarea>
                </div>
                <button type="submit" class="btn btn-primary btn-block">建立帳號</button>
            </form>

            <div class="auth-links">
                <p>已有會員？<a href="/login">前往登入</a></p>
            </div>
        </div>
    </div>
</section>
{% endblock %}
{% block scripts %}
<script src="/static/js/auth.js"></script>
{% endblock %}
"""

CART_HTML = """
{% extends "base.html" %}
{% block title %}購物車 - DJ 器材預購與入門學習平台{% endblock %}
{% block content %}
<section class="cart-section">
    <div class="container">
        <h1 class="section-title">購物車</h1>

        {% if items %}
        <div class="cart-content">
            <div class="cart-items">
                <table class="cart-table">
                    <thead>
                        <tr>
                            <th>SET 名稱</th>
                            <th>內容</th>
                            <th>數量</th>
                            <th>單價</th>
                            <th>小計</th>
                            <th>動作</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for item in items %}
                        <tr>
                            <td>{{ item.name }}</td>
                            <td>
                                {% if item.included_items %}
                                    {% for set_item in item.included_items %}
                                    <div>• {{ set_item.category|default('器材') }} x {{ set_item.quantity|default(1) }}</div>
                                    {% endfor %}
                                {% else %}
                                    {{ item.description or '預購套組' }}
                                {% endif %}
                            </td>
                            <td>
                                <form method="POST" action="/cart/update/{{ item.id }}" class="inline-form cart-qty-form">
                                    <input type="number" name="quantity" class="qty-input" value="{{ item.quantity }}" min="1" max="99" />
                                    <button type="submit" class="btn btn-sm btn-secondary">更新</button>
                                </form>
                            </td>
                            <td>NT${{ "%.0f"|format(item.unit_price) }}</td>
                            <td>NT${{ "%.0f"|format(item.subtotal) }}</td>
                            <td>
                                <form method="POST" action="/cart/remove/{{ item.id }}" class="inline-form">
                                    <button type="submit" class="btn btn-danger btn-sm">移除</button>
                                </form>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>

            <aside class="cart-summary">
                <h3>訂單摘要</h3>
                <div class="summary-item"><span>小計：</span><span>NT${{ "%.0f"|format(total) }}</span></div>
                <div class="summary-item"><span>運費：</span><span>NT$0</span></div>
                <div class="summary-total"><span>總計：</span><span>NT${{ "%.0f"|format(total) }}</span></div>
                <div class="cart-actions">
                    <a href="/category?instrument=ddj" class="btn btn-secondary">繼續購物</a>
                    <a href="/checkout" class="btn btn-primary">前往結帳</a>
                </div>
            </aside>
        </div>

        <section class="cart-notes">
            <h3>購物須知</h3>
            <ul>
                <li>✓ 本平台提供 DJ 器材預購服務。</li>
                <li>✓ 可修改商品數量或從購物車移除商品。</li>
                <li>✓ 付款方式：線下銀行轉帳。</li>
                <li>✓ 確認付款後 3-5 工作天出貨。</li>
                <li>✓ 若商品庫存不足，平台將主動聯繫調整訂單。</li>
            </ul>
        </section>
        {% else %}
        <div class="empty-cart">
            <p>您的購物車是空的</p>
            <a href="/category?instrument=ddj" class="btn btn-primary">前往分類選購</a>
        </div>
        {% endif %}
    </div>
</section>
{% endblock %}
{% block scripts %}
<script src="/static/js/cart.js"></script>
{% endblock %}
"""

CHECKOUT_HTML = """
{% extends "base.html" %}
{% block title %}結帳 - DJ 器材預購與入門學習平台{% endblock %}
{% block content %}
<section class="checkout-section">
    <div class="container">
        <h1 class="section-title">完成購買</h1>

        <div class="checkout-layout">
            <aside class="checkout-summary">
                <div class="checkout-summary-scroll">
                    <h3>訂單摘要</h3>
                    <div class="summary-items">
                        {% for item in items %}
                        <div class="summary-item">
                            <div class="item-name">{{ item.name }}</div>
                            <div class="item-qty">數量：{{ item.quantity }}</div>
                            <div class="item-price">NT${{ "%.0f"|format(item.subtotal) }}</div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                <div class="summary-total checkout-total-block">
                    <span>總計：</span>
                    <span class="total-amount">NT${{ "%.0f"|format(total) }}</span>
                </div>
            </aside>

            <main class="checkout-form">
                <h3>購買人資料</h3>

                {% if error %}
                <div class="alert alert-error">{{ error }}</div>
                {% endif %}

                <form method="POST" action="/checkout" class="form-large">
                    <div class="form-group">
                        <label for="buyer_name">姓名 *</label>
                        <input type="text" id="buyer_name" name="buyer_name" value="{{ user.full_name or '' }}" required />
                    </div>
                    <div class="form-group">
                        <label for="buyer_phone">電話 *</label>
                        <input type="tel" id="buyer_phone" name="buyer_phone" value="{{ user.phone or '' }}" required />
                    </div>
                    <div class="form-group">
                        <label for="buyer_email">電子郵件 *</label>
                        <input type="email" id="buyer_email" name="buyer_email" value="{{ user.email or '' }}" required />
                    </div>
                    <div class="form-group">
                        <label for="buyer_address">地址 *</label>
                        <textarea id="buyer_address" name="buyer_address" required>{{ user.address or '' }}</textarea>
                    </div>
                    <div class="form-group">
                        <label for="notes">備註</label>
                        <textarea id="notes" name="notes" rows="3"></textarea>
                    </div>
                    <div class="checkout-actions">
                        <a href="/cart" class="btn btn-secondary">返回購物車</a>
                        <button type="submit" class="btn btn-primary">送出訂單</button>
                    </div>
                </form>
            </main>
        </div>
    </div>
</section>
{% endblock %}
{% block scripts %}
<script src="/static/js/checkout.js"></script>
{% endblock %}
"""

COURSE_LIST_HTML = """
{% extends "base.html" %}
{% block title %}課程報名 - DJ 器材預購與入門學習平台{% endblock %}
{% block content %}
<section class="course-section">
    <div class="container">
        <h1 class="section-title">DJ 入門課程</h1>
        <p class="section-subtitle">依上架時間與難度排列，選擇適合你的課程。</p>

        <form method="GET" action="/course" class="filter-form">
            <label>排列方式</label>
            <select name="sort">
                <option value="created" {% if sort == 'created' %}selected{% endif %}>依課程上架時間</option>
                <option value="difficulty" {% if sort == 'difficulty' %}selected{% endif %}>依難度分級</option>
            </select>
            <button type="submit" class="btn btn-secondary">套用排序</button>
        </form>

        {% if courses %}
        <div class="courses-grid">
            {% for course in courses %}
            <div class="course-card">
                <div class="course-header">
                    <h3>{{ course.title }}</h3>
                    <span class="difficulty-badge">{{ course.difficulty }}</span>
                </div>
                <div class="course-info">
                    <p><strong>講師：</strong>{{ course.instructor }}</p>
                    <p><strong>時數：</strong>{{ course.duration_hours }} 小時</p>
                    <p><strong>費用：</strong>NT${{ "%.0f"|format(course.price) }}</p>
                </div>
                <p class="course-description">{{ (course.description or '')[:80] }}...</p>
                <div class="course-actions">
                    <a href="/course/detail?id={{ course.id }}" class="btn btn-secondary">查看詳情</a>
                    <a href="/course/detail?id={{ course.id }}#form" class="btn btn-primary">立即報名</a>
                </div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <p class="no-courses">目前沒有可報名的課程</p>
        {% endif %}
    </div>
</section>
{% endblock %}
{% block scripts %}
<script src="/static/js/course.js"></script>
{% endblock %}
"""

COURSE_DETAIL_HTML = """
{% extends "base.html" %}
{% block title %}{{ course.title }} - 課程詳情{% endblock %}
{% block content %}
<section class="course-detail-section">
    <div class="container">
        <a href="/course" class="btn btn-secondary">← 返回課程列表</a>

        {% if registered %}
        <div class="alert alert-success">✅ 報名成功！報名編號：{{ registered }}</div>
        {% endif %}

        <div class="detail-card">
            <h1>{{ course.title }}</h1>
            <p>{{ course.description }}</p>
            <div class="detail-grid">
                <p><strong>時數：</strong>{{ course.duration_hours }} 小時</p>
                <p><strong>推薦適用對象：</strong>{{ course.prerequisites or '初學者與對 DJ 有興趣者' }}</p>
                <p><strong>教授者：</strong>{{ course.instructor }}</p>
                <p><strong>費用：</strong>NT${{ "%.0f"|format(course.price) }}</p>
                <p><strong>難度：</strong>{{ course.difficulty }}</p>
                <p><strong>報名截止：</strong>{% if course.registration_deadline %}{{ course.registration_deadline.strftime('%Y-%m-%d') }}{% else %}未設定{% endif %}</p>
            </div>
            <h3>課程大綱</h3>
            <p>{{ course.syllabus or '課程大綱尚未填寫。' }}</p>
        </div>

        <section id="form" class="course-registration">
            <h2 class="section-title">課程報名表單</h2>
            <form method="POST" action="/course/register" class="registration-form">
                <input type="hidden" name="course_id" value="{{ course.id }}" />

                <div class="form-group">
                    <label for="name">姓名 *</label>
                    <input type="text" id="name" name="name" value="{{ user.full_name if user else '' }}" required />
                </div>
                <div class="form-group">
                    <label for="email">郵件 *</label>
                    <input type="email" id="email" name="email" value="{{ user.email if user else '' }}" required />
                </div>
                <div class="form-group">
                    <label for="phone">電話 *</label>
                    <input type="tel" id="phone" name="phone" value="{{ user.phone if user else '' }}" required />
                </div>
                <div class="form-group">
                    <label for="course_select">選擇課程</label>
                    <select id="course_select" name="course_id">
                        {% for c in courses %}
                        <option value="{{ c.id }}" {% if c.id == course.id %}selected{% endif %}>{{ c.title }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="form-group">
                    <label for="notes">備註</label>
                    <textarea id="notes" name="notes" rows="4"></textarea>
                </div>
                <button type="submit" class="btn btn-primary btn-large">確認報名</button>
            </form>
        </section>
    </div>
</section>
{% endblock %}
{% block scripts %}
<script src="/static/js/course.js"></script>
{% endblock %}
"""

CONTEST_LIST_HTML = """
{% extends "base.html" %}
{% block title %}比賽資訊 - DJ 器材預購與入門學習平台{% endblock %}
{% block content %}
<section class="contest-section">
    <div class="container">
        <h1 class="section-title">DJ 比賽資訊</h1>
        <p class="section-subtitle">依比賽時間近至遠排列。</p>

        {% if contests %}
        <div class="contests-grid">
            {% for contest in contests %}
            <div class="contest-card">
                <div class="contest-header">
                    <h3>{{ contest.title }}</h3>
                    <span class="contest-date">📅 {{ contest.event_date.strftime('%Y-%m-%d') }}</span>
                </div>
                <div class="contest-info">
                    <p><strong>地點：</strong>{{ contest.venue }}</p>
                    <p><strong>報名截止：</strong>{{ contest.registration_deadline.strftime('%Y-%m-%d') }}</p>
                    {% if contest.prize_pool %}
                    <p><strong>獎金：</strong>NT${{ "%.0f"|format(contest.prize_pool) }}</p>
                    {% endif %}
                </div>
                <p class="contest-description">{{ (contest.description or '')[:80] }}...</p>
                <div class="contest-actions">
                    <a href="/contest/detail?id={{ contest.id }}" class="btn btn-secondary">查看詳情</a>
                    {% if contest.registration_deadline > now %}
                    <a href="/contest/detail?id={{ contest.id }}#form" class="btn btn-primary">立即報名</a>
                    {% else %}
                    <button class="btn btn-disabled" disabled>報名已截止</button>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <p class="no-contests">目前沒有進行中的比賽</p>
        {% endif %}
    </div>
</section>
{% endblock %}
{% block scripts %}
<script src="/static/js/contest.js"></script>
{% endblock %}
"""

CONTEST_DETAIL_HTML = """
{% extends "base.html" %}
{% block title %}{{ contest.title }} - 比賽詳情{% endblock %}
{% block content %}
<section class="contest-detail-section">
    <div class="container">
        <a href="/contest" class="btn btn-secondary">← 返回比賽列表</a>

        {% if registered %}
        <div class="alert alert-success">✅ 報名成功！報名編號：{{ registered }}</div>
        {% endif %}

        <div class="detail-card" data-deadline="{{ contest.registration_deadline.isoformat() }}">
            <h1>{{ contest.title }}</h1>
            <p>{{ contest.description }}</p>
            <div class="detail-grid">
                <p><strong>報名時間：</strong>{{ contest.registration_start.strftime('%Y-%m-%d') }} ～ {{ contest.registration_deadline.strftime('%Y-%m-%d') }}</p>
                <p><strong>比賽日期：</strong>{{ contest.event_date.strftime('%Y-%m-%d') }}</p>
                <p><strong>地點：</strong>{{ contest.venue }}</p>
                <p><strong>報名費：</strong>NT${{ "%.0f"|format(contest.entry_fee or 0) }}</p>
            </div>

            <h3>賽事簡介</h3>
            <p>{{ contest.description or '尚未填寫。' }}</p>

            <h3>比賽相關注意事項</h3>
            <p>{{ contest.rules or contest.judging_criteria or '請依現場與主辦單位公告為準。' }}</p>
        </div>

        {% if not is_registration_closed %}
        <section id="form" class="contest-registration">
            <h2 class="section-title">比賽報名表單</h2>
            <form method="POST" action="/contest/register" class="registration-form">
                <input type="hidden" name="contest_id" value="{{ contest.id }}" />

                <div class="form-group">
                    <label for="name">姓名 *</label>
                    <input type="text" id="name" name="name" value="{{ user.full_name if user else '' }}" required />
                </div>
                <div class="form-group">
                    <label for="email">郵件 *</label>
                    <input type="email" id="email" name="email" value="{{ user.email if user else '' }}" required />
                </div>
                <div class="form-group">
                    <label for="phone">電話 *</label>
                    <input type="tel" id="phone" name="phone" value="{{ user.phone if user else '' }}" required />
                </div>
                <div class="form-group">
                    <label for="contest_select">選擇賽事</label>
                    <select id="contest_select" name="contest_id">
                        {% for c in contests %}
                        <option value="{{ c.id }}" {% if c.id == contest.id %}selected{% endif %}>{{ c.title }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="form-group">
                    <label for="dj_name">DJ 名稱</label>
                    <input type="text" id="dj_name" name="dj_name" />
                </div>
                <div class="form-group">
                    <label for="notes">備註</label>
                    <textarea id="notes" name="notes" rows="4"></textarea>
                </div>
                <button type="submit" class="btn btn-primary btn-large">確認報名</button>
            </form>
        </section>
        {% else %}
        <div class="alert alert-warning">
            <strong>⚠️ 報名已截止</strong><br>
            此比賽的報名已於 {{ contest.registration_deadline.strftime('%Y-%m-%d') }} 截止。
        </div>
        {% endif %}
    </div>
</section>
{% endblock %}
{% block scripts %}
<script src="/static/js/contest.js"></script>
{% endblock %}
"""

CONTACT_HTML = """
{% extends "base.html" %}
{% block title %}聯絡我們 - DJ 器材預購與入門學習平台{% endblock %}
{% block content %}
<section class="contact-section">
    <div class="container">
        <h1 class="section-title">聯絡我們</h1>
        <p class="section-subtitle">有問題或想合作？歡迎與我們聯絡</p>

        <div class="contact-layout">
            <aside class="contact-info">
                <h3>聯絡資訊</h3>
                <div class="info-item"><span class="label">📍 地址</span><p>{{ contact_address }}</p></div>
                <div class="info-item"><span class="label">📱 電話</span><p><a href="tel:{{ contact_phone }}">{{ contact_phone }}</a></p></div>
                <div class="info-item"><span class="label">📧 Email</span><p><a href="mailto:{{ contact_email }}">{{ contact_email }}</a></p></div>
                <div class="info-item"><span class="label">⏰ 營業時間</span><p>{{ business_hours }}</p></div>
                <div class="info-item"><span class="label">📸 Instagram</span><p><a href="{{ instagram_url }}" target="_blank">https://www.instagram.com/nchu_karaok/</a></p></div>
            </aside>

            <main class="contact-form-section">
                <h3>意見回饋 / 廠商贊助</h3>
                <p>個人意見回饋若已登入，系統會自動帶入會員資料；廠商贊助不需要登入。</p>

                {% if success %}
                <div class="alert alert-success">✅ 感謝您的訊息，我們將盡快回覆。</div>
                {% endif %}

                <form method="POST" action="/contact/submit" class="contact-form">
                    <div class="form-group">
                        <label for="name">姓名 *</label>
                        <input type="text" id="name" name="name" value="{{ user.full_name if user else '' }}" required />
                    </div>

                    <div class="form-group">
                        <label for="person_type">單位 or 個人 *</label>
                        <input type="text" id="person_type" name="person_type" value="{% if user %}個人{% endif %}" placeholder="例：個人、某某公司、某某社團" required />
                    </div>

                    <div class="form-group">
                        <label>聯絡類型 *</label>
                        <div class="radio-group">
                            <label><input type="radio" name="message_type" value="personal_feedback" checked /> 個人意見回饋</label>
                            <label><input type="radio" name="message_type" value="sponsor_inquiry" /> 廠商贊助</label>
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="email">聯絡信箱 *</label>
                        <input type="email" id="email" name="email" value="{{ user.email if user else '' }}" required />
                    </div>

                    <div class="form-group">
                        <label for="phone">聯絡電話 *</label>
                        <input type="tel" id="phone" name="phone" value="{{ user.phone if user else '' }}" required />
                    </div>

                    <div class="form-group">
                        <label for="subject">主旨</label>
                        <input type="text" id="subject" name="subject" />
                    </div>

                    <div class="form-group">
                        <label for="message">詳細內容 *</label>
                        <textarea id="message" name="message" rows="6" required minlength="10"></textarea>
                    </div>

                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">送出訊息</button>
                        <button type="reset" class="btn btn-secondary">清除</button>
                    </div>
                </form>
            </main>
        </div>
    </div>
</section>
{% endblock %}
{% block scripts %}
<script src="/static/js/contact.js"></script>
{% endblock %}
"""

ADMIN_PRODUCTS_HTML = """
{% extends "base.html" %}
{% block title %}商品管理 - 管理後台{% endblock %}
{% block content %}
<section class="admin-section">
    <div class="admin-container">
        <aside class="admin-sidebar">
            <div class="admin-header">
                <h3>管理後台</h3>
                <p class="admin-user">{{ user.username }}</p>
            </div>
            <nav class="admin-nav">
                <a href="/admin" class="admin-nav-item">📊 儀表板</a>
                <a href="/admin/products" class="admin-nav-item active">📦 商品管理</a>
                <a href="/admin/orders" class="admin-nav-item">📋 訂單管理</a>
                <a href="/admin/courses" class="admin-nav-item">📚 課程管理</a>
                <a href="/admin/contests" class="admin-nav-item">🎤 比賽管理</a>
                <a href="/logout" class="admin-nav-item logout">🚪 登出</a>
            </nav>
        </aside>

        <main class="admin-main">
            <div class="admin-header-with-btn">
                <h1>商品管理</h1>
            </div>

            <div class="admin-filter">
                <form method="GET" action="/admin/products" class="filter-form">
                    <label>種類:</label>
                    <select name="instrument">
                        <option value="ddj" {% if instrument == 'ddj' %}selected{% endif %}>DJ盤</option>
                        <option value="audio" {% if instrument == 'audio' %}selected{% endif %}>音響</option>
                        <option value="wire" {% if instrument == 'wire' %}selected{% endif %}>線材</option>
                        <option value="music" {% if instrument == 'music' %}selected{% endif %}>音樂</option>
                    </select>
                    <button type="submit" class="btn btn-secondary">篩選</button>
                </form>
            </div>

            <section class="admin-card">
                <h2>新增商品</h2>
                <form method="POST" action="/admin/products/create" class="admin-product-form">
                    <input type="hidden" name="instrument" value="{{ instrument }}">
                    <div class="form-row">
                        <input name="name" placeholder="名稱" required>
                        <input name="brand" placeholder="品牌 / 類型">
                        <input name="price" type="number" step="1" placeholder="價格" required>
                        <input name="stock" type="number" placeholder="庫存" value="0">
                    </div>
                    <textarea name="description" placeholder="描述"></textarea>
                    <button type="submit" class="btn btn-primary">新增商品</button>
                </form>
            </section>

            {% if products %}
            <table class="admin-table">
                <thead>
                    <tr>
                        <th>ID</th><th>名稱</th><th>品牌/類型</th><th>價格</th><th>庫存</th><th>動作</th>
                    </tr>
                </thead>
                <tbody>
                    {% for product in products %}
                    <tr>
                        <form method="POST" action="/admin/products/{{ instrument }}/{{ product.id }}/edit">
                            <td>{{ product.id }}</td>
                            <td><input name="name" value="{{ product.name if product.name is defined else product.title }}"></td>
                            <td><input name="brand" value="{{ product.brand if product.brand is defined else (product.genre if product.genre is defined else '') }}"></td>
                            <td><input name="price" type="number" step="1" value="{{ product.price }}"></td>
                            <td><input name="stock" type="number" value="{{ product.in_stock if product.in_stock is defined else 0 }}"></td>
                            <td>
                                <button type="submit" class="btn btn-sm btn-secondary">儲存</button>
                            </td>
                        </form>
                        <td>
                            <form method="POST" action="/admin/products/{{ instrument }}/{{ product.id }}/delete">
                                <button type="submit" class="btn btn-sm btn-danger" onclick="return confirm('確定刪除？')">刪除</button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p class="no-data">沒有找到商品</p>
            {% endif %}
        </main>
    </div>
</section>
{% endblock %}
{% block scripts %}
<script src="/static/js/admin.js"></script>
{% endblock %}
"""

CART_JS = """
function updateCartBadge() {
    fetch('/cart/count')
        .then(response => response.json())
        .then(data => {
            const badge = document.querySelector('.cart-badge');
            if (badge) badge.textContent = data.count;
        })
        .catch(() => {});
}

async function addToCart(setId, quantity = 1) {
    const response = await fetch('/cart/add', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({preorder_set_id: setId, quantity: quantity})
    });

    if (response.ok) {
        if (window.App && App.utils) App.utils.showNotification('✅ 已加入購物車', 'success');
        updateCartBadge();
    } else if (response.status === 401) {
        window.location.href = '/login?next=/cart';
    } else {
        const error = await response.json().catch(() => ({}));
        alert(error.detail || '加入購物車失敗');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.add-to-cart-form').forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const setId = form.querySelector('input[name="set_id"], input[name="preorder_set_id"]').value;
            const qtyInput = form.querySelector('input[name="quantity"]');
            addToCart(parseInt(setId), qtyInput ? parseInt(qtyInput.value || '1') : 1);
        });
    });
});
"""

COURSE_JS = """
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('a[href*="#form"]').forEach(link => {
        link.addEventListener('click', (e) => {
            const url = new URL(link.href);
            if (url.pathname !== window.location.pathname || url.search !== window.location.search) {
                return;
            }
            e.preventDefault();
            const formElement = document.querySelector('#form');
            if (formElement) {
                formElement.scrollIntoView({ behavior: 'smooth' });
                setTimeout(() => {
                    const firstInput = formElement.querySelector('input');
                    if (firstInput) firstInput.focus();
                }, 500);
            }
        });
    });
});
"""

CONTEST_JS = """
document.addEventListener('DOMContentLoaded', () => {
    const deadlineElement = document.querySelector('[data-deadline]');
    if (deadlineElement) {
        const deadline = new Date(deadlineElement.getAttribute('data-deadline'));
        if (new Date() > deadline) {
            const btn = document.querySelector('.registration-form .btn-primary');
            if (btn) {
                btn.disabled = true;
                btn.classList.add('btn-disabled');
            }
        }
    }

    document.querySelectorAll('a[href*="#form"]').forEach(link => {
        link.addEventListener('click', (e) => {
            const url = new URL(link.href);
            if (url.pathname !== window.location.pathname || url.search !== window.location.search) {
                return;
            }
            e.preventDefault();
            const formElement = document.querySelector('#form');
            if (formElement) {
                formElement.scrollIntoView({ behavior: 'smooth' });
                setTimeout(() => {
                    const firstInput = formElement.querySelector('input');
                    if (firstInput) firstInput.focus();
                }, 500);
            }
        });
    });
});
"""

AUTH_JS = """
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('input[type="password"]').forEach(input => {
        input.addEventListener('input', () => {
            if (input.value.length > 0 && input.value.length < 8) {
                input.setCustomValidity('密碼至少需要 8 個字元');
            } else {
                input.setCustomValidity('');
            }
        });
    });
});
"""

CHECKOUT_CSS = """
.checkout-section {
    padding: var(--spacing-2xl) var(--spacing-md);
    min-height: 80vh;
}

.checkout-layout {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: var(--spacing-xl);
    align-items: start;
}

.checkout-summary {
    background-color: var(--color-dark-tertiary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-lg);
    position: sticky;
    top: var(--spacing-xl);
    height: calc(100vh - 140px);
    display: flex;
    flex-direction: column;
}

.checkout-summary-scroll {
    flex: 1 1 80%;
    overflow-y: auto;
    padding-right: 6px;
}

.checkout-total-block {
    flex: 0 0 20%;
    border-top: 1px solid var(--border-color);
    margin-top: var(--spacing-md);
    padding-top: var(--spacing-md);
}

.checkout-summary h3,
.checkout-form h3 {
    color: var(--color-primary);
    margin-bottom: var(--spacing-lg);
}

.summary-items {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.summary-item {
    padding: var(--spacing-md);
    background-color: var(--color-dark-secondary);
    border-radius: var(--border-radius-md);
}

.item-name {
    font-weight: var(--font-weight-semibold);
    color: var(--color-light);
    margin-bottom: var(--spacing-xs);
}

.item-qty {
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
    margin-bottom: var(--spacing-xs);
}

.item-price {
    color: var(--color-secondary);
    font-weight: var(--font-weight-semibold);
}

.summary-total {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-bold);
    color: var(--color-primary);
}

.total-amount {
    font-size: var(--font-size-xl);
}

.checkout-form {
    background-color: var(--color-dark-tertiary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-lg);
}

.checkout-form .form-group {
    margin-bottom: var(--spacing-lg);
}

.checkout-form label {
    color: var(--color-light);
    font-weight: var(--font-weight-semibold);
}

.checkout-form input,
.checkout-form textarea {
    width: 100%;
    padding: var(--spacing-md);
    background-color: var(--color-dark-secondary);
    color: var(--color-light);
    border: 2px solid var(--border-color);
    border-radius: var(--border-radius-md);
    font-family: var(--font-family-base);
    transition: all var(--transition-base);
}

.checkout-form input:focus,
.checkout-form textarea:focus {
    outline: none;
    border-color: var(--color-secondary);
    box-shadow: 0 0 10px rgba(0, 245, 255, 0.2);
}

.checkout-actions {
    display: flex;
    gap: var(--spacing-md);
    margin-top: var(--spacing-xl);
}

.checkout-actions .btn {
    flex: 1;
}

@media (max-width: 768px) {
    .checkout-layout {
        grid-template-columns: 1fr;
    }
    .checkout-summary {
        position: static;
        height: auto;
        order: 1;
    }
    .checkout-summary-scroll {
        overflow: visible;
        max-height: none;
    }
    .checkout-form {
        order: 2;
    }
    .checkout-actions {
        flex-direction: column;
    }
}
"""

SQL_FIX = """
USE dj_platform;

ALTER TABLE course_registrations MODIFY user_id INT NULL;
ALTER TABLE contest_registrations MODIFY user_id INT NULL;
ALTER TABLE preorder_sets MODIFY set_type VARCHAR(50) NOT NULL;
ALTER TABLE ddj MODIFY brand VARCHAR(50);
ALTER TABLE audio MODIFY audio_type VARCHAR(50) NOT NULL;
ALTER TABLE music MODIFY genre VARCHAR(50) NOT NULL;
ALTER TABLE orders MODIFY status VARCHAR(50);
ALTER TABLE orders MODIFY payment_method VARCHAR(50) NULL;

UPDATE preorder_sets SET set_type = 'Starter' WHERE set_type = 'STARTER';
UPDATE preorder_sets SET set_type = 'Intermediate' WHERE set_type = 'INTERMEDIATE';
UPDATE preorder_sets SET set_type = 'Professional' WHERE set_type = 'PROFESSIONAL';
"""

def main():
    global_import_patch()
    patch_enum_models_to_string()

    write_file("main.py", MAIN_PY)
    write_file("app/core/config.py", CONFIG_PY)
    write_file("app/core/dependencies.py", DEPENDENCIES_PY)

    write_file("app/services/auth_service.py", AUTH_SERVICE_PY)
    write_file("app/services/product_service.py", PRODUCT_SERVICE_PY)
    write_file("app/services/cart_service.py", CART_SERVICE_PY)
    write_file("app/services/order_service.py", ORDER_SERVICE_PY)
    write_file("app/services/course_service.py", COURSE_SERVICE_PY)
    write_file("app/services/contest_service.py", CONTEST_SERVICE_PY)
    write_file("app/services/contact_service.py", CONTACT_SERVICE_PY)

    write_file("app/routers/auth.py", AUTH_ROUTER_PY)
    write_file("app/routers/home.py", HOME_ROUTER_PY)
    write_file("app/routers/category.py", CATEGORY_ROUTER_PY)
    write_file("app/routers/search.py", SEARCH_ROUTER_PY)
    write_file("app/routers/detail.py", DETAIL_ROUTER_PY)
    write_file("app/routers/cart.py", CART_ROUTER_PY)
    write_file("app/routers/checkout.py", CHECKOUT_ROUTER_PY)
    write_file("app/routers/course.py", COURSE_ROUTER_PY)
    write_file("app/routers/contest.py", CONTEST_ROUTER_PY)
    write_file("app/routers/contact.py", CONTACT_ROUTER_PY)
    write_file("app/routers/admin.py", ADMIN_ROUTER_PY)
    write_file("app/routers/orders.py", ORDERS_ROUTER_PY)

    write_file("templates/partials/head_meta.html", HEAD_META_HTML)
    write_file("templates/partials/navbar.html", NAVBAR_HTML)
    write_file("templates/login.html", LOGIN_HTML)
    write_file("templates/register.html", REGISTER_HTML)
    write_file("templates/cart.html", CART_HTML)
    write_file("templates/checkout.html", CHECKOUT_HTML)
    write_file("templates/course_list.html", COURSE_LIST_HTML)
    write_file("templates/course_detail.html", COURSE_DETAIL_HTML)
    write_file("templates/contest_list.html", CONTEST_LIST_HTML)
    write_file("templates/contest_detail.html", CONTEST_DETAIL_HTML)
    write_file("templates/contact.html", CONTACT_HTML)
    write_file("templates/admin_products.html", ADMIN_PRODUCTS_HTML)

    write_file("static/js/cart.js", CART_JS)
    write_file("static/js/course.js", COURSE_JS)
    write_file("static/js/contest.js", CONTEST_JS)
    write_file("static/js/auth.js", AUTH_JS)
    write_file("static/css/pages/checkout.css", CHECKOUT_CSS)

    write_file("sql/99_fix_existing_tables.sql", SQL_FIX)

    print("\\n[DONE] 修正完成")
    print("下一步：")
    print("1) python -m compileall .")
    print("2) uvicorn main:app --reload")
    print("3) 如果資料庫權限不允許程式自動 ALTER，請到 phpMyAdmin 執行 sql/99_fix_existing_tables.sql")

if __name__ == "__main__":
    main()
