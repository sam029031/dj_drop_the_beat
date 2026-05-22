"""商品業務邏輯。"""
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.preorder_set import PreorderSet
from app.models.ddj import DDJ
from app.models.audio import Audio
from app.models.wire import Wire
from app.models.music import Music

class ProductService:
    MODEL_MAP = {
        "dj": DDJ,
        "ddj": DDJ,
        "audio": Audio,
        "wire": Wire,
        "music": Music,
    }

    @staticmethod
    def get_featured_preorder_sets(db: Session, limit: int = 3) -> list[PreorderSet]:
        return (
            db.query(PreorderSet)
            .filter(PreorderSet.is_active == True)
            .order_by(PreorderSet.sort_order.asc(), PreorderSet.id.asc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_all_preorder_sets(db: Session, page: int = 1, page_size: int = 20) -> tuple[list[PreorderSet], int]:
        skip = (page - 1) * page_size
        query = db.query(PreorderSet).filter(PreorderSet.is_active == True)
        total = query.count()
        sets = query.order_by(PreorderSet.sort_order.asc(), PreorderSet.id.asc()).offset(skip).limit(page_size).all()
        return sets, total

    @staticmethod
    def get_preorder_set_by_id(db: Session, set_id: int) -> PreorderSet | None:
        return db.query(PreorderSet).filter(PreorderSet.id == set_id, PreorderSet.is_active == True).first()

    @staticmethod
    def get_product(db: Session, instrument: str, product_id: int):
        model = ProductService.MODEL_MAP.get(instrument, DDJ)
        return db.query(model).filter(model.id == product_id).first()

    @staticmethod
    def search_products(db: Session, q: str = "", instrument: str = "", brand: str = "", price_min: float = 0, price_max: float = 999999) -> list[tuple[object, str]]:
        selected = [instrument] if instrument in ProductService.MODEL_MAP else ["ddj", "audio", "wire", "music"]
        results = []
        for key in selected:
            model = ProductService.MODEL_MAP[key]
            query = db.query(model)
            if q:
                if key == "music":
                    query = query.filter(or_(Music.title.ilike(f"%{q}%"), Music.artist.ilike(f"%{q}%"), Music.description.ilike(f"%{q}%")))
                else:
                    query = query.filter(or_(model.name.ilike(f"%{q}%"), model.description.ilike(f"%{q}%")))
            if brand and hasattr(model, "brand"):
                query = query.filter(model.brand.ilike(f"%{brand}%"))
            query = query.filter(model.price >= price_min, model.price <= price_max)
            results.extend((item, key) for item in query.all())
        return results
