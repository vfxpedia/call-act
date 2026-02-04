-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- CALL:ACT 통합 DB 스키마 (Integrated Schema)
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- 
-- 목적: Mock 데이터 + 기존 DB 스키마 + API 스펙 통합
-- 버전: v2.0
-- 작성일: 2025-02-03
-- DBMS: PostgreSQL 15+
-- 확장: pgvector
-- 
-- ⭐ 주요 변경사항:
-- 1. users → employees 통합
-- 2. scenarios → simulations 통합
-- 3. simulation_attempts 추가
-- 4. badges, employee_badges 추가
-- 5. weekly_goals 추가
-- 6. consultations 카테고리 분리 (main_category, sub_category)
-- 
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

-- ========================================
-- 1. 데이터베이스 및 확장 설정
-- ========================================

-- 데이터베이스 생성 (이미 존재하면 스킵)
-- CREATE DATABASE callact_db
--   WITH ENCODING 'UTF8'
--   LC_COLLATE = 'ko_KR.UTF-8'
--   LC_CTYPE = 'ko_KR.UTF-8'
--   TEMPLATE template0;

-- 연결
-- \c callact_db

-- 확장 설치
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 스키마 생성
CREATE SCHEMA IF NOT EXISTS public;
CREATE SCHEMA IF NOT EXISTS rag;
CREATE SCHEMA IF NOT EXISTS logs;

SET search_path TO public, rag, logs;

-- ========================================
-- 2. 핵심 테이블 (P0 - 최우선)
-- ========================================

-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- 2.1 employees (직원) - users 통합
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DROP TABLE IF EXISTS employees CASCADE;
CREATE TABLE employees (
    -- 기본 정보
    id VARCHAR(50) PRIMARY KEY,                    -- EMP-001 (길이 여유)
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,           -- bcrypt 해시
    
    -- 직원 정보
    team VARCHAR(100) NOT NULL,                    -- 상담1팀, 상담2팀, 상담3팀
    position VARCHAR(50) NOT NULL,                 -- 사원, 대리, 과장, 차장, 부장, 팀장
    phone VARCHAR(20),
    join_date DATE NOT NULL,
    
    -- 권한 및 상태
    is_admin BOOLEAN DEFAULT FALSE,                -- 관리자 여부 (role 대신)
    status VARCHAR(20) DEFAULT 'active',           -- active, inactive, vacation
    
    -- 성과 지표 (실시간 업데이트)
    rank INTEGER,                                  -- 순위 (1, 2, 3, ...)
    consultations INTEGER DEFAULT 0,               -- 총 상담 건수
    fcr DECIMAL(5,2),                             -- FCR 달성률 (96.00%)
    avg_time VARCHAR(10),                          -- 평균 상담 시간 ("4:15" 형식)
    
    -- 메타 정보
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);

-- 인덱스
CREATE INDEX idx_employees_email ON employees(email);
CREATE INDEX idx_employees_team ON employees(team);
CREATE INDEX idx_employees_status ON employees(status);
CREATE INDEX idx_employees_rank ON employees(rank);

-- View (기존 코드 호환용)
CREATE VIEW users AS SELECT * FROM employees;

-- 샘플 데이터
INSERT INTO employees (id, name, email, password_hash, team, position, phone, join_date, is_admin, rank, consultations, fcr, avg_time) VALUES
('EMP-001', '김민수', 'kim@teddycard.com', '$2b$12$dummy_hash_1', '상담1팀', '팀장', '010-1234-5678', '2023-01-15', FALSE, 1, 145, 96.00, '4:15'),
('EMP-002', '박지영', 'park@teddycard.com', '$2b$12$dummy_hash_2', '상담1팀', '대리', '010-2345-6789', '2023-03-20', FALSE, 2, 138, 95.00, '4:20'),
('EMP-003', '이수진', 'lee@teddycard.com', '$2b$12$dummy_hash_3', '상담2팀', '과장', '010-3456-7890', '2022-06-10', FALSE, 3, 132, 94.00, '4:30'),
('ADMIN-001', '관리자', 'admin@teddycard.com', '$2b$12$dummy_hash_admin', '관리팀', '부장', '010-9999-9999', '2019-01-01', TRUE, NULL, 0, NULL, NULL);

