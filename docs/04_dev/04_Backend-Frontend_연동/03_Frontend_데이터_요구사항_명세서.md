# Frontend 데이터 요구사항 명세서

## 메타데이터
- **작성일**: 2026-02-03
- **작성자**: Claude Code
- **버전**: v2.0
- **상태**: 완료
- **변경이력**:
  - v2.0 (2026-02-03): 페르소나 6타입 확정, customers 테이블 정리, 피드백/녹취 필드 추가
- **관련 문서**:
  - [02_실제_DB_스키마_명세서.md](./02_실제_DB_스키마_명세서.md)
  - [17_CALLACT_DB_설계_및_분석.md](../02_db/17_CALLACT_DB_설계_및_분석.md)

## 목적

이 문서는 Frontend에서 요구하는 데이터 필드와 현재 DB 스키마 간의 Gap을 분석하여, Backend API 개발 및 DB 스키마 수정의 기준 문서로 활용합니다.

## 배경

- Frontend 개발이 진행 중이며, 실제 데이터 연동 준비 단계
- Mock 데이터 기반으로 개발되었으나, 실제 DB 스키마와 불일치 존재
- 페이지별 요구 데이터 필드를 명확히 정의하여 Backend와 협업 필요

---

## 확정 사항 (v2.0)

### 페르소나 시스템
| 항목 | 결정 |
|------|------|
| 페르소나 코드 | 팀원 5타입 (N1, N2, S1, S2, S3) |
| 고객당 페르소나 | 1개만 (customer_type_codes 삭제) |
| llm_guidance 위치 | persona_types 테이블에만 |
| personality_tags 위치 | persona_types 테이블에만 |
| communication_style 위치 | persona_types 테이블에만 |
| 데이터 조회 | JOIN (v_customer_with_persona 뷰) |

### 5타입 페르소나 (팀원 LLM 분류 기준 - 2026-02-03 확정)

| 코드 | 이름 | 설명 | LLM Guidance |
|------|------|------|--------------|
| N1 | 일반형 | 큰 특징 없이 바로 문의사항을 말함 | 표준 응대 매뉴얼대로 진행 |
| N2 | 수다형 | 사적인 이야기나 본인 상황을 길게 설명함 | 충분히 경청하고 공감 표현 |
| S1 | 급한성격형 | 빠른 처리를 선호함 | 시간 최소화, 핵심만 전달 |
| S2 | 디지털미아형 | 기술적 조작에 서툴고 앱 사용을 어려워함 | 천천히 단계별로 시각적 안내 |
| S3 | 불만형 | 분노, 짜증을 드러냄 | 먼저 사과, 즉각 해결책 제시 |

### 스키마 변경
- **적용 스크립트**: `14_schema_v4_frontend_integration.sql`
- **customers 삭제 컬럼**: llm_guidance, personality_tags, communication_style, customer_type_codes
- **consultations 추가 컬럼**: 15개 (피드백, 녹취, 후속조치 등)
- **자동 트리거**: total_consultations +1, FCR 자동 계산

---

## 1. 페이지 목록 및 데이터 의존성

| 페이지 | 파일명 | 주요 데이터 | 우선순위 |
|--------|--------|------------|----------|
| 로그인 | `LoginPage.tsx` | employees | P1 |
| 대시보드 | `DashboardPage.tsx` | employees, consultations (통계) | P1 |
| 실시간 상담 | `RealTimeConsultationPage.tsx` | customers, scenarios, RAG documents | P0 (개발중) |
| 로딩 | `LoadingPage.tsx` | LLM 분석 결과 (localStorage) | P1 |
| 후처리 | `AfterCallWorkPage.tsx` | consultations (저장), customers, documents | P0 |
| 상담 내역 | `ConsultationHistoryPage.tsx` | consultations (목록/상세) | P1 |
| 상담사 관리 | `EmployeesPage.tsx` | employees | P2 |
| 프로필 | `ProfilePage.tsx` | employees (현재 로그인 사용자) | P2 |
| 시뮬레이션 | `SimulationPage.tsx` | simulation_scenarios, simulation_results | P3 |
| 공지사항 | `NoticePage.tsx`, `AdminNoticePage.tsx` | notices | P3 |
| 관리자 통계 | `AdminStatsPage.tsx` | consultations, employees (집계) | P2 |
| 관리자 상담관리 | `AdminConsultationManagePage.tsx` | consultations, employees | P2 |

