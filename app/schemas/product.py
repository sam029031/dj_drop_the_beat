"""
商品相關 Pydantic 驗證模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ProductBase(BaseModel):
    """商品基礎 schema"""
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    description: Optional[str] = None


class PreorderSetResponse(BaseModel):
    """預購 SET 響應"""
    id: int
    name: str
    set_type: str
    price: float
    discount_price: Optional[float]
    description: Optional[str]
    available_quantity: int
    image_url: Optional[str]
    is_featured: bool

    class Config:
        from_attributes = True


class ProductFilterRequest(BaseModel):
    """商品篩選請求"""
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
