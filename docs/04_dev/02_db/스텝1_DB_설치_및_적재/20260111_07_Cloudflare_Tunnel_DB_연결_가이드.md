# Cloudflare Tunnel DB 연결 가이드

## 메타데이터
- **작성일**: 2026-01-11
- **작성자**: CALL:ACT Team
- **버전**: v1.0
- **상태**: 완료
- **관련 문서**: [팀원 DB 연결 가이드](./20260111_01_팀원_DB_연결_가이드.md), [Tailscale 가이드](./20260111_05_Tailscale_DB_연결_가이드.md), [README](./README.md)

## 목적

Cloudflare Tunnel (cloudflared)을 사용하여 팀원들이 DBeaver로 데이터베이스에 연결하는 방법을 안내합니다.

**⚠️ 중요**: 이 가이드는 담당자가 Cloudflare Tunnel을 사용하여 DB를 공유하는 경우를 위한 것입니다.

## 배경

- DB 적재는 담당자가 이미 완료
- 담당자의 PC에서 Docker로 PostgreSQL 실행 중
- Cloudflare Tunnel을 통한 안전한 네트워크 접근
- 팀원은 cloudflared 설치 없이 DBeaver로 연결 (담당자만 설정)

## Cloudflare Tunnel 개요

### 장점

- ✅ **담당자만 설정**: 팀원은 추가 설치 불필요
- ✅ **무료 계정 사용 가능**: 도메인 없이도 사용 가능 (Quick Tunnel)
- ✅ **보안**: Cloudflare의 암호화된 터널 사용
- ✅ **공용 IP 불필요**: 방화벽 설정 간소화

### 단점

- ⚠️ **Quick Tunnel**: 실행할 때마다 URL 변경 (고정 URL은 복잡)
- ⚠️ **cloudflared 계속 실행 필요**: 담당자 PC에서 터널이 살아있어야 함
- ⚠️ **설정 복잡도**: Tailscale보다 약간 복잡

### Tailscale과 비교

| 항목 | Cloudflare Tunnel | Tailscale |
|------|-------------------|-----------|
| 초대 절차 | ❌ 없음 | ⚠️ 1회 필요 |
| 담당자 설정 | ⭐⭐ 보통 | ⭐⭐ 보통 |
| 팀원 설치 | ❌ 불필요 | ✅ 필요 (1회) |
| IP/URL 고정 | ⚠️ Quick Tunnel: 변경됨<br>✅ Named Tunnel: 고정 (권장) | ✅ 고정 |
| 무료 사용 | ✅ 가능 | ✅ 가능 |
| 추천도 | ⭐⭐ (URL 변경 문제) | ⭐⭐⭐ (권장) |

**결론**: 
- **Named Tunnel 사용 시**: 터널 ID가 고정되어 URL이 안정적입니다 (권장)
- **Quick Tunnel 사용 시**: URL이 변경되므로 비권장
- **Tailscale**: 더 간단하고 완전히 고정된 IP 제공 (권장)

## 담당자 설정 (Windows)

### 1. cloudflared 설치

#### 1.1 다운로드

1. **Cloudflare Tunnel 다운로드**: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
2. **Windows 선택**: "Windows (amd64)" 다운로드
3. **압축 해제**: 다운로드한 ZIP 파일을 적절한 폴더에 압축 해제 (예: `C:\cloudflared\`)
4. **경로 확인**: `cloudflared.exe` 파일이 있는지 확인

**또는 Chocolatey 사용** (선택사항):
```powershell
choco install cloudflared
```

#### 1.2 설치 확인

```powershell
# PowerShell에서
cd C:\cloudflared  # 압축 해제한 폴더
.\cloudflared.exe --version

# 출력 예시: cloudflared 2024.x.x
```

### 2. Quick Tunnel 실행 (간단하지만 URL 변경됨)

**⚠️ 주의**: Quick Tunnel은 실행할 때마다 URL이 변경됩니다. **고정 URL이 필요하면 "Named Tunnel" 방법을 사용하세요** (3번 참조).

#### 2.1 PostgreSQL 터널 실행

```powershell
# PowerShell에서 (Docker 컨테이너 실행 중인 상태에서)
cd C:\cloudflared

# TCP 터널 실행 (PostgreSQL 5432 포트)
.\cloudflared.exe tunnel --url tcp://localhost:5432
```

**출력 예시**:
```
2024-01-11T10:00:00Z INF +--------------------------------------------------------------------------------------------+
2024-01-11T10:00:00Z INF |  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable): |
2024-01-11T10:00:00Z INF |  tcp://xxxx-xxxx-xxxx.trycloudflare.com:54321                                |
2024-01-11T10:00:00Z INF +--------------------------------------------------------------------------------------------+
```

**⚠️ 중요**: 
- 이 창을 닫으면 터널이 종료됩니다
- 터널 URL (`tcp://xxxx-xxxx-xxxx.trycloudflare.com:54321`)을 복사하세요
- 터널이 살아있는 동안만 접근 가능합니다

