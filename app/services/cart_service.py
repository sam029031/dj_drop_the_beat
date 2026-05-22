"""購物車業務邏輯"""
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
