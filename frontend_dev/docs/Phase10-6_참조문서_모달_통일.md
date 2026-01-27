# Phase 10-6: 참조 문서 UI 통일 (DocumentDetailModal)

## 📋 작업 개요

**목적:** 전체 시스템에서 참조 문서를 표시하는 방식을 `DocumentDetailModal`로 통일하여 일관된 사용자 경험 제공

**작업 일자:** 2025-01-23  
**Phase:** 10-6  
**상태:** ✅ **완료**

---

## 🎯 배경 및 문제점

### ❌ 이전 상태 (불일치)

| 페이지 | 참조 문서 UI | 문제점 |
|--------|-------------|--------|
| **상담 상세 (ConsultationDetailModal)** | ~~Accordion~~ | 하드코딩된 문자열, scenarios.ts 미연동 |
| **자주 찾는 문의 (FrequentInquiryModal)** | DocumentDetailModal 모달 | ✅ 정상 작동 |
| **후처리 (AfterCallWorkPage)** | DocumentDetailModal 모달 | ✅ 정상 작동 |

### 🐛 **버그 발견**
- 대시보드 → 상담 상세 → 참조 문서 클릭 **안됨**
- 상담관리 → 상담 상세 → 참조 문서 클릭 **안됨**

**원인:**
```typescript
// ❌ 잘못된 문서 ID (scenarios.ts에 존재하지 않음)
documents: [
  { id: 'doc1', title: '카드 분실 신고 처리 절차' },
  { id: 'doc2', title: '재발급 카드 배송 안내' },
  { id: 'doc3', title: '분실 카드 부정 사용 보상 정책' },
]
```

---

## ✅ 해결 방안

### 1. **중앙 관리 구조 확립**

```
┌─────────────────────────────────────┐
│   중앙 데이터 소스: scenarios.ts    │
│   - card-1-1-1: "카드 즉시 사용 정지" │
│   - card-1-1-2: "분실 신고 접수 완료" │
│   - card-1-1-3: "재발급 카드 신청"    │
└──────────────┬──────────────────────┘
               │
      ┌────────┼────────┐
      ▼        ▼        ▼
  대시보드   후처리   상담관리
    ↓         ↓        ↓
  모두 DocumentDetailModal 사용
```

### 2. **실제 문서 ID 사용**

#### ✅ **수정 후 (ConsultationDetailModal.tsx)**

```typescript
// ⭐ Phase 10-6: 실제 scenarios.ts의 문서 ID 사용
documents: [
  {
    id: 'card-1-1-1', // ✅ scenarios.ts의 실제 ID
    title: '카드 즉시 사용 정지',
    content: '고객의 카드 분실 신고 시 즉시 카드 사용을 정지하여 부정 사용을 방지합니다.'
  },
  {
    id: 'card-1-1-2', // ✅ scenarios.ts의 실제 ID
    title: '분실 신고 접수 완료',
    content: '분실 신고가 정식으로 접수되었으며, 신고 번호가 발급됩니다.'
  },
  {
    id: 'card-1-1-3', // ✅ scenarios.ts의 실제 ID
    title: '재발급 카드 신청',
    content: '분실 카드를 대체할 새로운 카드를 발급합니다.'
  },
],
```

### 3. **DocumentDetailModal 연동**

```typescript
// ⭐ 상태 관리 추가
const [isDocumentModalOpen, setIsDocumentModalOpen] = useState(false);
const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null);

// ⭐ 참조 문서 클릭 핸들러
<button
  onClick={() => {
    setSelectedDocumentId(doc.id); // 'card-1-1-1' 전달
    setIsDocumentModalOpen(true);
  }}
  className="w-full flex items-center gap-2 p-1.5 rounded bg-[#F8F9FA] hover:bg-[#E8F1FC] transition-colors cursor-pointer text-left"
>
  <FileText className="w-3.5 h-3.5 text-[#0047AB] flex-shrink-0" />
  <span className="text-xs text-[#333333]">{doc.title}</span>
</button>

// ⭐ DocumentDetailModal 렌더링
{isDocumentModalOpen && selectedDocumentId && (
  <DocumentDetailModal
    isOpen={isDocumentModalOpen}
    onClose={() => {
      setIsDocumentModalOpen(false);
      setSelectedDocumentId(null);
    }}
    documentId={selectedDocumentId}
  />
)}
```

