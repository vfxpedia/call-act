# 01_B: RAG 파이프라인 문서 타입 연동

> **담당**: Backend
> **상태**: 대기 (01_D Step 1 완료 후 착수)
> **날짜**: 2026-02-10
> **의존**: 01_D (DB에서 document_type 확립)

---

## 배경

DB 담당이 모든 문서에 `document_type` 필드를 부여합니다 (01_D Step 1).
Backend는 이를 RAG 검색 결과와 API 응답에 반영해야 합니다.

## 작업 범위

### 1. RAG 검색 결과에 document_type 포함

현재 RAG 결과의 ScenarioCard에 `documentType` 필드가 이미 정의되어 있으나,
실제 DB 검색 시 해당 필드를 채워서 반환하지 않음.

**변경 필요**:
- `retriever/db.py`: vector_search / text_search 결과에 `document_type` 컬럼 포함
- `pipeline/search.py`: 검색 결과 ScenarioCard 빌드 시 `documentType` 매핑
- `rag_frontend.py`: 응답에 `documentType` 필드 전달

### 2. 환경변수 조정 (즉시 가능)

```env
RAG_MATCH_CARD_NAMES=1          # 카드명만으로 vocab match 통과
# weak_intent 확장은 signals.py 수정 필요
```

### 3. saveConsultation API 확장 (01_D Step 4 이후)

`referenced_documents` JSONB에 확장 필드 수용:
```json
{
  "documentType": "guide",
  "sourceTable": "service_guide_documents",
  "category": "분실/도난",
  "relevanceScore": 85
}
```

기존 필드와 하위 호환 유지.

### 4. 문서 상세 조회 API (신규 또는 기존 확장)

현재 프론트에서 문서 상세를 볼 때 mock 데이터를 순차 탐색함.
DB에서 직접 조회하는 엔드포인트가 필요할 수 있음:

```
GET /api/v1/documents/{document_id}
→ service_guide_documents, card_products, notices 순차 조회
→ document_type, content, keywords, metadata 반환
```

---

## DB 세션에서 전달받을 정보

- Step 1 완료 시: 각 테이블의 document_type 분포 및 매핑 규칙
- Step 2 완료 시: 키워드 추출 결과 통계 (검색 테스트 가능)
- Step 4 협의: referenced_documents 확장 스키마 확정

---

*이 문서는 DB 작업(01_D) 진행에 따라 업데이트됩니다.*
