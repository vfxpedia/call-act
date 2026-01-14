# Teddycard 데이터 검증 가이드

**작성일**: 2026-01-13  
**작성자**: CALL:ACT Team  
**버전**: v1.0

---

## 개요

테디카드 데이터 DB 적재 후 검증 스크립트를 실행하여 데이터가 올바르게 적재되었는지 확인합니다.

## 검증 스크립트

**파일**: `backend_dev/app/db/scripts/06_verify_teddycard_load.py`

**기능**:
- 데이터 개수 확인 (service_guide_documents, card_products, notices)
- 임베딩 벡터 검증 (차원, NULL 체크)
- Structured 필드 확인
- 키워드 사전 적재 확인
- 샘플 데이터 확인
- Metadata 필드 확인

## 실행 방법

### 1. 환경 설정

```bash
# Conda 환경 활성화
conda activate final_env

# 스크립트 디렉토리로 이동
cd backend_dev/app/db/scripts
```

### 2. .env 파일 확인

`.env` 파일에 다음 환경 변수가 설정되어 있어야 합니다:

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=callact_admin
DB_PASSWORD=callact_pwd1
DB_NAME=callact_db
```

### 3. 검증 스크립트 실행

```bash
python 06_verify_teddycard_load.py
```

## 검증 항목

### 1. 데이터 개수 확인

다음 테이블의 데이터 개수를 확인합니다:
- `service_guide_documents`
- `card_products`
- `notices`
- `keyword_dictionary`
- `keyword_synonyms`

**예상 결과**:
- service_guide_documents: 약 1,273건
- card_products: 약 398건
- notices: 약 100건
- keyword_dictionary: 약 500건 이상
- keyword_synonyms: 약 1,000건 이상

### 2. 임베딩 벡터 검증

- 임베딩이 있는 문서 수 확인
- 임베딩 차원 확인 (1536차원)
- 임베딩이 없는 문서 수 확인

**예상 결과**:
- 임베딩 차원: 1536
- service_guide_documents의 모든 문서에 임베딩이 있어야 함

### 3. Structured 필드 확인

- `service_guide_documents`의 `structured` 필드 확인
- `card_products`의 `structured` 필드 확인

**예상 결과**:
- service_guide_documents의 모든 문서에 `structured` 필드가 있어야 함
- card_products의 모든 문서에 `structured` 필드가 있어야 함

### 4. 키워드 사전 적재 확인

- `keyword_dictionary` 테이블의 키워드 수
- 카테고리 수
- 평균 우선순위 및 긴급성
- `keyword_synonyms` 테이블의 동의어 수

### 5. 샘플 데이터 확인

각 테이블에서 샘플 데이터를 확인하여:
- ID, 제목, 카테고리 등 기본 정보 확인
- 키워드 수 확인
- 임베딩 및 structured 필드 존재 여부 확인
- 문서 번호 (document_number) 확인

### 6. Metadata 필드 확인

- `metadata` JSONB 필드에 `document_number`가 포함되어 있는지 확인

## 출력 예시

```
============================================================
테디카드 데이터 DB 적재 검증 스크립트
============================================================
[INFO] Database: localhost:5432/callact_db

============================================================
[1] 데이터 개수 확인
============================================================
  service_guide_documents: 1,273건
  card_products: 398건
  notices: 100건
  keyword_dictionary: 523건
  keyword_synonyms: 1,245건

============================================================
[2] 임베딩 벡터 검증
============================================================
  service_guide_documents:
    전체: 1,273건
    임베딩 있음: 1,273건
    임베딩 없음: 0건
    임베딩 차원: 1536
    ✅ 차원 검증 통과

============================================================
[3] Structured 필드 확인
============================================================
  service_guide_documents:
    전체: 1,273건
    structured 있음: 1,273건
    structured 없음: 0건
  card_products:
    전체: 398건
    structured 있음: 398건
    structured 없음: 0건

============================================================
[4] 키워드 사전 적재 확인
============================================================
  keyword_dictionary:
    전체 키워드: 523건
    카테고리 수: 15개
    평균 우선순위: 7.5
    평균 긴급성: 6.2
  keyword_synonyms:
    전체 동의어: 1,245건
    동의어가 있는 키워드: 312개

============================================================
[최종 요약]
============================================================
  전체 문서: 1,771건
    - service_guide_documents: 1,273건
    - card_products: 398건
    - notices: 100건
  키워드 사전: 523건
  동의어: 1,245건

  ✅ 모든 검증을 통과했습니다!
```

## 문제 해결

### 임베딩 차원이 올바르지 않은 경우

- 임베딩 생성 스크립트를 다시 실행
- OpenAI API 모델 확인 (`text-embedding-3-small`)

### Structured 필드가 없는 경우

- `12_propagate_structured.py` 스크립트 실행
- 데이터 적재 스크립트 재실행

### 키워드 사전이 비어있는 경우

- `04_load_keyword_dictionary.py` 스크립트 실행
- 키워드 사전 파일 경로 확인

## 다음 단계

검증이 완료되면:
1. Backend 동기화 진행
2. Backend 브랜치 커밋
3. Docker Hub 업로드
4. AWS Lightsail 배포

---

## 참고 문서

- [Backend 구조 비교 분석](./07_Backend_구조_비교_분석.md)
- [Backend 동기화 가이드](./09_Backend_동기화_가이드.md)
- [Backend 커밋 가이드](./10_Backend_커밋_가이드.md)
