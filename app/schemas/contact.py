"""
聯絡表單相關 Pydantic 驗證模型
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class ContactMessageRequest(BaseModel):
    """聯絡消息請求"""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    message_type: str = Field(..., min_length=1, max_length=50)
    subject: str = Field(..., min_length=1, max_length=150)
    message: str = Field(..., min_length=1)


class ContactMessageResponse(BaseModel):
    """聯絡消息響應"""
    id: int
    name: str
    email: str
    message_type: str
    subject: str
    status: str

    class Config:
        from_attributes = True
