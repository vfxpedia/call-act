# 키워드 사전, 임베딩 청킹, RAG 구조화 개선 실행 가이드

**작성일**: 2026-01-12  
**작성자**: CALL:ACT Team  
**버전**: v1.0

---

## 개요

세 가지 개선 작업을 수행합니다:

1. **키워드 사전 업데이트**: 하나카드 데이터 기반 하이브리드 업데이트
2. **임베딩 에러 처리**: 실패한 22개 문서 청킹 및 재처리
3. **RAG 구조화 데이터 생성**: 프론트엔드 형식으로 미리 구조화

---

## 사전 준비

### 1. 환경 확인

```bash
# Conda 환경 활성화
conda activate final_env

# 작업 디렉토리 이동
cd data-preprocessing_dev/preprocessing/teddycard

# 필요한 패키지 확인
python -c "import openai, tiktoken, tqdm; print('OK')"
```

### 1.1 설정 파일 확인

**중요**: 모든 설정은 `config.py`에서 관리됩니다.

- **경로 설정**: `ENV_TYPE`으로 dev/prod 전환 가능
- **임베딩 설정**: `EMBEDDING_CONFIG`에서 관리
- **LLM 설정**: `LLM_CONFIG`에서 관리
- **API 키**: `.env` 파일에서만 관리 (프로젝트 루트)

### 2. 파일 확인

다음 파일들이 존재하는지 확인:

- `data-preprocessing/data/hana/hana_vectordb.json` (하나카드 데이터)
- `data-preprocessing_dev/preprocessing/output/embedding_errors.json` (에러 목록)
- `data-preprocessing_dev/preprocessing/output/teddycard_card_products_enriched.json` (원본 문서)
- `data-preprocessing_dev/preprocessing/output/teddycard_card_products_with_embeddings.json` (기존 임베딩)

---

## Step 1: 키워드 사전 업데이트

### 1.1 스크립트 실행

```bash
python 10_generate_keywords_dict_from_hana.py
```

### 1.2 실행 결과

- **출력 파일**: `keywords_dict_updated.json`
- **백업 파일**: `keywords_dict_backup.json` (기존 사전 백업)

### 1.3 결과 확인

스크립트 실행 후 다음 정보가 출력됩니다:

```
카테고리별 키워드 통계:
  분실도난: 15개 키워드, 1234건 문서
  결제: 28개 키워드, 2345건 문서
  ...
```

### 1.4 키워드 사전 적용

```powershell
# 업데이트된 사전을 기존 사전으로 교체 (Windows PowerShell)
Copy-Item keywords_dict_updated.json keywords_dict.json -Force
```

또는 Windows CMD:
```cmd
copy keywords_dict_updated.json keywords_dict.json
```

**주의**: 기존 `keywords_dict.json`이 백업되었는지 확인하세요.

---

## Step 2: 임베딩 에러 처리 (청킹)

### 2.1 스크립트 실행

```bash
python 10_chunk_and_embed_failed_documents.py
```

### 2.2 실행 과정

1. 에러 문서 22개 로드
2. 각 문서의 토큰 수 확인
3. 8192 토큰 초과 문서만 청킹 처리
4. 청크별 임베딩 생성
5. 기존 임베딩 파일에 추가 (덮어쓰기 금지)

### 2.3 결과 확인

스크립트 실행 후:

```
기존 문서: 376개
추가 문서: N개 (청크)
총 문서: 376 + N개
```

**주의**: 기존 376개 문서는 그대로 유지되고, 청킹된 문서만 추가됩니다.

### 2.4 청킹 정보

청킹된 문서는 다음 메타데이터를 포함합니다:

```json
{
  "id": "CARD-SHINHAN-XXX_chunk_1",
  "metadata": {
    "chunked": true,
    "original_id": "CARD-SHINHAN-XXX",
    "chunk_index": 1,
    "total_chunks": 3
  }
}
```

---

## Step 3: RAG 구조화 데이터 생성

### 3.1 스크립트 실행

```bash
python 11_structured_for_rag.py
```

### 3.2 실행 과정

