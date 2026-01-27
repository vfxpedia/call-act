# CALL:ACT 3개 데이터베이스 구조

## 1. 개요

CALL:ACT 시스템은 **3개의 하이브리드 데이터베이스(RDB + VectorDB)**를 활용하여 상담사에게 실시간 정보를 제공합니다.

### 1.1 데이터베이스 구성

| DB 이름 | 주요 내용 | RDB | VectorDB |
|---------|----------|-----|----------|
| 카드 정보 DB | 카드 상품, 혜택, 수수료 | O | O |
| 카드사 이용 안내 DB | 공지사항, 자주 찾는 문의, 신용카드 사용 가이드, 금융안내, 소비자 주의 경보 | O (공지/문의) | O |
| 상담 사례 DB | 과거 상담 데이터, 교육 시나리오, 우수 사례 | O | O |

---

## 2. DB 1. 카드 정보 DB

### 2.1 개요

카드 상품, 혜택, 수수료, 포인트 정책 등 **카드 자체에 대한 정보**를 저장하는 데이터베이스입니다.

### 2.2 RDB 테이블 구조

```sql
-- 카드 상품 마스터
CREATE TABLE card_products (
  id VARCHAR(50) PRIMARY KEY,                    -- 'CARD-001'
  name VARCHAR(200),                             -- '하나카드 원큐 VIVA 체크카드'
  card_type VARCHAR(50),                         -- '신용카드', '체크카드'
  brand VARCHAR(50),                             -- 'VISA', 'MasterCard'
  annual_fee_domestic INT,                       -- 국내전용 연회비
  annual_fee_global INT,                         -- 해외겸용 연회비
  performance_condition TEXT,                    -- 실적 조건
  main_benefits TEXT,                            -- 주요 혜택 (간략)
  status VARCHAR(20),                            -- '정상판매', '판매중지'
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- 카드 혜택 상세
CREATE TABLE card_benefits (
  id SERIAL PRIMARY KEY,
  card_id VARCHAR(50) REFERENCES card_products(id),
  category VARCHAR(100),                         -- '주유', '커피', '편의점', '통신비'
  benefit_type VARCHAR(50),                      -- '할인', '포인트적립', '캐시백'
  benefit_rate DECIMAL(5,2),                     -- 5.00 (5% 할인)
  benefit_limit INT,                             -- 월 한도 (원)
  condition_text TEXT,                           -- '월 30만원 이상 이용시'
  partner_name VARCHAR(200),                     -- '제휴사명 (SK에너지, 스타벅스 등)'
  created_at TIMESTAMP
);

-- 수수료 정보
CREATE TABLE fee_info (
  id SERIAL PRIMARY KEY,
  fee_type VARCHAR(100),                         -- '해외수수료', '현금서비스수수료', '연회비'
  card_id VARCHAR(50) REFERENCES card_products(id),
  fee_rate DECIMAL(5,2),                         -- 1.50 (1.5%)
  fixed_fee INT,                                 -- 고정 수수료 (원)
  description TEXT,
  exemption_condition TEXT,                      -- 면제 조건
  created_at TIMESTAMP
);

-- 포인트 정책
CREATE TABLE point_policy (
  id SERIAL PRIMARY KEY,
  card_id VARCHAR(50) REFERENCES card_products(id),
  category VARCHAR(100),                         -- '일반가맹점', '해외가맹점'
  point_rate DECIMAL(5,2),                       -- 0.50 (0.5% 적립)
  point_unit INT,                                -- 적립 단위 (1000원당)
  expiry_months INT,                             -- 포인트 유효기간 (개월)
  created_at TIMESTAMP
);

-- 프로모션 정보
CREATE TABLE promotions (
  id VARCHAR(50) PRIMARY KEY,                    -- 'PROMO-2025-001'
  title VARCHAR(200),                            -- '하나카드x메가커피 프로모션'
  card_id VARCHAR(50) REFERENCES card_products(id),
  start_date DATE,
  end_date DATE,
  benefit_description TEXT,
  conditions TEXT,
  target_customer TEXT,                          -- '신규고객', '전체', '우수고객'
  status VARCHAR(20),                            -- '진행중', '종료'
  created_at TIMESTAMP
);
```

