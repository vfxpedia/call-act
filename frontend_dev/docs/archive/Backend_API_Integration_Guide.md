# Backend API 연동 가이드

## 개요
CALL:ACT 프론트엔드와 Backend API 연동을 위한 가이드입니다.
실제 DB 구조 분석을 기반으로 작성되었습니다.

**최종 수정일:** 2026-02-05
**버전:** 2.0

---

## 구현 완료 항목

### 1. employees 테이블

| 필드 | 타입 | 설명 | 상태 |
|------|------|------|------|
| phone | VARCHAR(20) | 연락처 (010-1234-5678) | ✅ 완료 |
| trend | VARCHAR(10) | 성과 추이 (up/down/same) | ✅ 완료 |

**API 엔드포인트:**
- `GET /api/v1/employees` - 상담사 목록 (trend 포함)
- `GET /api/v1/employees/{id}` - 상담사 상세 (trend 포함)
- `GET /api/v1/employees/top` - 우수 상담사

---

### 2. frequent_inquiries 테이블

```sql
CREATE TABLE frequent_inquiries (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(100) NOT NULL,            -- 짧은 키워드
    question TEXT NOT NULL,                   -- 전체 질문
    count INT DEFAULT 0,                      -- 문의 건수
    trend VARCHAR(10) DEFAULT 'same',         -- 추이 (up/down/same)
    content TEXT,                             -- 상세 설명
    related_document_id VARCHAR(100),         -- 관련 문서 ID
    related_document_title VARCHAR(300),
    related_document_regulation VARCHAR(200),
    related_document_summary TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

**API 엔드포인트:**
- `GET /api/v1/frequent-inquiries` - 자주 찾는 문의 목록

**응답 구조:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "keyword": "카드 분실",
      "question": "카드를 분실했어요. 어떻게 해야 하나요?",
      "count": 45,
      "trend": "up",
      "content": "...",
      "relatedDocument": {
        "document_id": "card-1-1-1",
        "title": "카드 즉시 사용 정지",
        "regulation": "여신전문금융업법 제16조",
        "summary": "..."
      }
    }
  ],
  "total": 5,
  "message": "자주 찾는 문의 5건 조회 완료"
}
```

---

### 3. consultations 테이블 확장

```sql
ALTER TABLE consultations ADD COLUMN referenced_document_ids TEXT[];
```

상담 중 참조한 문서 ID 배열을 저장합니다.

---

### 4. notices 테이블

| 필드 | 타입 | 설명 | 상태 |
|------|------|------|------|
| view_count | INT | 조회수 | ✅ 완료 |

**API 엔드포인트:**
- `GET /api/v1/notices` - 공지사항 목록 (view_count 포함)
- `PATCH /api/v1/notices/{id}/view` - 조회수 증가

---

## Trend 계산 시스템

### 계산 로직
이번 주 상담/문의 건수 vs 저번 주 상담/문의 건수 비교:
- 증가: `up`
- 감소: `down`
- 동일: `same`

### 실행 방식

#### 1. 최초 DB 적재 시
`01a_setup_callact_db.py` 실행 시 자동으로 trend 계산됨

#### 2. 배치 Job (매일 12시)
```bash
python batch_calculate_trends.py
```

**스케줄 설정:**
- **Windows Task Scheduler**: 매일 12:00 실행
- **Linux Cron**: `0 12 * * * /path/to/python batch_calculate_trends.py`

---

## DB 설정 스크립트

### 전체 DB 재적재 (팀원 동일하게)

```bash
# 1. 기본 스키마 + 데이터 적재
python 01a_setup_callact_db.py

# 2. 확장 필드 Mock 데이터 채우기
python 01b_populate_mock_data.py
```

### 생성되는 테이블
- employees (trend, phone 포함)
- consultations (referenced_document_ids 포함)
- frequent_inquiries (trend 포함)
- notices (view_count 포함)
- 기타: customers, category_mappings, service_guide_documents 등

---

## 프론트엔드 API 연동

### mockConfig.ts
```typescript
// Mock/Real 전환
export const USE_MOCK_DATA = getMockModeFromStorage();
```

### 연동 완료된 API

| 기능 | Mock | Real API | 상태 |
|------|------|----------|------|
| 상담사 목록 | employeesData | /api/v1/employees | ✅ 완료 |
| 상담사 CRUD | - | POST/PUT/DELETE | ✅ 완료 |
| 공지사항 | noticesData | /api/v1/notices | ✅ 완료 |
| 조회수 증가 | - | PATCH /notices/{id}/view | ✅ 완료 |
| 자주 찾는 문의 | frequentInquiriesData | /api/v1/frequent-inquiries | ✅ 완료 |
| 상담 내역 | consultationsData | /api/v1/consultations | ✅ 완료 |

---

## 불필요한 항목 (삭제됨)

### frequent_inquiry_documents 테이블
- **사유**: 프론트엔드가 단일 관련 문서만 사용
- **대안**: `frequent_inquiries` 테이블에 `related_document_*` 필드로 직접 저장

### inquiry_view_log 테이블
- **사유**: 별도 조회 로그 테이블 불필요
- **대안**: `frequent_inquiries.count`로 간소화

---

## 파일 구조

```
backend_dev/app/db/scripts/
├── 01a_setup_callact_db.py       # 기본 스키마 + 데이터 적재
├── 01b_populate_mock_data.py     # 확장 필드 Mock 데이터
├── batch_calculate_trends.py      # Trend 배치 Job (12시 실행)
├── modules/
│   ├── calculate_trends.py        # Trend 계산 로직
│   ├── load_frequent_inquiries.py # 자주 찾는 문의 적재
│   ├── load_employees.py          # 상담사 적재
│   └── ...
└── db_setup.sql                   # 스키마 정의
```

---

## 문의
- Frontend Team: 프론트엔드 연동 관련
- Backend Team: API/DB 관련
