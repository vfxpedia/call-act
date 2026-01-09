**1️⃣ 개발 환경 설정**

- 가상환경
    
    environment.yml
    
    ```python
    name: final_env
    channels:
      - conda-forge
      - defaults
    
    dependencies:
      - python=3.11
      - pip
    ```
    
    requirements.txt
    
    ```python
          - openai
          - langchain
          - langchain-community
          - langchain-core
          - langchain-openai
          - python-dotenv
          - requests
          - pandas
          - numpy
          - selenium
          - beautifulsoup4
          - pdfplumber
          - llama-parse
          - psycopg2-binary
    ```
    
    <aside>
    
    환경 변수 설정
    
    `.env` 파일 생성:
    
    ```
    # OPENAI
    OPENAI_API_KEY=
    # HUGGINGFACE
    HF_TOKEN=
    # RUNPOD
    RUNPOD_API_KEY=
    
    # R-DB
    DB_HOST=localhost
    DB_PORT=5432
    DB_USER=
    DB_PASSWORD=
    DB_NAME=
    
    # 모델 파일을 저장할 로컬 폴더 경로
    MODEL_CACHE_DIR=./model_cache
    
    ```
    
    실행 방법
    
    ```
    # 0. 저장소 클론
    git clone <repository-url>
    
    # 1. 새 conda 가상환경 생성
    conda env create -f environment.yml
    
    # 2. 가상환경 활성화
    conda activate final_env
    ```
    
    ```
    # 가상환경 활성화
    conda activate final_env
    
    # pip 최신화
    python -m pip install --upgrade pip
    
    # conda 가상환경 삭제
    conda remove -n 삭제할가상환경 --all
    
    # fastapi 실행
    uvicorn main:app --reload
    ```
    
    </aside>
    
- 폴더 구조
    
    ```python
    backend/
    ├── .env                       
    ├── .github                    
    ├── .gitignore                 
    ├── app/                       # FastAPI App
    │   ├── main.py                # FastAPI 엔트리포인트
    │   ├── api/                   # HTTP API (Controller 역할)
    │   │   ├── v1/                # API 버전 관리
    │   │   ├── endpoints/         # 실제 엔드포인트 구현부
    │   │   │   ├── user.py      
    │   │   │   ├── item.py      
    │   │   │   └── ...          
    │   │   └── routers.py         # 모든 endpoint router를 모아 main에 연결
    │   ├── core/                  # 전역 설정 및 인프라 공통 로직
    │   │   └── config.py          # 환경변수 로딩, Settings 정의
    │   ├── crud/                  # llm에서 만들어진 객체를 schema를 이용하여 crud 명령어 구현(Create, Read, Update, Delete)
    │   │   ├── user.py          
    │   │   ├── item.py          
    │   │   └── ...              
    │   ├── db/                    # DB 초기화 및 세션 관리
    │   │   ├── base.py            # DB 연결 엔진, 세션 생성
    │   │   └── session.py         # DB 세션 생성/관리 (의존성으로 주입)
    │   ├── llm/                   # LLM 관련 코드
    │   │   ├── base.py            # LLM 공통 인터페이스 (prompt, context 규격)
    │   │   ├── openai_client.py   # OpenAI API 호출 전용 클라이언트
    │   │   ├── runpod_client.py   # RunPod GPU LLM 서버 호출 클라이언트
    │   │   └── router.py          # 요청 조건에 따라 사용할 LLM 선택 (라우팅)
    │   ├── rag/                   # RAG 관련 코드
    │   │   ├── pipeline.py        # RAG 전체 흐름 오케스트레이션
    │   │   └── retriever.py       # 벡터 DB 검색 로직
    │   ├── schemas/               # 
    │   │   ├── common.py          # 공통 응답 포맷
    │   │   └── chat.py 
    │   │   └── ...           
    │   └── utils/                 # util 함수 모음
    ├── docker/                    # docker 설정
    │   ├── docker-compose.yml     
    │   └── Dockerfile             
    ├── docs/                      # 문서 모음 (실행 방법, 도구 정리 등)
    ├── environment.yml            
    ├── requirements.txt           
    ├── README.md                  
    └── tests/                     # 테스트 코드
        ├── test_user.py           
        └── test_item.py
        └── ...            
    ```
    

**2️⃣ 산출물 일정**

![image.png](https://img.notionusercontent.com/s3/prod-files-secure%2F2e42b292-3597-492a-9d2f-caaf0ff36a48%2Fe414479d-304a-43be-9531-ead40d4f6448%2Fimage.png/size/w=2000?exp=1767893620&sig=LOHuEa97RCfhiE9_K_3TSM0VoA1H4vze4lcO3GLqwxg&id=2e264913-6c11-8053-8539-c8c63f1d5d22&table=block&userId=bb019bce-1360-4b02-b954-086b51248495)

1/9

- 수집데이터, 수집된 데이터 및 전처리, 인공지능 데이터 전처리 결과서

1/12 

- 인공지능 학습 결과서, 학습된 인공지능 모델
- 시스템 아키텍처
- 데이터베이스 설계 문서 (ERD)

3️⃣ **다이어그램**

- **블록 다이어그램**
    
    https://www.mermaidchart.com/app/projects/95a88fd4-afd1-41f1-a29a-1b9c0cc56755/diagrams/54c70b42-410d-46d0-a787-3f2777ea89b9/version/v0.1/edit
    

![Block diagram-2026-01-08-023336.png](https://img.notionusercontent.com/s3/prod-files-secure%2F2e42b292-3597-492a-9d2f-caaf0ff36a48%2F42d92a8a-e89b-4f65-8b40-32f99e7813d5%2FBlock_diagram-2026-01-08-023336.png/size/w=2000?exp=1767893652&sig=KzTagUPg45g2_Esh7q9-2wH8PGu5XqJZrss2o76cJSg&id=2e264913-6c11-80c7-8eba-c8def2a172cf&table=block&userId=bb019bce-1360-4b02-b954-086b51248495)

- **프로젝트 시퀀스 다이어그램**
    
    https://www.mermaidchart.com/app/projects/95a88fd4-afd1-41f1-a29a-1b9c0cc56755/diagrams/cb8e3395-241d-419a-ad50-f67df3e9605d/version/v0.1/edit
    

4️⃣ **역할 분담**

- 벡터 DB 구축
    - 임베딩 → 벡터 DB 구축
- AI
    - 실시간 상담 지원
        - 실시간 웹소켓
        - STT
        - 카드사 단어 사전 구축
        - 단어 사전에서 현재 & 다음 키워드 추출용 매핑
        - **[핵심] 현재 키워드 & 다음 키워드로 벡터 DB 라우팅 후 유사도 검색**
        - 찾은 문서 LLM에 전달
        - GPT - 요약, 전문 생성 후 client로 전달
        - BC - 상담가이드 생성 후 client로 전달
    
    ---
    
    - 상담 종료 후
        - 대화 전문 화자 분리
        - 대화 전문으로 현재 상담 요약, 후처리 문서 생성
        - (RDB 구축 후 → RDB에서 유사 사례 검색)
        - 대화 전문으로 텍스트 감정 분석 및 피드백
        - 상담 후 데이터 RDB에 저장
    - 교육 시뮬레이션
        - 고객 페르소나 (EXAONE)
        - TTS (gpt-4o-mini-tts)