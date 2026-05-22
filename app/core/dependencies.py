"""依賴注入"""
from fastapi import Depends, HTTPException, status, Cookie
from sqlalchemy.orm import Session
from typing import Optional
import logging

from .database import get_db
from .security import verify_token
from ..models.user import User

logger = logging.getLogger(__name__)

def _user_from_cookie(session: Session, session_id: Optional[str]) -> Optional[User]:
    if not session_id:
        return None
    payload = verify_token(session_id)
    if not payload:
        return None
    user_id = payload.get("sub")
    try:
        user_id = int(user_id)
    except Exception:
        return None
    return session.query(User).filter(User.id == user_id, User.is_active == True).first()

def get_current_user(
    session: Session = Depends(get_db),
    session_id: Optional[str] = Cookie(None)
) -> User:
    user = _user_from_cookie(session, session_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登入或登入狀態已失效"
        )
    return user

def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限訪問，需要管理員帳號"
        )
    return current_user

def require_admin(current_user: User = Depends(get_current_admin)) -> User:
    return current_user

def get_optional_current_user(
    session: Session = Depends(get_db),
    session_id: Optional[str] = Cookie(None)
) -> Optional[User]:
    return _user_from_cookie(session, session_id)
