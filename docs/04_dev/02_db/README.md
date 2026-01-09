# 하나카드 데이터 DB 적재 프로젝트

## 문서 목록

1. **[00_hana_db_loading_설계.md](./00_hana_db_loading_설계.md)**: 전체 설계 문서
   - OpenAI 임베딩 API 사용 이유
   - 스키마 및 화면 구성 검증
   - 데이터 매핑 상세
   - 테스트 데이터 전략

2. **[01_개발환경_설정_가이드.md](./01_개발환경_설정_가이드.md)**: 개발 환경 설정 가이드
   - Conda 환경 설정
   - PostgreSQL + pgvector 설정
   - Docker 사용법
   - 주요 질문 답변

3. **[02_실행_가이드.md](./02_실행_가이드.md)**: 실행 가이드
   - 빠른 시작
   - 상세 실행 순서
   - 트러블슈팅

4. **[00_team_rules.md](./00_team_rules.md)**: 팀 규칙
   - 백엔드 폴더 구조
   - 환경 설정
   - 역할 분담

## 빠른 시작

```bash
# 1. 환경 설정
conda env create -f ../../scripts/environment.yml
conda activate final_env
pip install -r ../../scripts/requirements.txt

# 2. Docker로 PostgreSQL 실행
cd ../../scripts/docker
docker-compose up -d

# 3. DB 스키마 생성 (DBeaver에서 실행)
# scripts/db_loading/db_setup.sql

# 4. 테스트 데이터 적재
cd ../../scripts/db_loading
python generate_embeddings_hana.py --limit 200
python load_hana_to_db.py --limit 200
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

## 스크립트 위치

```
scripts/
├── db_loading/
│   ├── generate_embeddings_hana.py
│   ├── load_hana_to_db.py
│   ├── verify_db_load.py
│   ├── db_setup.sql
│   └── README.md
├── docker/
│   └── docker-compose.yml
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


