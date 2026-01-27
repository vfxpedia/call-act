# CALL:ACT DB 초기화 및 적재 가이드

**작성일**: 2026-01-21
**최종 수정일**: 2026-01-24
**작성자**: CALL:ACT Team

---

## 빠른 시작 (통합 스크립트)

### 사전 조건

1. **초기 환경 설정이 완료되어야 합니다**: `backend_dev/docs/SETUP.md` 참고
   - conda 환경 생성 및 활성화: `conda activate final_env`
   - 패키지 설치: `pip install -r requirements.txt`
   - `.env` 파일 생성 및 `DB_PORT=5555` 설정

2. **Docker 컨테이너 실행 중이어야 합니다**

### 전체 DB 설정

`.env` 파일에 `DB_PORT=5555`가 설정되어 있으면:

```bash
cd backend_dev/app/db/scripts

# 전체 설정 (스키마 + 데이터)
python 01_setup_callact_db.py

# 스키마만 생성 (데이터 적재 없이)
python 01_setup_callact_db.py --skip-employees --skip-hana --skip-keywords --skip-teddycard

# 검증만 실행
python 01_setup_callact_db.py --verify-only
```

> **참고**: `01_setup_callact_db.py`가 전체 오케스트레이터입니다.
> 모든 테이블 생성, 데이터 적재, 검증을 한 번에 처리합니다.
>
> VSCode, Cursor, Windows CMD, PowerShell 어디서든 실행 가능합니다.

---

## 개요

PostgreSQL + pgvector 데이터베이스에 전체 데이터를 초기화하고 적재하는 통합 가이드입니다.

### 현재 DB 상태 (2026-01-24 기준)

| 테이블 | 건수 | 설명 |
|--------|------|------|
| card_products | 398 | 테디카드 카드 상품 |
| consultation_documents | 6,533 | 상담 문서 (임베딩 포함) |
| consultations | 6,533 | 상담 이력 |
| customers | 2,500 | 고객 정보 (페르소나 포함) |
| employees | 70 | 상담사 정보 |
| employee_learning_analytics | 0 | 상담사 학습 분석 데이터 |
| keyword_dictionary | 2,483 | 키워드 사전 |
| keyword_synonyms | 450 | 동의어 사전 |
| notices | 52 | 공지사항 |
| recording_download_logs | 0 | 녹취 파일 다운로드 이력 |
| service_guide_documents | 1,273 | 서비스 가이드 문서 |
| simulation_results | 0 | 시뮬레이션 결과 |
| simulation_scenarios | 5 | 시뮬레이션 시나리오 템플릿 |
| audit_logs | 0 | 시스템 감사 로그 |

---

## 사전 준비

### 1. Docker 환경 확인

```bash
# Docker 컨테이너 상태 확인
# Windows CMD:
docker ps | findstr callact

# Linux/Mac:
# docker ps | grep callact

# 실행 중이 아니면 시작
cd backend_dev/docker
docker-compose up -d
```

### 2. 연결 정보

| 항목 | 값 | 비고 |
|------|-----|------|
| Host | localhost | |
| **Port** | **5555** | 5432 아님! (Windows 동적 포트 회피) |
| User | callact_admin | |
| Password | callact_pwd1 | |
| Database | callact_db | |

### 3. 패키지 설치

> **참고**: `backend_dev/requirements.txt`에 모든 패키지가 포함되어 있습니다.
> `SETUP.md`에 따라 `pip install -r requirements.txt`를 실행했다면 추가 설치 불필요.

---

## 전체 실행 순서

### Phase 1: DB 초기화 (처음부터 시작하는 경우)

```bash
# Docker 볼륨 삭제 후 재시작 (데이터 완전 초기화)
cd backend_dev/docker
docker-compose down -v
docker-compose up -d

# 컨테이너 healthy 상태 확인 (약 10초 대기)
docker ps
```

### Phase 2: 스키마 생성 (01~03)

