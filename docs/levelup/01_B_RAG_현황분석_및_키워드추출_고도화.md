# 01_B: RAG 현황 분석 및 키워드 추출 고도화 계획

> **담당**: Backend
> **날짜**: 2026-02-10
> **상태**: 분석 완료 → 1차 조치 대기

---

## 1. 현재 RAG 파이프라인 흐름

```
사용자 음성 → [STT: Whisper] → 전사 텍스트
                                    ↓
                            [Vocab Match Gate]  ← ⚠️ 25-35% 차단
                                    ↓ (통과 시)
                            [키워드 추출]
                            ├── FlashText (사전 매칭)
                            ├── 형태소 분석 (KeywordExtractor)
                            ├── Fuzzy 매칭 (rapidfuzz)
                            └── 복합 패턴 (regex)
                                    ↓
                            [라우팅 결정]
                            ├── card_info → card_products 테이블
                            ├── card_usage → service_guide_documents 테이블
                            └── both → 양쪽 검색
                                    ↓
                            [문서 검색]
                            ├── 벡터 검색 (pgvector, cosine) ← guide만 작동
                            └── 텍스트 검색 (trigram)        ← card는 이것만
                                    ↓
                            [LLM 카드 생성 + 가이드 스크립트]
                                    ↓
                            [프론트엔드 표시]
                            ├── 칸반 카드 (currentSituation 2장 + nextStep 2장)
                            ├── 가이드 스크립트 (상담원 안내 멘트 3문장)
                            └── 검색 레이어, 상담 상세, 자주 찾는 문의 등
```

---

## 2. 핵심 문제 진단

### 🔴 문제 1: Vocab Match Gate가 쿼리의 25-35%를 차단

**파일**: `backend/app/rag/router/signals.py` → `has_vocab_match()`

**원인**: `RAG_REQUIRE_VOCAB_MATCH=1` (기본 ON)일 때, 쿼리에서 사전에 등록된 키워드가 하나도 발견되지 않으면 RAG를 아예 실행하지 않음.

**현재 등록된 약한 의도(weak_intent)**: 단 **5개** — "혜택", "발급", "신청", "사용", "사용처"

**실제 상담에서 나올 수 있지만 차단되는 예시**:
- "이거 어떻게 해요?" (키워드 없음)
- "잘 안 되는데요" (키워드 없음)
- "왜 안 돼요?" (키워드 없음)
- "확인 좀 해주세요" (키워드 없음)

### 🔴 문제 2: card_products 49%에 keywords 배열이 비어있음

**파일**: DB `card_products.keywords` 컬럼

**결과**: 키워드 기반 매칭 시 카드 상품의 절반이 검색 대상에서 제외됨.

### 🟡 문제 3: card_products 벡터 검색이 사실상 비활성

**파일**: `backend/app/rag/retriever/db.py` → `vector_search()`

카드 상품 테이블에 embedding HNSW 인덱스가 있지만, `vector_search()` 코드에서 `card_products`는 `text_search()`로 폴스루됨. 의미 기반 검색이 카드 상품에 적용되지 않음.

### 🟡 문제 4: 키워드 사전과 실데이터 불일치 81%

**분석 문서**: `docs/DB_DATA_ANALYSIS_v1.md`

- 키워드 사전 1,157개 중 실제 DB 데이터와 매칭되는 것 17.4%
- 가이드 문서 ↔ 카드 상품 간 공유 키워드 단 17개

### 🟢 잘 되고 있는 것

- STT(Whisper) 자체는 정확함 (VAD 원본 복원 완료)
- 세션 컨텍스트 유지 (카드명/의도 3턴/180초 TTL)
- LLM 카드 생성 품질 (gpt-4.1-mini)
- 가이드 스크립트 3문장 형식
- 벡터 검색 (service_guide_documents에서는 정상 작동)

---

## 3. 개선 우선순위 (Backend 관점)

