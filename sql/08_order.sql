-- 訂單表
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    user_id INT NOT NULL,
    buyer_name VARCHAR(100) NOT NULL,
    buyer_email VARCHAR(120) NOT NULL,
    buyer_phone VARCHAR(20) NOT NULL,
    buyer_address TEXT NOT NULL,
    total_price FLOAT NOT NULL,
    discount_amount FLOAT DEFAULT 0,
    tax_amount FLOAT DEFAULT 0,
    final_price FLOAT NOT NULL,
    status VARCHAR(50) DEFAULT 'Pending',
    payment_method VARCHAR(50),
    items JSON,
    payment_deadline DATETIME,
    paid_at DATETIME,
    shipped_at DATETIME,
    delivered_at DATETIME,
    cancelled_at DATETIME,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_order_number (order_number),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 訂單項目表
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    preorder_set_id INT NOT NULL,
    set_name VARCHAR(100) NOT NULL,
    quantity INT DEFAULT 1,
    unit_price FLOAT NOT NULL,
    subtotal FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (preorder_set_id) REFERENCES preorder_sets(id) ON DELETE RESTRICT,
    INDEX idx_order_id (order_id),
    INDEX idx_preorder_set_id (preorder_set_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
