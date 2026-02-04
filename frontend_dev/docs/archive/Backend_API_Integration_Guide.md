# Backend API 연동 가이드

## 📋 개요
CALL:ACT 프론트엔드와 Backend API 연동을 위한 가이드입니다.
실제 DB 구조 분석을 기반으로 작성되었습니다.

**참조 문서:**
- `/PHASE7_CHANGELOG.md` - 프론트엔드 변경사항
- Backend DB 스키마 문서 3개

---

## 🔧 필수 DB 스키마 수정

### 1. `employees` 테이블 수정

```sql
-- ⭐ 프론트엔드에서 필요한 필드 추가
ALTER TABLE employees 
ADD COLUMN trend VARCHAR(10) CHECK (trend IN ('up', 'down', 'same')),
ADD COLUMN phone VARCHAR(20);

-- trend 기본값 설정 (기존 데이터)
UPDATE employees SET trend = 'same' WHERE trend IS NULL;
```

**사유:**
- `trend`: 대시보드에서 성과 추이 표시 (↑↓→)
- `phone`: 직원 관리 페이지에서 연락처 표시

---

### 2. `frequent_inquiries` 테이블 수정

```sql
-- ⭐ 프론트엔드에서 필요한 필드 추가
ALTER TABLE frequent_inquiries
ADD COLUMN keyword VARCHAR(100),
ADD COLUMN trend VARCHAR(10) CHECK (trend IN ('up', 'down', 'same'));

-- keyword 기본값 설정 (question에서 추출)
UPDATE frequent_inquiries SET keyword = 
  CASE
    WHEN question LIKE '%분실%' THEN '카드 분실'
    WHEN question LIKE '%해외%' THEN '해외 결제'
    WHEN question LIKE '%포인트%' THEN '포인트 적립'
    WHEN question LIKE '%연회비%' THEN '연회비 환불'
    WHEN question LIKE '%한도%' THEN '한도 증액'
    ELSE '기타'
  END
WHERE keyword IS NULL;
```

**사유:**
- `keyword`: 대시보드에서 짧은 키워드 표시 (예: "카드 분실")
- `trend`: 인입 건수 추이 표시

---

### 3. 관련 문서 매핑 테이블 생성 (신규)

```sql
-- ⭐ 자주 찾는 문의 ↔ 관련 문서 매핑 테이블
CREATE TABLE frequent_inquiry_documents (
  inquiry_id INTEGER REFERENCES frequent_inquiries(id) ON DELETE CASCADE,
  document_id VARCHAR(100) REFERENCES service_guide_documents(id) ON DELETE CASCADE,
  relevance_score DECIMAL(3,2) DEFAULT 0.50 CHECK (relevance_score >= 0 AND relevance_score <= 1),
  usage_count INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  PRIMARY KEY (inquiry_id, document_id)
);

-- 연관도 점수로 정렬하여 조회하기 위한 인덱스
CREATE INDEX idx_inquiry_docs_score 
ON frequent_inquiry_documents(inquiry_id, relevance_score DESC);

-- usage_count 업데이트용 트리거
CREATE OR REPLACE FUNCTION update_inquiry_doc_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_inquiry_docs_update
BEFORE UPDATE ON frequent_inquiry_documents
FOR EACH ROW
EXECUTE FUNCTION update_inquiry_doc_timestamp();
```

**사유:**
- 자주 찾는 문의마다 여러 관련 문서 연결 가능
- `relevance_score`: RAG 시스템에서 계산한 연관도
- `usage_count`: 실제 상담에서 몇 번 참조되었는지

---

### 4. `consultations` 테이블 확인/수정

```sql
-- ⭐ 참조 문서 저장 컬럼 확인 (없으면 추가)
-- consultations 테이블에 referenced_document_ids 컬럼이 있는지 확인
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'consultations' 
  AND column_name = 'referenced_document_ids';

-- 없으면 추가
ALTER TABLE consultations
ADD COLUMN referenced_document_ids TEXT[];  -- Step별 참조한 문서 ID 배열

-- 예시: ['card-1-1-1', 'card-1-1-2', 'card-1-2-1', 'card-1-2-2']
```