### 2.3 VectorDB 문서 구조

```json
{
  "id": "DOC-CARD-BENEFIT-001",
  "database": "card_info",
  "document_type": "card_benefit",
  "card_id": "CARD-001",
  "card_name": "하나카드 원큐 VIVA 체크카드",
  "category": "주유",
  "title": "주유 할인 혜택 안내",
  "keywords": ["주유", "할인", "SK에너지", "GS칼텍스", "리터당100원"],
  "content": "하나카드 VIVA 체크카드로 SK에너지, GS칼텍스에서 결제 시 리터당 100원 할인됩니다. 월 최대 5만원까지 할인 가능하며, 전월 실적 30만원 이상 시 적용됩니다.",
  "embedding": [0.123, -0.456, 0.789, ...],
  "metadata": {
    "benefit_rate": 100,
    "monthly_limit": 50000,
    "condition": "전월 실적 30만원 이상",
    "partner": "SK에너지, GS칼텍스",
    "priority": "high",
    "usage_count": 127,
    "last_updated": "2025-01-05T10:00:00Z"
  }
}
```

### 2.4 활용 페이지

- **실시간 상담 페이지**: AI 어시스턴트, 칸반보드 (카드 정보/혜택 문의 시)
- **상담 후처리 페이지**: 카드 정보 관련 상담 요약
- **관리자 페이지**: 카드 상품 관리

---

## 3. DB 2. 카드사 이용 안내 DB

### 3.1 개요

카드 사용 방법, 금융 안내, 공지사항, 자주 찾는 문의 등 **카드사 서비스 전반에 대한 안내**를 저장하는 데이터베이스입니다.

### 3.2 RDB 테이블 구조

```sql
-- 공지사항 (RDB 전용)
CREATE TABLE notices (
  id VARCHAR(50) PRIMARY KEY,                    -- 'NOTICE-2025-001'
  title VARCHAR(300),
  content TEXT,
  category VARCHAR(50),                          -- '시스템', '서비스', '긴급'
  priority VARCHAR(20),                          -- '일반', '중요', '긴급'
  is_pinned BOOLEAN DEFAULT false,               -- 상단 고정 여부
  start_date DATE,
  end_date DATE,
  status VARCHAR(20),                            -- '게시중', '종료'
  created_by VARCHAR(50),                        -- 작성자 ID
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- 자주 찾는 문의 (RDB 전용)
CREATE TABLE frequent_inquiries (
  id SERIAL PRIMARY KEY,
  category VARCHAR(100),                         -- '카드분실', '해외결제', '수수료'
  question TEXT,                                 -- '연회비는 언제 청구되나요?'
  answer TEXT,                                   -- '카드 발급일 기준 1년 후...'
  view_count INT DEFAULT 0,                      -- 조회수
  is_active BOOLEAN DEFAULT true,                -- 활성화 여부
  display_order INT,                             -- 표시 순서
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- 문의 조회 로그
CREATE TABLE inquiry_view_log (
  id SERIAL PRIMARY KEY,
  inquiry_id INT REFERENCES frequent_inquiries(id),
  viewed_by VARCHAR(50),                         -- 조회한 사용자 ID
  viewed_at TIMESTAMP
);
```

### 3.3 VectorDB 문서 구조

```json
{
  "id": "DOC-GUIDE-001",
  "database": "service_guide",
  "document_type": "usage_guide",
  "category": "신용카드사용가이드",
  "title": "신용카드 안전 사용 수칙",
  "keywords": ["신용카드", "안전", "보안", "비밀번호", "부정사용"],
  "content": "신용카드 사용 시 비밀번호는 타인에게 노출하지 않도록 주의하세요. 카드 뒷면 서명란에 반드시 서명하고, 분실 시 즉시 고객센터로 신고해야 합니다...",
  "embedding": [0.234, -0.567, 0.890, ...],
  "metadata": {
    "document_source": "금융감독원 가이드라인",
    "priority": "high",
    "last_updated": "2025-01-05T10:00:00Z"
  }
}
```

