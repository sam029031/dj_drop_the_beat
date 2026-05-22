-- 音樂表
CREATE TABLE IF NOT EXISTS music (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    artist VARCHAR(100) NOT NULL,
    genre VARCHAR(50) NOT NULL,
    price FLOAT NOT NULL,
    description TEXT,
    duration_seconds INT,
    bpm INT,
    `key` VARCHAR(10),
    release_year INT,
    image_url VARCHAR(255),
    category VARCHAR(50) DEFAULT 'music',
    in_stock INT DEFAULT 0,
    preorder_available INT DEFAULT 0,
    is_featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_artist (artist),
    INDEX idx_genre (genre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入示例音樂
INSERT INTO music (title, artist, genre, price, description, duration_seconds, bpm, release_year, is_featured) VALUES
('Electronize', 'DJ Max', 'Electronic', 99, '現代電子音樂作品', 240, 128, 2024, TRUE),
('House Energy', 'DJ Pulse', 'House', 79, '充滿能量的浩室舞曲', 300, 120, 2024, TRUE),
('Tech Groove', 'DJ Tech', 'Techno', 89, '技術性科技音樂', 280, 130, 2023, FALSE);
