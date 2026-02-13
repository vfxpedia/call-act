"""Keyword-Document Inverted Index
=================================
서버 시작 시 keyword → document[] 매핑을 미리 빌드하여
첫 키워드 감지 즉시 문서 반환 (< 100ms, 벡터 검색 없이).

Data Sources:
  1. service_guide_documents.keywords[]  (이미 채워진 10+ 키워드)
  2. service_guide_documents.title       (제목 토큰화)
  3. service_guide_documents.metadata     (card_name 등)
  4. card_products.name                   (카드명 → 변형 확장)
  5. card_products.keywords[]             (채워진 경우)

Usage:
  from app.rag.cache.keyword_doc_index import build_index, lookup, lookup_combo

  build_index()                          # 서버 시작 시 1회
  docs = lookup("나라사랑카드")          # O(1) 조회
  docs = lookup_combo(["나라사랑", "분실"])  # 교집합 조회
"""

from __future__ import annotations

import logging
import os
import re
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

# ── Index Entry ──────────────────────────────────────────────────────

@dataclass(frozen=True, slots=True)
class IndexEntry:
    """역색인에 저장되는 문서 정보."""
    doc_id: str
    table: str          # "card_products" | "service_guide_documents"
    title: str
    relevance: float    # 0.0 ~ 1.0  (키워드 소스에 따른 가중치)
    category: str = ""  # 문서 카테고리 (optional)


# ── Global State ─────────────────────────────────────────────────────

_INDEX: Dict[str, List[IndexEntry]] = {}
_CARD_INDEX: Dict[str, List[IndexEntry]] = {}   # 카드명 전용 (변형 포함)
_BUILD_LOCK = threading.Lock()
_BUILT = False
_STATS: Dict[str, int] = {}


# ── Normalization ────────────────────────────────────────────────────

_WHITESPACE_RE = re.compile(r"\s+")
_STRIP_CHARS = ".,!?;:\"'()[]{}~`"


def _normalize(keyword: str) -> str:
    """키워드 정규화: 소문자, 공백 제거, 특수문자 제거."""
    kw = keyword.strip().strip(_STRIP_CHARS).lower()
    kw = _WHITESPACE_RE.sub("", kw)
    return kw


def _expand_card_variants(name: str) -> Set[str]:
    """카드명 변형 생성 (검색 매칭 확장).

    예: "K-패스 테디카드 체크" →
        full: "K-패스 테디카드 체크", "k-패스테디카드체크"
        sub:  "K-패스", "K패스", "테디카드", "체크"
        trim: "K-패스 테디카드" (체크/신용 제거)
    """
    variants = {name}
    lower = name.lower()
    variants.add(lower)
    # 공백 제거
    no_space = name.replace(" ", "")
    variants.add(no_space)
    variants.add(no_space.lower())
    # "카드" 제거
    for v in list(variants):
        if v.endswith("카드"):
            variants.add(v[:-2])
    # 하이픈 ↔ 없음
    if "-" in name:
        variants.add(name.replace("-", ""))
        variants.add(name.replace("-", " "))

    # 공백 기준 sub-token 분리 (2글자 이상만)
    tokens = name.split()
    for token in tokens:
        if len(token) >= 2 and token not in _CARD_SUB_STOPWORDS:
            variants.add(token)
            variants.add(token.lower())
            # 하이픈 변형
            if "-" in token:
                variants.add(token.replace("-", ""))

    # "체크", "신용", "(신용_체크)" 등 접미사 제거 → 핵심 카드명
    trimmed = _trim_card_suffix(name)
    if trimmed and trimmed != name:
        variants.add(trimmed)
        variants.add(trimmed.replace(" ", ""))

    return {_normalize(v) for v in variants if v.strip() and len(v.strip()) >= 2}


_CARD_SUB_STOPWORDS = {"테디카드", "테디", "카드", "체크", "신용", "법인", "결제전용", "신용카드"}
_CARD_SUFFIX_RE = re.compile(r"\s*(체크|신용|법인|결제전용|\(신용_체크\)|\(체크\))\s*$")