```json
{
  "id": "DOC-ALERT-001",
  "database": "service_guide",
  "document_type": "consumer_alert",
  "category": "소비자주의경보",
  "title": "스미싱 문자 주의 경보",
  "keywords": ["스미싱", "문자", "사기", "피싱", "주의"],
  "content": "최근 하나카드를 사칭한 스미싱 문자가 발송되고 있습니다. 카드 정보를 요구하는 문자는 절대 응답하지 마시고, 의심되는 경우 고객센터로 문의하세요...",
  "embedding": [0.345, -0.678, 0.901, ...],
  "metadata": {
    "alert_level": "high",
    "issue_date": "2025-01-03",
    "expiry_date": "2025-02-03",
    "affected_customers": "전체"
  }
}
```

### 3.4 활용 페이지

- **대시보드**: 공지사항, 자주 찾는 문의
- **공지사항 페이지**: 전체 공지사항 조회
- **실시간 상담 페이지**: AI 어시스턴트 (소비자 주의 경보 안내)

---

## 4. DB 3. 상담 사례 DB

### 4.1 개요

과거 상담 데이터, 교육 시나리오, 우수 상담 사례 등 **실제 상담 이력**을 저장하는 데이터베이스입니다.

### 4.2 RDB 테이블 구조

```sql
-- 상담 마스터
CREATE TABLE consultations (
  id VARCHAR(50) PRIMARY KEY,                    -- 'CS-20250105-1432'
  customer_id VARCHAR(50) NOT NULL,              -- 'CUST-001'
  agent_id VARCHAR(50) NOT NULL,                 -- 'EMP-001'
  status VARCHAR(20),                            -- '완료', '진행중', '미완료'
  category VARCHAR(50),                          -- '카드분실', '해외결제'
  title TEXT,                                    -- '카드 분실 신고 및 재발급 요청'
  call_date DATE,
  call_time TIME,
  call_duration VARCHAR(20),                     -- '5:23'
  fcr BOOLEAN,                                   -- First Call Resolution
  is_best_practice BOOLEAN DEFAULT false,        -- 우수 사례 여부
  quality_score INT,                             -- 품질 점수 (0-100)
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- 고객 정보
CREATE TABLE customers (
  id VARCHAR(50) PRIMARY KEY,                    -- 'CUST-001'
  name VARCHAR(100),
  phone VARCHAR(20),
  birth_date DATE,
  address TEXT,
  card_id VARCHAR(50),                           -- 보유 카드 ID
  created_at TIMESTAMP
);

-- 상담 전문 (STT 결과)
CREATE TABLE consultation_transcripts (
  id SERIAL PRIMARY KEY,
  consultation_id VARCHAR(50) REFERENCES consultations(id),
  speaker VARCHAR(20),                           -- 'customer' or 'agent'
  message TEXT,
  timestamp TIME,
  sentiment VARCHAR(20),                         -- '긍정', '중립', '부정'
  created_at TIMESTAMP
);

-- 상담 요약 및 후처리
CREATE TABLE consultation_summaries (
  id SERIAL PRIMARY KEY,
  consultation_id VARCHAR(50) REFERENCES consultations(id),
  ai_summary TEXT,                               -- AI 생성 요약
  memo TEXT,                                     -- 상담사 메모
  follow_up_tasks TEXT,                          -- 후속 일정
  handoff_department VARCHAR(100),               -- 이관 부서
  handoff_notes TEXT,                            -- 이관 사항
  created_at TIMESTAMP
);

-- 감정 분석 및 피드백
CREATE TABLE consultation_feedback (
  id SERIAL PRIMARY KEY,
  consultation_id VARCHAR(50) REFERENCES consultations(id),
  emotion_start VARCHAR(20),                     -- '부정적', '중립', '긍정적'
  emotion_middle VARCHAR(20),
  emotion_end VARCHAR(20),
  quality_score VARCHAR(10),                     -- '상', '중', '하'
  processing_time_score INT,                     -- 후처리 소요 시간 점수
  gratitude_score INT,                           -- 감사 표현 비율 점수
  emotion_shift_score INT,                       -- 감정 전환 점수
  manual_compliance_score INT,                   -- 매뉴얼 준수 점수
  created_at TIMESTAMP
);

-- STT 키워드
CREATE TABLE stt_keywords (
  id SERIAL PRIMARY KEY,
  consultation_id VARCHAR(50) REFERENCES consultations(id),
  keyword VARCHAR(100),
  confidence FLOAT,                              -- 신뢰도 (0-1)
  created_at TIMESTAMP
);

-- 교육 시나리오
CREATE TABLE training_scenarios (
  id VARCHAR(50) PRIMARY KEY,                    -- 'SIM-001'
  title VARCHAR(200),                            -- '카드 분실 신고 및 재발급'
  description TEXT,                              -- 시나리오 설명
  difficulty VARCHAR(20),                        -- '초급', '중급', '고급'
  estimated_duration VARCHAR(20),                -- '5분', '10분'
  category VARCHAR(50),                          -- '카드분실', '해외결제'
  tags TEXT[],                                   -- ['카드분실', '재발급', '기본상담']
  scenario_type VARCHAR(50),                     -- 'real_case', 'llm_generated'
  source_consultation_id VARCHAR(50),            -- 실제 사례 기반인 경우 원본 상담 ID
  is_locked BOOLEAN DEFAULT false,               -- 잠금 여부
  unlock_condition TEXT,                         -- 잠금 해제 조건
  pass_score INT DEFAULT 80,                     -- 합격 점수
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- 시나리오 대화 스크립트
CREATE TABLE scenario_scripts (
  id SERIAL PRIMARY KEY,
  scenario_id VARCHAR(50) REFERENCES training_scenarios(id),
  step_order INT,                                -- 대화 순서
  speaker VARCHAR(20),                           -- 'customer' or 'agent'
  message TEXT,                                  -- 대화 내용
  expected_keywords TEXT[],                      -- 상담사가 말해야 할 키워드 (평가용)
  created_at TIMESTAMP
);

-- 시나리오 평가 기준
CREATE TABLE scenario_evaluation_criteria (
  id SERIAL PRIMARY KEY,
  scenario_id VARCHAR(50) REFERENCES training_scenarios(id),
  criteria_name VARCHAR(200),                    -- '고객 인사', '분실 확인', '재발급 안내'
  max_score INT,                                 -- 최대 점수
  keywords TEXT[],                               -- 필수 키워드
  created_at TIMESTAMP
);

-- 시나리오 시도 기록
CREATE TABLE scenario_attempts (
  id SERIAL PRIMARY KEY,
  scenario_id VARCHAR(50) REFERENCES training_scenarios(id),
  agent_id VARCHAR(50),                          -- 시도한 상담사 ID
  score INT,                                     -- 획득 점수
  duration VARCHAR(20),                          -- 소요 시간
  completed_at TIMESTAMP,
  evaluation_detail JSONB,                       -- 평가 상세 내역
  created_at TIMESTAMP
);

-- 우수 상담 사례
CREATE TABLE best_practices (
  id SERIAL PRIMARY KEY,
  consultation_id VARCHAR(50) REFERENCES consultations(id),
  title VARCHAR(200),                            -- '진상 고객 대응 우수 사례'
  category VARCHAR(50),                          -- '감정전환', '크로스셀'
  key_takeaway TEXT,                             -- 핵심 포인트
  recommended_for TEXT[],                        -- 추천 대상 ['신입', '중급']
  views INT DEFAULT 0,                           -- 조회수
  created_at TIMESTAMP
);
```

