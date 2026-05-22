-- 用戶表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入預設用戶 (admin 和 demo)
-- 密碼: Admin@123456 (已加密為 argon2)
INSERT INTO users (username, email, password_hash, full_name, is_admin, is_active) VALUES
('admin', 'admin@dj-platform.com', '$argon2id$v=19$m=65536,t=3,p=4$dGVzdDEyMzQ1Ng$1234567890abcdef', 'DJ Platform Admin', TRUE, TRUE),
('demo', 'demo@dj-platform.com', '$argon2id$v=19$m=65536,t=3,p=4$ZGVtbzEyMzQ1Ng$abcdef1234567890', 'Demo User', FALSE, TRUE);
