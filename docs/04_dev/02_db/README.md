# 하나카드 데이터 DB 적재 프로젝트

## 📚 문서 목록

### ⭐ 개발하면서 보기 좋은 문서 (우선순위)

1. **[00_빠른_실행_가이드.md](./00_빠른_실행_가이드.md)** ⭐ **가장 먼저 보기!**
   - 현재 상태 기준 빠른 실행 가이드
   - 지금 바로 실행 가능한 명령어
   - 단계별 체크리스트

2. **[02_실행_가이드.md](./02_실행_가이드.md)**: 상세 실행 가이드
   - 빠른 시작
   - 상세 실행 순서
   - 트러블슈팅

### 📖 참고 문서 (필요 시 확인)

3. **[00_hana_db_loading_설계.md](./00_hana_db_loading_설계.md)**: 전체 설계 문서
   - OpenAI 임베딩 API 사용 이유
   - 스키마 및 화면 구성 검증
   - 데이터 매핑 상세
   - 테스트 데이터 전략

4. **[01_개발환경_설정_가이드.md](./01_개발환경_설정_가이드.md)**: 개발 환경 설정 가이드
   - Conda 환경 설정
   - PostgreSQL + pgvector 설정
   - Docker 사용법
   - 주요 질문 답변

5. **[03_임베딩_데이터_저장_위치.md](./03_임베딩_데이터_저장_위치.md)**: 임베딩 파일 위치 안내

6. **[04_해야할일_체크리스트.md](./04_해야할일_체크리스트.md)**: 진행 상황 체크리스트

7. **[05_Docker_클라우드_배포.md](./05_Docker_클라우드_배포.md)**: 클라우드 배포 가이드 (나중에)

8. **[06_작업_순서_및_백그라운드_실행.md](./06_작업_순서_및_백그라운드_실행.md)**: 작업 순서 및 백그라운드 실행

9. **[07_CMD_conda_오류_해결.md](./07_CMD_conda_오류_해결.md)**: conda 오류 해결 가이드

10. **[00_team_rules.md](./00_team_rules.md)**: 팀 규칙
   - 백엔드 폴더 구조
   - 환경 설정
   - 역할 분담

## 🚀 빠른 시작

> **현재 상태 확인**: 임베딩 완료 ✅, Docker 실행 완료 ✅

### 지금 바로 실행하기

**1. DB 스키마 생성** (5분)
- DBeaver에서 `scripts/db_loading/db_setup.sql` 실행
- 또는: `python scripts/db_loading/setup_db.py`

**2. DB 적재** (10-20분)
```bash
conda activate final_env
cd scripts/db_loading
python load_hana_to_db.py
```

**3. 검증** (1분)
```bash
python verify_db_load.py
```

**자세한 가이드**: [00_빠른_실행_가이드.md](./00_빠른_실행_가이드.md) 참조

---

### 전체 파이프라인 (처음부터)

```bash
# 1. 환경 설정
conda env create -f scripts/environment.yml
conda activate final_env
pip install -r scripts/requirements.txt

# 2. Docker로 PostgreSQL 실행
cd scripts/docker
docker-compose up -d

# 3. DB 스키마 생성 (DBeaver에서 실행)
# scripts/db_loading/db_setup.sql

# 4. 임베딩 생성 (이미 완료했다면 생략)
cd ../db_loading
python generate_embeddings_hana.py

# 5. DB 적재
python load_hana_to_db.py

# 6. 검증
python verify_db_load.py
```

## 주요 답변 요약

### Q: 왜 OpenAI Embedding API를 사용해야 하는가?
- ✅ 한국어 문맥 이해 능력
- ✅ 실시간 성능 (200-500ms)
- ✅ 비용 효율성 (4,653건 기준 약 $0.09)
- ✅ ERD 스키마와 호환 (1536차원)

### Q: 개발 순서 (백 → 프론트 vs 프론트 → 백)?
- ✅ **프론트 → 백 접근 방식이 올바릅니다**
- 화면을 먼저 만들면 필요한 데이터 구조가 명확
- 반복적 개발이 더 효율적

### Q: 임베딩 먼저? 적재 먼저?
- ✅ **임베딩 먼저**
- 임베딩 생성 → DB 적재 순서

### Q: Docker Hub 계정 필요?
- ❌ **필수 아님** (로컬 개발)

### Q: 같은 터미널에서 실행 가능?
- ✅ **새 터미널 사용 권장** (독립 실행 가능)

## 📁 스크립트 위치

```
scripts/
├── db_loading/
│   ├── generate_embeddings_hana.py    # 임베딩 생성 (✅ 완료)
│   ├── setup_db.py                    # DB 스키마 생성 (Python)
│   ├── load_hana_to_db.py            # DB 적재 ⭐
│   ├── verify_db_load.py             # 검증
│   ├── db_setup.sql                  # DB 스키마 SQL ⭐
│   └── README.md
├── docker/
│   └── docker-compose.yml            # Docker 설정 (✅ 실행됨)
├── environment.yml
├── requirements.txt
└── .env.example
```

## 다음 단계

1. ✅ 환경 설정 완료
2. ✅ 스크립트 작성 완료
3. ⏳ 테스트 데이터 적재 (100-200개)
4. ⏳ 화면 연결 테스트
5. ⏳ 전체 데이터 적재