---

## 2. 핵심 타입 정의 (Frontend)

### 2.1 Customer (고객)

**소스**: `src/types/consultation.ts`, `src/data/mockCustomerDB.ts`, `src/data/scenarios/types.ts`

```typescript
interface CustomerInfo {
  // 식별자
  id: string;                    // 'CUST-TEDDY-00001'

  // 기본 정보
  name: string;                  // 실명 (마스킹은 Frontend 처리)
  phone: string;                 // '010-1234-5678'
  birthDate?: string;            // 'YYYY-MM-DD'
  address?: string;              // 전체 주소
  gender?: 'male' | 'female' | 'unknown';
  ageGroup?: string;             // '20대', '30대', ...
  age?: number;                  // 실제 나이

  // 카드 정보
  cardNumber: string;            // 전체 번호 (마스킹 Frontend)
  cardType: string;              // '테디카드 프리미엄'
  cardName?: string;             // 카드 상품명
  cardIssueDate?: string;        // 발급일
  cardExpiryDate?: string;       // 만료일 (MM/YY)
  grade: string;                 // 'VIP' | 'GOLD' | 'SILVER' | 'GENERAL'

  // 페르소나 (12타입 → CN 코드 예정)
  personalityTags?: string[];    // ['practical', 'direct']
  communicationStyle?: {
    speed?: 'fast' | 'moderate' | 'slow';
    tone?: 'formal' | 'neutral' | 'casual' | 'warm' | 'empathetic' | ...;
  };
  traits?: string[];             // UI 표시용 특성 태그
  preferredStyle?: string;       // LLM 가이드 (llm_guidance)

  // 상담 통계
  totalConsultations?: number;
  lastConsultationDate?: string;
}
```

### 2.2 Consultation (상담)

**소스**: `src/types/consultation.ts`

```typescript
interface Consultation {
  // 식별자
  consultationId: string;        // 'CS-EMP002-202601211430'
  employeeId: string;            // 'EMP-002'
  customerId: string;            // 'CUST-TEDDY-00001'

  // 상담 분류
  category: string;              // 대분류 (8개)
  // ⭐ 누락: subcategory (중분류 15개)
  // ⭐ 누락: categoryRaw (57개 원본)
  // ⭐ 누락: handledCategories (복합 상담 시)

  // 상담 내용
  title: string;                 // 상담 제목
  status: string;                // '진행중' | '완료' | '보류'

  // 시간 정보
  datetime: string;              // '2025-01-21 14:30' (상담 시작)
  callTimeSeconds: number;       // 통화 시간 (초)
  acwTimeSeconds: number;        // 후처리 시간 (초)
  // ⭐ 누락: callEndTime (통화 종료 시간)

  // AI 분석 결과
  aiSummary: string;             // LLM 요약
  sentiment?: string;            // 감정 분석
  feedbackScore?: number;        // 피드백 점수 (0-100)
  satisfactionScore?: number;    // 만족도 (1-5)

  // 상담 내용
  memo: string;                  // 상담사 메모
  transcript?: string;           // STT 전문 (문자열)
  // ⭐ 권장: transcript를 JSONB로 (채팅 형식)

  // 후속 조치
  followUpTasks: string;         // 후속 일정
  handoffDepartment: string;     // 이관 부서
  handoffNotes: string;          // 이관 전달사항

  // 참조 문서
  referencedDocuments: ReferencedDocument[];
  referencedDocumentIds: string[];
}
```

### 2.3 ACW Data (후처리 데이터)

**소스**: `src/data/afterCallWorkData/types.ts`

