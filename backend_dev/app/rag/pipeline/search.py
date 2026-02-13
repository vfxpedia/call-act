from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import asyncio
import os
import time

from app.rag.cache.retrieval_cache import (
    RETRIEVE_CACHE_ENABLED,
    build_retrieval_cache_key,
    retrieval_cache_get,
    retrieval_cache_set,
)
from app.rag.pipeline.retrieve import (
    post_filter_docs,
    retrieve_consult_cases,
    retrieve_docs,
    retrieve_docs_card_info,
)
from app.rag.pipeline.utils import (
    apply_session_context,
    build_retrieve_cache_entries,
    docs_from_retrieve_cache,
    format_ms,
    should_search_consult_cases,
)
from app.rag.postprocess.keywords import normalize_text
from app.rag.router.router import route_query
from app.rag.policy.search_gating import decide_search_gating
from app.rag.policy.answer_class import classify as classify_answer_class

import logging

_logger = logging.getLogger(__name__)

LOG_RETRIEVER_DEBUG = os.getenv("RAG_LOG_RETRIEVER_DEBUG") == "1"
RETRIEVE_BUDGET_MS = int(os.getenv("RAG_RETRIEVE_BUDGET_MS", "950"))
RETRIEVE_MAX_STAGES = int(os.getenv("RAG_RETRIEVE_MAX_STAGES", "2"))
KEYWORD_INDEX_ENABLED = os.getenv("RAG_KEYWORD_INDEX", "1") != "0"
FLOW_PREDICTION_ENABLED = os.getenv("RAG_FLOW_PREDICTION", "1") != "0"
# M-3: 최소 relevance 임계값 — 이 미만 score 문서는 제거 (최소 1개 유지)
MIN_RELEVANCE_THRESHOLD = float(os.getenv("RAG_MIN_RELEVANCE", "0.08"))


@dataclass(frozen=True)
class SearchResult:
    routing: Dict[str, Any]
    docs: List[Dict[str, Any]]
    consult_docs: List[Dict[str, Any]]
    retrieve_cache_status: str
    should_search: bool
    no_search_message: Optional[str]
    t_start: float
    t_route: float
    t_retrieve: float
    flow_docs: List[Dict[str, Any]] = None  # M-2 단계3: 흐름 예측 문서


def route(query: str) -> Dict[str, Any]:
    return route_query(query)


def _retrieval_failed(docs: List[Dict[str, Any]], routing: Dict[str, Any]) -> bool:
    if not docs:
        return True
    top = docs[0]
    score = top.get("score")
    if isinstance(score, (int, float)) and score < 0.05:
        return True
    filters = routing.get("filters") or routing.get("boost") or {}
    if routing.get("route") == "card_info" and filters.get("card_name"):
        if top.get("card_match") is False:
            return True
    return False


