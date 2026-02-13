# CALL:ACT 프로젝트 협업 가이드

## 세션 역할 분담

| 세션 | 담당 | 소유 디렉토리 | 절대 수정 금지 |
|------|------|--------------|---------------|
| **Backend** | API, 모델 서빙, DB, RAG | `backend/app/`, `backend/local_servers/` | `frontend/src/` |
| **Frontend** | UI/UX, 컴포넌트, 페이지 | `frontend/src/` | `backend/app/` |
| **Data** | 전처리, 임베딩, 프롬프트 | `data-preprocessing_dev/`, `backend/app/rag/resources/` | `frontend/src/` |
| **AI/ML (팀장)** | STT 품질, 키워드 추출, RAG 개선, 프로젝트 총괄 | `docs/`, `CLAUDE.md` | - (크로스세션 조율 권한) |

## 공유 파일 (수정 전 반드시 확인)

아래 파일은 여러 세션이 동시에 건드릴 수 있으므로 **수정 전 git pull 필수**:
- `backend/app/api/v1/routers.py` (라우터 등록)
- `backend/.env` (환경 변수)
- `frontend/src/config.ts` (API URL)
- `frontend/src/config/mockConfig.ts` (개발 설정)

## 브랜치 전략

```
main (프로덕션, GitActions 자동 배포)
├── feat/backend-xxx    ← Backend 세션
├── feat/frontend-xxx   ← Frontend 세션
├── feat/data-xxx       ← Data 세션
└── feat/ml-xxx         ← AI/ML 세션
```

- 작업 시작: `git checkout -b feat/세션-기능명`
- 완료 후: main에 머지 (충돌 시 해당 세션 소유자가 해결)
- **main 직접 커밋은 핫픽스만**

## 현재 작업 상태 (각 세션이 업데이트)

### Backend (최종 업데이트: 2026-02-10 15:30)
- [x] 로컬 E2E 전환 완료 (RunPod → 워크스테이션)
- [x] AWQ 양자화 (kanana-8B, analysis)
- [x] 플러거블 STT/TTS 아키텍처
- [x] STT/TTS 엔진 전환 UI + Settings API
- [x] 한국어 TTS 전처리 모듈
- [x] ngrok 외부 접속
- [x] Level 02: whisper 할루시네이션 필터 강화, prompt [메모] 추가, 유사도 점수 실제화, 상담 저장 API 안정화
- [x] D-2: card_generator.py LLM 환각 방지 (_DB_PROTECTED_FIELDS)
- [ ] Vercel + EC2 배포 연결
- [ ] **F-8 실데이터**: FeedbackModal 닫기 시 기본 피드백 저장 검토 (아래 전달사항 참고)

### Frontend (최종 업데이트: 2026-02-11 10:00) 🟢 활성
- [x] Level 01: 문서 타입 표시, 키보드 단축키, 피드백 모달, 문서 상세보기 개선
- [x] Level 02 Phase 1 전체 완료 (6건): F-1, F-3~F-7
- [x] 검색 유사도 하드코딩 제거 (searchSimulator.ts → 백엔드 실제 점수 사용)
- [x] 상담 상세 모달: transcript/referenced_documents 필드 매핑 수정
- [x] F-2/B-1: [메모] 섹션 AI 요약 — 프롬프트에 이미 포함 확인 (prompt.py:324)
- [x] **F-8**: FeedbackModal onClose/ESC/오늘보지않기 시 기본 feedbackScores localStorage 저장 완료
- [x] **F-10**: ACW category_raw localStorage 전달 — 이미 구현 확인 완료
- [x] **F-11**: 가이드 말풍선 CSS zoom 보정 (TutorialGuide.tsx: getBoundingClientRect zoom 보정, 경계 체크 CSS 좌표계 통일)
- [x] **F-12**: 교육 시뮬레이션 페이지 가이드 배지 추가 (SimulationPage: 웰컴→우수사례→기본시나리오→시작하기 4단계 가이드 + 헤더 가이드 버튼 연동)
- **현재**: F-11, F-12 완료 후 빌드/배포 완료