#### 2.2 백그라운드 실행 (선택사항)

PowerShell에서 백그라운드로 실행:

```powershell
# 백그라운드 실행
Start-Process -FilePath "C:\cloudflared\cloudflared.exe" -ArgumentList "tunnel --url tcp://localhost:5432" -WindowStyle Hidden

# 또는 새 PowerShell 창에서 실행하고 창을 최소화
```

**⚠️ 문제점**: Quick Tunnel은 재시작할 때마다 URL이 변경되므로, 팀원에게 매번 새 URL을 공유해야 합니다.

### 3. Named Tunnel 실행 (고정 URL, 권장) ⭐

**고정 URL을 원하는 경우**: Named Tunnel을 사용하면 터널 URL이 고정되어 팀원들이 재설정할 필요가 없습니다.

#### 3.1 Cloudflare 계정 생성 (필요시)

1. **Cloudflare 가입**: https://dash.cloudflare.com/sign-up
2. **무료 계정으로 가입**

#### 3.2 cloudflared 로그인

```powershell
cd C:\cloudflared
.\cloudflared.exe tunnel login
```

브라우저가 열리면 Cloudflare 계정으로 로그인하세요.
로그인하면 `C:\Users\[사용자명]\.cloudflared\cert.pem` 파일이 생성됩니다.

#### 3.3 터널 생성 (1회만)

```powershell
# 터널 생성 (1회만, 이름: callact-db)
.\cloudflared.exe tunnel create callact-db
```

**출력 예시**:
```
Created tunnel callact-db with id: xxxx-xxxx-xxxx-xxxx
```

터널이 생성되면 `C:\Users\[사용자명]\.cloudflared\` 폴더에 터널 정보가 저장됩니다.

#### 3.4 설정 파일 생성 (config.yml) - TCP 연결용

터널 설정 파일을 생성해야 합니다. TCP 연결을 위해서는 특별한 설정이 필요합니다.

**1단계: 터널 생성 시 생성된 JSON 파일 경로 확인**

터널을 생성하면 `C:\Users\[사용자명]\.cloudflared\` 폴더에 `xxxx-xxxx-xxxx-xxxx.json` 형식의 파일이 생성됩니다.
파일 이름을 확인하세요 (예: `a1b2c3d4-e5f6-7890-abcd-ef1234567890.json`).

**2단계: config.yml 파일 생성**

```powershell
# 메모장 실행
notepad C:\Users\$env:USERNAME\.cloudflared\config.yml
```

**config.yml 내용** (PostgreSQL TCP 연결용):

```yaml
tunnel: callact-db
credentials-file: C:\Users\YOUR_USERNAME\.cloudflared\TUNNEL_ID.json

ingress:
  - service: tcp://localhost:5432
```

**⚠️ 중요**: 
- `YOUR_USERNAME`을 실제 Windows 사용자명으로 변경하세요
- `TUNNEL_ID.json`을 실제 터널 생성 시 생성된 JSON 파일 이름으로 변경하세요
- `ingress` 섹션에서 `hostname`을 지정하지 않으면, cloudflared가 자동으로 임시 도메인을 생성합니다

**실제 예시** (사용자명이 `AI-WS01`이고 터널 ID가 `a1b2c3d4-e5f6-7890-abcd-ef1234567890`인 경우):

```yaml
tunnel: callact-db
credentials-file: C:\Users\AI-WS01\.cloudflared\a1b2c3d4-e5f6-7890-abcd-ef1234567890.json

