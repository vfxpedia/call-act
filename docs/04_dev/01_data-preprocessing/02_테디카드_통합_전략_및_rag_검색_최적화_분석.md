---
name: 테디카드 통합 전략 및 RAG 검색 최적화 분석
overview: 테디카드 서비스 특성을 반영하여 여러 카드사 데이터를 "테디카드" 브랜드로 통합하고, RAG 검색 정확도를 최대화하기 위한 데이터 매핑 전략을 분석합니다.
todos:
  - id: analyze_text_replacement
    content: 텍스트 치환 규칙 정의 (신한카드→테디카드 등)
    status: completed
  - id: design_preprocessing_scripts
    content: 전처리 스크립트 설계 (data-preprocessing_dev)
    status: in_progress
    dependencies:
      - analyze_text_replacement
  - id: test_text_replacement
    content: 텍스트 치환 테스트 및 검증
    status: pending
    dependencies:
      - design_preprocessing_scripts
  - id: generate_embeddings_tedicard
    content: 치환된 텍스트 기반 임베딩 생성
    status: pending
    dependencies:
      - test_text_replacement
  - id: design_db_loading_scripts
    content: DB 적재 스크립트 설계 (backend_dev)
    status: pending
    dependencies:
      - generate_embeddings_tedicard
  - id: test_rag_search
    content: RAG 검색 테스트 및 품질 검증
    status: pending
    dependencies:
      - design_db_loading_scripts
---

# 테디카드 통합 전략 및 RAG 검색 최적화 분석

## 1. 핵심 요구사항

### 1.1 테디카드 서비스 특성

- **서비스 이름**: "테디카드" (TeddyCard)
- **카드 정보 통합 전략**:
  - 신한카드, 현대카드, 삼성카드 → 모두 "테디카드"로 통합하여 DB 적재
  - 스페셜 카드(애플페이, K패스 등): 고유 이름 유지 (예: "애플페이", "K패스카드")
- **약관/서비스 가이드/공지사항**: 테디카드 정보로 통합

### 1.2 RAG 검색 목표

- **핵심 목표**: 테디카드 상담사를 위한 상담 도우미 서비스 - 고객 문의에 대한 정확한 정보 전달
- **고객 쿼리 특성**:
  - 고객 쿼리는 "테디카드 연회비" 등 "테디카드" 브랜드로 올 것 (가정)
  - "신한카드 연회비" 같은 원본 카드사 이름 쿼리는 없음
- **고객 시나리오**:
  - 고객이 "테디카드 연회비" 문의 → "테디카드" 정보 제공
  - 고객이 "테디카드 Apple Pay 이용처" 문의 → "테디카드" 정보 제공 (Apple Pay는 제휴 서비스명 유지)
  - 고객이 "애플페이" 관련 문의 → "애플페이" 정보 제공 (스페셜 카드)

## 2. 데이터 매핑 전략 옵션 재분석

### 옵션 A: source_type 컬럼 사용 (카드사 구분 유지)

**구조 예시**:

```sql
-- service_guide_documents 테이블
CREATE TABLE service_guide_documents (
  id VARCHAR(50) PRIMARY KEY,
  source_type VARCHAR(50),  -- 'hyundai', 'samsung', 'shinhan', 'special_card'
  document_type VARCHAR(50),
  category VARCHAR(100),
  title VARCHAR(300),
  content TEXT,
  keywords TEXT[],
  embedding VECTOR(1536),
  metadata JSONB,  -- 원본 카드사 정보 포함
  ...
);

-- card_products 테이블
CREATE TABLE card_products (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(200),
  issuer VARCHAR(50),  -- 'teddycard' 또는 'applepay', 'kpass'
  original_source VARCHAR(50),  -- 'shinhan', 'hyundai', 'samsung'
  ...
);
```

**적재 예시**:

