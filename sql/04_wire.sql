-- 線材配件表
CREATE TABLE IF NOT EXISTS wire (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    wire_type VARCHAR(50) NOT NULL,
    brand VARCHAR(50) NOT NULL,
    price FLOAT NOT NULL,
    description TEXT,
    length_meters FLOAT,
    connector_type VARCHAR(50),
    cable_material VARCHAR(100),
    shielding_type VARCHAR(50),
    image_url VARCHAR(255),
    category VARCHAR(50) DEFAULT 'wire',
    in_stock INT DEFAULT 0,
    preorder_available INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_wire_type (wire_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入示例線材
INSERT INTO wire (name, wire_type, brand, price, description, length_meters, connector_type, category, preorder_available) VALUES
('Neutrik Pro XLR Cable', 'XLR', 'Neutrik', 299, '專業 XLR 平衡線', 5, 'XLR', 'wire', 20),
('Hosa USB-210AF USB Cable', 'USB', 'Hosa', 199, '高品質 USB 傳輸線', 3, 'USB 2.0', 'wire', 15),
('Hosa 3.5mm TRS Cable', '3.5mm', 'Hosa', 149, '立體聲 3.5mm 連接線', 2, '3.5mm TRS', 'wire', 25);
