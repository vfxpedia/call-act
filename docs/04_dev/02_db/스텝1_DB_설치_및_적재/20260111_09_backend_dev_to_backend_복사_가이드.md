# backend_dev → backend 복사 가이드 (담당자용)

## 메타데이터
- **작성일**: 2026-01-11
- **작성자**: CALL:ACT Team
- **버전**: v1.0
- **상태**: 완료
- **관련 문서**: [담당자 배포 체크리스트](./20260111_06_담당자_배포_체크리스트.md), [README](./README.md)

## 목적

`backend_dev` 폴더에서 개발 및 테스트를 완료한 파일들을 `backend` 폴더(서브모듈, 팀 레포)로 복사하여 팀원들과 공유하는 방법을 안내합니다.

## 폴더 구조 이해

### backend_dev 폴더
- **목적**: 개발 및 테스트용
- **Git 관리**: 개인 Git (call-act 메인 레포)
- **위치**: `call-act/backend_dev/`
- **특징**: 개발 중인 스크립트, 테스트 파일 등

### backend 폴더 (서브모듈)
- **목적**: 팀원들과 공유할 안정적인 파일들
- **Git 관리**: 팀 레포 (별도 서브모듈, `https://github.com/SKN19-Final-1team/backend.git`)
- **위치**: `call-act/backend/`
- **특징**: 검증 완료된 파일만 포함

## 복사 원칙

✅ **복사 대상**: 검증 완료된 파일만
- 테스트 완료
- 오류 없음
- 팀원들이 사용 가능한 상태

❌ **복사 제외**: 
- 임시 파일 (`.log`, `_checkpoint.json` 등)
- 개인 설정 파일 (`.env`, `.env.local` 등)
- 개발 중인 파일 (미완성, 테스트 중)

## 복사할 파일 목록 (제안)

### 필수 파일 (팀원들이 필요)

#### 1. DB 스키마 관련
- `backend_dev/db_loading/db_setup.sql` → `backend/db/db_setup.sql` (또는 적절한 위치)
- `backend_dev/db_loading/setup_db.py` → `backend/scripts/setup_db.py` (또는 적절한 위치)

#### 2. 데이터 적재 스크립트
- `backend_dev/db_loading/load_hana_to_db.py` → `backend/scripts/load_hana_to_db.py`
- `backend_dev/db_loading/verify_db_load.py` → `backend/scripts/verify_db_load.py`

#### 3. 환경 설정
- `backend_dev/docker/docker-compose.yml` → `backend/docker/docker-compose.yml` (또는 병합)
- `backend_dev/environment.yml` → `backend/environment.yml` (또는 병합)
- `backend_dev/requirements.txt` → `backend/requirements.txt` (또는 병합)

#### 4. 문서
- `backend_dev/db_loading/README.md` → `backend/docs/db_loading/README.md` (또는 적절한 위치)

### 선택 파일 (필요시)

#### 임베딩 생성 스크립트 (선택)
- `backend_dev/db_loading/generate_embeddings_hana.py` → `backend/scripts/generate_embeddings_hana.py`
- **참고**: 임베딩 파일(`hana_vectordb_with_embeddings.json`)은 이미 data-preprocessing 레포에 있으므로, 스크립트는 선택사항

## 복사 절차

### 1. 복사 전 확인

✅ **체크리스트**:
- [ ] 복사할 파일들이 테스트 완료되었는지 확인
- [ ] 오류가 없는지 확인
- [ ] 팀원들이 사용할 수 있는 상태인지 확인
- [ ] backend 폴더 구조 확인 (서브모듈)

### 2. backend 폴더 구조 확인

```bash
# backend 폴더 구조 확인
cd backend
ls -la

# 현재 구조 예시:
# backend/
#   ├── app/
#   ├── docker/
#   ├── docs/
#   ├── environment.yml
#   ├── requirements.txt
#   └── README.md
```

### 3. 파일 복사 (수동)

**방법 1: 파일별 수동 복사** (권장)

```bash
# 예시: db_setup.sql 복사
# backend 폴더 구조에 맞게 위치 결정 필요

# 예시 1: backend/db/ 폴더 생성 후 복사
mkdir -p backend/db
cp backend_dev/db_loading/db_setup.sql backend/db/db_setup.sql

# 예시 2: backend/scripts/ 폴더 생성 후 복사
mkdir -p backend/scripts
cp backend_dev/db_loading/setup_db.py backend/scripts/setup_db.py
cp backend_dev/db_loading/load_hana_to_db.py backend/scripts/load_hana_to_db.py
cp backend_dev/db_loading/verify_db_load.py backend/scripts/verify_db_load.py

# 예시 3: docker-compose.yml 병합 (기존 파일이 있는 경우 확인)
# backend/docker/docker-compose.yml 확인 후 필요시 병합
cp backend_dev/docker/docker-compose.yml backend/docker/docker-compose.yml

# 예시 4: environment.yml, requirements.txt 병합 (기존 파일 확인)
# 기존 파일과 비교하여 필요한 항목만 추가
```

