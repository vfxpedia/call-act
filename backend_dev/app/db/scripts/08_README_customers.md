# Customers 테이블 설계 및 구현

## 개요

2,500명의 mock 고객 데이터를 생성하고 6,533개 상담 데이터와 FK 연결합니다.
FCR(First Call Resolution) 정확한 계산과 LLM 상담 가이던스를 지원합니다.

## ⚠️ 중요: DB 연결 정보

**Docker 환경에서는 포트 5555 사용** (Windows 동적 포트 예약 범위 회피)

```env
DB_HOST=localhost
DB_PORT=5555        # ← 주의! 5432 아님
DB_USER=callact_admin
DB_PASSWORD=callact_pwd1
DB_NAME=callact_db
```

## 파일 구조

```
backend_dev/app/db/scripts/
├── 07_setup_customers_table.sql       # 테이블 생성 DDL
├── 07a_setup_persona_types_table.sql  # 페르소나 유형 테이블
├── 08_generate_customers_data.py      # 2,500명 고객 생성 (페르소나 포함)
├── 08a_load_customers_to_db.py        # DB 적재
├── 08b_reassign_consultations.py      # 상담 customer_id 재배정
├── 08c_calculate_fcr.py               # FCR 계산 및 통계 업데이트
├── 08d_verify_customers.sql           # 검증 쿼리
├── 08_README_customers.md             # 이 문서
├── 08_README_customers_migration.md   # 마이그레이션 가이드
├── 99_verify_db_schema.sql            # 전체 DB 스키마 검증
└── config.py                          # CUSTOMERS_DATA_FILE 경로

backend_dev/app/db/data/
└── customersData.json                 # 생성된 2,500명 고객 데이터

frontend_dev/src/utils/
└── mask.ts                            # 마스킹 유틸 함수
```

## 실행 순서

### 0. Docker 컨테이너 확인

```bash
# Docker 컨테이너 실행 확인
docker ps | grep callact_db

# 실행 중이 아니면 시작
cd backend_dev/docker
docker-compose up -d
```

### 1. 테이블 생성/업데이트

```bash
cd backend_dev/app/db/scripts

# Python에서 실행 (포트 5555 사용!)
python -c "
import psycopg2
conn = psycopg2.connect(host='localhost', port=5555, user='callact_admin', password='callact_pwd1', database='callact_db')
cursor = conn.cursor()
with open('07_setup_customers_table.sql', 'r', encoding='utf-8') as f:
    cursor.execute(f.read())
conn.commit()
conn.close()
print('Table created/updated successfully')
"
```

**기존 테이블에 신규 컬럼 추가가 필요한 경우:**
```bash
# 신규 컬럼 수동 추가 (테이블이 이미 존재하는 경우)
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
    else:
        print(f'Exists: {col_name}')
conn.commit()
conn.close()
"
```

### 2. 고객 데이터 생성

```bash
cd backend_dev/app/db/scripts
python 08_generate_customers_data.py
```

출력 예시:
```
============================================================
고객 데이터 생성 스크립트
============================================================

[INFO] 2,500명의 고객 데이터 생성 중...
[INFO] 500/2500명 생성 완료
...
[INFO] 총 2500명 생성 완료

[성별 분포]
  female: 1362명 (54.5%) - 목표: 54.5%
  male: 1138명 (45.5%) - 목표: 45.5%

[연령대 분포]
  50대: 708명 (28.3%) - 목표: 28.3%
  ...

[SUCCESS] 고객 데이터 저장 완료: .../customersData.json
```

### 3. DB 적재

```bash
# 포트 5555 환경변수 설정 후 실행
DB_PORT=5555 python 08a_load_customers_to_db.py
```

테스트 모드 (100명만):
```bash
DB_PORT=5555 python 08a_load_customers_to_db.py --limit 100
```

검증만 (데이터 확인):
```bash
DB_PORT=5555 python 08a_load_customers_to_db.py --verify-only
```

### 4. 상담 재배정

