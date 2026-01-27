# 통합 DB 설정 가이드 v2.0

**작성일**: 2026-01-24
**작성자**: CALL:ACT Team
**버전**: v2.0

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| v2.0 | 2026-01-24 | 시뮬레이션 교육 테이블, 감사 로그 테이블, 상담 이력 유의미성 함수/뷰 추가 |
| v1.0 | 2026-01-13 | 최초 작성 |

---

## 개요

이 가이드는 `01_setup_callact_db.py` 스크립트를 사용하여 CALL:ACT 프로젝트의 **전체 데이터베이스를 한 번에 설정**하는 방법을 안내합니다.

### ONE-STOP 스크립트 장점

- **단 한 번 실행**으로 모든 테이블 생성 + 데이터 적재 완료
- 단계별 여러 스크립트 실행 불필요
- 실행 전 자동으로 필수 파일 및 설정 확인
- 중복 실행 안전 (`IF NOT EXISTS`, `ON CONFLICT` 사용)
- Windows/Mac 모두 지원

### v2.0 신규 테이블

| 테이블 | 설명 |
|--------|------|
| `simulation_scenarios` | 시뮬레이션 시나리오 템플릿 (5개 기본 제공) |
| `simulation_results` | 시뮬레이션 수행 결과 |
| `employee_learning_analytics` | 상담사별 학습 분석 데이터 |
| `recording_download_logs` | 녹취 파일 다운로드 이력 (법적 준수용) |
| `audit_logs` | 시스템 전체 감사 로그 |

### v2.0 신규 함수/뷰

| 함수/뷰 | 설명 |
|---------|------|
| `fn_get_consultation_relevance()` | 상담 이력 유의미성 점수 반환 |
| `fn_get_customer_persona_relevance()` | 고객 성향 정보 유효성 판단 |
| `fn_find_similar_recent_consultations()` | 동일 카테고리 최근 상담 조회 |
| `v_customer_guidance_info` | 상담 가이던스용 고객 정보 |
| `v_customer_recent_history` | 최근 90일 상담 이력 요약 |
| `v_suspicious_downloads` | 이상 다운로드 감지 |
| `v_daily_download_stats` | 일별 다운로드 통계 |

---

## 1. 사전 준비 체크리스트

### 1.1 필수 조건

- [ ] Docker Desktop 설치 및 실행 중
- [ ] Conda 환경 활성화 (`conda activate final_env`)
- [ ] 패키지 설치 완료 (`pip install -r requirements.txt`)
- [ ] `.env` 파일 생성 및 설정 완료
- [ ] Git LFS 파일 다운로드 완료

### 1.2 Docker 컨테이너 실행

```bash
# backend_dev/docker 디렉토리로 이동
cd backend_dev/docker

# Docker Compose로 PostgreSQL 컨테이너 실행
docker-compose up -d

# 실행 확인
docker ps
```

**확인 포인트:**
- `callact_db_container`가 실행 중인지 확인
- `PORTS` 컬럼에 `0.0.0.0:5555->5432/tcp` 표시 확인

### 1.3 .env 파일 설정

**위치**: `backend_dev/app/db/scripts/.env` (권장)

```env
DB_HOST=localhost
DB_PORT=5555
DB_USER=callact_admin
DB_PASSWORD=callact_pwd1
DB_NAME=callact_db
```

> **중요**: 포트는 반드시 `5555` 사용 (Windows 동적 포트 예약 범위 회피)

---

## 2. 실행 방법

### 2.1 전체 설정 (신규 환경)

```bash
# 1. Conda 환경 활성화
conda activate final_env

# 2. 스크립트 디렉토리로 이동
cd backend_dev/app/db/scripts

# 3. 통합 스크립트 실행 (ONE-STOP)
python 01_setup_callact_db.py
```

**이것만 실행하면 끝!**

### 2.2 기존 v1.0에서 업데이트

이미 v1.0으로 DB를 설정한 경우, 동일하게 실행하면 됩니다:

```bash
python 01_setup_callact_db.py
```

**안전한 이유:**
- `CREATE TABLE IF NOT EXISTS` 사용 → 기존 테이블 유지
- `ON CONFLICT DO UPDATE` 사용 → 기존 데이터 유지
- 새 테이블(시뮬레이션, 감사로그)만 추가됨

### 2.3 완전 초기화 (DB 밀고 새로 시작)

기존 데이터를 모두 삭제하고 처음부터 시작하려면:

```bash
# 1. Docker 볼륨 삭제 후 재시작
cd backend_dev/docker
docker-compose down -v
docker-compose up -d

# 2. 컨테이너 healthy 상태 확인 (약 10초 대기)
docker ps

# 3. 스크립트 실행
cd ../app/db/scripts
python 01_setup_callact_db.py
```

---

## 3. 실행 단계 (12단계)

스크립트 실행 시 터미널에 다음 단계가 표시됩니다:

