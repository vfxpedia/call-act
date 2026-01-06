# 개발 규칙 (Development Rules)

**작성일**: 2025-01-05
**대상**: 프로젝트 개발자 및 LLM
**목적**: 코드 및 문서 작성의 일관성, 통일성 확보

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

## 4. Git 규칙

### 4.1 절대 금지
- **다른 팀원 코드 수정 금지** (버그 발견 시 이슈 등록)
- 본인 작업 폴더 외 수정 금지

### 4.2 작업 폴더 구조
```
preprocess/
├── hana/          # 홍길동 작업
├── samsung/       # 김철수 작업 (수정 금지!)
└── special_card/  # 이영희 작업 (수정 금지!)
```

---

## 5. LLM 코드 작성 시 추가 규칙

### 5.1 함수 길이 제한
- **1개 함수 = 최대 50줄** (초과 시 분리)

### 5.2 매직 넘버 금지
```python
# Bad
if len(text) > 10:
    pass

# Good
MAX_TEXT_LENGTH = 10
if len(text) > MAX_TEXT_LENGTH:
    pass
```

### 5.3 Type Hints 필수
```python
# 모든 함수에 타입 힌트 작성
def process_text(text: str, max_length: int = 100) -> str:
    pass
```

### 5.4 에러 처리
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

## 6. 코드 리뷰 체크리스트

- [ ] 반복 코드 3회 이상 → 함수화?
- [ ] 변수명 의미 파악 가능?
- [ ] 주석이 "왜"를 설명?
- [ ] 이모지 사용 안 함?
- [ ] Type Hints 작성?
- [ ] 함수 길이 50줄 이하?
- [ ] 다른 팀원 코드 수정 안 함?
