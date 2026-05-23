"""管理後台路由"""
import csv
import io
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.models.ddj import DDJ
from app.models.audio import Audio
from app.models.wire import Wire
from app.models.music import Music
from app.models.order import Order
from app.models.course import Course, CourseRegistration
from app.models.contest import Contest, ContestRegistration

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent.parent / "templates"))

PRODUCT_MODELS = {"ddj": DDJ, "audio": Audio, "wire": Wire, "music": Music}

def _product_fields(model, form):
    data = {
        "price": float(form.get("price") or 0),
        "description": form.get("description") or "",
        "in_stock": int(form.get("stock") or form.get("in_stock") or 0),
        "preorder_available": int(form.get("preorder_available") or 0),
        "image_url": form.get("image_url") or None,
    }
    if model is Music:
        data["title"] = form.get("name") or form.get("title") or ""
        data["artist"] = form.get("artist") or "Unknown"
        data["genre"] = form.get("genre") or form.get("brand") or "Other"
    else:
        data["name"] = form.get("name") or ""
        if hasattr(model, "brand"):
            data["brand"] = form.get("brand") or "Other"
    if model is DDJ:
        data["model"] = form.get("model") or data["name"]
        data["channels"] = int(form.get("channels") or 2)
        data["effects_count"] = int(form.get("effects_count") or 8)
    if model is Audio:
        data["audio_type"] = form.get("audio_type") or "Speaker"
        data["watts"] = int(form.get("watts") or 0)
    if model is Wire:
        data["wire_type"] = form.get("wire_type") or "Cable"
        data["length_meters"] = float(form.get("length_meters") or 1)
    return data

# ============ 儀表板 ============

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    stats = {
        "products": sum(db.query(model).count() for model in PRODUCT_MODELS.values()),
        "orders": db.query(Order).count(),
        "courses": db.query(Course).count(),
        "contests": db.query(Contest).count(),
    }
    return templates.TemplateResponse("admin.html", {"request": request, "user": current_user, "stats": stats})

# ============ 商品 ============

