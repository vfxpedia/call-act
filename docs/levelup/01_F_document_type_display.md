# 01_F: 문서 타입 기반 표시 통일

> **담당**: Frontend
> **상태**: 대기 (01_D Step 1 + 01_B 완료 후 착수)
> **날짜**: 2026-02-10
> **의존**: 01_D (DB document_type), 01_B (API에서 타입 반환)

---

## 배경

현재 `DocumentDetailModal`에서 title 기반으로 documentType을 추론합니다.
DB에서 정확한 document_type을 제공하면, 추론 대신 **DB 값을 우선** 사용합니다.

## 작업 범위

### 1. DocumentType 소스 변경

```typescript
// 현재: title 기반 추론 (항상)
const type = inferDocumentType(title, content);

// 변경: DB 값 우선, 없으면 추론 fallback
const type = card.documentType || inferDocumentType(title, content);
```

### 2. ReferencedDocument 인터페이스 확장

```typescript
// 현재
interface ReferencedDocument {
  stepNumber: number;
  documentId: string;
  title: string;
  used: boolean;
  viewCount?: number;
}

// 확장 (하위 호환)
interface ReferencedDocument {
  stepNumber: number;
  documentId: string;
  title: string;
  used: boolean;
  viewCount?: number;
  // 신규 (optional)
  documentType?: DocumentType;
  sourceTable?: string;
  category?: string;
  relevanceScore?: number;
}
```

### 3. 상담 이력에서 문서 타입 표시

referenced_documents에 저장된 documentType으로 아이콘/색상 즉시 적용.
재추론 불필요.

---

## DB/Backend에서 전달받을 정보

- RAG 검색 결과에 `documentType` 필드 포함 여부
- `GET /api/v1/documents/{id}` 엔드포인트 가용 여부
- referenced_documents 확장 스키마 확정

---

*이 문서는 DB/Backend 작업 진행에 따라 업데이트됩니다.*
