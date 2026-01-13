# structured 필드 전파 실행 가이드

## 목적

`11_structured_for_rag.py` 실행 결과로 생성된 `structured` 필드를 원본, 보강(enriched), 임베딩(with_embeddings) 파일 모두에 일관되게 전파합니다.

## 배경

현재 상황:
- 일부 원본 파일(`teddycard_service_guides_*.json`)에 `structured` 필드가 있음
- `teddycard_notices_enriched.json`에 `structured` 필드가 있음
- 하지만 `_with_embeddings.json` 파일들에는 `structured` 필드가 없음
- DB 적재 시 `structured` 필드가 필요하므로 모든 파일에 일관되게 적용해야 함

## 실행 방법

### 1. 환경 확인

```powershell
# 프로젝트 루트로 이동
cd C:\Users\AI-WS01\projects\call-act

# conda 환경 활성화 (필요시)
conda activate call-act
```

### 2. 스크립트 실행

```powershell
# structured 필드 전파 실행
python data-preprocessing_dev/preprocessing/teddycard/12_propagate_structured.py
```

### 3. 예상 출력

```
============================================================
structured 필드 전파 스크립트
============================================================
출력 디렉토리: C:\Users\AI-WS01\projects\call-act\data-preprocessing_dev\preprocessing\output

=== 공지사항 (notices) 처리 ===
[INFO] Source 파일에서 2개의 structured 필드를 찾았습니다.
[INFO] teddycard_notices.json: 0개 업데이트, 2개 추가
[SUCCESS] 저장 완료: teddycard_notices.json
[INFO] teddycard_notices_with_embeddings.json: 0개 업데이트, 2개 추가
[SUCCESS] 저장 완료: teddycard_notices_with_embeddings.json

=== 서비스 가이드 (service_guides) 처리 ===
[INFO] teddycard_service_guides_hyundai.json: 4개의 structured 필드 발견
[INFO] teddycard_service_guides_samsung.json: 1개의 structured 필드 발견
[INFO] teddycard_service_guides_shinhan.json: 988개의 structured 필드 발견
[INFO] teddycard_service_guides_special.json: 8개의 structured 필드 발견
[INFO] 총 1001개의 structured 필드를 수집했습니다.
[INFO] teddycard_service_guides_enriched.json: 0개 업데이트, 1001개 추가
[SUCCESS] 저장 완료: teddycard_service_guides_enriched.json
[INFO] teddycard_service_guides_with_embeddings.json: 0개 업데이트, 1001개 추가
[SUCCESS] 저장 완료: teddycard_service_guides_with_embeddings.json

============================================================
처리 완료!
============================================================
```

## 처리 로직

### 1. 공지사항 (notices)

- **Source**: `teddycard_notices_enriched.json` (structured 필드가 있는 파일)
- **Targets**:
  - `teddycard_notices.json` (원본)
  - `teddycard_notices_with_embeddings.json` (임베딩)

### 2. 서비스 가이드 (service_guides)

- **Source**: 4개 원본 파일에서 structured 필드 수집
  - `teddycard_service_guides_hyundai.json`
  - `teddycard_service_guides_samsung.json`
  - `teddycard_service_guides_shinhan.json`
  - `teddycard_service_guides_special.json`
- **Targets**:
  - `teddycard_service_guides_enriched.json` (보강, 통합)
  - `teddycard_service_guides_with_embeddings.json` (임베딩)

### 3. 매칭 기준

- 문서의 `id` 필드를 기준으로 매칭
- 같은 `id`를 가진 문서에 `structured` 필드를 추가/업데이트

## 재임베딩 필요 여부

**재임베딩 불필요**

이유:
- `structured` 필드는 메타데이터이므로 본문(`text`, `content`)이 변경되지 않았습니다
- 기존 임베딩은 본문 기반으로 생성되었으므로 그대로 유효합니다
- DB 적재 시 `structured` 필드만 추가로 저장하면 됩니다

## 검증 방법

### 1. 파일 확인

```powershell
# structured 필드가 추가되었는지 확인
python -c "import json; f = open('data-preprocessing_dev/preprocessing/output/teddycard_notices_with_embeddings.json', 'r', encoding='utf-8'); data = json.load(f); print('첫 번째 문서에 structured 있음:', 'structured' in data[0] if data else False)"
```

### 2. 문서 수 확인

모든 파일의 문서 수가 일치하는지 확인:
- `teddycard_notices.json`: 2개
- `teddycard_notices_enriched.json`: 2개
- `teddycard_notices_with_embeddings.json`: 2개

## 다음 단계

1. ✅ `12_propagate_structured.py` 실행 완료
2. ✅ 파일 상태 확인 완료
3. ➡️ DB 적재 진행 (`backend_dev/app/db/scripts/`)

## 주의사항

1. **백업 권장**: 실행 전 원본 파일 백업 권장
   ```powershell
   # 백업 예시 (선택사항)
   Copy-Item -Path "data-preprocessing_dev/preprocessing/output/*.json" -Destination "data-preprocessing_dev/preprocessing/output/backup/" -Recurse
   ```

2. **파일 존재 확인**: Target 파일이 존재하지 않으면 경고만 출력하고 계속 진행

3. **id 일치 확인**: Source와 Target 파일의 `id`가 일치하지 않으면 해당 문서는 업데이트되지 않음

## 문제 해결

### 문제: "파일이 존재하지 않습니다" 경고

**원인**: Target 파일이 아직 생성되지 않았을 수 있음

**해결**: 
- `06_generate_embeddings.py`를 먼저 실행하여 `_with_embeddings.json` 파일 생성
- 또는 해당 파일이 필요 없는 경우 스크립트에서 제외

### 문제: "0개 업데이트, 0개 추가"

**원인**: 
- Source 파일에 `structured` 필드가 없음
- Source와 Target의 `id`가 일치하지 않음

**해결**:
- Source 파일에 `structured` 필드가 있는지 확인
- `id` 필드가 일치하는지 확인
