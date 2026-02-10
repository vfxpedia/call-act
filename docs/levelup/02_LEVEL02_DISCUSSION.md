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

### F-8. Mock 피드백 데이터 추가 ✅ 완료
- **현상**: 피드백 저장 기능은 작동하나, 기존 DB 데이터에 mock 피드백이 없어 화면 확인 불가
- **요구**: 기존 상담 데이터에 mock 피드백 정보 추가 (satisfaction_score, feedback_text, feedback_emotions 등)
- **담당**: D + F
- **상태**: ~~검토 예정~~ **완료** — `populate_extended_fields.py`에서 이미 모든 피드백 필드 생성 중 (sentiment 100%, emotion_score 100%, satisfaction_score 100%, feedback_text 60%, feedback_emotions 100%). API 반환 및 ConsultationDetailModal 피드백 보기 기능 정상 동작 확인됨.

---

## Phase 2: 데이터/백엔드 연동 개선

### D-1. 문서 fullText 가독성 (DB 데이터 포맷)
- **현상**: 서비스 가이드 fullText가 순수 텍스트로 저장, 가독성 부족
  ```
  카드대금 결제 신청금액은 계좌로 입금되지 않고 카드 결제대금에서 즉시 차감되며...
  ```
- **질문**: DB에서 모든 데이터를 다시 전처리해야 하는가?
- **결론**:
  - **즉시**: Frontend `convertToMarkdown()`에서 최대한 자동 변환 (제목 감지, 단락 분리) → **Level 01-02에서 이미 개선**
  - **중기**: DB 데이터 전처리 시 마크다운 포맷팅 적용 (Phase 3으로 이관)
  - **장기**: 데이터 수집 파이프라인에서 원본 포맷 보존
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

### M-1. STT 전사 품질 (CRITICAL)
- **현상**: 실시간 STT 전사 정확도 부족 → 키워드 추출 품질 저하 → RAG 검색 품질 저하
- **현재**: Whisper-1 (OpenAI API) 사용 중
- **테스트 대상**:
  | 모델 | 비고 |
  |------|------|
  | Whisper-1 (현재) | OpenAI API, 프로덕션 사용 중 |
  | Qwen3-ASR 1.7B | 로컬 서빙 가능, GPU 0 |
  | VibeVoice-ASR | 로컬 서빙 가능, 화자 분리 내장 |
  | VibeVoice Realtime 0.5B | 실시간 스트리밍 ASR, 타임스탬프 제공 |
- **VibeVoice ASR 데모 결과**: 시나리오 1 (122초 오디오) → 10.13초 처리, 화자 분리 정확
- **비교 평가 기준**: WER, 처리 속도(RTF), 화자 분리 정확도
- **담당**: M + B
- **상태**: **테스트 계획 수립 필요**

### M-2. 핵심 키워드 추출 개선 (CRITICAL)
- **현상**: 무분별한 키워드 도출 → 불필요한 문서 검색 → 화면 어지럽힘
- **문제 분석**:
  1. 인사 발화("안녕하세요 테디카드 상담사입니다")에서도 키워드 추출 → 불필요
  2. 상담 흐름(context) 무시 → 단편적 키워드만 추출
  3. 핵심 발화 vs 비핵심 발화 구분 없음
- **개선 방향**:
  1. **발화 중요도 판단**: 인사/감사/확인 등 비정보성 발화 필터링
  2. **상담 흐름 인식**: 연속 발화에서 주제 연관 키워드 묶기
  3. **키워드 품질 기준**: 실제 DB 문서와 매칭 가능한 키워드만 추출
- **담당**: M + B
- **상태**: **설계 필요**

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
| **1** | **D+F** | F-8 Mock 피드백 데이터 | ✅ **완료** (DB 데이터 + API + UI 확인) |
| **2** | **D** | D-1 fullText 전처리 | 중기 |
| **2** | **B+D** | D-2 참조 문서 환각 조사 | ✅ **조사 완료** (환각 아님) |
| **3** | **M+B** | M-1 STT 비교 테스트 | **🔥 최우선 — 진행 중** |
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
| 2026-02-10 | Phase 1 Frontend 수정 완료 (F-1, F-3~F-7 총 6건) |
| 2026-02-10 | Phase 2 전체 조사 완료: B-1 이미 적용 확인, D-2 환각 아님 확인, F-8 DB 데이터 존재 확인 |
| 2026-02-10 | 문서 상세보기 fullText API 연동, FAQ 필드명 수정, 피드백 저장 플로우 완성 |
| 2026-02-10 | Transcript 포맷 정규화 (dict/array 양방향 호환), 피드백 필드 5종 저장 추가 |

## 다음 단계

1. ~~**즉시**: Phase 1 Frontend 수정 진행 (F-1 ~ F-7)~~ ✅ 완료
2. ~~**이번 주**: Phase 2 조사/논의 (B-1, D-2, F-8)~~ ✅ 전체 완료 (B-1 이미 적용, D-2 환각 아님 확인, F-8 DB 데이터 존재 확인)
3. **이번 주**: Phase 3 M-1 STT 비교 테스트 실행 (비교 대시보드 활용)
4. **이번 주**: Phase 3 M-2 키워드 추출 개선 설계
5. **다음 주**: Phase 3 M-3 RAG 검색 품질 + Phase 4 논의
