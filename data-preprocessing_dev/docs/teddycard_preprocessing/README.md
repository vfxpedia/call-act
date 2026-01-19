# 테디카드 전처리 문서

## 작성일: 2026-01-11
## 목적: 테디카드 데이터 전처리 과정 및 실행 가이드

---

## 개요

이 문서는 테디카드 데이터 전처리 작업의 전체 과정을 설명합니다.

**주요 작업 내용**:
1. 신한/현대/삼성/스페셜 카드 데이터 변환
2. 데이터 보강 (DB 적재를 위한 필드 추가)
3. 키워드 추출
4. 임베딩 생성

**최종 출력**: `data-preprocessing_dev/data/teddycard/` 폴더의 JSON 파일 (임베딩 포함)

---

## 빠른 시작

### 1. 환경 설정

```bash
# Conda 환경 활성화
conda activate final_env

# 작업 디렉토리로 이동
cd data-preprocessing_dev/preprocess/teddycard
```

**필수 환경 변수** (프로젝트 루트의 `.env` 파일):
```env
OPENAI_API_KEY=sk-your-api-key-here
```

### 2. 실행 순서

**Step 1: 데이터 변환** (각 데이터 소스별 변환)
```bash
python 01_convert_shinhan_cards.py      # 신한 카드 정보
python 02_convert_hyundai_guides.py     # 현대 카드 가이드
python 03_convert_samsung_guides.py     # 삼성 카드 가이드 및 공지
python 04_convert_shinhan_terms.py      # 신한 약관
python 05_convert_special_cards.py      # 스페셜 카드 (K-Pass, Apple Pay 등)
```

**Step 2: 데이터 보강** (DB 적재를 위한 필드 추가)
```bash
python 07_enrich_for_db.py
```

**Step 3: 키워드 추출**
```bash
python 08_extract_keywords.py
# 또는 LLM 보완 사용
python 08_extract_keywords.py --use-llm
```

**Step 4: 임베딩 생성** (시간 소요: 약 10-30분)
```bash
python 06_generate_embeddings.py
```

---

## 스크립트 설명

### 데이터 변환 스크립트 (01~05)

- **입력**: `data-preprocessing_dev/data/` 하위의 원본 데이터
- **출력**: `data-preprocessing_dev/data/teddycard/teddycard_*.json`
- **주요 작업**:
  - 텍스트 치환 (신한 → 테디)
  - JSON 구조 변환
  - merge 로직 적용 (삼성/현대)

### 데이터 보강 스크립트 (07)

- **입력**: `teddycard_*.json` 파일
- **출력**: `teddycard_*_enriched.json` 파일
- **주요 작업**:
  - 공지사항 날짜 계산 (start_date, end_date)
  - 카드 상품 연회비 파싱
  - 브랜드 추출
  - 카테고리/우선순위 결정 (LLM 또는 규칙 기반)

### 키워드 추출 스크립트 (08)

- **입력**: `teddycard_*_enriched.json` 파일
- **출력**: 키워드 필드 추가 (같은 파일 업데이트)
- **주요 작업**:
  - 단어사전 기반 키워드 매칭
  - LLM 보완 (옵션)

### 임베딩 생성 스크립트 (06)

- **입력**: `teddycard_*_enriched.json` 파일
- **출력**: `teddycard_*_with_embeddings.json` 파일
- **모델**: OpenAI `text-embedding-3-small` (1536차원)
- **특징**:
  - 체크포인트 지원 (중단 후 재개 가능)
  - 배치 처리
  - 에러 로깅

---

## 출력 파일 구조

### 중간 파일

```
data-preprocessing_dev/data/teddycard/
├── teddycard_card_products.json
├── teddycard_card_products_enriched.json
├── teddycard_service_guides_hyundai.json
├── teddycard_service_guides_samsung.json
├── teddycard_service_guides_shinhan.json
├── teddycard_service_guides_special.json
├── teddycard_service_guides_enriched.json
├── teddycard_notices.json
└── teddycard_notices_enriched.json
```

### 최종 파일 (임베딩 포함)

```
data-preprocessing_dev/data/teddycard/
├── teddycard_service_guides_with_embeddings.json
├── teddycard_card_products_with_embeddings.json
└── teddycard_notices_with_embeddings.json
```

### 최종 적재용 파일

```
data-preprocessing_dev/data/teddycard/
├── teddycard_service_guides_with_embeddings.json
├── teddycard_card_products_with_embeddings.json
└── teddycard_notices_with_embeddings.json
```

---

## 주요 특징

### 1. 텍스트 치환

**치환 규칙**:
- "신한카드" → "테디카드"
- "신한은행" → "테디은행"
- "SHINHAN" → "TEDDY"
- 기타 카드사 이름도 테디카드로 통합

**예외**: 스페셜 카드(Apple Pay, K-Pass 등)는 원본 이름 유지

