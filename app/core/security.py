"""
安全和密碼管理
"""
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from typing import Optional, Dict, Any
import logging

from .config import settings

logger = logging.getLogger(__name__)

# 密碼加密上下文
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,
    argon2__time_cost=3,
    argon2__parallelism=4
)


def hash_password(password: str) -> str:
    """
    加密密碼
    
    Args:
        password: 明文密碼
        
    Returns:
        加密後的密碼雜湊
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    驗證密碼
    
    Args:
        plain_password: 明文密碼
        hashed_password: 加密後的密碼雜湊
        
    Returns:
        密碼是否正確
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"密碼驗證失敗: {e}")
        return False


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    建立訪問令牌 (JWT)
    
    Args:
        data: 令牌中包含的數據
        expires_delta: 過期時間差
        
    Returns:
        JWT 令牌字符串
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    驗證 JWT 令牌
    
    Args:
        token: JWT 令牌字符串
        
    Returns:
        令牌中的數據，或 None 如果驗證失敗
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("令牌已過期")
        return None
    except jwt.InvalidTokenError:
        logger.warning("無效的令牌")
        return None


def generate_password_strength_score(password: str) -> int:
    """
    計算密碼強度分數 (0-5)
    
    Args:
        password: 密碼字符串
        
    Returns:
        強度分數
    """
    score = 0
    
    # 檢查長度
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    
    # 檢查字符類型
    if any(c.isupper() for c in password):
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        score += 1
    
    return min(score, 5)
