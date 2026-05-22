"""
課程相關 Pydantic 驗證模型
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class CourseRegistrationRequest(BaseModel):
    """課程報名請求"""
    course_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=9)
    notes: Optional[str] = None


class CourseResponse(BaseModel):
    """課程響應"""
    id: int
    title: str
    instructor: str
    difficulty: str
    price: float
    duration_hours: float
    max_students: int
    current_students: int
    start_date: datetime
    registration_deadline: Optional[datetime]
    image_url: Optional[str]

    class Config:
        from_attributes = True


class CourseRegistrationResponse(BaseModel):
    """課程報名響應"""
    id: int
    registration_number: str
    name: str
    status: str
    registered_at: datetime

    class Config:
        from_attributes = True