def _try_keyword_index(query: str, routing: Dict[str, Any], top_k: int) -> List[Dict[str, Any]]:
    """역색인에서 키워드 기반 문서 조회 (< 1ms).

    routing.matched에서 추출된 card_names, actions, weak_intents를 사용하여
    미리 빌드된 역색인에서 문서를 즉시 조회합니다.

    Returns:
        역색인 매칭 문서 리스트 (빈 리스트 = 매칭 없음)
    """
    if not KEYWORD_INDEX_ENABLED:
        return []
    try:
        from app.rag.cache.keyword_doc_index import lookup, lookup_combo, is_built
        if not is_built():
            return []
    except ImportError:
        return []

    matched = routing.get("matched") or {}
    card_names = matched.get("card_names") or []
    actions = matched.get("actions") or []
    weak_intents = matched.get("weak_intents") or []

    # 키워드 수집 (중복 제거)
    keywords = []
    seen = set()
    for kw_list in (card_names, actions, weak_intents):
        for kw in kw_list:
            if kw and kw not in seen:
                keywords.append(kw)
                seen.add(kw)

    if not keywords:
        return []

    # 역색인 조회
    if len(keywords) >= 2:
        entries = lookup_combo(keywords, top_k=top_k * 2)
    else:
        entries = lookup(keywords[0], top_k=top_k * 2)

    if not entries:
        return []

    # IndexEntry → 전체 문서 fetch (DB에서 content, structured 포함)
    from app.rag.retriever.db import fetch_docs_by_ids
    from collections import defaultdict

    # 테이블별로 그룹핑
    by_table: Dict[str, List] = defaultdict(list)
    entry_map: Dict[str, Any] = {}  # doc_id → IndexEntry
    for entry in entries:
        table = entry.table
        if table in ("card_products", "service_guide_documents"):
            by_table[table].append(entry.doc_id)
            entry_map[entry.doc_id] = entry

    docs: List[Dict[str, Any]] = []
    for table, ids in by_table.items():
        fetched = fetch_docs_by_ids(table, ids)
        for doc in fetched:
            doc_id = doc.get("id")
            idx_entry = entry_map.get(doc_id)
            if idx_entry:
                # M-3: relevance는 키워드 소스 가중치(0.5~1.0)이지 쿼리 관련도가 아님
                # 벡터 검색 score(0.2~0.6)와 동일 스케일로 정규화
                doc["score"] = idx_entry.relevance * 0.45
                doc["_from_keyword_index"] = True
                doc["_index_keywords"] = keywords
            docs.append(doc)

    # relevance 내림차순 정렬
    docs.sort(key=lambda d: d.get("score", 0.0), reverse=True)
    _logger.debug(
        "keyword_index: query=%r keywords=%s → %d docs",
        query[:50], keywords, len(docs),
    )
    return docs[:top_k]


def _merge_index_and_vector_docs(
    index_docs: List[Dict[str, Any]],
    vector_docs: List[Dict[str, Any]],
    top_k: int,
) -> List[Dict[str, Any]]:
    """역색인 문서와 벡터 검색 문서를 score 기반 병합 (중복 제거)."""
    seen: set = set()
    merged: List[Dict[str, Any]] = []

    # M-3: 모든 문서를 합친 후 score 내림차순 정렬 (출처 무관)
    for doc in index_docs + vector_docs:
        doc_id = doc.get("id")
        if doc_id and doc_id not in seen:
            seen.add(doc_id)
            merged.append(doc)

    merged.sort(key=lambda d: d.get("score", 0.0), reverse=True)
    return merged[:top_k]


def _flip_route_for_fallback(routing: Dict[str, Any]) -> Dict[str, Any]:
    route_name = routing.get("route") or routing.get("ui_route")
    flipped = dict(routing)
    if route_name == "card_info":
        flipped["route"] = "card_usage"
        flipped["db_route"] = "guide_tbl"
    elif route_name == "card_usage":
        flipped["route"] = "card_info"
        flipped["db_route"] = "card_tbl"
    flipped["_lane_fallback_used"] = True
    flipped["route_fallback_from"] = route_name
    return flipped


