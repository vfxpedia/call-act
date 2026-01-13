# Structured 필드 생성 실행 가이드

## 개요

이 가이드는 개선된 structured 필드 생성 스크립트를 실행하는 방법을 안내합니다.

## 주요 개선 사항

1. **문서 타입 자동 분류**: workflow (업무 처리) vs information (정보 제공)
2. **키워드 사전 활용**: `keywords_dict.json`을 활용한 분류 정확도 향상
3. **타입별 다른 structured 형식**:
   - **workflow**: systemPath, requiredChecks, exceptions 등 업무 처리 형식
   - **information**: keyPoints, benefits, usageGuide 등 정보 제공 형식
   - **card_info**: 카드 정보 전용 형식
4. **자세히 보기용 필드 추가**: detailContent (1000자), fullTerms (약관 전문, 2000자)
5. **card_products 처리 추가**: 카드 상품 정보도 structured 필드 생성
6. **notices structured 제거**: RAG 검색 미사용이므로 structured 필드 제거

## 사전 준비

### 1. 환경 변수 확인

```powershell
# .env 파일 확인
cd C:\Users\AI-WS01\projects\call-act
Get-Content .env | Select-String "OPENAI_API_KEY"
```

**필수**: `OPENAI_API_KEY`가 설정되어 있어야 LLM을 사용한 구조화가 가능합니다.

### 2. 키워드 사전 확인

```powershell
# 키워드 사전 파일 확인
cd data-preprocessing_dev\preprocessing\teddycard
python -c "from config import KEYWORDS_DICT_FILE; import json; print(f'키워드 사전: {len(json.load(open(KEYWORDS_DICT_FILE, \"r\", encoding=\"utf-8\")))}개 카테고리')"
```

## 실행 단계

### Step 1: Structured 필드 생성

```powershell
# 작업 디렉토리로 이동
cd data-preprocessing_dev\preprocessing\teddycard

# Structured 필드 생성 실행
python 11_structured_for_rag.py
```

**실행 시간**: 
- 순차 처리: 약 100-200개 문서 기준 10-20분
- 병렬 처리: 약 5-10분 (환경 변수 `STRUCTURE_USE_PARALLEL=true` 설정 시)

**예상 출력**:
```
================================================================================
RAG 검색 성능 개선 - 구조화 데이터 생성
================================================================================

[INFO] 키워드 사전 로드 완료: 57개 카테고리

[INFO] 순차 처리 모드
[INFO] 요청 간 딜레이: 0.5초

[1단계] service_guide_documents 구조화

[INFO] 처리 중: teddycard_service_guides_hyundai.json (순차 처리)
구조화 중 (teddycard_service_guides_hyundai.json): 100%|████████| 50/50 [05:23<00:00,  6.46s/it]

[INFO] 처리 중: teddycard_service_guides_samsung.json (순차 처리)
구조화 중 (teddycard_service_guides_samsung.json): 100%|████████| 20/20 [02:15<00:00,  6.75s/it]

[INFO] 처리 중: teddycard_service_guides_shinhan.json (순차 처리)
구조화 중 (teddycard_service_guides_shinhan.json): 100%|████████| 988/988 [82:30<00:00,  5.00s/it]

[INFO] 처리 중: teddycard_service_guides_special.json (순차 처리)
구조화 중 (teddycard_service_guides_special.json): 100%|████████| 30/30 [02:30<00:00,  5.00s/it]

[2단계] card_products 구조화

[INFO] 처리 중: teddycard_card_products.json
구조화 중 (card_products): 100%|████████| 100/100 [08:20<00:00,  5.00s/it]

[3단계] notices 처리 (structured 필드 제거)

[INFO] 처리 중: teddycard_notices_enriched.json (structured 필드 제거 - RAG 검색 미사용)
[INFO] 저장 완료: ... (20개 문서, structured 필드 제거됨)

================================================================================
구조화 완료
================================================================================
  teddycard_service_guides_hyundai.json: 50개 문서
  teddycard_service_guides_samsung.json: 20개 문서
  teddycard_service_guides_shinhan.json: 988개 문서
  teddycard_service_guides_special.json: 30개 문서
  teddycard_card_products.json: 100개 카드
  teddycard_notices_enriched.json: 20개 문서

총 1208개 문서 구조화 완료

[INFO] 기존 JSON 파일에 structured 필드가 추가되었습니다.
[INFO] service_guides: workflow/information 타입별 다른 structured 형식
[INFO] card_products: 카드 정보 형식 structured 추가
[INFO] notices: structured 필드 제거 (RAG 검색 미사용)
[INFO] DB 적재 시 structured 필드를 함께 저장하세요.
```

### Step 2: Structured 필드 전파

```powershell
# Structured 필드 전파 실행
python 12_propagate_structured.py
```

**실행 시간**: 약 1-2분

