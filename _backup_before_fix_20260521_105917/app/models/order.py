"""
訂單模型
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
import enum

from ..core.database import Base


class OrderStatusEnum(str, enum.Enum):
    """訂單狀態"""
    PENDING = "Pending"
    PAID = "Paid"
    PROCESSING = "Processing"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"
    REFUNDED = "Refunded"


class PaymentMethodEnum(str, enum.Enum):
    """支付方式"""
    BANK_TRANSFER = "Bank Transfer"
    CREDIT_CARD = "Credit Card"
    PAYPAL = "PayPal"
    LINE_PAY = "Line Pay"
    CASH_ON_DELIVERY = "Cash on Delivery"


class Order(Base):
    """訂單表"""
    
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 收件人信息
    buyer_name = Column(String(100), nullable=False)
    buyer_email = Column(String(120), nullable=False)
    buyer_phone = Column(String(20), nullable=False)
    buyer_address = Column(Text, nullable=False)
    
    # 訂單金額
    total_price = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0)
    tax_amount = Column(Float, default=0)
    final_price = Column(Float, nullable=False)
    
    # 訂單狀態
    status = Column(String(50), default='Pending', index=True)
    payment_method = Column(String(50), nullable=True)
    
    # 訂單項目 (JSON 儲存)
    items = Column(JSON, nullable=True)
    
    # 時間戳
    payment_deadline = Column(DateTime, nullable=True)  # 支付截止日期
    paid_at = Column(DateTime, nullable=True)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Order(id={self.id}, order_number={self.order_number}, status={self.status})>"


class OrderItem(Base):
    """訂單項目表"""
    
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    preorder_set_id = Column(Integer, ForeignKey("preorder_sets.id"), nullable=False)
    
    # 項目信息
    set_name = Column(String(100), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, qty={self.quantity})>"
