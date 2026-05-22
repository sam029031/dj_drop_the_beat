"""
工具函數
"""
import re
from typing import Optional, Tuple
from datetime import datetime
import pytz
import logging

from .config import settings

logger = logging.getLogger(__name__)


def validate_email(email: str) -> bool:
    """
    驗證電子郵件格式
    
    Args:
        email: 電子郵件字符串
        
    Returns:
        電子郵件是否有效
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """
    驗證台灣電話號碼
    
    Args:
        phone: 電話號碼字符串
        
    Returns:
        電話號碼是否有效
    """
    # 移除所有非數字字符
    phone = re.sub(r"\D", "", phone)
    # 台灣手機: 09XX-XXXXXXX (10 碼)
    # 台灣市話: (X)XX-XXXXXXX
    return len(phone) >= 9


def validate_password(password: str) -> Tuple[bool, str]:
    """
    驗證密碼強度
    
    Args:
        password: 密碼字符串
        
    Returns:
        (是否有效, 錯誤消息)
    """
    if len(password) < 8:
        return False, "密碼至少 8 個字符"
    
    if not any(c.isupper() for c in password):
        return False, "密碼必須包含至少一個大寫字母"
    
    if not any(c.islower() for c in password):
        return False, "密碼必須包含至少一個小寫字母"
    
    if not any(c.isdigit() for c in password):
        return False, "密碼必須包含至少一個數字"
    
    return True, ""


def format_currency(amount: float, currency: str = "TWD") -> str:
    """
    格式化貨幣顯示
    
    Args:
        amount: 金額
        currency: 貨幣代碼
        
    Returns:
        格式化後的貨幣字符串
    """
    if currency == "TWD":
        return f"${amount:,.0f}"
    return f"{amount:,.2f} {currency}"


def get_current_datetime() -> datetime:
    """
    取得當前時間 (使用設定的時區)
    
    Returns:
        當前時間
    """
    tz = pytz.timezone(settings.TIMEZONE)
    return datetime.now(tz)


def sanitize_filename(filename: str) -> str:
    """
    清理文件名 (移除危險字符)
    
    Args:
        filename: 原始文件名
        
    Returns:
        清理後的文件名
    """
    # 移除路徑分隔符和其他危險字符
    filename = re.sub(r"[/\\:*?\"<>|]", "_", filename)
    # 限制長度
    return filename[:255]


def generate_order_number() -> str:
    """
    生成訂單編號
    
    Returns:
        訂單編號 (格式: ORD-YYYYMMDD-XXXXXXX)
    """
    from datetime import datetime as dt
    import random
    import string
    
    now = dt.now()
    date_str = now.strftime("%Y%m%d")
    random_str = "".join(random.choices(string.ascii_uppercase + string.digits, k=7))
    
    return f"ORD-{date_str}-{random_str}"


def parse_pagination_params(page: int = 1, page_size: int = 20) -> Tuple[int, int]:
    """
    驗證並規範化分頁參數
    
    Args:
        page: 頁碼 (預設 1)
        page_size: 每頁大小 (預設 20)
        
    Returns:
        (skip, limit) 元組
    """
    page = max(1, page)
    page_size = min(page_size, settings.MAX_PAGE_SIZE)
    page_size = max(1, page_size)
    
    skip = (page - 1) * page_size
    return skip, page_size
