# Backend와 Backend_dev 구조 비교 분석

**작성일**: 2026-01-13  
**작성자**: CALL:ACT Team  
**버전**: v1.0

---

## 개요

`backend` (팀 레포)와 `backend_dev` (개인 개발 폴더)의 구조를 비교하여 동기화 전략을 수립합니다.

## 1. 폴더 구조 비교

### 1.1 Backend (팀 레포) 구조

```
backend/app/
├── api/
│   └── v1/
│       ├── endpoints/
│       │   └── websocket.py
│       └── routers.py
├── audio/
│   └── whisper.py
├── core/
│   └── config.py
├── crud/
│   ├── create_rdb.py
│   ├── create_vec.py
│   └── read_db.py
├── db/
│   ├── base.py
│   ├── base_vec.py
│   ├── scripts/
│   │   ├── 01_setup_db.py
│   │   └── db_setup.sql
│   └── session.py
├── llm/
│   ├── base.py
│   ├── card_generator.py
│   └── rag_answerer.py
├── main.py
├── rag/
│   ├── cache/
│   │   ├── __init__.py
│   │   └── card_cache.py
│   ├── pipeline.py
│   ├── postprocess/
│   │   ├── __init__.py
│   │   ├── cards.py
│   │   └── keywords.py
│   ├── rag_test.ipynb
│   ├── resources/
│   │   ├── regression_tests.json
│   │   └── vocab.json
│   ├── retriever.py
│   ├── retriever_config.py
│   ├── router.py
│   ├── scripts/
│   │   ├── run_regression.py
│   │   └── vocab_builder.py
│   └── vocab/
│       └── rules.py
├── schemas/
│   └── common.py
└── utils/
```

**Python 파일 개수**: 28개

### 1.2 Backend_dev (개인 개발 폴더) 구조

```
backend_dev/app/
├── api/
│   └── v1/
│       └── endpoints/  (비어있음)
├── core/
│   └── config.py
├── crud/  (비어있음)
├── db/
│   └── scripts/
│       ├── 01_setup_db.py
│       ├── 02_alter_tedicard_tables.sql
│       ├── 02_fix_id_length.sql
│       ├── 02_generate_embeddings_hana.py
│       ├── 02_setup_tedicard_tables.sql
│       ├── 03_load_hana_to_db.py
│       ├── 03_setup_keyword_dictionary.sql
│       ├── 04_load_keyword_dictionary.py
│       ├── 04_verify_db_load.py
│       ├── 05_load_teddycard_data.py
│       ├── 99_fix_employee_data.sql
│       └── db_setup.sql
├── llm/  (비어있음)
├── rag/  (비어있음)
├── schemas/  (비어있음)
└── utils/  (비어있음)
```

**Python 파일 개수**: 6개 (DB 스크립트만)

## 2. 주요 차이점

### 2.1 파일 존재 여부

| 폴더/파일 | Backend | Backend_dev | 비고 |
|----------|---------|-------------|------|
| `app/api/` | ✅ 있음 | ❌ 비어있음 | 복사 필요 |
| `app/audio/` | ✅ 있음 | ❌ 없음 | 복사 필요 |
| `app/core/config.py` | ✅ 있음 | ✅ 있음 | **구조 다름** (병합 필요) |
| `app/crud/` | ✅ 있음 | ❌ 비어있음 | 복사 필요 |
| `app/db/base*.py` | ✅ 있음 | ❌ 없음 | 복사 필요 |
| `app/db/session.py` | ✅ 있음 | ❌ 없음 | 복사 필요 |
| `app/db/scripts/` | ✅ 2개 파일 | ✅ 11개 파일 | **보존 필요** |
| `app/llm/` | ✅ 있음 | ❌ 비어있음 | 복사 필요 |
| `app/rag/` | ✅ 있음 | ❌ 비어있음 | 복사 필요 |
| `app/schemas/` | ✅ 있음 | ❌ 비어있음 | 복사 필요 |
| `app/utils/` | ❌ 비어있음 | ❌ 비어있음 | - |
| `app/main.py` | ✅ 있음 | ❌ 없음 | 복사 필요 |

### 2.2 config.py 차이점

**Backend (`backend/app/core/config.py`)**:
- `.env` 파일을 사용하여 환경 변수 로드
- `python-dotenv` 사용
- 기본값: `localhost`, `callact_admin`, `callact_db`
- OpenAI 설정 포함
- 애플리케이션 설정 포함

**Backend_dev (`backend_dev/app/core/config.py`)**:
- 하드코딩된 DB 정보
- `.env` 파일 미사용
- 원격 서버 정보: `100.80.74.83`, `postgres`, `callact`

**병합 전략**: Backend 버전을 기본으로 사용 (`.env` 파일 사용)

### 2.3 requirements.txt 차이점

