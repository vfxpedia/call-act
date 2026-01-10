# Docker 클라우드 배포 가이드

**작성일**: 2026-01-09  
**작성자**: CALL:ACT Team  
**버전**: v1.0

---

## 개요

로컬 IP (192.168.x.x) 대신 클라우드 서버에 Docker를 배포하여 팀원들이 접근할 수 있도록 설정하는 방법입니다.

**장점**:
- ✅ 공용 IP 주소로 어디서나 접근 가능
- ✅ 개인 PC가 꺼져 있어도 접근 가능
- ✅ 방화벽 설정 간소화
- ✅ 안정적인 서비스 제공

**옵션**:
1. **AWS EC2** (가장 일반적)
2. **Docker Hub + 클라우드 서버**
3. **Tailscale VPN** (간단한 팀 공유)

---

## 방법 1: AWS EC2 배포 (권장)

### 1.1 AWS EC2 인스턴스 생성

1. **AWS 콘솔 접속** → EC2 서비스 선택
2. **인스턴스 시작**:
   - AMI: Ubuntu 22.04 LTS (또는 Amazon Linux)
   - 인스턴스 유형: t3.micro (무료 티어) 또는 t3.small
   - 키 페어: 새로 생성 또는 기존 사용
   - 보안 그룹: 22번 포트 (SSH), 5432번 포트 (PostgreSQL) 허용
3. **인스턴스 시작**

### 1.2 EC2 서버 접속 및 Docker 설치

```bash
# SSH 접속
ssh -i your-key.pem ubuntu@[EC2_퍼블릭_IP]

# Docker 설치 (Ubuntu)
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu

# 재접속 후 확인
docker --version
```

### 1.3 Docker Compose 파일 업로드

```bash
# EC2 서버에 접속한 후
mkdir -p ~/callact_db
cd ~/callact_db

# docker-compose.yml 파일 생성
nano docker-compose.yml
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg17
    container_name: callact_db_container
    environment:
      POSTGRES_USER: callact_admin
      POSTGRES_PASSWORD: callact_pwd1
      POSTGRES_DB: callact_db
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

### 1.4 Docker 실행

```bash
# Docker Compose 실행
docker-compose up -d

# 실행 확인
docker ps

# 로그 확인
docker-compose logs -f
```

### 1.5 pgvector 확장 설치

```bash
# 컨테이너 접속
docker exec -it callact_db_container psql -U callact_admin -d callact_db

# pgvector 확장 설치
CREATE EXTENSION IF NOT EXISTS vector;

# 확인
SELECT * FROM pg_extension WHERE extname = 'vector';

# 종료
\q
```

### 1.6 보안 그룹 설정

**AWS 콘솔에서**:
1. EC2 → 보안 그룹 선택
2. 인바운드 규칙 편집
3. 규칙 추가:
   - 유형: PostgreSQL
   - 포트: 5432
   - 소스: 팀원 IP 주소 또는 0.0.0.0/0 (개발 환경만)

### 1.7 팀원 연결 정보 공유

```
=== CALL:ACT PostgreSQL 연결 정보 (AWS EC2) ===

Host: [EC2 퍼블릭 IP] (예: 13.124.220.200)
Port: 5432
Database: callact_db
Username: callact_admin
Password: callact_pwd1

DBeaver 연결:
1. 새 연결 → PostgreSQL
2. Host: [EC2 퍼블릭 IP]
3. Port: 5432
4. Database: callact_db
5. Username: callact_admin
6. Password: callact_pwd1
```

---

## 방법 2: Docker Hub + 클라우드 서버

### 2.1 Docker 이미지 빌드 및 푸시

**로컬에서**:
```bash
# Docker Hub 로그인
docker login

# 이미지 태그
docker tag pgvector/pgvector:pg17 [DOCKER_HUB_USERNAME]/callact-postgres:latest

# 이미지 푸시
docker push [DOCKER_HUB_USERNAME]/callact-postgres:latest
```

### 2.2 클라우드 서버에서 실행

**클라우드 서버 (AWS EC2, GCP, Azure 등)**:
```bash
# Docker Hub에서 이미지 pull
docker pull [DOCKER_HUB_USERNAME]/callact-postgres:latest

# docker-compose.yml 수정
# image: [DOCKER_HUB_USERNAME]/callact-postgres:latest

# 실행
docker-compose up -d
```

---

## 방법 3: Tailscale VPN (가장 간단)

### 3.1 Tailscale 설치 및 설정

**모든 팀원이 설치**:
1. https://tailscale.com 접속
2. 계정 생성 (Google 계정으로 간편 가입)
3. Tailscale 다운로드 및 설치
4. 로그인

### 3.2 DB 호스트 PC 설정

**로컬 PC에서**:
```bash
# Tailscale IP 확인
tailscale ip

# 예: 100.x.x.x (Tailscale IP)
```

**Docker 실행** (기존과 동일):
```bash
cd scripts/docker
docker-compose up -d
```

### 3.3 팀원 연결 정보 공유

```
=== CALL:ACT PostgreSQL 연결 정보 (Tailscale) ===

Host: [Tailscale IP] (예: 100.64.1.2)
Port: 5432
Database: callact_db
Username: callact_admin
Password: callact_pwd1

참고: Tailscale이 설치되어 있어야 접근 가능합니다.
```

**장점**:
- ✅ 방화벽 설정 불필요
- ✅ 보안 자동 처리
- ✅ 무료 (개인 사용)
- ✅ 간단한 설정

---

## 방법 비교

| 방법 | 난이도 | 비용 | 안정성 | 접근성 | 추천 |
|------|--------|------|--------|--------|------|
| **AWS EC2** | 중 | 유료 (무료 티어 가능) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ 프로덕션 |
| **Docker Hub + 클라우드** | 중 | 유료 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ 팀 공유 |
| **Tailscale VPN** | 낮음 | 무료 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ 개발 환경 |
| **로컬 IP** | 낮음 | 무료 | ⭐⭐ | ⭐⭐ | ⚠️ 테스트용 |

---

## 보안 주의사항

### AWS EC2
- ✅ 보안 그룹에서 특정 IP만 허용 권장
- ✅ 강력한 비밀번호 사용
- ✅ 정기적인 보안 업데이트

### Tailscale
- ✅ Tailscale 자체 보안 기능 활용
- ✅ 팀원만 접근 가능 (자동)

### 일반
- ⚠️ 프로덕션 환경에서는 VPN 또는 IP 화이트리스트 필수
- ⚠️ 비밀번호는 안전한 채널로 공유
- ⚠️ 정기적인 백업 권장

---

## 추천 방법

### 개발 환경
**Tailscale VPN** 추천
- 설정 간단
- 무료
- 보안 자동 처리

### 프로덕션 환경
**AWS EC2** 추천
- 안정성 높음
- 확장 가능
- 모니터링 용이

---

## 다음 단계

1. ✅ 방법 선택 (Tailscale 또는 AWS EC2)
2. ⏳ 서버 설정 완료
3. ⏳ 팀원에게 연결 정보 공유
4. ⏳ DBeaver 연결 테스트

---

## 참고 문서

- 개발 환경 설정: `docs/04_dev/02_db/01_개발환경_설정_가이드.md`
- 실행 가이드: `docs/04_dev/02_db/02_실행_가이드.md`
- 체크리스트: `docs/04_dev/02_db/04_해야할일_체크리스트.md`

