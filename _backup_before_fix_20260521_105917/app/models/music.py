"""
音樂模型
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean
from sqlalchemy.sql import func
import enum

from ..core.database import Base


class GenreEnum(str, enum.Enum):
    """音樂風格"""
    ELECTRONIC = "Electronic"
    HIP_HOP = "Hip Hop"
    HOUSE = "House"
    TECHNO = "Techno"
    DRUM_AND_BASS = "Drum and Bass"
    DUBSTEP = "Dubstep"
    POP = "Pop"
    ROCK = "Rock"
    JAZZ = "Jazz"
    OTHER = "Other"


class Music(Base):
    """音樂表"""
    
    __tablename__ = "music"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    artist = Column(String(100), nullable=False, index=True)
    genre = Column(String(50), nullable=False, index=True)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    
    # 音樂信息
    duration_seconds = Column(Integer, nullable=True)  # 時長
    bpm = Column(Integer, nullable=True)  # 節奏 (拍/分鐘)
    key = Column(String(10), nullable=True)  # 調性 (如: C Major)
    release_year = Column(Integer, nullable=True)  # 發行年份
    
    # SEO 和分類
    image_url = Column(String(255), nullable=True)  # 專輯封面
    category = Column(String(50), default="music", index=True)
    in_stock = Column(Integer, default=0)
    preorder_available = Column(Integer, default=0)
    is_featured = Column(Boolean, default=False)  # 是否精選
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Music(id={self.id}, title={self.title}, artist={self.artist})>"

# ---- template compatibility ----
Music.name = property(lambda self: self.title)
Music.brand = property(lambda self: self.artist)
Music.image = property(lambda self: self.image_url)
Music.stock = property(lambda self: self.in_stock)
Music.format = property(lambda self: 'FLAC / MP3 / 唱片')