---

## 📊 Batch Job 구현 (trend 자동 계산)

### Job 1: employees.trend 계산 (매일 자정 실행)

```python
# batch_jobs/calculate_employee_trends.py

from datetime import datetime, timedelta
import psycopg2

def calculate_employee_trends():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # 이번 주 시작일 (월요일)
    this_week_start = datetime.now().date() - timedelta(days=datetime.now().weekday())
    last_week_start = this_week_start - timedelta(weeks=1)
    
    query = """
    WITH trend_calculation AS (
      SELECT 
        emp.id,
        -- 이번 주 상담 건수
        COUNT(CASE 
          WHEN c.call_date >= %s THEN 1 
        END) AS this_week,
        -- 저번 주 상담 건수
        COUNT(CASE 
          WHEN c.call_date >= %s AND c.call_date < %s THEN 1 
        END) AS last_week
      FROM employees emp
      LEFT JOIN consultations c ON c.agent_id = emp.id
      GROUP BY emp.id
    )
    UPDATE employees e
    SET 
      trend = CASE 
        WHEN tc.this_week > tc.last_week THEN 'up'
        WHEN tc.this_week < tc.last_week THEN 'down'
        ELSE 'same'
      END,
      updated_at = NOW()
    FROM trend_calculation tc
    WHERE e.id = tc.id;
    """
    
    cursor.execute(query, (this_week_start, last_week_start, this_week_start))
    conn.commit()
    
    print(f"✅ Employee trends updated: {cursor.rowcount} rows")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    calculate_employee_trends()
```

---

### Job 2: frequent_inquiries.trend 계산 (매일 자정 실행)

```python
# batch_jobs/calculate_inquiry_trends.py

def calculate_inquiry_trends():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # 이번 주와 저번 주
    this_week_start = datetime.now().date() - timedelta(days=datetime.now().weekday())
    last_week_start = this_week_start - timedelta(weeks=1)
    
    query = """
    WITH trend_calculation AS (
      SELECT 
        fi.id,
        -- 이번 주 조회 수
        COUNT(CASE 
          WHEN ivl.viewed_at >= %s THEN 1 
        END) AS this_week_views,
        -- 저번 주 조회 수
        COUNT(CASE 
          WHEN ivl.viewed_at >= %s AND ivl.viewed_at < %s THEN 1 
        END) AS last_week_views
      FROM frequent_inquiries fi
      LEFT JOIN inquiry_view_log ivl ON ivl.inquiry_id = fi.id
      GROUP BY fi.id
    )
    UPDATE frequent_inquiries fi
    SET 
      trend = CASE 
        WHEN tc.this_week_views > tc.last_week_views THEN 'up'
        WHEN tc.this_week_views < tc.last_week_views THEN 'down'
        ELSE 'same'
      END,
      view_count = (
        SELECT COUNT(*) 
        FROM inquiry_view_log 
        WHERE inquiry_id = fi.id
      ),
      updated_at = NOW()
    FROM trend_calculation tc
    WHERE fi.id = tc.id;
    """
    
    cursor.execute(query, (this_week_start, last_week_start, this_week_start))
    conn.commit()
    
    print(f"✅ Inquiry trends updated: {cursor.rowcount} rows")
    
    cursor.close()
    conn.close()
```

---

### Job 3: 관련 문서 연관도 계산 (매일 자정 실행)

