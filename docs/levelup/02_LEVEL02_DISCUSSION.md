# CALL:ACT Level 02 고도화 논의 문서

> **작성일**: 2026-02-10
> **참여**: Frontend(F), Backend(B), DB(D), AI/ML(M)
> **목적**: 사용자 피드백 기반 고도화 사항 정리 + 팀별 업무 분담 + Phase 구조화
> **이전 단계**: Level 01 → `01_DISCUSSION.md`, `03_PHASE_ABC_RESULTS.md`

---

## 현재 상태 요약

Level 01에서 달성한 것:
- Phase A: STT 57%→100%, VocabGate 67%→100%
- Phase B: FAQ 버그, FlashText+fallback 병합, DB 스크립트 동기화
- Phase C: 통합 테스트 6/6 통과
- 프론트: 문서 타입 표시, 키보드 단축키, 피드백 모달, 문서 상세보기 개선

---

## Phase 1: 즉시 수정 가능한 UI/UX 개선 (Frontend) ✅ 완료

### F-1. 대시보드 교육 시뮬레이션 데이터 불일치
- **현상**: "추천 교육 시뮬레이션"의 scenarioId가 `SIM-001~005`로 되어 있으나, 실제 시나리오 ID는 `scenario-1~8`
- **원인**: `mockData.ts`의 `simulationsData`에서 scenarioId 매핑이 잘못됨
- **수정**: scenarioId를 실제 시나리오 ID로 매핑 + 카테고리/제목 일치 확인
- **담당**: F
- **상태**: ~~수정 예정~~ **수정 완료**

### F-2. AI 요약 형식에 [메모] 섹션 추가 ✅ 이미 적용됨
- **현상**: 후처리 페이지 AI 요약에 `[메모]` 섹션이 없음
- **요구**: `[메모]` (개행 포함)를 마지막에 추가 → 복사하면 메모란에 바로 붙여넣기 가능
- **현재 형식**:
  ```
  요약 한줄

  [처리 내역]
  [고객 요청 사항]
  [상담사 조치]
  [참고사항]
  ```
- **변경 형식**:
  ```
  요약 한줄

  [처리 내역]
  [고객 요청 사항]
  [상담사 조치]
  [참고사항]

  [메모]
  (빈 줄)
  ```
- **수정 위치**: Backend `prompt.py` SUMMARIZE_SYSTEM_PROMPT
- **담당**: B
- **상태**: ~~Backend 대기~~ **이미 완료** — `backend/app/core/prompt.py` SUMMARIZE_SYSTEM_PROMPT에 [메모] 섹션 이미 포함

### F-3. 대시보드/상담이력 메인 텍스트 표시 개선
- **현상**: 대시보드 상담 내역에 `memo`(상담사 메모)가 표시됨
- **요구**: 요약 한줄 또는 AI가 생성한 `title`을 메인 텍스트로 표시
- **원인**: `DashboardPage.tsx:106` → `enriched.memo || enriched.content || '상담 내용'`
- **수정**: `(enriched.content?.split('\n')[0]) || enriched.memo || '상담 내용'`
- **담당**: F
- **상태**: ~~수정 예정~~ **수정 완료**

### F-4. 참조 문서 유사도 순 정렬
- **현상**: 상담 상세보기 + 후처리 페이지에서 참조 문서가 원본 순서로 나열
- **요구**: `relevanceScore` 높은 순으로 정렬
- **수정 위치**:
  - `ConsultationDetailModal.tsx` → `getDocumentsFromDB()` 결과 `.sort((a,b) => (b.relevanceScore||0) - (a.relevanceScore||0))`
  - `AfterCallWorkPage.tsx` → 클릭 우선 + 유사도 순 정렬
- **담당**: F
- **상태**: ~~수정 예정~~ **수정 완료**

### F-5. 포커싱 링 잘림 수정
- **현상**: 카드 포커싱 시 좌측열은 좌측 링이, 우측열은 우측 링이 잘려 보임
- **원인**: 부모 컨테이너에 `overflow: hidden` 적용 + `ring-2` CSS가 잘림
- **수정**: `ring-2 ring-[#0047AB]` → `outline outline-2 outline-[#0047AB]` + `overflow-visible` + `z-10`
- **담당**: F
- **상태**: ~~수정 예정~~ **수정 완료**

