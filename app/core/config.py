"""應用程式配置"""
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Settings:
    APP_NAME: str = "DJ 器材預購與入門學習平台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("1", "true", "yes", "on")

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:@127.0.0.1:3306/dj_platform?charset=utf8mb4"
    )

    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-secret-key")
    SESSION_SECRET: str = os.getenv("SESSION_SECRET", "change-this-session-secret")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))

    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./static/uploads")
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))

    TIMEZONE: str = os.getenv("TIMEZONE", "Asia/Taipei")

    CONTACT_EMAIL: str = os.getenv("CONTACT_EMAIL", "service@djequip.com")
    CONTACT_PHONE: str = os.getenv("CONTACT_PHONE", "0967-676-767")
    CONTACT_ADDRESS: str = os.getenv("CONTACT_ADDRESS", "台中市南區興大路145號")
    BUSINESS_HOURS: str = os.getenv("BUSINESS_HOURS", "週一至週五 09:00-18:00")
    INSTAGRAM_URL: str = os.getenv("INSTAGRAM_URL", "https://www.instagram.com/nchu_karaok/")

    ALLOWED_ORIGINS: list = [
        "http://localhost",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
    ]

    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    SMTP_SERVER: Optional[str] = os.getenv("SMTP_SERVER")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")

    PREORDER_SETS_COUNT: int = 3
    PAYMENT_DEADLINE_DAYS: int = 7
    REGISTRATION_DEADLINE_BUFFER_HOURS: int = 1

settings = Settings()
