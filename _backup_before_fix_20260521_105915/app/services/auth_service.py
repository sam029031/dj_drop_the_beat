"""
認證業務邏輯
"""
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.auth import UserLogin, UserRegister
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """認證業務邏輯"""
    
    @staticmethod
    def register_user(db: Session, user_data: UserRegister) -> User:
        """註冊新用戶"""
        user = db.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        
        if user:
            raise ValueError("用戶名或郵箱已存在")
        
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            full_name=user_data.full_name,
            phone=user_data.phone
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"新用戶註冊: {user_data.username}")
        return new_user
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> User:
        """驗證用戶登入"""
        user = db.query(User).filter(User.username == username).first()
        
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("用戶名或密碼錯誤")
        
        if not user.is_active:
            raise ValueError("帳號已停用")
        
        logger.info(f"用戶登入: {username}")
        return user
    
    @staticmethod
    def create_user_token(user: User) -> str:
        """為用戶建立 JWT 令牌"""
        token_data = {"sub": user.id, "username": user.username}
        token = create_access_token(token_data)
        return token
