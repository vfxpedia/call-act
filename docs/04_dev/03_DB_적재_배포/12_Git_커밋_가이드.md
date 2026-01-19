# Git 커밋 가이드

**작성일**: 2026-01-13  
**작성자**: CALL:ACT Team  
**목적**: 팀 레포와 개인 dev 폴더 동기화 후 Git 커밋 및 PR 생성 가이드

---

## 1. 최종 점검 결과

### 1.1 파일 동기화 상태

**Backend**:
- ✅ 스크립트 파일 동기화 완료 (8개 Python 파일, 6개 SQL 파일)
- ✅ Docker 파일 동기화 완료 (`Dockerfile`, `docker-compose.yml`, `environment.yml`)
- ✅ 문서 파일 동기화 완료 (`docs/` 폴더)

**Data-preprocessing**:
- ✅ 스크립트 파일 동기화 완료 (22개 Python 파일)
- ✅ 문서 파일 동기화 완료 (`docs/teddycard_preprocessing/README.md`)
- ✅ 경로 구조 일치화 완료 (`preprocess/teddycard/`, `data/teddycard/`)

### 1.2 문서 경로 수정 상태

**Backend 문서**:
- ✅ `backend/docs/통합_DB_설정_가이드.md`: 팀 레포 경로 기준 (정상)
- ✅ `backend_dev/docs/통합_DB_설정_가이드.md`: dev 경로 기준 (수정 완료)

**Data-preprocessing 문서**:
- ✅ `data-preprocessing/docs/teddycard_preprocessing/README.md`: 팀 레포 경로 기준 (수정 완료)
- ✅ `data-preprocessing_dev/docs/teddycard_preprocessing/README.md`: dev 경로 기준 (정상)

### 1.3 Git 상태 확인

**Backend 레포**:
- 현재 브랜치: `main`
- 로컬/원격 동기화: ✅ 동기화됨
- 사용할 브랜치: `feat/callact_db` (또는 `feat/collact_db`)

**Data-preprocessing 레포**:
- 현재 브랜치: `feat/data-merge`
- 로컬/원격 동기화: ⚠️ 원격에 11개의 더 최신 커밋 존재 (확인 필요)
- 사용할 브랜치: `feat/data-merge`

---

## 2. Git 커밋 단계별 가이드

### Phase 1: Data-preprocessing 레포 커밋

**현재 상태**: `feat/data-merge` 브랜치에 변경사항 있음

#### Step 1-1: 원격 최신 상태 확인 및 동기화

```bash
cd data-preprocessing

# 1. 원격 저장소 최신 정보 가져오기
git fetch origin

# 2. 원격 브랜치와 로컬 브랜치 상태 확인
git status

# 3. 원격에 있는 최신 커밋 확인 (선택사항)
git log HEAD..origin/main --oneline

# 4. 원격 main 브랜치 변경사항 확인 후 필요시 merge 또는 rebase
# 주의: 현재 브랜치(feat/data-merge)가 원격 main과 충돌하지 않는지 확인
```

#### Step 1-2: 변경사항 스테이징 및 커밋

```bash
cd data-preprocessing

# 1. 현재 변경사항 확인
git status

# 2. 커밋할 파일 스테이징
git add preprocess/teddycard/
git add docs/teddycard_preprocessing/README.md

# 3. 변경사항 확인 (선택사항)
git status

# 4. 커밋 메시지 작성 및 커밋
git commit -m "feat: teddycard 스크립트 경로 구조 변경 및 문서 업데이트

- 폴더 구조 정리: preprocessing → preprocess
- 출력 경로 변경: output → data/teddycard
- config.py 경로 참조 수정
- 스크립트 파일 경로 참조 일괄 수정 (00~09)
- teddycard_preprocessing README.md 경로 수정
- data-preprocessing 팀 레포와 구조 일치화"
```

#### Step 1-3: 원격 브랜치로 푸시

```bash
cd data-preprocessing

# 1. 원격 브랜치로 푸시
git push origin feat/data-merge

# 2. 푸시 결과 확인
git status
```

#### Step 1-4: Pull Request 생성 (GitHub 웹사이트)

1. GitHub에서 `data-preprocessing` 레포로 이동
2. "Pull requests" 탭 클릭
3. "New pull request" 클릭
4. **Base**: `main`
5. **Compare**: `feat/data-merge`
6. PR 제목: `feat: teddycard 스크립트 경로 구조 변경 및 문서 업데이트`
7. PR 설명 작성 후 "Create pull request" 클릭

---

### Phase 2: Backend 레포 커밋

**현재 상태**: `main` 브랜치에 변경사항 있음  
**사용할 브랜치**: `feat/callact_db` (또는 `feat/collact_db`)

#### Step 2-1: 브랜치 생성 또는 체크아웃

```bash
cd backend

# 1. 현재 브랜치 확인
git branch

# 2. feat/callact_db 브랜치가 있는지 확인
git branch -a | Select-String "callact_db"

# 3-A. 브랜치가 이미 존재하는 경우: 체크아웃
git checkout feat/callact_db

# 3-B. 브랜치가 없는 경우: 새로 생성
git checkout -b feat/callact_db

# 4. 브랜치 확인
git branch
```

