"""상담 흐름 전이 모델.

6,533건 하나카드 상담 데이터에서 추출한 통화 내(intra-call) 카테고리 전이 패턴.
488건(7.5%)의 다중 카테고리 통화에서 83개 전이 쌍 발견.

Usage:
    from app.rag.flow.flow_model import detect_category, predict_next_categories
    cat = detect_category(actions=["분실"], weak_intents=[])
    nexts = predict_next_categories(cat, visited=set())
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Optional, Set, Tuple


# ────────────────────────────────────────────────────
# 1. 액션 → category_raw 매핑
# ────────────────────────────────────────────────────

# actions/weak_intents 키워드가 어떤 상담 카테고리에 해당하는지
# (키워드는 keyword_extractor.py의 출력)
_ACTION_TO_CATEGORY: Dict[FrozenSet[str], str] = {
    frozenset(["분실"]): "분실/도난 신청/해제",
    frozenset(["도난"]): "분실/도난 신청/해제",
    frozenset(["분실도난"]): "분실/도난 신청/해제",
    frozenset(["재발급"]): "카드재발급",
    frozenset(["한도"]): "한도 안내",
    frozenset(["한도", "상향"]): "한도상향 접수/처리",
    frozenset(["한도", "증액"]): "한도상향 접수/처리",
    frozenset(["결제"]): "결제대금 안내",
    frozenset(["선결제"]): "선결제/즉시출금",
    frozenset(["즉시출금"]): "선결제/즉시출금",
    frozenset(["이용내역"]): "이용내역 안내",
    frozenset(["이용내역", "조회"]): "이용내역 안내",
    frozenset(["취소"]): "승인취소/매출취소 안내",
    frozenset(["승인", "취소"]): "승인취소/매출취소 안내",
    frozenset(["매출", "취소"]): "승인취소/매출취소 안내",
    frozenset(["결제일"]): "결제일 안내/변경/취소",
    frozenset(["결제일", "변경"]): "결제일 안내/변경/취소",
    frozenset(["결제", "계좌"]): "결제계좌 안내/변경",
    frozenset(["연체"]): "연체대금 안내",
    frozenset(["연회비"]): "연회비 안내",
    frozenset(["포인트"]): "포인트/마일리지 안내",
    frozenset(["마일리지"]): "포인트/마일리지 안내",
    frozenset(["이벤트"]): "이벤트 안내",
    frozenset(["해지"]): "일부결제대금이월약정 해지",
    frozenset(["리볼빙"]): "일부결제대금이월약정 해지",
    frozenset(["리볼빙", "해지"]): "일부결제대금이월약정 해지",
    frozenset(["가상계좌"]): "가상계좌 안내",
    frozenset(["배송"]): "긴급 배송 신청",
    frozenset(["긴급", "배송"]): "긴급 배송 신청",
    frozenset(["대출"]): "단기카드대출 안내/실행",
    frozenset(["카드대출"]): "단기카드대출 안내/실행",
    frozenset(["현금서비스"]): "단기카드대출 안내/실행",
    frozenset(["바우처"]): "정부지원 바우처 (등유, 임신 등)",
    frozenset(["정부지원"]): "정부지원 바우처 (등유, 임신 등)",
    frozenset(["오토할부"]): "오토할부/오토캐쉬백 안내/신청/취소",
    frozenset(["심사"]): "심사 진행사항 안내",
}

# 단일 키워드 → category (빠른 조회용)
_SINGLE_ACTION_MAP: Dict[str, str] = {}
for keys, cat in _ACTION_TO_CATEGORY.items():
    if len(keys) == 1:
        _SINGLE_ACTION_MAP[next(iter(keys))] = cat


# ────────────────────────────────────────────────────
# 2. 통화 내 카테고리 전이 확률
# ────────────────────────────────────────────────────

@dataclass(frozen=True)
class Transition:
    next_category: str
    count: int         # 관찰 빈도
    search_query: str  # 예측 문서 검색에 사용할 대표 쿼리


# 통화 내 전이 데이터 (6,533건 분석, 빈도 3건 이상만)
_INTRA_CALL_TRANSITIONS: Dict[str, List[Transition]] = {
    "이용내역 안내": [
        Transition("포인트/마일리지 안내", 41, "포인트 조회 적립"),
        Transition("결제대금 안내", 38, "결제 대금 안내"),
    ],
    "선결제/즉시출금": [
        Transition("한도 안내", 26, "카드 한도 조회"),
        Transition("이용내역 안내", 20, "이용내역 조회"),
        Transition("결제일 안내/변경/취소", 16, "결제일 변경"),
    ],
    "분실/도난 신청/해제": [
        Transition("긴급 배송 신청", 16, "카드 긴급 배송 신청"),
        Transition("카드재발급", 7, "카드 재발급 방법"),
    ],
    "한도상향 접수/처리": [
        Transition("결제대금 안내", 15, "결제 대금 안내"),
        Transition("한도 안내", 7, "카드 한도 조회"),
    ],
    "정부지원 바우처 (등유, 임신 등)": [
        Transition("이용방법 안내", 14, "바우처 이용방법"),
    ],
    "승인취소/매출취소 안내": [
        Transition("결제일 안내/변경/취소", 14, "결제일 안내"),
        Transition("이용내역 안내", 8, "이용내역 조회"),
        Transition("한도 안내", 6, "카드 한도 조회"),
    ],
    "이용방법 안내": [
        Transition("서비스 이용방법 안내", 10, "서비스 이용방법"),
    ],
    "결제대금 안내": [
        Transition("한도 안내", 10, "카드 한도 조회"),
        Transition("결제일 안내/변경/취소", 7, "결제일 변경 안내"),
        Transition("이용내역 안내", 6, "이용내역 조회"),
    ],
    "가상계좌 안내": [
        Transition("한도 안내", 9, "카드 한도 조회"),
        Transition("이용내역 안내", 6, "이용내역 조회"),
    ],
    "가상계좌 예약/취소": [
        Transition("결제일 안내/변경/취소", 8, "결제일 안내"),
        Transition("이용내역 안내", 6, "이용내역 조회"),
    ],
    "결제계좌 안내/변경": [
        Transition("한도 안내", 7, "카드 한도 조회"),
        Transition("결제일 안내/변경/취소", 5, "결제일 변경"),
    ],
    "한도 안내": [
        Transition("한도상향 접수/처리", 7, "한도 상향 신청"),
    ],
    "이벤트 안내": [
        Transition("포인트/마일리지 전환등록", 7, "포인트 전환 등록"),
    ],
    "장기카드대출 안내": [
        Transition("이용방법 안내", 5, "카드대출 이용방법"),
    ],
    "카드재발급": [
        Transition("배송 조회", 5, "카드 배송 조회"),
    ],
    "연체대금 안내": [
        Transition("결제대금 안내", 4, "결제 대금 안내"),
    ],
    "포인트/마일리지 안내": [
        Transition("이벤트 안내", 4, "카드 이벤트"),
    ],
}

# 고객별 연속 상담(inter-session) 전이도 참고용으로 포함
# (같은 고객이 다음 전화에서 물어볼 가능성 높은 주제)
_INTER_SESSION_HINTS: Dict[str, List[str]] = {
    "이용내역 안내": ["선결제/즉시출금", "분실/도난 신청/해제"],
    "선결제/즉시출금": ["이용내역 안내", "한도상향 접수/처리"],
    "분실/도난 신청/해제": ["이용내역 안내", "선결제/즉시출금"],
    "한도상향 접수/처리": ["선결제/즉시출금", "이용내역 안내"],
}


# ────────────────────────────────────────────────────
# 3. 카테고리 → 키워드 인덱스 검색 키워드
# ────────────────────────────────────────────────────

# flow_tracker에서 키워드 인덱스 조회 시 사용
CATEGORY_SEARCH_KEYWORDS: Dict[str, List[str]] = {
    "분실/도난 신청/해제": ["분실", "도난", "신고"],
    "카드재발급": ["재발급", "카드"],
    "긴급 배송 신청": ["배송", "긴급"],
    "배송 조회": ["배송", "조회"],
    "한도상향 접수/처리": ["한도", "상향"],
    "한도 안내": ["한도", "조회"],
    "결제대금 안내": ["결제", "대금"],
    "결제일 안내/변경/취소": ["결제일", "변경"],
    "결제계좌 안내/변경": ["결제", "계좌"],
    "이용내역 안내": ["이용내역", "조회"],
    "승인취소/매출취소 안내": ["승인", "취소"],
    "이벤트 안내": ["이벤트"],
    "포인트/마일리지 안내": ["포인트", "적립"],
    "포인트/마일리지 전환등록": ["포인트", "전환"],
    "연체대금 안내": ["연체"],
    "연회비 안내": ["연회비"],
    "일부결제대금이월약정 해지": ["리볼빙", "해지"],
    "가상계좌 안내": ["가상계좌"],
    "가상계좌 예약/취소": ["가상계좌", "예약"],
    "단기카드대출 안내/실행": ["카드대출", "단기"],
    "이용방법 안내": ["이용방법"],
    "서비스 이용방법 안내": ["서비스", "이용방법"],
    "정부지원 바우처 (등유, 임신 등)": ["바우처", "정부지원"],
    "심사 진행사항 안내": ["심사", "진행"],
    "오토할부/오토캐쉬백 안내/신청/취소": ["오토할부"],
}


# ────────────────────────────────────────────────────
# 4. 공개 함수
# ────────────────────────────────────────────────────

def detect_category(
    actions: List[str],
    weak_intents: List[str],
) -> Optional[str]:
    """추출된 액션/약의도에서 category_raw를 판별."""
    all_terms = [*actions, *weak_intents]
    if not all_terms:
        return None

    # 복합 키워드 우선 (더 구체적)
    term_set = frozenset(t.lower().replace(" ", "") for t in all_terms if t)
    best_match: Optional[str] = None
    best_len = 0
    for keys, cat in _ACTION_TO_CATEGORY.items():
        if keys.issubset(term_set) and len(keys) > best_len:
            best_match = cat
            best_len = len(keys)
    if best_match:
        return best_match

    # 단일 키워드 fallback
    for term in all_terms:
        normalized = term.lower().replace(" ", "")
        cat = _SINGLE_ACTION_MAP.get(normalized)
        if cat:
            return cat

    return None


def predict_next_categories(
    current_category: str,
    visited: Set[str],
    max_predictions: int = 2,
) -> List[Transition]:
    """현재 카테고리에서 다음 예상 카테고리를 반환.

    Args:
        current_category: 현재 감지된 카테고리
        visited: 이미 이 통화에서 다룬 카테고리 집합
        max_predictions: 반환할 최대 예측 수

    Returns:
        Transition 리스트 (빈도순, 이미 방문한 카테고리 제외)
    """
    transitions = _INTRA_CALL_TRANSITIONS.get(current_category, [])
    predictions = []
    for t in transitions:
        if t.next_category not in visited and t.next_category != current_category:
            predictions.append(t)
            if len(predictions) >= max_predictions:
                break
    return predictions


def get_search_keywords(category: str) -> List[str]:
    """카테고리에 대한 검색 키워드 반환."""
    return CATEGORY_SEARCH_KEYWORDS.get(category, [])
