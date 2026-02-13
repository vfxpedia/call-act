# Phase 3: STT/키워드/RAG 품질 개선 실행 계획

> **작성일**: 2026-02-10
> **담당**: AI/ML 팀장 (M 세션)
> **의존 문서**: `02_LEVEL02_DISCUSSION.md`, `03_PHASE_ABC_RESULTS.md`
> **상태**: Phase 1-2 완료, Phase 3 진입

---

## 현재 인프라 현황

### STT 엔진 (비교 대시보드 http://localhost:8889)

| 엔진 | 모델 크기 | 타입 | 비고 |
|------|-----------|------|------|
| whisper-1 (OpenAI) | Cloud | API | 현재 프로덕션 |
| faster-whisper-base | ~600MB | Local | 빠르지만 낮은 정확도 |
| faster-whisper-small | ~750MB | Local | 속도-정확도 균형 |
| faster-whisper-large-v3 | ~3GB | Local | 높은 정확도 |
| qwen3-asr-0.6B | 1.8GB | Local | 52개 언어 |
| qwen3-asr-1.7B | 4.4GB | Local | 더 높은 정확도 |
| vibevoice-asr | 17GB | Local | 화자 분리 내장, RTF 0.08 |

### 키워드 추출 아키텍처

```
STT 텍스트 → KeywordExtractor → extract_signals() → VocabGate → Router → RAG
    │              │                    │                │
    │         형태소 분석          FlashText +        25-35%
    │         STT 오류 교정       Fuzzy 매칭          차단률
    │              │                    │
    └──── keywords_dict_refine ──── keyword_dict.py
```

**5대 키워드 카테고리**: card_names, actions, payments, weak_intents, nouns

---

## M-1: STT 비교 테스트 계획

### 목표
- 시나리오 오디오 8종 × 7개 STT 엔진 = 56회 비교 테스트
- WER, RTF, 화자 분리 정확도 측정
- 프로덕션 STT 엔진 결정

### 테스트 오디오 준비

| 시나리오 | 카테고리 | 예상 길이 |
|----------|----------|-----------|
| scenario-1 | 부정 결제 문의 | ~120초 |
| scenario-2 | 카드 분실 | ~115초 |
| scenario-3 | 한도 변경 | ~90초 |
| scenario-4 | 포인트 조회 | ~80초 |
| scenario-5 | 해외 결제 | ~100초 |
| scenario-6 | 연체 문의 | ~95초 |
| scenario-7 | 카드 발급 | ~85초 |
| scenario-8 | 정부지원 | ~90초 |

**오디오 소스**: 교육 시뮬레이션 TTS 생성 or 직접 녹음

### 평가 기준

| 지표 | 가중치 | 측정 방법 |
|------|--------|-----------|
| **WER (Word Error Rate)** | 40% | 기대 텍스트 vs STT 출력 비교 |
| **RTF (Real-Time Factor)** | 20% | 처리시간 / 오디오길이 |
| **키워드 보존율** | 25% | 핵심 키워드(카드명, 액션) 추출 가능 여부 |
| **화자 분리** | 15% | 상담사/고객 구분 정확도 (지원 모델만) |

### 실행 방법

```bash
# 1. 비교 대시보드 실행
source ~/miniconda3/bin/activate callact-vllm
cd /mnt/c/Users/AI-WS01/projects/call-act/backend_dev/local_servers
python comparison_dashboard.py

# 2. 브라우저에서 http://localhost:8889 접속
# 3. 각 시나리오 오디오 업로드 → STT 비교
# 4. "기대 텍스트" 입력 → WER 자동 계산
# 5. 정성 평가 (👍😐👎) 기록
```

### 결과 저장
- 자동: `test_logs/stt_sequential_comparison_*.json`
- 정성평가: `test_logs/ratings.json`
- 분석: `/test-logs` API로 통계 조회

---

## M-2: 키워드 추출 개선 설계

### 현재 문제점

