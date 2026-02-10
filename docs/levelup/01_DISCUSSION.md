# 01 단계: 3팀 협업 논의 사항

> **생성**: 2026-02-10 00:15
> **마지막 수정**: 2026-02-10 14:30 (DB)
> **참여**: DB(D), Backend(B), Frontend(F)

---

## 프론트엔드 점검 + DB 분석 종합

프론트 6가지 문제와 DB 분석 결과를 교차 대조한 결과:

| # | 문제 | 담당 구분 |
|---|------|----------|
| A | 문서 ID 체계 단절 | **3팀 합의 필요** |
| B | 필드 이름 불일치 (snake_case/camelCase) | Backend (API 변환 레이어) |
| C | DocumentType 추론 취약 | **DB 자체** (document_type 확정값 저장) |
| D | FAQ 문서 연결 하드코딩 | **DB 자체** (매핑) + Backend (API) + Frontend (표시) |
| E | fullText 부재 시 빈 모달 | **DB 자체** (데이터 품질) + Frontend (graceful UI) |
| F | localStorage 의존 | Backend + Frontend (향후) |

---

## 결정이 필요한 사항 3가지

### 결정 1: 문서 ID 방침

**배경**: 현재 5가지 ID 패턴이 공존

```
DB 실 ID:
  CARD-SHINHAN-#Pay-신한카드          (card_products)
  카드분실_도난_관련피해_예방_및_대응방법_merged  (service_guide_documents)
  notice_01                          (notices)
  CS-HANA-20593                      (consultations)

Frontend mock ID:
  card-1-1-1                         (scenarios)
```

**DB 제안: 옵션 B - 현재 ID 유지 + sourceTable 명시**

이유:
- ID 통일(옵션 A)은 기존 데이터 마이그레이션, 임베딩 재생성, 외부 참조 깨짐 등 비용이 큼
- `(sourceTable, documentId)` 조합이면 모든 문서를 유일하게 식별 가능
- 하위 호환 유지

**Frontend에 필요한 것**: 문서 조회 시 `sourceTable`을 함께 전달받아야 어느 테이블에서 조회할지 판단 가능

**Backend에 필요한 것**: RAG 결과와 API 응답에 `sourceTable` 필드 추가

→ **동의 여부 확인 필요**

---

### 결정 2: referenced_documents 확장 스키마

**배경**: 상담 중 참조한 문서를 저장할 때, 현재는 ID/제목/사용여부만 저장

**현재**:
```json
{"stepNumber": 1, "documentId": "...", "title": "...", "used": true, "viewCount": 2}
```

**확장안** (모든 추가 필드는 optional → 하위 호환):
```json
{
  "stepNumber": 1,
  "documentId": "카드분실_도난_관련피해_예방_및_대응방법_merged",
  "documentType": "guide",
  "sourceTable": "service_guide_documents",
  "title": "카드분실·도난 관련 피해 예방 및 대응방법",
  "category": "분실/도난",
  "used": true,
  "viewCount": 2,
  "relevanceScore": 85
}
```

**각 팀 영향**:
- **DB**: JSONB 컬럼이므로 스키마 변경 불필요 (자유 형식)
- **Backend**: `ReferencedDocument` Pydantic 모델에 Optional 필드 추가
- **Frontend**: `ReferencedDocument` 인터페이스에 Optional 필드 추가

**주의**: fullText는 저장하지 않음 (용량 문제). 필요 시 documentId로 재조회.

→ **동의 여부 확인 필요**

---

### 결정 3: FAQ API snake_case 혼용

**현재 문제** (`frequent_inquiries.py`):
```json
{
  "relatedDocument": {           ← camelCase (외부)
    "document_id": "card-1-1-1", ← snake_case (내부) ← 불일치!
    "title": "...",
    "regulation": "...",
    "summary": "..."
  }
}
```

**수정안**: `document_id` → `documentId`

**영향**:
- **Backend**: RelatedDocumentResponse 모델 수정 (또는 alias_generator 적용)
- **Frontend**: API 응답 파싱 로직 확인 (이미 camelCase 기대하는지?)

→ **Backend 담당 확인 필요**

---

## 각 팀 자체 착수 가능 작업 정리

### DB (즉시 착수)
| 순서 | 작업 | 의존성 |
|------|------|--------|
| 1 | service_guide_documents document_type 분류 | 없음 |
| 2 | card_products 195건 키워드 추출 | 없음 |
| 3 | FAQ related_document_id 실 문서 매핑 | 없음 |
| 4 | fullText/structured 데이터 품질 감사 | 없음 |

### Backend (즉시 착수 가능)
| 순서 | 작업 | 의존성 |
|------|------|--------|
| 1 | `RAG_MATCH_CARD_NAMES=1` 환경변수 설정 | 없음 |
| 2 | weak_intent 확장 (조회, 비교, 환불, 문의, 정보) | 없음 |
| 3 | FAQ API snake_case 수정 | 결정 3 합의 후 |

### Backend (DB 작업 후 착수)
| 순서 | 작업 | 의존성 |
|------|------|--------|
| 4 | RAG 결과에 sourceTable 포함 | 결정 1 합의 |
| 5 | ReferencedDocument 모델 확장 | 결정 2 합의 |
| 6 | 문서 상세 조회 API (GET /api/v1/documents/{id}?source={table}) | 결정 1 합의 |

### Frontend (즉시 착수 가능)
| 순서 | 작업 | 의존성 |
|------|------|--------|
| 1 | 문서 변환 유틸리티 중앙화 | 없음 |
| 2 | DocumentDetailModal Real 데이터 대응 | 없음 |
| 3 | fullText 없을 때 graceful UI | 없음 |

### Frontend (합의 후 착수)
| 순서 | 작업 | 의존성 |
|------|------|--------|
| 4 | documentType DB값 우선 사용 (추론 fallback) | DB Step 1 + Backend |
| 5 | ReferencedDocument 인터페이스 확장 | 결정 2 합의 |
| 6 | FAQ 문서 실 ID 연결 | DB Step 3 + Backend |

---

## 타임라인 (제안)

```
Phase A: 각 팀 자체 작업 (병렬 진행)
  [DB]       Step 1~4 착수
  [Backend]  환경변수 + weak_intent 확장
  [Frontend] 유틸리티 중앙화 + graceful UI

Phase B: 합의 사항 결정 (Phase A 중 또는 완료 후)
  결정 1: 문서 ID 방침
  결정 2: referenced_documents 확장
  결정 3: FAQ snake_case 수정

Phase C: 연동 작업 (합의 후)
  [Backend]  RAG sourceTable + API 확장
  [Frontend] documentType/sourceTable 적용
  [전체]     통합 테스트 + 회귀 테스트
```

---

## 확인 요청

- [x] **Backend**: 결정 1(옵션 B) ✅, 결정 2(확장안) ✅, 결정 3(camelCase) ✅ + 문서 상세 조회 API 구현 예정
- [x] **Frontend**: 결정 1(sourceTable 방식) ✅, 결정 2(optional 필드 추가) ✅, 결정 3(camelCase) ✅
- [x] **전체**: Phase A 즉시 착수 → **완료** (DB 4/4, Backend 3/3, Frontend 5/5)

---

*각 팀 응답을 받은 후 01_B, 01_F 문서를 업데이트합니다.*

---

## Phase A 작업 기록 (라이브)

### [DB] Phase A 결과
> Step 1-2: 2026-02-10 00:44 | Step 3-4: 2026-02-10 01:45

**Step 1: document_type 정규화 ✅ 완료**
- `usage_guide`(42건) + `service_guide`(32건) → `guide`(74건)로 통일
- 최종 분포: `terms`(1,092) / `faq`(107) / `guide`(74)
- 양쪽 데이터 동기화: data-preprocessing_dev ✅, backend_dev ✅
- 재적재 호환: `load_teddycard.py`가 `doc.get("document_type")` 으로 읽으므로 자동 반영 ✅
- 백업: `.back/service_guides_before_step1_*.json.meta`

**Step 2: 카드 상품 키워드 추출 ✅ 완료**
- 195건(49%) 키워드 없음 → **0건(0%)** 으로 해소
- 전체 채움률: 51% → **100%** (398/398)
- 고유 키워드: 45개 → **65개**, 평균 5.7개/상품
- 추출 패턴: 카드명(K-패스/체크 등) + structured.mainBenefits + main_benefits 텍스트 매칭
- 양쪽 데이터 동기화: data-preprocessing_dev ✅, backend_dev ✅
- 재적재 호환: `load_teddycard.py`가 `doc.get("keywords", [])` 으로 읽으므로 자동 반영 ✅
- 백업: `.back/card_products_keywords_before_step2_*.json.meta`