| 단계 | 설명 | SQL 파일 |
|------|------|----------|
| [1/12] | 기본 DB 스키마 생성 | `db_setup.sql` |
| [2/12] | 테디카드 테이블 생성 | `02_setup_tedicard_tables.sql` |
| [3/12] | 키워드 사전 테이블 생성 | `03_setup_keyword_dictionary.sql` |
| [3-1/12] | 페르소나 유형 테이블 생성 | `07a_setup_persona_types_table.sql` |
| [3-2/12] | 고객 테이블 생성 | `07_setup_customers_table.sql` |
| [3-3/12] | **시뮬레이션 교육 테이블 생성** ⭐ | `10_setup_simulation_tables.sql` |
| [3-4/12] | **감사 로그 테이블 생성** ⭐ | `11_setup_audit_tables.sql` |
| [3-5/12] | **상담 이력 유의미성 함수/뷰 생성** ⭐ | `12_setup_consultation_relevance.sql` |
| [4/12] | 상담사 데이터 적재 | `employeesData.json` |
| [5/12] | 하나카드 데이터 적재 | `hana_*.json` |
| [6/12] | 키워드 사전 데이터 적재 | `keywords_dict_*.json` |
| [7/12] | 테디카드 데이터 적재 | `teddycard_*.json` |
| [12/12] | 데이터 적재 검증 | - |

⭐ = v2.0에서 추가됨

---

## 4. 실행 결과

### 4.1 성공 시 출력

```
============================================================
[SUCCESS] 모든 작업이 완료되었습니다!
[12/12] 완료
============================================================

생성된 테이블:
  - 기본: employees, consultations, consultation_documents
  - 테디카드: service_guide_documents, card_products, notices
  - 키워드: keyword_dictionary, keyword_synonyms
  - 고객: customers, persona_types
  - 시뮬레이션: simulation_scenarios, simulation_results, employee_learning_analytics
  - 감사로그: recording_download_logs, audit_logs

생성된 함수/뷰:
  - fn_get_consultation_relevance(): 상담 이력 유의미성
  - fn_get_customer_persona_relevance(): 고객 성향 유효성
  - v_customer_guidance_info: 상담 가이던스용 고객 정보
  - v_suspicious_downloads: 이상 다운로드 감지
============================================================
```

### 4.2 검증 결과 예시

```
[12/12] 데이터 적재 검증

[1/4] 테이블 존재 확인
  ✅ 모든 테이블 존재: 17개

[2/4] 데이터 개수 확인 및 검증
  ✅ employees: 70건
  ✅ consultations: 6,533건
  ✅ consultation_documents: 6,533건
  ✅ service_guide_documents: 1,273건
  ✅ card_products: 398건
  ✅ notices: 52건
  ✅ keyword_dictionary: 2,483건
  ✅ keyword_synonyms: 450건
  ✅ persona_types: 8건
  ✅ simulation_scenarios: 5건
  ⚠️ simulation_results: 0건 (데이터 없음)
  ⚠️ employee_learning_analytics: 0건 (데이터 없음)
  ⚠️ recording_download_logs: 0건 (데이터 없음)
  ⚠️ audit_logs: 0건 (데이터 없음)

[3/4] 스키마 확인
  ✅ pgvector 확장: 설치됨
  ✅ idx_consultation_documents_embedding_hnsw: 존재
```

> **참고**: `simulation_results`, `employee_learning_analytics`, `recording_download_logs`, `audit_logs`는 운영 중 데이터가 쌓이므로 0건이 정상입니다.

---

## 5. 옵션 사용

### 5.1 옵션 목록

| 옵션 | 설명 |
|------|------|
| `--skip-schema` | 스키마 생성 건너뛰기 |
| `--skip-employees` | 상담사 데이터 적재 건너뛰기 |
| `--skip-hana` | 하나카드 데이터 적재 건너뛰기 |
| `--skip-keywords` | 키워드 사전 적재 건너뛰기 |
| `--skip-teddycard` | 테디카드 데이터 적재 건너뛰기 |
| `--verify-only` | 검증만 실행 |

### 5.2 사용 예시

```bash
# 스키마만 생성 (데이터 적재 없이)
python 01_setup_callact_db.py --skip-employees --skip-hana --skip-keywords --skip-teddycard

# 검증만 실행
python 01_setup_callact_db.py --verify-only

# 스키마 생성 건너뛰고 데이터만 적재
python 01_setup_callact_db.py --skip-schema
```

---

## 6. 문제 해결

### 6.1 "필수 환경 변수가 설정되지 않았습니다"

**원인**: `.env` 파일이 없거나 필수 변수 누락

**해결**:
```bash
cd backend_dev/app/db/scripts
# .env 파일 생성 후 필수 변수 설정
```

### 6.2 "SQL file not found"

**원인**: SQL 파일이 `backend_dev/app/db/scripts/` 디렉토리에 없음

**해결**: 필수 SQL 파일 확인
```bash
ls backend_dev/app/db/scripts/*.sql
```

**필수 SQL 파일 목록:**
- `db_setup.sql`
- `02_setup_tedicard_tables.sql`
- `03_setup_keyword_dictionary.sql`
- `07_setup_customers_table.sql`
- `07a_setup_persona_types_table.sql`
- `10_setup_simulation_tables.sql`
- `11_setup_audit_tables.sql`
- `12_setup_consultation_relevance.sql`

