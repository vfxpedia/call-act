-- ==================================================
-- 직원 데이터 수정 스크립트 (Foreign Key 제약 조건 고려)
-- ==================================================
-- Description: 기존에 잘못 입력된 직원 데이터 수정
-- Author: CALL:ACT Team
-- Date: 2026-01-11
-- ==================================================
-- 주의: employees.id는 PRIMARY KEY이므로 직접 UPDATE 불가
-- consultations 테이블의 agent_id를 먼저 업데이트한 후 employees 레코드를 교체해야 함
-- ==================================================

-- Step 1: 새로운 직원 레코드 생성 (EMP-TEDDY-DEFAULT)
INSERT INTO employees (id, name, email, role, department, status, created_at)
SELECT 
    'EMP-TEDDY-DEFAULT',
    '테디카드 기본 상담사',
    'default@teddycard.com',
    role,
    department,
    status,
    created_at
FROM employees
WHERE id = 'EMP-TEDI-DEFAULT'
ON CONFLICT (id) DO NOTHING;

-- Step 2: consultations 테이블의 agent_id 업데이트
UPDATE consultations
SET agent_id = 'EMP-TEDDY-DEFAULT'
WHERE agent_id = 'EMP-TEDI-DEFAULT';

-- Step 3: 기존 직원 레코드 삭제
DELETE FROM employees
WHERE id = 'EMP-TEDI-DEFAULT';

-- Step 4: 변경 확인
SELECT id, name, email, role, department, status
FROM employees
WHERE id LIKE 'EMP-%DEFAULT';

-- Step 5: consultations 테이블 확인
SELECT agent_id, COUNT(*) as count
FROM consultations
WHERE agent_id LIKE 'EMP-%DEFAULT'
GROUP BY agent_id;