def _trim_card_suffix(name: str) -> str:
    """카드명에서 접미사(체크/신용 등) 제거."""
    trimmed = _CARD_SUFFIX_RE.sub("", name).strip()
    # "테디카드" 도 제거 (핵심 브랜드명만 추출)
    if trimmed.endswith("테디카드"):
        core = trimmed[:-4].strip()
        if core:
            return core
    return trimmed


# generic English terms (card_type, brand) - 낮은 relevance
_GENERIC_TERMS = {"local", "credit", "debit", "visa", "mastercard", "active", "inactive"}


# ── DB Connection (reuse from retriever.db) ──────────────────────────

def _db_config() -> Dict[str, object]:
    host = os.getenv("DB_HOST_IP") or os.getenv("DB_HOST")
    return {
        "host": host,
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "port": int(os.getenv("DB_PORT", "0")) or None,
    }


def _connect():
    import psycopg2
    return psycopg2.connect(connect_timeout=5, **_db_config())


# ── Index Building ───────────────────────────────────────────────────

def _add_entry(index: Dict[str, List[IndexEntry]], keyword: str, entry: IndexEntry) -> None:
    """정규화된 키워드로 역색인에 추가 (중복 doc_id 방지)."""
    nk = _normalize(keyword)
    if not nk or len(nk) < 2:
        return
    bucket = index.setdefault(nk, [])
    # 동일 doc_id가 이미 있으면 relevance가 높은 쪽 유지
    for i, existing in enumerate(bucket):
        if existing.doc_id == entry.doc_id:
            if entry.relevance > existing.relevance:
                bucket[i] = entry
            return
    bucket.append(entry)


def _build_from_service_guides(conn, index: Dict[str, List[IndexEntry]]) -> int:
    """service_guide_documents의 keywords[], title, metadata에서 역색인 빌드."""
    sql = """
        SELECT id, title, category, keywords, metadata
        FROM service_guide_documents
        WHERE id IS NOT NULL
    """
    count = 0
    with conn.cursor() as cur:
        cur.execute(sql)
        for row in cur.fetchall():
            doc_id, title, category, keywords, metadata = row
            if not doc_id:
                continue
            meta = metadata if isinstance(metadata, dict) else {}
            doc_title = title or meta.get("title", "")
            doc_category = category or meta.get("category", "")

            entry_high = IndexEntry(
                doc_id=str(doc_id),
                table="service_guide_documents",
                title=doc_title,
                relevance=1.0,
                category=doc_category,
            )
            entry_mid = IndexEntry(
                doc_id=str(doc_id),
                table="service_guide_documents",
                title=doc_title,
                relevance=0.7,
                category=doc_category,
            )
            entry_low = IndexEntry(
                doc_id=str(doc_id),
                table="service_guide_documents",
                title=doc_title,
                relevance=0.5,
                category=doc_category,
            )

            # 1) keywords 배열 (가장 높은 relevance)
            if keywords and isinstance(keywords, list):
                for kw in keywords:
                    if kw and isinstance(kw, str):
                        _add_entry(index, kw, entry_high)
                        count += 1

            # 2) 제목에서 키워드 추출 (중간 relevance)
            #    제목 전체도 인덱싱 (복합어 매칭: "카드분실_도난" → "분실도난")
            if doc_title:
                title_tokens = _tokenize_title(doc_title)
                for token in title_tokens:
                    _add_entry(index, token, entry_mid)
                    count += 1
                # 제목 전체 (언더스코어/공백 제거)
                full_title_norm = _normalize(doc_title)
                if len(full_title_norm) >= 3:
                    _add_entry(index, full_title_norm, entry_mid)
                    count += 1

            # 3) metadata.card_name 연결 (높은 relevance - 카드별 가이드)
            card_name = meta.get("card_name", "")
            if card_name:
                _add_entry(index, card_name, entry_high)
                count += 1

            # 4) metadata에서 추가 키워드 (intent 등)
            for meta_key in ("intent", "category1", "category2"):
                meta_val = meta.get(meta_key, "")
                if meta_val and isinstance(meta_val, str):
                    _add_entry(index, meta_val, entry_low)
                    count += 1

    return count


