"""首頁路由"""
from pathlib import Path
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.services.product_service import ProductService
from app.models.ddj import DDJ
from app.models.audio import Audio
from app.models.wire import Wire
from app.models.music import Music

router = APIRouter(tags=["Home"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent.parent / "templates"))

@router.get("/", response_class=HTMLResponse)
async def get_home(request: Request, db: Session = Depends(get_db), user=Depends(get_optional_current_user)):
    preorder_sets = ProductService.get_featured_preorder_sets(db, limit=3)
    latest_products = []
    for model, instrument in [(DDJ, "ddj"), (Audio, "audio"), (Wire, "wire"), (Music, "music")]:
        rows = db.query(model).order_by(model.id.asc()).limit(2).all()
        latest_products.extend([(row, instrument) for row in rows])
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "user": user,
            "preorder_sets": preorder_sets,
            "latest_products": latest_products,
        }
    )