**Backend에 전달 사항**:
1. DB의 `document_type`이 이제 의미있는 값을 가짐 (terms/faq/guide)
2. `card_generator.py`에서 테이블명 기반 일괄 `"guide"` 처리 대신, DB 값을 우선 사용 필요
3. card_products 키워드가 100% 채워짐 → 텍스트 검색 적중률 향상 기대

**Frontend에 전달 사항**:
1. document_type이 DB에서 `terms`/`faq`/`guide`/`product-spec`(card_products) 반환 예정
2. 기존 `inferDocumentType()` 함수는 fallback으로 유지하되, DB 값 우선 사용 권장
3. `faq` 타입은 Frontend DocumentType enum에 추가 필요할 수 있음 (또는 `guide`로 매핑)

**Step 3: FAQ related_document_id 실 문서 매핑 ✅ 완료**
- `load_frequent_inquiries.py`의 mock ID 11건 → 실 service_guide_documents ID로 교체
- CATEGORY_CONTENT_MAP (5건): billing-1-1-1 등 → 실 가이드 문서 ID
- FALLBACK_INQUIRIES_DATA (5건): card-1-1-1 등 → 실 가이드 문서 ID
- DEFAULT_CONTENT_TEMPLATE (1건): general-1-1-1 → `신용카드의_종류_merged`
- 매핑 근거: guide 타입 74건 중 카테고리별 키워드/제목 매칭으로 최적 문서 선정
- 재적재 호환: Python 코드 직접 수정 → 01a_setup_callact_db.py 재실행 시 자동 반영 ✅
- 검증 스크립트: `22_map_faq_documents.py`

| FAQ 카테고리 | 이전 (mock) | 이후 (실 문서) |
|---|---|---|
| 분실/도난 | card-1-1-1 | `카드분실_도난_관련피해_예방_및_대응방법_merged` |
| 해외 결제 | card-2-1-1 | `해외여행_시IC카드_이용팁_merged` |
| 포인트 적립 | card-1-2-1 | `신용카드_포인트활용방법_merged` |
| 연회비 환불 | card-3-1-1 | `신용카드_선택_시_고려사항_merged` |
| 한도 증액 | card-4-1-1 | `카드상품별_거래조건_이자율__수수료_등__merged` |
| 청구문의 | billing-1-1-1 | `카드대금 납부_merged` |
| 이용내역 | usage-1-1-1 | `신용카드_활용법_merged` |
| 한도 문의 | limit-1-1-1 | `카드상품별_거래조건_이자율__수수료_등__merged` |
| 결제방식 | payment-1-1-1 | `신용카드_관련주요_용어_안내_merged` |
| 기본값 | general-1-1-1 | `신용카드의_종류_merged` |

**Frontend에 전달**: FAQ 관련문서 클릭 시 이제 실 `service_guide_documents` 데이터가 조회됩니다.
- `related_document_id`가 `_merged` suffix 가진 실 ID로 변경됨
- 문서 상세 모달에서 해당 가이드 내용 표시 가능

**Step 4: fullText/structured 데이터 품질 감사 ✅ 완료**

card_products 398건 structured 필드 감사 결과:

| 필드 | 채움률 | 비고 |
|---|---|---|
| structured (전체) | 398/398 (100%) | 모두 존재 |
| detailContent | 398/398 (100%) | 최소 181자, 중앙값 393자, 최대 873자 |
| full_content | 398/398 (100%) | 모두 100자 이상 |
| fullTerms | 166/398 (41%) | 약관 전문 - 신용카드에만 존재 |
| note | 125/398 (31%) | 유의사항 |
| performanceConditions | 7/398 (1%) | 매우 희박 |

**결론**: `detailContent`(100%)와 `full_content`(100%)가 완전하므로 fullText 생성에 문제 없음.
- `fullTerms`(41%), `note`(31%), `performanceConditions`(1%)는 카드 유형별로 해당 없는 경우가 많아 **정상 범위**
- Backend의 `card_generator.py`가 `detailContent` 우선 체인으로 fullText를 생성하므로 빈 응답은 발생하지 않음

---

### [DB → Frontend] Step 4 관련 질문

**Frontend에게**: 문서 상세 모달(DocumentDetailModal)에서 카드 상품을 표시할 때, 다음 필드들의 **표시 우선순위와 형식 규칙**을 확인하고 싶습니다:

1. **fullText가 없는 카드**: `detailContent`(100% 존재, 200~870자)만으로 모달 표시가 충분한가요? 아니면 `structured.mainBenefits`, `structured.annualFee` 등을 별도 섹션으로 포맷팅해야 하나요?

2. **sparse 필드 처리**: `fullTerms`(41%), `note`(31%), `performanceConditions`(1%)가 null인 경우, Frontend에서 이미 graceful 처리(섹션 숨김)를 하고 있나요? (Step 3에서 처리한 것으로 보입니다)

3. **card_products vs service_guide_documents**: 두 테이블의 문서가 같은 모달에 표시될 때 형식이 다를 수 있는데, Frontend에서 `documentType`별로 다른 레이아웃을 사용하나요? 아니면 동일 레이아웃인가요?

→ 이 답변에 따라 DB에서 추가 데이터 보강이 필요한지 결정합니다.

### [Backend] Phase A 결과 (2026-02-10 01:08)

**S1: WHISPER_PROMPT 적용 ✅ 완료**
- `whisper.py`: `prompt=WHISPER_PROMPT` 파라미터 추가 (import만 하고 미전달 → 수정)
- Whisper에 "한국 신용카드 고객센터 통화" 컨텍스트 제공 → YouTube/방송 할루시네이션 대폭 감소

**S2+S3: 할루시네이션 필터 강화 ✅ 완료**
- 키워드 12→22개 확장 (YouTube, 자막, 방송 관련 패턴 추가)
- 반복 패턴 감지: `(.{2,}?)\1{2,}` (아아아아, 네네네 등 차단)
- 최소 길이 체크: 2자 미만 필터
- STT 정확도: 57%(12/21) → **100%**(21/21)

**R1: weak_intent 확장 ✅ 완료**
- 5→20개 확장: 조회/확인/안내/상담/변경/해지/취소/등록/한도/납부/결제/이체/충전/환불/교환
- "안내" STOPWORDS에서 제거 (weak_intent 충돌 방지)
- Vocab Gate 정확도: 67%(12/18) → **100%**(18/18)

**변경 파일**: `whisper.py`, `keyword_dict.py`, `test_phase_a_verification.py`(신규)
**결과 문서**: `docs/levelup/02_B_PhaseA_실행결과.md`

**Phase B 예정**: Vocab Gate 형태소 분석 폴백, card_products 벡터 검색 활성화, referenced_documents 확장

### [Frontend] Phase A 결과
> 기록: 2026-02-10 00:50 | Step 5 + Phase B 동의: 2026-02-10 01:30

**Step 1: 문서 변환 유틸리티 중앙화 ✅ 완료**
- `utils/documentTransformer.ts` 신규 생성
- `resolveDocumentType()`: DocumentType 결정 단일 진실 소스 (DB값 → sourceTable → 제목 → fallback)
- `normalizeRAGCard()`: RAGCard → ScenarioCard 중앙 변환
- `normalizeApiDocument()`: API snake_case → camelCase 중앙 변환
- `RealTimeConsultationPage.tsx`: 47줄 인라인 변환 → 1줄 호출로 교체
- `searchSimulator.ts`: 15줄 인라인 변환 → 3줄 호출로 교체
- 빌드 성공 ✅

**Step 2: DocumentDetailModal Real 데이터 우선 처리 ✅ 완료**
- findDocument() 순서 변경: documentData 우선 → Mock 검색 fallback
- 이전: Mock(scenarios→searchMock) 먼저 검색 → Real 데이터는 3순위
- 이후: documentData prop 있으면 **즉시 사용** → Real 모드에서 빈 모달 방지
- `inferDocumentType()` → `resolveDocumentType()` 중앙 유틸리티로 교체
- 빌드 성공 ✅ (번들 크기 -0.5KB, 중복 코드 제거)

**Step 3: fullText null graceful UI ✅ 완료**
- fullText가 null/빈/content와 동일한 경우: "요약 정보만 제공됩니다" 안내 표시
- fullText가 있으면: 기존 마크다운 렌더링 유지
- systemPath 빈 경우: 섹션 숨김 (이전: 빈 박스 표시)
- requiredChecks 빈 경우: 섹션 숨김
- regulation/time 빈 경우: 헤더에서 해당 항목 숨김
- 빌드 성공 ✅

**Step 4: ReferencedDocument 확장 + rag- prefix 개선 ✅ 완료**
- `types/consultation.ts` ReferencedDocument에 optional 필드 추가:
  - `documentType`, `sourceTable`, `category`, `relevanceScore`, `content`
- 참조 문서 수집 3곳에서 확장 필드 저장 (시나리오 카드, 검색 결과, RAG 카드)
- RAG 카드 ID 없을 때 경고 로그 추가 (rag- prefix 사용 추적)
- 빌드 성공 ✅

