# Backend 동기화 가이드

**작성일**: 2026-01-13  
**작성자**: CALL:ACT Team  
**버전**: v1.0

---

## 개요

`backend_dev` (개인 개발 폴더)의 개발 내용을 보존하면서 `backend` (팀 레포)의 최신 구조를 동기화하는 과정을 안내합니다.

## 전제 조건

- `backend` 서브모듈이 최신 상태로 동기화되어 있어야 함
- `backend_dev`의 DB 적재 스크립트가 완료되어 있어야 함
- `.env` 파일이 올바르게 설정되어 있어야 함

## 동기화 전략

### 원칙

1. **`backend_dev`의 기존 파일은 절대 삭제하지 않음**
2. **`backend`의 최신 파일만 `backend_dev`로 복사**
3. **`backend_dev/app/db/scripts/` 폴더는 보존**

### 복사 대상

**전체 복사**:
- `backend/app/api/` → `backend_dev/app/api/`
- `backend/app/audio/` → `backend_dev/app/audio/`
- `backend/app/crud/` → `backend_dev/app/crud/`
- `backend/app/llm/` → `backend_dev/app/llm/`
- `backend/app/rag/` → `backend_dev/app/rag/`
- `backend/app/schemas/` → `backend_dev/app/schemas/`
- `backend/app/db/base*.py`, `session.py` → `backend_dev/app/db/`
- `backend/app/main.py` → `backend_dev/app/main.py`

**비교 후 복사**:
- `backend/app/core/config.py` → `backend_dev/app/core/config.py` (Backend 버전 사용)
- `backend/requirements.txt` → `backend_dev/requirements.txt` (Backend 버전 사용)
- `backend/docker/` → `backend_dev/docker/` (비교 후 복사)

### 보존 대상

**절대 삭제/덮어쓰기 금지**:
- `backend_dev/app/db/scripts/02_*.py` (적재 스크립트)
- `backend_dev/app/db/scripts/02_*.sql` (테디카드 테이블 스키마)
- `backend_dev/app/db/scripts/03_*.py` (적재 스크립트)
- `backend_dev/app/db/scripts/03_*.sql` (키워드 사전 스키마)
- `backend_dev/app/db/scripts/04_*.py` (적재/검증 스크립트)
- `backend_dev/app/db/scripts/05_*.py` (적재 스크립트)
- `backend_dev/app/db/scripts/06_*.py` (검증 스크립트)
- `backend_dev/app/db/scripts/99_*.sql` (기타 수정)

## 실행 순서

### 1. Backend 최신 상태 확인

```bash
cd backend
git status
git pull origin main
```

### 2. 파일 복사

**PowerShell 사용**:

```powershell
# API 폴더
Copy-Item -Path "backend\app\api\v1\*" -Destination "backend_dev\app\api\v1\" -Recurse -Force

# CRUD 폴더
Copy-Item -Path "backend\app\crud\*" -Destination "backend_dev\app\crud\" -Recurse -Force

# LLM 폴더
Copy-Item -Path "backend\app\llm\*" -Destination "backend_dev\app\llm\" -Recurse -Force

# RAG 폴더
Copy-Item -Path "backend\app\rag\*" -Destination "backend_dev\app\rag\" -Recurse -Force

# Schemas 폴더
Copy-Item -Path "backend\app\schemas\*" -Destination "backend_dev\app\schemas\" -Recurse -Force

# DB 모듈
Copy-Item -Path "backend\app\db\base.py" -Destination "backend_dev\app\db\base.py" -Force
Copy-Item -Path "backend\app\db\base_vec.py" -Destination "backend_dev\app\db\base_vec.py" -Force
Copy-Item -Path "backend\app\db\session.py" -Destination "backend_dev\app\db\session.py" -Force

# Main 파일
Copy-Item -Path "backend\app\main.py" -Destination "backend_dev\app\main.py" -Force

# Config 파일 (Backend 버전 사용)
Copy-Item -Path "backend\app\core\config.py" -Destination "backend_dev\app\core\config.py" -Force

# Requirements (Backend 버전 사용)
Copy-Item -Path "backend\requirements.txt" -Destination "backend_dev\requirements.txt" -Force
```

### 3. 충돌 확인

**config.py**:
- Backend 버전은 `.env` 파일을 사용
- Backend_dev 버전은 하드코딩된 값 사용
- **해결**: Backend 버전 사용 (`.env` 파일 사용 권장)

**requirements.txt**:
- Backend 버전은 완전한 의존성 포함
- Backend_dev 버전은 최소 의존성만 포함
- **해결**: Backend 버전 사용 (프로덕션 환경 지원)

### 4. 테스트

```bash
# Python import 테스트
cd backend_dev
python -c "from app.core import config; print('✅ config import 성공')"
python -c "from app.db import base, base_vec, session; print('✅ db 모듈 import 성공')"
python -c "from app.crud import create_rdb, create_vec, read_db; print('✅ crud 모듈 import 성공')"
python -c "from app.llm import base, card_generator, rag_answerer; print('✅ llm 모듈 import 성공')"
python -c "from app.rag import pipeline, retriever, router; print('✅ rag 모듈 import 성공')"
```

## 주의사항

1. **`backend_dev/app/db/scripts/` 폴더는 절대 건드리지 않음**
2. **중첩된 폴더 구조가 생기지 않도록 주의** (예: `api/api/`)
3. **복사 후 파일 구조 확인**

## 문제 해결

### 중첩된 폴더 구조가 생긴 경우

```powershell
# 중첩된 폴더 제거
Remove-Item -Path "backend_dev\app\api\api" -Recurse -Force
Remove-Item -Path "backend_dev\app\crud\crud" -Recurse -Force
# ... 등등
```

### Import 오류가 발생하는 경우

1. Python 경로 확인
2. `__init__.py` 파일 존재 확인
3. 의존성 패키지 설치 확인 (`pip install -r requirements.txt`)

## 다음 단계

동기화가 완료되면:
1. Backend 브랜치 커밋
2. Docker Hub 업로드
3. AWS Lightsail 배포

---

## 참고 문서

- [Backend 구조 비교 분석](./07_Backend_구조_비교_분석.md)
- [Backend 커밋 가이드](./10_Backend_커밋_가이드.md)
- [개발 룰](../00_rules/01_dev_rules.md)
