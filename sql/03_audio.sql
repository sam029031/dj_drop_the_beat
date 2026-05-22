-- 音響設備表
CREATE TABLE IF NOT EXISTS audio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    audio_type VARCHAR(50) NOT NULL,
    brand VARCHAR(50) NOT NULL,
    price FLOAT NOT NULL,
    description TEXT,
    watts INT,
    frequency_response VARCHAR(50),
    impedance VARCHAR(50),
    connectivity VARCHAR(100),
    image_url VARCHAR(255),
    category VARCHAR(50) DEFAULT 'audio',
    in_stock INT DEFAULT 0,
    preorder_available INT DEFAULT 0,
    warranty_months INT DEFAULT 12,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_audio_type (audio_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入示例音響設備
INSERT INTO audio (name, audio_type, brand, price, description, watts, frequency_response, category, preorder_available) VALUES
('Pioneer PLX-500 Turntable', 'SPEAKER', 'Pioneer', 24999, '高品質黑膠唱盤', 0, '20Hz-20kHz', 'audio', 3),
('Technics EAH-DJ1200 Headphones', 'HEADPHONES', 'Technics', 8999, '專業 DJ 耳機，清晰音質', 0, '5Hz-30kHz', 'audio', 6),
('Numark NS7III Mixer', 'MIXER', 'Numark', 29999, '專業 DJ 混音機', 120, '20Hz-20kHz', 'audio', 2);
