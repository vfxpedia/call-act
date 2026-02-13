# RAG 카드 검색 실패 근본 원인 분석 + 수정 지시

> **작성일**: 2026-02-10 22:30
> **작성**: AI/ML 팀장 (M 세션)
> **긴급도**: 최상 - RAG 핵심 기능이 정상 작동하지 않는 상태
> **검증 데이터**: DB 직접 쿼리로 확인 완료

---

## 1. 문제 현상

"나라사랑카드 분실" 같은 **카드명 + 액션** 조합 질문에서:
- 라우터가 `card_names: ["나라사랑카드"]`, `actions: ["분실"]`을 정확히 추출함
- 그러나 DB 검색 단계에서 **카드명이 무시되고 "분실" intent로만 검색**
- 결과: 모든 "분실" 관련 가이드가 카드 구분 없이 뒤섞여 반환됨
- "나라사랑카드 분실" vs "테디카드 분실" 검색 결과가 **동일** (있어선 안 됨)

---

## 2. 근본 원인 3가지

### 원인 A: service_guide_documents의 card_name 메타데이터 전부 NULL

```sql
-- 실행 결과 (2026-02-10 22:30 확인)
SELECT COUNT(*) FROM service_guide_documents WHERE metadata->>'card_name' IS NOT NULL;
-- 결과: 0건 (1,251건 중 0건)
```

`_source_sql()` (`db.py:244-254`)에서 가이드 테이블 metadata 구성 시 `card_name` 필드 미포함:
```python
# card_products는 card_name을 넣음 (line 236)
"'card_name', name, "

# service_guide_documents는 card_name이 없음 (line 246-252)
"'title', title, "
"'category', category, "
"'category1', document_type, "
# ← card_name 필드 없음!
```

**하지만 가이드 ID 자체에 카드명이 인코딩되어 있음:**
| 가이드 ID 접두사 | 카드명 | 건수 |
|----------------|--------|------|
| `k패스_*` | K패스 | 41건 |
| `국민행복카드_*` | 국민행복카드 | 28건 |
| `나라사랑체크카드_*` | 나라사랑카드 | 21건 |
| `narasarang_faq_*` | 나라사랑카드 | 15건 |
| `서울시다둥이행복카드_*` | 서울시다둥이행복카드 | 19건 |
| `네이버페이카드_*` + `naverpay_*` | 네이버페이카드 | 23건 |
| `쿠팡와우카드_*` | 쿠팡와우카드 | 8건 |
| `hyundai_applepay_*` | Apple Pay | 34건 |

**→ 총 209건이 ID 패턴으로 카드명 추출 가능** (나머지 1,042건은 일반 약관/가이드)

### 원인 B: 가이드 테이블 WHERE절에서 card_name 필터 완전 누락

`build_where_clause()` (`db.py:372-409`):

```python
if _is_guide_table(table):       # ← 가이드 테이블일 때
    # card_name 필터 없음! intent만 처리
    guide_terms = _expand_guide_terms(...)
    guide_group = _build_like_group(guide_terms, params)
else:                             # ← 카드 테이블일 때만
    card_meta_clause = ...        # card_name ILIKE 매칭
```

**가이드 테이블에서는 card_name 매칭 코드가 완전히 빠져있음.**
라우터가 `filters.card_name = ["나라사랑카드"]`를 넘겨도 무시됨.

### 원인 C: card_products 임베딩을 코드에서 NULL로 덮어씌움

```python
# db.py:243
embedding_expr = "NULL::vector(1536) AS embedding"  # 항상 NULL 반환
```

```sql
-- 실제 DB 상태 (확인 완료)
SELECT COUNT(*) FROM card_products WHERE embedding IS NOT NULL;
-- 결과: 398건 / 398건 (100% 임베딩 있음!)
```

**DB에 398건 전부 임베딩이 있지만, 코드가 NULL로 덮어씌움** → 항상 text_search fallback.
카드 의미 검색이 불가능한 상태.

---

## 3. 데이터 흐름 추적 ("나라사랑카드 분실")

```
[1] router.py: route_query("나라사랑카드 분실")
    → route: "card_usage", db_route: "guide_tbl"
    → filters: {card_name: ["나라사랑카드"], intent: ["분실도난"]}
    ✅ 라우터는 정상 동작

[2] retrieve.py: retrieve_docs() → tables = ["service_guide_documents"]
    ✅ 테이블 선택 정상

[3] db.py: build_where_clause(filters, "service_guide_documents")
    → _is_guide_table() = True
    → card_name 필터 건너뜀! ← 🔴 원인 B
    → guide_terms = ["분실", "도난", ...] 만 사용
    → WHERE content ILIKE '%분실%'
    🔴 카드명 "나라사랑카드"가 필터에서 완전 누락

[4] db.py: vector_search()
    → embedding 유사도 + WHERE 분실 → 모든 분실 관련 가이드 반환
    → 나라사랑카드 특화 가이드가 상위에 오는 건 우연에 의존

[5] 결과: 카드 무관하게 "분실" 가이드 전체가 뒤섞여 반환
```

