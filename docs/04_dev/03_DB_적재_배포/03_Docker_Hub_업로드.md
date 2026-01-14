# Docker Hub 업로드 가이드

**작성일**: 2026-01-13  
**작성자**: CALL:ACT Team  
**버전**: v1.0  
**상태**: 완료

---

## 개요

PostgreSQL + pgvector Docker 이미지를 빌드하고 Docker Hub에 업로드하는 과정을 설명합니다.

## 사전 준비

1. **Docker Desktop 설치 및 실행 확인**
   ```powershell
   docker --version
   docker ps
   ```

2. **Docker Hub 계정 생성**
   - https://hub.docker.com 접속
   - 계정 생성 및 로그인
   - Docker Hub 사용자명 확인

## 1. Docker 이미지 빌드

### 1.1 빌드 명령어

`backend/` 디렉토리에서 실행:

```powershell
cd backend
docker build -f docker/Dockerfile -t YOUR_DOCKER_USERNAME/callact_db:latest .
```

**주의사항**:
- `YOUR_DOCKER_USERNAME`을 본인의 Docker Hub 사용자명으로 변경
- 빌드 컨텍스트는 `backend/` 디렉토리 (`.`)
- Dockerfile 경로는 `docker/Dockerfile`

### 1.2 빌드 확인

```powershell
docker images | findstr callact_db
```

빌드된 이미지가 표시되면 성공입니다.

## 2. Docker Hub 로그인

```powershell
docker login
```

- Docker Hub 사용자명 입력
- 비밀번호 입력 (화면에 표시되지 않음)

## 3. Docker Hub 업로드

### 3.1 이미지 푸시

```powershell
docker push YOUR_DOCKER_USERNAME/callact_db:latest
```

### 3.2 업로드 확인

1. Docker Hub 웹사이트 접속: https://hub.docker.com
2. 본인의 레포지토리 목록에서 `callact_db` 확인
3. 이미지가 정상적으로 업로드되었는지 확인

## 4. 이미지 테스트 (선택사항)

로컬에서 빌드한 이미지를 테스트할 수 있습니다:

```powershell
# 컨테이너 실행
docker run -d `
  -e POSTGRES_USER=callact_admin `
  -e POSTGRES_PASSWORD=callact_pwd1 `
  -e POSTGRES_DB=callact_db `
  --name callact_db_test `
  -p 5433:5432 `
  callact_db:test

# 로그 확인
docker logs callact_db_test

# DB 연결 테스트
docker exec -it callact_db_test psql -U callact_admin -d callact_db -c "\dt"
```

## 5. 트러블슈팅

### 5.1 빌드 오류

**문제**: COPY 명령어 실패
- **원인**: 빌드 컨텍스트 경로 오류
- **해결**: `backend/` 디렉토리에서 빌드 실행 확인

### 5.2 로그인 오류

**문제**: `unauthorized: authentication required`
- **원인**: Docker Hub 로그인 실패
- **해결**: `docker login` 재실행 및 계정 정보 확인

### 5.3 푸시 오류

**문제**: `denied: requested access to the resource is denied`
- **원인**: 이미지 태그에 Docker Hub 사용자명이 없음
- **해결**: 이미지 태그를 `YOUR_DOCKER_USERNAME/callact_db:latest` 형식으로 변경

## 6. 다음 단계

Docker Hub 업로드 완료 후:
- AWS Lightsail 배포 진행
- 참고: `docs/04_dev/03_DB_적재_배포/04_AWS_Lightsail_배포.md`

---

**마지막 업데이트**: 2026-01-13
