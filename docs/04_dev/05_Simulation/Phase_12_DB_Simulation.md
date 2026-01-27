# Phase 12: DB 스키마 - 시뮬레이션 교육 시스템

## 문서 개요

**목적:** 교육 시뮬레이션 시스템을 위한 DB 스키마 정의

**작성 일자:** 2026-01-23
**최종 수정일:** 2026-01-24
**Phase:** 12
**상태:** **구현 완료**

---

## DB 테이블 구조

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
  scenario_steps JSONB,                    -- 단계별 가이드
  required_documents TEXT[],               -- 필수 참조 문서 ID
  required_keywords TEXT[],                -- 필수 키워드

  -- AI 고객 설정
  ai_customer_persona VARCHAR(50),         -- '급한성향', '꼼꼼한성향', ...
  ai_customer_name VARCHAR(100),           -- '김민수'
  ai_customer_background TEXT,             -- 고객 배경 정보

  -- AI 인터랙티브 대화 흐름
  ai_conversation_flow JSONB,

  -- 평가 기준
  evaluation_criteria JSONB,
  passing_score INT DEFAULT 70,            -- 합격 점수

  -- 잠금 설정
  locked BOOLEAN DEFAULT FALSE,
  unlock_condition VARCHAR(500),           -- "SIM-001 완료 후 해제"

  -- 태그
  tags TEXT[],                             -- ['카드분실', '재발급', '기본상담']

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

#### ai_conversation_flow 구조

```json
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
```

#### evaluation_criteria 구조

```json
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
```

---

### 2. simulation_results (시뮬레이션 결과)

**목적:** 각 시뮬레이션 수행 결과 저장

```sql
CREATE TABLE simulation_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  employee_id VARCHAR(50) REFERENCES employees(id),

  -- 시뮬레이션 유형
  simulation_type VARCHAR(20) NOT NULL,    -- 'best_practice' or 'scenario'

  -- 우수사례 시뮬레이션
  original_consultation_id VARCHAR(50) REFERENCES consultations(id),

  -- 기본 시나리오 시뮬레이션
  scenario_id VARCHAR(50) REFERENCES simulation_scenarios(id),

  -- 생성된 시뮬레이션 상담 ID
  simulation_consultation_id VARCHAR(50) UNIQUE NOT NULL,

  -- 결과
  overall_score INT,                       -- 종합 점수
  passed BOOLEAN,                          -- 합격 여부

  -- 우수사례용 평가
  similarity_score INT,                    -- 우수사례 유사도 (0-100)
  keyword_match_score INT,
  document_match_score INT,
  sequence_match_score INT,
  time_comparison JSONB,                   -- 시간 비교

  -- 기본 시나리오용 평가
  objective_completion_rate INT,           -- 목표 달성률 (0-100)
  document_usage_score INT,
  keyword_coverage_score INT,
  sequence_correctness_score INT,
  customer_satisfaction_score INT,

  -- 상세 피드백
  feedback_data JSONB,

  -- AI 고객 반응 로그
  ai_customer_reactions JSONB,

  -- 통화 정보
  call_duration INT,                       -- 통화 시간 (초)
  call_started_at TIMESTAMP,
  call_ended_at TIMESTAMP,

  -- 녹음 파일
  recording_file_path VARCHAR(500),
  recording_transcript TEXT,               -- 마스킹된 녹취록

  created_at TIMESTAMP DEFAULT NOW(),

  CONSTRAINT chk_simulation_type CHECK (simulation_type IN ('best_practice', 'scenario'))
);
```

#### time_comparison 구조

```json
{
  "original_duration": 327,
  "simulation_duration": 345,
  "difference": 18,
  "percentage": 105.5,
  "efficiency": "slower"
}
```

#### feedback_data 구조

```json
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
  average_similarity_score DECIMAL(5,2),
  average_objective_completion DECIMAL(5,2),

  -- 합격률
  pass_rate DECIMAL(5,2),
  best_practice_pass_rate DECIMAL(5,2),
  scenario_pass_rate DECIMAL(5,2),

  -- 개선율
  improvement_rate DECIMAL(5,2),

  -- 강점/약점
  strengths JSONB,
  weaknesses JSONB,

  -- 카테고리별 성과
  category_performance JSONB,

  -- 완료한 시나리오
  completed_scenarios TEXT[],
  unlocked_scenarios TEXT[],

  -- 학습 시간
  total_learning_time_seconds INT DEFAULT 0,

  -- 최근 활동
  last_simulation_at TIMESTAMP,
  last_simulation_score INT,

  updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 샘플 시나리오

| ID | 제목 | 난이도 | 카테고리 | 합격점수 |
|----|------|--------|----------|----------|
| SIM-001 | 카드 분실 신고 및 재발급 | 초급 | 카드분실 | 70 |
| SIM-002 | 해외 결제 차단 해제 요청 | 중급 | 해외결제 | 70 |
| SIM-003 | 포인트 적립 누락 문의 | 초급 | 포인트 | 70 |
| SIM-004 | 분할결제 취소 요청 | 중급 | 결제취소 | 70 |
| SIM-005 | 이중결제 환불 요청 | 고급 | 이중결제 | 75 |

---

## 데이터 흐름

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

## 테이블 관계도

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

## 주요 쿼리 예시

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
  ss.category,
  COUNT(sr.id) as attempts,
  AVG(sr.overall_score) as avg_score
FROM employees e
JOIN simulation_results sr ON e.id = sr.employee_id
JOIN simulation_scenarios ss ON sr.scenario_id = ss.id
WHERE sr.simulation_type = 'scenario'
GROUP BY e.id, e.name, ss.category
ORDER BY e.name, avg_score DESC;
```

---

## 실행 방법

```bash
cd backend_dev/app/db/scripts

# 시뮬레이션 테이블 생성 및 샘플 데이터 적재
python -c "
import psycopg2
conn = psycopg2.connect(host='localhost', port=5555, user='callact_admin', password='callact_pwd1', database='callact_db')
cursor = conn.cursor()
with open('10_setup_simulation_tables.sql', 'r', encoding='utf-8') as f:
    cursor.execute(f.read())
conn.commit()
conn.close()
print('[OK] 10_setup_simulation_tables.sql')
"
```

---

## 버전 이력

| 날짜 | 변경 내용 |
|------|----------|
| 2026-01-24 | SQL 스크립트 생성 (10_setup_simulation_tables.sql), README 업데이트 |
| 2026-01-23 | 설계 완료 |

---

**관련 파일:**
- SQL 스크립트: `backend_dev/app/db/scripts/10_setup_simulation_tables.sql`
- README: `backend_dev/app/db/scripts/README.md`
