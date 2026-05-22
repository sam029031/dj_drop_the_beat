"""聯絡我們路由。"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.models.user import User
from app.services.contact_service import ContactService
from app.core.config import settings

router = APIRouter(prefix="/contact", tags=["Contact"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[2] / "templates"))

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def contact_page(request: Request, success: bool = False, user: User | None = Depends(get_optional_current_user)):
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
async def submit_contact(request: Request, db: Session = Depends(get_db), user: User | None = Depends(get_optional_current_user)):
    form_data = await request.form()
    contact_method = form_data.get("contact_method") or form_data.get("email") or form_data.get("phone") or "未提供"
    message_type = form_data.get("message_type") or "personal_feedback"
    unit_or_person = form_data.get("unit_or_person") or "個人"
    ContactService.create_contact_message(
        db=db,
        name=form_data.get("name"),
        email=contact_method if "@" in contact_method else f"no-email-{contact_method}@local.invalid",
        phone=contact_method,
        message_type=message_type,
        subject=unit_or_person,
        message=form_data.get("message"),
    )
    return RedirectResponse(url="/contact?success=true", status_code=303)
