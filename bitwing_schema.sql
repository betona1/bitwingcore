-- ============================================================
-- Bitwing AI 비서 시스템 — Database Schema
-- DB: bitwing (utf8mb4_unicode_ci)
-- Server: 192.168.219.200:3306
-- Created: 2026-03-29
-- ============================================================

USE bitwing;

-- ------------------------------------------------------------
-- 1. AI 매니저
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS managers (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE COMMENT '코드명 (schedule_mgr 등)',
    display_name VARCHAR(100) NOT NULL COMMENT '표시명 (일정 매니저 등)',
    role TEXT COMMENT '역할 설명',
    status ENUM('active','busy','idle','disabled') DEFAULT 'idle',
    modules JSON COMMENT '담당 모듈 목록',
    config JSON COMMENT '매니저 설정',
    total_tasks INT DEFAULT 0,
    last_active_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='AI 매니저 목록';

-- ------------------------------------------------------------
-- 2. 매니저 작업 히스토리
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS manager_tasks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    manager VARCHAR(50) NOT NULL COMMENT '매니저 코드명',
    intent VARCHAR(100) COMMENT '의도 분류',
    request TEXT COMMENT '사용자 요청 원문',
    response TEXT COMMENT '매니저 응답',
    status ENUM('pending','processing','completed','failed') DEFAULT 'pending',
    duration_ms INT COMMENT '처리 소요시간(ms)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    INDEX idx_manager (manager),
    INDEX idx_status (status)
) ENGINE=InnoDB COMMENT='매니저 작업 히스토리';

-- ------------------------------------------------------------
-- 3. 일정 (캘린더)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS calendars (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    start_at DATETIME NOT NULL,
    end_at DATETIME NOT NULL,
    location VARCHAR(500),
    reminder_minutes INT DEFAULT 30,
    status ENUM('active','cancelled','completed') DEFAULT 'active',
    google_event_id VARCHAR(200) COMMENT 'Google Calendar 이벤트 ID',
    source ENUM('bitwing','google','manual') DEFAULT 'bitwing',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_start_at (start_at),
    INDEX idx_google_event_id (google_event_id)
) ENGINE=InnoDB COMMENT='일정/캘린더';

-- ------------------------------------------------------------
-- 4. 할일
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS todos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    priority ENUM('urgent','high','normal','low') DEFAULT 'normal',
    status ENUM('pending','in_progress','completed','cancelled') DEFAULT 'pending',
    due_date DATE,
    assigned_manager VARCHAR(50) COMMENT '담당 매니저',
    completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_due_date (due_date)
) ENGINE=InnoDB COMMENT='할일 목록';

-- ------------------------------------------------------------
-- 5. 메모
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS memos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500),
    content TEXT NOT NULL,
    tags JSON,
    category VARCHAR(100),
    source ENUM('bitwing','google_keep','notion','manual') DEFAULT 'bitwing',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category)
) ENGINE=InnoDB COMMENT='메모';

-- ------------------------------------------------------------
-- 6. 대화 히스토리
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS conversations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    role ENUM('user','assistant','manager') NOT NULL,
    message TEXT NOT NULL,
    intent VARCHAR(100),
    module VARCHAR(50),
    manager VARCHAR(50),
    client ENUM('mobile','desktop','web') DEFAULT 'desktop',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_manager (manager),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB COMMENT='대화 히스토리';

-- ------------------------------------------------------------
-- 7. 가계부 거래
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS finance_transactions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    type ENUM('income','expense') NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    category VARCHAR(100) NOT NULL COMMENT '식비/교통/쇼핑 등',
    subcategory VARCHAR(100),
    description VARCHAR(500),
    payment_method VARCHAR(100) COMMENT '현금/카드/이체 등',
    bank_name VARCHAR(100),
    card_name VARCHAR(100),
    merchant VARCHAR(200) COMMENT '가맹점',
    receipt_image_path VARCHAR(500),
    source ENUM('manual','bank_api','ocr','crawling') DEFAULT 'manual',
    transaction_date DATE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_type (type),
    INDEX idx_category (category),
    INDEX idx_transaction_date (transaction_date)
) ENGINE=InnoDB COMMENT='가계부 거래내역';