async def run_search(
    query: str,
    *,
    top_k: int,
    enable_consult_search: bool = True,
    session_state: Optional[Dict[str, Any]] = None,
) -> SearchResult:
    t_start = time.perf_counter()
    routing = apply_session_context(query, route(query), session_state)
    phone_intent = any(k in query for k in ("전화", "번호", "고객센터", "연락처", "전화번호"))
    if phone_intent:
        filters = routing.get("filters") or {}
        filters["phone_lookup"] = True
        routing["filters"] = filters
        routing["route"] = "card_usage"
        routing["db_route"] = "guide_tbl"
        routing["ui_route"] = "card_usage"
        if (routing.get("route") or routing.get("ui_route")) == "card_info":
            routing["route"] = "card_usage"
    t_route = time.perf_counter()
    if "lane_allow_mixed" not in routing:
        routing["lane_allow_mixed"] = False
    gating = decide_search_gating(query, routing)
    routing["domain_score"] = gating.domain_score
    routing["retrieval_mode"] = gating.retrieval_mode
    aclass = classify_answer_class(query)
    routing["answer_class"] = aclass.primary
    routing["answer_class_secondary"] = aclass.secondary

    should_search = routing.get("should_search")
    if should_search is None:
        should_search = routing.get("should_route")
    if gating.no_search:
        should_search = False
    if not should_search:
        return SearchResult(
            routing=routing,
            docs=[],
            consult_docs=[],
            retrieve_cache_status="off",
            should_search=False,
            no_search_message=gating.message,
            t_start=t_start,
            t_route=t_route,
            t_retrieve=t_route,
        )

    retrieve_cache_status = "off"
    filters = routing.get("filters") or routing.get("boost") or {}
    cache_key = None
    docs: List[Dict[str, Any]] = []
    if RETRIEVE_CACHE_ENABLED:
        cache_filters = dict(filters)
        cache_filters["_retrieval_mode"] = routing.get("retrieval_mode")
        cache_key = build_retrieval_cache_key(
            normalized_query=normalize_text(query),
            route=routing.get("route") or routing.get("ui_route") or "",
            db_route=routing.get("db_route") or "",
            filters=cache_filters,
            top_k=top_k,
        )
        cached = await retrieval_cache_get(cache_key)
        if cached:
            entries, backend = cached
            docs = docs_from_retrieve_cache(entries)
            retrieve_cache_status = f"hit({backend})" if docs else "miss"
        else:
            retrieve_cache_status = "miss"

    consult_docs: List[Dict[str, Any]] = []
    consult_task: Optional[asyncio.Task] = None
    if enable_consult_search and (routing.get("route") or routing.get("ui_route")) == "card_usage":
        if should_search_consult_cases(query, routing, session_state, commit=False):
            consult_task = asyncio.create_task(
                retrieve_consult_cases(query=query, routing=dict(routing), top_k=top_k)
            )
    if retrieve_cache_status not in ("hit(mem)", "hit(redis)"):
        allow_fallback = (routing.get("route") or routing.get("ui_route")) != "card_info"
        retrieve_stage = 0
        retrieve_start = time.perf_counter()
        route_name = routing.get("route") or routing.get("ui_route")
        effective_top_k = top_k
        if route_name == "card_usage":
            effective_top_k = min(effective_top_k, 2)
        if route_name == "card_info":
            docs = await retrieve_docs_card_info(
                query=query,
                routing=routing,
                top_k=effective_top_k,
                log_scores=LOG_RETRIEVER_DEBUG,
                budget_ms=RETRIEVE_BUDGET_MS,
                start_ts=retrieve_start,
            )
            retrieve_stage = 2
        else:
            docs = await retrieve_docs(query=query, routing=routing, top_k=effective_top_k)
            retrieve_stage = 1
        elapsed_ms = (time.perf_counter() - retrieve_start) * 1000
        budget_exceeded = elapsed_ms >= RETRIEVE_BUDGET_MS
        stage_exceeded = retrieve_stage >= RETRIEVE_MAX_STAGES
        if allow_fallback:
            if (not budget_exceeded) and (not stage_exceeded) and _retrieval_failed(docs, routing) and routing.get("retrieval_mode") != "hybrid":
                routing = dict(routing)
                routing["retrieval_mode"] = "hybrid"
                docs = await retrieve_docs(query=query, routing=routing, top_k=effective_top_k)
                retrieve_stage += 1
            elif (
                (not budget_exceeded)
                and (not stage_exceeded)
                and not docs
                and routing.get("domain_score", 0) >= 3
                and not routing.get("_lane_fallback_used")
            ):
                flipped = _flip_route_for_fallback(routing)
                docs = await retrieve_docs(query=query, routing=flipped, top_k=effective_top_k)
                if docs:
                    routing = flipped
                retrieve_stage += 1
        if RETRIEVE_CACHE_ENABLED and cache_key:
            entries = build_retrieve_cache_entries(docs)
            if entries:
                await retrieval_cache_set(cache_key, entries)
                if retrieve_cache_status == "off":
                    retrieve_cache_status = "miss"
    # ── 역색인 병합: 벡터 검색 결과에 역색인 문서 추가 (Stage 2) ──
    if KEYWORD_INDEX_ENABLED:
        try:
            index_docs = _try_keyword_index(query, routing, top_k=top_k)
            if index_docs:
                docs = _merge_index_and_vector_docs(index_docs, docs, top_k=top_k * 2)
                routing["_keyword_index_hits"] = len(index_docs)
        except Exception:
            pass  # 역색인 실패 시 기존 벡터 결과 유지

    # M-3: 키워드 인덱스 문서의 제목-쿼리 관련성 보정
    # 쿼리 핵심어가 제목에 없는 키워드 인덱스 문서는 score 감쇠
    _TITLE_CHECK_STOPWORDS = {"카드", "안내", "체크", "신용", "체크카드", "신용카드", "확인", "조회", "방법"}
    _q_tokens = [t for t in query.split() if len(t) >= 2 and t not in _TITLE_CHECK_STOPWORDS]
    for doc in docs:
        if not doc.get("_from_keyword_index"):
            continue
        title_lower = str(doc.get("title") or "").lower()
        # 쿼리 핵심 토큰 중 하나라도 제목에 포함되면 OK (범용어 제외)
        if _q_tokens and not any(t.lower() in title_lower for t in _q_tokens):
            doc["score"] = doc.get("score", 0.0) * 0.15  # 제목 무관 → MIN_RELEVANCE 이하로 감쇠

    # normalize docs ordering and remove noisy k-pass for loss/loan queries (cache-safe)
    def _is_kpass_doc(doc: Dict[str, Any]) -> bool:
        title = str(doc.get("title") or "").lower()
        content = str(doc.get("content") or "").lower()
        return "k패스" in title or "k-패스" in title or "k패스" in content or "k-패스" in content

    normalized_query = query.lower()
    if any(term in normalized_query for term in ("분실", "도난", "잃어버", "대출", "현금서비스", "카드대출", "리볼빙")):
        filtered_docs = [doc for doc in docs if not _is_kpass_doc(doc)]
        docs = filtered_docs or docs
    if (routing.get("route") or routing.get("ui_route")) == "card_usage":
        docs = post_filter_docs(query, docs)
    for doc in docs:
        if not isinstance(doc.get("score"), (int, float)):
            doc["score"] = 0.0
    docs.sort(key=lambda d: d.get("score", 0.0), reverse=True)
    # M-3: 최소 relevance 임계값 이하 문서 제거 (최소 1개 유지)
    if docs and MIN_RELEVANCE_THRESHOLD > 0:
        above = [d for d in docs if d.get("score", 0.0) >= MIN_RELEVANCE_THRESHOLD]
        docs = above if above else docs[:1]
    if consult_task:
        consult_docs = await consult_task
        if (routing.get("route") or routing.get("ui_route")) != "card_usage":
            consult_docs = []
        else:
            if session_state is not None:
                session_state["consult_last_search_at"] = time.time()
                session_state["consult_last_query"] = query

    # ── M-2 단계3: 상담 흐름 예측 ──
    flow_docs: List[Dict[str, Any]] = []
    if FLOW_PREDICTION_ENABLED and session_state is not None:
        try:
            from app.rag.flow.flow_tracker import update_flow, predict_next_docs
            update_flow(session_state, routing)
            flow_docs = predict_next_docs(session_state, top_k=2)
            if flow_docs:
                # 현재 결과와 중복 제거
                current_ids = {d.get("id") for d in docs}
                flow_docs = [d for d in flow_docs if d.get("id") not in current_ids]
                routing["_flow_prediction_count"] = len(flow_docs)
        except Exception:
            pass  # 흐름 예측 실패 시 기존 동작 유지

    t_retrieve = time.perf_counter()
    return SearchResult(
        routing=routing,
        docs=docs,
        consult_docs=consult_docs,
        retrieve_cache_status=retrieve_cache_status,
        should_search=True,
        no_search_message=None,
        t_start=t_start,
        t_route=t_route,
        t_retrieve=t_retrieve,
        flow_docs=flow_docs,
    )
