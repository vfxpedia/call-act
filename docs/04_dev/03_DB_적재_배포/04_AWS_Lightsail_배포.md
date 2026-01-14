# AWS Lightsail 배포 가이드

**작성일**: 2026-01-13  
**작성자**: CALL:ACT Team  
**버전**: v1.0  
**상태**: 완료

---

## 개요

Docker Hub에 업로드한 PostgreSQL + pgvector 이미지를 AWS Lightsail에 배포하는 과정을 설명합니다.

## 사전 준비

1. **AWS 계정 및 Lightsail 접근 권한**
   - AWS 계정 생성
   - Lightsail 서비스 접근 권한 확인

2. **Docker Hub 이미지 업로드 완료**
   - 참고: `docs/04_dev/03_DB_적재_배포/03_Docker_Hub_업로드.md`

3. **SSH 클라이언트**
   - Windows: PowerShell 또는 PuTTY
   - Mac/Linux: 기본 터미널

---

## [1부] AWS Lightsail 인스턴스 생성

### 1.1 Lightsail 콘솔 접속

1. AWS Lightsail 콘솔 접속: https://lightsail.aws.amazon.com
2. AWS 계정으로 로그인

### 1.2 인스턴스 생성

1. **Create instance** 클릭
2. **플랫폼 선택**:
   - `Linux/Unix` 선택
   - `OS Only` 선택
   - `Ubuntu 22.04 LTS` 선택

3. **인스턴스 플랜 선택**:
   - 개발/테스트: $3.50/month (512MB RAM, 1 vCPU)
   - 프로덕션: $5/month 이상 권장

4. **인스턴스 이름 지정**:
   - 예: `callact-db-server`

5. **SSH 키 페어 생성**:
   - `Create new key pair` 선택
   - 키 이름 입력 (예: `callact-db-key`)
   - 키 다운로드 (`.pem` 파일)

6. **Create instance** 클릭

### 1.3 인스턴스 정보 확인

인스턴스 생성 후:
- **Public IP** 확인 (예: `3.34.123.45`)
- **SSH 접속 정보** 확인

---

## [2부] SSH 접속

### 2.1 Windows 사용자

PowerShell에서 실행:

```powershell
# .pem 파일이 있는 디렉토리로 이동
cd C:\path\to\key\file

# SSH 접속
ssh -i .\callact-db-key.pem ubuntu@<Lightsail-Public-IP>
```

**주의사항**:
- `.pem` 파일 권한 오류 발생 시:
  - 파일 우클릭 → 속성 → 보안 탭
  - 고급 → 상속 사용 안 함
  - 모든 권한 제거 → 추가 → 본인 계정 선택 → 확인

### 2.2 Mac/Linux 사용자

터미널에서 실행:

```bash
# 키 파일 권한 변경
chmod 400 callact-db-key.pem

# SSH 접속
ssh -i callact-db-key.pem ubuntu@<Lightsail-Public-IP>
```

---

## [3부] 서버 설정 (SSH 접속 후)

### 3.1 시스템 업데이트

```bash
sudo apt update && sudo apt upgrade -y
```

### 3.2 필수 패키지 설치

```bash
sudo apt install -y ca-certificates curl gnupg lsb-release
```

### 3.3 Docker 설치

```bash
# 기존 Docker 제거 (혹시 있다면)
sudo apt-get remove --purge containerd.io docker-ce docker-ce-cli -y
sudo apt-get autoremove -y

# Docker 및 Docker Compose 설치
sudo apt install -y docker.io docker-compose

# Docker 서비스 시작 및 자동 실행 설정
sudo systemctl start docker
sudo systemctl enable docker

# 현재 사용자에게 Docker 권한 부여
sudo usermod -aG docker $USER
```

### 3.4 권한 적용을 위한 재접속

**중요**: 위 명령어 실행 후 **반드시 SSH 창을 닫고 다시 접속**해야 합니다.

```bash
# 현재 세션 종료
exit

# 다시 접속
ssh -i .\callact-db-key.pem ubuntu@<Lightsail-Public-IP>
```

---

## [4부] 배포 파일 생성 (재접속 후)

### 4.1 Docker Hub 로그인

```bash
docker login
```

- Docker Hub 사용자명 입력
- 비밀번호 입력 (화면에 표시되지 않음)

### 4.2 배포 폴더 생성

```bash
mkdir -p ~/callact_db_deploy
cd ~/callact_db_deploy
```

### 4.3 .env 파일 생성

```bash
vim .env
```

**vim 사용법**:
- `i` 눌러서 입력 모드 진입
- 아래 내용 붙여넣기
- `Esc` 누르기
- `:wq` 입력 후 `Enter` (저장 및 종료)

**.env 파일 내용**:
```
POSTGRES_USER=callact_admin
POSTGRES_PASSWORD=강력한_비밀번호_입력
POSTGRES_DB=callact_db
```