### 4.3 VectorDB 문서 구조

```json
{
  "id": "DOC-CONSULT-001",
  "database": "consultation_cases",
  "document_type": "past_consultation",
  "consultation_id": "CS-20250105-1432",
  "category": "카드분실",
  "title": "카드 분실 신고 및 재발급 처리 사례",
  "keywords": ["카드분실", "재발급", "즉시정지", "배송안내"],
  "content": "고객이 카드를 분실하여 신고 접수. 즉시 카드 사용 정지 처리하고, 재발급 신청 완료. 등록된 주소로 3-5일 내 배송 예정임을 안내하고, SMS로 배송 추적 번호 발송 예정임을 안내.",
  "embedding": [0.456, -0.789, 0.123, ...],
  "metadata": {
    "agent_id": "EMP-001",
    "fcr": true,
    "quality_score": 95,
    "call_duration": "5:23",
    "is_best_practice": true,
    "call_date": "2025-01-05"
  }
}
```

```json
{
  "id": "DOC-SCENARIO-001",
  "database": "consultation_cases",
  "document_type": "training_scenario",
  "scenario_id": "SIM-001",
  "title": "카드 분실 신고 및 재발급 (초급)",
  "keywords": ["교육", "시나리오", "카드분실", "재발급"],
  "content": "고객이 카드를 분실했다고 전화. 상담사는 즉시 카드 정지 처리하고 재발급 절차를 안내해야 함. 배송지 주소를 확인하고 3-5일 내 배송 예정임을 안내.",
  "embedding": [0.567, -0.890, 0.234, ...],
  "metadata": {
    "difficulty": "초급",
    "estimated_duration": "5분",
    "scenario_type": "real_case",
    "source_consultation_id": "CS-20241220-1015",
    "pass_score": 80
  }
}
```

