# Phase A-C 고도화 최종 결과

> **작성**: 2026-02-10
> **담당**: DB/Backend
> **상태**: Phase A-C 완료, 테스트 통과

---

## 1. 전체 요약

| Phase | 목표 | 핵심 성과 | 테스트 |
|-------|------|----------|--------|
| **A** | STT 품질 + 키워드 추출 | 할루시네이션 57%→100%, VocabGate 67%→100% | 21/21 |
| **B** | API 보완 + RAG 검색 강화 | FAQ 버그 수정, FlashText 복합어 해결, DB 스크립트 안전성 | 8/8 항목 |
| **C** | 통합 검증 + 데이터 품질 | 3개 테이블 100% embedding, 연회비 0% NULL | 6/6 |

---

## 2. Phase A: STT 할루시네이션 + VocabGate

### 변경 파일

| 파일 | 변경 |
|------|------|
| `backend/app/audio/whisper.py` | `prompt=WHISPER_PROMPT` 추가, 필터 키워드 12→22개, 반복 패턴/최소 길이 체크 |
| `backend/app/rag/vocab/keyword_dict.py` | weak_intent 5→20개, "안내" STOPWORDS 제거 |

### S1: Whisper 프롬프트 적용

Whisper API 호출 시 `prompt=WHISPER_PROMPT` 파라미터를 추가하여 "한국 신용카드 고객센터 통화" 컨텍스트를 제공. YouTube/방송 관련 할루시네이션 대폭 감소.

### S2+S3: 할루시네이션 필터 강화

```
추가 키워드(10개): "구독 좋아요", "오늘도 맛있게", "잘 먹었습니다", "감사합니다 여러분",
                   "다음 시간에", "그럼 다음", "시간에 만나요", "자막 제공", "자막 by", "한국어 자막"
반복 패턴: (.{2,}?)\1{2,}  →  "아아아아아아" 차단
최소 길이: 2자 미만 차단
```

### R1: weak_intent 확장 (5 → 20개)

```
기존: 혜택, 발급, 신청, 사용, 사용처
추가: 조회, 확인, 안내, 상담, 변경, 해지, 취소, 등록, 한도, 납부, 결제, 이체, 충전, 환불, 교환
```

### 테스트 결과

```
STT 할루시네이션 필터: 12/21 (57%) → 21/21 (100%)  +9건 개선
VocabGate 통과율:     12/21 (57%) → 18/21 (86%)   +6건 개선
VocabGate 정확도:     12/18 (67%) → 18/18 (100%)  오탐 0건
```

---

## 3. Phase B: API 보완 + RAG 검색 강화

### B-5: FAQ API SELECT 버그 수정

`frequent_inquiries.py`의 두 SQL 쿼리(목록/상세)에 `related_source_table`, `related_document_type` 컬럼 누락 → 추가.

`db_setup.sql`의 CREATE TABLE에도 동일 컬럼 누락 → 추가.

### B-6: 특수카드 검색 오염 방지

`retrieve.py`에 `exclude_id_patterns` 필터 추가. "다둥이", "나라사랑" 등 특수카드 검색 시 일반 카드가 섞이지 않도록 SQL WHERE 절에서 패턴 제외.

### B-8: FlashText + fallback 항상 병합

**문제**: FlashText의 greedy L→R 소비로 "포인트적립"에서 "포인트"만 추출, "적립" 누락.

**해결**: `extract_signals()`에서 FlashText 결과와 `_fallback_contains` 결과를 항상 병합.

```python
# Before: fallback은 FlashText가 0건일 때만 실행
# After: 항상 병합
card_names = unique_in_order([
    *card_kp.extract_keywords(normalized),
    *_fallback_contains(get_card_name_synonyms(), normalized),
])
```

### DB 스크립트 동기화

| 항목 | 내용 |
|------|------|
| `fix_card_products_data.py` | D-13 로직 통합: 체크카드=0, structured 파싱, 실적조건 추출 |
| `01a_setup_callact_db.py` | Step 5-1에 fix_card_products_data() 자동 호출 연결 |
| `load_frequent_inquiries.py` | related_source_table, related_document_type 동기화 |
| `populate_extended_fields.py` | quality_score, 실제 문서 ID 참조 동기화 |

### Phase B 전체 현황

| # | 작업 | 상태 |
|---|------|------|
| B-1 | feedbackScore/satisfactionScore POST | 확인 완료 |
| B-2 | routing.matched 구조 | 확인 완료 |
| B-3 | satisfaction_score GET 응답 | 확인 완료 |
| B-4 | is_best_practice 목록 포함 | 확인 완료 |
| B-5 | FAQ API SELECT 버그 수정 | **수정 완료** |
| B-6 | 특수카드 scope 필터 | 적용 완료 |
| B-7 | relevanceScore + search_time_ms | 구현 완료 |
| B-8 | FlashText+fallback 병합 | **구현 완료** |

---

## 4. Phase C: 통합 검증 + 데이터 품질

### 테스트 결과

| 테스트 | 내용 | 결과 |
|--------|------|------|
| T-1 | RAG 소스 3개 테이블 데이터 완전성 | **PASS** — embedding 100%, 중복 0 |
| T-1b | card_products 연회비/브랜드 품질 | **PASS** — fee NULL 0%, brand NULL 0% |
| T-2 | FAQ → 실 문서 연결 | **PASS** — 10/10 매칭, sourceTable 100% |
| T-3 | referenced_documents JSONB 구조 | **PASS** — 구조 오류 0건 |
| T-4 | documents/{id} fullText 해석 | **PASS** — 15/15 정상 |
| T-5 | VocabGate 키워드 매칭 시뮬레이션 | **PASS** — 13/14 (93%) |

### DB 데이터 현황

