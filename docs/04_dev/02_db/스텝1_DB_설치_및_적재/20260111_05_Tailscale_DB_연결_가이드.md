# Tailscale DB 연결 가이드

## 메타데이터
- **작성일**: 2026-01-11
- **작성자**: CALL:ACT Team
- **버전**: v1.0
- **상태**: 완료
- **관련 문서**: [팀원 DB 연결 가이드](./20260111_01_팀원_DB_연결_가이드.md), [README](./README.md)

## 목적

Tailscale VPN을 사용하여 팀원들이 DBeaver로 데이터베이스에 연결하는 방법을 안내합니다.

**⚠️ 중요**: 이 가이드는 Tailscale을 사용하여 DB를 공유하는 경우를 위한 것입니다.

## 배경

- DB 적재는 이미 완료
- 담당자의 PC에서 Docker로 PostgreSQL 실행 중
- Tailscale VPN을 통한 안전한 네트워크 접근
- 팀원은 Tailscale 설치 후 DBeaver로 연결

## 내용

### 1. Tailscale 설치 및 설정

#### 1.1 Tailscale 설치

1. **Tailscale 공식 사이트 접속**: https://tailscale.com/download
2. **운영체제에 맞는 설치 파일 다운로드** (Windows, macOS, Linux 지원)
3. **설치 실행**
4. **계정 생성 또는 로그인**:
   - Google 계정, Microsoft 계정, 또는 이메일로 가입
   - 무료 계정으로 사용 가능

#### 1.2 Tailscale 접속 확인

**Windows**:
1. 시스템 트레이에서 Tailscale 아이콘 확인
2. 아이콘이 녹색이면 정상 접속
3. 아이콘 클릭 → "Connected" 상태 확인

**명령어로 확인**:
```bash
# PowerShell 또는 Command Prompt
tailscale status

# 또는 Tailscale IP 확인
tailscale ip
```

**예상 출력**:
```
100.64.1.2  # Tailscale IP (예시)
```

#### 1.3 팀 네트워크 확인

담당자가 Tailscale 관리 페이지에서 팀원들을 같은 네트워크에 추가해야 합니다.

