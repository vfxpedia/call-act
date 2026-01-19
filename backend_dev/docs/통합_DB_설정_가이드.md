# 통합 DB 설정 가이드

**작성일**: 2026-01-13  
**작성자**: CALL:ACT Team  
**버전**: v1.0

---

## 개요

이 가이드는 `01_setup_callact_db.py` 스크립트를 사용하여 CALL:ACT 프로젝트의 전체 데이터베이스를 한 번에 설정하고 데이터를 적재하는 방법을 안내합니다.

**이 스크립트의 장점**:
- 단계별로 여러 스크립트를 실행할 필요 없음
- 모든 설정과 데이터 적재를 한 번에 처리
- 실행 전 자동으로 필수 파일 및 설정 확인
- 중복 실행 안전 (ON CONFLICT 사용)

---

## 1. 전제 조건

### 1.1 Docker Desktop 설치 및 실행

**필수**: Docker Desktop이 설치되어 있어야 합니다.

**Windows 설치**:
1. [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/) 다운로드 및 설치
2. 설치 후 Docker Desktop 실행
3. 시스템 트레이에서 Docker 아이콘이 실행 중인지 확인

**설치 확인**:
```bash
docker --version
docker-compose --version
```

**중요**: Docker Desktop이 실행 중이어야 `docker-compose` 명령어가 작동합니다.

### 1.2 PostgreSQL + pgvector 설치 (Docker 사용)

**Docker Compose로 PostgreSQL 실행**:
```bash
# backend_dev/docker 디렉토리로 이동
cd backend_dev/docker

# Docker Compose로 PostgreSQL 컨테이너 실행
docker-compose up -d

# 실행 확인
docker ps
```

**실행 확인**:
- `docker ps` 명령어로 `callact_db_container`가 실행 중인지 확인
- 컨테이너가 실행 중이어야 DBeaver에서 접속 가능

**수동 설치** (Docker 사용 불가 시):
- PostgreSQL 15 이상 설치
- pgvector 확장 설치
- 참고: [개발환경 설정 가이드](../02_db/01_개발환경_설정_가이드.md)

### 1.2 Conda 환경 설정

```bash
# Conda 환경 활성화
conda activate final_env

# Python 버전 확인 (3.11 이상)
python --version

# 필수 패키지 설치 확인
pip list | grep psycopg2
pip list | grep python-dotenv
pip list | grep tqdm
```

### 1.3 .env 파일 설정

**위치**: `backend_dev/app/db/scripts/.env` (권장) 또는 프로젝트 루트 `.env`

**중요**: 
- `.env` 파일은 Git에 커밋되지 않습니다 (`.gitignore`에 포함됨)
- 각 개발자가 로컬에서 직접 생성해야 합니다
- 예외를 방지하기 위해 `backend_dev/app/db/scripts/.env` 위치에 복사해두는 것을 권장합니다

**파일 생성**:
```bash
# backend_dev/app/db/scripts/ 디렉토리에 .env 파일 생성
cd backend_dev/app/db/scripts
# 텍스트 에디터로 .env 파일 생성
```

**필수 변수**:
```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=callact_admin
DB_PASSWORD=your_password_here
DB_NAME=callact_db
```

**참고**: Docker Compose를 사용하는 경우 `docker-compose.yml` 파일의 기본 비밀번호를 사용하거나, 보안을 위해 다른 비밀번호를 설정하세요.

**선택 변수**:
```env
DB_LOAD_BATCH_SIZE=100
DB_COMMIT_INTERVAL=500
```

**참고**: Docker Compose를 사용하는 경우 위 값들이 기본값입니다.

### 1.4 DBeaver 설치 및 접속 설정

