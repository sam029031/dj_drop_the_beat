"""課程路由"""
from pathlib import Path

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.models.user import User
from app.models.course import Course
from app.services.course_service import CourseService

router = APIRouter()
TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def difficulty_rank(value: str) -> int:
    value = (value or "").lower()
    order = {
        "beginner": 1,
        "初級": 1,
        "intermediate": 2,
        "中級": 2,
        "advanced": 3,
        "進階": 3,
    }
    return order.get(value, 99)


@router.get("", response_class=HTMLResponse)
async def course_list(
    request: Request,
    page: int = 1,
    sort: str = "created",
    db: Session = Depends(get_db),
):
    query = db.query(Course).filter(Course.is_active == True)

    if sort == "difficulty":
        courses_all = query.order_by(Course.created_at.desc()).all()
        courses_all.sort(key=lambda course: difficulty_rank(course.difficulty))
    else:
        courses_all = query.order_by(Course.created_at.desc()).all()

    total = len(courses_all)
    start = (page - 1) * 12
    courses = courses_all[start:start + 12]

    return templates.TemplateResponse(
        "course_list.html",
        {
            "request": request,
            "courses": courses,
            "page": page,
            "total_pages": (total + 11) // 12,
            "sort": sort,
        },
    )


@router.get("/detail", response_class=HTMLResponse)
async def course_detail(
    request: Request,
    id: int = 1,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    course = db.query(Course).filter(Course.id == id).first()
    if not course:
        return templates.TemplateResponse("404.html", {"request": request})

    return templates.TemplateResponse(
        "course_detail.html",
        {
            "request": request,
            "course": course,
            "user": current_user,
            "error": request.query_params.get("error"),
            "registered": request.query_params.get("registered"),
        },
    )


@router.post("/register")
async def register_course(
    request: Request,
    course_id: int = Form(...),
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    notes: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    user_id = current_user.id if current_user else None

    try:
        registration = CourseService.register_course(
            db=db,
            user_id=user_id,
            course_id=course_id,
            name=name,
            email=email,
            phone=phone,
            notes=notes or None,
        )
    except Exception as exc:
        return RedirectResponse(
            url=f"/course/detail?id={course_id}&error={str(exc)}#form",
            status_code=303,
        )

    return RedirectResponse(
        url=f"/course/detail?id={course_id}&registered={registration.registration_number}#form",
        status_code=303,
    )
