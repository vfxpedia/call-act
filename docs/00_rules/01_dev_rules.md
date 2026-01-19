# 개발 규칙 (Development Rules)

**작성일**: 2025-01-05  
**최종 수정일**: 2026-01-13  
**대상**: 프로젝트 개발자 및 LLM  
**목적**: 코드 및 문서 작성의 일관성, 통일성 확보

---

## 중요 문서 참조

**⚠️ 필수 숙지**: 
- **[개발 환경 동기화 규칙](./03_개발환경_동기화_룰.md)**: `*_dev` → `*` 동기화 시 경로 오류 방지를 위한 필수 가이드
- **[Git 규칙](./00_git_final.md)**: Git 서브모듈 관리 및 커밋 프로세스
- **[문서 작성 규칙](./00_docs_rules.md)**: 문서 작성 표준

---

## 0. 문서 구조 규칙

### 0.1 개발 문서 위치
- **경로**: `docs/04_dev/{개발프로세스명}/{문서번호}_{문서이름}.md`
- **예시**:
  - `docs/04_dev/data-preprocessing/00_hana_data_schema.md`
  - `docs/04_dev/data-preprocessing/01_hana_preprocess_설명.md`

### 0.2 문서 넘버링 규칙
- 개발 순서에 따라 `00`, `01`, `02...` 순서로 넘버링
- 스키마 정의 → 전처리 설명 → 구현 가이드 순서

### 0.3 문서 작성 원칙
- LLM은 `docs/00_rules/`의 규칙을 따라 일관성 있게 작성
- 모든 개발 관련 문서는 `docs/04_dev/` 하위에 구성

---

## 1. 코드 작성 원칙

### 1.1 일반 원칙
- **반복 코드 지양**: 동일한 로직이 3회 이상 반복되면 함수로 추출
- **구조화**: 관련 기능은 클래스나 모듈로 그룹화
- **가독성 우선**: 성능 최적화보다 코드 이해도 우선 (단, 극단적인 비효율은 제외)

### 1.2 변수명 규칙
```python
# Good - 의미 파악 가능
consultation_data = load_csv()
masked_text = normalize_masking(text)
consultation_count = len(consultations)

# Bad - 너무 짧거나 애매함
d = load_csv()
t = normalize(text)
cnt = len(c)

# Bad - 너무 장황함
consultation_data_loaded_from_csv_file = load_csv()
```

**원칙**:
- 약어는 업계 표준만 사용 (`csv`, `json`, `db`, `id`)
- 한 번에 의미 파악 가능해야 함
- 3~15자 권장

### 1.3 주석 규칙
```python
# Good - 왜(Why) 설명 or 비자명한 로직 설명
def normalize_masking(text: str) -> str:
    # 전화번호 패턴: 10~11자리 연속된 ▲를 [전화번호]로 변환
    # (정규표현식 복잡도 때문에 10자리와 11자리를 별도 처리)
    text = re.sub(r'▲{10,11}', '[전화번호]', text)
    return text

# Bad - 코드 그대로 반복
def normalize_masking(text: str) -> str:
    # text에서 ▲를 [전화번호]로 변환
    text = re.sub(r'▲{10,11}', '[전화번호]', text)
    return text

# Bad - AI스러운 주석
def normalize_masking(text: str) -> str:
    """
    개인정보 마스킹 처리를 수행합니다.

    이 함수는 텍스트에서 개인정보를 의미 기반 태그로 변환합니다.
    주요 기능은 다음과 같습니다:
    1. 전화번호 마스킹
    2. 카드번호 마스킹
    ...
    """
```

**원칙**:
- 함수 docstring은 간결하게 (1~2줄, 긴 설명은 `docs/04_dev/`에)
- 코드 자체로 설명 가능하면 주석 생략
- Why > What > How 순서로 설명

### 1.4 이모지 금지
```python
# Bad
print("✅ 처리 완료")
print("❌ 에러 발생")

# Good
print("[SUCCESS] 처리 완료")
print("[ERROR] 에러 발생")
```

---

## 2. 스켈레톤 코드 작성 절차

### 2.1 절차
1. **요구사항 확인** → 2. **스켈레톤 코드 작성** → 3. **팀원 컨펌** → 4. **구현**