COMMENT ON TABLE employees IS '직원 정보 (users 통합)';
COMMENT ON COLUMN employees.is_admin IS '관리자 여부 (기존 role 대체)';
COMMENT ON COLUMN employees.rank IS '순위 (1, 2, 3, ...)';
COMMENT ON COLUMN employees.avg_time IS '평균 상담 시간 ("4:15" 형식, Mock 데이터 호환)';

-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- 2.2 consultations (상담 기록) - 카테고리 분리
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DROP TABLE IF EXISTS consultations CASCADE;
CREATE TABLE consultations (
    -- 기본 정보
    id VARCHAR(100) PRIMARY KEY,                   -- CS-EMP001-202501051432
    agent_id VARCHAR(50) NOT NULL,                 -- FK to employees
    
    -- 고객 정보
    customer VARCHAR(100) NOT NULL,                -- 고객명
    
    -- 카테고리 (대분류 > 중분류)
    main_category VARCHAR(100) NOT NULL,           -- "분실/도난"
    sub_category VARCHAR(100) NOT NULL,            -- "분실신고"
    
    -- 상담 정보
    status VARCHAR(20) NOT NULL DEFAULT 'in_progress',  -- 완료, 진행중, 보류, 미완료
    content TEXT,                                  -- 상담 내용 요약
    memo TEXT,                                     -- 상담사 메모
    
    -- 성과 지표
    fcr BOOLEAN DEFAULT FALSE,                     -- FCR 달성 여부
    is_best_practice BOOLEAN DEFAULT FALSE,        -- 우수 상담 사례
    
    -- 시간 정보
    datetime TIMESTAMP NOT NULL,                   -- 상담 일시 (Mock 호환)
    duration_seconds INTEGER,                      -- 통화 시간 (초)
    
    -- 메타 정보
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 외래키
    FOREIGN KEY (agent_id) REFERENCES employees(id) ON DELETE CASCADE
);

-- 인덱스
CREATE INDEX idx_consultations_agent_id ON consultations(agent_id);
CREATE INDEX idx_consultations_main_category ON consultations(main_category);
CREATE INDEX idx_consultations_sub_category ON consultations(sub_category);
CREATE INDEX idx_consultations_status ON consultations(status);
CREATE INDEX idx_consultations_fcr ON consultations(fcr);
CREATE INDEX idx_consultations_best_practice ON consultations(is_best_practice);
CREATE INDEX idx_consultations_datetime ON consultations(datetime DESC);
CREATE INDEX idx_consultations_agent_datetime ON consultations(agent_id, datetime DESC);

-- Helper function: duration을 "5:12" 형식으로 변환
CREATE OR REPLACE FUNCTION format_duration(seconds INT) RETURNS VARCHAR(10) AS $$
BEGIN
    RETURN LPAD((seconds / 60)::TEXT, 2, '0') || ':' || LPAD((seconds % 60)::TEXT, 2, '0');
END;
$$ LANGUAGE plpgsql;

-- 샘플 데이터
INSERT INTO consultations (id, agent_id, customer, main_category, sub_category, status, content, datetime, duration_seconds, fcr, is_best_practice, memo) VALUES
('CS-EMP001-202501051432', 'EMP-001', '김민수', '분실/도난', '분실신고', '완료', '카드 분실 신고 접수 및 즉시 정지 처리. 재발급 신청 완료', '2025-01-05 14:32:00', 312, TRUE, TRUE, '카드 분실 신고 및 재발급 처리 완료. 고객 만족도 높음'),
('CS-EMP002-202501061020', 'EMP-002', '이영희', '해외결제', '차단해제', '완료', '해외 여행 중 카드 결제 차단 해제 처리', '2025-01-06 10:20:00', 420, TRUE, FALSE, '해외 결제 차단 해제 완료'),
('CS-EMP001-202501071530', 'EMP-001', '박철수', '한도증액', '신용조회', '진행중', '한도 증액 신청 진행 중', '2025-01-07 15:30:00', NULL, FALSE, FALSE, '신용조회 대기 중');

COMMENT ON TABLE consultations IS '상담 기록 (카테고리 대분류/중분류 분리)';
COMMENT ON COLUMN consultations.main_category IS '대분류 (분실/도난, 해외결제, 한도증액 등)';
COMMENT ON COLUMN consultations.sub_category IS '중분류 (분실신고, 차단해제, 신용조회 등)';
COMMENT ON COLUMN consultations.duration_seconds IS '통화 시간 (초), format_duration()으로 변환 가능';

