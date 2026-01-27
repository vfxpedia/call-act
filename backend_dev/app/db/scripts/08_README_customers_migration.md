# 고객 데이터 마이그레이션 가이드

## 개요

기존 `customersData.json`에 신규 필드를 추가하는 마이그레이션 가이드입니다.

### 추가되는 필드 (6개)
| 필드명 | 타입 | 설명 |
|--------|------|------|
| birth_date | string | 생년월일 (YYYY-MM-DD) |
| address | string | 한국 주소 |
| card_issue_date | string | 카드 발급일 (YYYY-MM-DD) |
| card_expiry_date | string | 카드 만료일 (YYYY-MM-DD) |
| current_type_code | string | 현재 주요 유형 코드 (N1, S1 등) |
| type_history | array | 유형 이력 (빈 배열로 초기화) |

## 마이그레이션 실행 방법

### 기본 사용법

```bash
# 기본: customersData.json에 직접 추가 (백업 파일 자동 생성)
python 08_generate_customers_data.py --migrate
```

### 옵션 지정 사용법

```bash
# 입력 파일과 출력 파일 지정
python 08_generate_customers_data.py --migrate --input customersData.json --output customersData_updated.json
```

### 옵션 설명

- `--migrate`: 마이그레이션 모드 활성화
- `--input`: 입력 파일 경로 (기본값: `customersData.json`)
- `--output`: 출력 파일 경로 (기본값: 입력 파일과 동일, 덮어쓰기)

## 실행 예시

### 예시 1: 기본 마이그레이션
```bash
cd backend_dev/app/db/scripts
python 08_generate_customers_data.py --migrate
```

**결과:**
- 기존 `customersData.json` 백업: `customersData_backup_20260122_143025.json`
- 업데이트된 `customersData.json` 생성 (birth_date, address 필드 추가)

### 예시 2: 별도 파일로 저장
```bash
python 08_generate_customers_data.py --migrate --input customersData.json --output customersData_v2.json
```

**결과:**
- 기존 `customersData.json` 백업: `customersData_backup_20260122_143025.json`
- 새 파일 `customersData_v2.json` 생성 (원본은 유지)

## 마이그레이션 과정

1. **기존 데이터 로드**: `customersData.json` 파일 읽기
2. **필드 추가** (누락된 필드만 추가, 기존 값 유지):
   - `birth_date`: `age_group` 기반으로 생성 (재현성 보장)
   - `address`: 한국 주소 생성 (재현성 보장)
   - `card_issue_date`: 카드 발급일 (1~8년 전 랜덤)
   - `card_expiry_date`: 발급일 + 5년
   - `current_type_code`: `_persona_id` 값 복사
   - `type_history`: 빈 배열 `[]`
3. **백업 생성**: 원본 파일 자동 백업 (타임스탬프 포함)
4. **저장**: 업데이트된 데이터 저장

## 재현성 보장

- **랜덤 시드**: `random.seed(42)` 고정
- **고객별 시드**: `customer_id` 기반 해시값으로 추가 시드 생성
- **결과**: 동일한 `customer_id`는 항상 동일한 `birth_date`와 `address` 생성

## 생성 규칙

### 생년월일 (birth_date)
- `age_group` 기반으로 출생 연도 범위 계산
- 예: "30대" → 1987-1996년생 (현재 연도 기준)
- 월일: 1월~12월, 1일~28일 (랜덤, 재현성 보장)

### 주소 (address)
- 시/도별 실제 행정구역 구조 사용
- 예: "서울시 강남구 테헤란로 123"
- 주요 시/도별 구/군/시 및 도로명 매핑 포함

### 카드 발급일/만료일 (card_issue_date, card_expiry_date)
- 발급일: 오늘 기준 1~8년 전
- 만료일: 발급일 + 5년
- 윤년 2월 29일 처리: 2월 28일로 자동 조정

### 고객 유형 코드 (current_type_code)
- `_persona_id` 필드값 복사 (N1, N2, N3, S1~S5 등)

### 유형 이력 (type_history)
- 빈 배열 `[]`로 초기화
- 상담 후 업데이트됨 (08c_calculate_fcr.py에서 처리)

## 주의사항

1. **백업 파일**: 마이그레이션 전 자동으로 백업 파일 생성
2. **덮어쓰기**: `--output` 옵션 없이 실행하면 원본 파일이 덮어쓰기됨
3. **기존 필드**: 이미 `birth_date`나 `address`가 있으면 업데이트하지 않음

## 검증

마이그레이션 후 데이터 확인:

```bash
# JSON 파일 확인
python -c "import json; data = json.load(open('customersData.json', 'r', encoding='utf-8')); print(f'총 {len(data)}명'); print(f'생년월일 있음: {sum(1 for c in data if c.get(\"birth_date\"))}명'); print(f'주소 있음: {sum(1 for c in data if c.get(\"address\"))}명')"
```

## 다음 단계

마이그레이션 완료 후:

1. **DB 신규 컬럼 추가** (기존 테이블이 있는 경우):
   ```bash
   python -c "
   import psycopg2
   conn = psycopg2.connect(host='localhost', port=5555, user='callact_admin', password='callact_pwd1', database='callact_db')
   cursor = conn.cursor()
   columns = [
       ('birth_date', 'DATE'),
       ('address', 'VARCHAR(300)'),
       ('card_issue_date', 'DATE'),
       ('card_expiry_date', 'DATE'),
       ('current_type_code', 'VARCHAR(10)'),
       ('type_history', 'JSONB DEFAULT \'[]\'::jsonb'),
       ('customer_type_codes', 'TEXT[]'),
   ]
   for col_name, col_type in columns:
       cursor.execute('''SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'customers' AND column_name = %s)''', (col_name,))
       if not cursor.fetchone()[0]:
           cursor.execute(f'ALTER TABLE customers ADD COLUMN {col_name} {col_type}')
           print(f'Added: {col_name}')
   conn.commit()
   conn.close()
   "
   ```

2. **DB 적재**:
   ```bash
   DB_PORT=5555 python 08a_load_customers_to_db.py
   ```

3. **검증**:
   ```bash
   DB_PORT=5555 python 08a_load_customers_to_db.py --verify-only
   ```

## 문제 해결

### 오류: 파일을 찾을 수 없습니다
- `--input` 옵션으로 올바른 경로 지정
- 현재 디렉토리 확인: `pwd` (Linux/Mac) 또는 `cd` (Windows)

### 오류: JSON 파싱 실패
- 파일이 올바른 JSON 형식인지 확인
- 파일 인코딩이 UTF-8인지 확인

### 오류: day is out of range for month (ValueError)
- **원인**: 윤년 2월 29일 처리 문제 (2026-01-23 수정 완료)
- **해결**: `08_generate_customers_data.py`의 `generate_card_dates()` 함수에서 `safe_add_years()` 헬퍼 사용

### 오류: PostgreSQL 연결 실패 (port 5432)
- **원인**: Docker 환경에서는 포트 5555 사용
- **해결**: `DB_PORT=5555` 환경변수 설정

```bash
# Docker 컨테이너 포트 확인
docker ps | grep callact

# 결과 예시: 0.0.0.0:5555->5432/tcp
# → 호스트에서는 5555 포트로 접속해야 함
```

## 버전 이력

| 날짜 | 변경 내용 |
|------|----------|
| 2026-01-23 | 윤년 버그 수정, current_type_code/type_history 필드 추가, DB 포트 5555 반영 |
| 2026-01-22 | 최초 작성 (birth_date, address 마이그레이션) |