| # | 문제 | 영향 |
|---|------|------|
| 1 | 인사 발화에서 키워드 추출 | 불필요한 RAG 검색 ("안녕하세요 테디카드" → 테디카드 검색) |
| 2 | VocabGate 25-35% 차단 | 유효한 쿼리도 차단될 수 있음 |
| 3 | Weak Intent 20개만 정의 | 넓은 의도 공간 미커버 |
| 4 | 카드명 Fuzzy 78% | 오탐 가능 (음성 유사어) |
| 5 | 단편적 키워드만 추출 | 상담 흐름(context) 무시 |

### 개선 방향 (3단계)

#### 단계 1: 비정보성 발화 필터링 ✅ 완료 (2026-02-10 20:20)
- **위치**: `keyword_extractor.py` → `NON_INFO_PATTERNS` (10개 패턴)
- **구현**: `extract()` 메서드 시작 시 패턴 매칭 → 비정보성이면 빈 ExtractedKeywords 반환
- **필터 대상**: 인사, 감사, 확인, 맞장구, 자기소개, 마무리 발화
- **테스트 결과**: scenario-2 전사 15문장 중 3문장(20%) 필터 → 불필요한 RAG 검색 방지
- **STT 교정 사전도 확장**: M-1 오류 패턴 5개 추가 (테리카드→테디카드, 재발부→재발급 등)

#### 단계 2: Weak Intent 확장 + VocabGate 개선 (이번 주)
- WEAK_INTENT_SYNONYMS 20 → 60개 확장
- 질문 패턴 추가: "뭐가", "어떤", "어떻게", "얼마"
- VocabGate에 question-pattern 매칭 추가

#### 단계 3: 상담 흐름 인식 (다음 주)
- 연속 발화에서 주제 연속성 판단
- 이전 step 키워드와 현재 키워드 유사도 비교
- 주제 전환 감지 시에만 새 RAG 검색 트리거

### 핵심 수정 파일

| 파일 | 수정 내용 |
|------|-----------|
| `backend/app/llm/delivery/keyword_extractor.py` | 비정보성 발화 필터 추가 |
| `backend/app/rag/vocab/keyword_dict.py` | WEAK_INTENT_SYNONYMS 확장 |
| `backend/app/rag/router/signals.py` | question-pattern VocabGate 추가 |
| `backend/app/rag/pipeline/pipeline.py` | 상담 흐름 컨텍스트 유지 |

---

## M-3: RAG 검색 품질 (M-1,2 이후)

### 의존성
- M-1 완료 → STT 정확도 향상 → 깨끗한 키워드 입력
- M-2 완료 → 정확한 키워드 → 정확한 문서 검색

### 예정 개선
1. **Relevance Threshold**: 유사도 점수 하한 설정 (현재 없음)
2. **중복 문서 방지**: 이전 step에서 보여준 문서 제외
3. **상담 단계별 필터링**: 인사→본인확인→문의→처리→마무리 단계 인식

---

## 실행 일정

| 날짜 | 작업 | 담당 |
|------|------|------|
| 2/10 (월) | Phase 3 계획 수립 + 문서 업데이트 | M |
| 2/10-11 | M-1: 시나리오 오디오 준비 + STT 비교 테스트 | M |
| 2/11-12 | M-2 단계 1: 비정보성 발화 필터 구현 | M + B |
| 2/12-13 | M-2 단계 2: Weak Intent 확장 + VocabGate 개선 | M + B |
| 2/13-14 | M-1 결과 분석 + STT 엔진 결정 | M |
| 2/14-15 | M-2 단계 3: 상담 흐름 인식 설계 | M + B |
| 2/17 (월) | M-3: RAG 검색 품질 개선 착수 | B + D |

---

## 성공 지표

| 지표 | 현재 | 목표 |
|------|------|------|
| STT WER (한국어) | TBD (측정 예정) | < 15% |
| 키워드 추출 정확도 | ~67% (Phase A 이전) → 100% (Phase A 이후) | 유지 100% |
| VocabGate 정당 통과율 | 65-75% | > 85% |
| RAG 관련 문서 정확도 | 미측정 | > 80% (top-3 중 1개 이상 적합) |
| 비정보성 발화 필터율 | 0% | > 90% |