```bash
cd backend_dev/app/db/scripts

# 01. 기본 테이블 생성
python 01_setup_callact_db.py

# 02~03. SQL 스키마 실행
python -c "
import psycopg2
conn = psycopg2.connect(host='localhost', port=5555, user='callact_admin', password='callact_pwd1', database='callact_db')
cursor = conn.cursor()
for sql_file in ['02_setup_tedicard_tables.sql', '03_setup_keyword_dictionary.sql']:
    with open(sql_file, 'r', encoding='utf-8') as f:
        cursor.execute(f.read())
    print(f'[OK] {sql_file}')
conn.commit()
conn.close()
"
```

### Phase 3: 하나카드 데이터 적재 (02~04)

> **임베딩 완료**: `hana_vectordb_with_embeddings.json`이 이미 배포되어 있습니다.
> 02_generate_embeddings_hana.py 실행은 **불필요**합니다.

```bash
# 03. 하나카드 데이터 적재
python 03_load_hana_to_db.py

# 04. 키워드 사전 적재
python 04_load_keyword_dictionary.py

# 04. 적재 검증
python 04_verify_db_load.py
```

### Phase 4: 테디카드 데이터 적재 (05~06)

```bash
# 05. 테디카드 데이터 적재
python 05_load_teddycard_data.py

# 06. 적재 검증
python 06_verify_teddycard_load.py
```

### Phase 5: Customers 테이블 (07~08)

```bash
# 07. customers 테이블 생성
python -c "
import psycopg2
conn = psycopg2.connect(host='localhost', port=5555, user='callact_admin', password='callact_pwd1', database='callact_db')
cursor = conn.cursor()
with open('07_setup_customers_table.sql', 'r', encoding='utf-8') as f:
    cursor.execute(f.read())
conn.commit()
conn.close()
print('[OK] 07_setup_customers_table.sql')
"

# 08. 고객 데이터 생성 (customersData.json이 없는 경우만)
# python 08_generate_customers_data.py

# 08a. 고객 데이터 DB 적재
python 08a_load_customers_to_db.py
```

**기존 테이블에 신규 컬럼 추가가 필요한 경우:**

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
        print(f'[Added] {col_name}')
conn.commit()
conn.close()
"
```

### Phase 6: 상담 배정 (09)

```bash
# 09. 상담-상담사 배정
python 09_assign_consultations_to_agents.py
```

### Phase 7: 시뮬레이션 교육 시스템 (10)

```bash
# 10. 시뮬레이션 테이블 생성 및 샘플 데이터 적재
python -c "
import psycopg2
conn = psycopg2.connect(host='localhost', port=5555, user='callact_admin', password='callact_pwd1', database='callact_db')
cursor = conn.cursor()
with open('10_setup_simulation_tables.sql', 'r', encoding='utf-8') as f:
    cursor.execute(f.read())
conn.commit()
conn.close()
print('[OK] 10_setup_simulation_tables.sql')
"
```

생성되는 테이블:
- `simulation_scenarios`: 시뮬레이션 시나리오 템플릿 (SIM-001~SIM-005 샘플 포함)
- `simulation_results`: 시뮬레이션 수행 결과
- `employee_learning_analytics`: 상담사별 학습 분석 데이터

### Phase 8: 감사 로그 테이블 (11)

```bash
# 11. 녹취 파일 다운로드 이력 + 시스템 감사 로그 테이블 생성
python -c "
import psycopg2
conn = psycopg2.connect(host='localhost', port=5555, user='callact_admin', password='callact_pwd1', database='callact_db')
cursor = conn.cursor()
with open('11_setup_audit_tables.sql', 'r', encoding='utf-8') as f:
    cursor.execute(f.read())
conn.commit()
conn.close()
print('[OK] 11_setup_audit_tables.sql')
"
```

생성되는 테이블:
- `recording_download_logs`: 녹취 파일 다운로드 이력 (법적 준수용)
- `audit_logs`: 시스템 전체 감사 로그

생성되는 뷰:
- `v_suspicious_downloads`: 이상 다운로드 감지 (1시간 내 10건 이상)
- `v_daily_download_stats`: 일별 다운로드 통계

### Phase 9: 상담 이력 유의미성 로직 (12)

```bash
# 12. 최근 상담 이력 유의미성 판단 함수/뷰 생성
python -c "
import psycopg2
conn = psycopg2.connect(host='localhost', port=5555, user='callact_admin', password='callact_pwd1', database='callact_db')
cursor = conn.cursor()
with open('12_setup_consultation_relevance.sql', 'r', encoding='utf-8') as f:
    cursor.execute(f.read())