| 순번 | 문제 | 영향도 | 난이도 | 조치 |
|------|------|--------|--------|------|
| **1** | weak_intent 5개 → 확장 | 🔴 높음 | 🟢 쉬움 | 즉시 실행 가능 |
| **2** | card_products 키워드 빈 배열 채우기 | 🔴 높음 | 🟡 중간 | Data 세션과 협업 |
| **3** | Vocab Gate 로직 완화 | 🔴 높음 | 🟡 중간 | 형태소 분석 폴백 추가 |
| **4** | card_products 벡터 검색 활성화 | 🟡 중간 | 🟢 쉬움 | retriever 코드 수정 |
| **5** | 키워드 사전 정합성 개선 | 🟡 중간 | 🟠 높음 | Data 세션 주도 |
| **6** | STT 오류 보정 사전 확장 | 🟡 중간 | 🟡 중간 | keywords_dict_refine.json 보강 |

---

## 4. 1차 조치 계획 (Backend 즉시 실행)

### 조치 A: weak_intent 확장 (signals.py)

현재 5개 → **15+개**로 확장:
```
기존: 혜택, 발급, 신청, 사용, 사용처
추가: 조회, 변경, 해지, 취소, 등록, 한도, 납부, 결제, 이체, 충전, 교환, 환불, 상담, 확인, 안내
```

### 조치 B: Vocab Gate에 형태소 분석 폴백 추가

FlashText/fuzzy 모두 실패 시 → KeywordExtractor의 명사 추출 결과로 재검토.
"확인 좀 해주세요" → 형태소 분석 → ["확인"] → weak_intent 매칭 → 통과.

### 조치 C: card_products 벡터 검색 활성화 (retriever 코드)

`vector_search()` 에서 card_products도 pgvector cosine 검색 사용하도록 수정.

---

## 5. 세션 간 협업 필요 사항

### → Data 세션에 요청
- card_products의 빈 keywords 배열 채우기 (49% → 0%)
- 키워드 사전(keywords_dict_v2)과 실데이터 정합성 높이기
- STT 오류 보정 사전(keywords_dict_refine.json) 확장

### → Frontend 세션에 알림
- RAG 응답 구조는 변경 없음 (currentSituation, nextStep, guidanceScript)
- 카드의 `keywords` 배열에 더 많은 태그가 들어올 수 있음
- 검색 레이어에서 실데이터 RAG 연동 시 같은 ScenarioCard 형식 사용

---

## 6. 검증 방법

### 개선 전/후 비교 테스트 쿼리 (10개)

| # | 쿼리 | 현재 예상 | 개선 후 예상 |
|---|------|----------|------------|
| 1 | "카드 분실했어요" | ✅ 정상 (분실 = action) | ✅ 유지 |
| 2 | "잔액 확인 좀요" | ❌ 차단 (확인 미등록) | ✅ 통과 (확인 = weak_intent) |
| 3 | "이거 어떻게 써요?" | ❌ 차단 | ✅ 통과 (사용 의도 감지) |
| 4 | "리볼빙 해지하고 싶어요" | ✅ 정상 (리볼빙 = action) | ✅ 유지 |
| 5 | "왜 결제가 안 돼요?" | ✅ 정상 (결제 = action) | ✅ 유지 |
| 6 | "한도 좀 올려주세요" | ❌ 가능성 (한도 미등록) | ✅ 통과 (한도 = weak_intent) |
| 7 | "포인트 얼마 있어요?" | ✅ 정상 (포인트 = 혜택) | ✅ 유지 |
| 8 | "납부일이 언제예요?" | ❌ 차단 (납부 미등록) | ✅ 통과 (납부 = weak_intent) |
| 9 | "Pay 신한카드 혜택" | ✅ 정상 (카드명 + 혜택) | ✅ 유지 |
| 10 | "그냥 좀 알아보려고요" | ❌ 차단 | 🟡 형태소 폴백 시도 |

> 현재 10개 중 4개 차단 → 개선 후 1개 이하로 줄이는 것이 목표

---

## 7. 다음 단계

1차 조치 완료 후 → 검증 테스트 실행 → 결과 보고 → 2차 조치 계획 수립

2차 조치 후보:
- 키워드 추출 정확도 개선 (형태소 분석기 사전 확장)
- 복합 쿼리 처리 ("분실했는데 재발급 가능해요?" → [분실, 재발급] 동시 추출)
- 카드명 퍼지 매칭 threshold 조정 (현재 78% → 최적값 탐색)
- 상담 이력 기반 검색 가중치 (자주 찾는 문서 boost)
