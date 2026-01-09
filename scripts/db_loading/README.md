# 하나카드 데이터 DB 적재 스크립트

## 개요

하나카드 전처리 데이터를 PostgreSQL + pgvector 데이터베이스에 적재하는 스크립트 모음입니다.

## 파일 구조

```
scripts/db_loading/
├── generate_embeddings_hana.py    # 임베딩 생성
├── load_hana_to_db.py              # DB 적재
├── verify_db_load.py               # 검증
└── README.md                       # 이 파일
```

## 사전 준비

### 1. 환경 설정

**상세 가이드**: `docs/04_dev/02_db/01_개발환경_설정_가이드.md` 참고

**요약**:
1. Conda 환경 생성 (`conda env create -f ../environment.yml`)
2. 패키지 설치 (`pip install -r ../requirements.txt`)
3. Docker로 PostgreSQL + pgvector 실행
4. `.env` 파일 설정

### 2. DB 스키마 생성

```bash
# DBeaver에서 실행 또는
psql -h localhost -U callact_admin -d call_act_db -f ../../data-preprocessing/scripts/db_setup.sql
```

## 실행 순서

### 1단계: 임베딩 생성

**테스트용 (100-200개)**:
```bash
conda activate final_env
cd scripts/db_loading
python generate_embeddings_hana.py --limit 200
```

**전체 데이터**:
```bash
python generate_embeddings_hana.py
```

**재시작 (중단된 경우)**:
```bash
python generate_embeddings_hana.py --resume
```

**출력 파일**: `data-preprocessing/data/hana/hana_vectordb_with_embeddings.json`

### 2단계: DB 적재

**테스트용 (100-200개)**:
```bash
python load_hana_to_db.py --limit 200
```

**전체 데이터**:
```bash
python load_hana_to_db.py
```

**옵션**:
- `--skip-consultations`: consultations 테이블 적재 건너뛰기
- `--skip-documents`: consultation_documents 테이블 적재 건너뛰기

### 3단계: 검증

```bash
python verify_db_load.py
```

**유사도 검색 테스트 포함**:
```bash
python verify_db_load.py --test-search "카드 분실 신고"
```

## 실행 예시

### 전체 파이프라인 (테스트용)

```bash
# 1. 임베딩 생성 (200개)
python generate_embeddings_hana.py --limit 200

# 2. DB 적재 (200개)
python load_hana_to_db.py --limit 200

# 3. 검증
python verify_db_load.py
```

### 전체 데이터 처리

```bash
# 1. 임베딩 생성 (전체, 약 40분 소요)
python generate_embeddings_hana.py

# 2. DB 적재 (전체, 약 10분 소요)
python load_hana_to_db.py

# 3. 검증
python verify_db_load.py
```

## 환경 변수

`.env` 파일에 다음 변수 설정:

```env
# OpenAI
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_USER=callact_admin
DB_PASSWORD=callact_pwd1
DB_NAME=call_act_db

# 설정
EMBEDDING_BATCH_SIZE=100
DB_LOAD_BATCH_SIZE=100
```

## 트러블슈팅

### 임베딩 생성 중 API 에러

**증상**: `openai.RateLimitError`

**해결**:
- 재시도 로직이 자동으로 처리
- `EMBEDDING_REQUEST_DELAY` 증가 (기본값: 0.5초)

### DB 연결 실패

**증상**: `psycopg2.OperationalError`

**해결**:
1. Docker 컨테이너 실행 확인: `docker ps`
2. `.env` 파일의 DB 정보 확인
3. 포트 충돌 확인: `5432` 포트 사용 중인지 확인

### Foreign Key 제약 조건 위반

**증상**: `psycopg2.IntegrityError: insert or update on table "consultation_documents" violates foreign key constraint`

**해결**:
- `consultations` 테이블을 먼저 적재해야 함
- `--skip-consultations` 옵션 사용하지 않기

## 참고 문서

- 개발 환경 설정: `docs/04_dev/02_db/01_개발환경_설정_가이드.md`
- DB 적재 설계: `docs/04_dev/02_db/00_hana_db_loading_설계.md`
- ERD 스키마: `data-preprocessing/docs/erd_diagram/CALL_ACT_ERD_Schema_설명.md`


