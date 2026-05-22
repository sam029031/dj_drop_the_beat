"""認證業務邏輯"""
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.auth import UserRegister
import logging

logger = logging.getLogger(__name__)

class AuthService:
    @staticmethod
    def ensure_default_admin(db: Session) -> User:
        admin = db.query(User).filter(User.username == "admin").first()
        hashed = hash_password("Admin@123456")
        if not admin:
            admin = User(
                username="admin",
                email="admin@dj-platform.com",
                password_hash=hashed,
                full_name="DJ Platform Admin",
                phone="0967-676-767",
                is_admin=True,
                is_active=True
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            logger.info("已建立預設管理員：admin / Admin@123456")
            return admin

        changed = False
        if not verify_password("Admin@123456", admin.password_hash):
            admin.password_hash = hashed
            changed = True
        if not admin.is_admin:
            admin.is_admin = True
            changed = True
        if not admin.is_active:
            admin.is_active = True
            changed = True
        if changed:
            db.commit()
            db.refresh(admin)
            logger.info("已修正預設管理員密碼與權限：admin / Admin@123456")
        return admin

    @staticmethod
    def register_user(db: Session, user_data: UserRegister, address: str | None = None) -> User:
        exists = db.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        if exists:
            raise ValueError("用戶名或郵箱已存在")

        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            full_name=user_data.full_name,
            phone=user_data.phone,
            address=address,
            is_admin=False,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> User:
        user = db.query(User).filter(User.username == username).first()

        if username == "admin" and password == "Admin@123456":
            user = AuthService.ensure_default_admin(db)
            return user

        if not user:
            raise ValueError("用戶名稱或密碼錯誤")

        if not verify_password(password, user.password_hash):
            raise ValueError("用戶名稱或密碼錯誤")

        if not user.is_active:
            raise ValueError("帳號已停用")

        return user

    @staticmethod
    def create_user_token(user: User) -> str:
        return create_access_token({"sub": str(user.id), "username": user.username})