**Backend (`backend/requirements.txt`)**:
- 143개 패키지 (완전한 의존성)
- FastAPI, LangChain, OpenAI, Whisper 등 포함
- 프로덕션/개발 환경 모두 지원

**Backend_dev (`backend_dev/requirements.txt`)**:
- 11개 패키지 (최소 의존성)
- DB 적재에 필요한 패키지만 포함

**병합 전략**: Backend 버전을 기본으로 사용 (더 완전한 의존성)

### 2.4 DB 스크립트 차이점

**Backend (`backend/app/db/scripts/`)**:
- `01_setup_db.py` (DB 스키마 생성)
- `db_setup.sql` (SQL 스크립트)

**Backend_dev (`backend_dev/app/db/scripts/`)**:
- `01_setup_db.py` (동일)
- `02_*.sql` (테디카드 테이블 스키마)
- `02_*.py` (임베딩 생성)
- `03_*.sql` (키워드 사전 스키마)
- `03_*.py` (하나카드 데이터 적재)
- `04_*.py` (키워드 사전 적재, 검증)
- `05_*.py` (테디카드 데이터 적재)
- `99_*.sql` (기타 수정)

**보존 전략**: Backend_dev의 모든 DB 스크립트는 절대 삭제하지 않음

## 3. 동기화 전략

### 3.1 복사할 파일/폴더

**전체 복사**:
- `backend/app/api/` → `backend_dev/app/api/`
- `backend/app/audio/` → `backend_dev/app/audio/`
- `backend/app/crud/` → `backend_dev/app/crud/`
- `backend/app/db/base.py` → `backend_dev/app/db/`
- `backend/app/db/base_vec.py` → `backend_dev/app/db/`
- `backend/app/db/session.py` → `backend_dev/app/db/`
- `backend/app/llm/` → `backend_dev/app/llm/`
- `backend/app/rag/` → `backend_dev/app/rag/`
- `backend/app/schemas/` → `backend_dev/app/schemas/`
- `backend/app/main.py` → `backend_dev/app/main.py`

**비교 후 복사**:
- `backend/app/core/config.py` → `backend_dev/app/core/config.py` (Backend 버전 사용)
- `backend/app/db/scripts/db_setup.sql` → `backend_dev/app/db/scripts/` (비교 후 복사)
- `backend/requirements.txt` → `backend_dev/requirements.txt` (Backend 버전 사용)
- `backend/docker/` → `backend_dev/docker/` (비교 후 복사)

### 3.2 보존할 파일/폴더

**절대 삭제/덮어쓰기 금지**:
- `backend_dev/app/db/scripts/02_*.py` (적재 스크립트)
- `backend_dev/app/db/scripts/02_*.sql` (테디카드 테이블 스키마)
- `backend_dev/app/db/scripts/03_*.py` (적재 스크립트)
- `backend_dev/app/db/scripts/03_*.sql` (키워드 사전 스키마)
- `backend_dev/app/db/scripts/04_*.py` (적재/검증 스크립트)
- `backend_dev/app/db/scripts/05_*.py` (적재 스크립트)
- `backend_dev/app/db/scripts/06_*.py` (검증 스크립트 - 작성 예정)
- `backend_dev/app/db/scripts/99_*.sql` (기타 수정)

### 3.3 병합이 필요한 파일

1. **config.py**: Backend 버전 사용 (`.env` 파일 사용)
2. **requirements.txt**: Backend 버전 사용 (더 완전한 의존성)
3. **docker-compose.yml**: Backend 버전을 기본으로 사용, 필요시 병합

## 4. 예상 충돌 및 해결 방안

### 4.1 config.py 충돌

**문제**: Backend_dev는 하드코딩, Backend는 `.env` 사용

**해결**: Backend 버전 사용 (`.env` 파일 사용 권장)

### 4.2 requirements.txt 충돌

**문제**: Backend_dev는 최소 의존성, Backend는 완전한 의존성

**해결**: Backend 버전 사용 (프로덕션 환경 지원)

### 4.3 db_setup.sql 충돌

**문제**: 두 파일이 다를 수 있음

**해결**: 비교 후 Backend 버전 사용, 필요시 Backend_dev의 추가 SQL 스크립트는 별도 파일로 보존

## 5. 다음 단계

1. ✅ 구조 비교 분석 완료 (이 문서)
2. ⏳ 검증 스크립트 작성 (`06_verify_teddycard_load.py`)
3. ⏳ Backend 최신 파일 복사
4. ⏳ 구조 병합 및 충돌 확인
5. ⏳ Backend 브랜치 커밋

---

## 참고 문서

- [Backend 동기화 가이드](./09_Backend_동기화_가이드.md)
- [Backend 커밋 가이드](./10_Backend_커밋_가이드.md)
