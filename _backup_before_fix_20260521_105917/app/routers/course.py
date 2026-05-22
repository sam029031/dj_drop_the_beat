"""課程路由。"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.models.user import User
from app.models.course import Course
from app.services.course_service import CourseService

router = APIRouter(prefix="/course", tags=["Course"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[2] / "templates"))

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def course_list(request: Request, page: int = 1, db: Session = Depends(get_db), user: User | None = Depends(get_optional_current_user)):
    query = db.query(Course).filter(Course.is_active == True).order_by(Course.created_at.desc(), Course.difficulty.asc())
    total = query.count()
    courses = query.offset((page - 1) * 12).limit(12).all()
    return templates.TemplateResponse("course_list.html", {"request": request, "user": user, "courses": courses, "page": page, "total_pages": (total + 11) // 12})

@router.get("/detail", response_class=HTMLResponse)
async def course_detail(request: Request, id: int, db: Session = Depends(get_db), user: User | None = Depends(get_optional_current_user)):
    course = db.query(Course).filter(Course.id == id).first()
    if not course:
        return templates.TemplateResponse("404.html", {"request": request, "user": user}, status_code=404)
    return templates.TemplateResponse("course_detail.html", {"request": request, "user": user, "course": course})

@router.post("/register")
async def register_course(request: Request, db: Session = Depends(get_db), user: User | None = Depends(get_optional_current_user)):
    form_data = await request.form()
    course_id = int(form_data.get("course_id"))
    registration = CourseService.register_course(
        db=db,
        user_id=user.id if user else None,
        course_id=course_id,
        name=form_data.get("name"),
        email=form_data.get("email"),
        phone=form_data.get("phone"),
        notes=form_data.get("notes"),
    )
    return RedirectResponse(url=f"/course/detail?id={course_id}&registered={registration.registration_number}", status_code=303)