---

## 4. 수정 사항 (3가지 모두 수정해야 함)

### 수정 1: D-7 — service_guide metadata에 card_name 매핑 (Data팀)

**목표**: 가이드 ID 패턴에서 카드명을 추출하여 `metadata.card_name`에 저장

**매핑 규칙** (DB 조사 결과 기반):

```python
ID_TO_CARD_RULES = {
    # 한글 접두사 (ID = "접두사_숫자")
    "나라사랑체크카드": "나라사랑카드",
    "국민행복카드": "국민행복카드",
    "서울시다둥이행복카드": "서울시다둥이행복카드",
    "네이버페이카드": "네이버페이카드",
    "쿠팡와우카드": "쿠팡와우카드",
    "k패스": "K패스",
    "K패스": "K패스",

    # 영문 접두사
    "narasarang_faq": "나라사랑카드",
    "naverpay": "네이버페이카드",
    "minsaeng_faq": "민생회복소비쿠폰",
    "hyundai_applepay": "Apple Pay",
}
```

**스크립트**: `backend_dev/app/db/scripts/modules/populate_guide_card_names.py` (신규)

```python
# 핵심 로직
for guide_id in all_guide_ids:
    card_name = None
    for prefix, name in ID_TO_CARD_RULES.items():
        if guide_id.startswith(prefix):
            card_name = name
            break

    if card_name:
        UPDATE service_guide_documents
        SET metadata = COALESCE(metadata, '{}'::jsonb) || jsonb_build_object('card_name', card_name)
        WHERE id = guide_id;
```

**검증**:
```sql
SELECT metadata->>'card_name' AS cn, COUNT(*)
FROM service_guide_documents
WHERE metadata->>'card_name' IS NOT NULL
GROUP BY cn ORDER BY COUNT(*) DESC;
-- 목표: 209건 이상, 7~8개 카드그룹
```

### 수정 2: B-7 — 가이드 테이블 card_name 필터 추가 (Backend팀)

**파일**: `backend/app/rag/retriever/db.py`
**위치**: `build_where_clause()` 함수의 `if _is_guide_table(table):` 블록 (line 372~)

**현재 코드** (line 372, 406-409):
```python
if _is_guide_table(table):
    # ... exclude 로직들 ...
    guide_terms = _expand_guide_terms(unique_in_order([*intent_values, *weak_values]))
    guide_group = _build_like_group(guide_terms, params)
    if guide_group:
        clauses.append(guide_group)
```

**수정 코드**: guide_terms 처리 직전에 card_name 필터 추가
```python
if _is_guide_table(table):
    # ... 기존 exclude 로직 유지 ...

    # ── 가이드 테이블에서도 card_name으로 필터링 ──
    # card_terms는 이미 line 366에서 추출됨 (_expand_card_terms(card_values))
    if card_terms:
        card_group = _build_like_group(card_terms, params)
        if card_group:
            clauses.append(card_group)
    # ── 여기까지 추가 ──

    guide_terms = _expand_guide_terms(unique_in_order([*intent_values, *weak_values]))
    guide_group = _build_like_group(guide_terms, params)
    if guide_group:
        clauses.append(guide_group)
```

**핵심**: `_build_like_group(card_terms, params)`는 `content ILIKE '%나라사랑%' OR metadata->>'title' ILIKE '%나라사랑%'` 형태의 WHERE 조건을 생성.
- D-7에서 metadata.card_name이 채워지면: metadata 기반 필터도 추가 가능
- 그 전에도: content/title에 카드명이 포함된 가이드를 우선 반환

**fallback 주의**: card_terms + guide_terms가 모두 AND로 연결되므로, 카드명이 content에 없으면 결과가 0건이 될 수 있음.
→ `vector_search()` line 504-517의 기존 fallback이 이를 처리 (결과 0건이면 WHERE 완화하여 재검색)

### 수정 3: B-8 — card_products 임베딩 활성화 (Backend팀)

**파일**: `backend/app/rag/retriever/db.py`
**위치**: `_source_sql()` line 243

**현재 코드**:
```python
embedding_expr = "NULL::vector(1536) AS embedding"
```

**수정 코드**:
```python
embedding_expr = "embedding"
```

**주의**: 이 변경으로 `vector_search()` line 462-467의 card_products 분기가 더 이상 사용되지 않을 수 있음.
card_products에 임베딩이 활성화되면 벡터 검색이 가능해지므로, text_search fallback 대신 vector_search를 사용하게 됨.

