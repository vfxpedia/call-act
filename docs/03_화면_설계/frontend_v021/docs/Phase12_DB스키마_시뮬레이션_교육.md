# Phase 12: DB 스키마 - 시뮬레이션 교육 시스템

## 📋 문서 개요

**목적:** 교육 시뮬레이션 시스템을 위한 DB 스키마 정의

**작성 일자:** 2025-01-23  
**Phase:** 12  
**상태:** 📝 **설계 완료**

---

## 🗄️ DB 테이블 구조

### 1. simulation_scenarios (시나리오 템플릿)

**목적:** 기본 시뮬레이션 시나리오 정의 (SIM-001, SIM-002, ...)

```sql
CREATE TABLE simulation_scenarios (
  id VARCHAR(50) PRIMARY KEY,              -- 'SIM-001'
  title VARCHAR(200) NOT NULL,             -- '카드 분실 신고 및 재발급'
  difficulty VARCHAR(20) NOT NULL,         -- '초급', '중급', '고급'
  category VARCHAR(100),                   -- '카드분실'
  description TEXT,
  duration_estimate INT,                   -- 예상 소요 시간 (초)
  
  -- 시나리오 구조
  scenario_objectives JSONB,               -- 학습 목표
  /*
  예시:
  [
    "카드 즉시 정지 처리",
    "재발급 신청 완료",
    "배송 정보 안내"
  ]
  */
  
  scenario_steps JSONB,                    -- 단계별 가이드
  /*
  예시:
  [
    {"step": 1, "action": "고객 본인 확인", "documents": ["card-1-1-1"]},
    {"step": 2, "action": "카드 즉시 정지", "documents": ["card-1-1-2"]},
    {"step": 3, "action": "재발급 신청", "documents": ["card-1-1-3"]}
  ]
  */
  
  required_documents TEXT[],               -- 필수 참조 문서 ID
  required_keywords TEXT[],                -- 필수 키워드
  
  -- AI 고객 설정
  ai_customer_persona VARCHAR(50),         -- '급한성향', '꼼꼼한성향', ...
  ai_customer_name VARCHAR(100),           -- '김민수'
  ai_customer_background TEXT,             -- 고객 배경 정보
  
  -- ⭐ AI 인터랙티브 대화 흐름
  ai_conversation_flow JSONB,
  /*
  예시:
  {
    "initial": {
      "message": "안녕하세요, 카드를 분실했어요!",
      "emotion": "urgent",
      "tts_settings": {"pitch": 1.1, "rate": 1.2}
    },
    "responses": {
      "empathy_high": {
        "trigger": ["걱정", "안심", "빠르게"],
        "message": "네, 빨리 처리해주셔서 감사합니다.",
        "emotion": "calm"
      },
      "empathy_low": {
        "trigger": ["기다리", "확인", "시간"],
        "message": "왜 이렇게 오래 걸리는 거예요?",
        "emotion": "angry"
      },
      "verification_request": {
        "trigger": ["본인확인", "이름", "생년월일"],
        "message": "네, 김민수입니다. 1990년 5월 15일생이에요.",
        "emotion": "neutral"
      }
    },
    "triggers": {
      "card_stopped": {
        "condition": "카드 정지 처리 완료",
        "message": "카드가 정지되었나요? 확인 부탁드려요.",
        "emotion": "anxious"
      },
      "reissue_applied": {
        "condition": "재발급 신청 완료",
        "message": "새 카드는 언제 받을 수 있나요?",
        "emotion": "curious"
      }
    }
  }
  */
  
  -- 평가 기준
  evaluation_criteria JSONB,
  /*
  예시:
  {
    "document_usage": {
      "weight": 30,
      "required": ["card-1-1-1", "card-1-1-2", "card-1-1-3"],
      "description": "필수 문서 참조 여부"
    },
    "keyword_coverage": {
      "weight": 25,
      "required": ["본인확인", "즉시정지", "재발급", "배송"],
      "description": "필수 키워드 언급 여부"
    },
    "sequence_correctness": {
      "weight": 25,
      "expected_sequence": ["본인확인", "카드정지", "재발급신청"],
      "description": "처리 순서 정확성"
    },
    "customer_satisfaction": {
      "weight": 20,
      "factors": ["공감표현", "신속처리", "명확한안내"],
      "description": "고객 만족도"
    }
  }
  */
  passing_score INT DEFAULT 70,            -- 합격 점수
  
  -- 잠금 설정
  locked BOOLEAN DEFAULT FALSE,
  unlock_condition VARCHAR(500),           -- "SIM-001 완료 후 해제"
  
  -- 태그
  tags TEXT[],                             -- ['카드분실', '재발급', '기본상담']
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_simulation_scenarios_difficulty ON simulation_scenarios(difficulty);
CREATE INDEX idx_simulation_scenarios_category ON simulation_scenarios(category);
CREATE INDEX idx_simulation_scenarios_locked ON simulation_scenarios(locked);
```

