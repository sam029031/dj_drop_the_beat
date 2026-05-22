SET NAMES utf8mb4;

UPDATE preorder_sets
SET
    name = '初級 DJ SET',
    set_type = 'Starter',
    description = '適合 DJ 初學者的入門組合，包含 DJ 控制器與基礎線材，適合第一次接觸 DJ 的使用者。',
    included_items = '[{"category":"ddj","product_id":3,"quantity":1},{"category":"wire","product_id":1,"quantity":1}]',
    price = 29999,
    discount_price = 27999,
    is_featured = TRUE,
    is_active = TRUE
WHERE id = 1;

UPDATE preorder_sets
SET
    name = '進階 DJ SET',
    set_type = 'Intermediate',
    description = '適合已具備基礎技巧的使用者，包含 DJ 控制器、監聽喇叭與線材，適合練習與小型演出。',
    included_items = '[{"category":"ddj","product_id":2,"quantity":1},{"category":"audio","product_id":1,"quantity":1},{"category":"wire","product_id":1,"quantity":2}]',
    price = 59999,
    discount_price = 54999,
    is_featured = TRUE,
    is_active = TRUE
WHERE id = 2;

UPDATE preorder_sets
SET
    name = '專業完整 DJ SET',
    set_type = 'Professional',
    description = '專業級完整組合，包含高階 DJ 控制器、監聽喇叭、線材與音樂大禮包，適合進階演出與完整練習環境。',
    included_items = '[{"category":"ddj","product_id":1,"quantity":1},{"category":"audio","product_id":1,"quantity":2},{"category":"wire","product_id":1,"quantity":3},{"category":"music","product_id":1,"quantity":1}]',
    price = 99999,
    discount_price = 89999,
    is_featured = TRUE,
    is_active = TRUE
WHERE id = 3;