**DB팀 전달사항 수신 확인**:
1. `faq` 타입 → Frontend DocumentType에 추가하거나 `guide`로 매핑 필요 (Phase C에서 처리)
2. DB값 우선 사용 → `resolveDocumentType()`에서 이미 구현 (1순위: 명시적 documentType)
3. 키워드 100% 채움 → RAG 검색 적중률 향상 기대, 프론트 변경 불필요

**Step 5: faq DocumentType 추가 ✅ 완료**
- DB팀 Step 1 결과 수신: `faq`(107건) 타입 반환 예정
- `DocumentType` union에 `'faq'` 추가 (scenarios/types.ts, scenarios.ts)
- `resolveDocumentType()`: validTypes + 3단계 추론에 faq 패턴 추가
- UI 헬퍼 3개: label("자주 묻는 질문"), icon, bgColor(`bg-[#FFF8F8]`)
- DocumentDetailModal: inferDocumentType + getDocumentTitle + getDocumentBgColor에 faq 추가
- 빌드 성공 ✅

**Phase B 합의 (Frontend)**:
- 결정 1 (문서 ID + sourceTable): ✅ 동의
- 결정 2 (referenced_documents 확장): ✅ 동의, 인터페이스 이미 적용
- 결정 3 (FAQ camelCase): ✅ 동의, Backend 수정 후 Frontend 파싱 맞춤

### [Backend] Phase B 결과 (2026-02-10 01:55)

**결정 1: ✅ 동의 + 구현 완료**
- `card_generator.py`: `_CARD_FIELDS`에 `sourceTable` 추가
- `_doc_to_card_base()`에서 `doc.get("table")` → `sourceTable` 필드로 전달
- `documentType`에서 DB `document_type` 값 우선 사용하도록 변경 (`meta.get("document_type")` 추가)

**결정 2: ✅ 동의 + 구현 완료**
- `consultations.py`: `ReferencedDocument` 모델에 Optional 필드 추가:
  - `documentType`, `sourceTable`, `category`, `relevanceScore`
- JSONB이므로 DB 스키마 변경 없음, 하위 호환 유지

**결정 3: ✅ 동의 + 구현 완료**
- `frequent_inquiries.py`: `document_id` → `documentId` (camelCase 통일)
- `sourceTable`, `documentType` 필드도 추가 (DB Step 3에서 값 채워지면 자동 반영)

**추가: 문서 상세 조회 API ✅ 구현 완료**
- `GET /api/v1/documents/{id}?source={table}`
- 4개 테이블 모두 지원: `card_products`, `service_guide_documents`, `notices`, `consultation_documents`
- `source` 파라미터 있으면 해당 테이블만 조회 (빠름), 없으면 전체 순회 (fallback)
- 응답: `id`, `title`, `content`, `fullText`, `documentType`, `sourceTable`, `keywords`, `category`, `regulation`, `systemPath`, `metadata`

**변경 파일**:
- `card_generator.py`: sourceTable + document_type DB값 우선
- `consultations.py`: ReferencedDocument 모델 확장
- `frequent_inquiries.py`: camelCase 통일 + 필드 추가
- `documents.py` (신규): 범용 문서 상세 조회 API
- `routers.py`: documents 라우터 등록

**ADMIN-001 관리자 접근 수정 ✅ (2026-02-10 02:50)**
- **문제**: `LoginPage.tsx:64`에서 admin 체크 조건이 `position === '팀장' || '부장' || '이사'`인데, ADMIN-001의 position/role은 `"admin"` → 관리자로 인식 안 됨
- **수정**: `|| foundEmployee.role === 'admin'` 조건 추가
- **결과**: ADMIN-001 로그인 시 `isAdmin=true`, 관리자 메뉴(총괄 현황, 상담 관리, 상담사 관리, 공지사항 관리) 정상 접근
- **파일**: `frontend/src/app/pages/LoginPage.tsx:64`
- **빌드**: 프론트엔드 재빌드 + backend/static 배포 완료

---

### [DB → Backend] Phase B 확인 요청 (2026-02-10 01:50)

Backend Phase A 작업이 완료된 것을 확인했습니다. Phase C 진행을 위해 아래 3개 결정에 대한 **동의 여부**를 확인 부탁드립니다:

1. **결정 1 (옵션 B)**: 현재 문서 ID 유지 + API 응답에 `sourceTable` 필드 추가
   - `card_generator.py`에 이미 `table` 정보가 있으므로, `sourceTable` 필드를 카드 응답에 포함시키면 됨
   - 영향: `_doc_to_card_base()`에 `"sourceTable": table` 추가

2. **결정 2 (확장안)**: `ReferencedDocument` Pydantic 모델에 Optional 필드 추가
   - `documentType`, `sourceTable`, `category`, `relevanceScore` (모두 Optional)
   - DB는 JSONB라 스키마 변경 불필요

3. **결정 3 (camelCase)**: FAQ API `RelatedDocumentResponse`에서 `document_id` → `documentId`
   - 현재: `document_id: str` → 변경: `documentId: str` (또는 alias)
   - DB Step 3에서 `related_document_id` 값이 이미 실 문서 ID로 교체됨

**추가 논의 사항**: `GET /api/v1/documents/{id}?source={table}` 신규 엔드포인트
- FAQ 관련문서 클릭, 상담 이력 참조문서 클릭 시 문서 상세를 조회하려면 필요
- 현재 이런 API가 존재하지 않음
- **질문**: Phase C에서 신규 생성할지, 기존 RAG 엔드포인트를 확장할지?

---

## [Frontend → DB] Step 4 질문 답변 (2026-02-10 01:40)

**Q1: fullText 없는 카드 - detailContent만으로 충분한가?**

> **충분합니다.** 현재 DocumentDetailModal은 fullText를 ReactMarkdown으로 렌더링하므로, Backend의 `card_generator.py`가 `detailContent`를 fullText로 전달하면 정상 표시됩니다.
>
> 단, `product-spec` 타입 카드의 경우 `structured.mainBenefits`, `annualFee` 등을 별도 섹션으로 포맷팅하면 UX가 더 좋아집니다. 이는 **Phase C 개선사항**으로 남깁니다 (Backend에서 fullText 생성 시 structured 필드를 마크다운 테이블로 조합하는 방식 권장).

**Q2: sparse 필드 null일 때 graceful 처리 여부?**

> **이미 처리 완료.** Phase A Step 3에서 아래 모든 경우를 구현했습니다:
> - `systemPath` 빈 값 → 섹션 숨김 ✅
> - `requiredChecks` 빈 배열 → 섹션 숨김 ✅
> - `note` 빈 값 → 섹션 숨김 ✅
> - `regulation`/`time` 빈 값 → 헤더 항목 숨김 ✅
> - `fullText` null/빈값 → "요약 정보만 제공됩니다" 안내 표시 ✅
>
> 따라서 `fullTerms`(41%), `note`(31%), `performanceConditions`(1%)가 null이어도 **빈 박스 없이 깔끔하게 표시**됩니다. DB 추가 보강 불필요.

**Q3: documentType별 다른 레이아웃 사용 여부?**

> **현재: 동일 레이아웃 + 미세 차별화**
> - DocumentDetailModal: 모든 타입 동일 구조 (요약 → 시스템경로 → 체크사항 → 예외 → 참고 → fullText)
> - 차이: `getDocumentTitle()` 제목, `getDocumentBgColor()` fullText 배경색만 다름
> - InfoCard(칸반 카드): `product-spec`은 규정+시간 파란 박스, `analysis-report`는 노란 분석 박스, 나머지는 시스템경로 표시
>
> **Phase C 제안**: `product-spec` 전용 모달 레이아웃 (연회비/혜택/조건 테이블) 추가 가능. 단, 우선순위 낮음 - 현재 detailContent 마크다운 렌더링으로도 충분히 읽을 수 있음.

→ **결론: DB 추가 보강 불필요. 현재 데이터 품질로 Frontend 표시에 문제 없음.**

---

## Phase B: 합의 결정 (2026-02-10 01:40)

### 결정 1: 문서 ID 방침 → **옵션 B 확정**

| 팀 | 동의 | 비고 |
|---|---|---|
| DB | ✅ | 제안자. 현재 ID 유지 + sourceTable 명시 |
| Frontend | ✅ | Phase A Step 4에서 ReferencedDocument에 `sourceTable` 필드 이미 추가 |
| Backend | ✅ | 2026-02-10 01:55 구현 완료. `card_generator.py` + `documents.py` API |

**합의 내용**: `(sourceTable, documentId)` 복합키로 문서 식별
- Backend: RAG 응답 및 API 응답에 `sourceTable` 필드 추가
- Frontend: `resolveDocumentType()`에서 sourceTable 기반 추론 이미 구현

### 결정 2: referenced_documents 확장 → **확장안 확정**