```python
# batch_jobs/calculate_document_relevance.py

def calculate_document_relevance():
    """
    상담 이력에서 자주 찾는 문의별로 참조된 문서들의 연관도를 계산
    """
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    query = """
    -- 1. 각 카테고리별로 가장 많이 참조된 문서 찾기
    WITH category_documents AS (
      SELECT 
        c.category,
        unnest(c.referenced_document_ids) AS document_id,
        COUNT(*) AS reference_count
      FROM consultations c
      WHERE c.referenced_document_ids IS NOT NULL
        AND array_length(c.referenced_document_ids, 1) > 0
      GROUP BY c.category, document_id
    ),
    -- 2. 카테고리별 총 참조 건수
    category_totals AS (
      SELECT 
        category,
        SUM(reference_count) AS total_references
      FROM category_documents
      GROUP BY category
    ),
    -- 3. 연관도 점수 계산 (0.00 ~ 1.00)
    relevance_scores AS (
      SELECT 
        cd.category,
        cd.document_id,
        cd.reference_count,
        ROUND((cd.reference_count::DECIMAL / ct.total_references), 2) AS relevance_score
      FROM category_documents cd
      JOIN category_totals ct ON ct.category = cd.category
    )
    -- 4. frequent_inquiry_documents 테이블에 UPSERT
    INSERT INTO frequent_inquiry_documents (inquiry_id, document_id, relevance_score, usage_count, updated_at)
    SELECT 
      fi.id AS inquiry_id,
      rs.document_id,
      rs.relevance_score,
      rs.reference_count AS usage_count,
      NOW() AS updated_at
    FROM frequent_inquiries fi
    JOIN relevance_scores rs ON (
      -- 카테고리 매핑 (한글 → 영문 ENUM)
      (fi.keyword = '카드 분실' AND rs.category = 'card_loss') OR
      (fi.keyword = '해외 결제' AND rs.category = 'overseas_payment') OR
      (fi.keyword = '포인트 적립' AND rs.category = 'points') OR
      (fi.keyword = '연회비 환불' AND rs.category = 'fee_inquiry') OR
      (fi.keyword = '한도 증액' AND rs.category = 'limit_inquiry')
    )
    ON CONFLICT (inquiry_id, document_id) 
    DO UPDATE SET
      relevance_score = EXCLUDED.relevance_score,
      usage_count = EXCLUDED.usage_count,
      updated_at = NOW();
    """
    
    cursor.execute(query)
    conn.commit()
    
    print(f"✅ Document relevance updated: {cursor.rowcount} rows")
    
    cursor.close()
    conn.close()
```

---

## 🌐 필수 API 엔드포인트

### 1. 자주 찾는 문의 조회 (상위 1개 문서 포함)

**엔드포인트:**
```
GET /api/frequent-inquiries
```

**응답 구조:**
```json
[
  {
    "id": 1,
    "keyword": "카드 분실",
    "question": "카드를 분실했어요. 어떻게 해야 하나요?",
    "count": 45,
    "trend": "up",
    "top_document": {
      "document_id": "DOC-GUIDE-001",
      "title": "카드 즉시 사용 정지",
      "regulation": "여신전문금융업법 제16조",
      "summary": "고객의 카드 분실 신고 시 즉시 카드 사용을 정지하여...",
      "relevance_score": 0.95
    }
  },
  ...
]
```

**SQL 쿼리:**
```sql
SELECT 
  fi.id,
  fi.keyword,
  fi.question,
  fi.view_count AS count,
  fi.trend,
  -- 상위 1개 문서만 조회 (서브쿼리)
  (
    SELECT json_build_object(
      'document_id', fid.document_id,
      'title', sgd.title,
      'regulation', sgd.structured->>'regulation',
      'summary', sgd.structured->>'summary',
      'relevance_score', fid.relevance_score
    )
    FROM frequent_inquiry_documents fid
    JOIN service_guide_documents sgd ON sgd.id = fid.document_id
    WHERE fid.inquiry_id = fi.id
    ORDER BY fid.relevance_score DESC
    LIMIT 1
  ) AS top_document
FROM frequent_inquiries fi
WHERE fi.is_active = true
ORDER BY fi.view_count DESC;
```

---

### 2. 문서 상세 조회

**엔드포인트:**
```
GET /api/documents/:document_id
```