### 2.2 스켈레톤 코드 예시
```python
# skeleton_hana_preprocess.py

import csv
import json
import re
from pathlib import Path
from typing import Dict, List

# ===== 전역 상수 =====
FILLER_WORDS = {'네', '예', '아'}  # 불용어 리스트

# ===== 1. 개인정보 마스킹 =====
def normalize_masking(text: str) -> str:
    """▲ 기호를 의미 태그로 변환"""
    pass

# ===== 2. 불용어 제거 =====
def remove_fillers(text: str) -> str:
    """단순 반응어 제거"""
    pass

# ===== 3. JSON 변환 =====
def preprocess_row(row: Dict, idx: int) -> Dict:
    """CSV 1행을 JSON으로 변환"""
    pass

# ===== 4. 메인 처리 =====
def process_csv_to_json(csv_path: Path, output_dir: Path) -> None:
    """CSV 전체 처리"""
    pass

def main():
    """CLI 엔트리포인트"""
    pass

if __name__ == '__main__':
    main()
```

---

## 3. 문서화 규칙

### 3.1 코드 설명 문서 위치
- **경로**: `docs/04_dev/{개발프로세스명}/{문서번호}_{모듈명}_설명.md`
- **예시**: `docs/04_dev/data-preprocessing/01_hana_preprocess_설명.md`

### 3.2 문서 구조
```markdown
# {모듈명} 설명서

## 1. 목적
이 스크립트의 역할과 왜 필요한지

## 2. 주요 함수
### 2.1 normalize_masking()
- 입력: ...
- 출력: ...
- 동작 원리: ...
- 예시: ...

## 3. 사용법
python preprocess_hana.py

## 4. 주의사항
- ...
```

---

## 4. 프로젝트 구조 및 개발 워크플로우

### 4.0 개발 환경 관리 원칙

**핵심 원칙**: 모든 개발은 `*_dev` 폴더에서 진행하고, 테스트 완료 후 `*` 폴더로 복사하여 팀과 공유합니다.

**⚠️ 중요**: 동기화 시 반드시 경로 참조를 프로덕션 경로로 수정해야 합니다.  
**상세 가이드**: [개발 환경 동기화 규칙](./03_개발환경_동기화_룰.md) 참조

**경로 관리 방법**:
1. **`config.py` 사용** (권장, 우선 사용):
   - 환경 변수(`PREPROCESSING_ENV`)로 경로 전환
   - `dev`: `data-preprocessing_dev/data/teddycard`
   - `prod`: `data-preprocessing/data/teddycard`
   - **개발 환경 기본값**: `ENV_TYPE = os.getenv('PREPROCESSING_ENV', 'dev').lower()`
   - **프로덕션 환경 기본값**: `ENV_TYPE = os.getenv('PREPROCESSING_ENV', 'prod').lower()`
   - **이점**: 동기화 시 경로 수정 불필요, 환경 변수로 쉽게 전환
   - **사용법**: `from config import OUTPUT_DIR, DATA_DIR`
   
2. **하드코딩 경로** (지양, config.py 사용 불가능한 경우만):
   - 복사 시 직접 수정: `data-preprocessing_dev` → `data-preprocessing`
   - `backend_dev` → `backend`
   - `preprocessing` → `preprocess` (폴더 구조에 맞춰)
   - **예외**: 양방향 지원 스크립트(프로덕션 경로 우선, 개발 경로 대체)는 하드코딩 허용

**서브모듈 구조**:
- **메인 레포**: `call-act` (개인 Git)
- **서브모듈**: `data-preprocessing`, `backend`, `frontend` (팀 레포)
- **개인 개발**: `*_dev` 폴더 (메인 레포 내부)

**동기화 시 주의사항**:
- ❌ `backend_dev` 경로가 `backend`에 남아있으면 안 됨
- ❌ `data-preprocessing_dev` 경로가 `data-preprocessing`에 남아있으면 안 됨
- ❌ `config.py` 기본값이 `'dev'`로 설정되면 안 됨 (프로덕션에서는 `'prod'`)
- ✅ 문서에서 개발 환경을 설명하는 경우는 예외

### 4.1 프로젝트 폴더 구조

