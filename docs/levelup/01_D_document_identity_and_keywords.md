# 01_D: 문서 정체성 확립 및 키워드 정비

> **담당**: DB/데이터
> **상태**: 컨펌 대기 → 착수 준비 완료
> **날짜**: 2026-02-10
> **관련**: 01_B (백엔드 API 수정), 01_F (프론트엔드 타입 수정)

---

## 프론트엔드 점검 결과 반영

프론트 분석(00_F_현상분석_문서시스템.md)에서 발견된 6가지 문제 중 DB가 해결해야 할 항목:

| 프론트 이슈 | DB 해결 범위 | 자체/협업 |
|------------|-------------|----------|
| A. 문서 ID 체계 단절 | DB ID 체계 정리, 매핑 테이블 제공 | **협업** (3팀 합의) |
| B. 필드 이름 불일치 | DB 컬럼은 snake_case 유지, API 변환은 Backend 담당 | Backend 담당 |
| C. DocumentType 추론 취약 | **DB에 document_type 확정값 저장** | **DB 자체** |
| D. FAQ 문서 연결 하드코딩 | **실 문서 ID로 매핑** | **DB 자체** + Backend API |
| E. fullText 부재 시 빈 모달 | structured/full_content 데이터 품질 보장 | **DB 자체** |
| F. localStorage 의존 | DB/Backend 세션 저장 전환 | Backend/Frontend |

---

## DB 자체적으로 즉시 착수 가능한 작업

### Step 1: 문서 타입(document_type) DB에 확정값 저장

**현재**: service_guide_documents.document_type = 'service_guide' (모두 동일)
**변경**: 실제 문서 성격에 따라 분류

**분류 기준**:

| 분류 | 조건 | 프론트 매핑 | 예상 건수 |
|------|------|-----------|----------|
| `terms` | id에 `_terms` 포함 OR content에 "제1조", "제2조" 패턴 | 📜 약관 전문 | ~200건 |
| `guide` | id에 `_merged` 포함 OR content에 절차/방법/안내 | 📖 이용 가이드 | ~800건 |
| `general` | 나머지 | 📌 상세 정보 | ~270건 |
| `product-spec` | card_products 테이블 전체 | 📄 상품 상세 정보 | 398건 |
| `notice` | notices 테이블 전체 | 시스템 공지 | 52건 |

**작업 방법**:
- 전처리 스크립트로 JSON 데이터 분류 → DB 재적재
- 기존 document_type 컬럼 값 UPDATE (스키마 변경 불필요)

**롤백**: 원본 JSON 백업 보존. `UPDATE SET document_type = 'service_guide'`로 원복

### Step 2: 카드 상품 195건 키워드 추출

**현재**: 398건 중 195건(49%)이 keywords = []
**방법**: structured + content에서 자동 추출

```
추출 소스 우선순위:
1. structured.key_terms → 그대로 사용
2. structured.mainBenefits → 핵심 명사 추출
3. main_benefits + full_content → 키워드 사전(1,157개) 매칭
4. 카드명에서 브랜드/타입 추출 (K-패스, 체크, 신용 등)
```

**규칙**: 최소 3개, 최대 10개
**롤백**: 원본 JSON 백업

### Step 3: FAQ related_document_id를 실 문서 ID로 매핑

**현재**: `card-1-1-1` (mock ID) → 실 문서와 연결 없음
**변경**: 각 FAQ 카테고리에 가장 적합한 service_guide_documents ID 매핑

**매핑 방법**:
1. FAQ keyword → service_guide_documents.keywords 매칭
2. FAQ content → 벡터 유사도 검색으로 최적 문서 선정
3. 상위 1건의 실 문서 ID를 related_document_id에 저장

| FAQ 카테고리 | 현재 ID | 매핑 대상 예시 |
|-------------|---------|--------------|
| 카드 분실 | card-1-1-1 | `카드분실_도난_관련피해_예방_및_대응방법_merged` |
| 해외 결제 | card-2-1-1 | 해외 결제 관련 가이드 ID |
| 청구서 확인 | billing-1-1-1 | 청구서 관련 가이드 ID |
| ... | ... | ... |

**롤백**: 매핑 전 FAQ 데이터 백업

### Step 4: fullText/structured 데이터 품질 보장

**현재 문제**: card_products 중 structured = null인 건 존재 → fullText가 null 반환
**확인 필요**:
- structured가 null인 카드 상품 수 파악
- full_content가 비어있는 문서 수 파악
- 빈 문서에 content 채우기 (전처리 재실행 또는 수동 보완)

---

## 3팀 협업이 필요한 사항 (합의 대기)

### 협의 1: 문서 ID 통일 방침

**현재 5가지 패턴** → 통일 or 매핑 테이블?

**옵션 A: ID 통일** (비용 높음)
- 모든 문서 ID를 `DOC-{TYPE}-{SEQ}` 형태로 통일
- 예: `DOC-CARD-001`, `DOC-GUIDE-001`, `DOC-NOTICE-001`
- 장점: 모든 시스템에서 일관
- 단점: 기존 데이터 마이그레이션 필요, 외부 참조 깨짐

**옵션 B: 현재 ID 유지 + sourceTable 명시** (비용 낮음, 권장)
- 문서 ID는 현재 그대로 유지
- API 응답에 `sourceTable` 필드 추가 → 어느 테이블의 문서인지 명확
- Frontend에서 문서 조회 시 `(sourceTable, documentId)` 조합으로 조회
- 장점: 마이그레이션 불필요, 하위 호환
- 단점: ID만으로 출처 파악 불가 (sourceTable 필수)

**DB 의견: 옵션 B 권장.** 기존 ID를 유지하면서 `sourceTable`로 출처를 명시하면 충분.