**응답 구조:**
```json
{
  "id": "DOC-GUIDE-001",
  "title": "카드 즉시 사용 정지",
  "content": "고객의 카드 분실 신고 시 즉시 카드 사용을 정지하여 부정 사용을 방지합니다.",
  "keywords": ["카드분실", "긴급정지", "부정사용방지"],
  "structured": {
    "systemPath": "고객관리 > 카드관리 > 분실신고 > 즉시정지",
    "requiredChecks": ["본인 확인", "분실 시점 확인", "부정 사용 여부 확인"],
    "exceptions": ["본인 확인 실패 시 추가 인증 필요"],
    "time": "처리시간 1-2분",
    "note": "즉시 처리 필수",
    "regulation": "여신전문금융업법 제16조"
  },
  "fullText": "【카드 즉시 사용 정지 약관】\n\n제1조 (목적)...",
  "metadata": {
    "document_source": "테디카드 내부 가이드",
    "priority": "high",
    "usage_count": 156
  }
}
```

**SQL 쿼리:**
```sql
SELECT 
  id,
  title,
  content,
  keywords,
  structured,
  metadata->>'fullTerms' AS "fullText",  -- 또는 별도 컬럼
  metadata
FROM service_guide_documents
WHERE id = $1;
```

**참고:**
- `fullText`가 별도 컬럼이면 그대로 사용
- `metadata.fullTerms`에 있으면 추출하여 사용
- 프론트엔드에서 `fullText` 필드를 기대함

---

### 3. 상담 참조 문서 조회 (후처리용)

**엔드포인트:**
```
GET /api/consultations/:consultation_id/documents
```

**응답 구조:**
```json
{
  "consultation_id": "CS-20250105-1432",
  "referenced_documents": [
    {
      "step": 1,
      "documents": [
        {
          "id": "card-1-1-1",
          "title": "카드 즉시 사용 정지",
          "used": true,
          "viewed_at": "2025-01-05T14:33:15Z"
        },
        {
          "id": "card-1-1-2",
          "title": "분실 신고 접수 완료",
          "used": false,
          "viewed_at": null
        }
      ]
    },
    {
      "step": 2,
      "documents": [...]
    },
    {
      "step": 3,
      "documents": [...]
    }
  ]
}
```

**SQL 쿼리:**
```sql
-- consultations.referenced_document_ids에서 조회
SELECT 
  c.id AS consultation_id,
  c.referenced_document_ids,
  -- 각 문서 정보 조회
  (
    SELECT json_agg(
      json_build_object(
        'id', doc_id,
        'title', sgd.title,
        'used', true  -- referenced_document_ids에 있으면 사용함
      )
    )
    FROM unnest(c.referenced_document_ids) AS doc_id
    LEFT JOIN service_guide_documents sgd ON sgd.id = doc_id
  ) AS documents
FROM consultations c
WHERE c.id = $1;
```

---

### 4. 상담 내역 조회 (엑셀 다운로드용)

**엔드포인트:**
```
GET /api/consultations
Query Params: status, category, date_from, date_to
```

**응답 구조:**
```json
[
  {
    "id": "CS-20250105-1432",
    "customer_id": "CUST-2024-00127",  // ⭐ 고객명 대신 ID
    "agent": "홍길동",
    "category": "카드분실",
    "status": "완료",
    "datetime": "2025-01-05 14:32",
    "duration": "05:12",
    "content": "카드 분실 신고 접수 및 즉시 정지 처리. 재발급 신청 완료",  // ⭐ content 필드
    "fcr": true
  },
  ...
]
```

**SQL 쿼리:**
```sql
SELECT 
  c.id,
  c.customer_id,
  e.name AS agent,
  c.category,
  c.status::text AS status,  -- ENUM → 텍스트
  CONCAT(c.call_date, ' ', SUBSTRING(c.call_time::text, 1, 5)) AS datetime,
  c.call_duration AS duration,
  c.title AS content,  -- ⭐ 상담 내용
  c.fcr
FROM consultations c
JOIN employees e ON e.id = c.agent_id
WHERE 
  ($1::consultation_status IS NULL OR c.status = $1::consultation_status)
  AND ($2::consultation_category IS NULL OR c.category = $2::consultation_category)
  AND ($3::date IS NULL OR c.call_date >= $3::date)
  AND ($4::date IS NULL OR c.call_date <= $4::date)
ORDER BY c.call_date DESC, c.call_time DESC;
```