conn.commit()
conn.close()
print('[OK] 12_setup_consultation_relevance.sql')
"
```

생성되는 함수:
- `fn_get_consultation_relevance(customer_id, days)`: 상담 이력 유의미성 점수 반환
- `fn_get_customer_persona_relevance(customer_id)`: 고객 성향 정보 유효성 판단
- `fn_find_similar_recent_consultations(customer_id, category, days)`: 동일 카테고리 최근 상담 조회

생성되는 뷰:
- `v_customer_guidance_info`: 상담 가이던스용 고객 정보 (유의미성 포함)
- `v_customer_recent_history`: 최근 90일 상담 이력 요약

### Phase 10: 전체 검증

```bash
# 전체 DB 상태 확인
python 01_setup_callact_db.py --verify-only
```

---

## 파일 구조

```
backend_dev/app/db/scripts/
├── 01_setup_callact_db.py             # 통합 DB 설정 스크립트 (이것만 실행하면 전체 설정)
├── config.py                          # 경로 설정 (ENV_TYPE: dev/prod)
│
├── db_setup.sql                       # 기본 테이블 DDL
├── 02_setup_tedicard_tables.sql       # 테디카드 테이블 DDL
├── 02_generate_embeddings_hana.py     # 임베딩 생성 (배포 완료, 실행 불필요)
├── 03_setup_keyword_dictionary.sql    # 키워드 사전 테이블 DDL
├── 03_load_hana_to_db.py              # 하나카드 데이터 적재
├── 04_load_keyword_dictionary.py      # 키워드 사전 적재
├── 04_verify_db_load.py               # 하나카드 적재 검증
├── 05_load_teddycard_data.py          # 테디카드 데이터 적재
├── 06_verify_teddycard_load.py        # 테디카드 적재 검증
│
├── 07_setup_customers_table.sql       # customers 테이블 DDL
├── 07a_setup_persona_types_table.sql  # 페르소나 유형 테이블
├── 08_generate_customers_data.py      # 고객 데이터 생성 (2,500명)
├── 08a_load_customers_to_db.py        # 고객 데이터 적재
├── 08b_reassign_consultations.py      # 상담-고객 연결
├── 08c_calculate_fcr.py               # FCR 계산
├── 08d_verify_customers.sql           # 고객 데이터 검증
│
├── 09_assign_consultations_to_agents.py  # 상담-상담사 배정
├── 09a_update_agent_statistics.py     # 상담사 통계 업데이트
├── 09b_verify_all_assignments.py      # 배정 검증
│
├── 10_setup_simulation_tables.sql     # 시뮬레이션 테이블 DDL + 샘플 데이터
├── 11_setup_audit_tables.sql          # 감사 로그 테이블 DDL (녹취 다운로드 이력)
├── 12_setup_consultation_relevance.sql # 상담 이력 유의미성 함수/뷰
│
├── 99_verify_db_schema.sql            # 전체 스키마 검증
│
├── README.md                          # 이 문서
├── 08_README_customers.md             # Customers 상세 가이드
└── 08_README_customers_migration.md   # 마이그레이션 가이드