### 4.4 활용 페이지

- **실시간 상담 페이지**: 칸반보드 (과거 유사 사례 검색)
- **상담 후처리 페이지**: 유사 사례 참고 (과거 상담 후처리 방법 표시)
- **교육 시뮬레이션 페이지**: 시나리오 리스트, 시도 기록
- **대시보드**: 우수 사례집
- **상담 내역 페이지**: 전체 과거 상담 조회

---

## 5. 데이터 활용 프로세스

### 5.1 실시간 상담 중

```
1. 고객 전화 인입
   ↓
2. STT 실시간 변환
   ↓
3. 키워드 추출: ["카드분실", "재발급"]
   ↓
4. VectorDB 검색:
   - 카드 정보 DB: 재발급 카드 정보
   - 카드사 이용 안내 DB: 분실 신고 가이드
   - 상담 사례 DB: 과거 유사 상담 사례
   ↓
5. 칸반보드 표시:
   - 현재 상황: "카드 분실 신고 처리 절차" (상담 사례 DB)
   - 다음 단계: "재발급 카드 배송 안내" (카드 정보 DB)
   ↓
6. AI 어시스턴트: 상담사 질문에 즉시 답변
```

### 5.2 상담 후처리

```
1. 상담 종료
   ↓
2. STT 전문 자동 저장 (상담 사례 DB - RDB)
   ↓
3. LLM이 전문 분석 → AI 요약 생성
   ↓
4. VectorDB 검색: 유사 사례 검색 (상담 사례 DB)
   ↓
5. 유사 사례 후처리 방법 표시 (우측 상단 카드)
   ↓
6. 상담사가 AI 생성 문서 수정 후 저장
   ↓
7. 후처리 문서 저장 (RDB + VectorDB 임베딩)
```

### 5.3 교육 시나리오 생성