**루트 프로젝트 폴더**:
- 워크스테이션: `call-act`
- 노트북: `4th`

**서브 모듈 (팀 레포지토리)**:
- `data-preprocessing`: 데이터 전처리 팀 레포
- `backend`: 백엔드 팀 레포
- `frontend`: 프론트엔드 팀 레포

**개인 개발 폴더**:
- `data-preprocessing_dev`: 개인 데이터 전처리 개발
- `backend_dev`: 개인 백엔드 개발
- `frontend_dev`: 개인 프론트엔드 개발

### 4.2 개발 워크플로우 원칙

**기본 원칙**:
1. **개인 개발**: `*_dev` 폴더에서 개발 진행
2. **팀 공유**: 테스트 완료 후 `*` 폴더로 복사하여 커밋
3. **팀원 코드 수정 금지**: 다른 팀원이 작업한 내용은 원칙적으로 수정 금지
   - 수정이 필요한 경우: 사용자(담당자) 요구에 따라 진행
   - 버그 발견 시: 이슈 등록 후 담당자 확인

**개발 → 팀 공유 프로세스**:
1. `*_dev` 폴더에서 개발 및 테스트
2. 완료된 파일을 `*` 폴더로 복사
3. **경로 수정 (필수)**:
   - 하드코딩 경로: `backend_dev` → `backend`, `data-preprocessing_dev` → `data-preprocessing`
   - `config.py` 기본값: `'dev'` → `'prod'`
   - 문서 경로 예시: `backend_dev` → `backend`
4. **동기화 후 검증** (필수):
   - grep으로 경로 확인: `grep -r "backend_dev" backend/`
   - `config.py` 기본값 확인
   - 문서 경로 확인
5. Git 커밋 (서브모듈 및 메인 레포 동기화)

**⚠️ 중요**: 동기화 시 경로 참조를 반드시 프로덕션 경로로 수정해야 합니다.  
**상세 체크리스트**: [개발 환경 동기화 규칙](./03_개발환경_동기화_룰.md) 참조

**경로 관리 원칙**:
- `config.py` 사용: 환경 변수(`PREPROCESSING_ENV`) 또는 기본값으로 경로 전환
  - `dev`: `data-preprocessing_dev/data/teddycard` (개발 환경)
  - `prod`: `data-preprocessing/data/teddycard` (프로덕션 환경)
- 하드코딩 경로: 복사 시 `data-preprocessing_dev` → `data-preprocessing` 직접 수정

### 4.3 문서화 규칙

**3단계 문서화 구조**:

1. **진행 과정 문서** (`docs/04_dev/`):
   - 모든 진행 과정과 이슈 기록
   - `docs/00_rules/` 규칙 준수
   - 폴더별로 정리 (예: `docs/04_dev/02_db/`)

2. **정리된 전문 문서** (`*_dev/docs/`):
   - 1번 문서를 바탕으로 프로세스 정리
   - 사용자 요구 시 작성
   - 전문적이고 체계적인 문서

3. **팀 공유 문서** (`*/docs/`):
   - 2번 문서 중 팀원에게 공유할 핵심 내용만
   - 최소한의 필수 정보 포함

### 4.4 환경 변수 관리

**`.env` 파일 관리 원칙**:
- 메인 `.env`: 프로젝트 루트(`call-act/`)에서 관리
- 각 레포지토리: `.env.example`을 복사하여 `.env` 생성
- `.env.example`: 비밀번호 등 민감 정보 제외 (템플릿만 제공)
- Git 커밋: `.env` 파일은 절대 커밋하지 않음

**예시**:
```bash
# 프로젝트 루트에서
cp .env.example .env
# .env 파일에 실제 값 입력

# 각 레포지토리에서
cd backend
cp .env.example .env
# 또는 프로젝트 루트 .env 참조
```

## 5. Git 규칙

### 5.1 프로젝트 구조 (서브모듈)

**메인 레포지토리**: `call-act` (개인 Git)
- 프로젝트 전체 구조 관리
- 서브모듈 포인터 관리

**서브모듈 (팀 레포지토리)**:
- `data-preprocessing`: 데이터 전처리 팀 레포
- `backend`: 백엔드 팀 레포
- `frontend`: 프론트엔드 팀 레포

