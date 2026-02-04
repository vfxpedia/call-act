# 참조 문서 DB 연동 가이드

## 📋 현재 상태 (Phase 10)

### 1. 상담 내역 페이지 (ConsultationHistoryPage)
**위치:** `/src/app/pages/ConsultationHistoryPage.tsx`

**현재 동작:**
- 상담 목록 클릭 → `ConsultationDetailModal` 표시
- 모달에서 "참조 문서" 섹션에 **하드코딩된 Mock 데이터** 표시

**Mock 데이터 예시:**
```typescript
const detailData = {
  documents: [
    '카드 분실 신고 처리 절차',
    '재발급 카드 배송 안내',
    '분실 카드 부정 사용 보상 정책',
  ],
};
```

---

### 2. 관리자 상담 관리 페이지 (AdminConsultationManagePage)
**위치:** `/src/app/pages/AdminConsultationManagePage.tsx`

**현재 동작:**
- 동일하게 `ConsultationDetailModal` 사용
- 동일한 Mock 데이터 표시

---

## 🔗 DB 연동 구조

### 백엔드 테이블 설계

#### 1. consultations 테이블
```sql
CREATE TABLE consultations (
  id VARCHAR(50) PRIMARY KEY,
  customer_id VARCHAR(50) REFERENCES customers(id),
  employee_id VARCHAR(50) REFERENCES employees(id),
  category VARCHAR(100),
  -- ... 기타 필드
  
  -- 참조 문서 (JSON 또는 별도 테이블)
  referenced_document_ids TEXT[],  -- ['DOC-001', 'DOC-002']
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP
);
```

#### 2. documents 테이블 (칸반보드 문서)
```sql
CREATE TABLE documents (
  id VARCHAR(50) PRIMARY KEY,           -- 'DOC-001'
  title VARCHAR(200) NOT NULL,          -- '카드 분실 신고 처리 절차'
  category VARCHAR(100),                -- '카드분실'
  keywords TEXT[],                      -- ['카드분실', '긴급정지', '재발급']
  content TEXT,                         -- 문서 본문
  system_path VARCHAR(500),
  required_checks TEXT[],
  exceptions TEXT[],
  time VARCHAR(50),
  note TEXT,
  regulation TEXT,
  full_text TEXT,                       -- 전체 약관/규정
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP
);
```

#### 3. consultation_documents 테이블 (중간 테이블)
```sql
CREATE TABLE consultation_documents (
  consultation_id VARCHAR(50) REFERENCES consultations(id),
  document_id VARCHAR(50) REFERENCES documents(id),
  referenced_at TIMESTAMP DEFAULT NOW(),
  PRIMARY KEY (consultation_id, document_id)
);
```

---

## ✅ 프론트엔드 준비 상태

### 1. 타입 정의 (`/src/types/consultation.ts`)

**ReferencedDocument 타입:**
```typescript
export interface ReferencedDocument {
  id: string;
  title: string;
  category: string;
  timestamp: string;
}
```

**ConsultationData 타입:**
```typescript
export interface ConsultationData {
  // ... 기타 필드
  
  referencedDocuments: ReferencedDocument[];  // 참조 문서 배열
  referencedDocumentIds: string[];            // 문서 ID 배열
}
```

✅ **타입 준비 완료!**

---

### 2. API 함수 (`/src/api/consultationApi.ts`)

**현재 구현:**
```typescript
export function loadReferencedDocuments() {
  try {
    const data = localStorage.getItem('referencedDocuments');
    if (!data) return [];
    return JSON.parse(data);
  } catch (error) {
    console.error('❌ referencedDocuments 로드 실패:', error);
    return [];
  }
}
```

**DB 연동 시 수정 필요:**
```typescript
import { USE_MOCK_DATA } from '@/config/mockConfig';

export async function loadReferencedDocuments(consultationId: string): Promise<ReferencedDocument[]> {
  if (USE_MOCK_DATA) {
    // Mock 모드
    try {
      const data = localStorage.getItem('referencedDocuments');
      if (!data) return mockReferencedDocuments; // 기본 Mock 데이터
      return JSON.parse(data);
    } catch (error) {
      console.error('❌ referencedDocuments 로드 실패:', error);
      return mockReferencedDocuments;
    }
  } else {
    // Real 모드: 백엔드 API 호출
    try {
      const response = await fetch(`/api/v1/consultations/${consultationId}/documents`);
      if (!response.ok) {
        throw new Error('Failed to fetch referenced documents');
      }
      const data = await response.json();
      return data.documents;
    } catch (error) {
      console.error('❌ API 참조 문서 로드 실패:', error);
      return [];
    }
  }
}

// Mock 데이터 (백업용)
const mockReferencedDocuments: ReferencedDocument[] = [
  {
    id: 'DOC-001',
    title: '카드 분실 신고 처리 절차',
    category: '카드분실',
    timestamp: new Date().toISOString(),
  },
  {
    id: 'DOC-002',
    title: '재발급 카드 배송 안내',
    category: '카드분실',
    timestamp: new Date().toISOString(),
  },
  {
    id: 'DOC-003',
    title: '분실 카드 부정 사용 보상 정책',
    category: '카드분실',
    timestamp: new Date().toISOString(),
  },
];
```

---

### 3. ConsultationDetailModal 수정 필요

**현재 (하드코딩):**
```typescript
const detailData = {
  documents: [
    '카드 분실 신고 처리 절차',
    '재발급 카드 배송 안내',
    '분실 카드 부정 사용 보상 정책',
  ],
};
```