### 4. **ESC 키 이벤트 개선 (모달 안의 모달)**

```typescript
// ⭐ Phase 10-6: DocumentDetailModal이 열려있으면 ConsultationDetailModal의 ESC는 무시
useEffect(() => {
  const handleEscape = (e: KeyboardEvent) => {
    if (e.key === 'Escape' && isOpen && !isDocumentModalOpen) {
      onClose();
    }
  };

  if (isOpen) {
    document.addEventListener('keydown', handleEscape);
    document.body.style.overflow = 'hidden';
  }

  return () => {
    document.removeEventListener('keydown', handleEscape);
    document.body.style.overflow = 'unset';
  };
}, [isOpen, isDocumentModalOpen, onClose]);
```

---

## 🔗 데이터 흐름

### **Mock 모드 (현재)**

```
1. ConsultationDetailModal 렌더링
   ↓
2. 참조 문서 목록 표시 (documentId: 'card-1-1-1')
   ↓
3. 사용자가 문서 클릭
   ↓
4. DocumentDetailModal 열림 (documentId 전달)
   ↓
5. DocumentDetailModal이 scenarios.ts에서 검색
   ↓
   for (const scenario of scenarios) {
     for (const step of scenario.steps) {
       const found = step.currentSituationCards.find(card => card.id === 'card-1-1-1');
       if (found) return found;
     }
   }
   ↓
6. 전체 문서 상세 정보 표시 (약관, 시스템 경로, 필수 확인 사항 등)
```

### **DB 연동 후 (Real 모드)**

```
1. ConsultationDetailModal 렌더링
   ↓
2. GET /api/v1/consultations/{id}/documents
   응답: [{ id: 'card-1-1-1', title: '...' }]
   ↓
3. 참조 문서 목록 표시
   ↓
4. 사용자가 문서 클릭
   ↓
5. DocumentDetailModal 열림 (documentId 전달)
   ↓
6. GET /api/v1/documents/card-1-1-1
   ↓
7. 전체 문서 상세 정보 표시
```

---

## 📊 통일된 구조

### ✅ **현재 상태 (Phase 10-6 완료 후)**

| 페이지 | 참조 문서 UI | 데이터 소스 | 상태 |
|--------|-------------|-------------|------|
| **상담 상세 (ConsultationDetailModal)** | DocumentDetailModal 모달 | scenarios.ts | ✅ 완료 |
| **자주 찾는 문의 (FrequentInquiryModal)** | DocumentDetailModal 모달 | scenarios.ts | ✅ 완료 |
| **후처리 (AfterCallWorkPage)** | DocumentDetailModal 모달 | scenarios.ts | ✅ 완료 |

### 🎯 **일관성 보장**

1. **동일한 컴포넌트**
   - 모든 페이지에서 `DocumentDetailModal` 사용

2. **동일한 데이터 소스**
   - 모든 문서는 `scenarios.ts`에서 `documentId`로 검색

3. **동일한 UI/UX**
   - 모달 스타일, 레이아웃, ESC 키 동작 일관성

4. **DB 연동 준비 완료**
   - `documentId` 기반 구조로 API 연동 용이

---

## 🗄️ 데이터베이스 스키마 (권장)

### **documents 테이블**

