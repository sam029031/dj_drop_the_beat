"""
購物車相關 Pydantic 驗證模型
"""
from pydantic import BaseModel, Field
from typing import Optional


class AddToCartRequest(BaseModel):
    """加入購物車請求"""
    preorder_set_id: int = Field(..., gt=0)
    quantity: int = Field(1, ge=1, le=100)


class UpdateCartItemRequest(BaseModel):
    """更新購物車項目請求"""
    quantity: int = Field(..., ge=1, le=100)


class CartItemResponse(BaseModel):
    """購物車項目響應"""
    id: int
    preorder_set_id: int
    set_name: str
    quantity: int
    unit_price: float
    subtotal: float

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    """購物車響應"""
    id: int
    total_price: float
    item_count: int
    items: list[CartItemResponse]

    class Config:
        from_attributes = True