**프론트엔드 ENUM 변환 필요:**
```typescript
// Frontend → Backend
const statusMap = {
  '완료': 'completed',
  '진행중': 'in_progress',
  '미완료': 'incomplete'
};

const categoryMap = {
  '카드분실': 'card_loss',
  '해외결제': 'overseas_payment',
  '수수료문의': 'fee_inquiry',
  '한도증액': 'limit_inquiry',
  '연체문의': 'other',
  '결제일변경': 'other',
  '포인트혜택': 'points',
  '일반문의': 'other'
};
```

---

## 🔄 RAG 시스템 연동

### 상담 완료 시 문서 매핑 업데이트

```python
# services/consultation_service.py

def complete_consultation(consultation_id: str, referenced_documents: list[str]):
    """
    상담 완료 시 호출
    - 참조 문서 저장
    - 자주 찾는 문의 연관도 업데이트
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. consultations.referenced_document_ids 업데이트
    cursor.execute(
        "UPDATE consultations SET referenced_document_ids = %s WHERE id = %s",
        (referenced_documents, consultation_id)
    )
    
    # 2. 해당 상담의 카테고리 확인
    cursor.execute(
        "SELECT category FROM consultations WHERE id = %s",
        (consultation_id,)
    )
    category = cursor.fetchone()[0]
    
    # 3. 해당 카테고리의 자주 찾는 문의 조회
    cursor.execute(
        """
        SELECT id FROM frequent_inquiries 
        WHERE category = %s 
        ORDER BY view_count DESC 
        LIMIT 1
        """,
        (category,)
    )
    inquiry_id = cursor.fetchone()
    
    if inquiry_id:
        inquiry_id = inquiry_id[0]
        
        # 4. 참조된 문서들의 usage_count 증가
        for doc_id in referenced_documents:
            cursor.execute(
                """
                INSERT INTO frequent_inquiry_documents 
                  (inquiry_id, document_id, usage_count, relevance_score)
                VALUES (%s, %s, 1, 0.50)
                ON CONFLICT (inquiry_id, document_id) 
                DO UPDATE SET
                  usage_count = frequent_inquiry_documents.usage_count + 1,
                  updated_at = NOW()
                """,
                (inquiry_id, doc_id)
            )
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✅ Consultation {consultation_id} completed and documents mapped")
```

---

## 📱 프론트엔드 API 클라이언트 구현

### `src/utils/api.ts` (추후 작성 예정)

```typescript
// ==================== API 클라이언트 ====================

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// 1. 자주 찾는 문의 조회
export async function getFrequentInquiries() {
  const response = await fetch(`${API_BASE_URL}/api/frequent-inquiries`);
  if (!response.ok) throw new Error('Failed to fetch frequent inquiries');
  return await response.json();
}

// 2. 문서 상세 조회
export async function getDocument(documentId: string) {
  const response = await fetch(`${API_BASE_URL}/api/documents/${documentId}`);
  if (!response.ok) throw new Error('Failed to fetch document');
  return await response.json();
}

// 3. 상담 참조 문서 조회
export async function getConsultationDocuments(consultationId: string) {
  const response = await fetch(`${API_BASE_URL}/api/consultations/${consultationId}/documents`);
  if (!response.ok) throw new Error('Failed to fetch consultation documents');
  return await response.json();
}

// 4. 상담 내역 조회
export async function getConsultations(filters?: {
  status?: string;
  category?: string;
  date_from?: string;
  date_to?: string;
}) {
  const params = new URLSearchParams();
  if (filters?.status) params.append('status', filters.status);
  if (filters?.category) params.append('category', filters.category);
  if (filters?.date_from) params.append('date_from', filters.date_from);
  if (filters?.date_to) params.append('date_to', filters.date_to);
  
  const response = await fetch(`${API_BASE_URL}/api/consultations?${params}`);
  if (!response.ok) throw new Error('Failed to fetch consultations');
  return await response.json();
}
```