```sql
CREATE TABLE documents (
  id VARCHAR(50) PRIMARY KEY,           -- 'card-1-1-1' (현재 구조 유지)
  scenario_id VARCHAR(50),              -- 'scenario-1'
  step_number INT,                      -- 1, 2, 3
  card_type VARCHAR(50),                -- 'current' or 'next'
  title VARCHAR(200) NOT NULL,
  keywords TEXT[],                      -- {'카드분실', '긴급정지'}
  content TEXT,
  system_path VARCHAR(500),
  required_checks TEXT[],
  exceptions TEXT[],
  time VARCHAR(50),
  note TEXT,
  regulation TEXT,
  full_text TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### **consultation_documents 테이블 (중간 테이블)**

```sql
CREATE TABLE consultation_documents (
  consultation_id VARCHAR(50) REFERENCES consultations(id),
  document_id VARCHAR(50) REFERENCES documents(id),
  step_number INT,                      -- 조회 순서
  used BOOLEAN DEFAULT false,           -- 클릭 여부
  view_count INT DEFAULT 0,
  referenced_at TIMESTAMP DEFAULT NOW(),
  PRIMARY KEY (consultation_id, document_id)
);
```

---

## 🧪 테스트 체크리스트

### ✅ **동작 확인**

- [x] 대시보드 → 상담 상세 → 참조 문서 클릭 → **DocumentDetailModal 정상 표시**
- [x] 상담관리 → 상담 상세 → 참조 문서 클릭 → **DocumentDetailModal 정상 표시**
- [x] 자주 찾는 문의 → 관련 문서 → **DocumentDetailModal 정상 표시** (기존 기능)
- [x] 후처리 → 참조 문서 → **DocumentDetailModal 정상 표시** (기존 기능)

### ✅ **ESC 키 동작**

- [x] ConsultationDetailModal 열림 → ESC → **모달 닫힘**
- [x] ConsultationDetailModal → 참조 문서 클릭 → DocumentDetailModal 열림
  - ESC 1번 → **DocumentDetailModal 닫힘** (ConsultationDetailModal은 유지)
  - ESC 2번 → **ConsultationDetailModal 닫힘**

### ✅ **데이터 일관성**

- [x] 'card-1-1-1' 클릭 → **"카드 즉시 사용 정지"** 상세 정보 표시
- [x] 'card-1-1-2' 클릭 → **"분실 신고 접수 완료"** 상세 정보 표시
- [x] 'card-1-1-3' 클릭 → **"재발급 카드 신청"** 상세 정보 표시
- [x] 모든 페이지에서 동일한 문서 ID → **동일한 상세 정보 표시**

---

## 📝 수정된 파일

### 1. `/src/app/components/modals/ConsultationDetailModal.tsx`

**변경 사항:**
- ✅ DocumentDetailModal import 추가
- ✅ 상태 관리 추가 (`isDocumentModalOpen`, `selectedDocumentId`)
- ✅ Mock 데이터 문서 ID 수정 (`'doc1'` → `'card-1-1-1'`)
- ✅ 참조 문서 UI 변경 (Accordion → 클릭 가능한 버튼)
- ✅ DocumentDetailModal 렌더링 추가
- ✅ ESC 키 이벤트 개선 (모달 안의 모달 처리)

---

## 🎉 결과

### ✅ **버그 수정 완료**
- 대시보드/상담관리에서 참조 문서 클릭 정상 작동

### ✅ **UI/UX 일관성 확보**
- 모든 페이지에서 동일한 문서 상세보기 경험 제공

### ✅ **중앙 관리 구조 완성**
- `DocumentDetailModal` 하나로 모든 문서 표시 통일

### ✅ **DB 연동 준비 완료**
- `documentId` 기반 구조로 API 연동 용이

---

## 🚀 향후 작업

### **Phase 11: DB 연동 (예정)**

1. **DocumentDetailModal API 연동**
   ```typescript
   // Mock 모드
   if (USE_MOCK_DATA) {
     const doc = findDocument(); // scenarios.ts에서 검색
   }
   // Real 모드
   else {
     const response = await fetch(`/api/v1/documents/${documentId}`);
     const doc = await response.json();
   }
   ```

2. **상담 참조 문서 API 연동**
   ```typescript
   // GET /api/v1/consultations/{id}/documents
   // 응답: [{ id: 'card-1-1-1', title: '...', ... }]
   ```

3. **Feature Flag 전환**
   ```typescript
   // /src/config/mockConfig.ts
   export const USE_MOCK_DATA = false; // Mock → Real
   ```

---

## 📚 관련 문서

- [참조문서 DB연동 가이드](/docs/참조문서_DB연동_가이드.md)
- [Phase 10-2: UI개선 Toast알림](/docs/Phase10-2_UI개선_Toast알림.md)
- [시나리오 데이터 구조](/docs/08_시나리오_데이터.md)

---

**작성자:** AI Assistant  
**마지막 업데이트:** 2025-01-23  
**Phase:** 10-6  
**상태:** ✅ 완료
