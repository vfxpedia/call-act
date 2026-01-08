# ZF_DJANGO AWS Lightsail 배포 가이드 (최종 완벽판 - Docker Hub)

이 문서는 `zf_django` 프로젝트를 **Docker Hub**를 이용하여 AWS Lightsail(Ubuntu)에 처음부터 배포하는 과정을 설명합니다.
`requirements_docker.txt`를 사용하여 배포 전용 의존성을 관리합니다.

---

## [1부] 로컬 개발 환경 준비 (PC에서 수행)

**전제 조건:** 로컬 프로젝트에 `requirements_docker.txt` 파일과 이를 사용하도록 수정된 `Dockerfile`이 있어야 합니다. (이미 준비됨)

### 1. Docker 이미지 빌드 및 푸시
로컬 프로젝트 폴더(`.../zf_django`)에서 실행합니다.

```powershell
# 1. Docker Hub 로그인
# (명령어 실행 후 본인의 Docker ID와 비밀번호를 입력하세요)
docker login

# 2. 이미지 빌드
# 'YOUR_DOCKER_USERNAME'을 본인의 Docker Hub 사용자 이름으로 변경하세요.
docker build -t YOUR_DOCKER_USERNAME/zf_django:latest .

# 3. 이미지 푸시
docker push YOUR_DOCKER_USERNAME/zf_django:latest
```

---

## [2부] AWS Lightsail 인스턴스 생성 및 SSH 연결

### 1. Lightsail 인스턴스 생성
1.  **Lightsail 콘솔 접속:** AWS Lightsail 콘솔(lightsail.aws.amazon.com) 로그인.
2.  **인스턴스 생성:** `Create instance` 클릭.
3.  **플랫폼:** `Linux/Unix` -> `OS Only` -> `Ubuntu 22.04 LTS` 선택.
4.  **SSH 키 페어:** `Create new key pair`로 키 생성 및 다운로드 (`.pem`).
5.  **인스턴스 이름:** 지정 후 `Create instance`.

### 2. SSH 접속
다운로드한 `.pem` 파일이 있는 경로에서 명령어를 실행하세요.
`your-key-pair-name.pem`을 실제 다운로드한 키 파일 이름으로 변경해야 합니다.

#### 2-1. Mac / Linux 사용자
키 파일의 권한을 400으로 변경해야 합니다.
```bash
chmod 400 your-key-pair-name.pem
ssh -i your-key-pair-name.pem ubuntu@<Lightsail-Public-IP>
```

#### 2-2. Windows 사용자
PowerShell에서는 `chmod` 명령어가 필요 없습니다. 바로 접속을 시도하세요.
```powershell
ssh -i .\your-key-pair-name.pem ubuntu@<Lightsail-Public-IP>
```

**※ 만약 "WARNING: UNPROTECTED PRIVATE KEY FILE!" 오류가 발생하면:**
파일 속성 -> 보안 탭에서 해당 사용자를 제외한 모든 사용자의 권한을 제거해야 합니다.
(간단하게는: 파일 우클릭 -> 속성 -> 보안 -> 고급 -> 상속 사용 안 함 -> 모든 권한 제거 -> 추가 -> 보안 주체 선택: 본인 계정 -> 확인)

---

## [3부] AWS Lightsail 서버 설정 (SSH 접속 후 수행)

**SSH 접속 후의 상태에서 시작합니다.**

### 1. 기본 설정 및 Docker 설치
복사해서 한 줄씩 실행하세요.

```bash
# 1. 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# 2. 필수 패키지 설치
sudo apt install -y ca-certificates curl gnupg lsb-release

# 3. 충돌 방지를 위해 기존 패키지 제거 (혹시 있다면)
sudo apt-get remove --purge containerd.io docker-ce docker-ce-cli -y
sudo apt-get autoremove -y

# 4. Docker 및 Docker Compose 설치 (Ubuntu 기본 저장소 사용)
sudo apt install -y docker.io docker-compose

# 5. Docker 자동 실행 설정
sudo systemctl start docker
sudo systemctl enable docker

# 6. 현재 사용자에게 Docker 권한 부여 (중요)
sudo usermod -aG docker $USER
```

### 🚨 중요: 권한 적용을 위해 재접속
위 명령어를 모두 실행했다면, **반드시 현재 SSH 창을 닫고 다시 접속하세요.**
(재접속하지 않으면 권한 오류가 발생합니다.)

---

## [4부] 배포 파일 생성 및 실행 (재접속 후 수행)

### 1. Docker Hub 로그인
```bash
# 본인의 Docker Hub 계정으로 로그인합니다.
docker login
# Username과 Password 입력 (비밀번호 입력 시 화면에 아무것도 안 보여도 정상입니다)
```

### 2. 배포 폴더 생성
```bash
mkdir -p ~/zf_django_deploy/nginx
cd ~/zf_django_deploy
```

### 3. 설정 파일 생성 (`vim` 사용)

#### 3-1. `.env` 파일 생성
```bash
vim .env
```
*   **`vim` 사용법:** `i` 눌러서 입력 모드 진입 -> 아래 내용 붙여넣기 -> `Esc` 누르기 -> `:wq` 입력 후 `Enter` (저장 및 종료)

```
DJANGO_SECRET_KEY=여기에_시크릿키_입력
DB_NAME=데이터베이스이름
DB_USER=유저이름
DB_PASSWORD=비밀번호
DB_HOST=데이터베이스주소
DB_PORT=5432
OPENAI_API_KEY=여기에_OPENAI_키_입력
```

#### 3-2. `nginx/default.conf` 생성
```bash
vim nginx/default.conf
```
*   (동일하게 `i` -> 붙여넣기 -> `Esc` -> `:wq`)

```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /code/static/;
    }
}
```

#### 3-3. `docker-compose.yml` 생성
```bash
vim docker-compose.yml
```
*   (동일하게 `i` -> 붙여넣기 -> `Esc` -> `:wq`)

**중요:** `image:` 항목에 본인의 Docker Hub ID를 입력해야 합니다.

```yaml
services:
  web:
    # 아래 YOUR_DOCKER_USERNAME을 본인의 Docker ID로 변경하세요.
    image: YOUR_DOCKER_USERNAME/zf_django:latest
    container_name: zf_django_web
    restart: always
    env_file:
      - .env
    expose:
      - "8000"
    volumes:
      - static_volume:/code/static

  nginx:
    image: nginx:alpine
    container_name: zf_nginx_proxy
    restart: always
    ports:
      - "8080:80"
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf
      - static_volume:/code/static
    depends_on:
      - web

volumes:
  static_volume:
```

### 4. 서비스 실행
```bash
docker-compose pull
docker-compose up -d
```

### 5. 상태 확인
```bash
docker-compose ps
```
(`State`가 `Up`으로 되어 있으면 성공입니다.)

---

## [5부] Lightsail 방화벽 설정 (콘솔 웹페이지)

1.  Lightsail 인스턴스 관리 페이지 -> **Networking** 탭.
2.  **IPv4 Firewall** -> `Add rule`.
3.  **Port**: `8080`, **Protocol**: `TCP` 추가.
4.  브라우저 접속: `http://<Public-IP>:8080`