```typescript
interface ACWData {
  aiAnalysis: {
    title: string;               // 상담 제목
    inboundCategory: string;     // 인입 대분류
    handledCategories: string[]; // 처리 분류 배열
    subcategory: string;         // 중분류
    summary: string;             // AI 요약 (마크다운)
    followUpTasks?: string;      // 후속 일정
    handoffDepartment?: string;  // 이관 부서
    handoffNotes?: string;       // 이관 전달사항
  };
  processingTimeline: {
    time: string;                // 'HH:MM:SS'
    action: string;              // 처리 내용
    categoryRaw: string | null;  // 57개 케이스 중 하나
  }[];
  callTranscript: {
    speaker: 'customer' | 'agent';
    message: string;
    timestamp: string;           // 'HH:MM'
  }[];
}
```

### 2.4 Employee (상담사)

**소스**: `src/data/mockData.ts` (추론)

```typescript
interface Employee {
  id: string;                    // 'EMP-001' 또는 'ADMIN-001'
  employeeId: string;            // 표시용 ID
  name: string;
  email?: string;
  role: 'agent' | 'admin';
  department?: string;
  hireDate?: string;
  status?: 'active' | 'inactive' | 'vacation';

  // 성과 지표
  consultations?: number;        // 상담 건수
  fcr?: number;                  // FCR 비율 (0-100)
  avgTime?: string;              // 평균 통화 시간 ('MM:SS')
  rank?: number;                 // 순위
}
```

---

## 3. Gap Analysis: Frontend vs DB

### 3.1 consultations 테이블

| Frontend 필드 | DB 필드 | 상태 | 비고 |
|--------------|---------|------|------|
| `consultationId` | `id` | ✅ 일치 | VARCHAR(50) |
| `employeeId` | `agent_id` | ✅ 일치 | FK to employees |
| `customerId` | `customer_id` | ✅ 일치 | VARCHAR(50) |
| `category` | `category_main` | ✅ 일치 | 대분류 8개 |
| `subcategory` | `category_sub` | ❌ **Frontend 누락** | 중분류 15개 |
| `categoryRaw` | `category_raw` | ❌ **Frontend 누락** | 57개 원본 |
| `handledCategories[]` | `handled_categories` | ❌ **Frontend 누락** | TEXT[] |
| `title` | `title` | ✅ 일치 | TEXT |
| `status` | `status` | ✅ 일치 | ENUM |
| `datetime` | `call_date` + `call_time` | ✅ 일치 | DATE + TIME 조합 |
| `callTimeSeconds` | `call_duration` | ⚠️ 형식 차이 | DB: 'MM:SS' 문자열 |
| `callEndTime` | ❌ **DB 누락** | ❌ 추가 필요 | TIME |
| `acwTimeSeconds` | ❌ **DB 누락** | ❌ 추가 필요 | VARCHAR(20) |
| `aiSummary` | ❌ **DB 누락** | ❌ 추가 필요 | TEXT |
| `memo` | ❌ **DB 누락** | ❌ 추가 필요 | TEXT |
| `transcript` (JSON) | ❌ **DB 누락** | ❌ 추가 필요 | JSONB |
| `processingSteps[]` | `processing_timeline` | ✅ 일치 | JSONB |
| `followUpTasks` | ❌ **DB 누락** | ❌ 추가 필요 | TEXT |
| `handoffDepartment` | ❌ **DB 누락** | ❌ 추가 필요 | VARCHAR(100) |
| `handoffNotes` | ❌ **DB 누락** | ❌ 추가 필요 | TEXT |
| `referencedDocuments` | ❌ **DB 누락** | ❌ 추가 필요 | JSONB |
| `sentiment` | ❌ **DB 누락** | ⚠️ 선택적 | VARCHAR(20) |
| `feedbackScore` | ❌ **DB 누락** | ⚠️ 선택적 | INT |
| `satisfactionScore` | ❌ **DB 누락** | ⚠️ 선택적 | INT |
| `fcr` | `fcr` | ✅ 일치 | BOOLEAN |
| `quality_score` | `quality_score` | ✅ 일치 | INT |