---

### 2. simulation_results (시뮬레이션 결과)

**목적:** 각 시뮬레이션 수행 결과 저장

```sql
CREATE TABLE simulation_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  employee_id VARCHAR(50) REFERENCES employees(id),
  
  -- ⭐ 시뮬레이션 유형
  simulation_type VARCHAR(20) NOT NULL,    -- 'best_practice' or 'scenario'
  
  -- 우수사례 시뮬레이션
  original_consultation_id VARCHAR(50) REFERENCES consultations(id),  -- is_best_practice=true
  
  -- 기본 시나리오 시뮬레이션
  scenario_id VARCHAR(50) REFERENCES simulation_scenarios(id),
  
  -- 생성된 시뮬레이션 상담 ID
  simulation_consultation_id VARCHAR(50) UNIQUE NOT NULL,
  
  -- 결과
  overall_score INT,                       -- 종합 점수
  passed BOOLEAN,                          -- 합격 여부
  
  -- ⭐ 우수사례용 평가
  similarity_score INT,                    -- 우수사례 유사도 (0-100)
  keyword_match_score INT,
  document_match_score INT,
  sequence_match_score INT,
  time_comparison JSONB,                   -- 시간 비교
  /*
  예시:
  {
    "original_duration": 327,              // 우수사례 통화 시간
    "simulation_duration": 345,            // 시뮬레이션 통화 시간
    "difference": 18,                      // 차이 (초)
    "percentage": 105.5,                   // 비율 (%)
    "efficiency": "slower"                 // faster, similar, slower
  }
  */
  
  -- ⭐ 기본 시나리오용 평가
  objective_completion_rate INT,           -- 목표 달성률 (0-100)
  document_usage_score INT,
  keyword_coverage_score INT,
  sequence_correctness_score INT,
  customer_satisfaction_score INT,
  
  -- 상세 피드백
  feedback_data JSONB,
  /*
  예시:
  {
    "strengths": [
      "고객 본인 확인 절차 정확히 수행",
      "필수 문서 모두 참조",
      "공감 표현 우수"
    ],
    "improvements": [
      "응대 속도가 우수사례 대비 15% 느림",
      "'재발급 배송 안내' 문서 참조 누락"
    ],
    "expert_tips": [
      "즉시 카드 정지 → 재발급 순서 중요",
      "고객 불안감 해소를 위한 공감 표현 필수"
    ],
    "comparison": [
      {
        "aspect": "고객 본인 확인",
        "you_did": "이름, 생년월일 확인",
        "expert_did": "이름, 생년월일, 카드번호 뒷 4자리 확인",
        "difference": "카드번호 확인 추가 필요"
      }
    ]
  }
  */
  
  -- AI 고객 반응 로그 (기본 시나리오만)
  ai_customer_reactions JSONB,
  /*
  예시:
  [
    {
      "time": "00:30",
      "trigger": "empathy_high",
      "agent_said": "걱정하지 마세요, 빠르게 처리해드리겠습니다",
      "customer_reaction": "네, 감사합니다",
      "emotion": "calm"
    },
    {
      "time": "01:45",
      "trigger": "card_stopped",
      "agent_said": "카드 정지 처리 완료되었습니다",
      "customer_reaction": "정말요? 확인되었어요?",
      "emotion": "relieved"
    }
  ]
  */
  
  -- 통화 정보
  call_duration INT,                       -- 통화 시간 (초)
  call_started_at TIMESTAMP,
  call_ended_at TIMESTAMP,
  
  -- 녹음 파일
  recording_file_path VARCHAR(500),
  recording_transcript TEXT,               -- 마스킹된 녹취록
  
  created_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_simulation_results_employee ON simulation_results(employee_id, created_at DESC);
CREATE INDEX idx_simulation_results_type ON simulation_results(simulation_type);
CREATE INDEX idx_simulation_results_passed ON simulation_results(passed);
CREATE INDEX idx_simulation_results_score ON simulation_results(overall_score DESC);

-- 체크 제약
ALTER TABLE simulation_results ADD CONSTRAINT chk_simulation_type 
  CHECK (simulation_type IN ('best_practice', 'scenario'));
```

---

### 3. employee_learning_analytics (학습 분석)

**목적:** 개인별 학습 성과 및 분석 데이터