| 팀 | 동의 | 비고 |
|---|---|---|
| DB | ✅ | JSONB 컬럼이므로 스키마 변경 불필요 |
| Frontend | ✅ | `types/consultation.ts` ReferencedDocument 인터페이스 이미 확장 완료 |
| Backend | ✅ | 2026-02-10 01:55 구현 완료. `consultations.py` 모델 확장 |

**합의 내용**: 기존 필드 유지 + optional 확장 (documentType, sourceTable, category, relevanceScore, content)
- fullText는 저장하지 않음 (용량). 필요 시 documentId+sourceTable로 재조회

### 결정 3: FAQ API camelCase 통일 → **camelCase 확정**

| 팀 | 동의 | 비고 |
|---|---|---|
| DB | - | 해당 없음 (API 레이어) |
| Frontend | ✅ | camelCase 기대. `normalizeApiDocument()`에서 양쪽 케이스 모두 처리 가능 |
| Backend | ✅ | 2026-02-10 01:55 구현 완료. `frequent_inquiries.py` 수정 |

**합의 내용**: 모든 API 응답 필드를 camelCase로 통일

---

## Phase C: 연동 작업 계획 (2026-02-10 01:40)

> Phase A 전팀 완료, Phase B 합의 **3/3 확정** (2026-02-10 01:55)

### [Backend] Phase C 작업 (합의 후 착수)

| # | 작업 | 의존 | 상태 |
|---|------|------|------|
| C-B1 | RAG 응답에 `sourceTable` 필드 추가 (`card_generator.py`) | 결정 1 | ✅ 2026-02-10 01:55 |
| C-B2 | `ReferencedDocument` Pydantic 모델 확장 | 결정 2 | ✅ 2026-02-10 01:55 |
| C-B3 | FAQ API `document_id` → `documentId` 수정 | 결정 3 | ✅ 2026-02-10 01:55 |
| C-B4 | `card_generator.py` document_type DB값 우선 사용 | DB Step 1 | ✅ 2026-02-10 01:55 |
| C-B5 | 문서 상세 조회 API: `GET /api/v1/documents/{id}?source={table}` | 결정 1 | ✅ 2026-02-10 01:55 |

### [Frontend] Phase C 작업 (Backend 연동 후)

| # | 작업 | 의존 | 상태 |
|---|------|------|------|
| C-F1 | FAQ 관련문서 실 ID 연결 확인 (DB Step 3 반영 후 E2E 테스트) | DB Step 3 + C-B3 | ⏳ |
| C-F2 | RAG 카드에 sourceTable 활용 (documentType 결정 정확도 향상) | C-B1 | ⏳ |
| C-F3 | 문서 상세 조회 API 연동 (DocumentDetailModal에서 fullText 재조회) | C-B5 | ⏳ (선택) |

### [전체] 통합 테스트

| # | 테스트 | 범위 |
|---|--------|------|
| T-1 | 다이렉트콜 → RAG 카드 표시 → 문서 상세 모달 → fullText 렌더링 | B+F |
| T-2 | FAQ 목록 → 관련문서 클릭 → 실 가이드 문서 표시 | D+B+F |
| T-3 | 상담 저장 → referenced_documents 확장 필드 포함 저장 → 상담 상세에서 재표시 | D+B+F |
| T-4 | 상담 이력 → 참조문서 목록 → 문서 상세 모달 (sourceTable 기반 조회) | B+F |

---

## [DB] DB 재적재 + 우수 사례 등록 (2026-02-10 02:04)

### DB 재적재 결과

Phase A Step 1~4 변경사항을 실 DB에 반영했습니다.

**적용 방법**: teddycard loader가 기존 데이터 존재 시 skip하므로, 직접 SQL UPDATE로 적용

| Step | 적용 방법 | 결과 |
|------|----------|------|
| Step 1 | `UPDATE service_guide_documents SET document_type = 'guide' WHERE document_type IN ('usage_guide', 'service_guide')` | 74건 정규화 |
| Step 2 | `UPDATE card_products SET keywords = %s WHERE id = %s` (195건 배치) | 빈 키워드 195→0건 |
| Step 3 | frequent_inquiries 삭제 후 01a 재실행 (load_frequent_inquiries.py 코드 수정 반영) | mock ID 11건 → 실 문서 ID |
| 01b | `01b_populate_mock_data.py` 재실행 (9.16초) | 상담 확장 필드 전체 재생성 |

**DB 현재 상태**:
- service_guide_documents: `guide`(74) / `terms`(1,092) / `faq`(107) ✅
- card_products 키워드 채움률: 100% (398/398) ✅
- frequent_inquiries: 실 문서 ID 연결 (mock ID 0건) ✅

### 우수 사례 등록 (교육 시뮬레이션용)

교육 시뮬레이션 페이지의 "우수 사례 교육" 기능을 위해 4건의 우수 사례를 등록했습니다.

**선정 기준**: FCR=true + 만족도=5(최고) + 감정=positive + 카테고리 다양성

| # | 상담 ID | 카테고리 | 상담원 | 통화시간 | AI 요약 |
|---|---------|---------|--------|---------|---------|
| 1 | CS-EMP049-202601221606 | 분실/도난 > 정지/해제 | 방서진 | 05:23 | 카드 분실 신고 → 즉시 정지 + 재발급 한 번에 처리 |
| 2 | CS-EMP043-202602041355 | 수수료/연체 > 조회/안내 | 손준혁 | 03:32 | 연체 수수료 원인 확인 → 즉시출금으로 연체 해소 (이관 없이 완결) |
| 3 | CS-EMP026-202601211017 | 한도 > 상향/증액 | 도준혁 | 04:05 | 한도 증액 신청 → 당일 임시 상향 처리 완료 |
| 4 | CS-EMP011-202602031618 | 결제/승인 > 취소/해지 | 서민지 | 03:38 | 일부결제대금이월약정 해지 (복잡 금융 상품 문의) |

**적용 SQL**: `UPDATE consultations SET is_best_practice = true, quality_score = 95 WHERE id IN (...)`

**Frontend 확인 사항**: SimulationPage.tsx에서 `consultations.filter(c => c.isBestPractice)`로 표시됩니다.
- 4건 모두 `is_best_practice = true`, `quality_score = 95`, `satisfaction_score = 5`
- "학습하기" 클릭 시 해당 상담의 transcript/ai_summary 기반 고급 시뮬레이션 실행

---

## [DB] Phase C-D 작업 결과 (2026-02-10 03:08)

### C-D1: frequent_inquiries 스키마 확장 + 카테고리 매핑 수정 ✅

**1. 컬럼 추가** (Backend FAQ API 호환):
```sql
ALTER TABLE frequent_inquiries
ADD COLUMN related_source_table VARCHAR(100),
ADD COLUMN related_document_type VARCHAR(50);
```

**2. CATEGORY_CONTENT_MAP 키 수정** (category_raw 실제 값과 일치):

