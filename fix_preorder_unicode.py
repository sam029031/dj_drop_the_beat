from app.core.database import SessionLocal
from app.models.preorder_set import PreorderSet

db = SessionLocal()

data = [
    {
        "id": 1,
        "name": "初級 DJ SET",
        "set_type": "Starter",
        "description": "適合 DJ 初學者的入門組合，包含 DJ 控制器與基礎線材，適合第一次接觸 DJ 的使用者。",
        "included_items": '[{"category":"ddj","product_id":3,"quantity":1},{"category":"wire","product_id":1,"quantity":1}]',
        "price": 29999,
        "discount_price": 27999,
    },
    {
        "id": 2,
        "name": "進階 DJ SET",
        "set_type": "Intermediate",
        "description": "適合已具備基礎技巧的使用者，包含 DJ 控制器、監聽喇叭與線材，適合練習與小型演出。",
        "included_items": '[{"category":"ddj","product_id":2,"quantity":1},{"category":"audio","product_id":1,"quantity":1},{"category":"wire","product_id":1,"quantity":2}]',
        "price": 59999,
        "discount_price": 54999,
    },
    {
        "id": 3,
        "name": "專業完整 DJ SET",
        "set_type": "Professional",
        "description": "專業級完整組合，包含高階 DJ 控制器、監聽喇叭、線材與音樂大禮包，適合進階演出與完整練習環境。",
        "included_items": '[{"category":"ddj","product_id":1,"quantity":1},{"category":"audio","product_id":1,"quantity":2},{"category":"wire","product_id":1,"quantity":3},{"category":"music","product_id":1,"quantity":1}]',
        "price": 99999,
        "discount_price": 89999,
    },
]

for item in data:
    row = db.query(PreorderSet).filter(PreorderSet.id == item["id"]).first()

    if row is None:
        row = PreorderSet(
            id=item["id"],
            total_quantity=100,
            available_quantity=100,
            ordered_quantity=0,
            image_url=None,
            is_featured=True,
            sort_order=item["id"],
            is_active=True,
        )
        db.add(row)

    row.name = item["name"]
    row.set_type = item["set_type"]
    row.description = item["description"]
    row.included_items = item["included_items"]
    row.price = item["price"]
    row.discount_price = item["discount_price"]
    row.is_featured = True
    row.is_active = True

db.commit()

rows = db.query(PreorderSet).order_by(PreorderSet.id).all()
for row in rows:
    print(row.id, row.name, row.description)

db.close()
print("preorder_sets 中文已修正")