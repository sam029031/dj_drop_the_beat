"""依賴注入。"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Cookie
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User

def _get_user_from_cookie(session: Session, session_id: Optional[str]) -> Optional[User]:
    if not session_id:
        return None
    payload = verify_token(session_id)
    if not payload:
        return None
    user_id = payload.get("sub")
    if user_id is None:
        return None
    return session.query(User).filter(User.id == int(user_id)).first()

def get_optional_current_user(
    session: Session = Depends(get_db),
    session_id: Optional[str] = Cookie(None),
) -> Optional[User]:
    return _get_user_from_cookie(session, session_id)

def get_current_user(
    session: Session = Depends(get_db),
    session_id: Optional[str] = Cookie(None),
) -> User:
    user = _get_user_from_cookie(session, session_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="請先登入")
    return user

def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理員權限")
    return current_user

# 舊程式碼相容名稱
require_admin = get_current_admin
