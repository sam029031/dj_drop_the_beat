"""會員登入 / 註冊路由"""
from fastapi import APIRouter, Depends, Form, Request, Response, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.services.auth_service import AuthService
from app.schemas.auth import UserRegister

router = APIRouter(tags=["Authentication"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent.parent / "templates"))

@router.get("/login", response_class=HTMLResponse)
@router.get("/auth/login", response_class=HTMLResponse)
async def login_page(request: Request, next: str = "/", user=Depends(get_optional_current_user)):
    if user:
        return RedirectResponse(url=next or "/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "next": next, "user": user})

@router.post("/login")
@router.post("/auth/login")
async def login_submit(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    next: str = Form("/"),
    db: Session = Depends(get_db)
):
    try:
        user = AuthService.authenticate_user(db, username, password)
        token = AuthService.create_user_token(user)
        redirect = RedirectResponse(url=next or "/", status_code=303)
        redirect.set_cookie(
            key="session_id",
            value=token,
            httponly=True,
            max_age=86400 * 7,
            samesite="lax",
            path="/"
        )
        return redirect
    except ValueError as exc:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": str(exc), "next": next, "user": None},
            status_code=400
        )

@router.get("/register", response_class=HTMLResponse)
@router.get("/auth/register", response_class=HTMLResponse)
async def register_page(request: Request, user=Depends(get_optional_current_user)):
    if user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("register.html", {"request": request, "user": user})

@router.post("/register")
@router.post("/auth/register")
async def register_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(""),
    full_name: str = Form(None),
    phone: str = Form(None),
    address: str = Form(None),
    db: Session = Depends(get_db)
):
    try:
        if password_confirm and password != password_confirm:
            raise ValueError("兩次輸入的密碼不一致")
        user_data = UserRegister(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            phone=phone
        )
        user = AuthService.register_user(db, user_data, address=address)
        token = AuthService.create_user_token(user)
        redirect = RedirectResponse(url="/", status_code=303)
        redirect.set_cookie(
            key="session_id",
            value=token,
            httponly=True,
            max_age=86400 * 7,
            samesite="lax",
            path="/"
        )
        return redirect
    except Exception as exc:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": str(exc), "user": None},
            status_code=400
        )

@router.get("/logout")
@router.get("/auth/logout")
async def logout():
    redirect = RedirectResponse(url="/", status_code=303)
    redirect.delete_cookie("session_id", path="/")
    return redirect

@router.post("/api/login")
async def api_login(payload: dict, response: Response, db: Session = Depends(get_db)):
    try:
        user = AuthService.authenticate_user(db, payload.get("username", ""), payload.get("password", ""))
        token = AuthService.create_user_token(user)
        response.set_cookie("session_id", token, httponly=True, max_age=86400 * 7, samesite="lax", path="/")
        return {"access_token": token, "token_type": "bearer", "user": {"id": user.id, "username": user.username, "is_admin": user.is_admin}}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
