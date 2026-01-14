# Backend 커밋 가이드

**작성일**: 2026-01-13  
**작성자**: CALL:ACT Team  
**버전**: v1.0

---

## 개요

`backend_dev`에서 개발한 DB 적재 스크립트를 `backend` 팀 레포에 커밋하는 과정을 안내합니다.

## 전제 조건

- `backend` 서브모듈이 최신 상태로 동기화되어 있어야 함
- `backend_dev`의 DB 적재 스크립트가 완료되어 있어야 함
- 검증 스크립트가 통과되어야 함

## 커밋 전략

### 브랜치

**브랜치명**: `feat/teddycard-db-loading`

```bash
cd backend
git checkout -b feat/teddycard-db-loading
```

### 커밋할 파일

다음 파일들을 커밋합니다:

**SQL 스크립트**:
- `app/db/scripts/02_setup_tedicard_tables.sql` (테디카드 테이블 스키마)
- `app/db/scripts/02_alter_tedicard_tables.sql` (스키마 수정)
- `app/db/scripts/02_fix_id_length.sql` (ID 길이 수정)
- `app/db/scripts/03_setup_keyword_dictionary.sql` (키워드 사전 스키마)

**Python 스크립트**:
- `app/db/scripts/04_load_keyword_dictionary.py` (키워드 사전 적재)
- `app/db/scripts/05_load_teddycard_data.py` (테디카드 데이터 적재)
- `app/db/scripts/06_verify_teddycard_load.py` (검증 스크립트)

## 실행 순서

### 1. Backend 서브모듈로 이동

```bash
cd backend
```

### 2. 새 브랜치 생성 및 체크아웃

```bash
git checkout -b feat/teddycard-db-loading
```

### 3. 파일 복사

**PowerShell 사용**:

```powershell
# 절대 경로 사용
Copy-Item -Path "C:\Users\AI-WS01\projects\call-act\backend_dev\app\db\scripts\02_setup_tedicard_tables.sql" -Destination "C:\Users\AI-WS01\projects\call-act\backend\app\db\scripts\02_setup_tedicard_tables.sql" -Force
Copy-Item -Path "C:\Users\AI-WS01\projects\call-act\backend_dev\app\db\scripts\02_alter_tedicard_tables.sql" -Destination "C:\Users\AI-WS01\projects\call-act\backend\app\db\scripts\02_alter_tedicard_tables.sql" -Force
Copy-Item -Path "C:\Users\AI-WS01\projects\call-act\backend_dev\app\db\scripts\02_fix_id_length.sql" -Destination "C:\Users\AI-WS01\projects\call-act\backend\app\db\scripts\02_fix_id_length.sql" -Force
Copy-Item -Path "C:\Users\AI-WS01\projects\call-act\backend_dev\app\db\scripts\03_setup_keyword_dictionary.sql" -Destination "C:\Users\AI-WS01\projects\call-act\backend\app\db\scripts\03_setup_keyword_dictionary.sql" -Force
Copy-Item -Path "C:\Users\AI-WS01\projects\call-act\backend_dev\app\db\scripts\04_load_keyword_dictionary.py" -Destination "C:\Users\AI-WS01\projects\call-act\backend\app\db\scripts\04_load_keyword_dictionary.py" -Force
Copy-Item -Path "C:\Users\AI-WS01\projects\call-act\backend_dev\app\db\scripts\05_load_teddycard_data.py" -Destination "C:\Users\AI-WS01\projects\call-act\backend\app\db\scripts\05_load_teddycard_data.py" -Force
Copy-Item -Path "C:\Users\AI-WS01\projects\call-act\backend_dev\app\db\scripts\06_verify_teddycard_load.py" -Destination "C:\Users\AI-WS01\projects\call-act\backend\app\db\scripts\06_verify_teddycard_load.py" -Force
```

### 4. Git Add

```bash
git add app/db/scripts/02_setup_tedicard_tables.sql
git add app/db/scripts/02_alter_tedicard_tables.sql
git add app/db/scripts/02_fix_id_length.sql
git add app/db/scripts/03_setup_keyword_dictionary.sql
git add app/db/scripts/04_load_keyword_dictionary.py
git add app/db/scripts/05_load_teddycard_data.py
git add app/db/scripts/06_verify_teddycard_load.py
```

또는 한 번에:

```bash
git add app/db/scripts/02_*.sql app/db/scripts/03_*.sql app/db/scripts/04_*.py app/db/scripts/05_*.py app/db/scripts/06_*.py
```

### 5. 커밋

```bash
git commit -m "feat: Add Teddycard data DB loading scripts

- Add keyword dictionary loading script (04_load_keyword_dictionary.py)
- Add Teddycard data loading script (05_load_teddycard_data.py)
- Add verification script (06_verify_teddycard_load.py)
- Add SQL scripts for Teddycard tables and schema updates
  - 02_setup_tedicard_tables.sql: Create Teddycard tables
  - 02_alter_tedicard_tables.sql: Add RAG-related columns
  - 02_fix_id_length.sql: Fix ID column length
  - 03_setup_keyword_dictionary.sql: Create keyword dictionary tables"
```

### 6. 원격 저장소에 푸시

```bash
git push origin feat/teddycard-db-loading
```

## 커밋 메시지 가이드

### 형식

```
<type>: <subject>

<body>

<footer>
```

### Type

- `feat`: 새로운 기능 추가
- `fix`: 버그 수정
- `docs`: 문서 수정
- `style`: 코드 포맷팅
- `refactor`: 코드 리팩토링
- `test`: 테스트 추가
- `chore`: 빌드 업무 수정

### 예시

```
feat: Add Teddycard data DB loading scripts

- Add keyword dictionary loading script
- Add Teddycard data loading script
- Add verification script
- Add SQL scripts for Teddycard tables

Closes #123
```

## Pull Request 생성

GitHub에서 Pull Request를 생성합니다:

1. **제목**: `feat: Add Teddycard data DB loading scripts`
2. **설명**: 변경 사항 및 테스트 결과 요약
3. **리뷰어**: 팀원 지정
4. **라벨**: `enhancement`, `database`

## 주의사항

1. **서브모듈**: `backend`는 서브모듈이므로 메인 레포에서도 서브모듈 포인터를 업데이트해야 함
2. **환경 변수**: `.env` 파일은 커밋하지 않음 (`.env.example`만 커밋)
3. **테스트**: 커밋 전에 로컬에서 테스트 완료

## 다음 단계

커밋이 완료되면:
1. Pull Request 생성 및 리뷰 요청
2. 리뷰 피드백 반영
3. Merge 후 메인 레포 서브모듈 포인터 업데이트
4. Docker Hub 업로드
5. AWS Lightsail 배포

---

## 참고 문서

- [Backend 구조 비교 분석](./07_Backend_구조_비교_분석.md)
- [Backend 동기화 가이드](./09_Backend_동기화_가이드.md)
- [서브모듈 관리 가이드](../00_git/서브모듈_관리_가이드.md)
