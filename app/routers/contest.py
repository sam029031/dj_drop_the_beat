"""比賽路由"""
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.models.user import User
from app.models.contest import Contest
from app.services.contest_service import ContestService

router = APIRouter()
TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _naive(dt):
    if dt is None:
        return None
    if getattr(dt, "tzinfo", None) is not None:
        return dt.replace(tzinfo=None)
    return dt


def _now():
    return datetime.now()


def _can_register(contest: Contest, now: datetime) -> bool:
    deadline = _naive(contest.registration_deadline)
    event_date = _naive(contest.event_date)
    if not contest.is_active:
        return False
    if deadline is None or event_date is None:
        return False
    if event_date < now:
        return False
    if deadline < now:
        return False
    if contest.current_participants >= contest.max_participants:
        return False
    return True


@router.get("", response_class=HTMLResponse)
async def contest_list(
    request: Request,
    page: int = 1,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    now = _now()

    all_contests = (
        db.query(Contest)
        .filter(Contest.is_active == True)
        .order_by(Contest.event_date.asc())
        .all()
    )

    valid_contests = []
    for contest in all_contests:
        event_date = _naive(contest.event_date)
        if event_date is None or event_date < now:
            continue
        contest.can_register = _can_register(contest, now)
        valid_contests.append(contest)

    total = len(valid_contests)
    start = (page - 1) * 12
    contests = valid_contests[start:start + 12]

    return templates.TemplateResponse(
        "contest_list.html",
        {
            "request": request,
            "contests": contests,
            "page": page,
            "total_pages": (total + 11) // 12,
            "user": current_user,
        },
    )


@router.get("/detail", response_class=HTMLResponse)
async def contest_detail(
    request: Request,
    id: int = 1,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    contest = db.query(Contest).filter(Contest.id == id).first()
    if not contest:
        return templates.TemplateResponse("404.html", {"request": request})

    now = _now()
    contest.can_register = _can_register(contest, now)
    is_registration_closed = not contest.can_register

    return templates.TemplateResponse(
        "contest_detail.html",
        {
            "request": request,
            "contest": contest,
            "user": current_user,
            "is_registration_closed": is_registration_closed,
            "error": request.query_params.get("error"),
            "registered": request.query_params.get("registered"),
        },
    )


@router.post("/register")
async def register_contest(
    request: Request,
    contest_id: int = Form(...),
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    dj_name: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    user_id = current_user.id if current_user else None

    try:
        registration = ContestService.register_contest(
            db=db,
            user_id=user_id,
            contest_id=contest_id,
            name=name,
            email=email,
            phone=phone,
            dj_name=dj_name or None,
            notes=notes or None,
        )
    except Exception as exc:
        return RedirectResponse(
            url=f"/contest/detail?id={contest_id}&error={str(exc)}#form",
            status_code=303,
        )

    return RedirectResponse(
        url=f"/contest/detail?id={contest_id}&registered={registration.registration_number}#form",
        status_code=303,
    )