**수정 후 (API 연동):**
```typescript
import { loadReferencedDocuments } from '@/api/consultationApi';

const [referencedDocs, setReferencedDocs] = useState<ReferencedDocument[]>([]);

useEffect(() => {
  if (isOpen && consultation.id) {
    loadReferencedDocuments(consultation.id).then(setReferencedDocs);
  }
}, [isOpen, consultation.id]);

// 렌더링
{referencedDocs.map((doc) => (
  <div key={doc.id} className="...">
    <FileText className="..." />
    <span>{doc.title}</span>
  </div>
))}
```

---

## 🚀 백엔드 API 엔드포인트

### GET /api/v1/consultations/{consultation_id}/documents

**요청:**
```
GET /api/v1/consultations/CONS-20250122-001/documents
Authorization: Bearer {token}
```

**응답:**
```json
{
  "success": true,
  "consultationId": "CONS-20250122-001",
  "documents": [
    {
      "id": "DOC-001",
      "title": "카드 분실 신고 처리 절차",
      "category": "카드분실",
      "timestamp": "2025-01-22T14:33:15Z"
    },
    {
      "id": "DOC-002",
      "title": "재발급 카드 배송 안내",
      "category": "카드분실",
      "timestamp": "2025-01-22T14:34:20Z"
    }
  ]
}
```

---

## 🔍 DB 연동 시 문제 없는 이유

### 1. 타입 정의 완료 ✅
- `ReferencedDocument` 인터페이스 존재
- `ConsultationData`에 `referencedDocuments` 필드 포함

### 2. API 함수 구조 준비 ✅
- `loadReferencedDocuments()` 함수 존재
- Feature Flag (`USE_MOCK_DATA`) 통합 가능

### 3. 컴포넌트 수정 용이 ✅
- `ConsultationDetailModal`에서 `useEffect`로 데이터 로드
- 기존 Mock 데이터를 API 응답으로 대체만 하면 됨

### 4. 에러 처리 준비 ✅
- try-catch 블록으로 에러 핸들링
- 빈 배열 반환으로 fallback

---

## 📊 실제 연동 시나리오

### 상담 중 페이지 (RealTimeConsultationPage)

**1. STT로 키워드 추출**
```typescript
const keywords = ['카드분실', '긴급정지', '재발급'];
```

**2. RAG로 관련 문서 검색**
```
POST /api/v1/documents/search
{
  "keywords": ["카드분실", "긴급정지", "재발급"],
  "limit": 10
}
```

**3. 칸반보드에 문서 표시**
- 현재 상황 카드 2개
- 다음 단계 카드 2개

**4. 상담사가 참조한 문서 기록**
```typescript
const referencedDocumentIds = [
  'DOC-001', // 카드 즉시 사용 정지
  'DOC-002', // 재발급 카드 신청
];

localStorage.setItem('referencedDocuments', JSON.stringify(referencedDocumentIds));
```

**5. 후처리 페이지에서 저장**
```typescript
const consultationData = {
  // ... 기타 필드
  referencedDocumentIds: ['DOC-001', 'DOC-002'],
};

// POST /api/v1/consultations
await saveConsultation(consultationData);
```

**6. DB에 저장**
```sql
-- consultations 테이블
INSERT INTO consultations (id, ..., referenced_document_ids)
VALUES ('CONS-20250122-001', ..., ARRAY['DOC-001', 'DOC-002']);

-- consultation_documents 중간 테이블
INSERT INTO consultation_documents (consultation_id, document_id)
VALUES 
  ('CONS-20250122-001', 'DOC-001'),
  ('CONS-20250122-001', 'DOC-002');
```

**7. 상담 내역 페이지에서 조회**
```sql
SELECT 
  d.id, d.title, d.category, cd.referenced_at
FROM consultation_documents cd
JOIN documents d ON cd.document_id = d.id
WHERE cd.consultation_id = 'CONS-20250122-001'
ORDER BY cd.referenced_at;
```

---

## ✅ 체크리스트

### 프론트엔드 (현재 상태)
- [x] `ReferencedDocument` 타입 정의
- [x] `loadReferencedDocuments()` 함수 존재
- [x] `ConsultationDetailModal` 준비
- [ ] API 연동 코드 수정 (백엔드 완료 후)
- [ ] Feature Flag 전환 (USE_MOCK_DATA = false)

### 백엔드 (구현 필요)
- [ ] `documents` 테이블 생성
- [ ] `consultation_documents` 중간 테이블 생성
- [ ] `GET /api/v1/consultations/{id}/documents` API
- [ ] `POST /api/v1/documents/search` RAG 검색 API
- [ ] `consultations.referenced_document_ids` 필드 추가

---

## 🎯 결론

**질문: DB 연동 시 문제가 없을까요?**

**답변: 네, 문제 없습니다! ✅**

**이유:**
1. ✅ 타입 정의 완료 (`ReferencedDocument`, `ConsultationData`)
2. ✅ API 함수 구조 준비 (`loadReferencedDocuments`)
3. ✅ 컴포넌트 수정 용이 (Mock → API 대체만 하면 됨)
4. ✅ Feature Flag 통합 가능 (`USE_MOCK_DATA`)
5. ✅ 에러 처리 구조 완비

**백엔드 구현 완료 후 작업:**
1. `consultationApi.ts`에서 `loadReferencedDocuments()` 함수 수정
2. `ConsultationDetailModal`에서 API 호출로 변경
3. `mockConfig.ts`에서 `USE_MOCK_DATA = false` 설정

**소요 시간:** 약 30분 (백엔드 API 완료 전제)

---

**마지막 업데이트:** Phase 10-2  
**상태:** DB 연동 준비 완료 ✅
