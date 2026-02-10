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

### Backend (최종 업데이트: 2026-02-09)
- [x] 로컬 E2E 전환 완료 (RunPod → 워크스테이션)
- [x] AWQ 양자화 (kanana-8B, analysis)
- [x] 플러거블 STT/TTS 아키텍처
- [x] STT/TTS 엔진 전환 UI + Settings API
- [x] 한국어 TTS 전처리 모듈
- [x] ngrok 외부 접속
- [ ] Vercel + EC2 배포 연결

### Frontend (최종 업데이트: 2026-02-10) 🟢 세션 활성
- [x] Level 01: 문서 타입 표시, 키보드 단축키, 피드백 모달, 문서 상세보기 개선
- [x] Level 02 Phase 1 전체 완료 (6건):
  - [x] F-1: 대시보드 시뮬레이션 scenarioId 매핑 (SIM-001→scenario-1)
  - [x] F-3: 대시보드 메인 텍스트 → AI 요약 첫줄 표시
  - [x] F-4: 참조 문서 유사도 순 정렬 (상세보기 + 후처리)
  - [x] F-5: 포커싱 링 잘림 수정 (ring → outline)
  - [x] F-6: 검색 레이어 카드 키보드 포커싱 + Enter 상세보기
  - [x] F-7: 상담 ID 클립보드 복사 버튼
- [x] 검색 유사도 하드코딩 제거 (searchSimulator.ts → 백엔드 실제 점수 사용)
- [x] 문서 상세보기 fullText 렌더링 개선 (convertToMarkdown 한국어 전처리)
- [x] F-8: Mock 피드백 데이터 표시 — DB에 이미 존재 확인 (populate_extended_fields.py)
- [x] F-2/B-1: [메모] 섹션 AI 요약 — 프롬프트에 이미 포함 확인 (prompt.py:324)

### Data (최종 업데이트: )
- (Data 세션이 여기에 기록)

### AI/ML 팀장 (최종 업데이트: 2026-02-10) 🟢 세션 활성
- [x] 프로젝트 합류 및 전체 현황 파악 완료
- [x] Level 2 고도화 문서(`02_LEVEL02_DISCUSSION.md`) 검토 완료
- [x] Phase 2 전체 완료: B-1 이미 적용 확인, D-2 환각 아님 확인, F-8 DB 데이터 존재 확인
- [x] 문서 상세보기/FAQ/피드백/Transcript 버그 수정 및 배포
- [ ] **Phase 3 M-1**: STT 비교 테스트 실행 (Whisper-1 / Qwen3-ASR / VibeVoice)
- [ ] **Phase 3 M-2**: 키워드 추출 개선 설계
- [ ] **Phase 3 M-3**: RAG 검색 품질 개선 (M-1, M-2 이후)

#### 📋 각 세션 전달사항 (2026-02-10)
> 모든 세션은 `docs/levelup/02_LEVEL02_DISCUSSION.md`를 기준으로 작업합니다.

- **Backend에게**: ~~B-1 ([메모] 프롬프트 추가) 즉시 처리 부탁합니다.~~ ✅ 이미 적용 확인. ~~D-2 (참조 문서 환각) 원인 조사 시 M 세션과 협의 필요.~~ ✅ 조사 완료 (환각 아님).
- **Frontend에게**: ~~Phase 1 잔여 작업(F-6 검색 포커싱, F-7 복사 버튼) 진행 상황 CLAUDE.md에 업데이트 부탁합니다.~~ ✅ Phase 1 전체 완료 (6건). ~~타팀 의존 항목(F-2, F-8) 대기 중.~~ ✅ F-2, F-8 모두 완료 확인.
- **Data에게**: ~~F-8 Mock 피드백 데이터 준비~~ ✅ DB에 이미 존재. D-1 fullText 전처리 중기 계획 검토 부탁합니다.
- **전체**: Phase 1-2 완료! **Phase 3 (STT/키워드/RAG)** 진입. M-1 STT 비교 테스트, M-2 키워드 추출 개선이 최우선.

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