### F-6. 검색 레이어 카드 키보드 포커싱
- **현상**: 칸반 레이어 카드만 키보드 이동/포커싱 가능, 검색 레이어는 안됨
- **원인**: SearchLayer/SearchResultLayer에 `focusedCard` prop 미전달
- **수정**: `activeLayer` + `focusedCard` props를 SearchLayer → SearchResultLayer → InfoCard로 전달 + `onCardSelect`에 search 분기 추가
- **담당**: F
- **상태**: ~~수정 예정~~ **수정 완료**

### F-7. 상담 ID 클립보드 복사 버튼
- **현상**: 상담 상세 정보 모달에서 상담 ID를 수동으로 선택/복사해야 함
- **요구**: 상담 ID 옆에 복사 아이콘 버튼 추가
- **수정**: `ConsultationDetailModal.tsx`에 Copy/Check 아이콘 + `navigator.clipboard.writeText()` 추가
- **담당**: F
- **상태**: ~~수정 예정~~ **수정 완료**

### F-8. Mock 피드백 데이터 추가 — 부분 완료 (추가 작업 필요)
- **현상**: 피드백 저장 기능은 작동하나, 기존 DB 데이터에 mock 피드백이 없어 화면 확인 불가
- **요구**: 기존 상담 데이터에 mock 피드백 정보 추가 (satisfaction_score, feedback_text, feedback_emotions 등)
- **담당**: D + F
- **조사 결과** (2026-02-10 15:00):
  1. ✅ **Mock 데이터 (6,557건)**: `populate_extended_fields.py`에서 이미 생성됨 (feedback_text 61%, emotions 100%)
  2. ⚠️ **실데이터 (다이렉트콜 저장분)**: FeedbackModal "확인" 시에만 피드백 저장, "닫기"/"오늘 보지않기" 시 NULL
     - DB 확인: 10건 중 5건이 feedback_text=NULL, sentiment=NULL (emotion_score/satisfaction_score만 존재)
     - 원인: FeedbackModal.handleConfirm → localStorage('feedbackScores') → ACW 저장 흐름에서, 모달 미확인 시 localStorage에 데이터 없음
  3. ✅ **저장 파이프라인**: Backend consultations.py INSERT/UPDATE에 feedbackText/feedbackEmotions 필드 포함 확인됨
- **남은 작업**:
  - [ ] 실데이터 중 피드백 NULL인 건에 대해 emotion_score 기반 backfill 스크립트
  - [ ] FeedbackModal 닫기 시에도 기본 피드백 데이터 생성 (선택적)
- **상태**: 부분 완료 — Mock 데이터 OK, 실데이터 backfill 필요

---

## Phase 2: 데이터/백엔드 연동 개선

### D-1. 문서 fullText 가독성 (DB 데이터 포맷)
- **현상**: 서비스 가이드 fullText가 순수 텍스트로 저장, 가독성 부족
  ```
  카드대금 결제 신청금액은 계좌로 입금되지 않고 카드 결제대금에서 즉시 차감되며...
  ```
- **DB 분석 결과** (2026-02-10 16:00 Data팀):
  - `service_guide_documents` content 길이 분포: <100자 153건, 100-500자 693건, 500-1K 283건, 1K-3K 119건, 3K+ 3건
  - `card_products` main_benefits: <500자 324건, 500-2K 74건 (총 398건)
  - **structured.detailContent가 이미 요약 가독성 텍스트 제공** (1251/1251건, 398/398건)
  - content(원본)은 '#' 마크다운 헤더/중복 텍스트 포함, detailContent는 LLM 요약본
  - **결론**: 프론트에서 `structured.detailContent` 우선 표시 → content는 보조 참조용
- **중기 계획**:
  1. 데이터 전처리 파이프라인에서 `# 제목` 패턴 자동 인식 → 마크다운 보존
  2. 중복 텍스트 제거 (e-Gift 카드 content: 동일 블록 2회 반복)
  3. 원본 포맷(표, 목록)이 있는 문서는 HTML/마크다운으로 보존