```sql
CREATE TABLE employee_learning_analytics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  employee_id VARCHAR(50) REFERENCES employees(id) UNIQUE,
  
  -- 전체 통계
  total_simulations INT DEFAULT 0,
  total_best_practice_simulations INT DEFAULT 0,
  total_scenario_simulations INT DEFAULT 0,
  
  -- 평균 점수
  average_score DECIMAL(5,2),
  average_similarity_score DECIMAL(5,2),           -- 우수사례 유사도
  average_objective_completion DECIMAL(5,2),       -- 시나리오 목표 달성률
  
  -- 합격률
  pass_rate DECIMAL(5,2),
  best_practice_pass_rate DECIMAL(5,2),
  scenario_pass_rate DECIMAL(5,2),
  
  -- 개선율 (최근 vs 초기)
  improvement_rate DECIMAL(5,2),
  /*
  계산 방식:
  최근 5회 평균 점수 - 초기 5회 평균 점수
  */
  
  -- 강점/약점
  strengths JSONB,
  /*
  예시:
  [
    {"skill": "키워드 추출", "score": 92},
    {"skill": "문서 참조", "score": 88},
    {"skill": "공감 표현", "score": 85}
  ]
  */
  weaknesses JSONB,
  /*
  예시:
  [
    {"skill": "응대 시간", "score": 65},
    {"skill": "처리 순서", "score": 70},
    {"skill": "명확한 안내", "score": 72}
  ]
  */
  
  -- 카테고리별 성과
  category_performance JSONB,
  /*
  예시:
  {
    "카드분실": {
      "attempts": 5,
      "avg_score": 85.4,
      "pass_rate": 80.0,
      "best_score": 92
    },
    "해외결제": {
      "attempts": 3,
      "avg_score": 90.3,
      "pass_rate": 100.0,
      "best_score": 95
    }
  }
  */
  
  -- 완료한 시나리오
  completed_scenarios TEXT[],                      -- ['SIM-001', 'SIM-002']
  unlocked_scenarios TEXT[],                       -- ['SIM-001', 'SIM-002', 'SIM-003']
  
  -- 학습 시간
  total_learning_time_seconds INT DEFAULT 0,
  
  -- 최근 활동
  last_simulation_at TIMESTAMP,
  last_simulation_score INT,
  
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_learning_analytics_employee ON employee_learning_analytics(employee_id);
CREATE INDEX idx_learning_analytics_score ON employee_learning_analytics(average_score DESC);
CREATE INDEX idx_learning_analytics_improvement ON employee_learning_analytics(improvement_rate DESC);
```

---

## 📊 샘플 데이터

### simulation_scenarios 샘플

```sql
INSERT INTO simulation_scenarios (
  id, title, difficulty, category, description, duration_estimate,
  scenario_objectives, scenario_steps, required_documents, required_keywords,
  ai_customer_persona, ai_customer_name, ai_customer_background,
  ai_conversation_flow, evaluation_criteria, passing_score, locked, tags
) VALUES 
(
  'SIM-001',
  '카드 분실 신고 및 재발급',
  '초급',
  '카드분실',
  '고객의 카드 분실 신고를 접수하고 재발급 절차를 안내하는 시나리오',
  300,
  '["카드 즉시 정지 처리", "재발급 신청 완료", "배송 정보 안내"]'::jsonb,
  '[
    {"step": 1, "action": "고객 본인 확인", "documents": ["card-1-1-1"]},
    {"step": 2, "action": "카드 즉시 정지", "documents": ["card-1-1-2"]},
    {"step": 3, "action": "재발급 신청", "documents": ["card-1-1-3"]}
  ]'::jsonb,
  ARRAY['card-1-1-1', 'card-1-1-2', 'card-1-1-3'],
  ARRAY['본인확인', '즉시정지', '재발급', '배송'],
  '급한성향',
  '김민수',
  '어제 지갑을 분실하여 카드도 함께 없어짐. 부정 사용이 걱정되어 빠른 처리 원함.',
  '{
    "initial": {
      "message": "안녕하세요, 카드를 분실했어요! 빨리 정지시켜주세요!",
      "emotion": "urgent"
    },
    "responses": {
      "empathy_high": {
        "trigger": ["걱정", "안심", "빠르게"],
        "message": "네, 빨리 처리해주셔서 감사합니다.",
        "emotion": "calm"
      }
    }
  }'::jsonb,
  '{
    "document_usage": {"weight": 30},
    "keyword_coverage": {"weight": 25},
    "sequence_correctness": {"weight": 25},
    "customer_satisfaction": {"weight": 20}
  }'::jsonb,
  70,
  FALSE,
  ARRAY['카드분실', '재발급', '기본상담']
),
(
  'SIM-002',
  '해외 결제 차단 해제 요청',
  '중급',
  '해외결제',
  '해외 여행 중 카드 결제가 차단된 고객의 문의를 처리하는 시나리오',
  420,
  '["해외 결제 차단 사유 확인", "차단 해제 처리", "사용 가능 국가 안내"]'::jsonb,
  '[
    {"step": 1, "action": "고객 본인 확인 및 현재 위치 확인", "documents": ["overseas-1-1"]},
    {"step": 2, "action": "해외 결제 차단 해제", "documents": ["overseas-1-2"]},
    {"step": 3, "action": "사용 가능 국가 및 주의사항 안내", "documents": ["overseas-1-3"]}
  ]'::jsonb,
  ARRAY['overseas-1-1', 'overseas-1-2', 'overseas-1-3'],
  ARRAY['본인확인', '현재위치', '차단해제', '사용가능국가'],
  '급한성향',
  '박철수',
  '일본 여행 중 카드가 결제되지 않음. 긴급히 해결 필요.',
  '{
    "initial": {
      "message": "지금 일본인데 카드가 안 돼요! 급해요!",
      "emotion": "urgent"
    }
  }'::jsonb,
  '{
    "document_usage": {"weight": 30},
    "keyword_coverage": {"weight": 25},
    "sequence_correctness": {"weight": 25},
    "customer_satisfaction": {"weight": 20}
  }'::jsonb,
  70,
  FALSE,
  ARRAY['해외결제', '차단해제', '긴급처리']
);
```

