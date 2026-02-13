"""상담 흐름 추적 및 다음 문서 예측.

세션 상태에 흐름 정보를 저장하고, 다음 예상 문서를 반환합니다.
키워드 인덱스(F-1)를 활용하여 추가 벡터 검색 없이 <1ms로 예측합니다.

Usage:
    from app.rag.flow.flow_tracker import update_flow, predict_next_docs
    update_flow(session_state, routing)
    next_docs = predict_next_docs(session_state, top_k=2)
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from app.rag.flow.flow_model import (
    Transition,
    detect_category,
    get_search_keywords,
    predict_next_categories,
)

_logger = logging.getLogger(__name__)

# 흐름 예측 결과에 부여하는 기본 score (벡터 검색 결과보다 낮게)
_FLOW_PREDICTION_SCORE = 0.35


def _extract_actions_from_routing(routing: Dict[str, Any]) -> tuple:
    """라우팅 정보에서 actions, weak_intents 추출."""
    matched = routing.get("matched") or {}
    filters = routing.get("filters") or routing.get("boost") or {}

    actions = (
        matched.get("actions")
        or filters.get("intent")
        or []
    )
    weak_intents = (
        matched.get("weak_intents")
        or filters.get("weak_intent")
        or []
    )
    return list(actions), list(weak_intents)


def update_flow(
    session_state: Optional[Dict[str, Any]],
    routing: Dict[str, Any],
) -> Optional[str]:
    """현재 턴의 흐름 상태를 세션에 업데이트.

    Returns:
        감지된 category_raw (없으면 None)
    """
    if session_state is None:
        return None

    actions, weak_intents = _extract_actions_from_routing(routing)
    category = detect_category(actions, weak_intents)

    if not category:
        return None

    # 흐름 상태 초기화 (첫 턴)
    if "flow_visited" not in session_state:
        session_state["flow_visited"] = set()
        session_state["flow_history"] = []

    # 현재 카테고리 기록
    visited: set = session_state["flow_visited"]
    history: list = session_state["flow_history"]

    if category not in visited:
        visited.add(category)
        history.append(category)

    session_state["flow_current_category"] = category

    _logger.debug(
        "flow_tracker: category=%s, visited=%s, history=%s",
        category, visited, history,
    )
    return category


def predict_next_docs(
    session_state: Optional[Dict[str, Any]],
    top_k: int = 2,
) -> List[Dict[str, Any]]:
    """현재 흐름 상태에서 다음 예상 문서를 반환.

    키워드 인덱스를 활용하여 <1ms로 예측 문서를 조회합니다.

    Returns:
        예측 문서 리스트 (빈 리스트 = 예측 없음)
    """
    if not session_state:
        return []

    current_category = session_state.get("flow_current_category")
    if not current_category:
        return []

    visited = session_state.get("flow_visited") or set()

    # 전이 확률에 기반한 다음 카테고리 예측
    predictions = predict_next_categories(
        current_category, visited, max_predictions=top_k,
    )
    if not predictions:
        return []

    # 키워드 인덱스에서 예측 문서 조회
    predicted_docs: List[Dict[str, Any]] = []
    for pred in predictions:
        docs = _fetch_docs_for_prediction(pred)
        predicted_docs.extend(docs)
        if len(predicted_docs) >= top_k:
            break

    # 최대 top_k개만 반환
    result = predicted_docs[:top_k]

    if result:
        categories = [p.next_category for p in predictions[:len(result)]]
        _logger.debug(
            "flow_predict: current=%s → predicted=%s, docs=%d",
            current_category, categories, len(result),
        )
        # 세션에 예측 기록 (프론트엔드에서 활용 가능)
        session_state["flow_predictions"] = [
            {"category": p.next_category, "query": p.search_query}
            for p in predictions[:len(result)]
        ]

    return result


def _fetch_docs_for_prediction(pred: Transition) -> List[Dict[str, Any]]:
    """예측 전이에 대한 문서를 키워드 인덱스에서 조회."""
    keywords = get_search_keywords(pred.next_category)
    if not keywords:
        # 키워드 매핑이 없으면 search_query에서 추출
        keywords = [w for w in pred.search_query.split() if len(w) >= 2]

    if not keywords:
        return []

    # F-1 키워드 인덱스 조회 시도
    try:
        from app.rag.cache.keyword_doc_index import lookup, lookup_combo, is_built
        if not is_built():
            return _fallback_vector_search(pred)
    except ImportError:
        return _fallback_vector_search(pred)

    t0 = time.perf_counter()

    if len(keywords) >= 2:
        entries = lookup_combo(keywords, top_k=3)
    else:
        entries = lookup(keywords[0], top_k=3)

    if not entries:
        return _fallback_vector_search(pred)

    # 제목 관련성 필터: 키워드가 제목에 포함된 문서만 선택
    filtered = [
        e for e in entries
        if any(kw in (e.title or "").lower() for kw in keywords)
    ]
    if not filtered:
        return _fallback_vector_search(pred)
    entries = filtered

    # IndexEntry → 문서 dict 변환
    from app.rag.retriever.db import fetch_docs_by_ids
    from collections import defaultdict

    by_table: Dict[str, List] = defaultdict(list)
    entry_map: Dict[str, Any] = {}
    for entry in entries[:3]:
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
            doc["score"] = _FLOW_PREDICTION_SCORE
            doc["_from_flow_prediction"] = True
            doc["_predicted_category"] = pred.next_category
            doc["_prediction_query"] = pred.search_query
            docs.append(doc)

    elapsed_ms = (time.perf_counter() - t0) * 1000
    _logger.debug(
        "flow_fetch: category=%s, keywords=%s, docs=%d, %.1fms",
        pred.next_category, keywords, len(docs), elapsed_ms,
    )

    return docs[:1]  # 예측당 1개 문서


def _fallback_vector_search(pred: Transition) -> List[Dict[str, Any]]:
    """키워드 인덱스 사용 불가 시 벡터 검색 fallback."""
    try:
        from app.rag.retriever.db import vector_search
        keywords = get_search_keywords(pred.next_category) or pred.search_query.split()
        rows = vector_search(
            query=pred.search_query,
            table="service_guide_documents",
            limit=3,
            filters=None,
        )
        docs = []
        for row in rows:
            doc_id, content, metadata, structured, score = row
            meta = metadata if isinstance(metadata, dict) else {}
            title = meta.get("title") or meta.get("name") or ""
            # 관련성 필터: score > 0.5 또는 제목에 키워드 포함
            title_lower = title.lower()
            has_keyword = any(kw in title_lower for kw in keywords if len(kw) >= 2)
            if score < 0.5 and not has_keyword:
                continue
            docs.append({
                "id": doc_id,
                "content": content or "",
                "metadata": meta,
                "structured": structured,
                "score": _FLOW_PREDICTION_SCORE,
                "title": title,
                "_from_flow_prediction": True,
                "_predicted_category": pred.next_category,
                "_prediction_query": pred.search_query,
            })
        return docs[:1]
    except Exception:
        return []