1. `service_guide_documents` 파일들 처리 (4개 파일)
2. `notices` 파일 처리 (1개 파일)
3. 각 문서에 `structured` 필드 추가
4. `_structured.json` 파일로 저장

### 3.3 처리 파일 목록

**Service Guides**:
- `teddycard_service_guides_hyundai.json`
- `teddycard_service_guides_samsung.json`
- `teddycard_service_guides_shinhan.json`
- `teddycard_service_guides_special.json`

**Notices**:
- `teddycard_notices_enriched.json`

### 3.4 출력 파일

**중요**: 구조화된 데이터는 기존 JSON 파일에 `structured` 필드로 추가됩니다 (별도 파일 생성 안 함).

- `teddycard_service_guides_hyundai.json` (structured 필드 추가됨)
- `teddycard_service_guides_samsung.json` (structured 필드 추가됨)
- `teddycard_service_guides_shinhan.json` (structured 필드 추가됨)
- `teddycard_service_guides_special.json` (structured 필드 추가됨)
- `teddycard_notices_enriched.json` (structured 필드 추가됨)

### 3.5 구조화 데이터 형식

각 문서에 `structured` 필드가 추가됩니다:

```json
{
  "id": "...",
  "title": "...",
  "content": "...",
  "structured": {
    "title": "카드 분실 신고 처리 절차",
    "content": "고객의 카드 분실 신고를 접수하고 즉시 카드 사용을 정지합니다.",
    "systemPath": "고객관리 > 카드관리 > 분실신고 > 즉시정지",
    "requiredChecks": [
      "✓ 본인 확인: 주민번호 뒷자리 4자리 필수",
      "✓ 분실 일시 및 장소 확인"
    ],
    "exceptions": [
      "⚠️ 법인카드: 담당자 승인 필요",
      "⚠️ 가족카드: 주카드 회원 동의 필수"
    ],
    "regulation": "카드업무 취급요령 제34조 (분실신고 및 재발급)",
    "detailContent": "제34조 (카드의 분실신고 및 재발급)...",
    "time": "처리 시간: 약 3-5분",
    "note": "분실 신고 후 72시간 내 부정 사용 보상 가능"
  }
}
```

### 3.6 병렬 처리 옵션

**기본값**: 순차 처리 (안전)

**병렬 처리 활성화** (선택적):

```bash
# .env 파일에 추가
STRUCTURE_USE_PARALLEL=true
STRUCTURE_MAX_WORKERS=5  # 동시 작업자 수 (권장: 5-10)
```

**주의사항**:
- ✅ **하나의 API 키로 병렬 처리 가능**: 단일 노트북에서 5-10개 worker 사용 가능
- ⚠️ **다른 노트북에서 동시 실행 금지**: 동일 API 키를 여러 노트북에서 동시 사용 시 rate limit 초과 위험
- ⚠️ **Rate limit 관리**: 분당 60 requests로 제한 (안전 마진)
- 💡 **권장**: 안전하게 하나의 노트북에서 순차 처리 또는 병렬 처리 (5 workers)

**병렬 처리 실행**:

```bash
# .env 파일 설정 후
python 11_structured_for_rag.py
```

**순차 처리 실행** (기본, 권장):

```bash
# .env 파일에서 STRUCTURE_USE_PARALLEL 제거 또는 false로 설정
python 11_structured_for_rag.py
```

---

## 실행 순서 요약

```powershell
# 1. 키워드 사전 업데이트
python 10_generate_keywords_dict_from_hana.py
Copy-Item keywords_dict_updated.json keywords_dict.json -Force
```

# 2. 임베딩 에러 처리
python 10_chunk_and_embed_failed_documents.py

