"""管理後台路由。"""
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.user import User
from app.models.ddj import DDJ
from app.models.audio import Audio
from app.models.wire import Wire
from app.models.music import Music
from app.models.order import Order
from app.models.course import Course, CourseRegistration
from app.models.contest import Contest, ContestRegistration

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[2] / "templates"))
MODEL_MAP = {"ddj": DDJ, "audio": Audio, "wire": Wire, "music": Music}

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    stats = {"products": sum(db.query(m).count() for m in MODEL_MAP.values()), "orders": db.query(Order).count(), "courses": db.query(Course).count(), "contests": db.query(Contest).count()}
    return templates.TemplateResponse("admin.html", {"request": request, "user": current_user, "stats": stats})

@router.get("/products", response_class=HTMLResponse)
async def admin_products(request: Request, instrument: str = "ddj", current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    model = MODEL_MAP.get(instrument, DDJ)
    products = db.query(model).order_by(model.id.desc()).all()
    return templates.TemplateResponse("admin_products.html", {"request": request, "user": current_user, "instrument": instrument, "products": products})

@router.post("/products/create")
async def create_product(instrument: str = Form(...), name: str = Form(...), description: str = Form(""), price: float = Form(...), stock: int = Form(0), brand: str = Form("Other"), db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    model = MODEL_MAP.get(instrument, DDJ)
    if instrument == "music":
        item = Music(title=name, artist=brand or "Various", genre="Other", price=price, description=description, in_stock=stock)
    elif instrument == "audio":
        item = Audio(name=name, audio_type="Speaker", brand=brand or "Other", price=price, description=description, in_stock=stock)
    elif instrument == "wire":
        item = Wire(name=name, wire_type="Other", brand=brand or "Other", price=price, description=description, in_stock=stock)
    else:
        item = DDJ(name=name, brand=brand or "Other", model=name, price=price, description=description, in_stock=stock)
    db.add(item)
    db.commit()
    return RedirectResponse(url=f"/admin/products?instrument={instrument}", status_code=303)

@router.post("/products/{instrument}/{product_id}/update")
async def update_product(
    instrument: str,
    product_id: int,
    name: str = Form(...),
    description: str = Form(""),
    price: float = Form(...),
    stock: int = Form(0),
    brand: str = Form("Other"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    model = MODEL_MAP.get(instrument, DDJ)
    item = db.query(model).filter(model.id == product_id).first()
    if item:
        if instrument == "music":
            item.title = name
            item.artist = brand or item.artist
        else:
            item.name = name
            if hasattr(item, "brand"):
                item.brand = brand or item.brand
        item.description = description
        item.price = price
        if hasattr(item, "in_stock"):
            item.in_stock = stock
        db.commit()
    return RedirectResponse(url=f"/admin/products?instrument={instrument}", status_code=303)

@router.post("/products/{instrument}/{product_id}/delete")
async def delete_product(instrument: str, product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    model = MODEL_MAP.get(instrument, DDJ)
    item = db.query(model).filter(model.id == product_id).first()
    if item:
        db.delete(item)
        db.commit()
    return RedirectResponse(url=f"/admin/products?instrument={instrument}", status_code=303)

@router.get("/orders", response_class=HTMLResponse)
async def admin_orders(request: Request, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    orders = db.query(Order).order_by(Order.created_at.desc()).all()
    return templates.TemplateResponse("admin_orders.html", {"request": request, "user": current_user, "orders": orders})

@router.get("/courses", response_class=HTMLResponse)
async def admin_courses(request: Request, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    courses = db.query(Course).order_by(Course.created_at.desc()).all()
    return templates.TemplateResponse("admin_courses.html", {"request": request, "user": current_user, "courses": courses})

@router.get("/courses/{course_id}/registrations", response_class=HTMLResponse)
async def admin_course_registrations(request: Request, course_id: int, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    registrations = db.query(CourseRegistration).filter(CourseRegistration.course_id == course_id).all()
    return templates.TemplateResponse("admin_courses.html", {"request": request, "user": current_user, "courses": db.query(Course).all(), "selected_course": course, "registrations": registrations})

@router.get("/contests", response_class=HTMLResponse)
async def admin_contests(request: Request, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    contests = db.query(Contest).order_by(Contest.event_date.desc()).all()
    return templates.TemplateResponse("admin_contests.html", {"request": request, "user": current_user, "contests": contests})

@router.get("/contests/{contest_id}/registrations", response_class=HTMLResponse)
async def admin_contest_registrations(request: Request, contest_id: int, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    registrations = db.query(ContestRegistration).filter(ContestRegistration.contest_id == contest_id).all()
    return templates.TemplateResponse("admin_contests.html", {"request": request, "user": current_user, "contests": db.query(Contest).all(), "selected_contest": contest, "registrations": registrations})