```
1. 관리자가 우수 상담 사례 선택
   ↓
2. 해당 상담의 STT 전문, 요약, 평가 점수 조회 (RDB)
   ↓
3. LLM이 교육용 시나리오 생성:
   - 실제 사례 기반 시나리오
   - 어려운 상황을 추가한 변형 시나리오
   ↓
4. 시나리오 저장 (training_scenarios, scenario_scripts)
   ↓
5. VectorDB에 임베딩 저장
   ↓
6. 교육 시뮬레이션 페이지에 표시
```

### 5.4 교육 시뮬레이션 진행

```
1. 상담사가 시나리오 선택 → "시작하기" 클릭
   ↓
2. /consultation/live 페이지로 이동 (실제 상담 환경)
   ↓
3. 시나리오 스크립트에 따라 가상 고객 대화 표시
   ↓
4. 상담사가 응답 입력
   ↓
5. 실시간 평가:
   - 필수 키워드 포함 여부 확인
   - 응답 속도 측정
   - STT 전문과 시나리오 기대 응답 비교 (유사도 검색)
   ↓
6. 상담 종료 → /acw 페이지로 이동
   ↓
7. 후처리 작성 (실제 환경과 동일)
   ↓
8. 평가 기준에 따라 점수 산출:
   - 대화 품질 (40%)
   - 후처리 완성도 (30%)
   - 소요 시간 (20%)
   - 매뉴얼 준수 (10%)
   ↓
9. 점수 및 피드백 표시
   ↓
10. 시도 기록 저장 (scenario_attempts)
```

---

## 6. API 엔드포인트 구조

### 6.1 교육 시나리오 관련

```typescript
// 시나리오 목록 조회
GET /api/training/scenarios

// 응답
{
  "scenarios": [
    {
      "id": "SIM-001",
      "title": "카드 분실 신고 및 재발급",
      "difficulty": "초급",
      "duration": "5분",
      "description": "고객의 카드 분실 신고를 접수하고...",
      "tags": ["카드분실", "재발급", "기본상담"],
      "scenarioType": "real_case",
      "isLocked": false,
      "passScore": 80,
      "completed": true,
      "lastScore": 95
    }
  ]
}
```

```typescript
// 시나리오 상세 조회 (시작하기 클릭 시)
GET /api/training/scenarios/{scenarioId}

// 응답
{
  "scenario": {
    "id": "SIM-001",
    "title": "카드 분실 신고 및 재발급",
    "description": "...",
    "difficulty": "초급",
    "estimatedDuration": "5분",
    "passScore": 80
  },
  "scripts": [
    {
      "stepOrder": 1,
      "speaker": "customer",
      "message": "안녕하세요, 카드를 분실했어요.",
      "expectedKeywords": null
    },
    {
      "stepOrder": 2,
      "speaker": "agent",
      "message": null,
      "expectedKeywords": ["인사", "카드정지", "재발급"]
    }
  ],
  "evaluationCriteria": [
    {
      "criteriaName": "고객 인사",
      "maxScore": 10,
      "keywords": ["안녕하세요", "고객님"]
    },
    {
      "criteriaName": "카드 정지 안내",
      "maxScore": 30,
      "keywords": ["즉시정지", "사용정지", "차단"]
    },
    {
      "criteriaName": "재발급 절차 안내",
      "maxScore": 40,
      "keywords": ["재발급", "3-5일", "배송", "주소"]
    }
  ]
}
```

```typescript
// 시나리오 평가 제출
POST /api/training/scenarios/{scenarioId}/evaluate

// 요청
{
  "agentId": "EMP-001",
  "transcript": [
    {"speaker": "agent", "message": "안녕하세요, 고객님...", "timestamp": "14:32:05"},
    {"speaker": "customer", "message": "카드를 분실했어요.", "timestamp": "14:32:10"}
  ],
  "acwDocument": {
    "title": "카드 분실 신고 및 재발급 요청",
    "summary": "고객 카드 분실 신고 접수...",
    "memo": "재발급 카드 배송 추적 필요"
  },
  "duration": "4:50"
}

// 응답
{
  "score": 95,
  "evaluation": {
    "dialogueQuality": 38,    // 40점 만점
    "acwCompleteness": 28,    // 30점 만점
    "timeEfficiency": 19,     // 20점 만점
    "manualCompliance": 10    // 10점 만점
  },
  "feedback": [
    {
      "criteria": "고객 인사",
      "score": 10,
      "maxScore": 10,
      "comment": "우수: 적절한 인사말 사용"
    },
    {
      "criteria": "카드 정지 안내",
      "score": 28,
      "maxScore": 30,
      "comment": "양호: '즉시정지' 키워드 사용, 추가 안내 보완 필요"
    }
  ],
  "passed": true
}
```