**예상 출력**:
```
============================================================
structured 필드 전파 스크립트
============================================================
출력 디렉토리: ...\data-preprocessing_dev\preprocessing\output

=== 서비스 가이드 (service_guides) 처리 ===
[INFO] teddycard_service_guides_hyundai.json: 50개의 structured 필드 발견
[INFO] teddycard_service_guides_samsung.json: 20개의 structured 필드 발견
[INFO] teddycard_service_guides_shinhan.json: 988개의 structured 필드 발견
[INFO] teddycard_service_guides_special.json: 30개의 structured 필드 발견
[INFO] 총 1088개의 structured 필드를 수집했습니다.
[INFO] teddycard_service_guides_enriched.json: 1088개 업데이트, 0개 추가
[SUCCESS] 저장 완료: ...\teddycard_service_guides_enriched.json
[INFO] teddycard_service_guides_with_embeddings.json: 1088개 업데이트, 0개 추가
[SUCCESS] 저장 완료: ...\teddycard_service_guides_with_embeddings.json

=== 카드 상품 (card_products) 처리 ===
[INFO] Source 파일에서 100개의 structured 필드를 찾았습니다.
[INFO] teddycard_card_products_enriched.json: 100개 업데이트, 0개 추가
[SUCCESS] 저장 완료: ...\teddycard_card_products_enriched.json
[INFO] teddycard_card_products_with_embeddings.json: 100개 업데이트, 0개 추가
[SUCCESS] 저장 완료: ...\teddycard_card_products_with_embeddings.json

=== 공지사항 (notices) 처리 - structured 필드 제거 ===
[INFO] teddycard_notices.json: 0개 문서에서 structured 필드 제거
[INFO] teddycard_notices_enriched.json: 20개 문서에서 structured 필드 제거
[SUCCESS] 저장 완료: ...\teddycard_notices_enriched.json
[INFO] teddycard_notices_with_embeddings.json: 20개 문서에서 structured 필드 제거
[SUCCESS] 저장 완료: ...\teddycard_notices_with_embeddings.json

============================================================
처리 완료!
============================================================

[INFO] service_guides: enriched, with_embeddings에 structured 필드 전파 완료
[INFO] card_products: enriched, with_embeddings에 structured 필드 전파 완료
[INFO] notices: structured 필드 제거 완료 (RAG 검색 미사용)
```

### Step 3: 결과 검증

```powershell
# Structured 필드 확인
python -c "
import json
from pathlib import Path

output_dir = Path('../../output')

# service_guides 확인
files = [
    'teddycard_service_guides_hyundai.json',
    'teddycard_service_guides_samsung.json',
    'teddycard_card_products.json'
]

for filename in files:
    file_path = output_dir / filename
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if data:
            sample = data[0]
            structured = sample.get('structured', {})
            structured_type = sample.get('structured_type', 'unknown')
            print(f'\n{filename}:')
            print(f'  총 문서 수: {len(data)}')
            print(f'  structured 필드 있음: {sum(1 for d in data if \"structured\" in d)}')
            print(f'  문서 타입: {structured_type}')
            print(f'  structured 키: {list(structured.keys()) if structured else []}')
"
```

**예상 출력**:
```
teddycard_service_guides_hyundai.json:
  총 문서 수: 50
  structured 필드 있음: 50
  문서 타입: workflow
  structured 키: ['title', 'content', 'systemPath', 'requiredChecks', 'exceptions', 'regulation', 'detailContent', 'fullTerms', 'time', 'note']

teddycard_service_guides_samsung.json:
  총 문서 수: 20
  structured 필드 있음: 20
  문서 타입: information
  structured 키: ['title', 'content', 'keyPoints', 'benefits', 'usageGuide', 'relatedTopics', 'detailContent', 'fullTerms', 'note']

teddycard_card_products.json:
  총 문서 수: 100
  structured 필드 있음: 100
  문서 타입: card_info
  structured 키: ['cardName', 'cardType', 'annualFee', 'mainBenefits', 'benefitDetails', 'performanceConditions', 'usageGuide', 'detailContent', 'fullTerms', 'note']
```

## 병렬 처리 옵션

병렬 처리를 사용하려면 환경 변수를 설정합니다:

```powershell
# 환경 변수 설정 (PowerShell)
$env:STRUCTURE_USE_PARALLEL = "true"
$env:STRUCTURE_MAX_WORKERS = "5"

# 스크립트 실행
python 11_structured_for_rag.py
```

**주의**: 동일한 OpenAI API 키를 다른 노트북에서 동시에 사용하면 rate limit 초과 위험이 있습니다.

## 문제 해결

### LLM API 호출 실패

**증상**: `[WARNING] LLM 구조화 실패: ...`

**해결**:
1. `OPENAI_API_KEY` 확인
2. API 사용량 한도 확인
3. 네트워크 연결 확인
4. 규칙 기반 fallback으로 자동 처리됨

### 키워드 사전 파일 없음

**증상**: `[WARNING] 키워드 사전 파일을 찾을 수 없습니다`

**해결**:
- 키워드 사전 없이도 기본 키워드 매칭으로 작동
- 분류 정확도는 다소 낮을 수 있음

### 문서 타입 분류 오류

**증상**: workflow 문서가 information으로 분류되거나 그 반대

**해결**:
- `keywords_dict.json` 업데이트로 개선 가능
- 수동으로 `structured_type` 필드 확인 후 필요시 재실행

## 다음 단계

1. **DB 적재**: `backend_dev/app/db/scripts/03_load_teddycard_to_db.py` 실행
2. **데이터 검증**: `backend_dev/app/db/scripts/04_verify_teddycard_load.py` 실행
3. **Docker 빌드**: Docker 이미지 빌드 및 Docker Hub 푸시
4. **AWS Lightsail 배포**: 팀원 공유

자세한 내용은 `28_structured_필드_생성_및_배포_실행_가이드.md` 참조