**확인 방법**:
- Tailscale 웹 콘솔 (https://login.tailscale.com/admin/machines) 접속
- 팀원들의 기기가 같은 네트워크에 있는지 확인
- 필요시 담당자에게 네트워크 초대 요청

### 2. DBeaver 연결 설정

#### 2.1 연결 정보 받기

담당자으로부터 다음 정보를 받으세요:

- **Host**: `[Tailscale IP 주소]` (예: `100.64.1.2`)
- **Port**: `5432`
- **Database**: `callact_db`
- **Username**: `callact_admin`
- **Password**: `callact_pwd1`

#### 2.2 DBeaver 새 연결 생성

1. **DBeaver 실행**
2. **새 연결 생성**:
   - 좌측 상단 "+" 버튼 클릭
   - 또는 메뉴: Database → New Database Connection
3. **데이터베이스 선택**: **PostgreSQL** 선택 → Next

#### 2.3 연결 정보 입력

**Main 탭**:
- **Host**: Tailscale IP 주소 (예: `100.64.1.2`)
- **Port**: `5432`
- **Database**: `callact_db`
- **Username**: `callact_admin`
- **Password**: `callact_pwd1`
- **Save password**: 체크 (선택사항)

#### 2.4 연결 테스트

1. **"Test Connection" 버튼 클릭**
2. **드라이버 다운로드 안내가 나오면**: "Download" 클릭하여 자동 설치
3. **성공 메시지 확인**: ✅ "Connected" 또는 "연결이 성공적으로 완료되었습니다"

#### 2.5 연결 완료

1. **"Finish" 버튼 클릭**
2. **좌측 패널에서 연결 확인**: `callact_db` 연결이 보임
3. **확장하여 테이블 확인**:
   - `callact_db` → `Schemas` → `public` → `Tables`
   - 다음 테이블 3개가 보여야 함:
     - `employees`
     - `consultations`
     - `consultation_documents`

### 3. 데이터 확인

#### 3.1 테이블 데이터 확인

```sql
-- DBeaver에서 SQL 편집기 열기 (Ctrl+Shift+Enter)

-- 전체 데이터 개수 확인
SELECT 
    (SELECT COUNT(*) FROM consultations) as consultations_count,
    (SELECT COUNT(*) FROM consultation_documents) as documents_count,
    (SELECT COUNT(*) FROM employees) as employees_count;

-- 상담 데이터 샘플 확인
SELECT id, category, title, call_date 
FROM consultations 
LIMIT 10;

-- 문서 데이터 샘플 확인
SELECT id, category, title, created_at 
FROM consultation_documents 
LIMIT 10;
```

#### 3.2 기본 상담사 확인

```sql
-- 기본 상담사 확인
SELECT id, name, email, role, department 
FROM employees 
WHERE id = 'EMP-TEDI-DEFAULT';

-- 결과 예시:
-- EMP-TEDI-DEFAULT | 테디카드 기본 상담사 | default@tedicard.com | 상담사 | 테디카드 상담팀
```

### 4. 문제 해결

#### 4.1 Tailscale 연결 실패

**증상**: Tailscale 아이콘이 빨간색이거나 "Disconnected" 상태

**해결**:
1. Tailscale 재시작 (시스템 트레이 아이콘 우클릭 → Quit, 다시 실행)
2. 로그인 상태 확인
3. 인터넷 연결 확인
4. 담당자에게 네트워크 초대 확인 요청

#### 4.2 DBeaver 연결 실패: `Connection refused` 또는 `Connection timeout`

**원인**: 
- Tailscale이 연결되지 않음
- 담당자의 Docker 컨테이너가 실행되지 않음
- Tailscale IP 주소가 잘못됨

**해결**:
1. **Tailscale 연결 상태 확인**:
   ```bash
   tailscale status
   # 담당자의 기기가 보여야 함
   ```

2. **담당자에게 Docker 컨테이너 실행 확인 요청**:
   ```bash
   docker ps
   # callact_db_container가 보여야 함
   ```

3. **Tailscale IP 확인** (담당자자에게 요청):
   ```bash
   tailscale ip
   ```

4. **Ping 테스트** (Tailscale IP로):
   ```bash
   ping [Tailscale IP]
   # 예: ping 100.64.1.2
   ```

#### 4.3 `FATAL: password authentication failed`

**원인**: 비밀번호가 잘못됨

**해결**:
- 담당자에게 정확한 비밀번호 확인
- Password 필드 다시 입력

#### 4.4 `FATAL: database "callact_db" does not exist`

**원인**: 데이터베이스 이름이 잘못됨

**해결**:
- Database 필드 확인: `callact_db` (언더스코어 없음)
- `call_act_db`로 입력하지 않았는지 확인

#### 4.5 Tailscale은 연결되었지만 DB에 접근 불가

**원인**: 담당자의 PC 방화벽 설정

**해결** (담당자가 해야 할 작업):
1. Windows 방화벽 설정 확인
2. PostgreSQL 포트 (5432) 인바운드 규칙 추가
3. Tailscale 네트워크에서 허용

### 5. Backend 코드에서 사용

#### 5.1 .env 파일 설정

프로젝트를 받은 후 `.env` 파일을 생성하세요:

```bash
# backend/.env.example을 복사
Copy-Item backend\.env.example backend\.env
```

#### 5.2 .env 파일 수정

```env
# backend/.env
DB_HOST=[Tailscale IP 주소]  # localhost가 아님!
DB_PORT=5432
DB_USER=callact_admin
DB_PASSWORD=callact_pwd1
DB_NAME=callact_db
```

#### 5.3 Backend 코드에서 자동 사용

`backend/app/core/config.py`가 환경 변수를 자동으로 읽어옵니다:

```python
# backend/app/core/config.py는 이미 환경 변수를 사용하도록 설정됨
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "callact_db")
# ...
```

### 6. Tailscale 장점

**보안**:
- ✅ 자동 암호화 (WireGuard 기반)
- ✅ 방화벽 설정 자동 처리
- ✅ 팀 네트워크 분리

**편의성**:
- ✅ 공용 IP 주소 불필요
- ✅ 방화벽 규칙 수동 설정 불필요
- ✅ 무료 계정으로 사용 가능
- ✅ 어디서나 접근 가능 (인터넷 연결만 있으면)

**비교**:
- **로컬 네트워크**: 같은 Wi-Fi 필요, 공용 IP 없음
- **AWS EC2**: 비용 발생, 설정 복잡
- **Tailscale**: 무료, 간단, 안전 ⭐

### 7. 체크리스트

연결 완료 확인:

- [ ] Tailscale 설치 완료
- [ ] Tailscale 로그인 및 연결 확인
- [ ] 담당자으로부터 Tailscale IP 및 연결 정보 받기
- [ ] DBeaver 설치 완료
- [ ] 새 연결 생성 (`callact_db`)
- [ ] 연결 테스트 성공
- [ ] 테이블 3개 확인 (employees, consultations, consultation_documents)
- [ ] 데이터 샘플 확인
- [ ] Backend .env 파일 설정 (필요한 경우)

## 결론

Tailscale을 사용하면 팀원들은 간단하게 안전하게 데이터베이스에 접근할 수 있습니다.
DBeaver 연결만 설정하면 바로 데이터를 사용할 수 있으며, Backend 코드는 `.env` 파일의 환경 변수를 자동으로 읽어옵니다.

## 다음 단계

- Backend API 개발 시작
- RAG 파이프라인 테스트
- 프론트엔드와 연동

**관련 문서**:
- [팀원 DB 연결 가이드](./20260111_01_팀원_DB_연결_가이드.md) (일반 가이드)
- [오류 대응 가이드](./20260111_04_오류_대응_가이드.md)
- [Backend SETUP 가이드](../../../../backend/docs/SETUP.md)

---

**문서 버전**: v1.0  
**최종 수정일**: 2026-01-11  
**작성자**: CALL:ACT Team
