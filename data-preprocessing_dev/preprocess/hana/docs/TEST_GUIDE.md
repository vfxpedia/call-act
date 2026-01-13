# 코드 테스트 가이드

**작성일**: 2026-01-07
**최종 수정일**: 2026-01-07
**버전**: v1.0
**목적**: `preprocess_hana.py` 및 `generate_scenarios.py` 테스트 방법 안내

---

## 목차

1. [단일 source_id 테스트](#1-단일-source_id-테스트)
2. [여러 샘플 테스트](#2-여러-샘플-테스트)
3. [시나리오 생성 테스트](#3-시나리오-생성-테스트)
4. [전체 데이터 처리 테스트](#4-전체-데이터-처리-테스트)
5. [검증 체크리스트](#5-검증-체크리스트)
6. [문제 해결](#6-문제-해결)
7. [성능 측정](#7-성능-측정)
8. [테스트 시나리오 예시](#8-테스트-시나리오-예시)

---

## 1. 단일 source_id 테스트

### 1.1 기본 테스트 스크립트 사용

```bash
cd C:\SKN_19\project\4th\data-preprocessing
python preprocess/hana/test_specific_row.py
```

**설정 변경**: `test_specific_row.py` 파일에서 `target_source_id` 수정
```python
target_source_id = '21749'  # 원하는 source_id로 변경
```

**출력 위치**:
- `preprocess/hana/test_results/test_{source_id}.txt` - 전처리된 텍스트
- `preprocess/hana/test_results/test_{source_id}.json` - 메타데이터 포함 JSON

**주의사항**:
- 기본 LLM 모델: `gpt-4.1-mini` (환경변수 `OPENAI_MODEL`로 변경 가능)
- API 키가 없으면 `[개인정보]`로 폴백 처리됨

### 1.2 직접 함수 호출 테스트

```python
from preprocess.hana.preprocess_hana import (
    normalize_all_masking_v2, 
    extract_scenario_tags,
    merge_semantic_duplicate_tags
)

# 원본 텍스트 (▲ 포함)
text = "상담사: ▲▲▲초등학교 ▲▲▲학생 맞으실까요?"

# 전처리 실행 (v2.5)
cleaned_text, slot_types = normalize_all_masking_v2(
    text, 
    use_llm=True,              # LLM 사용 여부
    validate=True,              # 검증 수행 여부
    merge_semantic_tags=True,   # v2.5: 문맥 기반 태그 통합
    semantic_use_llm=False      # 빠른 규칙 기반 (True면 LLM 사용, 느리지만 정확)
)

# 시나리오 태그 추출
scenario_tags = extract_scenario_tags(cleaned_text)

print(f"Slot types: {slot_types}")
print(f"Scenario tags: {scenario_tags}")
print(f"Cleaned text: {cleaned_text}")

# 문맥 태그 통합 직접 테스트
test_text = "기본 연회비가 [금액#1]이고 ... 기본 연회비를 이미 [금액#4]에서"
merged = merge_semantic_duplicate_tags(test_text, use_llm=False)
print(f"Merged: {merged}")  # [금액#4] → [금액#1]로 통합됨
```

**파라미터 설명**:
- `use_llm`: LLM을 사용한 슬롯 태깅 여부 (기본값: True)
- `validate`: 검증 수행 여부 (기본값: True)
- `merge_semantic_tags`: 문맥 기반 태그 통합 수행 여부 (기본값: True, v2.5 추가)
- `semantic_use_llm`: 태그 통합 시 LLM 사용 여부 (기본값: False, 규칙 기반이 빠름)

---

## 2. 여러 샘플 테스트

### 2.1 114개 샘플 테스트 (57 카테고리 × 2개)

```bash
cd C:\SKN_19\project\4th\data-preprocessing
python preprocess/hana/test_114_samples.py
```

**출력 위치**: `preprocess/hana/test_results/samples_114/`
- 각 샘플: `test_{source_id}.txt`
- 요약: `summary.json`

### 2.2 57개 카테고리 테스트 (각 1개씩)

```bash
cd C:\SKN_19\project\4th\data-preprocessing
python preprocess/hana/test_all_categories.py
```

**출력 위치**: `preprocess/hana/test_results/all_categories_v{N}/`

---

## 3. 시나리오 생성 테스트

### 3.1 테스트 모드 (카테고리별 1개씩)

```bash
cd C:\SKN_19\project\4th\data-preprocessing
python preprocess/hana/generate_scenarios.py
```

**입력**: `test_results/samples_114/`
**출력**: `test_results/scenarios_llm_v{NN}/`

### 3.2 전체 데이터 처리 모드 (카테고리별 2개씩)

```bash
cd C:\SKN_19\project\4th\data-preprocessing
python preprocess/hana/generate_scenarios.py --full-run
```

**입력**: `test_results/full_run/` (전처리 완료 후 생성된 샘플)
**출력**: `test_results/scenarios_llm_v{NN}/`

### 3.3 사용자 지정 입력 디렉토리

```bash
python preprocess/hana/generate_scenarios.py --input=test_results/custom_folder
```

---

## 4. 전체 데이터 처리 테스트

### 4.1 소규모 샘플 테스트 (10개)

```python
# preprocess_hana.py 수정
process_csv_file(
    csv_path=Path('data/hana/TS_하나카드_통합 - 시트1.csv'),
    output_dir=Path('data/hana'),
    sample_size=10  # 처음 10개만 테스트
)
```

### 4.2 전체 데이터 처리

```bash
cd C:\SKN_19\project\4th\data-preprocessing
python preprocess/hana/preprocess_hana.py
```

**출력 위치**:
- `data/hana/hana_vectordb.json` - VectorDB용
- `data/hana/hana_rdb_metadata.json` - RDB용
- `preprocess/hana/test_results/full_run/` - 샘플 txt 파일 (카테고리별 2개)

---

## 5. 검증 체크리스트

### 5.1 전처리 결과 검증

- [ ] ▲ 마스킹이 모두 태그로 변환되었는가?
- [ ] 태그 형식이 `[타입#번호]`인가?
- [ ] 동일 개체가 같은 번호를 사용하는가? (Entity Tracking)
- [ ] 불용어가 적절히 축소되었는가?
- [ ] 문맥상 같은 의미의 태그가 통합되었는가? (v2.5)

### 5.2 시나리오 생성 검증

- [ ] 모든 태그가 실제 값으로 치환되었는가?
- [ ] 동일 번호의 태그가 같은 값인가?
- [ ] 단위 중복이 없는가? (예: "15만원원" → "15만원")
- [ ] 문맥상 자연스러운가?
- [ ] 카테고리별 특성이 반영되었는가?

---

## 6. 문제 해결

### 6.1 LLM API 오류

**증상**: `OPENAI_API_KEY not found` 또는 API 오류

**해결**:
```bash
# 환경변수 설정 (Windows PowerShell)
$env:OPENAI_API_KEY = "your-api-key-here"

# 모델 변경 (선택사항)
$env:OPENAI_MODEL = "gpt-4.1-mini"  # 기본값

# 또는 .env 파일 사용 (프로젝트 루트에 생성)
# OPENAI_API_KEY=your-api-key-here
# OPENAI_MODEL=gpt-4.1-mini
```

**기본 모델**: `gpt-4.1-mini` (환경변수 `OPENAI_MODEL`로 변경 가능)

### 6.2 처리 시간이 너무 오래 걸림

**원인**: LLM API 호출 시간

**해결**:
- `semantic_use_llm=False`로 설정 (규칙 기반 태그 통합 사용)
- `use_llm=False`로 설정 (LLM 없이 정규식만 사용, 품질 저하)

### 6.3 태그 통합이 제대로 안 됨

**원인**: 문맥 유사도 임계값이 너무 높음

**해결**: `_calculate_context_similarity()` 함수의 임계값 조정
```python
if similarity > 0.6:  # 0.5로 낮추면 더 많이 통합됨
```

---

## 7. 성능 측정

### 7.1 처리 시간 확인

전처리 로그에서 확인:
```
[COMPLETE] Total processing time: 35분 30초
[COMPLETE] Average per row: 21.34초
```

### 7.2 예상 시간 계산

- **평균 처리 시간**: 21.34초/샘플
- **6,000개 예상 시간**: 약 35.6시간 (약 1.5일)
- **시나리오 생성**: 약 12.4초/시나리오

---

## 8. 테스트 시나리오 예시

### 시나리오 1: 단일 케이스 빠른 검증
```bash
# 1. test_specific_row.py에서 source_id 변경
# 2. 실행하여 결과 확인
python preprocess/hana/test_specific_row.py
# 3. test_results/test_{source_id}.txt 확인
```

### 시나리오 2: 새 기능 검증 (문맥 태그 통합)

**목적**: v2.5에서 추가된 문맥 기반 태그 통합 기능 테스트

```python
from preprocess.hana.preprocess_hana import merge_semantic_duplicate_tags

# 테스트 케이스 1: 같은 의미의 금액 태그 통합
text1 = "기본 연회비가 [금액#1]이고 ... 기본 연회비를 이미 [금액#4]에서"
result1 = merge_semantic_duplicate_tags(text1, use_llm=False)
# 예상 결과: [금액#4] → [금액#1]로 통합

# 테스트 케이스 2: 다른 의미의 금액 태그는 분리 유지
text2 = "기본 연회비 [금액#1] ... 제휴 연회비 [금액#2]"
result2 = merge_semantic_duplicate_tags(text2, use_llm=False)
# 예상 결과: [금액#1]과 [금액#2]는 분리 유지 (다른 의미)

print(f"Test 1: {result1}")
print(f"Test 2: {result2}")
```

**검증 포인트**:
- 같은 문맥의 태그는 통합되는가?
- 다른 문맥의 태그는 분리 유지되는가?
- 규칙 기반 vs LLM 기반 차이 확인

### 시나리오 3: 전체 파이프라인 테스트

**목적**: 전처리부터 시나리오 생성까지 전체 흐름 검증

```bash
# 1. 전처리 (소규모 테스트)
# preprocess_hana.py의 main() 함수에서 sample_size=10으로 수정
cd C:\SKN_19\project\4th\data-preprocessing
python preprocess/hana/preprocess_hana.py

# 출력 확인:
# - data/hana/hana_vectordb.json
# - data/hana/hana_rdb_metadata.json
# - preprocess/hana/test_results/full_run/ (샘플 txt 파일)

# 2. 시나리오 생성 (전체 데이터 처리 모드)
python preprocess/hana/generate_scenarios.py --full-run

# 출력 확인:
# - preprocess/hana/test_results/scenarios_llm_v{NN}/
# - 각 카테고리별 2개씩 시나리오 생성됨

# 3. 결과 검증
# - 시나리오 파일들이 자연스러운지 확인
# - 태그가 모두 치환되었는지 확인
# - 문맥상 일관성이 있는지 확인
```

### 시나리오 4: 모델 변경 테스트

**목적**: 다른 LLM 모델로 성능 비교

```bash
# gpt-4o-mini로 변경하여 테스트
$env:OPENAI_MODEL = "gpt-4o-mini"
python preprocess/hana/test_specific_row.py

# 결과 비교:
# - 처리 시간
# - 태깅 정확도
# - 비용 (토큰 사용량)
```

---

## 9. 빠른 참조

### 9.1 주요 명령어

| 작업 | 명령어 |
|------|--------|
| 단일 테스트 | `python preprocess/hana/test_specific_row.py` |
| 114개 샘플 | `python preprocess/hana/test_114_samples.py` |
| 전체 전처리 | `python preprocess/hana/preprocess_hana.py` |
| 시나리오 생성 (테스트) | `python preprocess/hana/generate_scenarios.py` |
| 시나리오 생성 (전체) | `python preprocess/hana/generate_scenarios.py --full-run` |

### 9.2 주요 출력 경로

| 파일/폴더 | 경로 | 설명 |
|-----------|------|------|
| VectorDB JSON | `data/hana/hana_vectordb.json` | 최종 전처리 결과 |
| RDB JSON | `data/hana/hana_rdb_metadata.json` | 메타데이터 |
| 샘플 txt | `preprocess/hana/test_results/samples_114/` | 테스트 샘플 |
| 시나리오 | `preprocess/hana/test_results/scenarios_llm_v{NN}/` | 생성된 시나리오 |

### 9.3 환경변수

| 변수명 | 기본값 | 설명 |
|--------|--------|------|
| `OPENAI_API_KEY` | (필수) | OpenAI API 키 |
| `OPENAI_MODEL` | `gpt-4.1-mini` | 사용할 LLM 모델 |

---

