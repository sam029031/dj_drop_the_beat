"""購物車業務邏輯"""
from sqlalchemy.orm import Session
from app.models.cart import Cart, CartItem
from app.models.preorder_set import PreorderSet
from app.models.ddj import DDJ
from app.models.audio import Audio
from app.models.wire import Wire
from app.models.music import Music
import json

PRODUCT_MODELS = {
    "preorder_set": PreorderSet,
    "ddj": DDJ,
    "audio": Audio,
    "wire": Wire,
    "music": Music,
}

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
    def _get_product(db: Session, product_type: str, product_id: int):
        """取得指定產品"""
        model = PRODUCT_MODELS.get(product_type)
        if not model:
            return None
        return db.query(model).filter(model.id == product_id).first()

    @staticmethod
    def _price(product) -> float:
        """取得產品價格"""
        if hasattr(product, 'discount_price') and product.discount_price:
            return float(product.discount_price)
        if hasattr(product, 'price'):
            return float(product.price or 0)
        return 0.0

    @staticmethod
    def _product_name(product) -> str:
        """取得產品名稱"""
        if hasattr(product, 'name'):
            return product.name
        if hasattr(product, 'title'):
            return product.title
        return "商品"

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
    def add_to_cart(db: Session, user_id: int, product_id: int, quantity: int = 1, 
                   product_type: str = "preorder_set") -> CartItem:
        """添加產品到購物車"""
        # 規範化 product_type
        product_type = product_type.lower() if product_type else "preorder_set"
        if product_type == "dj":
            product_type = "ddj"
        
        quantity = max(1, int(quantity or 1))
        cart = CartService.get_or_create_cart(db, user_id)
        
        # 取得產品
        product = CartService._get_product(db, product_type, product_id)
        if not product:
            raise ValueError(f"產品不存在 (類型: {product_type}, ID: {product_id})")
        
        # 檢查庫存
        if hasattr(product, 'available_quantity') and product.available_quantity is not None:
            if product.available_quantity < quantity:
                raise ValueError("庫存不足")
        elif hasattr(product, 'stock') and product.stock:
            # stock == 0 視為未設定（無限量），只在明確有庫存數量時才檢查
            if product.stock < quantity:
                raise ValueError("庫存不足")

        # 檢查是否已在購物車中
        item = db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.product_type == product_type,
            CartItem.product_id == product_id
        ).first()

        price = CartService._price(product)
        product_name = CartService._product_name(product)

        if item:
            item.quantity += quantity
            CartService._update_item_subtotal(item)
        else:
            item = CartItem(
                cart_id=cart.id,
                product_type=product_type,
                product_id=product_id,
                preorder_set_id=product_id if product_type == "preorder_set" else None,
                quantity=quantity,
                unit_price=price,
                product_name=product_name or "商品",
                subtotal=quantity * price
            )
            db.add(item)

        CartService._update_cart_totals(db, cart)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def get_cart_view(db: Session, user_id: int) -> dict:
        """取得購物車視圖"""
        cart = CartService.get_or_create_cart(db, user_id)
        items_data = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()

        items = []
        total = 0
        for cart_item in items_data:
            # 取得產品資訊
            product = CartService._get_product(db, cart_item.product_type, cart_item.product_id)
            
            if not product:
                # 產品已刪除，移除購物車項目
                db.delete(cart_item)
                continue
            
            unit_price = CartService._price(product)
            product_name = CartService._product_name(product)
            subtotal = unit_price * int(cart_item.quantity or 0)
            total += subtotal
            
            item_info = {
                "id": cart_item.id,
                "product_type": cart_item.product_type,
                "product_id": cart_item.product_id,
                "name": product_name,
                "quantity": cart_item.quantity,
                "unit_price": unit_price,
                "subtotal": subtotal,
            }
            
            # 添加產品特定資訊
            if hasattr(product, 'description'):
                item_info["description"] = product.description
            if hasattr(product, 'included_items'):
                item_info["included_items"] = CartService._normalize_included_items(product.included_items)
            
            items.append(item_info)

        cart.total_price = total
        cart.item_count = sum(item["quantity"] for item in items)
        db.commit()
        return {"cart": cart, "items": items, "total": total}

    @staticmethod
    def update_quantity(db: Session, user_id: int, item_id: int, quantity: int):
        """更新購物車項目數量"""
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
        """從購物車移除項目"""
        cart = CartService.get_or_create_cart(db, user_id)
        item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
        if not item:
            raise ValueError("購物車項目不存在")
        db.delete(item)
        CartService._update_cart_totals(db, cart)
        db.commit()

    @staticmethod
    def clear_cart(db: Session, user_id: int):
        """清空購物車"""
        cart = CartService.get_or_create_cart(db, user_id)
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        cart.total_price = 0
        cart.item_count = 0
        db.commit()

    @staticmethod
    def _normalize_included_items(value):
        if value is None:
            return []

        if isinstance(value, list):
            return value

        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, str):
                    parsed = json.loads(parsed)
                return parsed if isinstance(parsed, list) else []
            except Exception:
                return []
        return []

        return []