**방법 2: PowerShell로 일괄 복사** (Windows)

```powershell
# PowerShell에서
$backendDevPath = "C:\Users\AI-WS01\projects\call-act\backend_dev"
$backendPath = "C:\Users\AI-WS01\projects\call-act\backend"

# scripts 폴더 생성
New-Item -ItemType Directory -Path "$backendPath\scripts" -Force

# 파일 복사
Copy-Item "$backendDevPath\db_loading\setup_db.py" "$backendPath\scripts\"
Copy-Item "$backendDevPath\db_loading\load_hana_to_db.py" "$backendPath\scripts\"
Copy-Item "$backendDevPath\db_loading\verify_db_load.py" "$backendPath\scripts\"
Copy-Item "$backendDevPath\db_loading\db_setup.sql" "$backendPath\db\db_setup.sql"

# docker-compose.yml 복사 (기존 파일 확인 후)
Copy-Item "$backendDevPath\docker\docker-compose.yml" "$backendPath\docker\docker-compose.yml" -Force
```

### 4. 파일 경로 확인

복사한 파일들의 경로가 스크립트 내부에서 올바르게 참조되는지 확인:

```python
# 예시: load_hana_to_db.py 내부의 경로 확인
# 파일 경로가 변경되었다면 수정 필요
BASE_DIR = Path(__file__).parent.parent.parent
RDB_METADATA_FILE = BASE_DIR / "data-preprocessing" / "data" / "hana" / "hana_rdb_metadata.json"
VECTORDB_FILE = BASE_DIR / "data-preprocessing" / "data" / "hana" / "hana_vectordb_with_embeddings.json"
```

### 5. backend 서브모듈에 커밋 및 푸시

```bash
# backend 폴더로 이동
cd backend

# Git 상태 확인
git status

# 변경사항 추가
git add .

# 커밋
git commit -m "feat: Add DB loading scripts and schema files"

# 팀 레포에 푸시
git push origin main

# 또는 브랜치 사용 시
git push origin [브랜치명]
```

### 6. 메인 레포에서 서브모듈 포인터 업데이트

```bash
# 메인 레포로 이동
cd ..

# 서브모듈 포인터 업데이트
git add backend
git commit -m "chore: Update backend submodule"
git push origin main
```

## backend 폴더 내 권장 구조

복사할 파일들의 위치 제안:

```
backend/
├── app/              # 기존 백엔드 코드
├── db/               # 새로 생성 (DB 관련 파일)
│   └── db_setup.sql
├── scripts/          # 새로 생성 (스크립트 파일)
│   ├── setup_db.py
│   ├── load_hana_to_db.py
│   ├── verify_db_load.py
│   └── generate_embeddings_hana.py (선택)
├── docker/           # 기존 폴더
│   ├── Dockerfile
│   ├── docker-compose.yml (병합 또는 교체)
│   └── environment.yml
├── docs/             # 기존 폴더
│   ├── SETUP.md
│   └── db_loading/   # 새로 생성 (선택)
│       └── README.md
├── environment.yml   # 병합 또는 교체
├── requirements.txt  # 병합 또는 교체
└── README.md
```

**⚠️ 참고**: 실제 backend 폴더 구조는 팀 레포의 기존 구조를 확인하고 결정해야 합니다.

## 복사 시 주의사항

### 1. 기존 파일과의 충돌
- `environment.yml`, `requirements.txt`, `docker-compose.yml` 등은 기존 파일이 있을 수 있습니다
- 기존 파일을 확인하고 필요한 항목만 추가하거나 병합

### 2. 경로 수정
- 스크립트 내부의 파일 경로가 변경되었을 수 있습니다
- 복사 후 스크립트 내 경로 확인 및 수정 필요

### 3. 환경 변수
- `.env` 파일은 복사하지 않습니다 (개인 설정)
- `.env.example` 파일만 복사하거나 문서화

### 4. 테스트
- 복사 후 backend 폴더에서 스크립트가 정상 작동하는지 확인

## 체크리스트

복사 완료 확인:

- [ ] 복사할 파일 목록 결정
- [ ] backend 폴더 구조 확인
- [ ] 파일 복사 완료
- [ ] 파일 경로 확인 및 수정
- [ ] 기존 파일과의 충돌 해결
- [ ] 복사한 파일 테스트 (backend 폴더에서)
- [ ] backend 서브모듈에 커밋
- [ ] 팀 레포에 푸시
- [ ] 메인 레포 서브모듈 포인터 업데이트

## 다음 단계

1. 팀원들에게 backend 레포 업데이트 알림
2. 팀원들이 `git pull` 또는 서브모듈 업데이트
3. 팀원들이 복사된 파일 사용

---

**문서 버전**: v1.0  
**최종 수정일**: 2026-01-11  
**작성자**: CALL:ACT Team