#### Step 2-2: 변경사항 확인 및 스테이징

```bash
cd backend

# 1. 현재 변경사항 확인
git status

# 2. 커밋할 파일 스테이징
git add docker/Dockerfile
git add docker/docker-compose.yml
git add docker/environment.yml
git add app/db/scripts/
git add docs/

# 3. 변경사항 확인 (선택사항)
git status
```

#### Step 2-3: 커밋

```bash
cd backend

# 커밋 메시지 작성 및 커밋
git commit -m "feat: 통합 DB 설정 스크립트 및 하나카드 데이터 적재 기능 추가

- 반드시 docs/14_DB_초기화_및_재적재_가이드.md 를 보고 진행해주세요.

- 통합 DB 설정 스크립트 개선 (01_setup_callact_db.py)
  - 하나카드 데이터 적재 기능 통합
  - 상담사 데이터 적재 기능 추가 (employeesData.json)
  - 상담사 성과 지표 업데이트 기능 추가 (DB 실제 데이터 기반: consultations, fcr, avgTime, rank)
  - 상담사 배분 로직 개선 (균등 분배, 편차 허용, 풀 캐싱 최적화)
  - 랜덤 시드 고정 (RANDOM_SEED = 42)으로 재현 가능한 결과 보장
  - config.py를 통한 경로 중앙 관리 (Windows/Mac 호환)
  - 데이터 존재 시 검증만 수행 (덮어쓰기 방지)
- SQL 파일 통합 (02_setup_tedicard_tables.sql)
- 데이터 적재 스크립트 config.py 사용으로 변경
  - 04_load_keyword_dictionary.py
  - 05_load_teddycard_data.py
  - 03_load_hana_to_db.py
  - 04_verify_db_load.py
- Docker 및 docker-compose 설정 추가
- Git LFS 설치 가이드 문서 추가
- 통합 DB 설정 가이드 문서 업데이트
  - 하나카드 데이터 적재 방법 추가
  - 상담사 데이터 적재 방법 추가
  - 실행 순서 업데이트 (스키마 → 상담사 → 하나카드 → 성과지표 업데이트 → 테디카드)"
```

#### Step 2-4: 원격 브랜치로 푸시

```bash
cd backend

# 1. 원격 브랜치로 푸시
git push origin feat/callact_db

# 2. 푸시 결과 확인
git status
```

#### Step 2-5: Pull Request 생성 (GitHub 웹사이트)

1. GitHub에서 `backend` 레포로 이동
2. "Pull requests" 탭 클릭
3. "New pull request" 클릭
4. **Base**: `main`
5. **Compare**: `feat/callact_db`
6. PR 제목: `feat: 통합 DB 설정 스크립트 및 하나카드 데이터 적재 기능 추가`
7. PR 설명 작성 후 "Create pull request" 클릭

---

### Phase 3: 개인 루트 레포 업데이트 (전체 동기화)

**개인 루트 레포**: `call-act`  
**주의**: 개인 레포이므로 모든 변경사항(.back 폴더 포함)을 커밋합니다.

#### Step 3-1: 변경사항 확인 및 스테이징

```bash
cd C:\Users\AI-WS01\projects\call-act

# 1. 현재 변경사항 확인
git status

# 2. 서브모듈 상태 업데이트 (서브모듈이 가리키는 커밋 해시 반영)
git add backend data-preprocessing

# 3. 문서 파일들 추가
git add README.md
git add docs/

# 4. 개인 개발 폴더 동기화 (개인 레포이므로 포함)
git add backend_dev/
git add data-preprocessing_dev/
git add frontend_dev/

# 5. .back 폴더 추가 (개인 레포이므로 백업 파일도 포함)
git add .back/

# 6. 상태 확인
git status
```

#### Step 3-2: 커밋
```bash
git commit -m "chore: 팀 레포 최신화 및 개인 개발 폴더 동기화

- backend 팀 레포 최신 변경사항 반영 (팀원 작업)
- backend → backend_dev 동기화 완료
- 서브모듈(backend, data-preprocessing) 최신 커밋 반영
- 문서 업데이트 (Git 커밋 가이드, DB 초기화 가이드 등)
- 개인 개발 폴더(backend_dev, data-preprocessing_dev, frontend_dev) 동기화
- .back 폴더 백업 파일 포함"
```

#### Step 3-3: 원격 레포로 푸시

```bash
cd C:\Users\AI-WS01\projects\call-act

# 1. 원격 레포로 푸시
git push origin main

# 2. 푸시 결과 확인
git status
```

---

## 3. 주의사항 및 체크리스트

### 3.1 커밋 전 체크리스트

**Data-preprocessing**:
- [ ] 원격 main 브랜치와 충돌하지 않는지 확인
- [ ] 변경사항이 올바른지 확인 (`git diff` 사용)
- [ ] 커밋 메시지가 명확한지 확인
- [ ] 불필요한 파일이 스테이징되지 않았는지 확인 (`.gitignore` 확인)