### 2. merge 로직

**적용 대상**:
- ✅ 삼성 가이드: `original_category2` 기준으로 merge
- ✅ 현대 가이드: `original_category2` 기준으로 merge
- ❌ 신한 약관: merge 미적용 (조 단위 독립성 유지)
- ❌ 스페셜 카드: merge 미적용

**효과**: 관련 문서를 하나로 묶어 RAG 검색 시 더 풍부한 컨텍스트 제공

### 3. 문서 번호 정보

**약관 조 번호**:
- `title` 필드에 포함 (예: "제1조(목적)")
- 프론트엔드에서 문서 번호 표시 가능

**문서 식별자**:
- `id` 필드: 고유 식별자
- `metadata.original_source`: 원본 출처 정보

### 4. 키워드 추출

**방법**:
- 단어사전 기반 매칭 (`keywords_dict.json`)
- LLM 보완 옵션 (`--use-llm`)
- STT 키워드 추출 정밀도 향상

**용도**:
- RAG 검색 필터링
- STT 키워드 매칭

---

## 파일 구조

### 스크립트 위치

```
data-preprocessing_dev/preprocess/teddycard/
├── 00_analyze_document_lengths.py    # 문서 길이 분석
├── 01_convert_shinhan_cards.py       # 신한 카드 변환
├── 02_convert_hyundai_guides.py      # 현대 가이드 변환
├── 03_convert_samsung_guides.py      # 삼성 가이드/공지 변환
├── 04_convert_shinhan_terms.py       # 신한 약관 변환
├── 05_convert_special_cards.py       # 스페셜 카드 변환
├── 06_generate_embeddings.py         # 임베딩 생성
├── 07_enrich_for_db.py               # 데이터 보강
├── 08_extract_keywords.py            # 키워드 추출
├── 09_check_merge_candidates.py      # merge 후보 분석
├── text_replacement.py               # 텍스트 치환 유틸리티
├── merge_utils.py                    # merge 로직 유틸리티
└── keywords_dict.json                # 키워드 사전
```

---

## 주의사항

### 실행 순서

**중요**: 반드시 다음 순서대로 실행해야 합니다.

1. 데이터 변환 (01~05) → 중간 JSON 파일 생성
2. 데이터 보강 (07) → `_enriched.json` 파일 생성
3. 키워드 추출 (08) → `_enriched.json` 파일에 키워드 추가
4. 임베딩 생성 (06) → `_with_embeddings.json` 파일 생성

### 파일 이름 규칙

- **중간 파일**: `teddycard_*.json`, `teddycard_*_enriched.json`
- **최종 파일**: `teddycard_*_with_embeddings.json`
- 임베딩 생성 스크립트는 `_enriched.json` 파일을 우선적으로 읽습니다.

### 환경 변수

- `OPENAI_API_KEY`: 필수 (임베딩 생성 및 LLM 사용 시)
- 기타 설정값 (모델, 딜레이 등)은 스크립트 내 기본값 사용 가능

---

## 트러블슈팅

### 임베딩 생성 중단

**재개 방법**:
```bash
python 06_generate_embeddings.py --resume
```

체크포인트 파일(`embedding_checkpoint.json`)에서 중단 지점부터 재개합니다.

### 메모리 부족

임베딩 생성 시 메모리 사용량이 높을 수 있습니다. 필요시 배치 크기를 줄이거나 파일을 분할하여 처리하세요.

### API 요청 제한

OpenAI API 요청 제한에 걸릴 수 있습니다. 기본 딜레이(0.5초)가 설정되어 있으나, 필요시 `.env`에서 조정 가능합니다.

---

## 다음 단계

1. **DB 적재**: `backend_dev/app/db/scripts/05_load_teddycard_data.py` 실행
2. **검증**: 데이터베이스에 올바르게 적재되었는지 확인
3. **프론트엔드 연동**: STT 키워드 → VectorDB 검색 → 화면 표시

---

## 상세 문서

- [실행 가이드](./실행_가이드.md): 전체 전처리 과정의 상세 실행 가이드 (작성 예정)
- [파일 구조 및 워크플로우](./파일_구조_및_워크플로우.md): 파일 명명 규칙 및 워크플로우 설명 (작성 예정)
- [향후 전처리 작업 가이드](../향후_전처리_작업_가이드.md) ⭐ Backend/RAG 개발 중 전처리 개선이 필요할 때 참고

## 참고

- 모든 스크립트는 프로젝트 루트에서 실행 가능합니다 (상대 경로 사용)
- 출력 파일은 `data-preprocessing_dev/data/teddycard/`에 생성됩니다
- `config.py`의 `ENV_TYPE`이 `'dev'`로 설정되어 있어 자동으로 올바른 경로를 사용합니다

---

**작성일**: 2026-01-11  
**최종 업데이트**: 2026-01-13