backend_dev/app/db/data/
├── employeesData.json                 # 상담사 데이터 (70명)
└── customersData.json                 # 고객 데이터 (2,500명)
```

---

## 임베딩 관련 안내

### 임베딩 배포 완료

다음 파일들은 이미 임베딩이 완료되어 배포되었습니다:

| 파일 | 위치 | 건수 |
|------|------|------|
| hana_vectordb_with_embeddings.json | data-preprocessing/data/hana/ | 6,533 |
| teddycard_card_products_with_embeddings.json | data-preprocessing/data/teddycard/ | 398 |
| teddycard_service_guide_with_embeddings.json | data-preprocessing/data/teddycard/ | 1,273 |

**따라서 02_generate_embeddings_hana.py 실행은 불필요합니다.**

### 임베딩 재생성이 필요한 경우 (선택)

OpenAI API 키가 있고 임베딩을 재생성해야 하는 경우에만:

```bash
# .env 파일에 OPENAI_API_KEY 설정 필요
python 02_generate_embeddings_hana.py --limit 100  # 테스트
python 02_generate_embeddings_hana.py              # 전체 (약 40분)
```

---

## 고객 페르소나 (8개 유형)

### 일반 고객 (N: Normal) - 60%

| ID | 이름 | 비율 |
|----|------|------|
| N1 | 실용주의형 | 25% |
| N2 | 친화적수다형 | 20% |
| N3 | 신중/보안중시형 | 15% |

### 특수 고객 (S: Special) - 40%

| ID | 이름 | 비율 |
|----|------|------|
| S1 | 급한성격형 | 15% |
| S2 | 꼼꼼상세형 | 10% |
| S3 | 이해부족형 | 7% |
| S4 | 반복민원형 | 5% |
| S5 | 불만형 | 3% |

---

## 시뮬레이션 교육 시스템

### 개요

상담사 교육을 위한 시뮬레이션 시스템입니다. 두 가지 유형의 시뮬레이션을 지원합니다:

1. **우수사례 시뮬레이션** (`best_practice`): 실제 우수 상담 사례를 학습
2. **기본 시나리오 시뮬레이션** (`scenario`): 미리 정의된 시나리오로 연습

### 시나리오 목록 (5개 기본 제공)

| ID | 제목 | 난이도 | 카테고리 |
|----|------|--------|----------|
| SIM-001 | 카드 분실 신고 및 재발급 | 초급 | 카드분실 |
| SIM-002 | 해외 결제 차단 해제 요청 | 중급 | 해외결제 |
| SIM-003 | 포인트 적립 누락 문의 | 초급 | 포인트 |
| SIM-004 | 분할결제 취소 요청 | 중급 | 결제취소 |
| SIM-005 | 이중결제 환불 요청 | 고급 | 이중결제 |

### 평가 기준

| 항목 | 가중치 | 설명 |
|------|--------|------|
| document_usage | 30% | 필수 문서 참조 여부 |
| keyword_coverage | 25% | 필수 키워드 언급 여부 |
| sequence_correctness | 25% | 처리 순서 정확성 |
| customer_satisfaction | 20% | 고객 만족도 |

### 테이블 구조

- **simulation_scenarios**: 시나리오 템플릿 (AI 고객 설정, 평가 기준 포함)
- **simulation_results**: 시뮬레이션 수행 결과 (점수, 피드백, 녹취록)
- **employee_learning_analytics**: 상담사별 학습 분석 (강점/약점, 개선율)

---

## 상담 이력 유의미성 판단

### 개요

최근 상담 이력이 현재 인입 케이스와 관련이 있는지 자동으로 판단합니다.

- **1년 전 상담** → 유의미하지 않음 (outdated)
- **7일~30일 전 상담** → 유의미할 수 있음 (유사 케이스 가능성)
- **고객 성향 파악** 시에도 최근 이력 기준 적용

### 유의미성 레벨

| 경과 일수 | 레벨 | 점수 | 설명 |
|----------|------|------|------|
| 0~7일 | high | 100~65 | 매우 유의미, 동일 이슈 재문의 가능성 높음 |
| 8~30일 | medium | 64~20 | 유의미, 연관성 확인 필요 |
| 31~90일 | low | 19~10 | 약한 연관성 |
| 91일+ | none | 0 | 유의미하지 않음 |

### 사용 예시

```sql
-- 고객의 최근 상담 이력 유의미성 조회
SELECT * FROM fn_get_consultation_relevance('CUST-TEDDY-00001', 30);

-- 고객 성향 정보 유효성 확인
SELECT * FROM fn_get_customer_persona_relevance('CUST-TEDDY-00001');

-- 동일 카테고리 최근 상담 (FCR 실패 여부 포함)
SELECT * FROM fn_find_similar_recent_consultations('CUST-TEDDY-00001', '카드분실', 30);

