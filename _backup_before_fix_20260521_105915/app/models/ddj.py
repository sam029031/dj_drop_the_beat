"""
DJ 控制器模型 (DJ Board / DDJ)
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Enum
from sqlalchemy.sql import func
import enum

from ..core.database import Base


class BrandEnum(str, enum.Enum):
    """品牌列表"""
    PIONEER = "Pioneer"
    NUMARK = "Numark"
    TECHNICS = "Technics"
    RELOOP = "Reloop"
    DENON = "Denon"
    OTHER = "Other"


class DDJ(Base):
    """DJ 控制器表"""
    
    __tablename__ = "ddj"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    brand = Column(String(50), default='Pioneer')
    model = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    channels = Column(Integer, default=2)  # 頻道數
    effects_count = Column(Integer, default=8)  # 效果數
    jog_wheels = Column(Integer, default=2)  # 轉盤數
    faders = Column(Integer, default=3)  # 推子數
    
    # SEO 和分類
    image_url = Column(String(255), nullable=True)
    category = Column(String(50), default="ddj", index=True)
    in_stock = Column(Integer, default=0)
    preorder_available = Column(Integer, default=0)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<DDJ(id={self.id}, name={self.name}, brand={self.brand})>"

# ---- template compatibility ----
DDJ.image = property(lambda self: self.image_url)
DDJ.stock = property(lambda self: self.in_stock)
DDJ.features = property(lambda self: self.description)

