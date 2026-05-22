"""應用程式配置"""
import os
from dotenv import load_dotenv
from typing import Optional
from urllib.parse import quote_plus

load_dotenv()


def _split_env(name: str, default: list[str]) -> list[str]:
    """將逗號分隔的環境變數轉成 list。"""
    value = os.getenv(name)
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


def _build_database_url() -> str:
    """
    Railway 部署時優先使用 Railway MySQL 提供的環境變數；
    本機開發時則回退到 XAMPP MySQL 的 dj_platform / 1234。
    """
    mysql_url = os.getenv("MYSQL_URL")
    if mysql_url:
        if mysql_url.startswith("mysql://"):
            mysql_url = mysql_url.replace("mysql://", "mysql+pymysql://", 1)
        return mysql_url

    mysql_host = os.getenv("MYSQLHOST") or os.getenv("DB_HOST")
    if mysql_host:
        mysql_port = os.getenv("MYSQLPORT") or os.getenv("DB_PORT") or "3306"
        mysql_user = os.getenv("MYSQLUSER") or os.getenv("DB_USER") or "root"
        mysql_password = os.getenv("MYSQLPASSWORD") or os.getenv("DB_PASSWORD") or ""
        mysql_database = os.getenv("MYSQLDATABASE") or os.getenv("DB_NAME") or "railway"
        return (
            f"mysql+pymysql://{quote_plus(mysql_user)}:{quote_plus(mysql_password)}"
            f"@{mysql_host}:{mysql_port}/{mysql_database}?charset=utf8mb4"
        )

    database_url = os.getenv("DATABASE_URL")
    if database_url:
        if database_url.startswith("mysql://"):
            database_url = database_url.replace("mysql://", "mysql+pymysql://", 1)
        return database_url

    return "mysql+pymysql://dj_platform:1234@127.0.0.1:3306/dj_platform?charset=utf8mb4"


class Settings:
    APP_NAME: str = "DJ 器材預購與入門學習平台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("1", "true", "yes", "on")

    DATABASE_URL: str = _build_database_url()

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

    # 你的網站主要是後端直接渲染 HTML，同源請求通常不會被 CORS 擋；
    # 這裡保留本機與 Railway 網域，若前端另外部署再用環境變數 ALLOWED_ORIGINS 加入。
    ALLOWED_ORIGINS: list[str] = _split_env(
        "ALLOWED_ORIGINS",
        [
            "http://localhost",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "http://localhost:3000",
            "https://*.railway.app",
        ],
    )

    # 先開放所有 Host，避免 Railway 公開網址被 TrustedHostMiddleware 擋成 400 Bad Request。
    # 上線穩定後可在 Railway Variables 設定 TRUSTED_HOSTS=djdropthebeat-production.up.railway.app,localhost,127.0.0.1
    TRUSTED_HOSTS: list[str] = _split_env("TRUSTED_HOSTS", ["*"])

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
