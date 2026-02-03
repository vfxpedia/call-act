-- ==================================================
-- Persona Types 테이블 생성 스크립트
-- ==================================================
-- Description: 고객 페르소나 유형 마스터 테이블
-- Author: CALL:ACT Team
-- Date: 2026-01-28
-- ==================================================

-- 1. persona_types 테이블 생성
CREATE TABLE IF NOT EXISTS persona_types (
    -- 유형 코드 (Primary Key)
    code VARCHAR(10) PRIMARY KEY,             -- 'N1', 'S1' 등

    -- 기본 정보
    name VARCHAR(50) NOT NULL,                -- '일반친절형'
    description TEXT,                         -- '불필요한 말 없이 바로 문의사항을 말함'
    category VARCHAR(20) NOT NULL,            -- 'normal' 또는 'special'

    -- LLM 가이던스용 태그
    personality_tags TEXT[],                  -- ['practical', 'direct', 'efficient']
    communication_style JSONB,                -- {"speed": "fast", "tone": "direct"}
    llm_guidance TEXT,                        -- 'LLM에게 전달할 상담 가이드'

    -- 분포 비율 (데이터 생성 시 참고)
    distribution_ratio DECIMAL(4,2),          -- 0.25 (25%)

    -- 표시 순서
    display_order INT DEFAULT 0,

    -- 활성화 여부
    is_active BOOLEAN DEFAULT TRUE,

    -- 타임스탬프
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- 2. 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_persona_types_category ON persona_types(category);
CREATE INDEX IF NOT EXISTS idx_persona_types_active ON persona_types(is_active);

-- 3. 초기 데이터 삽입 (12개 유형: N1-N4, S1-S8)
INSERT INTO persona_types (code, name, description, category, personality_tags, communication_style, llm_guidance, distribution_ratio, display_order)
VALUES
    -- Normal Types (일반 고객 유형)
    ('N1', '일반친절형', '일반적인 응대, 친절한 안내 선호', 'normal',
     ARRAY['normal', 'polite'],
     '{"speed": "moderate", "tone": "neutral"}'::jsonb,
     '일반적인 응대로 친절하게 안내해주세요.',
     0.20, 1),

    ('N2', '조용한내성형', '간결한 답변 선호, 불필요한 대화 최소화', 'normal',
     ARRAY['quiet', 'reserved'],
     '{"speed": "moderate", "tone": "calm"}'::jsonb,
     '간결한 답변을 선호합니다. 불필요한 대화는 최소화하세요.',
     0.13, 2),

    ('N3', '실용주의형', '목적 지향적, 해결책 먼저 제시', 'normal',
     ARRAY['practical', 'efficient'],
     '{"speed": "fast", "tone": "direct"}'::jsonb,
     '목적 지향적입니다. 해결책을 먼저 제시하세요.',
     0.10, 3),

    ('N4', '친화적수다형', '대화를 즐기는 고객, 친근한 응대', 'normal',
     ARRAY['friendly', 'talkative'],
     '{"speed": "moderate", "tone": "warm"}'::jsonb,
     '대화를 즐기는 고객입니다. 친근하게 응대해주세요.',
     0.07, 4),

    -- Special Types (특수 고객 유형)
    ('S1', '급한성격형', '빠른 답변 선호, 간결한 핵심 전달', 'special',
     ARRAY['impatient', 'direct', 'busy'],
     '{"speed": "fast", "tone": "concise"}'::jsonb,
     '빠른 답변을 선호합니다. 간결하게 핵심만 전달하세요.',
     0.07, 5),

    ('S2', '꼼꼼상세형', '상세한 설명 필요, 차근차근 안내', 'special',
     ARRAY['detailed', 'analytical'],
     '{"speed": "slow", "tone": "thorough"}'::jsonb,
     '상세한 설명이 필요합니다. 차근차근 안내해주세요.',
     0.05, 6),

    ('S3', '감정호소형', '경청, 공감 후 해결책 제시', 'special',
     ARRAY['emotional', 'expressive'],
     '{"speed": "moderate", "tone": "empathetic"}'::jsonb,
     '경청하고 공감한 후 해결책을 제시해주세요.',
     0.05, 7),

    ('S4', '시니어친화형', '쉬운 용어, 천천히 반복 안내', 'special',
     ARRAY['elderly', 'patient', 'needs_repetition'],
     '{"speed": "slow", "tone": "respectful"}'::jsonb,
     '천천히 쉬운 용어로 반복 안내해주세요.',
     0.19, 8),

    ('S5', '디지털네이티브', '앱/웹 셀프서비스 경로 우선 안내', 'special',
     ARRAY['tech_savvy', 'self_service'],
     '{"speed": "fast", "tone": "casual"}'::jsonb,
     '앱/웹 셀프서비스 경로를 먼저 안내해주세요.',
     0.06, 9),

    ('S6', 'VIP고객형', '프리미엄 서비스, 신속 처리', 'special',
     ARRAY['high_value', 'premium', 'loyal'],
     '{"speed": "moderate", "tone": "premium"}'::jsonb,
     '프리미엄 서비스로 신속하게 처리해주세요.',
     0.03, 10),

    ('S7', '반복민원형', '이전 상담 이력 확인, 확실한 해결책 제시', 'special',
     ARRAY['frequent_caller', 'frustrated'],
     '{"speed": "moderate", "tone": "solution_focused"}'::jsonb,
     '이전 상담 이력을 확인하고, 확실한 해결책을 제시하세요.',
     0.03, 11),

    ('S8', '불만항의형', '차분하게 경청 후 해결 방안 제시', 'special',
     ARRAY['complaining', 'demanding'],
     '{"speed": "moderate", "tone": "calm_professional"}'::jsonb,
     '차분하게 경청한 후 해결 방안을 제시해주세요.',
     0.02, 12)

ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    category = EXCLUDED.category,
    personality_tags = EXCLUDED.personality_tags,
    communication_style = EXCLUDED.communication_style,
    llm_guidance = EXCLUDED.llm_guidance,
    distribution_ratio = EXCLUDED.distribution_ratio,
    display_order = EXCLUDED.display_order,
    updated_at = NOW();

-- 4. 테이블 및 컬럼 코멘트
COMMENT ON TABLE persona_types IS '고객 페르소나 유형 마스터 테이블 - LLM 상담 가이던스용';
COMMENT ON COLUMN persona_types.code IS '유형 코드 (N1~N4: 일반, S1~S8: 특수)';
COMMENT ON COLUMN persona_types.name IS '유형명 (예: 일반친절형)';
COMMENT ON COLUMN persona_types.description IS '유형 설명';
COMMENT ON COLUMN persona_types.category IS '유형 카테고리 (normal/special)';
COMMENT ON COLUMN persona_types.personality_tags IS 'LLM 가이던스용 특성 태그 배열';
COMMENT ON COLUMN persona_types.communication_style IS '의사소통 스타일 (JSON)';
COMMENT ON COLUMN persona_types.llm_guidance IS 'LLM에게 전달할 상담 가이드 메시지';
COMMENT ON COLUMN persona_types.distribution_ratio IS '데이터 생성 시 분포 비율';

-- 5. 성공 메시지
DO $$
BEGIN
    RAISE NOTICE '======================================';
    RAISE NOTICE 'Persona Types 테이블 설정 완료:';
    RAISE NOTICE '- persona_types 테이블 생성됨';
    RAISE NOTICE '- 12개 페르소나 유형 삽입됨';
    RAISE NOTICE '  - Normal: N1(일반친절형), N2(조용한내성형), N3(실용주의형), N4(친화적수다형)';
    RAISE NOTICE '  - Special: S1(급한성격형), S2(꼼꼼상세형), S3(감정호소형), S4(시니어친화형), S5(디지털네이티브), S6(VIP고객형), S7(반복민원형), S8(불만항의형)';
    RAISE NOTICE '======================================';
END $$;