### Data (최종 업데이트: 2026-02-10 23:10)
- [x] D-3/M-2 지원: card_products 키워드 현황 분석 완료
  - Phase B에서 398건 전체 100% 키워드 채움 (이전 49% 없음 → 해결됨)
  - 품질 문제: 범용 키워드 과다(혜택 85%, 연회비 81%), 범용만 있는 카드 10건
  - keyword_dictionary 교차: 65개 중 26개만 매칭(40%), 39개 미등록
- [x] D-4/D-1: fullText 전처리 중기 계획 수립
  - DB 분석: structured.detailContent가 이미 요약본 제공 (1251/1251, 398/398)
  - content 원본은 '#' 헤더, 중복 텍스트 포함 → 중기 정리 대상
  - 중기 계획: 마크다운 보존, 중복 제거, 원본 포맷(표/목록) 보존
- [x] D-5: CLAUDE.md Data 섹션 업데이트
- [x] **D-7**: `populate_guide_card_names.py` 01a 파이프라인 통합 완료 (2026-02-10 23:10)
  - M 세션에서 DB 직접 실행한 204건 매핑을 01a 재실행 시에도 자동 적용되도록 연결
  - `01a_setup_callact_db.py` Step 5-2에서 테디카드 적재 후 자동 호출
  - 멱등성 검증 완료 (이미 매핑된 상태에서 재실행 시 +0건, 정상)
- [x] **D-8**: 전이 모델 데이터 검증 완료 (2026-02-11 01:30)
  - 488건 다중 카테고리 통화, 89개 전이 패턴 (자기전이 제외), 빈도>=3: 52개
  - 모델 29개 전이 중 20개 정확 일치, **9개 불일치** (아래 상세)
  - 불일치 원인 및 권고사항 → AI/ML 팀장에게 보고 완료
- [ ] D-6: keyword_dictionary 보강 - card_products 전용 키워드 39개 + STT 동의어 등록 (M-2 이후)

### AI/ML 팀장 (최종 업데이트: 2026-02-11 02:30) 🟢 세션 활성
- [x] 프로젝트 합류 및 전체 현황 파악 완료
- [x] Level 02 Phase 1-2: B-1 확인, D-2 수정 완료, F-8 Mock OK / 실데이터 조사 완료
- [x] STT 에코 방지, 상담 상세 모달 수정, 유사도 점수 실제화, Admin/Stats 빈화면 수정
- [x] F-8 실데이터 10건 backfill 완료, Frontend FeedbackModal 수정 완료
- [x] **Phase 3 M-1 완료**: STT 3개 엔진 비교 → faster-whisper-large-v3 최적
- [x] **Phase 3 M-2 단계 1-2 완료**: 비정보성 발화 필터 + STT 교정 사전
- [x] **아키텍처 v2 설계 문서**: `docs/levelup/05_ARCHITECTURE_V2.md`
  - 듀얼 트랙 STT, 키워드-문서 캐시, 4단계 응답, GPU 리소스 설계
- [x] **F-1 완료**: 키워드-문서 역색인 프로토타입 (5,342 키워드, 조회 0.75ms)
  - `backend/app/rag/cache/keyword_doc_index.py` → `search.py` 통합
  - 벡터 검색 전 역색인 조회 → 결과 병합 (`RAG_KEYWORD_INDEX=1`)
- [x] **"분실" 단독 검색 score=0.000 버그 수정 (2026-02-10 23:30)**:
  - 원인: `terms.py:_expand_guide_terms()` "분실"→"분실도난" 치환 시 원본 삭제
  - 수정: 원본 term 유지 + 확장어 추가 (score 0.000→0.529)
- [x] **M-2 단계3 완료 (2026-02-11 01:00)**: 상담 흐름 인식
  - 모듈: `backend/app/rag/flow/` (flow_model.py, flow_tracker.py)
  - 83개 전이 패턴 (6,533건 상담 분석), 25개 카테고리 키워드 매핑
  - 통합: search.py + pipeline.py → nextStep에 예측 카드 병합
  - `RAG_FLOW_PREDICTION=1` 환경변수로 제어
  - 문서: `docs/levelup/07_M2_FLOW_PREDICTION.md`
