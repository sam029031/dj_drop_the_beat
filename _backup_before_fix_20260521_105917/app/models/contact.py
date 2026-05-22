"""
聯絡/消息模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func

from ..core.database import Base


class ContactMessage(Base):
    """聯絡表"""
    
    __tablename__ = "contact_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    
    # 消息信息
    message_type = Column(String(50), nullable=False)  # 如: question, suggestion, complaint
    subject = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    
    # 狀態
    status = Column(String(20), default="New")  # New, Reviewed, Resolved
    is_read = Column(Boolean, default=False)
    
    # 回覆
    reply = Column(Text, nullable=True)
    replied_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ContactMessage(id={self.id}, name={self.name}, type={self.message_type})>"
