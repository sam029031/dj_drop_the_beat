"""
音響設備模型
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Enum, Boolean
from sqlalchemy.sql import func
import enum

from ..core.database import Base


class AudioTypeEnum(str, enum.Enum):
    """音響類型"""
    SPEAKER = "Speaker"
    HEADPHONES = "Headphones"
    MONITOR = "Monitor"
    SUBWOOFER = "Subwoofer"
    MIXER = "Mixer"
    MICROPHONE = "Microphone"


class Audio(Base):
    """音響設備表"""
    
    __tablename__ = "audio"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    audio_type = Column(String(50), nullable=False)
    brand = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    
    # 音響規格
    watts = Column(Integer, nullable=True)  # 功率 (瓦特)
    frequency_response = Column(String(50), nullable=True)  # 頻率響應
    impedance = Column(String(50), nullable=True)  # 阻抗
    connectivity = Column(String(100), nullable=True)  # 連接類型
    
    # SEO 和分類
    image_url = Column(String(255), nullable=True)
    category = Column(String(50), default="audio", index=True)
    in_stock = Column(Integer, default=0)
    preorder_available = Column(Integer, default=0)
    warranty_months = Column(Integer, default=12)  # 保修月數
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Audio(id={self.id}, name={self.name}, type={self.audio_type})>"

# ---- template compatibility ----
Audio.image = property(lambda self: self.image_url)
Audio.stock = property(lambda self: self.in_stock)
Audio.form = property(lambda self: self.audio_type.value if hasattr(self.audio_type, 'value') else self.audio_type)
Audio.size = property(lambda self: self.frequency_response)
Audio.features = property(lambda self: self.description)

