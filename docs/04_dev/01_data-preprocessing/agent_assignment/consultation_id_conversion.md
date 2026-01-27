# 상담 ID 변환 문서

## 개요

기존 하나카드 상담 ID 형식(`hana_consultation_20593`)을 새 형식(`CS-EMP001-202601211430`)으로 변환하는 로직입니다.

## ID 형식

### 기존 형식
- **형식**: `hana_consultation_{source_id}`
- **예시**: `hana_consultation_20593`
- **특징**: 
  - 상담사 정보 없음
  - 날짜/시간 정보 없음
  - 단순 순차 번호

### 새 형식
- **형식**: `CS-{EMPLOYEE_ID}-{YYYYMMDDHHMM}`
- **예시**: `CS-EMP001-202601211430`
- **특징**:
  - 상담사 ID 포함 (EMP-001 → EMP001)
  - 날짜/시간 정보 포함 (2026-01-21 14:30 → 202601211430)
  - 총 21자리 (CS- + EMP002 + - + 12자리 날짜시간)

## 변환 로직

### 함수 시그니처
```python
def convert_to_new_consultation_id(
    old_id: str,
    agent_id: str,
    call_start_time: Optional[str] = None,
    created_at: Optional[str] = None
) -> str:
    """
    기존 상담 ID를 새 형식으로 변환
    
    Args:
        old_id: 기존 ID (예: "hana_consultation_20593")
        agent_id: 상담사 ID (예: "EMP-001")
        call_start_time: 통화 시작 시간 (ISO 형식)
        created_at: 생성 시간 (ISO 형식, fallback)
    
    Returns:
        새 형식 ID (예: "CS-EMP001-202601211430")
    """
```

### 변환 단계

#### 1. 상담사 ID 정리
```python
# 대시 제거 (EMP-001 → EMP001)
clean_agent_id = agent_id.replace("-", "")
```

#### 2. 날짜/시간 추출
```python
dt = None

# 1차: call_start_time 사용
if call_start_time:
    try:
        dt = datetime.fromisoformat(call_start_time.replace("Z", "+00:00"))
    except:
        pass

# 2차: created_at 사용 (fallback)
if not dt and created_at:
    try:
        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    except:
        pass

# 3차: 현재 시간 사용 (최후의 수단)
if not dt:
    dt = datetime.now()
```

#### 3. 새 형식 ID 생성
```python
# YYYYMMDDHHMM 형식으로 변환
timestamp_str = dt.strftime("%Y%m%d%H%M")

# 최종 ID 생성
new_id = f"CS-{clean_agent_id}-{timestamp_str}"
```

## 변환 예시

### 예시 1: 정상 케이스
```python
old_id = "hana_consultation_20593"
agent_id = "EMP-001"
call_start_time = "2026-01-21T14:30:00Z"

# 변환 결과
new_id = "CS-EMP001-202601211430"
```

### 예시 2: call_start_time 없음
```python
old_id = "hana_consultation_20594"
agent_id = "EMP-019"
call_start_time = None
created_at = "2026-01-21T15:45:00Z"

# 변환 결과 (created_at 사용)
new_id = "CS-EMP019-202601211545"
```

### 예시 3: 둘 다 없음
```python
old_id = "hana_consultation_20595"
agent_id = "ADMIN-001"
call_start_time = None
created_at = None

# 변환 결과 (현재 시간 사용)
# 실행 시점: 2026-01-21 16:00:00
new_id = "CS-ADMIN001-202601211600"
```

## 적용 시점

### 1. 배정 완료 후
```python
# 상담사 배정 완료
agent_id = assign_agent(...)

# 배정 후 즉시 ID 변환
new_consultation_id = convert_to_new_consultation_id(
    old_id=old_consultation_id,
    agent_id=agent_id,
    call_start_time=row.get("call_start_time"),
    created_at=row.get("created_at")
)
```

### 2. DB 적재 시
```python
# consultations 테이블 적재
consultation_batch.append((
    new_consultation_id,  # 새 형식 ID 사용
    customer_id,
    agent_id,
    ...
))
```

### 3. consultation_documents 매핑
```python
# ID 매핑 저장
old_to_new_id_map[old_consultation_id] = new_consultation_id

# consultation_documents 적재 시 매핑 사용
consultation_id = old_to_new_id_map.get(old_id, old_id)
```

## ID 매핑 저장

### 매핑 딕셔너리
```python
old_to_new_id_map = {
    "hana_consultation_20593": "CS-EMP001-202601211430",
    "hana_consultation_20594": "CS-EMP019-202601211545",
    ...
}
```

### 사용 목적
1. **consultation_documents 매핑**: 문서 테이블의 consultation_id 업데이트
2. **검증**: 변환 결과 확인
3. **디버깅**: 변환 과정 추적

## 주의사항

### 1. 중복 ID 방지
- 동일한 상담사가 동일한 시간에 여러 상담을 받을 경우 중복 가능
- 해결: 밀리초 단위 추가 고려 (필요 시)

### 2. 시간대 처리
- ISO 형식의 시간대 정보 처리 (`Z` → `+00:00`)
- 로컬 시간대 변환 고려

### 3. 날짜/시간 없음
- `call_start_time`과 `created_at`이 모두 없으면 현재 시간 사용
- 실제 상담 시간과 다를 수 있음 (과거 데이터의 한계)

## 기존 데이터와의 호환성

### 하이브리드 방식
- **기존 데이터**: 새 형식으로 변환
- **새 데이터**: 처음부터 새 형식 사용
- **하위 호환성**: 기존 ID 형식도 인식 가능하도록 유지

### 마이그레이션 전략
1. **Phase 1**: 배정 로직 개선 및 ID 변환 함수 추가
2. **Phase 2**: 기존 데이터 변환 (배정 완료 후)
3. **Phase 3**: 새 데이터는 처음부터 새 형식 사용

## 검증 방법

### 1. 변환 결과 확인
```python
# 변환 전후 비교
print(f"{old_id} → {new_id}")
```

### 2. 형식 검증
```python
import re

pattern = r"^CS-[A-Z0-9]+-\d{12}$"
if re.match(pattern, new_id):
    print("✅ 형식 검증 통과")
```

### 3. 중복 확인
```python
# 중복 ID 확인
if new_id in existing_ids:
    print(f"⚠️ 중복 ID 발견: {new_id}")
```

## 참고사항

### 관리자 상담사
- **형식**: `ADMIN-001` → `ADMIN001`
- **예시**: `CS-ADMIN001-202601211430`
- **특징**: 관리자도 동일한 형식 적용

### 향후 개선 방향
1. **밀리초 추가**: 중복 방지를 위한 밀리초 단위 추가
2. **타임존 처리**: 명시적 타임존 정보 포함
3. **버전 관리**: ID 형식 버전 정보 포함
