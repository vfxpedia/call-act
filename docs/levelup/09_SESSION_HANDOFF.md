# 세션 인수인계 문서 (2026-02-11)

## 프로젝트 전환 요약

팀 프로젝트 → 개인 프로젝트로 전환.
- **작업 디렉토리**: `backend_dev/`, `frontend_dev/` (개인 레포)
- **팀 레포** (`backend/`, `frontend/`): git submodule, 이후 참조용
- **동기화 완료**: frontend/ → frontend_dev/ 42개 파일, backend/ → backend_dev/ 테스트 파일

---

## 세션별 현재 상태 및 다음 작업

### 1. Backend 세션

**소유 디렉토리**: `backend_dev/app/`

**완료된 작업**:
- 로컬 E2E 전환 (RunPod → 워크스테이션 2x RTX 5080)
- AWQ 양자화 (kanana-8B, analysis → 각 5.4GB)
- 플러거블 STT/TTS 아키텍처 (`stt_engine.py`, `tts_engine.py`)
- STT/TTS 엔진 전환 API (`/api/v1/settings/`)
- Phase A-C 고도화 (STT 57→100%, VocabGate 67→100%)
- Phase 3: M-1 STT 비교 → M-2 키워드+흐름 인식 → M-3 RAG 검색 품질
- RAG 카드 검색 수정 (card_name 매핑, WHERE 필터, 임베딩 활성화)

**핵심 파일 (수정 빈도순)**:
| 파일 | 역할 |
|------|------|
| `app/rag/pipeline/search.py` | RAG 검색 메인 (M-3 Fix-1~4 포함) |
| `app/rag/pipeline/pipeline.py` | 카드 생성 + flow 병합 |
| `app/rag/cache/keyword_doc_index.py` | 키워드 역색인 (F-1) |
| `app/rag/flow/flow_tracker.py` | 상담 흐름 예측 (M-2) |
| `app/core/prompt.py` | LLM 프롬프트 (SUMMARIZE, EDUCATION) |
| `app/api/v1/endpoints/consultations.py` | 상담 CRUD API |
| `app/audio/stt_engine.py` | STT 엔진 팩토리 |
| `app/llm/education/tts_engine.py` | TTS 엔진 팩토리 |

**다음 작업 (우선순위순)**:
1. **ACW 고도화** — AI 요약 상세화 + category_raw 자동 분류
   - Plan 파일: `.claude/plans/glowing-doodling-garden.md`
   - `prompt.py` SUMMARIZE_SYSTEM_PROMPT 수정 (result 구조화, category_raw 추가)
   - `consultations.py` SaveConsultationRequest + SQL에 category_raw 추가
2. **F-2 VibeVoice Realtime 검증** — 실시간 STT 스트리밍 테스트
3. **F-3 kanana-8B 요약 비교** — kanana-2.1B vs 8B 요약 품질

**환경 설정**:
```bash
# WSL2에서 실행
source ~/miniconda3/bin/activate callact-vllm
cd /mnt/c/Users/AI-WS01/projects/call-act/backend_dev

# 서버 시작
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 모델 서빙 (orchestrator)
bash local_servers/orchestrator.sh start education  # 또는 acw
```

**환경 변수** (`.env`):
```
STT_ENGINE=openai-whisper   # openai-whisper | qwen3-asr | faster-whisper
TTS_ENGINE=edge-tts         # edge-tts | qwen3-tts | supertonic
RAG_FLOW_PREDICTION=1       # 흐름 예측 활성화
RAG_KEYWORD_INDEX=1         # 키워드 역색인 활성화
RAG_MIN_RELEVANCE=0.08      # 최소 relevance 임계값
```

---

### 2. Frontend 세션

**소유 디렉토리**: `frontend_dev/src/`

**완료된 작업**:
- Level 01: 문서 타입, 키보드 단축키, 피드백 모달, 문서 상세보기
- Level 02 Phase 1 전체 (F-1~F-7): 시뮬레이션 매핑, AI 요약 표시, 유사도 정렬, 포커싱, 키보드, 클립보드
- 검색 유사도 하드코딩 제거 (백엔드 실제 점수 사용)
- 문서 상세보기 fullText Markdown 렌더링
- STT/TTS 엔진 전환 UI (Sidebar 드롭다운)
- 동적 URL 설정 (config.ts)

**핵심 파일**:
| 파일 | 역할 |
|------|------|
| `src/app/pages/RealTimeConsultationPage.tsx` | 실시간 상담 메인 (8000줄+) |
| `src/app/pages/AfterCallWorkPage.tsx` | 후처리(ACW) 페이지 |
| `src/app/pages/SimulationPage.tsx` | 교육 시뮬레이션 |
| `src/api/consultationApi.ts` | 상담 API + 저장 분기 로직 |
| `src/config.ts` | API/WS URL 동적 감지 |
| `src/config/engineConfig.ts` | STT/TTS 엔진 설정 |
| `src/app/components/layout/Sidebar.tsx` | 엔진 전환 드롭다운 |
| `src/utils/documentTransformer.ts` | Markdown 변환 유틸 |