-- 상담 가이던스용 고객 정보 조회 (활동 상태 포함)
SELECT * FROM v_customer_guidance_info WHERE customer_id = 'CUST-TEDDY-00001';
```

### 활동 상태 (activity_status)

| 상태 | 조건 | 가이던스 |
|------|------|---------|
| new_customer | 상담 이력 없음 | 신규 고객입니다. 친절하게 안내해주세요. |
| recent_active | 7일 이내 상담 | 최근 상담 이력이 있습니다. 이전 문의와 연관될 수 있습니다. |
| active | 30일 이내 상담 | 최근 상담 이력이 있습니다. |
| moderate | 90일 이내 상담 | 상담 이력이 있으나 다소 오래되었습니다. |
| dormant | 365일 이내 상담 | 휴면 고객입니다. 현재 상황 파악 필요. |
| inactive | 365일 초과 | 오랜만에 연락하신 고객입니다. |

---

## 녹취 파일 다운로드 이력 (감사 로그)

### 목적

1. **법적 준수**: 금융권 녹취 파일 관리 의무 (5년 보관, 접근 기록)
2. **보안 강화**: 개인정보 포함 파일 다운로드 추적
3. **감사 추적**: 누가, 언제, 어떤 파일을 다운로드했는지 기록

### 테이블 구조

**recording_download_logs**
- `consultation_id`: 다운로드한 상담 ID
- `downloaded_by`: 다운로드한 상담사 ID
- `download_type`: 파일 유형 (txt, wav, mp3)
- `download_ip`: 다운로드 시점 IP 주소
- `file_name`: 다운로드 파일명
- `downloaded_at`: 다운로드 시각

### 이상 다운로드 감지

```sql
-- 1시간 내 10건 이상 다운로드한 사용자 조회
SELECT * FROM v_suspicious_downloads;

-- 일별 다운로드 통계 (최근 30일)
SELECT * FROM v_daily_download_stats;
```

---

## 트러블슈팅

### 연결 실패: port 5432

```
connection refused (port 5432)
```

**해결**: `.env` 파일에서 `DB_PORT=5555` 설정 확인

```env
# .env 파일
DB_PORT=5555
```

또는 환경 변수를 직접 설정:
```bash
# Windows CMD
set DB_PORT=5555
python [스크립트].py

# PowerShell
$env:DB_PORT="5555"
python [스크립트].py
```

### 테이블이 존재하지 않음

```
relation "customers" does not exist
```

**해결**: SQL 스키마 먼저 실행

```bash
python -c "
import psycopg2
conn = psycopg2.connect(host='localhost', port=5555, user='callact_admin', password='callact_pwd1', database='callact_db')
cursor = conn.cursor()
with open('07_setup_customers_table.sql', 'r', encoding='utf-8') as f:
    cursor.execute(f.read())
conn.commit()
conn.close()
"
```

### customersData.json 없음

```bash
python 08_generate_customers_data.py
```

### 윤년 날짜 오류 (ValueError)

2026-01-23 수정 완료. 최신 버전 사용 시 문제 없음.

---

## 환경 변수 설정

`.env` 파일 또는 환경 변수:

```env
DB_HOST=localhost
DB_PORT=5555
DB_USER=callact_admin
DB_PASSWORD=callact_pwd1
DB_NAME=callact_db

# 임베딩 재생성 시에만 필요
OPENAI_API_KEY=your_key_here
```

---

## 참고 문서

- 개발 규칙: `docs/00_rules/01_dev_rules.md`
- Customers 상세: `08_README_customers.md`
- 마이그레이션: `08_README_customers_migration.md`
- 시뮬레이션 시스템 설계: `docs/04_dev/05_Simulation/Phase_12_DB_Simulation.md`

---

## 버전 이력

| 날짜 | 변경 내용 |
|------|----------|
| 2026-01-24 | 01_setup_callact_db.py 통합 오케스트레이터로 정리, Windows CMD 호환성 개선 (grep → findstr) |
| 2026-01-23 | 감사 로그 테이블 추가 (11_setup_audit_tables.sql), 상담 이력 유의미성 로직 추가 (12_setup_consultation_relevance.sql), 시뮬레이션 교육 시스템 테이블 추가 (10_setup_simulation_tables.sql) |
| 2026-01-23 | 통합 가이드 작성, 포트 5555 반영, 임베딩 배포 완료 명시, 페르소나 8개로 정리 |
| 2026-01-21 | 초기 README 작성 |
