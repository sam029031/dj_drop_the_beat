"""訂單業務邏輯"""
from sqlalchemy.orm import Session
from app.models.order import Order, OrderItem
from app.models.cart import Cart, CartItem
from app.models.preorder_set import PreorderSet
from app.models.ddj import DDJ
from app.models.audio import Audio
from app.models.wire import Wire
from app.models.music import Music
from app.core.utils import generate_order_number, get_current_datetime
from datetime import timedelta
import json

PRODUCT_MODELS = {
    "preorder_set": PreorderSet,
    "ddj": DDJ,
    "audio": Audio,
    "wire": Wire,
    "music": Music,
}

class OrderService:
    @staticmethod
    def _get_product(db: Session, product_type: str, product_id: int):
        """取得指定產品"""
        model = PRODUCT_MODELS.get(product_type)
        if not model:
            return None
        return db.query(model).filter(model.id == product_id).first()

    @staticmethod
    def _product_name(product) -> str:
        """取得產品名稱"""
        if hasattr(product, 'name'):
            return product.name
        if hasattr(product, 'title'):
            return product.title
        return "商品"

    @staticmethod
    def _update_product_stock(db: Session, product_type: str, product_id: int, quantity: int):
        """更新產品庫存"""
        product = OrderService._get_product(db, product_type, product_id)
        if not product:
            return
        
        if hasattr(product, 'available_quantity') and product.available_quantity is not None:
            product.available_quantity = max(0, product.available_quantity - quantity)
        
        if hasattr(product, 'stock') and product.stock is not None:
            product.stock = max(0, product.stock - quantity)
        
        if hasattr(product, 'ordered_quantity'):
            product.ordered_quantity = (product.ordered_quantity or 0) + quantity

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
            product_type = cart_item.product_type or "preorder_set"
            product_id = cart_item.product_id or cart_item.preorder_set_id
            
            product = OrderService._get_product(db, product_type, product_id)
            if not product:
                continue

            product_name = OrderService._product_name(product)

            order_item = OrderItem(
                order_id=order.id,
                product_type=product_type,
                product_id=product_id,
                preorder_set_id=product_id if product_type == "preorder_set" else None,
                product_name=product_name,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                subtotal=cart_item.subtotal
            )
            db.add(order_item)

            # 更新產品庫存
            OrderService._update_product_stock(db, product_type, product_id, cart_item.quantity)

            order_items_data.append({
                "product_type": product_type,
                "product_id": product_id,
                "product_name": product_name,
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