-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- 2.3 consultation_messages (상담 대화 내용)
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DROP TABLE IF EXISTS consultation_messages CASCADE;
CREATE TABLE consultation_messages (
    id BIGSERIAL PRIMARY KEY,
    consultation_id VARCHAR(100) NOT NULL,         -- FK to consultations
    
    speaker VARCHAR(20) NOT NULL,                  -- agent, customer
    message TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (consultation_id) REFERENCES consultations(id) ON DELETE CASCADE
);

CREATE INDEX idx_messages_consultation_id ON consultation_messages(consultation_id);
CREATE INDEX idx_messages_timestamp ON consultation_messages(timestamp);

-- 샘플 데이터
INSERT INTO consultation_messages (consultation_id, speaker, message, timestamp) VALUES
('CS-EMP001-202501051432', 'customer', '카드를 잃어버렸어요', '2025-01-05 14:32:05'),
('CS-EMP001-202501051432', 'agent', '고객님 카드 분실 신고를 도와드리겠습니다', '2025-01-05 14:32:15'),
('CS-EMP001-202501051432', 'customer', '네 빨리 정지 부탁드려요', '2025-01-05 14:32:22');

COMMENT ON TABLE consultation_messages IS 'STT로 변환된 실시간 대화 내용';

-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- 2.4 simulations (시뮬레이션 시나리오) - scenarios 통합
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DROP TABLE IF EXISTS simulations CASCADE;
CREATE TABLE simulations (
    -- 기본 정보
    id VARCHAR(50) PRIMARY KEY,                    -- SIM-001
    category VARCHAR(100) NOT NULL,                -- 카드분실, 해외결제 등
    title VARCHAR(255) NOT NULL,
    difficulty VARCHAR(20) NOT NULL,               -- 초급, 중급, 고급
    duration_minutes INTEGER NOT NULL,             -- 예상 소요 시간 (분)
    description TEXT,
    
    -- 추가 정보
    tags JSON,                                     -- ["카드분실", "재발급", "기본상담"]
    is_active BOOLEAN DEFAULT TRUE,                -- 활성 여부
    
    -- 메타 정보
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_simulations_difficulty ON simulations(difficulty);
CREATE INDEX idx_simulations_is_active ON simulations(is_active);

-- 샘플 데이터
INSERT INTO simulations (id, category, title, difficulty, duration_minutes, description, tags, is_active) VALUES
('SIM-001', '카드분실', '카드 분실 신고 및 재발급', '초급', 5, '고객의 카드 분실 신고를 접수하고 재발급 절차를 안내하는 시나리오', '["카드분실", "재발급", "기본상담"]', TRUE),
('SIM-002', '해외결제', '해외 결제 차단 해제 요청', '중급', 7, '해외 여행 중 카드 결제가 차단된 고객의 문의를 처리하는 시나리오', '["해외결제", "차단해제", "긴급처리"]', TRUE),
('SIM-003', '수수료문의', '복잡한 수수료 환불 요청', '고급', 10, '여러 건의 수수료 환불을 요청하는 까다로운 고객 응대', '["수수료", "환불", "복잡처리"]', TRUE);

COMMENT ON TABLE simulations IS '시뮬레이션 시나리오 (scenarios 통합, tags 추가)';
COMMENT ON COLUMN simulations.tags IS 'JSON 배열 형태의 태그 (Mock 데이터 호환)';

-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- 2.5 simulation_attempts (시뮬레이션 시도 기록) ⭐ 신규
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DROP TABLE IF EXISTS simulation_attempts CASCADE;
CREATE TABLE simulation_attempts (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,                  -- FK to employees
    scenario_id VARCHAR(50) NOT NULL,              -- FK to simulations
    
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),  -- 점수 (0-100)
    duration_seconds INTEGER NOT NULL,             -- 소요 시간 (초)
    answers JSON,                                  -- 답변 데이터
    
    completed_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES employees(id) ON DELETE CASCADE,
    FOREIGN KEY (scenario_id) REFERENCES simulations(id) ON DELETE CASCADE
);

CREATE INDEX idx_attempts_user_id ON simulation_attempts(user_id);
CREATE INDEX idx_attempts_scenario_id ON simulation_attempts(scenario_id);
CREATE INDEX idx_attempts_completed_at ON simulation_attempts(completed_at DESC);
CREATE INDEX idx_attempts_user_scenario ON simulation_attempts(user_id, scenario_id, completed_at DESC);