**영향 범위**: `vector_search()` 내 `if actual_table == "card_products"` 분기 (line 462-467) 검토 필요.
임베딩 활성화 후 카드 검색 품질이 text_search 대비 나아지는지 비교 테스트 필요.

### 수정 4: B-8b — _source_sql() 가이드 metadata에 card_name 반영 (D-7 이후)

**파일**: `backend/app/rag/retriever/db.py`
**위치**: `_source_sql()` line 244-254

**현재 코드** (가이드 metadata 구성):
```python
metadata_expr = (
    "COALESCE(metadata, '{}'::jsonb) || jsonb_build_object("
    "'title', title, "
    "'category', category, "
    "'category1', document_type, "
    "'source_table', 'service_guide_documents'"
    ")"
)
```

**수정 코드** (D-7 완료 후):
```python
metadata_expr = (
    "COALESCE(metadata, '{}'::jsonb) || jsonb_build_object("
    "'title', title, "
    "'card_name', COALESCE(metadata->>'card_name', ''), "  # ← 추가
    "'category', category, "
    "'category1', document_type, "
    "'source_table', 'service_guide_documents'"
    ")"
)
```

이렇게 하면 DB의 `metadata.card_name`이 검색 결과의 metadata에도 포함됨.

---

## 5. 수정 순서 및 의존성

```
D-7 (metadata 매핑)  ─────────────────┐
                                       ├──→ B-8b (SQL metadata 반영) → 검증
B-7 (WHERE 필터 추가) ────────────────┘
B-8 (card_products 임베딩 활성화) ──────────→ 독립 검증
```

| 순서 | 작업 | 담당 | 의존성 | 효과 |
|------|------|------|--------|------|
| **1** | D-7: guide metadata card_name 매핑 | Data | 없음 | 209건 카드-가이드 연결 |
| **1** | B-7: 가이드 WHERE card_name 필터 | Backend | 없음 (D-7 전에도 content ILIKE로 동작) | 카드+intent 조합 검색 |
| **2** | B-8: card_products 임베딩 활성화 | Backend | 없음 | 카드 의미 검색 가능 |
| **3** | B-8b: _source_sql metadata card_name | Backend | D-7 완료 | 검색 결과에 card_name 포함 |

**B-7과 D-7은 병렬 진행 가능** (독립적). B-8도 독립 진행 가능.

---

## 6. 검증 방법

### 검증 1: DB 상태 확인 (D-7 완료 후)
```sql
SELECT metadata->>'card_name' AS cn, COUNT(*)
FROM service_guide_documents
WHERE metadata->>'card_name' IS NOT NULL AND metadata->>'card_name' != ''
GROUP BY cn ORDER BY COUNT(*) DESC;
-- 기대: 나라사랑카드 36, 국민행복카드 28, K패스 41, ...
```

### 검증 2: RAG 검색 품질 (B-7 완료 후)
```
테스트 1: "나라사랑카드 분실" → 나라사랑카드 관련 분실 가이드가 상위
테스트 2: "국민행복카드 발급" → 국민행복카드 관련 발급 가이드가 상위
테스트 3: "분실" 단독 → 일반 분실 가이드 (카드 무관)
```

**핵심: 테스트 1과 "국민행복카드 분실"의 결과가 달라야 정상** (현재는 동일)

### 검증 3: card_products 벡터 검색 (B-8 완료 후)
```
"할인이 많은 카드" → 의미 유사도 기반 카드 추천 (현재: text_search만)
"해외 이용 수수료 낮은 카드" → 관련 카드 반환
```

---

## 7. 역색인(F-1)의 역할 재정의

근본 원인 수정 후, F-1 역색인의 역할:
- ~~임시 보완책~~ → **속도 최적화 레이어 (< 1ms)** + **벡터 검색 보험**
- 벡터 검색이 정확해져도, 첫 키워드 즉시 반응은 역색인이 담당 (아키텍처 v2 Stage 2)
- 벡터 검색 실패 시 fallback으로도 유지

---

## 부록: DB 실측 데이터 (2026-02-10 22:30)

| 항목 | 값 |
|------|-----|
| service_guide_documents 전체 | 1,251건 |
| metadata.card_name NOT NULL | **0건** (0%) |
| ID 패턴으로 카드명 추출 가능 | 209건 (17%) |
| 나머지 (일반 약관/가이드) | 1,042건 (83%) — sinhan_terms 988, merged 35, plumb 19 |
| card_products 전체 | 398건 |
| card_products embedding NOT NULL | **398건 (100%)** — 코드가 NULL로 덮어씌움 |
| card_products keywords NOT NULL | 398건 (100%) |
| guide document_type 분포 | terms 1,070, faq 107, guide 74 |