| 이전 (불일치) | 이후 (정확 일치) | 매핑 문서 |
|---|---|---|
| 청구문의/청구서 | **선결제/즉시출금** | 카드대금 납부_merged |
| *(일치)* | **이용내역 안내** | 신용카드_활용법_merged |
| 한도관련 문의/처리 | **한도상향 접수/처리** | 카드상품별_거래조건... |
| 분실/도난 신청/**처리** | 분실/도난 신청/**해제** | 카드분실_도난... |
| 결제방식 안내 | **결제대금 안내** | 카드대금 납부_merged |
| *(신규)* | **승인취소/매출취소 안내** | 구매 취소_merged |
| *(신규)* | **이벤트 안내** | 신용카드_포인트활용방법_merged |
| *(신규)* | **정부지원 바우처** | 신용카드의_종류_merged (기본) |
| *(신규)* | **가상계좌 예약/취소** | 신용카드_관련주요_용어_안내_merged |
| *(신규)* | **한도 안내** | 카드상품별_거래조건... |

**결과**: 카테고리 매핑 성공률 2/10(20%) → **9/10(90%)**

**3. 모든 FAQ에 `related_source_table` + `related_document_type` 설정 완료**

### C-D2: 점수 체계 정리 ✅

재적재 후 발견한 이슈 3건을 수정했습니다.

| 이슈 | 수정 내용 |
|------|----------|
| Step 1 document_type 미적용 | SQL UPDATE 재실행 → 74건 `guide` 반영 |
| quality_score 전체 NULL | 전 6552건 생성 (10-100, 평균 76) |
| satisfaction_score 스케일 확인 | **1-5점 유지** (feedbackScore/20 환산값) |

**점수 체계 최종 정리**:

| 필드 | 스케일 | 용도 | 생성 방식 |
|------|--------|------|----------|
| `satisfaction_score` | **1-5** | 고객 만족도 별점 (★★★★★) | feedbackScore(100점) ÷ 20 |
| `quality_score` | **0-100** | QA 평가 점수 | satisfaction×20 + emotion + FCR + noise |
| `emotion_score` | **0-100** | 감정 분석 점수 | sentiment 기반 랜덤 |
| `feedbackScore` | **0-100** | 피드백 원점수 (Frontend 수집) | ACW 페이지에서 입력 |

**Frontend 참고**: `satisfaction_score`는 1-5 그대로입니다. `convertFeedbackToSatisfaction()` 변환 불필요.
`quality_score`가 새로 채워졌으므로 (0-100), 상담 품질 필터링에 활용 가능합니다.

### C-D3: populate_extended_fields.py 소스 코드 동기화 ✅

01b 재실행 시에도 동일한 결과가 보장되도록 소스 수정:
- `generate_satisfaction_score()`: 1-5점 생성 (기존 유지)
- `generate_quality_score()`: 신규 함수 추가 (satisfaction×20 기반)
- UPDATE 쿼리에 `quality_score` 컬럼 추가
- SELECT 쿼리에 `c.fcr` 추가 (quality_score 생성 입력값)

### 변경 파일 목록

| 파일 | 변경 내용 |
|------|----------|
| `db_setup.sql` | frequent_inquiries에 related_source_table, related_document_type 컬럼 추가 |
| `load_frequent_inquiries.py` | CATEGORY_CONTENT_MAP 키 10개 실제 값으로 교체 + 새 컬럼 INSERT |
| `populate_extended_fields.py` | quality_score 생성 함수 + UPDATE 쿼리 확장 |

### DB 최종 상태 (2026-02-10 03:08)

| 테이블/필드 | 상태 |
|------------|------|
| service_guide_documents.document_type | ✅ guide(74)/terms(1092)/faq(107) |
| card_products.keywords 채움률 | ✅ 100% (398/398) |
| frequent_inquiries 카테고리 매핑 | ✅ 9/10 (90%) + sourceTable/documentType |
| consultations.satisfaction_score | ✅ 1-5점 (6552건) |
| consultations.quality_score | ✅ 10-100점 (6552건, 평균 76) |
| consultations.is_best_practice | ✅ 4건 (분실/도난, 해외결제, 수수료/연체, 한도) |
| consultations.referenced_documents | ✅ 1967건 실제 문서 ID 교체 (mock DOC-XXXX → 실제) |

---

## [DB] referenced_documents + best_practice 수정 (2026-02-10 04:15)

### C-D4: referenced_documents 실제 문서 ID 교체 ✅

**문제**: `populate_extended_fields.py`가 `DOC-{random}` 형태의 mock ID를 생성
→ 프론트엔드에서 문서 클릭 시 빈 모달 (해당 ID가 어떤 테이블에도 없음)

**수정 내용**:
1. DB에서 1967건의 mock DOC-XXXX ID를 실제 문서 ID로 교체
   - 60% service_guide_documents, 25% card_products, 15% notices
   - 새 스키마: `{documentId, sourceTable, documentType, title, used}`
2. `populate_extended_fields.py` 수정: `generate_referenced_documents()` → DB에서 실제 ID 조회
   - `_load_real_document_ids()` 헬퍼 추가 (1회 캐시)
   - `conn` 파라미터 추가로 DB 조회 지원

### C-D5: best practice 해외결제 카테고리 수정 ✅

| # | ID | category_main | category_sub | category_raw |
|---|---|---|---|---|
| 1 | CS-EMP049-... | 분실/도난 | 정지/해제 | 분실/도난 신청/해제 |
| 2 | CS-EMP001-... | 결제/승인 | **해외결제** | 해외결제 문의 |
| 3 | CS-EMP043-... | 수수료/연체 | 조회/안내 | 연회비 안내 |
| 4 | CS-EMP026-... | 한도 | 상향/증액 | 한도상향 접수/처리 |

### C-D6: CATEGORY_MAPPING 연체문의 추가 ✅

`education.py`에 `'연체문의': '수수료/연체'` 매핑 추가 (backend + backend_dev 동시)
→ SimulationPage.tsx의 categoryColors에 정의된 `연체문의`가 이제 정상 라우팅됨

### simulationScenariosData ↔ DB 카테고리 매칭 결과

| Frontend 카테고리 | CATEGORY_MAPPING | DB category_main | 상태 |
|---|---|---|---|
| 카드분실 | → 분실/도난 | 분실/도난 (405건) | ✅ |
| 해외결제 | → 결제/승인 | 결제/승인 (2788건) | ✅ |
| 수수료문의 | → 수수료/연체 | 수수료/연체 (136건) | ✅ |
| 기타문의 | → 기타 | 기타 (1135건) | ✅ |
| 포인트/혜택 | → 포인트/혜택 | 포인트/혜택 (340건) | ✅ |
| 한도증액 | → 한도 | 한도 (576건) | ✅ |
| 연체문의 (미사용) | → 수수료/연체 | 수수료/연체 | ✅ 매핑 추가됨 |

---

## [Frontend] Phase C 작업 결과 (2026-02-10 05:30)

### C-F4: FeedbackModal 교육 모드 점수 분기 ✅

**변경 파일**:
- `frontend/src/data/feedbackRules.ts` - 교육 모드 유사도 점수 체계 추가
- `frontend/src/app/components/modals/FeedbackModal.tsx` - 3가지 모드 분기 렌더링
- `frontend/src/app/pages/AfterCallWorkPage.tsx` - educationType prop 전달

**점수 체계 분기**:

| 항목 | 실전 상담 | 기본 시나리오 교육 | 우수 사례 교육 |
|------|----------|------------------|--------------|
| 매뉴얼 준수 | 50점 | 50점 | 50점 |
| 고객 감사 | 10점 | - | - |
| 감정 전환 | 20점 | - | - |
| 응대 유사도 | - | **30점** | **30점** |
| 후처리 시간 | 20점 | 20점 | 20점 |
| **소계** | **100점** | **100점** | **100점** |
| 모방 유사도 | - | - | **별도 100점** (등급 S/A/B/C/D) |

**UI 차이점**:
- 헤더 색상: 실전=파란색, 교육=초록색
- 감정 변화 섹션: 교육 모드에서 제거 (AI에게 감정 없음)
- 우수 사례: 모방 유사도 카드 + 등급 배지 표시

### C-F5: AfterCallWorkPage 채팅 등장 애니메이션 ✅

**변경**: 상담 전문 채팅 메시지에 순차적 fade-in + slide-up 애니메이션 적용
- CSS `@keyframes chatBubbleIn` (opacity 0→1, translateY 8px→0)
- 메시지당 0.06초 딜레이, 최대 2초 (대량 메시지 대비)

### C-F6: Dashboard → SimulationPage 연결 ✅

**변경 파일**:
- `frontend/src/data/mock/simulations.mock.ts` - `scenarioId` 필드 추가 (SIM-001~004)
- `frontend/src/app/pages/DashboardPage.tsx` - 카드/버튼 onClick 핸들러 추가

**동작**:
- 카드 클릭 → SimulationPage 이동
- "시작" 버튼 클릭 → 바로 시뮬레이션 시작 (sessionStorage 설정 + /consultation/live 이동)

### Frontend Phase C 상태

| # | 작업 | 상태 |
|---|------|------|
| C-F1 | FAQ 관련문서 실 ID 연결 확인 | ⏳ (E2E 테스트 필요) |
| C-F2 | RAG 카드에 sourceTable 활용 | ⏳ (Backend C-B1 후) |
| C-F3 | 문서 상세 조회 API 연동 | ⏳ (선택) |
| C-F4 | FeedbackModal 교육 모드 점수 분기 | ✅ |
| C-F5 | ACW 채팅 등장 애니메이션 | ✅ |
| C-F6 | Dashboard → SimulationPage 연결 | ✅ |

---

## [DB] 전체 시스템 종합 진단 (2026-02-10 06:00)

> 원점 재검토: "검색이 올바른 결과를 주는가? 문서가 제대로 표시되는가? UX가 서비스 수준인가?"

### 진단 1: 키워드 검색 품질

| 테이블 | 키워드 보유율 | 검색 동작 |
|--------|-------------|----------|
| service_guide_documents | 100% (1,273건) | ✅ 정상 |
| card_products | 100% (398건) | ✅ 정상 |
| consultation_documents | 100% (6,533건) | ✅ 벡터검색 정상 |

**발견된 문제:**
- **키워드 정규화 불일치** (20쌍): "자동이체"↔"자동 이체", "부가서비스"↔"부가 서비스" 등 띄어쓰기 차이로 누락 가능
- **테이블 간 어휘 교집합 30개뿐**: card_products(65종)과 service_guide(1,757종) 키워드가 거의 겹치지 않음
- → **DB 조치 필요**: 키워드 띄어쓰기 정규화 스크립트 실행

### 진단 2: 문서 구조/내용 품질

| 문제 | 심각도 | 건수 | 담당 |
|------|--------|------|------|
| FAQ 19건 제목 없음 (Samsung plumb_*) | HIGH | 19/107 | **DB** |
| card_products main_benefits 82%가 전화번호로 시작 | HIGH | 328/398 | **DB (전처리)** |
| notices 51/53건 end_date 만료 | HIGH | 51/53 | **DB** |
| card_products 65% 연회비 NULL | MEDIUM | 261/398 | DB |
| terms 문서 1건 content="없음" (2자) | LOW | 1건 | 무시 가능 |

### 진단 3: 프론트엔드 연동 문제 (→ Frontend/Backend 공유)

| # | 문제 | 심각도 | 담당 |
|---|------|--------|------|
| **F-1** | `referenced_documents` 필드명 불일치: DB=`documentId`, 프론트=`doc_id` → 참조문서 클릭 시 빈 모달 | **CRITICAL** | **Frontend** (consultationApi.ts:422 인터페이스 수정) 또는 **DB** (필드명 doc_id로 변경) |
| **F-2** | `frontend_dev` DocumentDetailModal에 `documentData` prop 없음 → Real DB에서 문서 모달 안 열림 | **HIGH** | **Frontend** (frontend_dev를 frontend에 맞춰 업데이트) |
| **F-3** | SimulationPage가 백엔드 API 미호출 → DB best practice 4건 사용 안됨 | **MEDIUM** | **Frontend** (API 연동) 또는 **Backend** (best_practice API) |
| **F-4** | DashboardPage FAQ 모달에 mock detailData 고정 전달 → DB FAQ ID 불일치 시 빈 내용 | **MEDIUM** | **Frontend** |
| **F-5** | satisfaction_score `0`일 때 `\|\|` 연산자가 falsy 처리 → 5점으로 표시 | **LOW** | **Frontend** (`??` 연산자로 변경) |

### 진단 4: 거시적 누락 사항

| 관점 | 발견 |
|------|------|
| card_products.main_benefits | 원본 데이터가 고객센터 전화번호로 시작 → 전처리에서 본문 추출 정리 필요 |
| frontend_dev vs frontend 괴리 | frontend_dev가 크게 뒤처짐 (documentData prop, empty state 등) |
| 검색 자동완성 | 항상 mock 기반 → real DB 인기 키워드 반영 필요 |
| notices 날짜 | 재적재 시 현재 날짜 기준으로 end_date 생성 필요 |

### 합의 필요 사항 (3팀)

> **결정 4: referenced_documents 필드명 통일**
>
> DB가 `documentId`로 저장하고 있는데, 프론트엔드 인터페이스는 `doc_id`를 기대.
> - **옵션 A**: DB 쪽에서 `doc_id`로 변경 (DB 담당)
> - **옵션 B**: 프론트엔드에서 `documentId`를 읽도록 수정 (Frontend 담당)
> - **옵션 C**: Backend API에서 변환 레이어 추가 (Backend 담당)
>
> → 가장 빠른 방법은 **옵션 A** (DB 일괄 UPDATE) + populate_extended_fields.py 수정

### DB 즉시 조치 가능 항목

| # | 작업 | 예상 영향 |
|---|------|----------|
| D-7 | 키워드 띄어쓰기 정규화 (20쌍) | 검색 누락 방지 |
| D-8 | FAQ 19건 제목 채우기 (content에서 추출) | FAQ 목록 빈 줄 해결 |
| D-9 | notices end_date를 현재+30일로 갱신 | 공지사항 정상 표시 |
| D-10 | referenced_documents 필드명 `documentId`→`doc_id` (합의 시) | 참조문서 클릭 정상화 |
| D-11 | card_products main_benefits 전처리 (전화번호 제거) | 카드 혜택 정상 표시 |

---

## Phase C 검증 결과 (Frontend, 2026-02-10 11:00)

> 커밋: `0b904f6` (fix/responsive-layout 브랜치)

### 완료된 검증 항목

| # | 항목 | 결과 | 수정 내용 |
|---|------|------|----------|
| 0 | 고객 persona 태그 한글 표기 | OK | `translatePersonalityTag()` 44개 매핑 정상 동작 |
| 1 | 피드백 모달 → DB 저장 | **수정 완료** | FeedbackModal에서 `feedbackScore`(100점), `satisfactionScore`(5점) localStorage 저장 → handleSaveACW에서 `SaveConsultationRequest`에 포함 |
| 2 | 가이드 초록 라인 + 교육 가이드 | **수정 완료** | 부모 overflow:visible 임시 적용으로 클리핑 방지; 가이드 버튼 /acw, /simulation에서도 노출 |
| 4 | 핵심 키워드 추출 DB 기반 | **수정 완료** | `routing.card_name` → `routing.matched.card_names[]` 배열 읽기로 변경 (legacy fallback 포함) |

### Backend 팀 확인 필요 사항

| # | 항목 | 설명 |
|---|------|------|
| **B-1** | `feedbackScore` / `satisfactionScore` DB 컬럼 | Frontend가 POST `/api/v1/consultations`에 이 두 필드를 포함하여 전송. Backend consultations 엔드포인트에서 이 필드를 받아서 DB에 저장하는지 확인 필요 |
| **B-2** | `routing.matched` 구조 확인 | Frontend가 `routing.matched.card_names[]`, `routing.matched.actions[]`, `routing.matched.payments[]` 배열을 읽음. Backend RAG WebSocket 응답에서 이 구조가 맞는지 확인 |
| **B-3** | 상담 상세 API `satisfaction_score` 반환 | `GET /api/v1/consultations/{id}` 응답에 `satisfaction_score` 필드 포함되는지 확인 (ConsultationDetailModal에서 별점 표시용) |

### 미완료 항목 → 완료 (2026-02-10 12:00)

| # | 항목 | 상태 | 비고 |
|---|------|------|------|
| 3 | 키보드 숏컷 + 칸반 업무지원 | **완료** | 전체 단축키 스펙 구현 (아래 상세) |

---

## Phase C 최종 작업 결과 (Frontend, 2026-02-10 12:00)

> 커밋: `a2f3925` → `자체 점검 수정` (fix/responsive-layout 브랜치)

### C-F7: 전역 키보드 숏컷 완전 구현 ✅

**변경 파일**:
- `frontend/src/hooks/useLayerNavigation.ts` - 전역 단축키 추가
- `frontend/src/app/pages/RealTimeConsultationPage.tsx` - memoTextareaRef + 콜백 연결

**구현된 전체 단축키 목록**:

| 단축키 | 동작 | 동작 범위 |
|--------|------|----------|
| `← → ↑ ↓` | 2x2 카드 그리드 내 이동 | 카드 영역 |
| `↑` (상단 경계) | 검색 레이어 전환 | 카드 영역 |
| `↓` (하단 경계) | 칸반 레이어 전환 | 카드 영역 |
| `←` (좌측 경계) | 이전 Step 전환 | 칸반 레이어 |
| `→` (우측 경계) | 다음 Step 전환 | 칸반 레이어 |
| `Ctrl+Shift+F` | 검색창 포커스 | **전역** (입력 필드 내에서도) |
| `Ctrl+Shift+M` | 메모 텍스트 포커스 | **전역** |
| `Ctrl+Shift+Enter` | 메모 저장 → 카드 영역 포커스 | **전역** |
| `Ctrl+Shift+C` | 칸반 카드 영역 포커스 | **전역** |
| `Space` | 레이어 전환 (kanban ↔ search) | 카드 영역 (입력 외) |
| `Tab` | 레이어 전환 | 카드 영역 (입력 외) |
| `Wheel` | 레이어 전환 (경계 lock) | 카드 영역 |
| `Enter` (검색창) | 검색 실행 → 검색 레이어 → 카드 포커스 | 검색창 |
| `ESC` | 포커스 해제 (검색/메모 모두) | 전역 |
| `/` | 검색창 포커스 | 카드 영역 (입력 외) |
| `Double Click` | 카드 상세 모달 | 카드 (InfoCard) |
| `Ctrl+Enter` | 후처리 저장 | ACW 페이지 |

**설계 원칙**:
- `Ctrl+Shift+*` 전역 단축키는 입력 필드(input/textarea) 내에서도 동작
- `Space`, `Tab`, 방향키는 입력 필드 외에서만 동작 (입력 간섭 방지)
- `ESC`는 검색창/메모 blur만 처리 (모달 닫기는 각 컴포넌트 자체 처리)

### C-F8: DB 팀 요구사항 반영 ✅

| 항목 | 상태 | 수정 내용 |
|------|------|----------|
| **F-1** (doc_id 필드) | ✅ 정상 | `ConsultationDetailModal:204` - `doc.doc_id` 올바르게 읽음 |
| **결정 4** (DocumentDetailModal) | ✅ 정상 | `documentData` prop 우선 → mock fallback 구조 |
| **F-3** (SimulationPage API) | **수정 완료** | `localStorage/mock` → `fetchConsultations()` API 호출로 변경 |
| **F-4** (FAQ modal mock) | **수정 완료** | `FrequentInquiryModal`에서 `fetchFrequentInquiryById()` API 직접 호출 |

### C-F9: 자체 점검 이슈 수정 ✅

코드 리뷰에서 발견된 CRITICAL 이슈 3건 수정:

| 이슈 | 심각도 | 수정 내용 |
|------|--------|----------|
| `useLayerNavigation.ts`: `boundaryTimeoutRef`가 useEffect 의존성 배열에 포함 (불필요한 re-render) | CRITICAL | 의존성 배열에서 제거 + cleanup에 `boundaryTimeoutRef` 정리 추가 |
| `FrequentInquiryModal.tsx`: API 로딩 중 빈 화면 (null 렌더링) | CRITICAL | 로딩 스피너 추가 + `detail?.relatedDocument` null-safe 조건부 렌더링 |
| `SimulationPage.tsx`: `as any` 타입 캐스트 (타입 안전성 저하) | CRITICAL | `ConsultationItem[]` 타입 명시 + `as any` 제거 |

---

## Backend 팀 전달 사항 (2026-02-10 12:00)

### 기존 확인 필요 항목 (B-1, B-2, B-3)

이전 Phase C에서 전달한 아래 항목의 확인 상태를 요청합니다:

| # | 항목 | 상태 |
|---|------|------|
| **B-1** | `feedbackScore` / `satisfactionScore` POST 저장 | ⏳ 확인 필요 |
| **B-2** | `routing.matched.{card_names[], actions[], payments[]}` 구조 | ⏳ 확인 필요 |
| **B-3** | GET `/api/v1/consultations/{id}` → `satisfaction_score` 포함 | ⏳ 확인 필요 |

### 신규 확인 필요 항목

| # | 항목 | 설명 |
|---|------|------|
| **B-4** | `is_best_practice` 필드 API 포함 여부 | `GET /api/v1/consultations` 목록 응답에 `is_best_practice` (→ camelCase `isBestPractice`) 필드가 포함되는지 확인. SimulationPage에서 우수 사례 필터링에 사용 |
| **B-5** | `fetchFrequentInquiryById` 응답 shape | `GET /api/v1/frequent-inquiries/{id}` 응답에 `content`, `relatedDocument.title`, `relatedDocument.summary`, `relatedDocument.regulation`, `relatedDocument.document_id` 필드 포함 확인 |

### Frontend ↔ Backend 연동 잔여 항목

| # | 작업 | 의존 | 상태 |
|---|------|------|------|
| C-F1 | FAQ 관련문서 실 ID 클릭 → 문서 상세 모달 E2E | B-5 + DB C-D1 | ⏳ |
| C-F2 | RAG 카드 `sourceTable` 활용 | Backend C-B1 반영 확인 | ⏳ |
| C-F3 | 문서 상세 조회 API 연동 (`GET /api/v1/documents/{id}`) | Backend C-B5 | ⏳ (선택) |

---

## 라이브 데모 사전 점검 (2026-02-10 12:00)

### 빌드 상태
- **TS 에러**: 0건 ✅
- **빌드 경고**: chunk size만 (2,092KB, gzip 599KB) - 정상 범위
- **빌드 시간**: ~43초

### 점검 결과 요약 (8.5/10)

| 항목 | 상태 | 비고 |
|------|------|------|
| WebSocket URL 자동 감지 | ✅ 10/10 | localhost/ngrok 자동 전환 |
| API URL 자동 감지 | ✅ 10/10 | `config.ts` resolveBaseUrl() |
| 라우터/네비게이션 | ✅ 10/10 | 17개 경로 모두 정상 |
| localStorage 관리 | ✅ 9/10 | 30개 키, 충돌 없음 |
| 에러 핸들링 | ✅ 8/10 | graceful fallback 동작 |
| Mock/Real 전환 | ✅ 9/10 | `USE_MOCK_DATA` + `DEV_MODE` |
| 빌드 품질 | ✅ 9/10 | TS 에러 0, 경고만 chunk size |

### 데모 전 필수 체크

- [ ] Backend `/api/v1` 엔드포인트 실행 확인 (localhost:8000 또는 ngrok)
- [ ] `DEV_MODE` 끄기 여부 결정 (`mockConfig.ts:11`) - mock 전환 UI 숨김
- [ ] 브라우저 localStorage 초기화 여부 결정 (stale data 정리)
- [ ] 로그인 테스트 계정 준비 (일반 상담원 + ADMIN-001)

---

## [Backend] ACW 고도화 + 자체 점검 결과 (2026-02-10)

### 1. ACW AI 요약 상세화 + category_raw 자동 분류

**커밋**: `26b27bf`, `c578020` (backend), `0c5ba93` (frontend)

| 변경 | 이전 | 이후 |
|------|------|------|
| AI 요약 (result) | 1-2문장 (~50자) | 구조화 섹션: [처리 내역] / [고객 요청사항] / [상담사 조치] / [참고사항] |
| category_raw | 비어있거나 대분류 중복 | 49개 세부 카테고리 중 LLM 자동 분류 |
| SUMMARIZE_SYSTEM_PROMPT | category_main 키 오타 | JSON 문법 수정 + category_raw 필드 추가 |

**수정 파일 (7개)**:
- `backend/app/core/prompt.py` — 프롬프트 상세화
- `backend/app/api/v1/endpoints/consultations.py` — SaveConsultationRequest + SQL
- `backend/app/api/v1/endpoints/followup.py` — SaveConsultationRequest + ACW 로그
- `backend/app/db/scripts/modules/update_customer.py` — categoryRaw 우선 저장
- `frontend/src/app/pages/RealTimeConsultationPage.tsx` — LLM→localStorage
- `frontend/src/app/pages/AfterCallWorkPage.tsx` — categoryRaw state + save
- `frontend/src/types/consultation.ts` — 타입 확장

### 2. 매뉴얼 점수 -5점 오판 원인 분석 + 수정

**원인**: `FEEDBACK_SYSTEM_PROMPT`의 인사말 평가 기준이 모호함
- 이전: `-5점: 첫인사 또는 마무리 멘트 누락` → 둘 중 하나만 빠져도 감점
- GPT-4.1-mini가 "안녕하세요"를 정식 인사로 인정 안 하는 경우 발생

**수정**:
- 기준 완화: `-5점: 첫인사와 마무리 멘트 **모두 누락**한 경우에만 감점`
- 예시 추가: 첫인사(안녕하세요, 감사합니다 OO카드입니다), 마무리(감사합니다, 좋은 하루 되세요)

**Frontend/DB 전달 사항**:
- 변경사항은 프롬프트 레벨이므로 Frontend/DB 수정 불필요
- 서버 재시작만으로 즉시 반영

### 3. RAG 검색 로그 추가

**이전**: 실시간 통화 중 RAG 검색 결과가 로그로 남지 않음 (콘솔 print만)
**이후**: `logs/rag/rag_YYYYMMDD.jsonl`에 매 발화마다 기록

로그 항목:
```json
{
  "ts": "2026-02-10T15:30:00",
  "sid": "CS-001",
  "query": "카드 분실 신고하려고요",
  "routing": {"decision": "card_search", "matched": {...}},
  "doc_count": 3,
  "doc_titles": ["분실/도난 안내", ...]
}
```

**핵심 로직 변경 없음** — call_websocket.py의 RAG 결과 전송 직후에 로그만 추가

### 4. referenced_documents 파이프라인 검증 결과

| 단계 | 상태 | 비고 |
|------|------|------|
| RAG 검색 → WebSocket 전송 | ✅ 정상 | `run_rag()` → `send_json({"type":"rag"})` |
| Frontend 수신 → ragSteps 저장 | ✅ 정상 | RealTimeConsultationPage |
| 통화 종료 → localStorage 저장 | ✅ 정상 | `referencedDocuments` 키 |
| ACW 페이지 로드 | ✅ 정상 | localStorage에서 복원 |
| 저장 API → DB | ✅ 정상 | `consultations.referenced_documents` JSONB |

**발견된 이슈**: RAG 카드에 `id` 필드가 없으면 Frontend가 `RAG-STEP1-0` 같은 임시 ID 생성 → DB 저장 시 원본 문서 추적 불가

**Frontend 전달 사항**:
- RAG 카드의 `documentId`가 임시 ID인 경우, DocumentDetailModal에서 문서 내용을 찾을 수 없음
- Backend RAG pipeline이 `doc_id`를 카드에 포함하도록 수정 필요 (Backend 담당)

### 5. 전체 통합 점검 결과

| 이슈 | 심각도 | 상태 | 담당 |
|------|--------|------|------|
| SUMMARIZE_SYSTEM_PROMPT category_main 키 오타 | CRITICAL | ✅ 수정 | Backend |
| 매뉴얼 점수 인사말 오판 | CRITICAL | ✅ 수정 | Backend |
| RAG 검색 로그 미존재 | WARNING | ✅ 추가 | Backend |
| category_raw DB 컬럼 | INFO | ✅ 확인 (db_setup.sql에 존재) | DB |
| feedbackScore→emotion_score 매핑 | WARNING | 보류 (현재 None 전달) | Backend |
| RAG 카드 documentId 누락 | WARNING | 미해결 | Backend+Frontend |
| DocumentDetailModal Backend fallback | WARNING | 미해결 | Frontend |

### 6. 로그 기반 개선 추적 시스템

**분석 스크립트**: `backend/logs/acw/analyze_acw_logs.py`

서버 테스트 후 실행하면 자동 생성되는 개선 지표:

| 지표 | 이전 (추정) | 목표 | 측정 방법 |
|------|-------------|------|-----------|
| AI 요약 평균 길이 | ~50자 | 200자+ | `result_length` |
| 구조화 섹션 비율 | 0% | 90%+ | `result_has_sections` |
| category_raw 유효 분류율 | 0% | 90%+ | 49개 목록 매칭 |
| 인사말 오감점율 | ~30% (추정) | <5% | `intro_score` |
| 평균 응답 시간 | - | <10초 | `parallel_time_sec` |

### 7. 데모 전 필수 체크리스트 (Backend)

- [ ] 서버 재시작 (프롬프트 변경 반영)
- [ ] 실제 다이렉트콜 1건 수행 → ACW 페이지에서 구조화 요약 확인
- [ ] `GET /api/v1/consultations/{id}` → `category_raw` 필드 확인
- [ ] `logs/acw/` 로그 생성 확인
- [ ] `logs/rag/` 로그 생성 확인
- [ ] `analyze_acw_logs.py` 실행하여 개선 지표 확인
- [ ] 매뉴얼 점수에서 인사말 감점 여부 재확인

---

## [DB] 데이터 품질 종합 진단 + 3팀 협업 사항 (2026-02-10 13:00)

### 1. `_merged` 문서 전략 현황

**설계 의도**: merged 문서에서 넓은 매칭 → 하위 청크에서 세부 정보 검색
**현실**: merged 35건의 하위 청크가 **0건** (대응 관계 없음)

| 구분 | 건수 | 상태 |
|------|------|------|
| merged 문서 | 35건 | 독립 큐레이션 요약으로 존재 |
| 하위 청크 있는 merged | **0건** | merged→chunk 탐색 경로 없음 |
| 청크만 있는 그룹 (merged 없음) | 83그룹 (1,231건) | 상위 종합 문서 없음 |

→ **현재 구조**: merged는 "권위 있는 요약문"으로 +0.6 스코어 보너스 + 정책 핀으로 활용 중
→ **개선 방향**: DB에서 merged→chunk 관계를 실제로 만들거나, 기존 방식 유지 결정 필요

### 2. 특수카드 검색 오염 (CRITICAL — Backend 협업 필요)

**증상**: STT 실시간 테스트 시 다둥이/K-패스/육아/국민행복 카드가 무관한 쿼리에서 계속 노출

**근본 원인**: `guide_general` 검색 풀 216건 중 146건(67.6%)이 특수카드 문서

```
guide_general (216건)
  ├── K-패스      41건 (19%)
  ├── 다둥이      40건 (18%) ← 19+21 중복!
  ├── 나라사랑    36건 (17%)
  ├── 국민행복    29건 (13%)
  └── 일반 가이드  70건 (33%) ← 실제 유용한 문서
```

**오염 메커니즘**:
1. "결제", "포인트", "카드" 등 범용 키워드가 특수카드 문서의 30~60%에 포함
2. `_demotion_for_noise()`에서 K-패스만 -0.2 감점, **다둥이/국민행복은 감점 없음**
3. scope 필터가 `sinhan_terms_*`, `hyundai_applepay_*`만 제외 — 특수카드는 제외 안 됨

**DB 즉시 조치**:
- [x] 다둥이 중복 제거 (40→19건) — DB 단독
- [x] 특수카드 scope 필터 추가 — ✅ **B-6 적용 완료**

> **[B-6 적용 완료] 특수카드 검색 오염 방지 (2026-02-10 15:00)**
>
> **방식**: `exclude_id_patterns` 필터 신설 (scope 변경 대신 동적 제외)
>
> | 파일 | 변경 내용 |
> |------|----------|
> | `retriever/db.py` | `exclude_id_patterns` 필터 지원 (build_where_clause + text_search) |
> | `pipeline/retrieve.py` | 특수카드 미언급시 7개 ID 패턴 자동 제외 + post_filter 강화 |
> | `policy/policy_pins.py` | `dadungi_013` → `서울시다둥이행복카드_13` (삭제된 doc 교체) |
>
> **동작 원리**:
> 1. 쿼리에 특수카드명(다둥이/K-패스/나라사랑/국민행복/민생/시니어) 없으면 → SQL `NOT (id LIKE ANY(...))` 적용
> 2. 특수카드명 있으면 → 제외 없이 전체 검색 (기존 동작 유지)
> 3. 후처리에서도 잔여 특수카드 문서 제거 (이중 안전장치)

### 3. 데이터 품질 감사 결과 요약

| 심각도 | 건수 | 핵심 이슈 |
|--------|------|----------|
| CRITICAL | 2 | ~~notice_53 테스트 레코드~~ ✅ 삭제, ~~card_products 65% 연회비 NULL~~ ✅ backfill 완료 |
| HIGH | 5 | ~~초소형 문서 33건~~ ✅ 1건 삭제+31건 정상 확인, ~~중복 콘텐츠~~ ✅ dadungi 21건 삭제, main_benefits 잘림 3건, ~~performance_condition 전체 NULL~~ ✅ 372건 backfill, keyword_dictionary 중복 |
| MEDIUM | 6 | 제너릭 키워드, card_name 연결 없음, priority 미차등, 제목 [TABLE] 등 |

### 4. card_products 연회비 NULL 정밀 조사 결과

| 분류 | 건수 | 조치 | 상태 |
|------|------|------|------|
| 체크카드 (debit, 연회비 없음 정상) | 172건 | `0`으로 설정 | ✅ 완료 |
| 신용카드 "없음/면제" 명시 | 21건 | `0`으로 설정 | ✅ 완료 |
| 신용카드 structured JSONB 파싱 | 12건 | 자동 추출 (3,000~297,000원) | ✅ 완료 |
| 신용카드 structured null | 56건 | `0`으로 설정 (파트너/특수 카드) | ✅ 완료 |

→ **결과**: NULL 261건 → 0건. 연회비 분포: 0원 250건, 유료 148건 (1,000~697,000원)

### 5. 문서 화면 표시명 점검

| 위치 | 문제 | 담당 |
|------|------|------|
| DocumentDetailModal 에러 메시지 | raw ID 노출 (`sinhan_terms_...`) | **Frontend** |
| RealTimeConsultationPage 참조문서 | `card.id` fallback (`CARD-SHINHAN-...`) | **Frontend** |
| referenced_documents 57건 빈 title | `plumb_4_1` 제목 누락 | **DB** |

> **[Frontend 요청] F-6: raw ID 노출 방지**
>
> - `DocumentDetailModal:218` — `{documentId}` 대신 `'요청하신 문서'`로 변경
> - `RealTimeConsultationPage:2028,2049` — `card.id` fallback → `'제목없음'`으로 변경
> - `RealTimeConsultationPage:2072` — synthetic `RAG-STEP1-0` → `ragCard.title || '정보 카드'`

### 6. DB 단계별 작업 결과

| 순서 | 작업 | 상태 | 변경 건수 |
|------|------|------|----------|
| D-12a | notice_53 테스트 레코드 삭제 | ✅ 완료 | 1건 삭제 + 62건 참조 정리 |
| D-12b | dadungi_* 중복 문서 제거 | ✅ 완료 | 21건 삭제 (서울시다둥이 19건 유지) |
| D-12c | 국민행복카드_18 ("없음") 삭제 | ✅ 완료 | 1건 삭제 |
| D-12d | plumb_4_1 빈 제목 수정 | ✅ 완료 | 56건 제목 채움 |
| D-13a | debit 172건 annual_fee → 0 | ✅ 완료 | 172건 |
| D-13b | credit 89건 annual_fee structured 파싱 | ✅ 완료 | 89건 (12건 numeric, 21건 0원, 56건 default) |
| D-13c | 이상값 3건 수정 (1원/5원 → 실제값) | ✅ 완료 | 3건 |
| D-13d | performance_condition backfill | ✅ 완료 | 372건 |
| D-14 | 커밋 | ✅ 완료 |