- **담당**: D (데이터 전처리), F (렌더링)

### D-2. 참조 문서에 실제 아닌 문서 기록 ✅ 수정 완료
- **현상**: '카드 두께 관련 문의' 같은 실제 DB에 없는 문서가 참조 문서로 기록됨
- **원인**: `card_generator.py`의 `_merge_card()` 함수에서 LLM overlay가 DB 원본의 `id`/`title`을 덮어쓸 수 있었음
  - `generate_detail_cards()`에서 LLM에 `id, title, keywords, content` 생성을 요청
  - `_merge_card(base, item)` line 133: `if val not in ("", None): merged[key] = val` → LLM이 생성한 title이 DB title을 대체
- **수정** (2026-02-10):
  - `_DB_PROTECTED_FIELDS = {"id", "title", "sourceTable", "documentType", "relevanceScore"}`
  - `_merge_card()`에서 base에 값이 있는 보호 필드는 LLM overlay로 덮어쓰지 않음
  - `build_rule_cards()` 경로는 원래 안전 (LLM 미호출)
- **담당**: B + D
- **상태**: ~~조사 필요~~ **수정 완료**

### B-1. AI 요약 프롬프트 [메모] 추가 (= F-2) ✅ 이미 적용됨
- **위치**: `backend/app/core/prompt.py` SUMMARIZE_SYSTEM_PROMPT (line 324)
- **현재 상태**: `result` 필드에 이미 `[메모]\n` 섹션 포함됨
  ```
  [참고사항]\n- 해당 시 기재 (없으면 생략)\n\n[메모]\n
  ```
- **담당**: B
- **상태**: ~~Backend 대기~~ **이미 완료** (프롬프트에 [메모] 섹션 존재 확인)

---

## Phase 3: 핵심 품질 개선 (STT/키워드/RAG)

> **최우선 개선 영역** - 모든 팀이 논의 필요

### M-1. STT 전사 품질 (CRITICAL) ✅ 테스트 완료

- **현상**: 실시간 STT 전사 정확도 부족 → 키워드 추출 품질 저하 → RAG 검색 품질 저하
- **테스트 결과**: `docs/levelup/M1_STT_RESULTS.md` (2026-02-10 20:04)
- **테스트 조건**: 시나리오 2종 × 3개 엔진, 원본 m4a → WAV, 전체 오디오 (청크 분할 없음)

  | 엔진 | 평균 RTF | 키워드 보존율 | 주요 오류 |
  |------|----------|-------------|-----------|
  | whisper-1 (현재) | 0.101 | 86% (19/22) | 재발부(x4), 반복 환각, 네트워크 변동 |
  | qwen3-asr-1.7B | 0.133 | 82% (18/22) | 숫자 한글화(치명), 출력 끊김, 브랜드명 오류 |
  | **faster-whisper-large-v3** | **0.066** | **91% (20/22)** | 테리카드(1자), prompt 튜닝 가능 |

- **결론**: **faster-whisper-large-v3 최적** (속도 2x, 정확도 최고, 무료, 숫자 아라비아 유지)
- **후속 과제**:
  1. "테디카드" prompt 추가 → "테리카드" 오인식 개선
  2. 프로덕션 청크 모드 (1.5초 VAD) 테스트
  3. `stt_engine.py`에 faster-whisper 백엔드 추가 (Backend)
- **담당**: M + B
- **상태**: ✅ 비교 완료, 후속 통합 작업 필요

### M-2. 핵심 키워드 추출 개선 (CRITICAL)
- **현상**: 무분별한 키워드 도출 → 불필요한 문서 검색 → 화면 어지럽힘
- **문제 분석**:
  1. 인사 발화("안녕하세요 테디카드 상담사입니다")에서도 키워드 추출 → 불필요
  2. 상담 흐름(context) 무시 → 단편적 키워드만 추출
  3. 핵심 발화 vs 비핵심 발화 구분 없음
