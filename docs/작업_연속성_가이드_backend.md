# Backend 작업 연속성 가이드

> **작성일**: 2026-02-04
> **목적**: 집에서 작업을 이어가기 위한 종합 가이드

---

## 1. 완료된 작업 내용

### 1.1 DirectCall 고객 정보 실제 DB 연동

| 파일 | 작업 | 설명 |
|------|------|------|
| `app/api/v1/endpoints/customers.py` | **신규 생성** | DirectCall용 고객 API |
| `app/api/v1/routers.py` | 수정 | customers 라우터 등록 |

**API 엔드포인트:**
- `GET /api/v1/customers/random` - 랜덤 고객 조회 (DirectCall 인입 시 사용)
- `GET /api/v1/customers/{customer_id}` - 특정 고객 조회

**핵심 로직:**
```python
# customers.py - persona_types 테이블 JOIN으로 personality_tags, llm_guidance 조회
SELECT
    c.id, c.name, c.phone, c.birth_date, c.address, c.grade,
    c.card_type, c.card_number_last4, c.card_brand,
    c.card_issue_date, c.card_expiry_date,
    c.current_type_code,
    p.personality_tags,
    p.llm_guidance
FROM customers c
LEFT JOIN persona_types p ON c.current_type_code = p.code
ORDER BY RANDOM()
LIMIT 1
```

### 1.2 card_products 테이블 embedding 지원

| 파일 | 작업 | 설명 |
|------|------|------|
| `app/db/scripts/02_setup_tedicard_tables.sql` | 수정 | keywords, embedding 컬럼 및 HNSW 인덱스 추가 |
| `app/db/scripts/modules/load_teddycard.py` | 수정 | embedding 적재 로직 추가 |
| `app/db/scripts/modules/fix_card_products_data.py` | **신규 생성** | 데이터 품질 보완 스크립트 |

**DB 스키마 변경:**
```sql
-- card_products 테이블에 추가된 컬럼
keywords TEXT[],  -- RAG 검색용 키워드 배열
embedding vector(1536),  -- pgvector 확장 타입 (RAG 검색용)

-- HNSW 인덱스
CREATE INDEX idx_card_products_embedding_hnsw
ON card_products USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

### 1.3 Git 커밋 완료

- **브랜치**: `feat/callact_db`
- **커밋**: `2c071c7`
- **PR #153**: main에 머지 완료
- **현재 main**: `7733ade`

---

## 2. 앞으로 작업할 내용

### 2.1 실제 DB 연동 테스트 (미완료)

```bash
# API 테스트
curl http://localhost:8001/api/v1/customers/random
```

**확인 사항:**
- [ ] 랜덤 고객 조회 API 정상 작동
- [ ] personality_tags, llm_guidance 정상 반환
- [ ] Frontend DirectCall 연동 테스트

### 2.2 Frontend 연동

**파일**: `frontend_dev/src/app/pages/RealTimeConsultationPage.tsx`

```typescript
// DirectCall 시 실제 DB에서 고객 정보 조회
const fetchRandomCustomer = async () => {
  const response = await fetch(`${API_BASE_URL}/customers/random`);
  // ...
};
```

### 2.3 card_products 데이터 품질 보완 (선택)

```bash
cd backend_dev/app/db/scripts/modules
python fix_card_products_data.py --report  # 현황 확인
python fix_card_products_data.py --apply   # 실제 적용
```

---

## 3. 집에서 작업 시작 가이드

### 3.1 Git 동기화

```bash
cd C:\SKN_19\project\4th

# 1. root 최신화
git pull origin main

# 2. 서브모듈 동기화
git submodule update --init --recursive

# 3. backend 서브모듈 확인
cd backend
git checkout main
git pull origin main
```

### 3.2 환경 설정

```bash
# 1. 가상환경 활성화
conda activate final_env

# 2. requirements 설치
cd backend_dev
pip install -r requirements.txt
```

### 3.3 Docker 및 DB 시작

```bash
# 1. Docker 컨테이너 시작
cd backend_dev/docker
docker-compose up -d

# 2. DB 연결 확인
docker exec callact_db_container pg_isready -U callact_admin -d callact_db

# 3. (필요시) DB 재적재
cd backend_dev/app/db/scripts
python 01a_setup_callact_db.py
python 01b_populate_mock_data.py
```

### 3.4 Backend 서버 시작

```bash
cd backend_dev
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**주의**: 포트 8000에 다른 프로세스가 있을 수 있으므로 8001 사용 권장

### 3.5 테스트

```bash
# API 테스트
curl http://localhost:8001/api/v1/customers/random

# Swagger 문서
# 브라우저에서 http://localhost:8001/docs 접속
```

---

## 4. Claude AI 페르소나 및 역할

### 4.1 기본 정보

- **모델**: Claude Opus 4.5 (`claude-opus-4-5-20251101`)
- **도구**: Claude Code (Anthropic CLI)
- **지식 기준일**: 2025년 5월

### 4.2 역할 정의

```
당신은 CALL:ACT 프로젝트의 Backend 개발을 지원하는 AI 어시스턴트입니다.

주요 역할:
1. FastAPI 백엔드 개발 지원
2. PostgreSQL + pgvector DB 설계 및 쿼리 작성
3. RAG 파이프라인 구현 지원
4. 코드 리뷰 및 디버깅
5. Git 워크플로우 관리

기술 스택:
- Backend: FastAPI, Uvicorn, Pydantic
- Database: PostgreSQL, pgvector, psycopg2
- AI/ML: OpenAI Embeddings, RAG Pipeline
- DevOps: Docker, Docker Compose
```