def _build_from_card_products(conn, index: Dict[str, List[IndexEntry]], card_index: Dict[str, List[IndexEntry]]) -> int:
    """card_products의 name, keywords, main_benefits에서 역색인 빌드."""
    sql = """
        SELECT id, name, card_type, brand, keywords, main_benefits, metadata
        FROM card_products
        WHERE id IS NOT NULL AND name IS NOT NULL
    """
    count = 0
    with conn.cursor() as cur:
        cur.execute(sql)
        for row in cur.fetchall():
            doc_id, name, card_type, brand, keywords, main_benefits, metadata = row
            if not doc_id or not name:
                continue
            meta = metadata if isinstance(metadata, dict) else {}

            entry = IndexEntry(
                doc_id=str(doc_id),
                table="card_products",
                title=name,
                relevance=1.0,
                category=card_type or "",
            )
            entry_mid = IndexEntry(
                doc_id=str(doc_id),
                table="card_products",
                title=name,
                relevance=0.6,
                category=card_type or "",
            )

            # 1) 카드명 + 변형 (최고 relevance, 카드 전용 인덱스에도 추가)
            variants = _expand_card_variants(name)
            for v in variants:
                _add_entry(index, v, entry)
                _add_entry(card_index, v, entry)
                count += 1

            # 2) keywords 배열 (채워져 있으면)
            if keywords and isinstance(keywords, list):
                for kw in keywords:
                    if kw and isinstance(kw, str):
                        _add_entry(index, kw, entry)
                        count += 1

            # 3) brand (visa, mastercard 등) - generic 제외
            if brand and _normalize(brand) not in _GENERIC_TERMS:
                _add_entry(index, brand, entry_mid)
                count += 1

            # 4) card_type (credit, check 등) - generic 제외
            if card_type and _normalize(card_type) not in _GENERIC_TERMS:
                _add_entry(index, card_type, entry_mid)
                count += 1

            # 5) main_benefits에서 핵심 토큰 추출
            if main_benefits and isinstance(main_benefits, str):
                benefit_tokens = _extract_benefit_keywords(main_benefits)
                for token in benefit_tokens:
                    _add_entry(index, token, entry_mid)
                    count += 1

    return count


# ── Tokenization Helpers ─────────────────────────────────────────────

_TITLE_SPLIT_RE = re.compile(r"[_/\-\s·]+")
_TITLE_STOPWORDS = {"안내", "관련", "관한", "방법", "사항", "이용", "서비스", "기타", "merged", "일반"}

# 복합어 분리 맵 (도메인 특화): "분실도난" → ["분실", "도난"]
_COMPOUND_SPLIT = {
    "분실도난": ["분실", "도난"],
    "도난분실": ["도난", "분실"],
    "한도상향": ["한도", "상향"],
    "한도증액": ["한도", "증액"],
    "결제승인": ["결제", "승인"],
    "승인취소": ["승인", "취소"],
    "매출취소": ["매출", "취소"],
    "선결제": ["선결제", "즉시출금"],
    "즉시출금": ["즉시출금", "선결제"],
    "연체대금": ["연체", "대금"],
    "재발급": ["재발급"],
    "해외결제": ["해외", "결제"],
    "소득공제": ["소득공제"],
    "일부결제대금이월약정": ["리볼빙"],
    "오토할부": ["오토할부"],
    "오토캐쉬백": ["오토캐쉬백"],
    "간편페이": ["간편페이", "페이"],
    "애플페이": ["애플페이", "apple pay"],
    "삼성페이": ["삼성페이"],
    "카카오페이": ["카카오페이"],
    "네이버페이": ["네이버페이"],
    "안심클릭": ["안심클릭"],
}


