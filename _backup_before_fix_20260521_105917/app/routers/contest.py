"""比賽路由。"""
from datetime import datetime
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.models.user import User
from app.models.contest import Contest
from app.services.contest_service import ContestService

router = APIRouter(prefix="/contest", tags=["Contest"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[2] / "templates"))

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def contest_list(request: Request, page: int = 1, db: Session = Depends(get_db), user: User | None = Depends(get_optional_current_user)):
    now = datetime.utcnow()
    query = db.query(Contest).filter(Contest.is_active == True, Contest.event_date > now).order_by(Contest.event_date.asc())
    total = query.count()
    contests = query.offset((page - 1) * 12).limit(12).all()
    return templates.TemplateResponse("contest_list.html", {"request": request, "user": user, "contests": contests, "page": page, "total_pages": (total + 11) // 12, "now": now})

@router.get("/detail", response_class=HTMLResponse)
async def contest_detail(request: Request, id: int, db: Session = Depends(get_db), user: User | None = Depends(get_optional_current_user)):
    contest = db.query(Contest).filter(Contest.id == id).first()
    if not contest:
        return templates.TemplateResponse("404.html", {"request": request, "user": user}, status_code=404)
    now = datetime.utcnow()
    is_registration_closed = contest.registration_deadline < now
    return templates.TemplateResponse("contest_detail.html", {"request": request, "user": user, "contest": contest, "is_registration_closed": is_registration_closed})

@router.post("/register")
async def register_contest(request: Request, db: Session = Depends(get_db), user: User | None = Depends(get_optional_current_user)):
    form_data = await request.form()
    contest_id = int(form_data.get("contest_id"))
    registration = ContestService.register_contest(
        db=db,
        user_id=user.id if user else None,
        contest_id=contest_id,
        name=form_data.get("name"),
        email=form_data.get("email"),
        phone=form_data.get("phone"),
        notes=form_data.get("notes"),
    )
    return RedirectResponse(url=f"/contest/detail?id={contest_id}&registered={registration.registration_number}", status_code=303)
