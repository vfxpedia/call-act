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

### Frontend (최종 업데이트: 2026-02-10 16:30) 🟢 세션 활성
- [x] Level 01: 문서 타입 표시, 키보드 단축키, 피드백 모달, 문서 상세보기 개선
- [x] Level 02 Phase 1 전체 완료 (6건): F-1, F-3~F-7
- [x] 검색 유사도 하드코딩 제거 (searchSimulator.ts → 백엔드 실제 점수 사용)
- [x] 상담 상세 모달: transcript/referenced_documents 필드 매핑 수정
- [x] F-2/B-1: [메모] 섹션 AI 요약 — 프롬프트에 이미 포함 확인 (prompt.py:324)
- [x] **F-8**: FeedbackModal onClose/ESC/오늘보지않기 시 기본 feedbackScores localStorage 저장 완료

### Data (최종 업데이트: 2026-02-10 16:30)
- [x] D-3/M-2 지원: card_products 키워드 현황 분석 완료
  - Phase B에서 398건 전체 100% 키워드 채움 (이전 49% 없음 → 해결됨)
  - 품질 문제: 범용 키워드 과다(혜택 85%, 연회비 81%), 범용만 있는 카드 10건
  - keyword_dictionary 교차: 65개 중 26개만 매칭(40%), 39개 미등록
- [x] D-4/D-1: fullText 전처리 중기 계획 수립
  - DB 분석: structured.detailContent가 이미 요약본 제공 (1251/1251, 398/398)
  - content 원본은 '#' 헤더, 중복 텍스트 포함 → 중기 정리 대상
  - 중기 계획: 마크다운 보존, 중복 제거, 원본 포맷(표/목록) 보존
- [x] D-5: CLAUDE.md Data 섹션 업데이트
- [ ] keyword_dictionary 보강: card_products 전용 키워드 39개 등록 대기 (M-2 결과에 따라)

### AI/ML 팀장 (최종 업데이트: 2026-02-10 16:00) 🟢 세션 활성
- [x] 프로젝트 합류 및 전체 현황 파악 완료
- [x] Level 02 Phase 1-2: B-1 확인, D-2 수정 완료, F-8 Mock OK / 실데이터 조사 완료
- [x] STT 에코 방지, 상담 상세 모달 수정, 유사도 점수 실제화, Admin/Stats 빈화면 수정
- [ ] **F-8 실데이터 피드백 저장 흐름 수정** ← 현재 진행 중
- [ ] **Phase 3 M-1**: STT 비교 테스트 실행 (Whisper-1 / Qwen3-ASR / VibeVoice)
- [ ] **Phase 3 M-2**: 키워드 추출 개선 설계
- [ ] **Phase 3 M-3**: RAG 검색 품질 개선 (M-1, M-2 이후)

#### 📋 각 세션 전달사항 (2026-02-10 16:00 갱신)
> 모든 세션은 `docs/levelup/02_LEVEL02_DISCUSSION.md`를 기준으로 작업합니다.
> **작업 완료 시 반드시** 이 섹션과 Discussion 문서 "진행 이력"에 타임스탬프와 함께 기록해주세요.

---

##### Backend에게 (즉시 착수)
> M-1 대기 불필요. 인프라 확인 작업이 있습니다.

| # | 작업 | 상세 | 상태 |
|---|------|------|------|
| B-1 | ~~[메모] 프롬프트~~ | prompt.py | ✅ 완료 |
| B-2 | ~~D-2 환각 방지~~ | card_generator.py `_DB_PROTECTED_FIELDS` | ✅ 완료 |
| **B-3** | **M-1 인프라: Qwen3-ASR 동작 확인** | 포트 8104 서버 상태 + `POST /api/v1/settings/stt-engine` {"engine":"qwen3-asr"} 호출 테스트 | 🔲 즉시 |
| **B-4** | **M-1 인프라: 시나리오 오디오 파일 확인** | 시나리오 1~8 오디오 파일 위치 확인 (TTS 생성분 또는 녹음본), 없으면 생성 필요 여부 M에게 보고 | 🔲 즉시 |

##### Frontend에게 (즉시 착수)
> **M-1은 Frontend 작업이 아닙니다.** STT 비교는 AI/ML+Backend에서 진행합니다. 대기하지 마세요.

| # | 작업 | 상세 | 상태 |
|---|------|------|------|
| F-1~7 | ~~Phase 1 UI/UX~~ | 6건 전체 | ✅ 완료 |
| **F-8** | **FeedbackModal 닫기 시 기본값 저장** | 파일: `frontend/src/app/components/modals/FeedbackModal.tsx`. 현재: "확인"만 feedbackScores 저장 → "닫기"/"오늘보지않기" 시 NULL. 수정: onClose 호출 전에 기본값 `{feedbackScore:70, satisfactionScore:3, sentiment:'neutral', feedbackEmotions:['neutral','neutral','neutral'], feedbackText:''}` 을 localStorage에 저장 | 🔲 즉시 |

##### Data에게 (완료 보고)
> F-8 backfill은 10건뿐이라 AI/ML에서 직접 처리합니다. 스크립트 불필요.

| # | 작업 | 상세 | 상태 |
|---|------|------|------|
| ~~D-3~~ | ~~M-2 지원: 키워드 품질 분석~~ | Phase B에서 100% 채움 확인. 품질 문제: 범용 과다(10건), 사전 미등록 39개 | ✅ 2026-02-10 16:30 |
| ~~D-4~~ | ~~D-1 fullText 전처리 계획~~ | structured.detailContent 이미 활용 가능. 중기: 마크다운 보존/중복 제거 | ✅ 2026-02-10 16:30 |
| ~~D-5~~ | ~~CLAUDE.md Data 섹션 업데이트~~ | Data 섹션 작업 현황 기록 완료 | ✅ 2026-02-10 16:30 |
| **D-6** | **keyword_dictionary 보강** | card_products 전용 키워드 39개 등록 (주유, 교통, 간편결제, 쇼핑 등). M-2 설계 결과에 따라 진행 | 🔲 M-2 이후 |

##### AI/ML 팀장 (본인, 즉시 착수)
| # | 작업 | 상태 |
|---|------|------|
| **M-0** | F-8 실데이터 10건 backfill (DB 직접 처리) | 🔲 즉시 |
| **M-1** | STT 비교 테스트 설계 + 실행 (Backend 인프라 확인 후) | 🔲 오늘 |
| **M-2** | 키워드 추출 개선 설계 (Data 분석 결과 받은 후) | 🔲 이번 주 |

---

- **전체**: Phase 1-2 완료. F-8 잔여 + **Phase 3 (STT/키워드/RAG)** 병렬 진행 중
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
