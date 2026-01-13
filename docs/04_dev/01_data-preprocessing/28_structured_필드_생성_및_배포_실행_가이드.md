# Structured 필드 생성 및 배포 실행 가이드

## 개요

이 가이드는 structured 필드 생성부터 AWS Lightsail 배포까지의 전체 과정을 단계별로 안내합니다.

## Phase 1: Structured 필드 생성 및 전파

### 1.1 환경 설정 확인

```bash
# 작업 디렉토리로 이동
cd data-preprocessing_dev/preprocessing/teddycard

# .env 파일 확인
# OPENAI_API_KEY가 설정되어 있는지 확인
cat ../../../../.env | grep OPENAI_API_KEY
```

**필수 확인 사항**:
- `OPENAI_API_KEY` 환경 변수 설정
- `config.py`에서 `ENV_TYPE = 'dev'` 확인
- `keywords_dict.json` 파일 존재 확인

### 1.2 Structured 필드 생성

```bash
# Structured 필드 생성 실행
python 11_structured_for_rag.py
```

**실행 시간**: 문서 수에 따라 다름 (약 100-200개 문서 기준 10-20분)

**예상 출력**:
```
Processing service guides...
Processing: teddycard_service_guides_hyundai.json
  Document 1/50: workflow type
  Document 2/50: information type
  ...
Processing: teddycard_service_guides_samsung.json
  ...
Processing: teddycard_service_guides_shinhan.json
  ...
Processing: teddycard_service_guides_special.json
  ...
Processing card products...
  Document 1/100: card_info type
  ...
Structured field generation completed!
```

**생성되는 파일**:
- `data-preprocessing_dev/preprocessing/output/teddycard_service_guides_*.json` (structured 필드 추가)
- `data-preprocessing_dev/preprocessing/output/teddycard_card_products.json` (structured 필드 추가)

### 1.3 Structured 필드 전파

```bash
# Structured 필드 전파 실행
python 12_propagate_structured.py
```

**실행 시간**: 약 1-2분

**예상 출력**:
```
Propagating structured field...
  Propagating to enriched files...
  Propagating to _with_embeddings files...
  Completed: 150 documents updated
```

**전파되는 파일**:
- `teddycard_service_guides_enriched.json`
- `teddycard_service_guides_with_embeddings.json`
- `teddycard_card_products_enriched.json`
- `teddycard_card_products_with_embeddings.json`

### 1.4 결과 검증

```bash
# JSON 파일에서 structured 필드 확인
python -c "
import json
with open('../../output/teddycard_service_guides_hyundai.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    print(f'Total documents: {len(data)}')
    print(f'Documents with structured: {sum(1 for d in data if \"structured\" in d)}')
    if data:
        print(f'Sample structured keys: {list(data[0].get(\"structured\", {}).keys())}')
"
```

## Phase 2: DB 적재

### 2.1 DB 적재 스크립트 실행

```bash
# 작업 디렉토리로 이동
cd ../../../../backend_dev/app/db/scripts

# DB 적재 실행
python 03_load_teddycard_to_db.py
```

**실행 시간**: 데이터 양에 따라 다름 (약 5-10분)

**예상 출력**:
```
Loading service guides...
  Loading: teddycard_service_guides_hyundai.json
  Inserted: 50 documents
  ...
Loading card products...
  Inserted: 100 documents
  ...
Loading notices...
  Inserted: 20 documents
  ...
DB loading completed!
```

### 2.2 데이터 검증

```bash
# 데이터 검증 실행
python 04_verify_teddycard_load.py
```

**검증 항목**:
- 각 테이블의 레코드 수
- structured 필드 포함 여부
- 임베딩 벡터 존재 여부
- 외래 키 제약 조건 확인

**예상 출력**:
```
Verifying DB load...
  service_guide_documents: 500 records ✓
  card_products: 100 records ✓
  notices: 20 records ✓
  All embeddings present: ✓
  Structured fields present: ✓
Verification completed!
```

## Phase 3: Docker 빌드 및 배포

### 3.1 Docker 이미지 빌드

```bash
# 작업 디렉토리로 이동
cd ../../../../backend_dev

# Docker 이미지 빌드
docker build -t call-act-backend:latest -f docker/Dockerfile .
```

**빌드 시간**: 약 5-10분

**예상 출력**:
```
[+] Building 120.5s (15/15) FINISHED
 => [internal] load build definition from Dockerfile
 => => transferring dockerfile: 2.00kB
 => [1/15] FROM docker.io/library/postgres:15
 => ...
 => [15/15] COPY app /app
 => exporting to image
 => => exporting layers
 => => writing image sha256:...
 => => naming to docker.io/library/call-act-backend:latest
```

### 3.2 Docker Hub 푸시

```bash
# Docker Hub 로그인
docker login

# 이미지 태그 설정 (Docker Hub 사용자명으로 변경)
docker tag call-act-backend:latest <your-dockerhub-username>/call-act-backend:latest

# 이미지 푸시
docker push <your-dockerhub-username>/call-act-backend:latest
```

**푸시 시간**: 이미지 크기에 따라 다름 (약 2-5분)

### 3.3 AWS Lightsail 배포

#### 3.3.1 AWS Lightsail 인스턴스 생성

