"""
預購 SET 模型
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON, Boolean
from sqlalchemy.sql import func
import enum

from ..core.database import Base


class SetTypeEnum(str, enum.Enum):
    """預購 SET 類型"""
    STARTER = "Starter"
    INTERMEDIATE = "Intermediate"
    PROFESSIONAL = "Professional"


class PreorderSet(Base):
    """預購 SET 表"""
    
    __tablename__ = "preorder_sets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    set_type = Column(String(50), nullable=False, index=True)
    price = Column(Float, nullable=False)
    discount_price = Column(Float, nullable=True)  # 優惠價格
    description = Column(Text, nullable=True)
    
    # SET 包含的項目
    # 格式: [{"category": "ddj", "product_id": 1, "quantity": 1}, ...]
    included_items = Column(JSON, nullable=True)
    
    # 庫存和預購
    total_quantity = Column(Integer, default=50)  # 總數量
    available_quantity = Column(Integer, default=50)  # 可用數量
    ordered_quantity = Column(Integer, default=0)  # 已訂購數量
    
    # 圖片和展示
    image_url = Column(String(255), nullable=True)
    is_featured = Column(Boolean, default=False)  # 是否精選
    sort_order = Column(Integer, default=0)  # 排序
    
    # 預購信息
    preorder_deadline = Column(DateTime, nullable=True)  # 預購截止日期
    estimated_delivery = Column(DateTime, nullable=True)  # 預計交期
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<PreorderSet(id={self.id}, name={self.name}, type={self.set_type})>"
