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
