# 파일 상태 정리 및 structured 필드 전파 가이드

## 목적

`data-preprocessing_dev/preprocessing/output/` 폴더 내 모든 테디카드 JSON 파일의 상태를 명확히 정리하고, `structured` 필드를 원본, 보강(enriched), 임베딩(with_embeddings) 파일 모두에 일관되게 적용합니다.

## 파일 상태 정리

### 1. 카드 상품 (card_products)

| 파일명 | 단계 | structured 필드 | 설명 |
|--------|------|----------------|------|
| `teddycard_card_products.json` | 원본 | ❌ 없음 | 신한카드 마크다운에서 변환된 기본 JSON |
| `teddycard_card_products_enriched.json` | 보강 | ❌ 없음 | 연회비, 브랜드 등 DB 적재용 필드 추가 |
| `teddycard_card_products_with_embeddings.json` | 임베딩 | ❌ 없음 | 임베딩 벡터 포함 (DB 적재용 최종 파일) |

**참고**: `card_products`는 프론트엔드에서 구조화 형식을 사용하지 않으므로 `structured` 필드가 필요 없습니다.

### 2. 공지사항 (notices)

| 파일명 | 단계 | structured 필드 | 설명 |
|--------|------|----------------|------|
| `teddycard_notices.json` | 원본 | ❌ 없음 | 삼성카드 공지사항에서 변환된 기본 JSON |
| `teddycard_notices_enriched.json` | 보강 | ✅ 있음 | `11_structured_for_rag.py` 실행 결과 포함 |
| `teddycard_notices_with_embeddings.json` | 임베딩 | ❌ 없음 | 임베딩 벡터 포함, structured 필드 누락 |

**작업 필요**: `structured` 필드를 `teddycard_notices.json`과 `teddycard_notices_with_embeddings.json`에 전파

### 3. 서비스 가이드 (service_guides)

#### 3.1 원본 파일 (카드사별)

| 파일명 | 단계 | structured 필드 | 설명 |
|--------|------|----------------|------|
| `teddycard_service_guides_hyundai.json` | 원본 | ✅ 있음 | `11_structured_for_rag.py` 실행 결과 포함 |
| `teddycard_service_guides_samsung.json` | 원본 | ✅ 있음 | `11_structured_for_rag.py` 실행 결과 포함 |
| `teddycard_service_guides_shinhan.json` | 원본 | ✅ 있음 | `11_structured_for_rag.py` 실행 결과 포함 |
| `teddycard_service_guides_special.json` | 원본 | ✅ 있음 | `11_structured_for_rag.py` 실행 결과 포함 |

#### 3.2 통합 파일

| 파일명 | 단계 | structured 필드 | 설명 |
|--------|------|----------------|------|
| `teddycard_service_guides_enriched.json` | 보강 | ❓ 확인 필요 | 4개 원본 파일 통합, structured 필드 확인 필요 |
| `teddycard_service_guides_with_embeddings.json` | 임베딩 | ❌ 없음 | 임베딩 벡터 포함, structured 필드 누락 |

**작업 필요**: 
- `teddycard_service_guides_enriched.json`에 structured 필드 확인 및 추가
- `teddycard_service_guides_with_embeddings.json`에 structured 필드 전파

## 데이터 파이프라인

```
원본 데이터 변환
    ↓
[원본 JSON] teddycard_*.json
    ↓
데이터 보강 (07_enrich_for_db.py)
    ↓
[보강 JSON] teddycard_*_enriched.json
    ↓
키워드 추출 (08_extract_keywords.py)
    ↓
RAG 구조화 (11_structured_for_rag.py) ← structured 필드 추가
    ↓
임베딩 생성 (06_generate_embeddings.py)
    ↓
[임베딩 JSON] teddycard_*_with_embeddings.json ← structured 필드 누락
```

## 문제점

1. **structured 필드 불일치**: `11_structured_for_rag.py`가 일부 파일에만 `structured` 필드를 추가했고, 임베딩 파일에는 전파되지 않음
2. **파일 간 동기화 부족**: 원본, 보강, 임베딩 파일 간 `structured` 필드가 일관되지 않음
3. **DB 적재 시 데이터 손실**: `_with_embeddings.json` 파일에 `structured` 필드가 없으면 DB 적재 후 RAG 검색 시 구조화 데이터를 사용할 수 없음

## 해결 방안

### 1. structured 필드 전파 스크립트 실행

`12_propagate_structured.py` 스크립트를 실행하여:
- `structured` 필드가 있는 파일에서 필드를 읽어옴
- 같은 `id`를 가진 문서를 원본, enriched, with_embeddings 파일에서 찾음
- `structured` 필드를 추가/업데이트함

### 2. 재임베딩 필요 여부

**재임베딩 불필요**: `structured` 필드는 메타데이터이므로 본문(`text`, `content`)이 변경되지 않았습니다. 기존 임베딩은 그대로 유효합니다.

### 3. 실행 순서

1. `12_propagate_structured.py` 실행
2. 결과 확인 (structured 필드가 모든 파일에 추가되었는지)
3. DB 적재 준비 완료

## 다음 단계

1. `12_propagate_structured.py` 스크립트 작성 및 실행
2. 파일 상태 최종 확인
3. DB 적재 진행