def _tokenize_title(title: str) -> List[str]:
    """제목을 의미 있는 토큰으로 분리. 복합어도 분해."""
    tokens = _TITLE_SPLIT_RE.split(title)
    result = []
    for t in tokens:
        t = t.strip()
        if len(t) >= 2 and t.lower() not in _TITLE_STOPWORDS:
            result.append(t)
            # 복합어 분리
            tn = _normalize(t)
            if tn in _COMPOUND_SPLIT:
                result.extend(_COMPOUND_SPLIT[tn])
    return result


_BENEFIT_KEYWORDS_RE = re.compile(
    r"(할인|적립|캐시백|무이자|포인트|마일리지|바우처|라운지|주유|교통|통신|"
    r"배달|쇼핑|영화|스트리밍|해외|면세|편의점|커피|음식|병원|학원|"
    r"보험|여행|항공|호텔|렌터카|골프|자동차|ETC|하이패스)"
)


def _extract_benefit_keywords(text: str) -> List[str]:
    """main_benefits 텍스트에서 핵심 혜택 키워드 추출."""
    return list(set(_BENEFIT_KEYWORDS_RE.findall(text)))


# ── Public API ───────────────────────────────────────────────────────

def build_index() -> Dict[str, int]:
    """DB에서 전체 문서를 읽어 역색인 빌드. 서버 시작 시 1회 호출.

    Returns:
        stats dict: {"guide_entries": N, "card_entries": N, "unique_keywords": N, "build_ms": N}
    """
    global _INDEX, _CARD_INDEX, _BUILT, _STATS

    with _BUILD_LOCK:
        if _BUILT:
            return _STATS

        t0 = time.time()
        new_index: Dict[str, List[IndexEntry]] = {}
        new_card_index: Dict[str, List[IndexEntry]] = {}

        try:
            conn = _connect()
        except Exception as e:
            logger.error("keyword_doc_index: DB 연결 실패 - %s", e)
            return {"error": str(e)}

        try:
            guide_count = _build_from_service_guides(conn, new_index)
            card_count = _build_from_card_products(conn, new_index, new_card_index)
        except Exception as e:
            logger.error("keyword_doc_index: 빌드 실패 - %s", e)
            return {"error": str(e)}
        finally:
            conn.close()

        # 각 버킷을 relevance 내림차순 정렬
        for bucket in new_index.values():
            bucket.sort(key=lambda e: -e.relevance)
        for bucket in new_card_index.values():
            bucket.sort(key=lambda e: -e.relevance)

        _INDEX = new_index
        _CARD_INDEX = new_card_index
        _BUILT = True

        elapsed_ms = int((time.time() - t0) * 1000)
        _STATS = {
            "guide_entries": guide_count,
            "card_entries": card_count,
            "unique_keywords": len(new_index),
            "card_keywords": len(new_card_index),
            "build_ms": elapsed_ms,
        }
        logger.info(
            "keyword_doc_index: 빌드 완료 - 키워드 %d개, 카드키워드 %d개, "
            "가이드 %d건, 카드 %d건, %dms",
            len(new_index), len(new_card_index),
            guide_count, card_count, elapsed_ms,
        )
        return _STATS


def _lookup_direct(nk: str, top_k: int) -> List[IndexEntry]:
    """정규화된 키워드로 인덱스 직접 조회 (재귀 없음)."""
    return _INDEX.get(nk, [])[:top_k]