ingress:
  - service: tcp://localhost:5432
```

**3단계: 파일 저장**

메모장에서 파일을 저장하세요 (`Ctrl+S`).

#### 3.5 터널 실행 및 URL 확인

```powershell
# 터널 실행
cd C:\cloudflared
.\cloudflared.exe tunnel run callact-db
```

**출력 예시**:
```
2024-01-11T10:00:00Z INF +--------------------------------------------------------------------------------------------+
2024-01-11T10:00:00Z INF |  Connection established. Listening on:                                                     |
2024-01-11T10:00:00Z INF |  tcp://xxxx-xxxx-xxxx.trycloudflare.com:54321                                              |
2024-01-11T10:00:00Z INF +--------------------------------------------------------------------------------------------+
```

**⚠️ 중요**: 
- 이 URL (`tcp://xxxx-xxxx-xxxx.trycloudflare.com:54321`)을 복사하세요
- **이 URL은 Named Tunnel을 사용하면 고정됩니다** (같은 config.yml로 실행하면 같은 URL을 사용)
- 팀원들에게 이 URL을 공유하세요

**4단계: 백그라운드 실행 (선택사항)**

터널이 계속 실행되도록 하려면 새 PowerShell 창에서 실행하거나, Windows 서비스로 등록:

```powershell
# 새 PowerShell 창에서 실행 (터널이 살아있도록 유지)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\cloudflared; .\cloudflared.exe tunnel run callact-db"

# 또는 Windows 서비스로 등록 (관리자 권한 필요)
.\cloudflared.exe service install
.\cloudflared.exe service start
```

**서비스 등록 후 관리**:
```powershell
# 서비스 중지
.\cloudflared.exe service stop

# 서비스 시작
.\cloudflared.exe service start

# 서비스 제거
.\cloudflared.exe service uninstall
```

### 4. Docker 컨테이너 확인

터널을 실행하기 전에 Docker 컨테이너가 실행 중인지 확인:

```powershell
docker ps
# callact_db_container가 "healthy" 상태로 보이면 정상
```

## 팀원 연결 방법

### 1. 연결 정보 받기

담당자로부터 다음 정보를 받으세요:

**연결 정보 예시**:
```
터널 URL: tcp://xxxx-xxxx-xxxx.trycloudflare.com:54321
Host: xxxx-xxxx-xxxx.trycloudflare.com
Port: 54321
Database: callact_db
Username: callact_admin
Password: callact_pwd1
```

**⚠️ 중요**: 
- **Named Tunnel 사용 시**: URL이 고정되어 있어 재설정할 필요가 없습니다 ✅
- 담당자가 터널을 재시작해도 같은 URL을 사용합니다
- **Quick Tunnel 사용 시**: 담당자가 터널을 재시작하면 URL이 변경됩니다 (비권장)

### 2. DBeaver 연결 설정

#### 2.1 새 연결 생성

1. **DBeaver 실행**
2. **새 연결 생성**:
   - 좌측 상단 "+" 버튼 클릭
   - 또는 메뉴: Database → New Database Connection
3. **데이터베이스 선택**: **PostgreSQL** 선택 → Next

#### 2.2 연결 정보 입력

**Main 탭**:
- **Host**: 터널 URL의 호스트 부분 (예: `xxxx-xxxx-xxxx.trycloudflare.com`)
- **Port**: 터널 URL의 포트 (예: `54321`)
- **Database**: `callact_db`
- **Username**: `callact_admin`
- **Password**: `callact_pwd1`
- **Save password**: 체크 (선택사항)

#### 2.3 연결 테스트

1. **"Test Connection" 버튼 클릭**
2. **드라이버 다운로드 안내가 나오면**: "Download" 클릭하여 자동 설치
3. **성공 메시지 확인**: ✅ "Connected" 또는 "연결이 성공적으로 완료되었습니다"

#### 2.4 연결 완료

1. **"Finish" 버튼 클릭**
2. **좌측 패널에서 연결 확인**: `callact_db` 연결이 보임
3. **확장하여 테이블 확인**:
   - `callact_db` → `Schemas` → `public` → `Tables`
   - 다음 테이블 3개가 보여야 함:
     - `employees`
     - `consultations`
     - `consultation_documents`