-- ------------------------------------------------------------
-- 8. 은행 계좌
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bank_accounts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    bank_name VARCHAR(100) NOT NULL,
    account_number_masked VARCHAR(50) COMMENT '마스킹된 계좌번호',
    account_type VARCHAR(50),
    balance DECIMAL(15,2),
    last_synced_at DATETIME,
    config JSON COMMENT '연동 설정 (암호화)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='은행 계좌';

-- ------------------------------------------------------------
-- 9. 이메일 캐시
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS email_cache (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    email_provider ENUM('gmail','outlook','imap') NOT NULL,
    message_id VARCHAR(200) UNIQUE,
    subject VARCHAR(500),
    sender VARCHAR(200),
    received_at DATETIME,
    is_read BOOLEAN DEFAULT FALSE,
    ai_summary TEXT COMMENT 'AI 요약',
    labels JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_received_at (received_at),
    INDEX idx_is_read (is_read)
) ENGINE=InnoDB COMMENT='이메일 캐시';

-- ------------------------------------------------------------
-- 10. 사원 PC
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS managed_pcs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    hostname VARCHAR(200) NOT NULL,
    ip_address VARCHAR(45),
    os_type ENUM('windows','linux') NOT NULL,
    employee_name VARCHAR(100),
    department VARCHAR(100),
    status ENUM('online','offline','maintenance') DEFAULT 'offline',
    last_seen_at DATETIME,
    system_info JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status)
) ENGINE=InnoDB COMMENT='사원 PC 관리';

-- ------------------------------------------------------------
-- 11. 파일 관리
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS managed_files (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(500) NOT NULL,
    filepath VARCHAR(1000) NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    category VARCHAR(100),
    access_level ENUM('public','manager','private') DEFAULT 'public',
    allowed_managers JSON,
    uploaded_by VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_access_level (access_level)
) ENGINE=InnoDB COMMENT='파일 관리';

-- ------------------------------------------------------------
-- 12. 외부 연동 설정
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS integrations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    service VARCHAR(100) NOT NULL COMMENT 'google_calendar, gmail, bank 등',
    status ENUM('connected','disconnected','error') DEFAULT 'disconnected',
    config JSON COMMENT '연동 설정 (OAuth 토큰 등, 암호화)',
    last_synced_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE INDEX idx_service (service)
) ENGINE=InnoDB COMMENT='외부 서비스 연동';

-- ------------------------------------------------------------
-- 13. 시스템 로그
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS system_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    level ENUM('info','warning','error','critical') DEFAULT 'info',
    module VARCHAR(50),
    manager VARCHAR(50),
    message TEXT,
    details JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_level (level),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB COMMENT='시스템 로그';

-- ============================================================
-- 초기 데이터: 5개 AI 매니저 등록
-- ============================================================
INSERT INTO managers (name, display_name, role, status, modules) VALUES
('schedule_mgr', '📅 일정 매니저', '캘린더, 일정 관리, Google Calendar 연동, 알림', 'idle',
 '["calendar_mod"]'),
('task_mgr', '💼 업무 매니저', '할일, 메모, 이메일, 파일 관리', 'idle',
 '["todo_mod", "memo_mod", "email_mod", "file_mod"]'),
('finance_mgr', '💰 재무 매니저', '가계부, 금융, 은행 연동, 영수증 OCR, 크롤링', 'idle',
 '["finance_mod"]'),
('it_mgr', '🖥️ IT 매니저', '사원 PC 관리, AI100 시스템 연동, 원격 제어', 'idle',
 '["pc_manager_mod"]'),
('report_mgr', '📊 보고 매니저', '리포트, 통계 분석, 일일/주간/월간 보고', 'idle',
 '["report_mod"]')
ON DUPLICATE KEY UPDATE display_name=VALUES(display_name);