### 6.2 유사 사례 검색 (후처리 페이지)

```typescript
POST /api/consultations/similar-acw

// 요청
{
  "currentConsultationId": "CS-20250105-1432",
  "category": "카드분실",
  "keywords": ["분실신고", "재발급"],
  "transcript": "고객이 카드를 분실하여..."
}

// 응답
{
  "similarCases": [
    {
      "consultationId": "CS-20241228-1015",
      "title": "카드 분실 신고 및 재발급",
      "category": "카드분실",
      "acwSummary": "고객 카드 분실 신고 후 재발급 처리. 해외 여행 전 긴급 배송 요청하여 익일 배송으로 변경 처리.",
      "acwMemo": "고객 요청으로 긴급 배송 처리. 추가 비용 5,000원 안내 완료.",
      "followUpTasks": "배송 추적 번호 SMS 발송",
      "handoffDepartment": "카드발급팀",
      "handoffNotes": "긴급 배송 요청 건",
      "similarityScore": 0.94,
      "qualityScore": 95,
      "fcrAchieved": true
    }
  ]
}
```

---

## 7. 프론트엔드 데이터 수신 구조

### 7.1 교육 시뮬레이션 페이지

**현재 Mock 데이터:**
```typescript
const scenarios = [
  {
    id: 'SIM-001',
    title: '카드 분실 신고 및 재발급',
    difficulty: '초급',
    duration: '5분',
    description: '고객의 카드 분실 신고를 접수하고...',
    tags: ['카드분실', '재발급', '기본상담'],
    completed: true,
    score: 95,
    locked: false
  }
];
```

**백엔드 연동 시 필요한 구조:**
```typescript
interface TrainingScenario {
  id: string;                          // 'SIM-001'
  title: string;                       // '카드 분실 신고 및 재발급'
  difficulty: '초급' | '중급' | '고급';
  estimatedDuration: string;           // '5분'
  description: string;
  tags: string[];                      // ['카드분실', '재발급']
  scenarioType: 'real_case' | 'llm_generated';  // 실제 사례 or LLM 생성
  sourceConsultationId?: string;       // 실제 사례 기반인 경우
  isLocked: boolean;
  unlockCondition?: string;            // 잠금 해제 조건
  passScore: number;                   // 합격 점수
  completed: boolean;                  // 완료 여부
  lastScore?: number;                  // 최근 점수
}

interface ScenarioScript {
  stepOrder: number;                   // 대화 순서
  speaker: 'customer' | 'agent';
  message?: string;                    // 고객 대사 (상담사는 null)
  expectedKeywords?: string[];         // 상담사가 말해야 할 키워드
}

interface EvaluationCriteria {
  criteriaName: string;                // '고객 인사'
  maxScore: number;                    // 10
  keywords: string[];                  // ['안녕하세요', '고객님']
}
```

### 7.2 상담 후처리 페이지 (유사 사례 카드)

**현재 Mock 데이터:**
```typescript
const similarCase = {
  category: '카드분실',
  summary: '2024-12-28 처리 사례. 고객 카드 분실 신고 후...'
};
```

