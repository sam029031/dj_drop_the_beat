"""
線材配件模型
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.sql import func

from ..core.database import Base


class Wire(Base):
    """線材配件表"""
    
    __tablename__ = "wire"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    wire_type = Column(String(50), nullable=False)  # 如: XLR, USB, 3.5mm 等
    brand = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    
    # 線材規格
    length_meters = Column(Float, nullable=True)  # 長度 (公尺)
    connector_type = Column(String(50), nullable=True)  # 連接器類型
    cable_material = Column(String(100), nullable=True)  # 線材材質
    shielding_type = Column(String(50), nullable=True)  # 屏蔽類型
    
    # SEO 和分類
    image_url = Column(String(255), nullable=True)
    category = Column(String(50), default="wire", index=True)
    in_stock = Column(Integer, default=0)
    preorder_available = Column(Integer, default=0)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Wire(id={self.id}, name={self.name}, type={self.wire_type})>"

# ---- template compatibility ----
Wire.image = property(lambda self: self.image_url)
Wire.stock = property(lambda self: self.in_stock)
Wire.type = property(lambda self: self.wire_type)
Wire.length = property(lambda self: f'{self.length_meters:g} 公尺' if self.length_meters else '')