- [x] **RAG 카드 검색 근본 수정 완료 (2026-02-10 23:00)**:
  - D-7: guide metadata card_name 매핑 완료 (204건, 8개 카드그룹)
  - B-7: `db.py:build_where_clause()` 가이드 테이블 card_name 필터 추가
  - B-8: card_products 임베딩 활성화 (`NULL::vector` → `embedding`)
  - B-8b: `_source_sql()` 가이드 metadata에 card_name 반영
  - **검증**: "나라사랑카드 분실" → 정확한 FAQ 반환 (score=0.556), 카드별 결과 분리 확인
- [x] **M-3 완료 (2026-02-11 02:30)**: RAG 검색 품질 종합 개선
  - 진단: 17쿼리 유형 × 5가지 이슈 (score 인플레이션, 범용 문서, 병합 순서, 임계값, 제목 무관)
  - Fix-1: 키워드 인덱스 score 정규화 (1.0→0.45, `relevance * 0.45`)
  - Fix-2: score 기반 병합 (키워드 우선 → score 순 인터리빙)
  - Fix-3: 최소 relevance 임계값 (`RAG_MIN_RELEVANCE=0.08`)
  - Fix-4: 제목-쿼리 관련성 감쇠 (제목 무관 × 0.15 → 자동 필터)
  - 결과: "Gift 카드"(100→제거), "한도 조회" 정확 매칭, 11/11 전용 테스트 통과
  - 문서: `docs/levelup/08_M3_SEARCH_QUALITY.md`
- [ ] **F-2**: VibeVoice Realtime 스트리밍 모드 API 검증
- [ ] **F-3**: kanana-8B vs GPT-4.1-mini 요약 품질 비교
- [ ] **F-5**: 듀얼 트랙 WebSocket 프로토타입 (F-2 이후)

#### 📋 각 세션 전달사항 (2026-02-11 01:00 갱신)
> 모든 세션은 `docs/levelup/02_LEVEL02_DISCUSSION.md`를 기준으로 작업합니다.
> **작업 완료 시 반드시** 이 섹션과 Discussion 문서 "진행 이력"에 타임스탬프와 함께 기록해주세요.

---

##### Backend에게

| # | 작업 | 상세 | 상태 |
|---|------|------|------|
| B-1~8b | ~~이전 작업~~ | 모두 완료 | ✅ |
| B-5 | faster-whisper STT 엔진 통합 검토 | 이전 지시 유지 | 🔲 이번 주 |
| B-6 | WHISPER_PROMPT 테디카드 추가 | 이전 지시 유지 | 🔲 즉시 가능 |
| B-9 | M-2 흐름 예측 코드 리뷰 | `backend/app/rag/flow/` 모듈, `search.py`, `pipeline.py` 변경 확인 | 🔲 리뷰 |
| B-10 | ACW category_raw 저장 경로 | `consultations.py`, `followup.py`에 categoryRaw 필드 + SQL 반영 | 🔲 확인 필요 |
| B-11 | 키워드 인덱스 빌드 확인 | `main.py:lifespan()`에서 `build_index()` 호출되는지 확인 | 🔲 확인 |

##### Frontend에게

| # | 작업 | 상세 | 상태 |
|---|------|------|------|
| F-1~8 | ~~Phase 1-2 전체~~ | 모두 완료 | ✅ |
| F-9 | 흐름 예측 카드 UI 차별화 | 이미 구현 확인 (배지/라벨) | ✅ |
| F-10 | ACW category_raw localStorage 전달 | 이미 구현 확인 | ✅ |
| F-11 | 가이드 말풍선 CSS zoom 보정 | TutorialGuide.tsx zoom 보정 + 경계 체크 통일 | ✅ |
| F-12 | 시뮬레이션 페이지 가이드 | SimulationPage에 4단계 가이드 추가 + 헤더 연동 | ✅ |

##### Data에게

| # | 작업 | 상세 | 상태 |
|---|------|------|------|
| D-3~7 | ~~이전 작업~~ | 모두 완료 | ✅ |
| D-6 | keyword_dictionary 보강 | card_products 전용 키워드 39개 + STT 동의어 등록 | 🔲 M-2 이후 |
| D-8 | 전이 모델 데이터 검증 | `flow_model.py` 전이 패턴 83개가 실데이터와 일치하는지 | 🔲 리뷰 |

##### AI/ML 팀장 (현재 진행)