1. AWS Lightsail 콘솔 접속
2. "인스턴스 생성" 클릭
3. 플랫폼: Linux/Unix 선택
4. 블루프린트: "OS Only" → "Ubuntu 22.04 LTS" 선택
5. 인스턴스 플랜: 최소 2GB RAM 권장
6. 인스턴스 이름: `call-act-backend` 입력
7. "인스턴스 생성" 클릭

#### 3.3.2 SSH 접속 및 Docker 설치

```bash
# SSH 접속 (Lightsail 콘솔에서 "SSH" 버튼 클릭 또는)
ssh -i ~/.ssh/lightsail-key.pem ubuntu@<lightsail-ip>

# Docker 설치
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

# Docker 서비스 시작
sudo systemctl start docker
sudo systemctl enable docker

# 현재 사용자를 docker 그룹에 추가
sudo usermod -aG docker ubuntu
# (재로그인 필요)
```

#### 3.3.3 Docker 이미지 Pull 및 실행

```bash
# Docker Hub에서 이미지 Pull
docker pull <your-dockerhub-username>/call-act-backend:latest

# 컨테이너 실행
docker run -d \
  --name call-act-db \
  -p 5432:5432 \
  -e POSTGRES_DB=callact_db \
  -e POSTGRES_USER=callact_admin \
  -e POSTGRES_PASSWORD=callact_pwd1 \
  -v postgres_data:/var/lib/postgresql/data \
  <your-dockerhub-username>/call-act-backend:latest
```

#### 3.3.4 방화벽 설정

AWS Lightsail 콘솔에서:
1. 네트워킹 탭 선택
2. 방화벽 규칙 추가:
   - 애플리케이션: PostgreSQL
   - 포트: 5432
   - 소스: 팀원 IP 주소 또는 0.0.0.0/0 (임시, 보안 주의)

### 3.4 연결 테스트

```bash
# 로컬에서 연결 테스트
psql -h <lightsail-ip> -p 5432 -U callact_admin -d callact_db

# 비밀번호 입력: callact_pwd1
```

## Phase 4: 팀원 공유

### 4.1 접속 정보 제공

팀원에게 다음 정보를 공유:

```
AWS Lightsail 접속 정보:
- 호스트: <lightsail-ip>
- 포트: 5432
- 데이터베이스: callact_db
- 사용자: callact_admin
- 비밀번호: callact_pwd1
```

### 4.2 DBeaver 연결 가이드

1. DBeaver 실행
2. "새 연결" → "PostgreSQL" 선택
3. 연결 정보 입력:
   - 호스트: `<lightsail-ip>`
   - 포트: `5432`
   - 데이터베이스: `callact_db`
   - 사용자: `callact_admin`
   - 비밀번호: `callact_pwd1`
4. "테스트 연결" 클릭하여 확인
5. "완료" 클릭

### 4.3 API 엔드포인트 공유

백엔드 API가 배포된 경우:

```
API Base URL: http://<lightsail-ip>:8000
RAG Search: POST /api/rag/search
STT Keywords: POST /api/stt/keywords
```

## Phase 5: RAG, STT, Frontend 연동 테스트

### 5.1 RAG 연동 테스트

```bash
# RAG 검색 테스트
curl -X POST http://<lightsail-ip>:8000/api/rag/search \
  -H "Content-Type: application/json" \
  -d '{
    "sttKeywords": ["카드분실", "재발급"],
    "customerId": "CUST-001",
    "consultationId": "CS-20250109-1432"
  }'
```

### 5.2 STT 연동 테스트

```bash
# STT 키워드 추출 테스트
curl -X POST http://<lightsail-ip>:8000/api/stt/keywords \
  -H "Content-Type: application/json" \
  -d '{
    "audioText": "카드 분실 신고하고 싶어요"
  }'
```

### 5.3 Frontend 연동

Frontend에서 API 엔드포인트를 `<lightsail-ip>:8000`으로 설정하여 테스트

## 문제 해결

### Structured 필드 생성 실패

**증상**: LLM API 호출 실패

**해결**:
1. `OPENAI_API_KEY` 확인
2. API 사용량 한도 확인
3. 네트워크 연결 확인
4. 재시도 (일부 문서만 실패한 경우)

### DB 적재 실패

**증상**: 외래 키 제약 조건 오류

**해결**:
1. `employees` 테이블에 기본 에이전트 존재 확인
2. `02_setup_tedicard_tables.sql` 실행 확인
3. 데이터 무결성 확인

### Docker 빌드 실패

**증상**: 의존성 설치 오류

**해결**:
1. `requirements.txt` 확인
2. Dockerfile의 Python 버전 확인
3. 네트워크 연결 확인

### AWS Lightsail 연결 실패

**증상**: 포트 5432 접속 불가

**해결**:
1. 방화벽 규칙 확인
2. 보안 그룹 설정 확인
3. 인스턴스 상태 확인 (실행 중인지)

## 다음 단계

1. **성능 측정**: RAG 성능 로깅 시스템 구축 (Phase 2)
2. **A-B 테스트**: structured 필드 효과 검증
3. **모델 비교**: gpt-4o-mini vs gpt-4o 성능 비교
4. **최적화**: 검색 결과 및 응답 시간 개선