- shinhan/card_info/*.md → card_products (issuer='teddycard', original_source='shinhan')
- hyundai/applepay.json → service_guide_documents (source_type='hyundai')
- samsung/creditcard_guide.json → service_guide_documents (source_type='samsung')

**RAG 검색 전략**:

1. 고객 쿼리: "신한카드 연회비"
2. 임베딩 검색: 모든 source_type에서 검색
3. 결과 후처리: 원본 카드사 정보를 metadata에서 확인하여 "테디카드"로 치환

**장점**:

- 원본 데이터 출처 추적 가능
- 데이터 소스별 업데이트 용이
- 디버깅 및 품질 관리 용이

**단점**:

- RAG 검색 결과에서 원본 카드사 이름 노출 가능 ("신한카드" → "테디카드" 치환 필요)
- 검색 시 source_type 필터링 복잡
- 고객에게 일관된 "테디카드" 브랜드 경험 제공 어려움

**RAG 검색 정확도 영향**:

- ❌ 부정적: 임베딩에 원본 카드사 이름 포함 → 검색 시 혼란 가능
- ❌ 부정적: 결과 후처리 복잡 → 오류 가능성

### 옵션 B: 통합 구조 (카드사 정보 제거/통합)

**구조 예시**:

```sql
-- service_guide_documents 테이블 (source_type 제거)
CREATE TABLE service_guide_documents (
  id VARCHAR(50) PRIMARY KEY,
  document_type VARCHAR(50),
  category VARCHAR(100),
  title VARCHAR(300),  -- "테디카드"로 치환된 제목
  content TEXT,  -- "테디카드"로 치환된 내용
  keywords TEXT[],
  embedding VECTOR(1536),  -- "테디카드" 기반 임베딩
  metadata JSONB,  -- 원본 정보는 내부 참조용으로만 저장
  ...
);

-- card_products 테이블
CREATE TABLE card_products (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(200),  -- "테디카드 [카드명]" 형식
  issuer VARCHAR(50),  -- 'teddycard' 또는 'applepay', 'kpass'
  ...
);
```

**전처리 단계**:

1. JSON/MD 파일 읽기
2. 텍스트 내 "신한카드", "현대카드", "삼성카드" → "테디카드"로 치환
3. 임베딩 생성 (치환된 텍스트 기반)
4. DB 적재 (issuer='teddycard')

**적재 예시**:

- shinhan/card_info/*.md → 전처리 → card_products (issuer='teddycard')
- hyundai/applepay.json → 전처리 → service_guide_documents
- samsung/creditcard_guide.json → 전처리 → service_guide_documents

**RAG 검색 전략**:

1. 고객 쿼리: "테디카드 연회비" (테디카드 브랜드로 쿼리)
2. 임베딩 검색: 통합된 데이터에서 검색 (임베딩에 "테디카드" 포함)
3. 결과: "테디카드" 정보 반환

**장점**:

- 고객에게 일관된 "테디카드" 브랜드 경험
- RAG 검색 결과 일관성 보장
- 검색 단순화 (필터링 최소화)

**단점**:

- 원본 데이터 손실 (치환 과정)
- 디버깅 시 원본 정보 확인 어려움
- 카드사별 데이터 업데이트 시 전체 재처리 필요

**RAG 검색 정확도 영향**:

- ✅ 긍정적: 임베딩에 "테디카드" 이름 포함 → 검색 일관성
- ✅ 긍정적: 고객 쿼리 "신한카드"와 "테디카드" 모두 동일 결과 반환 가능 (임베딩 유사도)
- ⚠️ 주의: 전처리 시 치환 누락 가능성

### 옵션 C: 하이브리드 (카드 정보는 통합, 서비스 가이드는 source_type 유지)

**구조 예시**:

```sql
-- card_products 테이블 (통합)
CREATE TABLE card_products (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(200),  -- "테디카드 [카드명]"
  issuer VARCHAR(50),  -- 'teddycard'
  ...
);

-- service_guide_documents 테이블 (source_type 유지)
CREATE TABLE service_guide_documents (
  id VARCHAR(50) PRIMARY KEY,
  source_type VARCHAR(50),  -- 'hyundai', 'samsung', 'shinhan', 'special_card'
  document_type VARCHAR(50),
  category VARCHAR(100),
  title VARCHAR(300),  -- 원본 유지 또는 "테디카드"로 치환
  content TEXT,  -- 원본 유지 또는 "테디카드"로 치환
  keywords TEXT[],
  embedding VECTOR(1536),
  metadata JSONB,
  ...
);
```

**적재 예시**:

- card_products: 모든 카드 정보 → issuer='teddycard'로 통합
- service_guide_documents: source_type으로 구분 (치환 여부 선택)

**RAG 검색 전략**:

- 카드 정보 검색: 통합된 card_products에서 검색
- 서비스 가이드 검색: source_type 필터링 또는 전체 검색

**장점**:

- 카드 정보는 일관성 유지
- 서비스 가이드는 유연성 유지

**단점**:

- 일관성 부족 (두 가지 방식 혼재)
- 서비스 가이드 검색 시 source_type 처리 복잡

**RAG 검색 정확도 영향**:

- ⚠️ 중간: 카드 정보는 일관성, 서비스 가이드는 불일치 가능

## 3. 테디카드 서비스 특성 기반 권장 방안

### 권장 방안: **옵션 B (통합 구조)** - RAG 검색 정확도 우선

### 3.1 권장 근거

1. **서비스 정체성 일관성**:

   - 테디카드는 통합 카드 서비스
   - 고객에게 "테디카드" 브랜드로 일관된 경험 제공 필요
   - 원본 카드사 이름 노출 시 브랜드 정체성 혼란

2. **RAG 검색 정확도 최대화**:

   - 임베딩에 "테디카드" 이름 포함 → 검색 일관성
   - 고객 쿼리 "신한카드 연회비"와 "테디카드 연회비" 모두 동일 결과
   - 후처리 없이 직접적인 검색 결과 반환

3. **ERD 설계 원칙 준수**:

   - 3개 논리적 DB 구조 유지
   - 도메인 주도 설계 원칙 준수
   - 카드사 구분은 메타데이터 수준 (도메인 아님)

### 3.2 구체적 구현 전략

#### 단계 1: 전처리 단계 (data-preprocessing_dev)

**카드 정보 데이터 (shinhan/card_info/*.md)**:

1. MD 파일 읽기
2. 텍스트 내 카드사 이름 치환 (데이터 소스별 화이트리스트 방식):

   - shinhan 데이터: "신한" 관련 모든 표현 → "테디"로 치환
     - "신한카드" → "테디카드"
     - "신한은행" → "테디은행"
     - "신한 SOL페이" → "테디 SOL페이"
     - "신한" → "테디"
     - "shinhan" → "teddy"
   - 카드 이름 변환: "신한카드 Deep Dream" → "테디카드 Deep Dream"

3. JSON 변환 (card_products 형식)
4. 임베딩 생성 (치환된 텍스트 기반)

**서비스 가이드 데이터 (hyundai, samsung, shinhan, special_card)**:

1. JSON/MD 파일 읽기
2. 텍스트 내 카드사 이름 치환 (데이터 소스별 화이트리스트 방식):

   - hyundai 데이터: "현대" 관련 모든 표현 → "테디"로 치환
     - "현대카드" → "테디카드"
     - "현대은행" → "테디은행"
     - "현대" → "테디"
     - "hyundai" → "teddy"
   - samsung 데이터: "삼성" 관련 모든 표현 → "테디"로 치환
     - "삼성카드" → "테디카드"
     - "삼성" → "테디"
     - "samsung" → "teddy"
   - shinhan 데이터: "신한" 관련 모든 표현 → "테디"로 치환 (위와 동일)
   - special_card 데이터: **치환하지 않음** (제휴 카드 정보 보존)
     - "KB국민은행", "KB국민카드" 등 제휴 파트너 정보는 원본 유지

3. JSON 변환 (service_guide_documents 형식)
4. 임베딩 생성 (치환된 텍스트 기반)

**공지사항 데이터 (samsung/notice.json)**:

1. JSON 파일 읽기
2. 텍스트 내 카드사 이름 치환
3. notices 테이블 형식으로 변환

#### 단계 2: DB 적재 단계 (backend_dev)

**card_products 테이블**:

```sql
INSERT INTO card_products (id, name, issuer, ...)
VALUES 
  ('CARD-001', '테디카드 Deep Dream', 'teddycard', ...),
  ('CARD-002', '테디카드 The Classic', 'teddycard', ...),
  ('CARD-SPECIAL-001', '애플페이', 'applepay', ...);  -- 스페셜 카드
```

**service_guide_documents 테이블**:

```sql
-- source_type 제거 또는 'teddycard'로 통일
INSERT INTO service_guide_documents (id, document_type, category, title, content, embedding, ...)
VALUES 
  ('DOC-GUIDE-001', 'usage_guide', '이용처 안내', '테디카드 Apple Pay 이용처', '...', ...),
  ('DOC-GUIDE-002', 'usage_guide', '이용처 안내', '테디카드 신용카드 이용 가이드', '...', ...);
```

#### 단계 3: RAG 검색 최적화

**검색 쿼리 예시**:

```sql
-- 고객 쿼리: "테디카드 연회비는 얼마인가요?"
-- 임베딩 검색
SELECT id, title, content, 
       1 - (embedding <=> $query_embedding) as similarity
FROM service_guide_documents
WHERE category = 'fee_inquiry'
ORDER BY embedding <=> $query_embedding
LIMIT 5;

-- 결과: "테디카드 연회비 안내" 문서 반환
-- 고객에게: "테디카드 연회비는 ..." 형태로 응답
```

**고객 쿼리 처리**:

- 고객: "테디카드 연회비"
- 임베딩 검색: "테디카드 연회비" 문서와 높은 유사도 (임베딩에 "테디카드" 포함)
- 결과: "테디카드 연회비" 정보 제공

### 3.3 스페셜 카드 처리 전략

**스페셜 카드 예시**:

- 애플페이 (Apple Pay)
- K패스카드
- 기타 제휴 카드

**처리 방식**:

1. **카드 이름**: 고유 이름 유지 (예: "애플페이", "K패스카드")
2. **issuer 컬럼**: 'applepay', 'kpass' 등으로 구분
3. **임베딩**: 고유 이름 포함하여 임베딩 생성
4. **검색**: 고객이 "애플페이" 검색 시 → "애플페이" 문서 반환

**예시**:

```sql
-- card_products
INSERT INTO card_products (id, name, issuer, ...)
VALUES 
  ('CARD-APPLEPAY-001', '애플페이', 'applepay', ...),
  ('CARD-KPASS-001', 'K패스카드', 'kpass', ...);
```

### 3.4 원본 데이터 추적 (디버깅/품질 관리)

**metadata JSONB 활용**:

```json
{
  "original_source": "shinhan",
  "original_card_name": "신한카드 Deep Dream",
  "preprocessing_date": "2026-01-11",
  "preprocessing_version": "1.0"
}
```

**장점**:

- 디버깅 시 원본 정보 확인 가능
- 품질 관리 및 검증 용이
- 향후 데이터 업데이트 시 참조

## 4. 데이터 매핑 상세 전략

### 4.1 카드 정보 DB 매핑

| 데이터 소스 | 원본 형식 | 적재 테이블 | issuer | 변환 규칙 |

|------------|----------|-----------|--------|----------|

| shinhan/card_info/*.md | MD 파일 | card_products | 'teddycard' | "신한" 관련 모든 표현 → "테디"로 치환 ("신한카드", "신한은행", "신한 SOL페이" 등) |

| special_card (애플페이 등) | JSON | card_products | 'applepay' | 고유 이름 유지 (치환하지 않음) |

### 4.2 카드사 이용 안내 DB 매핑

| 데이터 소스 | 원본 형식 | 적재 테이블 | 변환 규칙 |

|------------|----------|-----------|----------|

| hyundai/applepay.json | JSON | service_guide_documents | "현대" 관련 모든 표현 → "테디"로 치환 ("현대카드", "현대은행" 등) |

| hyundai/hyundai_giftcard.json | JSON | service_guide_documents | "현대" 관련 모든 표현 → "테디"로 치환 |

| samsung/creditcard_guide.json | JSON | service_guide_documents | "삼성" 관련 모든 표현 → "테디"로 치환 ("삼성카드" 등) |

| samsung/notice.json | JSON | notices | "삼성" 관련 모든 표현 → "테디"로 치환 |

| shinhan/terms/*.json | JSON | service_guide_documents | "신한" 관련 모든 표현 → "테디"로 치환 ("신한카드", "신한은행" 등) |

| special_card/*.json | JSON | service_guide_documents | 치환하지 않음 (제휴 카드 정보 보존, 예: "KB국민은행", "KB국민카드") |

### 4.3 상담 사례 DB 매핑

- hana 데이터: 이미 적재 완료 (consultations, consultation_documents)
- hyundai, samsung, shinhan 상담 데이터: 현재 없음 (향후 필요 시 동일 방식)

## 5. 스키마 변경 사항

### 5.1 service_guide_documents 테이블

**옵션 1: source_type 제거 (완전 통합)**:

```sql
-- 기존 스키마 유지 (source_type 컬럼 없음)
-- 모든 데이터를 'teddycard'로 통합
```

**옵션 2: source_type을 'teddycard'로 통일**:

```sql
ALTER TABLE service_guide_documents 
ADD COLUMN IF NOT EXISTS source_type VARCHAR(50) DEFAULT 'teddycard';

-- 모든 레코드에 source_type='teddycard' 설정
-- 스페셜 카드는 source_type='special' 또는 issuer로 구분
```

**권장: 옵션 1** (source_type 제거)

- 통합 브랜드 정체성 일관성
- 검색 단순화

### 5.2 card_products 테이블

**issuer 컬럼 추가/확인**:

```sql
-- issuer 컬럼 확인
-- 'teddycard': 일반 카드 (통합)
-- 'applepay', 'kpass' 등: 스페셜 카드
```

### 5.3 metadata JSONB 활용

**모든 테이블에 metadata 컬럼 활용**:

```sql
-- 원본 정보 저장
metadata JSONB DEFAULT '{}'::jsonb

-- 예시
{
  "original_source": "shinhan",
  "original_title": "신한카드 Deep Dream",
  "preprocessing_version": "1.0"
}
```

## 6. 전처리 스크립트 설계

### 6.1 작업 흐름

```
data-preprocessing_dev/
├── preprocessing/
│   ├── tedicard/
│   │   ├── 01_convert_shinhan_cards.py    # shinhan/card_info/*.md → card_products JSON
│   │   ├── 02_convert_hyundai_guides.py   # hyundai/*.json → service_guide_documents JSON
│   │   ├── 03_convert_samsung_guides.py   # samsung/*.json → service_guide_documents JSON
│   │   ├── 04_convert_shinhan_terms.py    # shinhan/terms/*.json → service_guide_documents JSON
│   │   ├── 05_convert_special_cards.py    # special_card/*.json → card_products/service_guide_documents JSON
│   │   └── 06_generate_embeddings.py      # 임베딩 생성
│   └── output/
│       ├── tedicard_card_products.json
│       ├── tedicard_service_guides.json
│       └── tedicard_notices.json
```

### 6.2 전처리 로직 (예시)

**텍스트 치환 함수 (데이터 소스별 화이트리스트 방식)**:

```python
def replace_card_brand(text: str, source: str) -> str:
    """카드사 이름을 테디카드로 치환 (데이터 소스별 화이트리스트)"""
    
    # shinhan 데이터: 신한 관련 모든 표현 치환
    if source == 'shinhan':
        replacements = [
            ('신한카드사', '테디카드사'),      # 긴 패턴부터 먼저
            ('신한 카드', '테디 카드'),
            ('신한카드', '테디카드'),
            ('신한은행', '테디은행'),
            ('신한 SOL페이', '테디 SOL페이'),
            ('신한 SOL', '테디 SOL'),
            ('신한', '테디'),                  # 마지막에 적용
            ('shinhan', 'teddy'),             # 영문도 치환
            ('Shinhan', 'Teddy'),
        ]
        # 긴 패턴부터 먼저 치환 (중복 치환 방지)
        for old, new in sorted(replacements, key=lambda x: len(x[0]), reverse=True):
            text = text.replace(old, new)
    
    # hyundai 데이터: 현대 관련 모든 표현 치환
    elif source == 'hyundai':
        replacements = [
            ('현대카드사', '테디카드사'),
            ('현대 카드', '테디 카드'),
            ('현대카드', '테디카드'),
            ('현대은행', '테디은행'),
            ('현대', '테디'),
            ('hyundai', 'teddy'),
            ('Hyundai', 'Teddy'),
        ]
        for old, new in sorted(replacements, key=lambda x: len(x[0]), reverse=True):
            text = text.replace(old, new)
    
    # samsung 데이터: 삼성 관련 모든 표현 치환
    elif source == 'samsung':
        replacements = [
            ('삼성카드사', '테디카드사'),
            ('삼성 카드', '테디 카드'),
            ('삼성카드', '테디카드'),
            ('삼성', '테디'),
            ('samsung', 'teddy'),
            ('Samsung', 'Teddy'),
        ]
        for old, new in sorted(replacements, key=lambda x: len(x[0]), reverse=True):
            text = text.replace(old, new)
    
    # special_card 데이터: 치환하지 않음 (제휴 카드 정보 보존)
    # hyundai, samsung, shinhan 이외 데이터 소스: 치환하지 않음
    
    return text
```

**치환 규칙 설명**:

1. **데이터 소스별 화이트리스트 방식**:

   - 각 데이터 소스(`shinhan`, `hyundai`, `samsung`)에서만 해당 카드사 관련 표현 치환
   - `special_card` 데이터는 치환하지 않음 (제휴 카드 정보 보존)

2. **치환 범위**:

   - **shinhan**: "신한카드", "신한은행", "신한 SOL페이", "신한" → 모두 "테디" 계열로 치환
   - **hyundai**: "현대카드", "현대은행", "현대" → 모두 "테디" 계열로 치환
   - **samsung**: "삼성카드", "삼성" → 모두 "테디" 계열로 치환

3. **제휴 파트너 정보 보존**:

   - `special_card` 데이터의 "KB국민은행", "KB국민카드" 등은 치환하지 않음
   - 제휴 정보의 정확성 유지

4. **치환 순서**:

   - 긴 패턴부터 먼저 치환 (예: "신한카드사" → "테디카드사" 후 "신한카드" → "테디카드")
   - 중복 치환 방지

**테스트 예시**:

```python
# shinhan 데이터
text = "신한은행 최초고시 전신환 매도율을 적용한 후, 신한카드사가 부과하는..."
result = replace_card_brand(text, 'shinhan')
# → "테디은행 최초고시 전신환 매도율을 적용한 후, 테디카드사가 부과하는..."

# special_card 데이터 (치환하지 않음)
text = "KB국민은행 최초고시 전신환 매도율..."
result = replace_card_brand(text, 'special_card')
# → "KB국민은행 최초고시 전신환 매도율..." (변경 없음)
```

## 7. RAG 검색 품질 보장 전략

### 7.1 임베딩 품질

**치환 전 텍스트 vs 치환 후 텍스트**:

- 치환 후 텍스트로 임베딩 생성 → "테디카드" 기반 임베딩
- 고객 쿼리 "테디카드 연회비"와 데이터 내 "테디카드 연회비" 일치

### 7.2 검색 쿼리 최적화

**고객 쿼리 처리**:

- 입력: "테디카드 연회비" (테디카드 브랜드로 쿼리)
- 임베딩 생성: "테디카드 연회비" → 임베딩 벡터
- 검색: "테디카드 연회비" 문서와 높은 유사도 (임베딩에 "테디카드" 포함)
- 결과: "테디카드 연회비" 정보 반환

**최적화 방법**:

- 고객 쿼리와 데이터 모두 "테디카드" 브랜드로 통일되어 있으므로 추가 전처리 불필요
- 임베딩 검색으로 직접 매칭

### 7.3 검색 결과 후처리

**결과 반환 시**:

- 응답 텍스트: "테디카드" 브랜드로 일관되게 반환
- 원본 카드사 이름 노출 방지

## 8. 다음 단계

1. 전처리 스크립트 개발 (data-preprocessing_dev)
2. 텍스트 치환 규칙 정의 및 테스트
3. 임베딩 생성 (치환된 텍스트 기반)
4. DB 적재 스크립트 개발 (backend_dev)
5. RAG 검색 테스트 및 품질 검증