---

## 🔄 데이터 흐름

### A. 우수사례 시뮬레이션

```
1. 교육 시뮬레이션 페이지
   ↓
2. 우수 사례 "학습하기" 클릭
   ↓
3. RealTimeConsultationPage
   - simulation_type = 'best_practice'
   - original_consultation_id = 'CS-EMP001-...'
   ↓
4. 상담 진행 (정해진 스크립트)
   ↓
5. 상담 종료
   ↓
6. simulation_results 테이블에 저장
   - similarity_score 계산
   - keyword_match_score 계산
   - document_match_score 계산
   ↓
7. employee_learning_analytics 업데이트
```

### B. 기본 시나리오 시뮬레이션

```
1. 교육 시뮬레이션 페이지
   ↓
2. 기본 시나리오 "시작하기" 클릭
   ↓
3. RealTimeConsultationPage
   - simulation_type = 'scenario'
   - scenario_id = 'SIM-001'
   ↓
4. 상담 진행 (AI 인터랙티브)
   ↓
5. 상담 종료
   ↓
6. simulation_results 테이블에 저장
   - objective_completion_rate 계산
   - customer_satisfaction_score 계산
   ↓
7. employee_learning_analytics 업데이트
```

---

## 🔗 테이블 관계도

```
employees
    │
    ├─→ simulation_results
    │       ├─→ consultations (original_consultation_id)
    │       └─→ simulation_scenarios (scenario_id)
    │
    └─→ employee_learning_analytics
```

---

## 📝 주요 쿼리 예시

### 1. 상담사별 학습 현황 조회

```sql
SELECT 
  e.id,
  e.name,
  ela.total_simulations,
  ela.average_score,
  ela.pass_rate,
  ela.improvement_rate
FROM employees e
LEFT JOIN employee_learning_analytics ela ON e.id = ela.employee_id
WHERE e.role = 'agent'
ORDER BY ela.average_score DESC;
```

### 2. 특정 시나리오 평균 점수

```sql
SELECT 
  ss.title,
  COUNT(sr.id) as attempts,
  AVG(sr.overall_score) as avg_score,
  SUM(CASE WHEN sr.passed THEN 1 ELSE 0 END)::FLOAT / COUNT(sr.id) * 100 as pass_rate
FROM simulation_scenarios ss
LEFT JOIN simulation_results sr ON ss.id = sr.scenario_id
GROUP BY ss.id, ss.title
ORDER BY avg_score DESC;
```

### 3. 개인별 카테고리 성과

```sql
SELECT 
  e.name,
  c.category,
  COUNT(sr.id) as attempts,
  AVG(sr.overall_score) as avg_score
FROM employees e
JOIN simulation_results sr ON e.id = sr.employee_id
JOIN consultations c ON sr.original_consultation_id = c.id
  OR EXISTS (
    SELECT 1 FROM simulation_scenarios ss 
    WHERE ss.id = sr.scenario_id AND ss.category = c.category
  )
GROUP BY e.id, e.name, c.category
ORDER BY e.name, avg_score DESC;
```

---

## ✅ 체크리스트

- [x] simulation_scenarios 테이블 정의
- [x] simulation_results 테이블 정의
- [x] employee_learning_analytics 테이블 정의
- [x] 샘플 데이터 작성
- [x] 데이터 흐름 정의
- [x] 테이블 관계도 작성
- [x] 주요 쿼리 예시 작성

---

**작성자:** AI Assistant  
**마지막 업데이트:** 2025-01-23  
**Phase:** 12  
**상태:** 📝 설계 완료