### 6.3 "Failed to connect to database"

**원인**: Docker 컨테이너가 실행되지 않았거나 포트 문제

**해결**:
```bash
# Docker 상태 확인
docker ps

# Windows CMD:
docker ps | findstr callact

# 컨테이너가 없으면 시작
cd backend_dev/docker
docker-compose up -d
```

### 6.4 포트 충돌 (Windows)

**증상**: `bind: An attempt was made to access a socket in a way forbidden`

**해결**:
```cmd
# 예약된 포트 확인
netsh interface ipv4 show excludedportrange protocol=tcp

# 5555 포트가 예약 범위에 있으면 docker-compose.yml에서 다른 포트 사용
```

### 6.5 "일부 데이터 파일을 찾을 수 없습니다"

**해결**:
```bash
# Git LFS 파일 다운로드
cd data-preprocessing
git lfs pull
```

---

## 7. 생성되는 전체 테이블 목록 (17개)

| 카테고리 | 테이블 | 설명 | 예상 건수 |
|----------|--------|------|----------|
| 기본 | `employees` | 상담사 정보 | 70 |
| 기본 | `consultations` | 상담 이력 | 6,533 |
| 기본 | `consultation_documents` | 상담 문서 (임베딩 포함) | 6,533 |
| 테디카드 | `service_guide_documents` | 서비스 가이드 문서 | 1,273 |
| 테디카드 | `card_products` | 카드 상품 정보 | 398 |
| 테디카드 | `notices` | 공지사항 | 52 |
| 키워드 | `keyword_dictionary` | 키워드 사전 | 2,483 |
| 키워드 | `keyword_synonyms` | 동의어 사전 | 450 |
| 고객 | `persona_types` | 페르소나 유형 (8개) | 8 |
| 고객 | `customers` | 고객 정보 | 2,500 |
| 시뮬레이션 ⭐ | `simulation_scenarios` | 시나리오 템플릿 | 5 |
| 시뮬레이션 ⭐ | `simulation_results` | 시뮬레이션 결과 | 0 (운영 중 적재) |
| 시뮬레이션 ⭐ | `employee_learning_analytics` | 학습 분석 | 0 (운영 중 적재) |
| 감사로그 ⭐ | `recording_download_logs` | 녹취 다운로드 이력 | 0 (운영 중 적재) |
| 감사로그 ⭐ | `audit_logs` | 시스템 감사 로그 | 0 (운영 중 적재) |

⭐ = v2.0에서 추가됨

---

## 8. 개별 SQL 스크립트 (참고용)

통합 스크립트가 자동으로 실행하지만, 개별적으로 테스트하고 싶다면:

```bash
# 시뮬레이션 테이블만 생성
python -c "
import psycopg2
conn = psycopg2.connect(host='localhost', port=5555, user='callact_admin', password='callact_pwd1', database='callact_db')
with open('10_setup_simulation_tables.sql', 'r', encoding='utf-8') as f:
    conn.cursor().execute(f.read())
conn.commit()
print('OK')
"

# 감사 로그 테이블만 생성
python -c "
import psycopg2
conn = psycopg2.connect(host='localhost', port=5555, user='callact_admin', password='callact_pwd1', database='callact_db')
with open('11_setup_audit_tables.sql', 'r', encoding='utf-8') as f:
    conn.cursor().execute(f.read())
conn.commit()
print('OK')
"

# 상담 이력 유의미성 함수/뷰만 생성
python -c "
import psycopg2
conn = psycopg2.connect(host='localhost', port=5555, user='callact_admin', password='callact_pwd1', database='callact_db')
with open('12_setup_consultation_relevance.sql', 'r', encoding='utf-8') as f:
    conn.cursor().execute(f.read())
conn.commit()
print('OK')
"
```

---

## 9. 참고 문서

- [DB 스크립트 상세 README](../app/db/scripts/README.md) - 개발자용 상세 문서
- [SETUP.md](./SETUP.md) - 초기 환경 설정
- [Git LFS 가이드](./00_git/Git_LFS_설치_및_사용_가이드.md)

---

## 10. 체크리스트 (신규 팀원용)

### 초기 설정
- [ ] Docker Desktop 설치 및 실행
- [ ] `backend_dev/docker`에서 `docker-compose up -d` 실행
- [ ] Conda 환경 활성화 (`conda activate final_env`)
- [ ] 패키지 설치 (`pip install -r requirements.txt`)
- [ ] `.env` 파일 생성 및 설정
- [ ] Git LFS 초기화 및 파일 다운로드

### DB 설정
- [ ] `cd backend_dev/app/db/scripts`
- [ ] `python 01_setup_callact_db.py` 실행
- [ ] 성공 메시지 확인
- [ ] DBeaver로 테이블 17개 확인

---

**문의**: 문제 발생 시 팀 채널에 에러 로그와 함께 공유해주세요.

---

**마지막 업데이트**: 2026-01-24