- **DB 키워드 현황 분석** (2026-02-10 16:00 Data팀):
  - `card_products`: 398건 전체 키워드 보유 (Phase B에서 100% 채움)
  - `service_guide_documents`: 1251건 전체 키워드 보유
  - **키워드 품질 문제**:
    - 고유 키워드 65개 중 범용 5개(혜택/연회비/포인트/대출/할부)가 전체의 40-85% 차지
    - 범용 키워드만 있는 카드 10건 → 카드 구별 불가
    - keyword_dictionary(1555개)와 card_products 키워드(65개) 교집합 26개(40%)만
    - **39개 카드 전용 키워드**가 사전에 미등록 → RAG 라우팅 시 매칭 누락 가능
  - **추출 가능 소스**: `structured.detailContent` (398/398건), `main_benefits`, `structured.benefits/features`
- **개선 방향 및 진행 상태**:
  1. ✅ **비정보성 발화 필터** (2026-02-10 20:20): `keyword_extractor.py`에 `NON_INFO_PATTERNS` 10개 추가. 20% 필터율 달성
  2. ✅ **STT 오인식 교정 사전 확장** (2026-02-10 20:15): M-1 오류 5개 추가 (테리카드, 재발부, 서강 등)
  3. 🔲 **상담 흐름 인식**: 연속 발화에서 주제 연관 키워드 묶기 → 다음 주
  4. 🔲 **keyword_dictionary 보강**: card_products 전용 키워드 39개 등록 (D팀, M-2 이후)
- **담당**: M + B + D
- **상태**: **단계 1-2 완료, 단계 3-4 진행 예정**

### M-3. RAG 검색 품질 (연관 문서 정확도)
- **현상**: STT 오류 + 무분별한 키워드 → 관련 없는 문서 검색
- **의존성**: M-1 (STT) + M-2 (키워드) 해결이 선행되어야 함
- **추가 개선**:
  1. 검색 결과의 relevance threshold 설정
  2. 상담 흐름 기반 문서 필터링
  3. 이전 step에서 이미 보여준 문서 중복 방지
- **담당**: B + D
- **상태**: M-1, M-2 이후 진행

---

## Phase 4: 관리자/서비스 논의 사항

### 논의-1. admin/stats 페이지 실효성
- **현상**: 팀별 성과, 일별 추이, 알림 등이 표시되지만 실제 관리자에게 필요한 정보인지 불확실
- **논의 필요**: 실제 서비스라고 할 때 관리자에게 정말 필요한 KPI/지표는 무엇인가?
- **담당**: 전체 팀 논의

### 논의-2. 녹취 재생 실제 구현
- **현상**: 상담 상세보기/상담 관리에 녹취 재생 UI는 있으나 실제 파일 없음
- **기술 검토**: 실시간 STT 중 원본 오디오 저장 → 재생 가능한 구조 필요
- **담당**: B + F (후순위)

### 논의-3. Transcript 전문 저장
- **현상**: transcript가 짧게 저장됨 (풀 대화가 아닌 일부만)
- **기대 형식**:
  ```json
  [{"speaker": "agent", "message": "...", "timestamp": "14:32:30"}, ...]
  ```
- **원인**: 실시간 STT에서 전사된 전체 대화가 transcript로 저장되어야 하나, 시뮬레이션 모드에서는 mock 데이터만 저장
- **담당**: B + F

---

## Phase 5: 기술 로드맵 (MVP 이후)

### 기술-1. VibeVoice Realtime 0.5B 적용
- 실시간 스트리밍 ASR + 화자 분리 + 타임스탬프
- Audio Segments 제공 → 상담사 목소리 임베딩으로 Speaker Diarization 고도화
- 현재 Whisper + pyannote 2단계 → 1단계로 축소 가능

### 기술-2. 상담사 음성 임베딩
- 상담사 목소리만 학습 → 상담사 vs 고객 자동 분리
- VibeVoice ASR의 Speaker Segments 활용

### 기술-3. 상담 흐름 기반 지능형 문서 추천
- 발화 시퀀스 분석 → 상담 단계(인사→본인확인→문의→처리→마무리) 자동 인식
- 단계별 관련 문서만 추천 (현재: 모든 키워드에 대해 검색)

---

## 팀별 업무 분담 요약