**Backend**:
- [ ] `feat/callact_db` 브랜치가 올바른지 확인
- [ ] 변경사항이 올바른지 확인 (`git diff` 사용)
- [ ] 커밋 메시지가 명확한지 확인
- [ ] Docker 파일 및 스크립트가 올바른지 확인

**개인 루트 레포**:
- [ ] README.md 변경사항이 올바른지 확인
- [ ] docs 폴더 변경사항이 올바른지 확인
- [ ] 서브모듈 상태가 올바른지 확인

### 3.2 커밋 후 체크리스트

**Data-preprocessing**:
- [ ] 푸시 성공 확인 (`git status`)
- [ ] PR 생성 완료 확인
- [ ] PR 설명 작성 완료

**Backend**:
- [ ] 푸시 성공 확인 (`git status`)
- [ ] PR 생성 완료 확인
- [ ] PR 설명 작성 완료

**개인 루트 레포**:
- [ ] 푸시 성공 확인 (`git status`)

### 3.3 문제 발생 시 해결 방법

**푸시 실패 (rejected)**:
```bash
# 원격에 더 최신 커밋이 있는 경우
git pull origin <브랜치명>
# 충돌 해결 후
git push origin <브랜치명>
```

**브랜치가 없는 경우**:
```bash
# 새 브랜치 생성
git checkout -b feat/callact_db
# 변경사항 커밋 후 푸시
git push -u origin feat/callact_db
```

**잘못된 파일이 스테이징된 경우**:
```bash
# 특정 파일 unstage
git reset HEAD <파일명>
# 모든 파일 unstage
git reset HEAD
```

---

## 4. 커밋 메시지 예시

### Data-preprocessing

```
feat: teddycard 스크립트 경로 구조 변경 및 문서 업데이트

- 폴더 구조 정리: preprocessing → preprocess
- 출력 경로 변경: output → data/teddycard
- config.py 경로 참조 수정
- 스크립트 파일 경로 참조 일괄 수정 (00~09)
- teddycard_preprocessing README.md 경로 수정
- data-preprocessing 팀 레포와 구조 일치화
```

### Backend

```
feat: 통합 DB 설정 스크립트 및 하나카드 데이터 적재 기능 추가

- 통합 DB 설정 스크립트 개선 (01_setup_callact_db.py)
  - 하나카드 데이터 적재 기능 통합
  - 상담사 데이터 적재 기능 추가 (employeesData.json)
  - 상담사 성과 지표 업데이트 기능 추가 (DB 실제 데이터 기반: consultations, fcr, avgTime, rank)
  - 상담사 배분 로직 개선 (균등 분배, 편차 허용, 풀 캐싱 최적화)
  - 랜덤 시드 고정 (RANDOM_SEED = 42)으로 재현 가능한 결과 보장
  - config.py를 통한 경로 중앙 관리 (Windows/Mac 호환)
  - 데이터 존재 시 검증만 수행 (덮어쓰기 방지)
- SQL 파일 통합 (02_setup_tedicard_tables.sql)
- 데이터 적재 스크립트 config.py 사용으로 변경
  - 04_load_keyword_dictionary.py
  - 05_load_teddycard_data.py
  - 03_load_hana_to_db.py
  - 04_verify_db_load.py
- Docker 및 docker-compose 설정 추가
- Git LFS 설치 가이드 문서 추가
- 통합 DB 설정 가이드 문서 업데이트
  - 하나카드 데이터 적재 방법 추가
  - 상담사 데이터 적재 방법 추가
  - 실행 순서 업데이트 (스키마 → 상담사 → 하나카드 → 성과지표 업데이트 → 테디카드)
```

### 개인 루트 레포

```
docs: README.md 데이터베이스 설정 부분 수정

- 통합 스크립트 사용 방법으로 변경
- 데이터베이스 이름 callact_db로 통일
- 통합_DB_설정_가이드.md 링크 추가
```

---

## 5. 실행 순서 요약

1. **Data-preprocessing 레포**
   - `git fetch origin` → 원격 상태 확인
   - `git add` → 변경사항 스테이징
   - `git commit` → 커밋
   - `git push origin feat/data-merge` → 푸시
   - GitHub에서 PR 생성

2. **Backend 레포**
   - `git checkout feat/callact_db` (또는 생성)
   - `git add` → 변경사항 스테이징
   - `git commit` → 커밋
   - `git push origin feat/callact_db` → 푸시
   - GitHub에서 PR 생성

3. **개인 루트 레포**
   - `git add` → 변경사항 스테이징
   - `git commit` → 커밋
   - `git push origin main` → 푸시

---

## 6. 참고 문서

- [통합 DB 설정 가이드](./11_통합_DB_설정_가이드.md)
- [Git LFS 설치 및 사용 가이드](../../00_git/Git_LFS_설치_및_사용_가이드.md)
- [Backend 동기화 가이드](./09_Backend_동기화_가이드.md)
- [향후 전처리 작업 가이드](./13_향후_전처리_작업_가이드.md) ⭐ Backend/RAG 개발 중 전처리 개선이 필요할 때 참고

---

**마지막 업데이트**: 2026-01-13