**백엔드 연동 시 필요한 구조:**
```typescript
interface SimilarACWCase {
  consultationId: string;              // 'CS-20241228-1015'
  title: string;                       // '카드 분실 신고 및 재발급'
  category: string;                    // '카드분실'
  acwSummary: string;                  // AI 요약본
  acwMemo: string;                     // 상담사 메모
  followUpTasks?: string;              // 후속 일정
  handoffDepartment?: string;          // 이관 부서
  handoffNotes?: string;               // 이관 사항
  similarityScore: number;             // 0.94 (유사도)
  qualityScore: number;                // 95 (품질 점수)
  fcrAchieved: boolean;
  callDate: string;                    // '2024-12-28'
}
```

### 7.3 대시보드 - 자주 찾는 문의

**백엔드 연동 시 필요한 구조:**
```typescript
interface FrequentInquiry {
  id: number;
  category: string;                    // '카드분실'
  question: string;                    // '연회비는 언제 청구되나요?'
  answer: string;                      // '카드 발급일 기준 1년 후...'
  viewCount: number;                   // 조회수
  displayOrder: number;                // 표시 순서
}

// API 호출
GET /api/dashboard/frequent-inquiries?limit=5

// 응답
{
  "inquiries": [
    {
      "id": 1,
      "category": "수수료문의",
      "question": "연회비는 언제 청구되나요?",
      "answer": "카드 발급일 기준 1년 후 청구됩니다...",
      "viewCount": 1542
    }
  ]
}
```

---

## 8. 데이터 흐름 요약

### 8.1 3개 DB 활용 시나리오

**시나리오: 고객이 "연회비 환불" 문의**

```
1. STT 키워드 추출: ["연회비", "환불"]
   ↓
2. VectorDB 검색 (3개 DB 모두):
   
   [카드 정보 DB]
   - "연회비 정책 안내" (0.96)
   - "연회비 환불 절차" (0.92)
   
   [카드사 이용 안내 DB]
   - "신용카드 사용 가이드: 연회비 관리" (0.88)
   
   [상담 사례 DB]
   - "과거 상담 사례: 연회비 환불 요청" (0.94)
   ↓
3. 칸반보드 표시:
   - 현재 상황: "연회비 정책 안내" (카드 정보 DB)
   - 다음 단계: "연회비 환불 절차" (카드 정보 DB)
   ↓
4. AI 어시스턴트:
   - 3개 DB의 검색 결과를 종합하여 답변 생성
   ↓
5. 후처리 페이지:
   - 유사 사례 카드: "과거 연회비 환불 처리 사례" (상담 사례 DB)
```

### 8.2 DB 간 우선순위

| 문의 유형 | 1순위 DB | 2순위 DB | 3순위 DB |
|-----------|----------|----------|----------|
| 카드 상품/혜택 문의 | 카드 정보 DB | 상담 사례 DB | 카드사 이용 안내 DB |
| 분실/재발급 등 업무 처리 | 상담 사례 DB | 카드사 이용 안내 DB | 카드 정보 DB |
| 금융 안내/주의 사항 | 카드사 이용 안내 DB | 상담 사례 DB | - |

---

## 9. 핵심 포인트

### 9.1 3개 DB 역할 분담

- **카드 정보 DB**: 상품, 혜택, 수수료 등 **카드 자체 정보**
- **카드사 이용 안내 DB**: 공지, 가이드, 경보 등 **서비스 안내**
- **상담 사례 DB**: 과거 상담, 시나리오, 우수 사례 등 **실제 업무 사례**

### 9.2 교육 서비스의 차별점

- 실제 과거 상담 데이터로 시나리오 생성
- LLM이 어려운 변형 시나리오 자동 생성
- 실제 상담 환경 (/consultation/live → /acw) 완전 재현
- 유사도 검색 기반 실시간 평가
- 우수 사례를 교육 자료로 활용

### 9.3 후처리 자동화

- STT 전문을 LLM이 분석하여 자동 문서 생성
- 유사 사례 검색으로 과거 후처리 방법 참고
- 상담사가 수정 후 저장 (완전 자동화 X, AI 보조)