| 테이블 | 건수 | embedding | 비고 |
|--------|------|-----------|------|
| card_products | 398 | 100% | fee NULL 0%, brand NULL 0% |
| service_guide_documents | 1,251 | 100% | |
| notices | 52 | 100% | |
| consultations | 6,552 | - | referenced_documents 50건 |
| customers | 2,500 | - | |
| employees | 72 | - | |
| frequent_inquiries | 10 | - | sourceTable 100% |
| keyword_dictionary | 2,881 | - | |
| simulation_scenarios/results | 5/150 | - | |

### card_products 품질 (fix_card_products_data 실행 후)

| 필드 | Before | After |
|------|--------|-------|
| annual_fee_domestic NULL | 261 (65.6%) | **0 (0%)** |
| brand NULL | 23 (5.8%) | **0 (0%)** |
| performance_condition 비어있음 | 26 | **0** |
| annual_fee_global NULL | 187 | 48 (국내전용 카드, 정상) |

---

## 5. DB 재적재 안전성

### 스크립트 동기화 현황

`backend/` (팀) ↔ `backend_dev/` (개발) 핵심 파일 검증 결과:

| 파일 | 상태 |
|------|------|
| `01a_setup_callact_db.py` | 동일 |
| `01b_populate_mock_data.py` | 동일 |
| `modules/schema_runner.py` | 동일 |
| `modules/__init__.py` | 동일 |
| `modules/fix_card_products_data.py` | 동일 |
| `modules/load_frequent_inquiries.py` | 동일 |
| `modules/load_consultations.py` | 동일 |
| `modules/populate_extended_fields.py` | 동일 |
| `db_setup.sql` | 동일 |
| `13_extend_consultations_table.sql` | 동일 |
| `14_schema_v4_frontend_integration.sql` | 동일 |

### 재적재 실행 순서 (01a_setup_callact_db.py)

```
1. run_all_schemas()
   ├─ db_setup.sql (기본 테이블)
   ├─ 02_setup_tedicard_tables.sql (card_products, service_guide, notices)
   ├─ 03~12 (keyword, customer, simulation, audit, relevance)
   ├─ load_category_mappings() (57→8+15 매핑)
   └─ 14_schema_v4_frontend_integration.sql (consultations 확장 필드)
2. load_employees_data()
3. load_customers_data()
4. load_hana_data() + update_employee_performance()
5. load_keyword_dictionary()
6. load_teddycard_data()
7. fix_card_products_data()      ← Phase B-C: 연회비/브랜드/실적조건 자동 보완
8. load_frequent_inquiries_data() ← Phase C: sourceTable/documentType 포함
9. calculate_all_trends()
10. generate_mock_simulation_data() + generate_mock_audit_data()
11. verify_load()
```

```
이후: python 01b_populate_mock_data.py
  → consultations 확장 필드 (transcript, ai_summary, referenced_documents 등)
```

### 안전 장치

- `CREATE TABLE IF NOT EXISTS` / `ADD COLUMN IF NOT EXISTS` — 중복 실행 안전
- `ON CONFLICT DO UPDATE` — 재적재 시 데이터 덮어쓰기
- `RANDOM_SEED=42` — mock 데이터 재현 가능
- `fix_card_products_data()` — 오케스트레이터에 자동 연결, 재적재 시 빠짐 없이 실행

---

## 6. 변경 파일 전체 목록

### Backend 코드 변경

| 파일 | Phase | 변경 내용 |
|------|-------|----------|
| `app/audio/whisper.py` | A | WHISPER_PROMPT 적용, 할루시네이션 필터 강화 |
| `app/rag/vocab/keyword_dict.py` | A | weak_intent 5→20개 |
| `app/api/v1/endpoints/frequent_inquiries.py` | B | SELECT 쿼리 컬럼 추가 |
| `app/rag/router/signals.py` | B | FlashText+fallback 병합, VocabGate 로깅 |
| `app/rag/pipeline/pipeline.py` | B | VocabGate 차단 시 안내 메시지 |
| `app/rag/retriever/db.py` | B | exclude_id_patterns 필터 |
| `app/rag/pipeline/retrieve.py` | B | 특수카드 scope 필터 |
| `app/rag/policy/policy_pins.py` | B | 다둥이 카드 ID 수정 |
| `app/db/scripts/db_setup.sql` | B | frequent_inquiries 컬럼 추가 |
| `app/db/scripts/modules/fix_card_products_data.py` | B-C | D-13 로직 통합 |
| `app/db/scripts/01a_setup_callact_db.py` | B-C | 오케스트레이터에 fix 연결 |
| `app/db/scripts/modules/load_frequent_inquiries.py` | C | sourceTable 동기화 |
| `app/db/scripts/modules/populate_extended_fields.py` | C | quality_score 동기화 |

### 테스트 파일

| 파일 | 내용 |
|------|------|
| `tests/test_phase_a_verification.py` | STT 필터 21건 + VocabGate 21건 |
| `tests/test_phase_c_integration.py` | DB 통합 검증 T-1~T-5 (6개 테스트) |

---

## 7. 다음 단계

| 항목 | 설명 | 담당 |
|------|------|------|
| 프론트엔드 연동 테스트 | RAG 카드 → 문서 모달 → fullText 표시 | Frontend |
| VocabGate 형태소 분석 폴백 | 키워드 매칭 실패 시 명사 추출 재검토 | Backend |
| card_products 키워드 보강 | 49% 빈 배열 → 키워드 자동 추출 | Data |
| 카드명 VocabGate 매칭 | RAG_MATCH_CARD_NAMES=1 실서버 적용 | Backend |
| E2E 시나리오 테스트 | 다이렉트콜 → STT → RAG → 카드 → ACW 저장 | 3팀 공동 |