| # | 작업 | 상태 |
|---|------|------|
| ~~M-0~~ | ~~F-8 실데이터 10건 backfill~~ | ✅ 2026-02-10 16:30 |
| ~~M-1~~ | ~~STT 비교 테스트~~ | ✅ 2026-02-10 20:04 |
| ~~M-2 단계1-2~~ | ~~비정보성 필터 + STT 교정 사전~~ | ✅ 2026-02-10 20:20 |
| ~~F-1~~ | ~~키워드-문서 역색인~~ | ✅ 2026-02-10 21:40 |
| ~~RAG 진단~~ | ~~카드 검색 실패 근본 원인 분석~~ | ✅ 2026-02-10 22:30 |
| ~~RAG 수정~~ | ~~D-7+B-7+B-8+B-8b 직접 수정 + 검증~~ | ✅ 2026-02-10 23:00 |
| ~~M-2 단계3~~ | ~~상담 흐름 인식 (전이 모델 + 키워드인덱스 연동)~~ | ✅ 2026-02-11 01:00 |
| ~~"분실" 버그~~ | ~~_expand_guide_terms 원본 term 삭제 버그~~ | ✅ 2026-02-10 23:30 |
| **M-3** | RAG 검색 품질 개선 (relevance threshold, 중복방지) | 🔲 |
| **F-2** | VibeVoice Realtime 스트리밍 검증 | 🔲 |
| **F-3** | kanana-8B vs GPT-4.1-mini 요약 비교 | 🔲 |

---

- **전체**: M-2 단계3 흐름 인식 완료! 다음: M-3 RAG 품질, F-2 VibeVoice Realtime, F-3 요약 비교
- **작업 규칙**: 완료 시 CLAUDE.md 본인 섹션 + Discussion 진행이력에 `날짜 시:분` 타임스탬프 필수

## 로컬 모델 서빙 (워크스테이션 전용)

```bash
# 교육 모드 시작
cd backend && bash local_servers/orchestrator.sh start education

# 후처리(ACW) 모드 시작
cd backend && bash local_servers/orchestrator.sh start acw

# 상태 확인
bash local_servers/orchestrator.sh status
```

| 포트 | 모델 | GPU | 용도 |
|------|------|-----|------|
| 8100 | kanana-2.1B | GPU 0 | 교육 시뮬레이션 |
| 8101 | kanana-8B-AWQ | GPU 0 | 텍스트 교정 |
| 8102 | kanana-analysis-AWQ | GPU 1 | 성격 분류 |
| 8103 | Qwen3-TTS | GPU 1 | 음성 합성 |
| 8104 | Qwen3-ASR | GPU 0 | 로컬 STT |
| 8000 | FastAPI + SPA | CPU | 백엔드 + 프론트 |

## API 엔드포인트 정리

| 경로 | 메서드 | 설명 |
|------|--------|------|
| `/api/v1/health` | GET | 헬스체크 |
| `/api/v1/settings/engines` | GET | STT/TTS 엔진 상태 |
| `/api/v1/settings/stt-engine` | POST | STT 전환 |
| `/api/v1/settings/tts-engine` | POST | TTS 전환 + 프리로드 |
| `/api/v1/consultations` | GET/POST | 상담 CRUD |
| `/api/v1/notices` | GET/POST | 공지사항 |
| `/api/v1/employees` | GET | 사원 목록 |
| `/api/v1/customers` | GET | 고객 정보 |
| `/api/v1/education/*` | POST | 교육 시뮬레이션 |
| `/api/v1/followup/*` | POST | 후처리 (화자분리, 교정, 분류) |
| `/ws/call` | WS | 실시간 상담 (STT + RAG) |
| `/ws/edu` | WS | 교육 모드 (시뮬레이션 + TTS) |

## 규칙

1. **커밋 메시지**: `[Feat]`, `[Fix]`, `[Refactor]`, `[Docs]` 접두사 사용
2. **팀 원본 코드 보호**: `whisper.py`, `call_websocket.py`의 핵심 로직 변경 금지
3. **VAD 파라미터 변경 금지**: `useVoiceRecoders.ts`의 1500ms/0.025/1000ms 유지
4. **models/ 디렉토리**: .gitignore에 포함됨, git에 올리지 않음
5. **환경**: WSL2 + Miniconda `callact-vllm` + PyTorch 2.9.1+cu128
