-- 比賽表
CREATE TABLE IF NOT EXISTS contests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    venue VARCHAR(200) NOT NULL,
    entry_fee FLOAT DEFAULT 0,
    prize_pool FLOAT,
    rules TEXT,
    judging_criteria TEXT,
    registration_start DATETIME NOT NULL,
    registration_deadline DATETIME NOT NULL,
    event_date DATETIME NOT NULL,
    event_start_time VARCHAR(10),
    max_participants INT DEFAULT 100,
    current_participants INT DEFAULT 0,
    min_age INT,
    image_url VARCHAR(255),
    is_featured BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_registration_deadline (registration_deadline),
    INDEX idx_event_date (event_date),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 比賽註冊表
CREATE TABLE IF NOT EXISTS contest_registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    contest_id INT NOT NULL,
    user_id INT NOT NULL,
    registration_number VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    dj_name VARCHAR(100),
    notes TEXT,
    status VARCHAR(20) DEFAULT 'Registered',
    paid BOOLEAN DEFAULT FALSE,
    rank INT,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    participated_at DATETIME,
    FOREIGN KEY (contest_id) REFERENCES contests(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_contest_id (contest_id),
    INDEX idx_user_id (user_id),
    INDEX idx_registration_number (registration_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入示例比賽
INSERT INTO contests (title, description, venue, entry_fee, prize_pool, registration_start, registration_deadline, event_date, event_start_time, max_participants, is_featured, is_active) VALUES
('中部 DJ 大賽 2026', '台中地區最大規模的 DJ 競技場', '台中市中友百貨 12F', 500, 50000, '2026-05-20 00:00:00', '2026-06-15 23:59:59', '2026-06-22 18:00:00', '18:00', 50, TRUE, TRUE),
('全國 DJ 總決賽', '全台各地 DJ 高手匯聚一堂', '台北市信義區', 1000, 200000, '2026-06-01 00:00:00', '2026-08-15 23:59:59', '2026-08-30 15:00:00', '15:00', 100, TRUE, TRUE),
('春季 DJ 挑戰賽', '新手友善的 DJ 比賽', '台中市西屯區', 300, 30000, '2026-04-20 00:00:00', '2026-05-22 23:59:59', '2026-05-31 19:00:00', '19:00', 40, FALSE, TRUE);
