"""
訂單相關 Pydantic 驗證模型
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class CheckoutRequest(BaseModel):
    """結帳請求"""
    buyer_name: str = Field(..., min_length=1, max_length=100)
    buyer_email: EmailStr
    buyer_phone: str = Field(..., min_length=9)
    buyer_address: str = Field(..., min_length=1)


class OrderItemResponse(BaseModel):
    """訂單項目響應"""
    id: int
    set_name: str
    quantity: int
    unit_price: float
    subtotal: float

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """訂單響應"""
    id: int
    order_number: str
    buyer_name: str
    total_price: float
    final_price: float
    status: str
    created_at: datetime
    items: list[OrderItemResponse]

    class Config:
        from_attributes = True