---

## 🔀 프론트엔드 수정 포인트 (API 연동 시)

### 1. `DocumentDetailModal.tsx`
**현재 (Mock):**
```typescript
const findDocument = () => {
  for (const scenario of scenarios) {
    // scenarios에서 검색...
  }
};
const document = findDocument();
```

**변경 후 (API):**
```typescript
const [document, setDocument] = useState<ScenarioCard | null>(null);

useEffect(() => {
  if (isOpen && documentId) {
    api.getDocument(documentId).then(data => {
      setDocument(data);
    });
  }
}, [isOpen, documentId]);
```

---

### 2. `DashboardPage.tsx`
**현재 (Mock):**
```typescript
const frequentInquiries = frequentInquiriesData;
```

**변경 후 (API):**
```typescript
const [frequentInquiries, setFrequentInquiries] = useState([]);

useEffect(() => {
  api.getFrequentInquiries().then(data => {
    setFrequentInquiries(data);
  });
}, []);
```

---

### 3. `ConsultationHistoryPage.tsx`
**현재 (Mock):**
```typescript
const [consultations] = useState(consultationsData);
```

**변경 후 (API):**
```typescript
const [consultations, setConsultations] = useState([]);

useEffect(() => {
  api.getConsultations(filters).then(data => {
    setConsultations(data);
  });
}, [filters]);
```

---

## 📊 데이터 매핑 정리

### 프론트엔드 필드 → DB 컬럼

| 프론트 | DB 테이블 | DB 컬럼 | 변환 필요 |
|--------|-----------|---------|----------|
| `customer` | consultations | customer_id | - |
| `agent` | employees | name (JOIN 필요) | - |
| `category` (한글) | consultations | category (ENUM) | ✅ 변환 |
| `status` (한글) | consultations | status (ENUM) | ✅ 변환 |
| `datetime` | consultations | call_date + call_time | ✅ 결합 |
| `content` | consultations | title | - |
| `memo` | consultation_summaries | memo | ✅ JOIN |
| `trend` | employees / frequent_inquiries | trend | ✅ Batch Job |

---

## 🎯 Backend 개발 우선순위

### 우선순위 1: 필수 (Phase 7 완료를 위해)
1. ✅ `employees.trend` 컬럼 추가
2. ✅ `frequent_inquiries.keyword`, `trend` 컬럼 추가
3. ✅ `frequent_inquiry_documents` 테이블 생성
4. ✅ `GET /api/frequent-inquiries` 구현
5. ✅ `GET /api/documents/:id` 구현

### 우선순위 2: 중요 (엑셀 다운로드)
6. ✅ `GET /api/consultations` 구현
7. ✅ ENUM 변환 로직 구현

### 우선순위 3: 일반 (후처리 페이지)
8. ✅ `GET /api/consultations/:id/documents` 구현
9. ✅ Batch Job 구현 (trend 계산)
10. ✅ RAG 문서 매핑 로직 구현

---

## 📝 Backend 팀원에게 전달

### 체크리스트

- [ ] DB 스키마 수정 (employees, frequent_inquiries, 신규 테이블)
- [ ] API 엔드포인트 3개 구현
- [ ] ENUM 변환 로직 구현
- [ ] Batch Job 3개 작성 및 스케줄링
- [ ] RAG 문서 매핑 로직 구현
- [ ] 프론트엔드와 API 응답 구조 확인

### 참고 파일
- `/PHASE7_CHANGELOG.md` - 프론트엔드 요구사항
- 이 문서 - Backend 구현 가이드
- DB 스키마 문서 3개

---

**작성일**: 2026-01-20  
**작성자**: Frontend Team  
**버전**: 1.0
