"""聯絡我們路由"""
from pathlib import Path
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.services.contact_service import ContactService

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent.parent / "templates"))

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def contact_page(request: Request, success: str = "", user=Depends(get_optional_current_user)):
    return templates.TemplateResponse("contact.html", {
        "request": request,
        "user": user,
        "success": success,
        "contact_email": settings.CONTACT_EMAIL,
        "contact_phone": settings.CONTACT_PHONE,
        "contact_address": settings.CONTACT_ADDRESS,
        "business_hours": settings.BUSINESS_HOURS,
        "instagram_url": settings.INSTAGRAM_URL,
    })

@router.post("/submit")
async def submit_contact(
    name: str = Form(...),
    person_type: str = Form("個人"),
    email: str = Form(...),
    phone: str = Form(...),
    message_type: str = Form("personal_feedback"),
    subject: str = Form(None),
    message: str = Form(...),
    db: Session = Depends(get_db),
    user=Depends(get_optional_current_user),
):
    ContactService.submit_message(
        db,
        name=name,
        email=email,
        phone=phone,
        message_type=message_type,
        message=f"身份：{person_type}\n{message}",
        user_id=user.id if user else None,
        subject=subject
    )
    return RedirectResponse(url="/contact?success=true", status_code=303)
