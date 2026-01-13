# ERD 스키마 업데이트 내용

## 작성일: 2026-01-13
## 목적: RAG 검색을 위한 ERD 스키마 업데이트

---

## 업데이트된 테이블

### 1. `service_guide_documents` 테이블

**추가된 컬럼**:
- `structured JSONB`: RAG 검색용 구조화 데이터

**변경 사항**:
- 기존 ERD에는 없었지만, RAG Kanban board 표시를 위해 추가
- `structured` 필드에 프론트엔드 표시용 구조화된 데이터 저장

---

### 2. `card_products` 테이블

**추가된 컬럼**:
- `metadata JSONB`: 추가 메타데이터 (original_source, full_content 등)
- `structured JSONB`: RAG 검색용 구조화 데이터

**변경 사항**:
- 기존 ERD에는 없었지만, RAG 검색 및 프론트엔드 표시를 위해 추가
- `full_content`는 `metadata` 필드에 저장 (ERD에 별도 컬럼 없음)

---

### 3. `notices` 테이블

**추가된 컬럼**:
- `keywords TEXT[]`: RAG 검색용 키워드 배열
- `embedding vector(1536)`: RAG 검색용 벡터 임베딩
- `metadata JSONB`: 추가 메타데이터

**추가된 인덱스**:
- `idx_notices_embedding_hnsw`: embedding 벡터 인덱스 (HNSW)

**변경 사항**:
- 기존 ERD에는 없었지만, RAG 검색을 위해 추가
- 공지사항도 RAG 검색 대상이 되도록 확장

---

### 4. `brand_type` ENUM

**추가된 값**:
- `'local'`: 국내전용 카드 브랜드

**변경 사항**:
- 기존 ERD에는 `visa`, `mastercard`, `amex`, `unionpay`만 있었음
- 테디카드 데이터에 국내전용 카드가 있어 추가

---

## 업데이트 이유

### RAG 검색 지원

1. **`service_guide_documents`**:
   - `structured`: 프론트엔드 Kanban board 표시용 구조화 데이터
   - LLM 재구성 시간 단축을 위해 사전 구조화

2. **`card_products`**:
   - `metadata`: 원본 출처, 전체 내용 등 메타데이터 저장
   - `structured`: 카드 정보 표시용 구조화 데이터

3. **`notices`**:
   - `keywords`: 키워드 기반 필터링
   - `embedding`: 벡터 유사도 검색
   - `metadata`: 원본 출처 등 메타데이터

### 프론트엔드 성능 최적화

- `structured` 필드를 통해 LLM이 매번 데이터를 재구성하는 시간 단축
- 사전 구조화된 데이터로 즉시 화면 표시 가능

---

## ERD 파일 업데이트

**파일**: `docs/04_dev/02_db/CALL_ACT_ERD_Diagram.sql`

**업데이트 내용**:
1. `brand_type` ENUM에 `'local'` 추가
2. `card_products` 테이블에 `metadata`, `structured` 컬럼 추가
3. `notices` 테이블에 `keywords`, `embedding`, `metadata` 컬럼 추가
4. `service_guide_documents` 테이블에 `structured` 컬럼 추가
5. `notices` 테이블에 `embedding` 인덱스 추가

---

## 기존 테이블 수정 방법

기존에 테이블이 이미 생성되어 있는 경우, 다음 스크립트를 실행하세요:

**파일**: `backend_dev/app/db/scripts/02_alter_tedicard_tables.sql`

**실행 방법**:
```sql
-- DBeaver에서 실행
-- 또는
psql -h localhost -U callact_admin -d callact_db -f backend_dev/app/db/scripts/02_alter_tedicard_tables.sql
```

이 스크립트는:
- 기존 테이블에 필요한 컬럼을 안전하게 추가
- 이미 존재하는 컬럼은 건너뜀
- 필요한 인덱스 생성

---

## 검증

### 테이블 구조 확인

```sql
-- service_guide_documents 구조 확인
\d service_guide_documents

-- card_products 구조 확인
\d card_products

-- notices 구조 확인
\d notices
```

### 컬럼 존재 확인

```sql
-- structured 컬럼 확인
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'service_guide_documents' 
AND column_name = 'structured';

-- notices embedding 컬럼 확인
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'notices' 
AND column_name = 'embedding';
```

---

## 참고 문서

- [ERD 스키마 설명](../01_data-preprocessing/ERD/CALL_ACT_ERD_Schema_설명.md)
- [DB 스키마 문서번호 정보 점검](./03_DB_스키마_문서번호_정보_점검.md)
