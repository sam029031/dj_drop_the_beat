"""商品業務邏輯"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.preorder_set import PreorderSet
from app.models.ddj import DDJ
from app.models.audio import Audio
from app.models.wire import Wire
from app.models.music import Music

MODEL_MAP = {
    "dj": DDJ,
    "ddj": DDJ,
    "audio": Audio,
    "wire": Wire,
    "music": Music,
}

class ProductService:
    @staticmethod
    def get_featured_preorder_sets(db: Session, limit: int = 3) -> list:
        return db.query(PreorderSet).filter(
            PreorderSet.is_featured == True,
            PreorderSet.is_active == True
        ).order_by(PreorderSet.sort_order.asc(), PreorderSet.id.asc()).limit(limit).all()

    @staticmethod
    def get_all_preorder_sets(db: Session, page: int = 1, page_size: int = 20) -> tuple:
        skip = (page - 1) * page_size
        query = db.query(PreorderSet).filter(PreorderSet.is_active == True)
        total = query.count()
        sets = query.order_by(PreorderSet.sort_order.asc(), PreorderSet.id.asc()).offset(skip).limit(page_size).all()
        return sets, total

    @staticmethod
    def get_preorder_set_by_id(db: Session, set_id: int) -> PreorderSet | None:
        return db.query(PreorderSet).filter(
            PreorderSet.id == set_id,
            PreorderSet.is_active == True
        ).first()

    @staticmethod
    def get_product(db: Session, instrument: str, product_id: int):
        model = MODEL_MAP.get((instrument or "ddj").lower())
        if not model:
            return None
        return db.query(model).filter(model.id == product_id).first()

    @staticmethod
    def search_products(db: Session, query: str = "", category: str | None = None,
                        brand: str = "", price_min: float = 0, price_max: float = 999999) -> list:
        models = [MODEL_MAP[category]] if category in MODEL_MAP else [DDJ, Audio, Wire, Music]
        results = []
        for model in models:
            q = db.query(model)
            if query:
                if model is Music:
                    q = q.filter(or_(Music.title.ilike(f"%{query}%"), Music.artist.ilike(f"%{query}%"), Music.description.ilike(f"%{query}%")))
                else:
                    q = q.filter(or_(model.name.ilike(f"%{query}%"), model.description.ilike(f"%{query}%")))
            if brand and hasattr(model, "brand"):
                q = q.filter(model.brand.ilike(f"%{brand}%"))
            if hasattr(model, "price"):
                q = q.filter(model.price >= price_min, model.price <= price_max)
            inst = "music" if model is Music else model.__tablename__
            for item in q.all():
                results.append((item, inst))
        return results