### 4.3 작업 스타일

- 코드 변경 전 반드시 파일 읽기
- 변경사항 명확히 설명
- 테스트 가능한 단계별 진행
- 에러 발생 시 원인 분석 후 해결

---

## 5. 개발 워크플로우 규칙 (중요)

### 5.1 backend_dev ↔ backend 동기화 규칙

```
┌─────────────────────────────────────────────────────────────┐
│                    작업 순서 가이드                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 팀 레포(backend) 최신 확인                              │
│     git -C backend fetch origin                             │
│     git -C backend checkout main                            │
│     git -C backend pull origin main                         │
│                                                             │
│  2. 팀 업데이트 → backend_dev 반영                          │
│     # backend의 최신 파일을 backend_dev로 복사              │
│     # 특히 endpoints, modules, scripts 등                   │
│                                                             │
│  3. backend_dev에서 개발 및 테스트                          │
│     cd backend_dev                                          │
│     uvicorn app.main:app --reload --port 8001               │
│                                                             │
│  4. 테스트 완료 후 backend에 반영                           │
│     # backend_dev → backend 파일 복사                       │
│     # 경로 문제 확인 (상대경로 등)                          │
│                                                             │
│  5. backend 커밋 (feature 브랜치)                           │
│     git -C backend checkout -b feat/기능명                  │
│     git -C backend add <파일들>                             │
│     git -C backend commit -m "커밋메시지"                   │
│     git -C backend push -u origin feat/기능명               │
│     ※ Claude Co-Author 금지                                 │
│     ※ main 직접 push 금지                                   │
│                                                             │
│  6. 서브모듈 및 root 동기화                                 │
│     cd .. (root로 이동)                                     │
│     git add backend                                         │
│     git commit -m "chore: backend 서브모듈 업데이트"        │
│     git push origin main                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 절대 금지 사항

| 항목 | 설명 |
|------|------|
| `git push origin main` (backend) | 반드시 feature 브랜치 사용 후 PR |
| Claude Co-Author | 커밋 메시지에 Claude 언급 금지 |
| backend_dev 직접 커밋 | backend_dev는 로컬 개발용, git 추적 안 함 |
| 테스트 없이 배포 | backend_dev에서 충분히 테스트 후 backend 반영 |

### 5.3 파일 동기화 체크리스트

**backend → backend_dev 동기화 시:**
```bash
# 전체 비교
diff -rq backend/app backend_dev/app --exclude="__pycache__"

# 주요 파일 동기화
cp backend/app/main.py backend_dev/app/
cp backend/app/api/v1/routers.py backend_dev/app/api/v1/
cp backend/app/api/v1/endpoints/*.py backend_dev/app/api/v1/endpoints/
cp backend/app/db/scripts/modules/*.py backend_dev/app/db/scripts/modules/
```

**backend_dev → backend 반영 시:**
```bash
# 내가 수정한 파일만 복사
cp backend_dev/app/api/v1/endpoints/customers.py backend/app/api/v1/endpoints/
# ... 등
```

---

## 6. 현재 프로젝트 구조

```
C:\SKN_19\project\4th\
├── backend/              # 팀 레포 (서브모듈) - 커밋 대상
├── backend_dev/          # 로컬 개발용 - 커밋 안 함
├── frontend/             # 팀 레포 (서브모듈)
├── frontend_dev/         # 로컬 개발용
├── data-preprocessing/   # 팀 레포 (서브모듈)
└── docs/                 # 프로젝트 문서
```

---

## 7. 주요 파일 경로 참조

### API 엔드포인트
- `backend_dev/app/api/v1/endpoints/customers.py` - 고객 API
- `backend_dev/app/api/v1/endpoints/followup.py` - 후처리 API
- `backend_dev/app/api/v1/endpoints/education.py` - 교육 API
- `backend_dev/app/api/v1/endpoints/rag_frontend.py` - RAG API

### DB 스크립트
- `backend_dev/app/db/scripts/01a_setup_callact_db.py` - DB 초기화
- `backend_dev/app/db/scripts/01b_populate_mock_data.py` - Mock 데이터 적재
- `backend_dev/app/db/scripts/02_setup_tedicard_tables.sql` - 테디카드 스키마
- `backend_dev/app/db/scripts/modules/load_teddycard.py` - 테디카드 적재

### 설정 파일
- `backend_dev/app/core/config.py` - 환경 설정
- `backend_dev/docker/docker-compose.yml` - Docker 설정

---

## 8. 트러블슈팅

### 8.1 포트 충돌
```bash
# Windows에서 포트 사용 프로세스 확인
netstat -ano | findstr :8000

# 프로세스 종료
taskkill /F /PID <PID>
```

### 8.2 Import 에러
```bash
# backend_dev에서 팀 레포 파일이 누락된 경우
# backend → backend_dev 전체 동기화 필요
diff -rq backend/app backend_dev/app --exclude="__pycache__"
```

### 8.3 DB 연결 실패
```bash
# Docker 컨테이너 상태 확인
docker ps

# 컨테이너 재시작
docker-compose -f backend_dev/docker/docker-compose.yml restart
```

---

## 9. 다음 세션 시작 시 체크리스트

- [ ] Git pull (root, submodules)
- [ ] Docker 컨테이너 실행 확인
- [ ] DB 연결 테스트
- [ ] Backend 서버 시작
- [ ] API 테스트 (`/customers/random`)
- [ ] 이 문서 참고하여 작업 이어가기

---

*문서 끝*