@router.get("/products", response_class=HTMLResponse)
async def admin_products(request: Request, instrument: str = "ddj", current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    model = PRODUCT_MODELS.get(instrument, DDJ)
    products = db.query(model).order_by(model.id.desc()).all()
    return templates.TemplateResponse("admin_products.html", {
        "request": request,
        "user": current_user,
        "instrument": instrument,
        "products": products,
    })

@router.post("/products/create")
async def admin_product_create(request: Request, instrument: str = Form("ddj"), current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    form = await request.form()
    model = PRODUCT_MODELS.get(instrument, DDJ)
    obj = model(**_product_fields(model, form))
    db.add(obj)
    db.commit()
    return RedirectResponse(url=f"/admin/products?instrument={instrument}", status_code=303)

@router.post("/products/{instrument}/{product_id}/edit")
async def admin_product_edit(request: Request, instrument: str, product_id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    form = await request.form()
    model = PRODUCT_MODELS.get(instrument)
    if not model:
        raise HTTPException(404)
    obj = db.query(model).filter(model.id == product_id).first()
    if not obj:
        raise HTTPException(404)
    for key, value in _product_fields(model, form).items():
        if hasattr(obj, key):
            setattr(obj, key, value)
    db.commit()
    return RedirectResponse(url=f"/admin/products?instrument={instrument}", status_code=303)

@router.post("/products/{instrument}/{product_id}/delete")
async def admin_product_delete(instrument: str, product_id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    model = PRODUCT_MODELS.get(instrument)
    if not model:
        raise HTTPException(404)
    obj = db.query(model).filter(model.id == product_id).first()
    if obj:
        db.delete(obj)
        db.commit()
    return RedirectResponse(url=f"/admin/products?instrument={instrument}", status_code=303)

# ============ 訂單 ============

@router.get("/orders", response_class=HTMLResponse)
async def admin_orders(request: Request, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    orders = db.query(Order).order_by(Order.created_at.desc()).all()
    return templates.TemplateResponse("admin_orders.html", {"request": request, "user": current_user, "orders": orders})

@router.get("/orders/{order_id}")
async def admin_order_detail(order_id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404)
    return {
        "id": order.id,
        "order_number": order.order_number,
        "buyer_name": order.buyer_name,
        "buyer_email": order.buyer_email,
        "buyer_phone": order.buyer_phone,
        "final_price": order.final_price,
        "status": order.status,
        "items": order.items,
    }

@router.post("/orders/{order_id}/status")
async def admin_order_status(order_id: int, status: str = Form(...), current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.status = status
        db.commit()
    return RedirectResponse(url="/admin/orders", status_code=303)

# ============ 課程 ============

@router.get("/courses", response_class=HTMLResponse)
async def admin_courses(request: Request, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    courses = db.query(Course).order_by(Course.created_at.desc()).all()
    return templates.TemplateResponse("admin_courses.html", {"request": request, "user": current_user, "courses": courses})

@router.post("/courses/{course_id}/edit")
async def admin_course_edit(
    course_id: int,
    title: str = Form(...),
    difficulty: str = Form(...),
    duration_hours: float = Form(...),
    instructor: str = Form(...),
    prerequisites: str = Form(""),
    price: float = Form(...),
    syllabus: str = Form(""),
    description: str = Form(""),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(404)
    course.title = title
    course.difficulty = difficulty
    course.duration_hours = duration_hours
    course.instructor = instructor
    course.prerequisites = prerequisites or None
    course.price = price
    course.syllabus = syllabus or None
    course.description = description or None
    db.commit()
    return RedirectResponse(url="/admin/courses", status_code=303)

@router.post("/courses/{course_id}/delete")
async def admin_course_delete(course_id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if course:
        db.delete(course)
        db.commit()
    return RedirectResponse(url="/admin/courses", status_code=303)

@router.get("/courses/{course_id}/registrations/export")
async def export_course_registrations(course_id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    regs = db.query(CourseRegistration).filter(CourseRegistration.course_id == course_id).order_by(CourseRegistration.registered_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["名字", "電子郵件", "電話", "備註"])
    for r in regs:
        writer.writerow([r.name, r.email, r.phone, r.notes or ""])
    content = ("﻿" + output.getvalue()).encode("utf-8")
    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=course_{course_id}_registrations.csv"},
    )

@router.get("/courses/{course_id}/registrations", response_class=HTMLResponse)
async def admin_course_registrations(request: Request, course_id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(404)
    regs = db.query(CourseRegistration).filter(CourseRegistration.course_id == course_id).order_by(CourseRegistration.registered_at.desc()).all()
    return templates.TemplateResponse("admin_course_registrations.html", {
        "request": request,
        "user": current_user,
        "course": course,
        "registrations": regs,
    })

@router.post("/courses/{course_id}/registrations/{reg_id}/delete")
async def admin_course_registration_delete(course_id: int, reg_id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    reg = db.query(CourseRegistration).filter(CourseRegistration.id == reg_id, CourseRegistration.course_id == course_id).first()
    if reg:
        db.delete(reg)
        db.commit()
    return RedirectResponse(url=f"/admin/courses/{course_id}/registrations", status_code=303)

# ============ 比賽 ============

@router.get("/contests", response_class=HTMLResponse)
async def admin_contests(request: Request, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    contests = db.query(Contest).order_by(Contest.event_date.desc()).all()
    return templates.TemplateResponse("admin_contests.html", {"request": request, "user": current_user, "contests": contests})

@router.post("/contests/{contest_id}/edit")
async def admin_contest_edit(
    contest_id: int,
    title: str = Form(...),
    venue: str = Form(...),
    prize_pool: float = Form(0),
    registration_start: str = Form(...),
    registration_deadline: str = Form(...),
    event_date: str = Form(...),
    description: str = Form(""),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(404)
    contest.title = title
    contest.venue = venue
    contest.prize_pool = prize_pool
    contest.registration_start = datetime.fromisoformat(registration_start)
    contest.registration_deadline = datetime.fromisoformat(registration_deadline)
    contest.event_date = datetime.fromisoformat(event_date)
    contest.description = description or None
    db.commit()
    return RedirectResponse(url="/admin/contests", status_code=303)

@router.post("/contests/{contest_id}/delete")
async def admin_contest_delete(contest_id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if contest:
        db.delete(contest)
        db.commit()
    return RedirectResponse(url="/admin/contests", status_code=303)

@router.get("/contests/{contest_id}/registrations/export")
async def export_contest_registrations(contest_id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    regs = db.query(ContestRegistration).filter(ContestRegistration.contest_id == contest_id).order_by(ContestRegistration.registered_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["名字", "電子郵件", "電話", "DJ 藝名", "備註"])
    for r in regs:
        writer.writerow([r.name, r.email, r.phone, r.dj_name or "", r.notes or ""])
    content = ("﻿" + output.getvalue()).encode("utf-8")
    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=contest_{contest_id}_registrations.csv"},
    )

@router.get("/contests/{contest_id}/registrations", response_class=HTMLResponse)
async def admin_contest_registrations(request: Request, contest_id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(404)
    regs = db.query(ContestRegistration).filter(ContestRegistration.contest_id == contest_id).order_by(ContestRegistration.registered_at.desc()).all()
    return templates.TemplateResponse("admin_contest_registrations.html", {
        "request": request,
        "user": current_user,
        "contest": contest,
        "registrations": regs,
    })

@router.post("/contests/{contest_id}/registrations/{reg_id}/delete")
async def admin_contest_registration_delete(contest_id: int, reg_id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    reg = db.query(ContestRegistration).filter(ContestRegistration.id == reg_id, ContestRegistration.contest_id == contest_id).first()
    if reg:
        db.delete(reg)
        db.commit()
    return RedirectResponse(url=f"/admin/contests/{contest_id}/registrations", status_code=303)
