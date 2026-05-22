-- DJ 控制器表 (DDJ)
CREATE TABLE IF NOT EXISTS ddj (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    brand VARCHAR(50),
    model VARCHAR(50) NOT NULL,
    price FLOAT NOT NULL,
    description TEXT,
    channels INT DEFAULT 2,
    effects_count INT DEFAULT 8,
    jog_wheels INT DEFAULT 2,
    faders INT DEFAULT 3,
    image_url VARCHAR(255),
    category VARCHAR(50) DEFAULT 'ddj',
    in_stock INT DEFAULT 0,
    preorder_available INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_brand (brand)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入示例 DJ 控制器
INSERT INTO ddj (name, brand, model, price, description, channels, effects_count, category, preorder_available) VALUES
('Pioneer DDJ-800', 'Pioneer', 'DDJ-800', 19999, '專業 2 頻道 DJ 控制器，適合進階 DJ', 2, 8, 'ddj', 5),
('Numark Mixtrack Pro 3', 'Numark', 'Mixtrack Pro 3', 12999, '中階 DJ 控制器，初學者推薦', 2, 4, 'ddj', 8),
('Reloop Beatmix 2', 'Reloop', 'Beatmix 2', 9999, '經濟實惠的 DJ 控制器', 2, 4, 'ddj', 10);