```bash
# 미리보기 (DB 변경 없음)
DB_PORT=5555 python 08b_reassign_consultations.py --dry-run

# 실행
DB_PORT=5555 python 08b_reassign_consultations.py
```

### 5. FCR 계산

```bash
# 미리보기 (DB 변경 없음)
DB_PORT=5555 python 08c_calculate_fcr.py --dry-run

# 실행
DB_PORT=5555 python 08c_calculate_fcr.py
```

### 6. 검증

```bash
# 전체 DB 스키마 검증 (Python으로 SQL 실행)
python -c "
import psycopg2
conn = psycopg2.connect(host='localhost', port=5555, user='callact_admin', password='callact_pwd1', database='callact_db')
cursor = conn.cursor()
with open('99_verify_db_schema.sql', 'r', encoding='utf-8') as f:
    cursor.execute(f.read())
conn.close()
print('Verification completed')
"

# 또는 Python 스크립트로 검증
DB_PORT=5555 python 08a_load_customers_to_db.py --verify-only
DB_PORT=5555 python 08b_reassign_consultations.py --verify-only
DB_PORT=5555 python 08c_calculate_fcr.py --verify-only
```

## 고객 페르소나 (8개 유형) - 2026-01-23 확정

### 일반 고객 (N: Normal) - 60%

| ID | 이름 | 비율 | LLM 가이던스 |
|----|------|------|-------------|
| N1 | 실용주의형 | 25% | 바로 본론으로 진행, 간결하고 명확하게 답변 |
| N2 | 친화적수다형 | 20% | 고객 이야기 경청, 공감하며 친근하게 응대 |
| N3 | 신중/보안중시형 | 15% | 본인 확인 절차 상세 안내, 보안 우려 해소 |

### 특수 고객 (S: Special) - 40%

| ID | 이름 | 비율 | LLM 가이던스 |
|----|------|------|-------------|
| S1 | 급한성격형 | 15% | 신속하게 처리, 핵심만 간결하게 전달 |
| S2 | 꼼꼼상세형 | 10% | 단계별 상세 설명, 빠짐없이 안내 |
| S3 | 이해부족형 | 7% | 쉬운 용어로 천천히 설명, 필요시 반복 안내 |
| S4 | 반복민원형 | 5% | 이전 상담 이력 확인, 근본적 해결책 제시 |
| S5 | 불만형 | 3% | 차분하게 경청, 공감 후 해결 방안 제시 |

> **참고**: 60대/70대 고객은 S3(이해부족형) 비율이 30% 높아짐
> **참고**: 10대/20대 고객은 N1(실용주의형) 비율이 20% 높아짐

## 데이터 분포

### 성별 (hana_rdb_metadata.json 분석 기반)
- 여성: 54.5%
- 남성: 45.5%

### 연령대
| 연령대 | 비율 |
|--------|------|
| 10대 | 0.4% |
| 20대 | 5.7% |
| 30대 | 12.6% |
| 40대 | 24.9% |
| **50대** | **28.3%** (최다) |
| 60대 | 21.6% |
| 70대 | 6.5% |

### 상담 횟수별 고객 분포
| 구분 | 고객 비율 | 상담 횟수 |
|------|----------|----------|
| 1회 고객 | 35% | 1회 |
| 일반 고객 | 45% | 2-4회 |
| 다빈도 고객 | 17% | 5-9회 |
| VIP 고객 | 3% | 10회+ |

## FCR (First Call Resolution) 계산

### 정의
- 동일 고객의 동일 카테고리 상담이 7일 이내 재발생하지 않으면 FCR 성공
- 업계 표준 목표: 70% (금융권 평균)

### 계산 예시
```
고객 A: 1/1 카드분실 → 1/5 카드분실 (재문의) → FCR 실패
고객 B: 1/1 카드분실 → 1/15 포인트문의 (다른 카테고리) → FCR 성공
```

## Frontend 마스킹 사용 예시