### 3.2 customers 테이블

| Frontend 필드 | DB 필드 | 상태 | 비고 |
|--------------|---------|------|------|
| `id` | `id` | ✅ 일치 | VARCHAR(50) |
| `name` | `name` | ✅ 일치 | |
| `phone` | `phone` | ✅ 일치 | |
| `birthDate` | `birth_date` | ✅ 일치 | DATE |
| `address` | `address` | ✅ 일치 | VARCHAR(300) |
| `gender` | `gender` | ✅ 일치 | VARCHAR(10) |
| `ageGroup` | `age_group` | ✅ 일치 | VARCHAR(10) |
| `age` | ❌ **DB 누락** | ⚠️ 계산 가능 | birth_date에서 계산 |
| `cardNumber` | `card_number_last4` | ⚠️ 부분 일치 | DB는 마지막 4자리만 |
| `cardType` | `card_type` | ✅ 일치 | |
| `cardIssueDate` | `card_issue_date` | ✅ 일치 | DATE |
| `cardExpiryDate` | `card_expiry_date` | ✅ 일치 | DATE |
| `grade` | `grade` | ✅ 일치 | VARCHAR(20) |
| `personalityTags` | ❌ **customers에서 삭제** | ⚠️ persona_types JOIN | v_customer_with_persona 뷰 사용 |
| `communicationStyle` | ❌ **customers에서 삭제** | ⚠️ persona_types JOIN | v_customer_with_persona 뷰 사용 |
| `traits` | ❌ **DB 누락** | ⚠️ Frontend 전용 | UI 표시용 |
| `preferredStyle` | ❌ **customers에서 삭제** | ⚠️ persona_types.llm_guidance | v_customer_with_persona 뷰 사용 |
| `totalConsultations` | `total_consultations` | ✅ 일치 | INT |
| `lastConsultationDate` | `last_consultation_date` | ✅ 일치 | DATE |
| `current_type_code` | `current_type_code` | ✅ 일치 | 6타입 LLM 분류 |
| `type_history` | `type_history` | ✅ 일치 | JSONB |

### 3.3 employees 테이블

| Frontend 필드 | DB 필드 | 상태 | 비고 |
|--------------|---------|------|------|
| `id` | `id` | ✅ 일치 | VARCHAR(50) |
| `name` | `name` | ✅ 일치 | |
| `email` | `email` | ✅ 일치 | |
| `role` | `role` | ✅ 일치 | VARCHAR(50) |
| `department` | `department` | ✅ 일치 | |
| `hireDate` | `hire_date` | ✅ 일치 | DATE |
| `status` | `status` | ✅ 일치 | ENUM |
| `consultations` | `consultations` | ✅ 일치 | INT |
| `fcr` | `fcr` | ✅ 일치 | INT (0-100) |
| `avgTime` | `avgTime` | ✅ 일치 | VARCHAR(10) |
| `rank` | `rank` | ✅ 일치 | INT |

---

## 4. 필수 DB 스키마 수정 사항

### 4.1 consultations 테이블 확장 (필수)

```sql
-- 시간 정보
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS call_end_time TIME;
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS acw_duration VARCHAR(20);

-- 상담 내용
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS transcript JSONB;
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS ai_summary TEXT;
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS agent_notes TEXT;

-- 후속 조치
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS follow_up_schedule TEXT;
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS transfer_department VARCHAR(100);
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS transfer_notes TEXT;

-- 참조 문서
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS referenced_documents JSONB;

-- 선택적: 감정/피드백 분석
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS sentiment VARCHAR(20);
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS feedback_score INT;
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS satisfaction_score INT;
```

### 4.2 transcript JSONB 구조

