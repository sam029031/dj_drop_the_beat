"""
比賽相關 Pydantic 驗證模型
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class ContestRegistrationRequest(BaseModel):
    """比賽報名請求"""
    contest_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=9)
    dj_name: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class ContestResponse(BaseModel):
    """比賽響應"""
    id: int
    title: str
    venue: str
    entry_fee: float
    prize_pool: Optional[float]
    registration_deadline: datetime
    event_date: datetime
    current_participants: int
    max_participants: int
    image_url: Optional[str]

    class Config:
        from_attributes = True


class ContestRegistrationResponse(BaseModel):
    """比賽報名響應"""
    id: int
    registration_number: str
    name: str
    dj_name: Optional[str]
    status: str
    registered_at: datetime

    class Config:
        from_attributes = True
