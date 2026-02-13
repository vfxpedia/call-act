# Backend 세션 작업 지시: B-7, B-8, B-8b

> **지시자**: AI/ML 팀장 (M 세션)
> **긴급도**: 최상
> **배경 문서**: `docs/levelup/06_RAG_CARD_RETRIEVAL_FIX.md` (근본 원인 분석 전체)

---

## 배경

RAG 카드 검색이 정상 작동하지 않는 근본 원인 3가지가 발견되었습니다.
아래 3건의 수정을 순서대로 진행해주세요.

---

## 작업 B-7: 가이드 테이블 card_name 필터 추가 (최우선)

### 문제

`backend/app/rag/retriever/db.py`의 `build_where_clause()` 함수에서,
**가이드 테이블(`_is_guide_table()`)일 때 card_name 필터가 완전히 누락**되어 있습니다.

현재 코드 (line 372~):
```python
if _is_guide_table(table):
    # ... exclude 로직들 ...
    guide_terms = _expand_guide_terms(unique_in_order([*intent_values, *weak_values]))
    guide_group = _build_like_group(guide_terms, params)
    if guide_group:
        clauses.append(guide_group)
```

`card_values` (예: `["나라사랑카드"]`)가 라우터에서 넘어와도 **완전히 무시**됩니다.
`else:` 블록 (line 415-441)에서만 `card_meta_clause`를 구성하는데, 이건 카드 테이블용입니다.

### 수정 내용

`if _is_guide_table(table):` 블록의 `guide_terms` 처리 직전에 card_name 필터를 추가하세요.

`card_terms`는 이미 line 366에서 `_expand_card_terms(card_values)`로 추출되어 있습니다.

```python
if _is_guide_table(table):
    # ... 기존 exclude 로직들 그대로 유지 ...

    # ── B-7: 가이드 테이블에서도 card_name으로 content/title 필터링 ──
    if card_terms:
        card_group = _build_like_group(card_terms, params)
        if card_group:
            clauses.append(card_group)

    guide_terms = _expand_guide_terms(unique_in_order([*intent_values, *weak_values]))
    guide_group = _build_like_group(guide_terms, params)
    if guide_group:
        clauses.append(guide_group)
```

### 동작 원리

- `_build_like_group(["나라사랑"], params)` → `(content ILIKE '%나라사랑%' OR metadata->>'title' ILIKE '%나라사랑%')`
- card_terms + guide_terms가 모두 AND로 clauses에 추가됨
- "나라사랑카드 분실" → WHERE (content ILIKE '%나라사랑%') AND (content ILIKE '%분실%')
- 결과가 0건이면 line 504-517의 기존 fallback이 WHERE를 완화하여 재검색

### 주의사항

- `card_terms`가 빈 리스트일 때는 아무것도 추가하지 않음 (기존 동작 유지)
- fallback 로직(line 504-517)이 이미 결과 0건 처리를 하므로 추가 fallback 불필요
- `backend_dev/app/rag/retriever/db.py`도 동일하게 수정 (팀레포+개발레포 동기화)

---

## 작업 B-8: card_products 임베딩 활성화

### 문제

`backend/app/rag/retriever/db.py` line 243:
```python
embedding_expr = "NULL::vector(1536) AS embedding"
```

DB에 card_products 398건 **전부 임베딩이 있음**에도 코드가 NULL로 덮어씌움.
결과적으로 card_products는 항상 `text_search()`로만 검색됨 (line 462-467).

### 수정 내용

```python
# 변경 전
embedding_expr = "NULL::vector(1536) AS embedding"

# 변경 후
embedding_expr = "embedding"
```

### 영향 범위

이 변경으로 `vector_search()` line 462-467의 분기:
```python
if actual_table == "card_products":
    terms = _extract_query_terms(query)
    ...
    return text_search(...)
```
이 더 이상 실행되지 않을 수 있습니다. card_products에 임베딩이 있으므로 vector_search 경로를 탈 수 있습니다.

**검증 필요**: 임베딩 활성화 후 카드 검색 결과가 text_search 대비 동등하거나 나은지 확인.
만약 품질이 떨어지면 text_search fallback을 유지하되, 둘 다 시도하는 하이브리드 방식 검토.

---

## 작업 B-8b: _source_sql 가이드 metadata에 card_name 반영 (D-7 이후)

### 전제

Data팀이 D-7(guide metadata card_name 매핑)을 완료한 후 진행.

### 수정 내용

`backend/app/rag/retriever/db.py` `_source_sql()` line 244-254:

```python
# 변경 전
elif actual == "service_guide_documents":
    content_expr = "content"
    metadata_expr = (
        "COALESCE(metadata, '{}'::jsonb) || jsonb_build_object("
        "'title', title, "
        "'category', category, "
        "'category1', document_type, "
        "'source_table', 'service_guide_documents'"
        ")"
    )

# 변경 후
elif actual == "service_guide_documents":
    content_expr = "content"
    metadata_expr = (
        "COALESCE(metadata, '{}'::jsonb) || jsonb_build_object("
        "'title', title, "
        "'card_name', COALESCE(metadata->>'card_name', ''), "
        "'category', category, "
        "'category1', document_type, "
        "'source_table', 'service_guide_documents'"
        ")"
    )
```

이렇게 하면 검색 결과의 metadata에 card_name이 포함되어,
B-7의 card_meta_clause 방식으로도 가이드 필터링이 가능해집니다.

---

## 검증

B-7 + B-8 수정 후 아래 스크립트로 검증:

```python
# backend_dev/local_servers/test_rag_card_fix.py
import asyncio
from app.rag.pipeline.search import run_search

async def test():
    # 테스트 1: 카드명+액션 조합
    r1 = await run_search("나라사랑카드 분실", top_k=5)
    r2 = await run_search("국민행복카드 발급", top_k=5)
    r3 = await run_search("분실", top_k=5)

    print("=== 나라사랑카드 분실 ===")
    for d in r1.docs[:3]:
        print(f"  {d.get('title', '?')[:50]}  score={d.get('score', 0):.3f}")

    print("=== 국민행복카드 발급 ===")
    for d in r2.docs[:3]:
        print(f"  {d.get('title', '?')[:50]}  score={d.get('score', 0):.3f}")

    print("=== 분실 (카드 무관) ===")
    for d in r3.docs[:3]:
        print(f"  {d.get('title', '?')[:50]}  score={d.get('score', 0):.3f}")

    # 핵심 검증: r1과 r2의 결과가 달라야 함
    ids1 = {d.get('id') for d in r1.docs[:3]}
    ids2 = {d.get('id') for d in r2.docs[:3]}
    overlap = ids1 & ids2
    if overlap:
        print(f"\n⚠️ 결과 겹침: {overlap}")
    else:
        print(f"\n✅ 카드별 다른 결과 반환!")

asyncio.run(test())
```

---

## 완료 후

1. CLAUDE.md Backend 섹션에 B-7, B-8 완료 기록 (타임스탬프 포함)
2. `backend_dev/app/rag/retriever/db.py`도 동기화
3. M 세션에 검증 결과 공유