```json
{
  "messages": [
    {
      "speaker": "customer",
      "message": "안녕하세요, 카드를 분실했어요.",
      "timestamp": "14:32:00"
    },
    {
      "speaker": "agent",
      "message": "안녕하세요. 즉시 카드 사용을 정지하겠습니다.",
      "timestamp": "14:32:15"
    }
  ],
  "total_turns": 5,
  "customer_turns": 3,
  "agent_turns": 2
}
```

### 4.3 processing_timeline JSONB 구조 (기존)

```json
[
  {
    "time": "14:32:30",
    "action": "카드 분실 신고 접수",
    "category": "분실/도난"
  },
  {
    "time": "14:33:15",
    "action": "카드 사용 즉시 정지 처리",
    "category": "분실/도난"
  }
]
```

### 4.4 referenced_documents JSONB 구조

```json
[
  {
    "step_number": 1,
    "doc_id": "DOC-001",
    "doc_type": "terms",
    "title": "카드 분실 처리 규정",
    "used": true,
    "view_count": 2
  },
  {
    "step_number": 2,
    "doc_id": "DOC-002",
    "doc_type": "guide",
    "title": "재발급 안내 가이드",
    "used": true,
    "view_count": 1
  }
]
```

---

## 5. API 엔드포인트 명세

### 5.1 상담 저장 API

**POST** `/api/v1/consultations`

```typescript
// Request Body
interface SaveConsultationRequest {
  consultationId: string;
  employeeId: string;
  customerId: string;

  // 분류
  categoryMain: string;          // 대분류
  categorySub: string;           // 중분류
  categoryRaw?: string;          // 57개 원본
  handledCategories?: string[];  // 복합 상담

  // 기본 정보
  title: string;
  status: 'in_progress' | 'completed';

  // 시간
  callDate: string;              // 'YYYY-MM-DD'
  callTime: string;              // 'HH:MM:SS'
  callEndTime: string;           // 'HH:MM:SS'
  callDuration: string;          // 'MM:SS'
  acwDuration: string;           // 'MM:SS'

  // AI 분석
  aiSummary: string;
  processingTimeline: ProcessingTimelineItem[];

  // 상담 내용
  transcript: TranscriptMessage[];
  agentNotes?: string;

  // 후속 조치
  followUpSchedule?: string;
  transferDepartment?: string;
  transferNotes?: string;

  // 참조 문서
  referencedDocuments?: ReferencedDocument[];

  // 선택적
  sentiment?: string;
  feedbackScore?: number;
  satisfactionScore?: number;
}

// Response
interface SaveConsultationResponse {
  success: boolean;
  data?: {
    consultationId: string;
    fcr: boolean;                // 서버에서 계산
  };
  error?: string;
}
```

### 5.2 고객 정보 조회 API

**GET** `/api/v1/customers/{customerId}`

```typescript
// Response
interface CustomerResponse {
  id: string;
  name: string;
  phone: string;
  birthDate: string | null;
  address: string | null;
  gender: string;
  ageGroup: string;
  grade: string;

  // 카드 정보
  cardType: string;
  cardNumberLast4: string;
  cardIssueDate: string | null;
  cardExpiryDate: string | null;

  // 페르소나
  currentTypeCode: string | null;  // 6타입
  personalityTags: string[];
  communicationStyle: object;
  llmGuidance: string;

  // 통계
  totalConsultations: number;
  lastConsultationDate: string | null;

  // Frontend 계산용
  age: number;                     // 서버에서 계산하여 제공
}
```

### 5.3 고객 페르소나 업데이트 API

**PATCH** `/api/v1/customers/{customerId}/persona`

```typescript
// Request Body (상담 종료 후 호출)
interface UpdatePersonaRequest {
  currentTypeCode: string;        // LLM 분류 결과 (N1, S2 등)
  consultationId: string;         // 이번 상담 ID
  callDate: string;               // 상담 일자
}

// Response
interface UpdatePersonaResponse {
  success: boolean;
  data?: {
    previousTypeCode: string | null;
    currentTypeCode: string;
    typeHistory: TypeHistoryItem[];  // 최근 3개
    finalPersonality: string;        // determine_personality() 결과
  };
}
```