**다음 작업**:
1. **ACW 페이지에 category_raw 표시** — Backend가 category_raw 추가 후 연동
2. **예측 카드 UI 차별화** — `_from_flow_prediction` 배지/색상 표시
3. **검색 레이어 UX 개선** — 키워드 하이라이팅, 스크롤 최적화

**개발 실행**:
```bash
cd /mnt/c/Users/AI-WS01/projects/call-act/frontend_dev
npm run dev  # Vite dev server (포트 5173)
```

---

### 3. Data 세션

**소유 디렉토리**: `data-preprocessing_dev/`, `backend_dev/app/rag/resources/`

**완료된 작업**:
- 카드 상품 키워드 100% 채움 (Phase B)
- 서비스 가이드 card_name 매핑 (204건, 8개 카드그룹)
- 임베딩 생성 완료 (card_products + service_guides)
- vocab.json 확장 (Phase A weak_intent)

**핵심 파일**:
| 파일 | 역할 |
|------|------|
| `data-preprocessing_dev/preprocess/teddycard/` | 전처리 스크립트 |
| `backend_dev/app/rag/resources/vocab.json` | VocabGate 사전 |
| `backend_dev/app/rag/resources/keywords_dict.json` | 키워드 사전 |
| `backend_dev/app/rag/resources/keywords_dict_refine.json` | STT 교정 사전 |
| `backend_dev/app/db/data/teddycard/` | JSON 원본 데이터 |

**다음 작업**:
1. **D-1 fullText 전처리** — 서비스 가이드 본문 구조화 (중기)
2. **리볼빙 관련 문서 보강** — M-3에서 발견된 콘텐츠 갭
3. **임베딩 모델 업그레이드 검토** — 한국어 세부 의미 구분 개선

---

### 4. AI/ML 세션 (팀장)

**소유 디렉토리**: `docs/`, `CLAUDE.md`

**완료된 작업**:
- Phase 3 전체 완료 (M-1 STT 비교, M-2 키워드+흐름, M-3 RAG 품질)
- Level 02 Phase 1-2 완료
- 고도화 분석 문서 작성
- 비교 대시보드 v2.6 (`backend_dev/local_servers/comparison_dashboard.py`)

**핵심 문서**:
| 문서 | 내용 |
|------|------|
| `docs/levelup/00_OVERVIEW.md` | 전체 고도화 계획 |
| `docs/levelup/08_M3_SEARCH_QUALITY.md` | M-3 RAG 품질 개선 결과 |
| `docs/levelup/07_M2_FLOW_PREDICTION.md` | M-2 상담 흐름 인식 |
| `docs/levelup/M1_STT_RESULTS.md` | M-1 STT 비교 결과 |
| `docs/levelup/03_PHASE_ABC_RESULTS.md` | Phase A-C 결과 |

**다음 작업**:
1. **ACW 고도화 조율** — Backend/Frontend 세션 간 category_raw 통합 관리
2. **STT 재평가** — ngrok 테스트에서 팀 원본 STT가 더 나은 결과 관찰. 원인 분석 필요
3. **RAG 라우팅 개선** — M-3에서 발견된 2개 라우팅 실패 (리볼빙 해지, SOL트래블 수수료)

---

## DB 구조 (PostgreSQL)

```
Host: localhost:5555
DB: callact_db
User: callact_admin / callact_pwd1
```

주요 테이블: `consultations`, `employees`, `customers`, `card_products`, `service_guide_documents`, `keywords`

**DB 재구축** (필요 시):
```bash
cd backend_dev/app/db/scripts
python 01a_setup_callact_db.py        # 스키마 + 기본 데이터
python 01b_populate_mock_data.py      # Mock 확장 데이터
```

---

## 로컬 모델 서빙

| 포트 | 모델 | GPU | VRAM |
|------|------|-----|------|
| 8100 | kanana-2.1B | GPU 0 | 4GB |
| 8101 | kanana-8B-AWQ | GPU 0 | 5.4GB |
| 8102 | kanana-analysis-AWQ | GPU 1 | 5.4GB |
| 8103 | Qwen3-TTS | GPU 1 | 2.4GB |
| 8104 | Qwen3-ASR | GPU 0 | 4.4GB |

모델 파일: `backend_dev/models/` (61GB, .gitignore)

---

## 알려진 이슈

1. **STT 팀 원본 vs 개선 버전**: ngrok 테스트에서 팀 원본 VAD 설정이 더 나은 결과를 보임. 원인: 팀 원본의 1500ms/0.025/1000ms VAD가 짧은 발화에 최적화되어 Whisper에 작은 청크 전달 → 더 정확
2. **리볼빙 해지 검색 실패**: 벡터 검색에서 관련 문서 매칭 약함 (콘텐츠 갭). 데이터 보강 필요
3. **라우팅 오류**: "테디카드 SOL트래블 수수료" → card_usage로 잘못 라우팅. 라우팅 로직 개선 필요
4. **category_raw 미구현**: Plan 문서는 있으나 아직 코드 미적용