## 문제 해결

### 1. 터널 연결 실패

**증상**: `Unable to reach the origin service. The service may be down or it may not be responding to traffic from cloudflared`

**원인**: Docker 컨테이너가 실행되지 않음

**해결**:
```powershell
# Docker 컨테이너 상태 확인
docker ps

# 컨테이너가 없으면 실행
cd C:\Users\AI-WS01\projects\call-act\backend_dev\docker
docker-compose up -d
```

### 2. DBeaver 연결 실패: `Connection timeout`

**원인**: 
- cloudflared가 실행되지 않음
- 터널 URL이 잘못됨
- 담당자가 터널을 재시작하여 URL이 변경됨

**해결**:
1. 담당자에게 cloudflared 실행 상태 확인 요청
2. 담당자에게 최신 터널 URL 요청
3. DBeaver에서 새 URL로 연결 설정

### 3. `FATAL: password authentication failed`

**원인**: 비밀번호가 잘못됨

**해결**:
- 담당자에게 정확한 비밀번호 확인
- Password 필드 다시 입력

### 4. URL이 자주 변경됨

**원인**: Quick Tunnel 사용 중

**해결 방법**:
1. **Named Tunnel 사용** (권장): 터널 ID가 고정되어 URL이 안정적
2. **Tailscale 사용**: 더 간단하고 완전히 고정된 IP 제공

## 담당자 권장사항

### Quick Tunnel vs Named Tunnel vs Tailscale

| 방법 | URL 고정 | 설정 난이도 | 권장도 |
|------|----------|------------|--------|
| Quick Tunnel | ❌ 변경됨 | ⭐ 간단 | ❌ 비권장 (URL 변경) |
| Named Tunnel | ✅ 고정 | ⭐⭐⭐ 복잡 | ⚠️ 가능하지만 복잡 |
| Tailscale | ✅ 고정 | ⭐⭐ 보통 | ✅ **권장** |

**최종 권장**: 
- **Named Tunnel 사용 시**: URL이 고정되어 팀원들이 재설정할 필요가 없습니다 (권장)
- **Tailscale 사용 시**: 더 간단하고 완전히 고정된 IP 제공 (권장)

**선택 기준**:
- **Cloudflare Named Tunnel**: 도메인 없이도 사용 가능, URL 고정, 설정 복잡
- **Tailscale**: 설정 간단, 완전히 고정된 IP, 1회 초대 필요

## 체크리스트

### 담당자 체크리스트

- [ ] cloudflared 설치 완료
- [ ] Docker 컨테이너 실행 중 확인
- [ ] Quick Tunnel 또는 Named Tunnel 실행
- [ ] 터널 URL 확인 및 기록
- [ ] 팀원에게 연결 정보 공유
- [ ] cloudflared가 계속 실행 중인지 확인

### 팀원 체크리스트

- [ ] 담당자로부터 터널 URL 및 연결 정보 받기
- [ ] DBeaver 설치 완료
- [ ] 새 연결 생성 (`callact_db`)
- [ ] 연결 테스트 성공
- [ ] 테이블 3개 확인 (employees, consultations, consultation_documents)
- [ ] 데이터 샘플 확인

## 결론

Cloudflare Tunnel Named Tunnel을 사용하면:
- ✅ 터널 ID가 고정되어 URL이 안정적
- ✅ 팀원들이 재설정할 필요가 없음
- ⚠️ 초기 설정이 복잡함

더 간단한 방법을 원한다면 **Tailscale 사용을 권장**합니다.

## 다음 단계

- Backend API 개발 시작
- RAG 파이프라인 테스트
- 프론트엔드와 연동

**관련 문서**:
- [팀원 DB 연결 가이드](./20260111_01_팀원_DB_연결_가이드.md) (일반 가이드)
- [Tailscale DB 연결 가이드](./20260111_05_Tailscale_DB_연결_가이드.md) ⭐ **권장**
- [오류 대응 가이드](./20260111_04_오류_대응_가이드.md)
- [Backend SETUP 가이드](../../../../backend/docs/SETUP.md)

---

**문서 버전**: v1.0  
**최종 수정일**: 2026-01-11  
**작성자**: CALL:ACT Team
