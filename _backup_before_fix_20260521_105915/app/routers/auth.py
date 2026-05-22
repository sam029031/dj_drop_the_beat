"""會員登入與註冊路由。"""
from fastapi import APIRouter, Depends, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import UserRegister

router = APIRouter(tags=["Authentication"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[2] / "templates"))

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "user": None})

@router.post("/login")
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        user = AuthService.authenticate_user(db, username, password)
        token = AuthService.create_user_token(user)
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie("session_id", token, httponly=True, max_age=86400 * 7, samesite="lax")
        return response
    except ValueError as exc:
        return templates.TemplateResponse("login.html", {"request": request, "error": str(exc), "user": None}, status_code=400)

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "user": None})

@router.post("/register")
async def register_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    full_name: str = Form(""),
    phone: str = Form(""),
    address: str = Form(""),
    db: Session = Depends(get_db),
):
    if password != password_confirm:
        return templates.TemplateResponse("register.html", {"request": request, "error": "兩次輸入的密碼不一致", "user": None}, status_code=400)
    try:
        data = UserRegister(username=username, email=email, password=password, full_name=full_name or None, phone=phone or None)
        user = AuthService.register_user(db, data)
        if address:
            user.address = address
            db.commit()
        token = AuthService.create_user_token(user)
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie("session_id", token, httponly=True, max_age=86400 * 7, samesite="lax")
        return response
    except Exception as exc:
        return templates.TemplateResponse("register.html", {"request": request, "error": str(exc), "user": None}, status_code=400)

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("session_id")
    return response

# 舊網址相容：避免模板或舊連結壞掉
@router.get("/auth/login")
async def old_login_redirect():
    return RedirectResponse(url="/login", status_code=303)

@router.get("/auth/register")
async def old_register_redirect():
    return RedirectResponse(url="/register", status_code=303)

@router.get("/auth/logout")
async def old_logout_redirect():
    return await logout()