-- 샘플 데이터
INSERT INTO simulation_attempts (user_id, scenario_id, score, duration_seconds, answers, completed_at) VALUES
('EMP-001', 'SIM-001', 95, 290, '{"q1": "A", "q2": "B", "q3": "C"}', '2025-01-05 14:30:00'),
('EMP-002', 'SIM-002', 88, 395, '{"q1": "A", "q2": "C", "q3": "B"}', '2025-01-04 10:20:00'),
('EMP-001', 'SIM-001', 92, 310, '{"q1": "A", "q2": "B", "q3": "C"}', '2025-01-03 16:10:00');

COMMENT ON TABLE simulation_attempts IS '⭐ 신규: 시뮬레이션 시도 기록 (recentAttemptsData)';

-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- 2.6 badges (배지 마스터) ⭐ 신규
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DROP TABLE IF EXISTS badges CASCADE;
CREATE TABLE badges (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    color VARCHAR(7) NOT NULL,                     -- #FBBC04
    description TEXT,
    criteria JSON,                                 -- {"fcr_threshold": 95, "period": "month"}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_badges_name ON badges(name);

-- 샘플 데이터
INSERT INTO badges (name, color, description, criteria) VALUES
('FCR 마스터', '#FBBC04', 'FCR 95% 이상 달성', '{"fcr_threshold": 95}'),
('스피드 레이서', '#0047AB', '평균 통화 시간 4분 이하', '{"avg_time_threshold": 240}'),
('감정 케어', '#34A853', '감정 전환율 80% 이상', '{"emotion_conversion_threshold": 80}'),
('완벽주의자', '#9C27B0', '고객 만족도 95% 이상', '{"satisfaction_threshold": 95}'),
('시뮬 마니아', '#FF6B35', '시뮬레이션 10회 완료', '{"simulation_count": 10}');

COMMENT ON TABLE badges IS '⭐ 신규: 배지 마스터 (badgesData)';
COMMENT ON COLUMN badges.criteria IS 'JSON 형태의 획득 조건';

-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- 2.7 employee_badges (직원-배지 매핑) ⭐ 신규
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DROP TABLE IF EXISTS employee_badges CASCADE;
CREATE TABLE employee_badges (
    id BIGSERIAL PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL,              -- FK to employees
    badge_id INTEGER NOT NULL,                     -- FK to badges
    earned_at TIMESTAMP NOT NULL,
    
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    FOREIGN KEY (badge_id) REFERENCES badges(id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX idx_employee_badge_unique ON employee_badges(employee_id, badge_id);
CREATE INDEX idx_employee_badges_employee ON employee_badges(employee_id, earned_at DESC);
CREATE INDEX idx_employee_badges_earned_at ON employee_badges(earned_at DESC);

-- 샘플 데이터
INSERT INTO employee_badges (employee_id, badge_id, earned_at) VALUES
('EMP-001', 1, '2025-01-15 00:00:00'),  -- FCR 마스터
('EMP-001', 2, '2025-01-20 00:00:00'),  -- 스피드 레이서
('EMP-002', 1, '2025-01-18 00:00:00');  -- FCR 마스터

COMMENT ON TABLE employee_badges IS '⭐ 신규: 직원-배지 매핑';

-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- 2.8 notices (공지사항)
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DROP TABLE IF EXISTS notices CASCADE;
CREATE TABLE notices (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    author_id VARCHAR(50) NOT NULL,
    is_pinned BOOLEAN DEFAULT FALSE,
    views INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (author_id) REFERENCES employees(id) ON DELETE CASCADE
);

CREATE INDEX idx_notices_is_pinned ON notices(is_pinned);
CREATE INDEX idx_notices_created_at ON notices(created_at DESC);

-- 샘플 데이터
INSERT INTO notices (title, content, author_id, is_pinned, views) VALUES
('[필독] 2025년 1월 시스템 점검 안내', '시스템 점검이 1월 10일 02:00~04:00에 진행됩니다.', 'ADMIN-001', TRUE, 245),
('신규 시뮬레이션 시나리오 추가', 'SIM-004 "진상 고객 감정 전환" 시나리오가 추가되었습니다.', 'ADMIN-001', FALSE, 132);

COMMENT ON TABLE notices IS '공지사항';

-- ========================================
-- 3. 중요 테이블 (P1)
-- ========================================

-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- 3.1 weekly_goals (주간 목표 설정) ⭐ 신규
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DROP TABLE IF EXISTS weekly_goals CASCADE;
CREATE TABLE weekly_goals (
    id SERIAL PRIMARY KEY,
    week_start DATE NOT NULL,
    week_end DATE NOT NULL,
    target INTEGER NOT NULL,                       -- 목표 건수
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_weekly_goals_week_range ON weekly_goals(week_start, week_end);

-- 샘플 데이터
INSERT INTO weekly_goals (week_start, week_end, target) VALUES
('2025-01-27', '2025-02-02', 500),
('2025-02-03', '2025-02-09', 550);

COMMENT ON TABLE weekly_goals IS '⭐ 신규: 주간 목표 설정 (weeklyGoalData)';

-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- 3.2 consultation_keywords (상담 키워드)
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DROP TABLE IF EXISTS consultation_keywords CASCADE;
CREATE TABLE consultation_keywords (
    id BIGSERIAL PRIMARY KEY,
    consultation_id VARCHAR(100) NOT NULL,         -- FK to consultations
    
    keyword VARCHAR(100) NOT NULL,                 -- 키워드 (예: "카드분실")
    tagged_at TIMESTAMP NOT NULL,                  -- 태깅된 시간
    confidence DECIMAL(5,4),                      -- 신뢰도 (0.9500)
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (consultation_id) REFERENCES consultations(id) ON DELETE CASCADE
);

CREATE INDEX idx_keywords_consultation_id ON consultation_keywords(consultation_id);
CREATE INDEX idx_keywords_keyword ON consultation_keywords(keyword);
CREATE INDEX idx_keywords_tagged_at ON consultation_keywords(tagged_at);

COMMENT ON TABLE consultation_keywords IS '실시간으로 추출된 키워드 (태깅 시간 포함)';

-- ========================================
-- 4. 집계 뷰 (성능 최적화)
-- ========================================

-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- 4.1 대시보드 통계 (Materialized View)
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DROP MATERIALIZED VIEW IF EXISTS dashboard_stats_cache;
CREATE MATERIALIZED VIEW dashboard_stats_cache AS
SELECT 
  COUNT(*) as today_calls,
  COUNT(*) FILTER (WHERE status = '완료') as completed,
  COUNT(*) FILTER (WHERE status = '진행중') as pending,
  COUNT(*) FILTER (WHERE status = '미완료') as incomplete,
  CURRENT_DATE as stat_date
FROM consultations
WHERE DATE(datetime) = CURRENT_DATE;

CREATE UNIQUE INDEX idx_dashboard_stats_date ON dashboard_stats_cache(stat_date);

COMMENT ON MATERIALIZED VIEW dashboard_stats_cache IS '대시보드 통계 캐시 (1시간마다 갱신)';

-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- 4.2 팀별 통계 (Materialized View)
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DROP MATERIALIZED VIEW IF EXISTS team_stats_cache;
CREATE MATERIALIZED VIEW team_stats_cache AS
SELECT 
  e.team,
  COUNT(c.id) as calls,
  ROUND(AVG(CASE WHEN c.fcr = TRUE THEN 100 ELSE 0 END), 0) as fcr,
  COUNT(DISTINCT e.id) as members
FROM employees e
LEFT JOIN consultations c ON e.id = c.agent_id AND c.datetime >= CURRENT_DATE - INTERVAL '7 days'
WHERE e.status = 'active'
GROUP BY e.team
ORDER BY calls DESC;

CREATE INDEX idx_team_stats_team ON team_stats_cache(team);

COMMENT ON MATERIALIZED VIEW team_stats_cache IS '팀별 통계 캐시 (1시간마다 갱신)';

-- ========================================
-- 5. 자동 갱신 트리거 (pg_cron 필요)
-- ========================================

-- pg_cron 확장 설치
-- CREATE EXTENSION IF NOT EXISTS pg_cron;

-- 1시간마다 Materialized View 갱신
-- SELECT cron.schedule('refresh_dashboard_stats', '0 * * * *', 
--   'REFRESH MATERIALIZED VIEW CONCURRENTLY dashboard_stats_cache');

-- SELECT cron.schedule('refresh_team_stats', '0 * * * *', 
--   'REFRESH MATERIALIZED VIEW CONCURRENTLY team_stats_cache');

-- ========================================
-- 6. 유용한 쿼리 함수
-- ========================================

-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- 6.1 현재 주간 목표 조회
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CREATE OR REPLACE FUNCTION get_current_weekly_goal()
RETURNS TABLE (
  week_start DATE,
  week_end DATE,
  target INTEGER,
  current INTEGER,
  percentage INTEGER
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    wg.week_start,
    wg.week_end,
    wg.target,
    COUNT(c.id)::INTEGER as current,
    ROUND((COUNT(c.id)::DECIMAL / wg.target * 100), 0)::INTEGER as percentage
  FROM weekly_goals wg
  LEFT JOIN consultations c ON c.datetime >= wg.week_start AND c.datetime <= wg.week_end
  WHERE CURRENT_DATE BETWEEN wg.week_start AND wg.week_end
  GROUP BY wg.week_start, wg.week_end, wg.target
  LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- 6.2 사용자별 배지 목록 조회
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CREATE OR REPLACE FUNCTION get_user_badges(p_user_id VARCHAR(50))
RETURNS TABLE (
  badge_id INTEGER,
  badge_name VARCHAR(100),
  badge_color VARCHAR(7),
  earned BOOLEAN,
  earned_at TIMESTAMP
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    b.id,
    b.name,
    b.color,
    CASE WHEN eb.id IS NOT NULL THEN TRUE ELSE FALSE END as earned,
    eb.earned_at
  FROM badges b
  LEFT JOIN employee_badges eb ON b.id = eb.badge_id AND eb.employee_id = p_user_id
  ORDER BY b.id;
END;
$$ LANGUAGE plpgsql;

-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- 6.3 시뮬레이션 진행률 조회
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CREATE OR REPLACE FUNCTION get_simulation_progress(p_user_id VARCHAR(50), p_scenario_id VARCHAR(50))
RETURNS TABLE (
  scenario_id VARCHAR(50),
  title VARCHAR(255),
  completed BOOLEAN,
  best_score INTEGER,
  avg_score INTEGER,
  attempts INTEGER,
  last_attempt_date TIMESTAMP
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    s.id,
    s.title,
    CASE WHEN COUNT(sa.id) > 0 THEN TRUE ELSE FALSE END as completed,
    MAX(sa.score)::INTEGER as best_score,
    ROUND(AVG(sa.score))::INTEGER as avg_score,
    COUNT(sa.id)::INTEGER as attempts,
    MAX(sa.completed_at) as last_attempt_date
  FROM simulations s
  LEFT JOIN simulation_attempts sa ON s.id = sa.scenario_id AND sa.user_id = p_user_id
  WHERE s.id = p_scenario_id
  GROUP BY s.id, s.title;
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- 7. 권한 설정
-- ========================================

-- API 사용자 생성 (필요시)
-- CREATE USER callact_api WITH PASSWORD 'secure_password';
-- GRANT CONNECT ON DATABASE callact_db TO callact_api;
-- GRANT USAGE ON SCHEMA public, rag TO callact_api;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO callact_api;
-- GRANT SELECT ON ALL TABLES IN SCHEMA rag TO callact_api;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO callact_api;

-- ========================================
-- 8. 검증 쿼리
-- ========================================

-- 테이블 개수 확인
SELECT 
  schemaname, 
  COUNT(*) as table_count
FROM pg_tables 
WHERE schemaname IN ('public', 'rag', 'logs')
GROUP BY schemaname;

-- 샘플 데이터 확인
SELECT 'employees' as table_name, COUNT(*) as row_count FROM employees
UNION ALL
SELECT 'consultations', COUNT(*) FROM consultations
UNION ALL
SELECT 'simulations', COUNT(*) FROM simulations
UNION ALL
SELECT 'simulation_attempts', COUNT(*) FROM simulation_attempts
UNION ALL
SELECT 'badges', COUNT(*) FROM badges
UNION ALL
SELECT 'employee_badges', COUNT(*) FROM employee_badges
UNION ALL
SELECT 'notices', COUNT(*) FROM notices
UNION ALL
SELECT 'weekly_goals', COUNT(*) FROM weekly_goals;

-- 주간 목표 테스트
SELECT * FROM get_current_weekly_goal();

-- 사용자 배지 테스트
SELECT * FROM get_user_badges('EMP-001');

-- 시뮬레이션 진행률 테스트
SELECT * FROM get_simulation_progress('EMP-001', 'SIM-001');

-- ========================================
-- 완료!
-- ========================================
-- 통합 DB 스키마 생성 완료
-- 총 테이블: 11개 (P0: 8개, P1: 3개)
-- Materialized Views: 2개
-- Functions: 3개
-- ========================================
