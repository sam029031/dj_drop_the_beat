"""
認證相關 Pydantic 驗證模型
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserLogin(BaseModel):
    """用戶登入請求"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)


class UserRegister(BaseModel):
    """用戶註冊請求"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)


class UserResponse(BaseModel):
    """用戶信息響應"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    is_admin: bool
    is_active: bool

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """令牌響應"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