### 협의 2: referenced_documents JSONB 확장

**현재 포맷**:
```json
{"stepNumber": 1, "documentId": "...", "title": "...", "used": true, "viewCount": 2}
```

**확장 제안** (하위 호환):
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

**추가 필드**: `documentType`, `sourceTable`, `category`, `relevanceScore`

→ **Backend**: SaveConsultation API의 ReferencedDocument 모델에 optional 필드 추가
→ **Frontend**: ReferencedDocument 인터페이스에 optional 필드 추가
→ **DB**: JSONB라 스키마 변경 불필요 (자유 형식)

### 협의 3: Frequent Inquiries API - snake_case 혼용 수정

**현재**:
```json
{"relatedDocument": {"document_id": "...", "title": "..."}}
```
- 외부: camelCase (`relatedDocument`)
- 내부: snake_case (`document_id`) ← **불일치**

→ **Backend**: `document_id` → `documentId`로 통일 (또는 Pydantic alias 설정)

---

## 검증 기준

| 지표 | 현재 | 목표 | 측정 방법 |
|------|------|------|----------|
| 카드 상품 키워드 채움률 | 51% | **95%+** | ✅ **100%** 달성 (Step 2) |
| document_type DB 보유율 | 0% (의미있는 값) | **100%** | ✅ **100%** 달성 (Step 1) |
| FAQ 실 문서 연결률 | 0% | **100%** | ✅ **100%** 달성 (Step 3, 11건 매핑) |
| fullText null 비율 | 측정 필요 | **10% 이하** | ✅ **0%** (detailContent 100%, Step 4) |
| 회귀 테스트 통과율 | 기준선 측정 | 기준선 이상 | Phase C에서 검증 예정 |

---

## 작업 순서

```
[DB 자체] Step 1: document_type 분류 ✅ 완료
    ↓ terms(1092)/faq(107)/guide(74) 분포 확인
[DB 자체] Step 2: 키워드 추출 ✅ 완료
    ↓ 채움률 51% → 100% (398/398)
[DB 자체] Step 3: FAQ 실 문서 매핑 ✅ 완료
    ↓ mock ID 11건 → 실 service_guide_documents ID
[DB 자체] Step 4: fullText 데이터 품질 감사 ✅ 완료
    ↓ detailContent 100%, full_content 100% (null 없음)
--- DB Phase A 자체 작업 전체 완료 ---
[협업] 문서 ID 방침 합의 (옵션 B) → Frontend ✅ 동의, Backend 대기
[협업] referenced_documents 스키마 확장 → Frontend ✅ 동의, Backend 대기
[협업] FAQ API snake_case 수정 → Frontend ✅ 동의, Backend 대기
```

---

## 재적재 호환성 (CRITICAL)

**원칙**: 01a_setup_callact_db.py 재실행 시 모든 변경사항이 자동 반영되어야 한다.

| Step | 변경 대상 | 자동 반영? | 방법 |
|------|----------|-----------|------|
| Step 1 | document_type | **YES** | JSON 파일의 `document_type` 필드 수정 → `load_teddycard.py`가 자동 읽음 |
| Step 2 | keywords | **YES** | JSON 파일의 `keywords` 필드 수정 → `load_teddycard.py`가 자동 읽음 |
| Step 3 | FAQ document_id | **YES** (코드 수정 완료) | `load_frequent_inquiries.py`의 `CATEGORY_CONTENT_MAP` + `FALLBACK_INQUIRIES_DATA` + `DEFAULT_CONTENT_TEMPLATE` 직접 수정 → 재실행 시 자동 반영 |
| Step 4 | fullText 품질 | **YES** | JSON 파일의 `structured`/`full_content` 수정 → 자동 반영 |

모든 로더가 `ON CONFLICT (id) DO UPDATE` 사용 → 재실행 시 기존 행 업데이트, 신규 행 추가 (멱등성 보장).
단, JSON에서 삭제된 행은 DB에서 자동 삭제되지 않음 (UPDATE only, no DELETE).

---

## 롤백 계획

| 단계 | 변경 대상 | 롤백 방법 |
|------|----------|----------|
| Step 1 | service_guide_documents.document_type | 원본 JSON 백업 → DB 재적재 |
| Step 2 | card_products.keywords | 원본 JSON 백업 → DB 재적재 |
| Step 3 | frequent_inquiries.related_document_id | 매핑 전 데이터 백업 → 복원 |
| Step 4 | structured/full_content 보완 | 원본 JSON 백업 보존 |

모든 원본 파일은 작업 전 `.back/` 디렉토리에 타임스탬프와 함께 백업.

---

## 파일 위치

```
변경 대상 (data-preprocessing_dev → backend_dev/app/db/data/ 동기화):
  teddycard_card_products_with_embeddings.json     (Step 2: 키워드 추가)
  teddycard_service_guides_with_embeddings.json    (Step 1: document_type 분류)
  keywords_dict_v2_with_patterns.json              (Step 2 연계: 사전 동기화)

Backend DB 스크립트:
  backend_dev/app/db/scripts/modules/load_teddycard.py          (적재 시 document_type 반영)
  backend_dev/app/db/scripts/modules/load_frequent_inquiries.py (Step 3: 실 문서 매핑)

신규 스크립트 (data-preprocessing_dev/preprocess/teddycard/):
  20_classify_document_types.py   (Step 1)
  21_extract_card_keywords.py     (Step 2)
  22_map_faq_documents.py         (Step 3)
  23_audit_fulltext_quality.py    (Step 4)
```

---

**Phase A 전체 완료 (2026-02-10)**. Phase B 합의 + Phase C 연동 작업 대기 중.