# 3. RAG 구조화 데이터 생성
python 11_structured_for_rag.py
```

---

## 예상 소요 시간

- **키워드 사전 업데이트**: 
  - 하나카드 데이터 수집: 1-2분
  - LLM 보완 (선택적): 30-60분 (샘플 수에 따라)
  
- **임베딩 청킹 처리**: 
  - 22개 문서 청킹: 5-10분
  - 청크 임베딩 생성: 10-20분 (청크 수에 따라)
  
- **RAG 구조화 데이터 생성**: 
  - 규칙 기반: 1-2분
  - LLM 기반 (순차 처리): 30-60분 (문서 수에 따라)
  - LLM 기반 (병렬 처리, 5 workers): 10-20분 (문서 수에 따라)

**총 예상 시간**: 
- 순차 처리: 약 1-2시간 (LLM 사용 시)
- 병렬 처리: 약 30-40분 (LLM 사용 시, 5 workers)

---

## 주의사항

### 1. 키워드 사전 업데이트

- 기존 `keywords_dict.json`이 자동으로 백업됩니다 (`keywords_dict_backup.json`)
- 업데이트된 사전을 적용하려면 수동으로 복사해야 합니다

### 2. 임베딩 청킹 처리

- **절대 덮어쓰기 금지**: 기존 376개 문서는 그대로 유지됩니다
- 청킹된 문서만 추가되므로 최종 문서 수는 376 + N개가 됩니다
- 청킹 정보는 `metadata` 필드에 저장됩니다

### 3. RAG 구조화 데이터 생성

- ✅ **기존 JSON 파일에 `structured` 필드가 추가됩니다** (별도 파일 생성 안 함)
- ✅ LLM 실패 시 규칙 기반 구조화로 자동 fallback됩니다
- ⚠️ **병렬 처리 시 주의**: 동일 API 키를 다른 노트북에서 동시 사용 금지
- 💡 **권장**: 안전하게 하나의 노트북에서 순차 처리 또는 병렬 처리 (5 workers)

---

## 트러블슈팅

### 문제 1: 하나카드 데이터 파일을 찾을 수 없음

**해결**:
```bash
# 파일 경로 확인
ls -la data-preprocessing/data/hana/hana_vectordb.json
```

파일이 다른 위치에 있다면 `10_generate_keywords_dict_from_hana.py`의 `HANA_DATA_FILE` 경로를 수정하세요.

### 문제 2: 임베딩 생성 실패

**원인**: OpenAI API 키 없음 또는 네트워크 오류

**해결**:
- `.env` 파일에 `OPENAI_API_KEY`가 설정되어 있는지 확인
- 네트워크 연결 확인
- API 사용량 한도 확인

### 문제 3: LLM 구조화 실패

**해결**: 규칙 기반 구조화로 자동 fallback되므로 문제없습니다. 다만 품질이 낮을 수 있으므로 LLM 사용을 권장합니다.

### 문제 4: Rate limit 오류 (429 Too Many Requests)

**원인**: 병렬 처리 시 API rate limit 초과

**해결**:
1. **병렬 처리 비활성화**: `.env`에서 `STRUCTURE_USE_PARALLEL=false` 설정
2. **Worker 수 감소**: `STRUCTURE_MAX_WORKERS=3`으로 설정
3. **순차 처리로 전환**: 가장 안전한 방법

**예방**:
- 동일 API 키를 다른 노트북에서 동시 사용 금지
- 하나의 노트북에서만 실행
- Worker 수를 5개 이하로 유지

---

## 다음 단계

1. **키워드 사전 적용**: `keywords_dict.json` 업데이트
2. **임베딩 파일 확인**: 청킹된 문서가 올바르게 추가되었는지 확인
3. **구조화 데이터 확인**: 기존 JSON 파일에 `structured` 필드가 추가되었는지 확인
4. **DB 적재**: 업데이트된 데이터를 DB에 적재 (structured 필드 포함)
5. **RAG 검색 테스트**: 구조화된 데이터로 RAG 검색 성능 확인

---

## 참고 파일

- 키워드 사전: `data-preprocessing_dev/preprocessing/tedicard/keywords_dict.json`
- 하나카드 데이터: `data-preprocessing/data/hana/hana_vectordb.json`
- 임베딩 에러: `data-preprocessing_dev/preprocessing/output/embedding_errors.json`
- 임베딩 결과: `data-preprocessing_dev/preprocessing/output/teddycard_card_products_with_embeddings.json`
- 구조화 결과: `data-preprocessing_dev/preprocessing/output/teddycard_*_structured.json`
