-- 課程表
CREATE TABLE IF NOT EXISTS courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    instructor VARCHAR(100) NOT NULL,
    difficulty VARCHAR(50) NOT NULL,
    price FLOAT NOT NULL,
    duration_hours FLOAT NOT NULL,
    max_students INT DEFAULT 30,
    current_students INT DEFAULT 0,
    syllabus TEXT,
    prerequisites TEXT,
    learning_outcomes TEXT,
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
    class_schedule TEXT,
    image_url VARCHAR(255),
    is_featured BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    registration_deadline DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_difficulty (difficulty),
    INDEX idx_start_date (start_date),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 課程註冊表
CREATE TABLE IF NOT EXISTS course_registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    user_id INT NOT NULL,
    registration_number VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    notes TEXT,
    status VARCHAR(20) DEFAULT 'Active',
    paid BOOLEAN DEFAULT FALSE,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_course_id (course_id),
    INDEX idx_user_id (user_id),
    INDEX idx_registration_number (registration_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入示例課程
INSERT INTO courses (title, description, instructor, difficulty, price, duration_hours, max_students, syllabus, start_date, end_date, registration_deadline, is_featured, is_active) VALUES
('DJ 初級入門課程', '適合完全初學者，從基礎開始教起', 'DJ Master Chen', 'Beginner', 4999, 12, 20, '基礎概念、設備認識、混音技巧', '2026-06-01 19:00:00', '2026-07-31 21:00:00', '2026-05-25 23:59:59', TRUE, TRUE),
('DJ 中級進階課程', '適合有基礎的 DJ 學習進階技巧', 'DJ Pulse', 'Intermediate', 7999, 16, 15, '進階混音、特效應用、表演技巧', '2026-07-01 19:00:00', '2026-08-31 21:00:00', '2026-06-20 23:59:59', TRUE, TRUE),
('DJ 專業精英課程', '最高級別的 DJ 課程，面向職業人士', 'DJ Pro Max', 'Advanced', 12999, 20, 10, '專業表演、音樂製作、舞台控制', '2026-08-01 19:00:00', '2026-09-30 21:00:00', '2026-07-15 23:59:59', FALSE, TRUE);
