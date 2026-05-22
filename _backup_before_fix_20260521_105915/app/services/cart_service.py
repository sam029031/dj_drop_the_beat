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