**보안 주의사항**:
- 프로덕션 환경에서는 강력한 비밀번호 사용
- `.env` 파일은 Git에 커밋하지 않음

### 4.4 docker-compose.yml 생성

```bash
vim docker-compose.yml
```

**docker-compose.yml 내용**:
```yaml
version: '3.8'

services:
  postgres:
    image: YOUR_DOCKER_USERNAME/callact_db:latest
    container_name: callact_db_container
    env_file:
      - .env
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U callact_admin -d callact_db"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

**중요**: `YOUR_DOCKER_USERNAME`을 본인의 Docker Hub 사용자명으로 변경하세요.

---

## [5부] 서비스 실행

### 5.1 이미지 다운로드

```bash
docker-compose pull
```

### 5.2 서비스 시작

```bash
docker-compose up -d
```

### 5.3 상태 확인

```bash
# 컨테이너 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f postgres
```

**정상 상태 확인**:
- `State`가 `Up`으로 표시되면 성공
- 로그에서 "DB 설정이 완료되었습니다" 메시지 확인

### 5.4 DB 연결 테스트

```bash
# 컨테이너 내부에서 psql 실행
docker exec -it callact_db_container psql -U callact_admin -d callact_db

# 테이블 목록 확인
\dt

# pgvector 확장 확인
\dx vector

# 종료
\q
```

---

## [6부] Lightsail 방화벽 설정

### 6.1 방화벽 규칙 추가

1. Lightsail 콘솔에서 인스턴스 선택
2. **Networking** 탭 클릭
3. **IPv4 Firewall** 섹션에서 **Add rule** 클릭
4. 규칙 추가:
   - **Application**: `Custom`
   - **Protocol**: `TCP`
   - **Port**: `5432`
   - **Source**: `Anywhere (0.0.0.0/0)` 또는 특정 IP
5. **Create** 클릭

**보안 권장사항**:
- 프로덕션 환경에서는 특정 IP만 허용하는 것을 권장
- VPN 또는 SSH 터널을 통한 접근 권장

---

## [7부] 외부에서 DB 연결 테스트

### 7.1 DBeaver 연결 설정

1. DBeaver 실행
2. 새 연결 생성 → PostgreSQL 선택
3. 연결 정보 입력:
   - **Host**: `<Lightsail-Public-IP>`
   - **Port**: `5432`
   - **Database**: `callact_db`
   - **Username**: `callact_admin`
   - **Password**: `.env` 파일에 설정한 비밀번호

4. **Test Connection** 클릭하여 연결 확인

### 7.2 psql로 연결 테스트

로컬에서 실행:

```powershell
# psql 설치 필요 시
# Windows: https://www.postgresql.org/download/windows/

psql -h <Lightsail-Public-IP> -p 5432 -U callact_admin -d callact_db
```

---

## 트러블슈팅

### 문제 1: Docker 권한 오류

**증상**: `permission denied while trying to connect to the Docker daemon socket`

**해결**:
```bash
# 재접속 확인
exit
ssh -i .\callact-db-key.pem ubuntu@<Lightsail-Public-IP>

# Docker 그룹 확인
groups
# docker가 표시되어야 함

# 없으면 다시 추가
sudo usermod -aG docker $USER
# 재접속
```

### 문제 2: 이미지 pull 실패

**증상**: `unauthorized: authentication required`

**해결**:
```bash
# Docker Hub 재로그인
docker login
```

### 문제 3: 컨테이너 시작 실패

**증상**: 컨테이너가 계속 재시작됨

**해결**:
```bash
# 로그 확인
docker-compose logs postgres

# .env 파일 확인
cat .env

# 환경 변수 형식 확인 (공백, 따옴표 등)
```

### 문제 4: 외부에서 연결 불가

**증상**: 타임아웃 또는 연결 거부

**해결**:
1. Lightsail 방화벽 규칙 확인
2. 인스턴스 보안 그룹 확인
3. 컨테이너 포트 매핑 확인:
   ```bash
   docker-compose ps
   ```

---

## 데이터 백업

### 백업 명령어

```bash
# 컨테이너 내부에서 백업
docker exec callact_db_container pg_dump -U callact_admin callact_db > backup_$(date +%Y%m%d).sql

# 볼륨 백업
docker run --rm -v callact_db_deploy_postgres_data:/data -v $(pwd):/backup ubuntu tar czf /backup/postgres_data_backup_$(date +%Y%m%d).tar.gz /data
```

---

## 다음 단계

AWS Lightsail 배포 완료 후:
- Frontend 동기화 진행
- Backend 연결 진행
- 참고: `docs/04_dev/03_DB_적재_배포/00_세션_전달_문서.md`

---

**마지막 업데이트**: 2026-01-13
