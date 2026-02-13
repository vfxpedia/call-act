# 01_F: Frontend 협업 응답 및 Phase A 실행 계획

> **담당**: Frontend
> **날짜**: 2026-02-10
> **참조**: `01_DISCUSSION.md`, `01_B_프론트협업응답_및_STT진단.md`, `01_D_document_identity_and_keywords.md`

---

## 3가지 결정 사항에 대한 Frontend 입장

### 결정 1: 문서 ID 방침 → ✅ 동의 (Option B: 현 ID + sourceTable)

**동의 이유**:
- Frontend에서 `rag-${timestamp}` prefix를 붙이는 곳은 `convertRagToScenarioCard()`의 **fallback**임
- Backend가 DB 원본 ID를 이미 보내고 있다면, fallback이 작동하는 건 id 필드가 비어있을 때뿐
- sourceTable이 함께 오면 DocumentDetailModal에서 문서 조회 API 호출 가능

**Frontend 조치**:
- `convertRagToScenarioCard()`에서 id fallback 로직 개선 (빈 ID 경고 로그)
- DocumentDetailModal에 sourceTable 기반 조회 로직 추가 (Phase C)

### 결정 2: referenced_documents 확장 → ✅ 동의

**동의 이유**: 모든 추가 필드가 optional이므로 하위 호환 문제 없음

**Frontend 조치**:
- `ReferencedDocument` 인터페이스에 optional 필드 추가
- 상담 종료 시 RAG 카드에서 documentType, sourceTable 함께 저장
- 상담 상세 내역에서 documentType으로 아이콘/색상 즉시 표시

### 결정 3: FAQ snake_case → ✅ 동의

**Frontend 현황 확인**:
- `FrequentInquiryModal.tsx`에서 `detail.relatedDocument.document_id`로 접근 중
- Backend에서 `documentId`로 변경하면 Frontend도 맞춰 수정

---

## Phase A: Frontend 자체 작업 (즉시 착수)

### Step 1: 문서 변환 유틸리티 중앙화

**문제**: RAGCard→ScenarioCard 변환, API snake→camel 변환이 각 컴포넌트에 분산

**작업**: `utils/documentTransformer.ts` 생성
- `normalizeRAGCard(ragCard) → ScenarioCard` - RAG 응답 정규화
- `normalizeApiDocument(apiDoc) → ScenarioCard` - API 응답 정규화 (snake→camel)
- `resolveDocumentType(card) → DocumentType` - documentType 결정 (DB값 우선 → 추론 fallback)

**영향 범위**:
- `RealTimeConsultationPage.tsx` - convertRagToScenarioCard 교체
- `ConsultationDetailModal.tsx` - getDocumentsFromDB 교체
- `searchSimulator.ts` - searchWithRAG 변환 교체

### Step 2: DocumentDetailModal Real 데이터 대응

**문제**: 문서 찾기 순서가 Mock 우선 (scenarios→searchMock→documentData→title검색)

**작업**:
- documentData prop이 있으면 **즉시 사용** (Mock 검색 건너뛰기)
- documentData 없을 때만 기존 fallback 체인 사용
- "문서를 찾을 수 없습니다" 대신 최소한 제목+요약 표시

### Step 3: fullText 없을 때 graceful UI

**문제**: fullText가 null이면 "전체 약관" 섹션이 비어보임

**작업**:
- content(요약)를 메인 표시, fullText가 있으면 확장 가능한 "전문 보기" 섹션
- fullText null일 때: "요약 정보만 제공됩니다" 안내 메시지

### Step 4: rag- prefix ID fallback 개선

**문제**: `convertRagToScenarioCard`에서 id 비어있으면 `rag-${timestamp}` 생성 → DB ID와 단절

**작업**:
- Backend가 이미 DB 원본 ID를 보내므로, fallback은 경고 로그 + 임시 ID
- 임시 ID 생성 시 sourceTable 정보 포함하여 추후 추적 가능하게

---

## 검증 계획

| Step | 검증 방법 | 성공 기준 |
|------|----------|----------|
| 1 | 빌드 성공 + 기존 기능 동일 작동 | vite build 성공, 시나리오 모드/다이렉트콜 모두 정상 |
| 2 | Real 모드에서 상담 상세 → 참조 문서 클릭 | 빈 모달 대신 최소한 제목+요약 표시 |
| 3 | fullText null인 카드 상세 열기 | "요약만 제공" 안내 표시, 빈 영역 없음 |
| 4 | 다이렉트콜 RAG 응답 콘솔 로그 | id 필드에 DB 원본 ID 확인, rag- fallback 미사용 |

---

## 롤백 계획

모든 변경은 `fix/responsive-layout` 브랜치에서 진행.
각 Step 완료 후 커밋으로 롤백 포인트 확보.

---

*Phase A 완료 후, B/D팀 Phase A 결과와 합쳐서 Phase B(합의) → Phase C(연동) 진행.*
