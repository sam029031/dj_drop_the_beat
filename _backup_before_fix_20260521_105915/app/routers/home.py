"""首頁路由。"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.models.user import User
from app.models.ddj import DDJ
from app.models.audio import Audio
from app.models.wire import Wire
from app.models.music import Music
from app.services.product_service import ProductService

router = APIRouter(tags=["Home"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[2] / "templates"))

@router.get("/", response_class=HTMLResponse)
async def get_home(
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_current_user),
):
    preorder_sets = ProductService.get_featured_preorder_sets(db, limit=3)
    latest_products = []
    for model, inst_type in [(DDJ, "ddj"), (Audio, "audio"), (Wire, "wire"), (Music, "music")]:
        latest_products.extend((p, inst_type) for p in db.query(model).order_by(model.id.asc()).limit(2).all())
    return templates.TemplateResponse("home.html", {
        "request": request,
        "user": user,
        "preorder_sets": preorder_sets,
        "latest_products": latest_products[:8],
    })