**개인 개발 폴더**:
- `data-preprocessing_dev`: 개인 전처리 개발
- `backend_dev`: 개인 백엔드 개발
- `frontend_dev`: 개인 프론트엔드 개발

### 5.2 브랜치 전략

**현재 진행 중인 브랜치**:
- `data-preprocessing`: `feat/preprocessing-hana` → `feat/data-merge`
- `backend`: `feat/collact_db`
- `frontend`: `feat/ui-main`

### 5.3 Git 커밋 프로세스

**서브모듈 커밋**:
```bash
# 1. 서브모듈 폴더로 이동
cd data-preprocessing

# 2. 변경사항 확인
git status

# 3. 파일 추가
git add data/teddycard/
git add preprocess/teddycard/
git add docs/teddycard_preprocessing/

# 4. 커밋
git commit -m "feat: 테디카드 전처리 데이터 및 스크립트 추가

- 전처리 완료 파일 (with_embeddings.json 3개)
- 키워드 사전 파일 (keywords_dict_v2_with_patterns.json)
- 전처리 스크립트 (00~17번)
- config.py (ENV_TYPE='prod' 설정)
- 실행 가이드 문서"

# 5. 푸시
git push origin feat/teddycard-data
```

**메인 레포지토리 서브모듈 포인터 업데이트**:
```bash
# 메인 레포 루트에서
git add data-preprocessing
git commit -m "chore: data-preprocessing 서브모듈 업데이트 (테디카드 데이터)"
git push
```

### 5.4 절대 금지
- **다른 팀원 코드 수정 금지** (버그 발견 시 이슈 등록)
- 본인 작업 폴더 외 수정 금지
- `.env` 파일 커밋 금지
- 서브모듈 포인터만 업데이트하고 서브모듈 내부 파일을 직접 수정하지 않기

### 5.5 작업 폴더 구조
```
preprocess/
├── hana/          # 홍길동 작업
├── samsung/       # 김철수 작업 (수정 금지!)
└── special_card/  # 이영희 작업 (수정 금지!)
```

### 5.6 서브모듈 동기화

**서브모듈 커밋 순서**:
1. 서브모듈 폴더로 이동 (`cd data-preprocessing`)
2. 변경사항 커밋 (`git add .`, `git commit`, `git push`)
3. 메인 레포 루트로 이동 (`cd ..`)
4. 서브모듈 포인터 업데이트 (`git add data-preprocessing`, `git commit`, `git push`)

**주의사항**:
- 서브모듈 내부 커밋 후 메인 레포에서도 서브모듈 포인터를 업데이트해야 함
- 서브모듈 포인터만 업데이트하고 서브모듈 내부 파일을 직접 수정하지 않기

**상세 가이드**: [테디카드 전처리 데이터 커밋 가이드](../00_git/테디카드_전처리_데이터_커밋_가이드.md)

---

## 6. LLM 코드 작성 시 추가 규칙

### 6.1 함수 길이 제한
- **1개 함수 = 최대 50줄** (초과 시 분리)

### 6.2 매직 넘버 금지
```python
# Bad
if len(text) > 10:
    pass

# Good
MAX_TEXT_LENGTH = 10
if len(text) > MAX_TEXT_LENGTH:
    pass
```

### 6.3 Type Hints 필수
```python
# 모든 함수에 타입 힌트 작성
def process_text(text: str, max_length: int = 100) -> str:
    pass
```

### 6.4 에러 처리
```python
# Bad - 묵시적 에러 무시
try:
    data = json.load(f)
except:
    pass

# Good - 명시적 에러 처리
try:
    data = json.load(f)
except json.JSONDecodeError as e:
    print(f"[ERROR] JSON 파싱 실패: {e}")
    return None
```

---

## 7. 코드 리뷰 체크리스트

- [ ] 반복 코드 3회 이상 → 함수화?
- [ ] 변수명 의미 파악 가능?
- [ ] 주석이 "왜"를 설명?
- [ ] 이모지 사용 안 함?
- [ ] Type Hints 작성?
- [ ] 함수 길이 50줄 이하?
- [ ] 다른 팀원 코드 수정 안 함?