def lookup(keyword: str, top_k: int = 10) -> List[IndexEntry]:
    """단일 키워드로 문서 조회. O(1) dict lookup.

    직접 매칭 실패 시 복합어 분리를 시도합니다.
    예: "분실도난" → "분실" + "도난" combo lookup

    Args:
        keyword: 검색 키워드 (정규화 자동 적용)
        top_k: 반환할 최대 문서 수

    Returns:
        relevance 내림차순 정렬된 IndexEntry 리스트
    """
    nk = _normalize(keyword)
    if not nk:
        return []
    # 직접 매칭
    entries = _INDEX.get(nk, [])
    if entries:
        return entries[:top_k]
    # 복합어 분리 fallback (자기 자신 제외)
    parts = _COMPOUND_SPLIT.get(nk)
    if parts:
        distinct = [p for p in parts if _normalize(p) != nk]
        if len(distinct) >= 1:
            return lookup_combo(distinct, top_k=top_k)
    return []


def lookup_card(keyword: str, top_k: int = 10) -> List[IndexEntry]:
    """카드명 전용 조회 (변형 포함)."""
    nk = _normalize(keyword)
    if not nk:
        return []
    entries = _CARD_INDEX.get(nk, [])
    return entries[:top_k]


def lookup_combo(keywords: List[str], top_k: int = 10) -> List[IndexEntry]:
    """복수 키워드 조합 조회 - 교집합 우선, 없으면 합집합.

    예: ["나라사랑", "분실"] → 두 키워드 모두 포함된 문서 우선 반환.

    Args:
        keywords: 키워드 리스트
        top_k: 반환할 최대 문서 수

    Returns:
        교집합 우선 → 합집합 fallback, relevance 내림차순
    """
    if not keywords:
        return []

    # 각 키워드별 문서 집합 수집 (직접 조회로 재귀 방지)
    keyword_doc_sets: List[Dict[str, IndexEntry]] = []
    for kw in keywords:
        nk = _normalize(kw)
        entries = _lookup_direct(nk, top_k=100)
        doc_map = {e.doc_id: e for e in entries}
        keyword_doc_sets.append(doc_map)

    if not keyword_doc_sets:
        return []

    # 교집합: 모든 키워드에 매칭되는 문서
    common_ids = set(keyword_doc_sets[0].keys())
    for doc_map in keyword_doc_sets[1:]:
        common_ids &= set(doc_map.keys())

    if common_ids:
        # 교집합 문서: relevance 합산
        results = []
        for doc_id in common_ids:
            # 가장 높은 relevance entry를 대표로, 합산 점수 부여
            best_entry = None
            total_rel = 0.0
            for doc_map in keyword_doc_sets:
                entry = doc_map.get(doc_id)
                if entry:
                    total_rel += entry.relevance
                    if best_entry is None or entry.relevance > best_entry.relevance:
                        best_entry = entry
            if best_entry:
                # 새 entry에 합산 relevance 반영 (최대 1.0으로 clip)
                boosted = IndexEntry(
                    doc_id=best_entry.doc_id,
                    table=best_entry.table,
                    title=best_entry.title,
                    relevance=min(total_rel / len(keywords), 1.0),
                    category=best_entry.category,
                )
                results.append(boosted)
        results.sort(key=lambda e: -e.relevance)
        return results[:top_k]

    # 교집합 없으면 합집합 (각 키워드별 top 결과 merge)
    seen: Set[str] = set()
    merged: List[IndexEntry] = []
    for doc_map in keyword_doc_sets:
        for entry in sorted(doc_map.values(), key=lambda e: -e.relevance):
            if entry.doc_id not in seen:
                seen.add(entry.doc_id)
                merged.append(entry)
    merged.sort(key=lambda e: -e.relevance)
    return merged[:top_k]


def is_built() -> bool:
    """인덱스가 빌드되었는지 확인."""
    return _BUILT


def get_stats() -> Dict[str, int]:
    """빌드 통계 반환."""
    return dict(_STATS)


def get_index_size() -> int:
    """인덱스에 등록된 고유 키워드 수."""
    return len(_INDEX)


def rebuild_index() -> Dict[str, int]:
    """인덱스 강제 재빌드 (카드 상품 업데이트 후 등)."""
    global _BUILT
    _BUILT = False
    return build_index()