```typescript
import { maskName, maskPhone, maskCardNumber, maskCustomerInfo } from '@/utils/mask';

// 개별 함수 사용
const maskedName = maskName("김민수");  // "김*수"
const maskedPhone = maskPhone("010-1234-5678");  // "010-****-5678"
const maskedCard = maskCardNumber("5678");  // "****-****-****-5678"

// 고객 정보 전체 마스킹
const customer = {
  id: "CUST-TEDDY-00001",
  name: "김민수",
  phone: "010-1234-5678",
  cardNumber: "1234-5678-9012-3456",
  cardType: "테디카드 프리미엄",
  grade: "VIP"
};

const masked = maskCustomerInfo(customer);
console.log(masked.name.masked);  // "김*수"
console.log(masked.name.original);  // "김민수" (클릭 시 표시)
```

## API 응답 형식

```json
{
  "id": "CUST-TEDDY-00001",
  "name": "김*수",
  "phone": "010-****-5678",
  "cardNumber": "****-****-****-3456",
  "cardType": "테디카드 프리미엄",
  "grade": "VIP",
  "llmGuidance": "김민수 고객님: 프리미엄 서비스로 신속하게 처리해드리겠다고 안내하세요. VIP 고객이므로 최우선으로 응대해주세요.",
  "stats": {
    "totalConsultations": 5,
    "fcrRate": 80
  }
}
```

## 트러블슈팅

### 테이블이 존재하지 않는 경우
```bash
psql -U callact_admin -d callact_db -f 07_setup_customers_table.sql
```

### customersData.json이 없는 경우
```bash
python 08_generate_customers_data.py
```

### FK 제약조건 오류
상담 재배정 스크립트 실행 전에 고객 데이터가 먼저 적재되어야 합니다:
```bash
python 08a_load_customers_to_db.py
python 08b_reassign_consultations.py
```

### 환경 변수 설정
`.env` 파일 또는 환경 변수로 다음 설정이 필요합니다:
```env
DB_HOST=localhost
DB_PORT=5555        # Docker 환경에서는 5555 사용!
DB_USER=callact_admin
DB_PASSWORD=callact_pwd1
DB_NAME=callact_db
```

또는 명령어 실행 시 직접 지정:
```bash
DB_PORT=5555 python 08a_load_customers_to_db.py
```

## Customers 테이블 스키마 (24개 컬럼)

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| id | VARCHAR(50) | 고객 고유 ID (CUST-TEDDY-00001) |
| name | VARCHAR(100) | 고객 실명 (마스킹은 Frontend에서 처리) |
| phone | VARCHAR(20) | 전화번호 (010-1234-5678) |
| gender | VARCHAR(10) | 성별 (male, female, unknown) |
| age_group | VARCHAR(10) | 연령대 (20대, 30대, ...) |
| birth_date | DATE | 생년월일 (YYYY-MM-DD) |
| address | VARCHAR(300) | 주소 |
| grade | VARCHAR(20) | 등급 (VIP, GOLD, SILVER, GENERAL) |
| card_type | VARCHAR(100) | 카드 상품명 (실제 398개 상품 중 선택) |
| card_number_last4 | VARCHAR(4) | 카드번호 마지막 4자리 |
| card_brand | VARCHAR(20) | 브랜드 (visa, mastercard, local) |
| card_issue_date | DATE | 카드 발급일 |
| card_expiry_date | DATE | 카드 만료일 (만료 임박 고객 안내용) |
| current_type_code | VARCHAR(10) | 현재 주요 유형 코드 (N1, S1 등) |
| type_history | JSONB | 유형 이력 (최근 3개) |
| personality_tags | TEXT[] | LLM 가이던스용 특성 태그 |
| communication_style | JSONB | 의사소통 스타일 |
| customer_type_codes | TEXT[] | 복합 유형 배열 |
| llm_guidance | TEXT | LLM 상담 가이드 메시지 |
| total_consultations | INT | 총 상담 횟수 |
| resolved_first_call | INT | FCR 성공 횟수 |
| last_consultation_date | DATE | 최근 상담일 |
| created_at | TIMESTAMP | 생성일시 |
| updated_at | TIMESTAMP | 수정일시 |