| Phase | 담당 | 항목 | 상태 |
|-------|------|------|------|
| **1** | **F** | F-1 시뮬레이션 매핑, F-3 메인텍스트, F-4 문서정렬, F-5 포커싱링, F-6 검색포커싱, F-7 복사버튼 | ✅ **전체 완료** |
| **1** | **B** | F-2/B-1 [메모] 프롬프트 | ✅ **이미 적용됨** |
| **1** | **D+F** | F-8 Mock 피드백 데이터 | ⚠️ Mock OK, 실데이터 backfill 필요 |
| **2** | **D** | D-1 fullText 전처리 | 중기 |
| **2** | **B+D** | D-2 참조 문서 환각 방지 | ✅ **수정 완료** (_DB_PROTECTED_FIELDS) |
| **3** | **M+B** | M-1 STT 비교 테스트 | ✅ **완료** (faster-whisper 최적) |
| **3** | **M+B** | M-2 키워드 추출 개선 | **🔥 최우선 — 설계 중** |
| **3** | **B+D** | M-3 RAG 검색 품질 | M-1,2 이후 |
| **4** | **전체** | 논의-1,2,3 | 논의 |

---

## VibeVoice ASR 데모 결과 (참고)

### 시나리오 1 (부정 결제 문의)
- **오디오**: 122.07초
- **처리**: 10.13초 (RTF 0.083)
- **토큰**: 1994 (98.6 tokens/s)
- **화자 분리**: Speaker 0 (상담사), Speaker 1 (고객) 정확 분리
- **전사 품질**: 숫자 한글 변환("천구백구십년"), 자연어 표현 양호

### 시나리오 2 (카드 분실)
- **오디오**: 114.43초
- **처리**: 11.53초 (RTF 0.101)
- **토큰**: 2085 (99.5 tokens/s)
- **특이**: 환경음 감지 (`[Environmental Sounds]`), 감정적 고객 발화 정확 전사

---

## 진행 이력

| 날짜 | 내용 |
|------|------|
| 2026-02-10 AM | Phase 1 Frontend 수정 완료 (F-1, F-3~F-7 총 6건) |
| 2026-02-10 AM | 문서 상세보기 fullText API 연동, FAQ 필드명 수정, 피드백 저장 플로우 완성 |
| 2026-02-10 AM | Transcript 포맷 정규화 (dict/array 양방향 호환), 피드백 필드 5종 저장 추가 |
| 2026-02-10 09:00~10:30 | STT WHISPER_PROMPT 에코 방지 (whisper.py 할루시네이션 필터 12개 추가) |
| 2026-02-10 10:30~11:00 | 상담 상세 모달 필드 매핑 수정 (transcript, referenced_documents) |
| 2026-02-10 11:00~12:00 | RAG 유사도 점수 실제화 (simple_retriever.py 하드코딩 0.9 → _text_similarity) |
| 2026-02-10 13:00~14:00 | Level 02 Phase 2 진행: B-1 [메모] 프롬프트 확인, D-2 LLM 환각 조사 |
| 2026-02-10 14:00~15:00 | D-2 수정: card_generator.py _DB_PROTECTED_FIELDS 추가 (id/title/sourceTable/documentType/relevanceScore 보호) |
| 2026-02-10 15:00~15:30 | F-8 실데이터 조사: ADMIN 10건 중 5건 피드백 NULL, FeedbackModal 미확인 시 저장 안됨 확인 |
| 2026-02-10 15:30 | Backend/Frontend 서브모듈 커밋 + Discussion 문서 업데이트 |
| 2026-02-10 16:30 | **F-8 FeedbackModal 수정 완료**: onClose/ESC/오늘보지않기 시 기본 feedbackScores localStorage 저장 (feedbackScore:70, satisfactionScore:3, sentiment:neutral) |
| 2026-02-10 16:30 | **M-0 완료**: F-8 실데이터 10건 backfill (SQL UPDATE) |
| 2026-02-10 19:40 | M-1 STT 테스트 스크립트 작성 (`m1_stt_comparison.py`), 1차 실행 (faster-whisper만 성공) |
| 2026-02-10 20:04 | **M-1 완료**: 3개 엔진 전체 성공. 결과 → `docs/levelup/M1_STT_RESULTS.md` |
| | - faster-whisper-large-v3: RTF 0.066, 키워드 91%, 숫자 아라비아 유지 → **최적** |
| | - whisper-1: RTF 0.101, 키워드 86%, 반복 환각, 네트워크 의존 |
| | - qwen3-asr-1.7B: RTF 0.133, 키워드 82%, 숫자 한글화, 출력 끊김 |
| 2026-02-10 20:15 | **M-2 단계 1 완료**: STT 교정 사전에 M-1 오류 패턴 5개 추가 (테리카드, 태리카드, 테딜카드, 재발부, 서강과) |
| 2026-02-10 20:20 | **M-2 단계 2 완료**: `keyword_extractor.py`에 `NON_INFO_PATTERNS` 10개 비정보성 발화 필터 추가. 테스트: 15문장 중 3문장(20%) 필터 |
| 2026-02-10 20:45 | **B-3 완료**: WHISPER_PROMPT에 "테디카드, 나라사랑카드, 재발급, 이의신청" 추가. faster-whisper 기본 모델 base→large-v3 변경. 서버 재시작 완료 |
| 2026-02-11 10:00 | **F-10 확인 완료**: ACW category_raw localStorage 전달 — 이미 구현 확인 (5단계 flow 정상) |
| 2026-02-11 10:00 | **F-11 완료**: 가이드 말풍선 CSS zoom 보정 (`TutorialGuide.tsx`: getBoundingClientRect zoom 보정, 경계 체크 CSS 좌표계 통일, `tutorialConfig.ts`: getViewportScale zoom 보정) |
| 2026-02-11 10:00 | **F-12 완료**: 교육 시뮬레이션 페이지 가이드 배지 추가 (`SimulationPage.tsx`: 웰컴→우수사례→기본시나리오→시작하기 4단계 가이드, 헤더 버튼 연동, `tutorialSteps.ts`: tutorialStepsSimulation 추가) |

