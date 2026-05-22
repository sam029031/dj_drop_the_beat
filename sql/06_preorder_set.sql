-- 預購 SET 表
CREATE TABLE IF NOT EXISTS preorder_sets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    set_type VARCHAR(50) NOT NULL,
    price FLOAT NOT NULL,
    discount_price FLOAT,
    description TEXT,
    included_items JSON,
    total_quantity INT DEFAULT 50,
    available_quantity INT DEFAULT 50,
    ordered_quantity INT DEFAULT 0,
    image_url VARCHAR(255),
    is_featured BOOLEAN DEFAULT FALSE,
    sort_order INT DEFAULT 0,
    preorder_deadline DATETIME,
    estimated_delivery DATETIME,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_set_type (set_type),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入示例預購 SET
INSERT INTO preorder_sets (name, set_type, price, discount_price, description, included_items, available_quantity, sort_order, is_featured, is_active) VALUES
('初級 DJ SET', 'Starter', 29999, 27999, '適合 DJ 初學者，包含控制器和耳機', '[{"category":"ddj","product_id":3,"quantity":1},{"category":"audio","product_id":2,"quantity":1},{"category":"wire","product_id":1,"quantity":2}]', 20, 1, TRUE, TRUE),
('中級專業 SET', 'Intermediate', 59999, 54999, '進階 DJ 必備套組，包含混音機和音響', '[{"category":"ddj","product_id":2,"quantity":1},{"category":"audio","product_id":1,"quantity":1},{"category":"audio","product_id":3,"quantity":1}]', 15, 2, TRUE, TRUE),
('專業完整 SET', 'Professional', 99999, 89999, '專業級 DJ 完整解決方案', '[{"category":"ddj","product_id":1,"quantity":1},{"category":"audio","product_id":1,"quantity":2},{"category":"audio","product_id":3,"quantity":1},{"category":"wire","product_id":1,"quantity":3}]', 10, 3, FALSE, TRUE);