---

## 6. 페이지별 데이터 흐름

### 6.1 RealTimeConsultationPage (상담 중)

```
[인입] → 고객 ID 확인 → GET /customers/{id} → 고객 정보 표시
                                            ↓
[상담 중] → STT 실시간 전사 → 키워드 추출 → RAG 문서 조회
                           ↓
[localStorage 저장] → pendingConsultation, referencedDocuments, callTime
```

### 6.2 LoadingPage (로딩)

```
[localStorage 읽기] → pendingConsultation
                    ↓
[LLM 분석] → 요약, 제목, 카테고리 분류, 후속 조치 추천
           ↓
[localStorage 저장] → llmAnalysisResult
```

### 6.3 AfterCallWorkPage (후처리)

```
[localStorage 읽기] → pendingConsultation, llmAnalysisResult, referencedDocuments
                    ↓
[화면 표시] → 상담 전문(채팅), AI 요약, 참조 문서, 처리 내역
            ↓
[상담사 수정] → 제목, 카테고리, 메모, 후속 일정 등
              ↓
[저장] → POST /consultations → DB 저장
       ↓
[페르소나 업데이트] → PATCH /customers/{id}/persona
                   ↓
[통계 업데이트] → (Backend Trigger 또는 별도 API)
```

### 6.4 ConsultationHistoryPage (상담 내역)

```
[목록 조회] → GET /consultations?page=1&limit=20&employeeId=...
            ↓
[상세 조회] → GET /consultations/{id} → 모달 표시
            ↓
[필터링] → 날짜, 카테고리, 상태, 고객명 등
```

---

## 7. 다음 단계

### 완료 (v2.0)
1. ✅ consultations 테이블 스키마 확장 SQL 작성
2. ✅ 페르소나 코드 체계 확정 (6타입: N1-N3, S1-S3)
3. ✅ type_history JSONB 형식 확정 (심플: `["N1", "S2", "S2"]`)
4. ✅ FCR 자동 계산 트리거 구현
5. ✅ customers 테이블 정리 (불필요 컬럼 삭제)
6. ✅ v_customer_with_persona JOIN 뷰 생성

### 즉시 실행 (P0)
1. ☐ `14_schema_v4_frontend_integration.sql` 실행
2. ☐ 상담 저장 API 엔드포인트 구현 (`POST /api/v1/consultations`)
3. ☐ 고객 페르소나 업데이트 API 구현 (`PATCH /api/v1/customers/{id}/persona`)

### 단기 (P1)
4. ☐ 상담 목록/상세 조회 API 구현
5. ☐ Frontend `consultationApi.ts` Real 모드 연동
6. ☐ Frontend 타입 정의 동기화 (`subcategory`, `categoryRaw` 추가)
7. ☐ Frontend `mockCustomerDB.ts` 6타입으로 수정

### 중기 (P2)
8. ☐ 녹취 파일 저장 경로 결정 (로컬 vs S3)
9. ☐ STT 타임스탬프 연동 테스트

---

## 결론

### v2.0 업데이트
- **consultations 테이블**: 15개 컬럼 추가 완료 (SQL 스크립트 준비됨)
- **customers 테이블**: 불필요 컬럼 삭제, persona_types와 FK 연결
- **persona_types 테이블**: 6타입으로 교체 (팀원 LLM 분류 기준)
- **자동 통계**: 트리거로 total_consultations, FCR 자동 계산

### 실행 필요
```bash
# DB 스키마 v4.0 적용
psql -U callact_admin -d callact_db -f 14_schema_v4_frontend_integration.sql

# 또는 Python 스크립트로 전체 실행
python 01_setup_callact_db.py
```

### API 개발 필요
1. `POST /api/v1/consultations` - 상담 저장
2. `GET /api/v1/consultations/{id}` - 상담 상세 조회
3. `PATCH /api/v1/customers/{id}/persona` - 페르소나 업데이트
4. `GET /api/v1/customers/{id}` - **v_customer_with_persona 뷰 사용**