## 다음 단계 (2026-02-10 20:25 갱신)

### 즉시 (금일~내일)
| # | 담당 | 작업 | 상세 |
|---|------|------|------|
| ~~1~~ | ~~**F**~~ | ~~F-8 FeedbackModal 기본값 저장~~ | ✅ 완료 |
| ~~2~~ | ~~**M**~~ | ~~M-0 F-8 실데이터 backfill~~ | ✅ 완료 (10건 UPDATE) |
| ~~3~~ | ~~**M**~~ | ~~M-1 STT 비교 테스트~~ | ✅ 완료 (faster-whisper 최적) |
| ~~4~~ | ~~**M**~~ | ~~M-2 단계 1-2: 비정보성 필터 + STT 교정~~ | ✅ 완료 |
| ~~5~~ | ~~**B**~~ | ~~faster-whisper prompt 튜닝~~ | ✅ 완료 (2026-02-10 20:45) `WHISPER_PROMPT`에 "테디카드, 나라사랑카드, 재발급, 이의신청" 추가 |
| ~~6~~ | ~~**B**~~ | ~~faster-whisper `stt_engine.py` 통합~~ | ✅ 완료 (2026-02-10 20:45) 기본 모델 base→large-v3, 라벨 업데이트, 서버 재시작 |

### 이번 주
| # | 담당 | 작업 | 상세 |
|---|------|------|------|
| ~~6~~ | ~~**B**~~ | ~~faster-whisper `stt_engine.py` 통합~~ | ✅ 완료 (large-v3 기본, Settings API 반영) |
| 7 | **M+B** | M-2 키워드 추출 개선 구현 | 비정보성 발화 필터, Weak Intent 확장, 상담 흐름 인식 |
| 8 | **D** | D-6 keyword_dictionary 보강 | STT 오인식 동의어 추가 (테리카드→테디카드, 재발부→재발급 등) + 미등록 39개 |

### 다음 주
| # | 담당 | 작업 |
|---|------|------|
| 9 | **B+D** | M-3 RAG 검색 품질 (M-1,2 결과 반영) |
| 10 | **전체** | Phase 4 논의 (admin/stats, 녹취 재생, transcript 저장) |