**DBeaver 설치**:
1. [DBeaver 공식 사이트](https://dbeaver.io/download/)에서 다운로드
2. Community Edition 설치 (무료)

**PostgreSQL 연결 설정**:
1. DBeaver 실행
2. "새 데이터베이스 연결" 클릭
3. PostgreSQL 선택
4. 연결 정보 입력:
   - **호스트**: `localhost`
   - **포트**: `5432`
   - **데이터베이스**: `callact_db`
   - **사용자 이름**: `callact_admin`
   - **비밀번호**: `your_password_here` (Docker Compose 기본값 또는 .env 파일에 설정한 값)
5. "테스트 연결" 클릭하여 연결 확인
6. "완료" 클릭

**테이블 확인 방법**:
1. DBeaver에서 `callact_db` 연결 선택
2. 왼쪽 트리에서 `callact_db` → `스키마` → `public` → `테이블` 확장
3. 생성된 테이블 목록 확인:
   - `service_guide_documents`
   - `card_products`
   - `notices`
   - `keyword_dictionary`
   - `keyword_synonyms`
   - 기타 테이블들

**SQL 실행 방법**:
1. DBeaver에서 `callact_db` 연결 선택
2. 상단 메뉴에서 "SQL 편집기" → "새 SQL 스크립트" 클릭
3. SQL 파일 내용 복사/붙여넣기
4. `Ctrl+Enter` 또는 실행 버튼 클릭

### 1.5 Git LFS 설정

큰 데이터 파일을 다운로드하기 위해 Git LFS가 필요합니다:

```bash
# Git LFS 설치 확인
git lfs version

# Git LFS 초기화 (처음 한 번만)
git lfs install

# data-preprocessing 레포에서 LFS 파일 다운로드
cd data-preprocessing
git lfs pull
```

**참고**: [Git LFS 설치 및 사용 가이드](../../00_git/Git_LFS_설치_및_사용_가이드.md)

---

## 2. 필수 파일 확인

### 2.1 SQL 스키마 파일

다음 파일들이 `backend_dev/app/db/scripts/` 디렉토리에 있어야 합니다:

- `db_setup.sql` - 기본 DB 스키마
- `02_setup_tedicard_tables.sql` - 테디카드 테이블 생성 (통합본: 테이블 생성 + 컬럼 추가 + ID 길이 수정 포함)
- `03_setup_keyword_dictionary.sql` - 키워드 사전 테이블 생성

**참고**: `02_alter_tedicard_tables.sql`과 `02_fix_id_length.sql`은 `02_setup_tedicard_tables.sql`에 통합되었습니다.

### 2.2 데이터 파일

다음 데이터 파일이 있어야 합니다:

**상담사 데이터**:
- `backend_dev/app/db/scripts/data/employeesData.json` (스크립트와 함께 배포)

**하나카드 데이터** (프로덕션 경로):
- `data-preprocessing/data/hana/hana_rdb_metadata.json`
- `data-preprocessing/data/hana/hana_vectordb_with_embeddings.json`

**테디카드 데이터**:

**프로덕션 경로** (우선):
- `data-preprocessing/data/teddycard/teddycard_service_guides_with_embeddings.json`
- `data-preprocessing/data/teddycard/teddycard_card_products_with_embeddings.json`
- `data-preprocessing/data/teddycard/teddycard_notices_with_embeddings.json`
- `data-preprocessing/data/teddycard/keywords_dict_*.json` (여러 버전 지원)

**개발 경로** (프로덕션 경로에 없을 경우):
- `data-preprocessing_dev/data/teddycard/teddycard_service_guides_with_embeddings.json`
- `data-preprocessing_dev/data/teddycard/teddycard_card_products_with_embeddings.json`
- `data-preprocessing_dev/data/teddycard/teddycard_notices_with_embeddings.json`
- `data-preprocessing_dev/data/teddycard/keywords_dict_*.json` (팀 레포와 동일한 구조)

**참고**: 스크립트는 자동으로 프로덕션 경로를 먼저 확인하고, 없으면 개발 경로를 확인합니다. `config.py`를 통해 경로가 중앙 관리됩니다.

---

## 3. 실행 방법

### 3.1 기본 실행 (전체 설정)

```bash
# 1. Conda 환경 활성화
conda activate final_env

# 2. 스크립트 디렉토리로 이동
cd backend_dev/app/db/scripts

# 3. 통합 스크립트 실행
python 01_setup_callact_db.py
```

**실행 순서** (9단계):
1. 실행 전 체크리스트 확인
2. [1/9] 기본 DB 스키마 생성
3. [2/9] 테디카드 테이블 생성 (통합본)
4. [3/9] 키워드 사전 테이블 생성
5. [4/9] 상담사 데이터 적재 (하나카드 데이터 적재 전 필요)
6. [5/9] 하나카드 데이터 적재
7. [6/9] 키워드 사전 데이터 적재
8. [7/9] 테디카드 데이터 적재
9. [8/9] 데이터 적재 검증
10. [9/9] 완료

### 3.2 옵션 사용

#### 스키마만 생성 (데이터 적재 건너뛰기)

```bash
python 01_setup_callact_db.py --skip-keywords --skip-teddycard
```

#### 키워드 사전만 적재

```bash
python 01_setup_callact_db.py --skip-schema --skip-teddycard
```

#### 테디카드 데이터만 적재

```bash
python 01_setup_callact_db.py --skip-schema --skip-keywords
```

#### 검증만 실행

```bash
python 01_setup_callact_db.py --verify-only
```

### 3.3 옵션 설명

| 옵션 | 설명 |
|------|------|
| `--skip-schema` | 스키마 생성 건너뛰기 (이미 생성된 경우) |
| `--skip-employees` | 상담사 데이터 적재 건너뛰기 |
| `--skip-hana` | 하나카드 데이터 적재 건너뛰기 |
| `--skip-keywords` | 키워드 사전 적재 건너뛰기 |
| `--skip-teddycard` | 테디카드 데이터 적재 건너뛰기 |
| `--verify-only` | 검증만 실행 (스키마 생성 및 데이터 적재 건너뛰기) |

---

## 4. 실행 전 체크리스트

스크립트는 실행 전 자동으로 다음을 확인합니다:

### 4.1 필수 SQL 파일 확인

```
✅ 필수 SQL 파일: 모두 존재
```

파일이 없으면:
```
❌ 필수 SQL 파일 누락:
   - backend_dev/app/db/scripts/db_setup.sql
```

### 4.2 데이터 파일 확인

```
✅ 데이터 파일: 모두 존재
   - Employees: C:\...\employeesData.json
   - Hana RDB: C:\...\hana_rdb_metadata.json
   - Hana VectorDB: C:\...\hana_vectordb_with_embeddings.json
   - Service Guides: C:\...\teddycard_service_guides_with_embeddings.json
   - Card Products: C:\...\teddycard_card_products_with_embeddings.json
   - Notices: C:\...\teddycard_notices_with_embeddings.json
   - Keywords Dict: C:\...\keywords_dict_v2_with_patterns.json
```

일부 파일이 없으면:
```
⚠️ 데이터 파일 일부 누락:
   - employeesData.json
   - hana_rdb_metadata.json
   - teddycard_service_guides_with_embeddings.json
   ⚠️ 상담사 데이터 파일이 없으면 상담사 적재를 건너뜁니다.
   ⚠️ 하나카드 데이터 파일이 없으면 하나카드 적재를 건너뜁니다.
   ⚠️ 테디카드 데이터 파일이 없으면 테디카드 적재를 건너뜁니다.
```

### 4.3 환경 변수 확인

```
✅ 환경 변수: 모두 설정됨
   - DB: localhost:5432/callact_db
```

---

## 5. 실행 결과

### 5.1 성공 시

```
============================================================
[SUCCESS] 모든 작업이 완료되었습니다!
============================================================
```

### 5.2 검증 결과

```
============================================================
[8/9] 데이터 적재 검증
============================================================
  employees: 50건
  consultations: 2,500건
  consultation_documents: 2,500건
  service_guide_documents: 1,234건
  card_products: 567건
  notices: 89건
  keyword_dictionary: 1,456건
  keyword_synonyms: 2,345건
```

---

## 6. 상담사 데이터 적재

### 6.1 개요

상담사 데이터는 `employeesData.json` 파일에서 읽어와 `employees` 테이블에 적재됩니다. 하나카드 데이터 적재 전에 먼저 적재되어야 합니다 (`consultations.agent_id`가 Foreign Key이므로).

### 6.2 데이터 파일 위치

- **파일**: `backend_dev/app/db/scripts/data/employeesData.json`
- **데이터 출처**: `frontend_dev/src/data/mockData.ts`의 `employeesData` 배열
- **데이터 개수**: 50명의 상담사

### 6.3 적재 방법

**자동 적재** (기본 실행):
```bash
python 01_setup_callact_db.py
```

상담사 데이터는 [4/9] 단계에서 자동으로 적재됩니다.

**별도 실행** (이미 스키마가 생성된 경우):
```bash
python 01_setup_callact_db.py --skip-schema --skip-hana --skip-keywords --skip-teddycard
```

### 6.4 이미 데이터가 있는 경우

스크립트는 자동으로 `employees` 테이블에 데이터가 있는지 확인합니다:
- 데이터가 있으면: 적재를 스킵하고 검증만 수행
- 메시지: `[INFO] employees 테이블에 이미 데이터가 있습니다. (건수: 50건) - 적재 스킵`

### 6.5 건너뛰기

상담사 데이터 적재를 건너뛰려면:
```bash
python 01_setup_callact_db.py --skip-employees
```

**주의**: 상담사 데이터를 건너뛰면 하나카드 데이터 적재 시 Foreign Key 오류가 발생할 수 있습니다.

---

## 7. 하나카드 데이터 적재

### 7.1 개요

하나카드 데이터는 `hana_rdb_metadata.json`과 `hana_vectordb_with_embeddings.json` 파일에서 읽어와 `consultations` 및 `consultation_documents` 테이블에 적재됩니다.

### 7.2 데이터 파일 위치

- **RDB 메타데이터**: `data-preprocessing/data/hana/hana_rdb_metadata.json`
- **VectorDB (임베딩 포함)**: `data-preprocessing/data/hana/hana_vectordb_with_embeddings.json`

### 7.3 적재 순서

1. **상담사 데이터 적재** ([4/9] 단계) - 필수
2. **하나카드 데이터 적재** ([5/9] 단계) - 상담사 데이터 후

**이유**: `consultations.agent_id`가 `employees.id`를 참조하는 Foreign Key이므로 상담사 데이터가 먼저 있어야 합니다.

### 7.4 적재 방법

**자동 적재** (기본 실행):
```bash
python 01_setup_callact_db.py
```

하나카드 데이터는 [5/9] 단계에서 자동으로 적재됩니다.

**별도 실행** (이미 스키마가 생성된 경우):
```bash
# 상담사 데이터와 함께 적재
python 01_setup_callact_db.py --skip-schema --skip-keywords --skip-teddycard
```

### 7.5 이미 데이터가 있는 경우

스크립트는 자동으로 `consultations` 테이블에 데이터가 있는지 확인합니다:
- 데이터가 있으면: 적재를 스킵하고 검증만 수행
- 메시지: `[INFO] consultations 테이블에 이미 데이터가 있습니다. (건수: 2,500건) - 적재 스킵`

### 7.6 건너뛰기

하나카드 데이터 적재를 건너뛰려면:
```bash
python 01_setup_callact_db.py --skip-hana
```

---

## 8. 중복 실행 안전성

이 스크립트는 **중복 실행이 안전**합니다:

### 6.1 스키마 생성

- `CREATE TABLE IF NOT EXISTS` 사용
- `CREATE EXTENSION IF NOT EXISTS` 사용
- 이미 존재하는 객체는 무시됨

### 6.2 데이터 적재

- `ON CONFLICT DO UPDATE` 사용
- 동일한 ID가 있으면 업데이트, 없으면 삽입
- 중복 실행해도 데이터가 중복되지 않음

### 6.3 주의사항

- 스키마 변경이 필요한 경우: 기존 테이블을 수동으로 수정하거나 DROP 후 재생성
- 데이터를 완전히 초기화하려면: 테이블을 DROP 후 스크립트 재실행

### 8.3 이미 데이터가 있는 경우 처리

각 테이블에 대해 스크립트는 자동으로 데이터 존재 여부를 확인합니다:
- `employees` 테이블: 상담사 데이터 확인
- `consultations` 테이블: 하나카드 상담 데이터 확인
- 기타 테이블: 기존 로직 유지

데이터가 있으면 적재를 스킵하고 검증만 수행합니다.

---

## 9. 문제 해결

### 7.1 "필수 환경 변수가 설정되지 않았습니다"

**원인**: `.env` 파일이 없거나 필수 변수가 누락됨

**해결**:
1. `backend_dev/app/db/scripts/.env` 파일 생성
2. 필수 변수 설정 (위의 "1.3 .env 파일 설정" 참고)

### 7.2 "SQL file not found"

**원인**: 필수 SQL 파일이 없음

**해결**:
1. `backend_dev/app/db/scripts/` 디렉토리에 필수 SQL 파일 확인
2. 파일이 없으면 `backend_dev` 폴더의 파일을 확인하거나 팀 레포에서 복사

### 7.3 "일부 데이터 파일을 찾을 수 없습니다"

**원인**: 데이터 파일이 없거나 경로가 잘못됨

**해결**:
1. Git LFS 파일 다운로드:
   ```bash
   cd data-preprocessing
   git lfs pull
   ```
2. 파일 경로 확인:
   - 프로덕션: `data-preprocessing/data/teddycard/`
   - 개발: `data-preprocessing_dev/data/teddycard/`
3. 파일이 정말 없으면 `--skip-teddycard` 또는 `--skip-keywords` 옵션 사용

### 7.4 "Failed to connect to database"

**원인**: PostgreSQL이 실행되지 않았거나 연결 정보가 잘못됨

**해결**:
1. PostgreSQL 실행 확인:
   ```bash
   # Docker 사용 시
   docker ps
   
   # 또는 직접 확인
   psql -h localhost -U callact_admin -d callact_db
   ```
2. `.env` 파일의 DB 연결 정보 확인
3. PostgreSQL이 실행 중인지 확인

### 7.5 "column 'embedding' does not exist"

**원인**: 테이블 스키마가 올바르게 생성되지 않음

**해결**:
1. 스키마 재생성:
   ```bash
   python 01_setup_callact_db.py --skip-keywords --skip-teddycard
   ```
2. 또는 수동으로 SQL 파일 실행:
   ```bash
   psql -h localhost -U callact_admin -d callact_db -f 02_setup_tedicard_tables.sql
   ```

### 7.6 "cannot cast type vector to double precision[]"

**원인**: pgvector 확장이 설치되지 않음

**해결**:
1. pgvector 확장 설치:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
2. 또는 `db_setup.sql` 재실행

---

## 10. 상세 검증

데이터 적재 후 상세 검증을 원하면:

```bash
python 06_verify_teddycard_load.py
```

**검증 항목**:
- 데이터 개수 확인
- 임베딩 벡터 검증 (차원, NULL 체크)
- Structured 필드 확인
- 키워드 사전 적재 확인
- 샘플 데이터 확인
- Metadata 필드 확인

**참고**: [Teddycard 데이터 검증 가이드](./08_Teddycard_데이터_검증.md)

---

## 11. 단계별 실행 (선택사항)

통합 스크립트 대신 단계별로 실행하려면:

### 9.1 기본 스키마 생성

```bash
python 01_setup_db.py
```

### 9.2 테디카드 테이블 생성

**방법 1: Python 스크립트 사용 (권장)**

통합 스크립트를 사용하면 자동으로 모든 SQL 파일을 실행합니다:
```bash
python 01_setup_callact_db.py --skip-keywords --skip-teddycard
```

**방법 2: DBeaver 사용 (권장)**

1. DBeaver에서 `callact_db` 연결 선택
2. "SQL 편집기" → "새 SQL 스크립트" 클릭
3. 각 SQL 파일 내용을 복사/붙여넣기하여 실행:
   - `02_setup_tedicard_tables.sql`
   - `02_alter_tedicard_tables.sql`
   - `02_fix_id_length.sql`

**방법 3: psql 명령어 사용 (선택사항)**

Windows에서 psql을 사용하려면 PostgreSQL을 설치하거나 Docker 컨테이너 내부에서 실행해야 합니다:

```bash
# Docker 컨테이너 내부에서 실행
docker exec -it callact_db_container psql -U callact_admin -d callact_db -f /path/to/02_setup_tedicard_tables.sql

# 또는 로컬에 PostgreSQL이 설치된 경우
psql -h localhost -U callact_admin -d callact_db -f 02_setup_tedicard_tables.sql
```

**참고**: 
- Windows에서 psql을 사용하려면 PostgreSQL을 별도로 설치해야 합니다
- Docker를 사용하는 경우 컨테이너 내부에서 실행하거나 DBeaver를 사용하는 것이 더 편리합니다
- Python 스크립트를 사용하면 psql 설치 없이도 모든 작업을 수행할 수 있습니다

### 9.3 키워드 사전 테이블 생성

**방법 1: Python 스크립트 사용 (권장)**
```bash
python 01_setup_callact_db.py --skip-keywords --skip-teddycard
```

**방법 2: DBeaver 사용**
1. DBeaver에서 `03_setup_keyword_dictionary.sql` 파일 내용 복사
2. SQL 편집기에서 실행

**방법 3: psql 명령어 사용**
```bash
# Docker 컨테이너 내부에서 실행
docker exec -it callact_db_container psql -U callact_admin -d callact_db -f /path/to/03_setup_keyword_dictionary.sql
```

### 9.4 키워드 사전 적재

```bash
python 04_load_keyword_dictionary.py
```

### 9.5 테디카드 데이터 적재

```bash
python 05_load_teddycard_data.py
```

### 9.6 검증

```bash
python 06_verify_teddycard_load.py
```

---

## 12. 체크리스트

새로운 팀원이 로컬 환경을 설정할 때:

- [ ] PostgreSQL + pgvector 설치 (Docker 또는 수동)
- [ ] Conda 환경 설정 (`final_env`)
- [ ] `.env` 파일 설정
- [ ] Git LFS 설치 및 초기화
- [ ] 서브모듈 LFS 파일 다운로드
- [ ] 필수 SQL 파일 확인
- [ ] 데이터 파일 확인
- [ ] 통합 스크립트 실행
- [ ] 검증 스크립트 실행

---

## 13. 참고 문서

- [DB 적재 및 배포 통합 작업 README](./README.md)
- [Teddycard 데이터 검증 가이드](./08_Teddycard_데이터_검증.md)
- [Backend 동기화 가이드](./09_Backend_동기화_가이드.md)
- [Git LFS 설치 및 사용 가이드](../../00_git/Git_LFS_설치_및_사용_가이드.md)
- [개발환경 설정 가이드](../02_db/01_개발환경_설정_가이드.md)

---

## 14. 문제 발생 시

위의 문제 해결 방법으로 해결되지 않으면:

1. **팀 채널에 문의**: DB 설정 관련 문제 공유
2. **로그 확인**: 스크립트 실행 시 출력되는 오류 메시지 확인
3. **단계별 실행**: 통합 스크립트 대신 단계별로 실행하여 문제 지점 파악

---

**마지막 업데이트**: 2026-01-13
