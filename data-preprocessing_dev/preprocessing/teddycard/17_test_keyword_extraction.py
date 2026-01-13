"""
키워드 추출 테스트 스크립트

개선된 키워드 추출 로직의 정확도를 테스트합니다.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

# 설정 파일 로드
from config import SCRIPT_DIR

# 파일 경로
KEYWORD_DICT_FILE = SCRIPT_DIR / "keywords_dict_v2_with_patterns.json"

# 테스트 케이스
TEST_CASES = [
    {
        "name": "동의어 정규화",
        "text": "카드를 잃어버렸어요",
        "expected_keywords": ["분실"],
        "expected_priority": 10
    },
    {
        "name": "복합 키워드 우선 처리",
        "text": "해외에서 카드 분실했어요",
        "expected_keywords": ["해외", "카드", "분실"],
        "expected_priority": 10
    },
    {
        "name": "변형 표현 인식",
        "text": "카드를 분실했어요",
        "expected_keywords": ["분실"],
        "expected_priority": 10
    },
    {
        "name": "맥락 기반 카테고리 선택",
        "text": "도난 카드로 결제가 거부되었어요",
        "expected_keywords": ["도난", "카드", "결제"],
        "expected_category": "결제"
    },
    {
        "name": "우선순위 정렬",
        "text": "일본 여행 중 카드 분실했어요",
        "expected_keywords": ["해외", "카드", "분실"],
        "expected_priority_order": ["분실", "해외", "카드"]
    }
]


def load_keyword_dict() -> Dict:
    """키워드 사전 로드"""
    if not KEYWORD_DICT_FILE.exists():
        print(f"[ERROR] 키워드 사전 파일이 없습니다: {KEYWORD_DICT_FILE}")
        return {}
    
    with open(KEYWORD_DICT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def normalize_keyword(keyword: str, keyword_dict: Dict) -> Optional[str]:
    """
    동의어를 표준 키워드로 정규화
    
    Args:
        keyword: 후보 키워드
        keyword_dict: 키워드 사전
    
    Returns:
        표준 키워드 또는 None
    """
    keywords = keyword_dict.get("keywords", {})
    
    # 1. 직접 매칭
    if keyword in keywords:
        return keyword
    
    # 2. 동의어 검색
    for canonical, data in keywords.items():
        if keyword in data.get("synonyms", []):
            return canonical
        if keyword in data.get("variations", []):
            return canonical
    
    return None


def extract_compound_keywords(text: str, keyword_dict: Dict) -> List[Dict]:
    """
    복합 키워드 추출
    
    Args:
        text: 텍스트
        keyword_dict: 키워드 사전
    
    Returns:
        복합 키워드 리스트
    """
    keywords = keyword_dict.get("keywords", {})
    found_keywords = []
    
    # 모든 복합 패턴 수집
    all_patterns = []
    for canonical, data in keywords.items():
        for pattern_info in data.get("compound_patterns", []):
            all_patterns.append({
                **pattern_info,
                "canonical": canonical
            })
    
    # 패턴을 길이 순으로 정렬 (긴 것부터)
    all_patterns.sort(key=lambda x: len(x["pattern"]), reverse=True)
    
    matched_positions = set()
    
    for pattern_info in all_patterns:
        pattern = pattern_info["pattern"]
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        for match in matches:
            start, end = match.span()
            
            # 이미 매칭된 위치와 겹치지 않는지 확인
            if not any(start <= pos < end for pos in matched_positions):
                found_keywords.append({
                    "keyword": match.group(),
                    "canonical": pattern_info["canonical"],
                    "category": pattern_info["category"],
                    "priority": pattern_info["priority"],
                    "position": (start, end)
                })
                matched_positions.update(range(start, end))
    
    # 우선순위 정렬
    found_keywords.sort(key=lambda x: x["priority"], reverse=True)
    
    return found_keywords


def extract_keywords(text: str, keyword_dict: Dict) -> List[Dict]:
    """
    키워드 추출 (통합)
    
    Args:
        text: 텍스트
        keyword_dict: 키워드 사전
    
    Returns:
        키워드 리스트
    """
    keywords = keyword_dict.get("keywords", {})
    found_keywords = []
    
    # 1. 복합 키워드 우선 추출
    compounds = extract_compound_keywords(text, keyword_dict)
    found_keywords.extend(compounds)
    
    # 2. 단일 키워드 추출 (복합 키워드 제외)
    matched_positions = set()
    for compound in compounds:
        start, end = compound["position"]
        matched_positions.update(range(start, end))
    
    text_lower = text.lower()
    for keyword, data in keywords.items():
        # 복합 키워드에 포함된 키워드는 스킵
        if keyword in [c["canonical"] for c in compounds]:
            continue
        
        # 텍스트에서 키워드 검색
        if keyword in text_lower:
            # 위치 확인
            start = text_lower.find(keyword)
            end = start + len(keyword)
            
            # 이미 매칭된 위치와 겹치지 않는지 확인
            if not any(start <= pos < end for pos in matched_positions):
                category = data["categories"][0] if data.get("categories") else None
                priority = category["priority"] if category else 5
                
                found_keywords.append({
                    "keyword": keyword,
                    "canonical": keyword,
                    "category": category["category"] if category else None,
                    "priority": priority
                })
                matched_positions.update(range(start, end))
    
    # 우선순위 정렬
    found_keywords.sort(key=lambda x: x["priority"], reverse=True)
    
    return found_keywords


def run_test(test_case: Dict, keyword_dict: Dict) -> bool:
    """
    테스트 케이스 실행
    
    Args:
        test_case: 테스트 케이스
        keyword_dict: 키워드 사전
    
    Returns:
        테스트 통과 여부
    """
    name = test_case["name"]
    text = test_case["text"]
    
    print(f"\n[TEST] {name}")
    print(f"  입력: {text}")
    
    # 키워드 추출
    extracted = extract_keywords(text, keyword_dict)
    extracted_keywords = [k["canonical"] for k in extracted]
    
    print(f"  추출된 키워드: {extracted_keywords}")
    
    # 검증
    expected = test_case.get("expected_keywords", [])
    if expected:
        # 동의어 정규화
        normalized_expected = []
        for kw in expected:
            normalized = normalize_keyword(kw, keyword_dict) or kw
            normalized_expected.append(normalized)
        
        # 키워드 매칭 확인
        matched = all(kw in extracted_keywords for kw in normalized_expected)
        
        if not matched:
            print(f"  [FAIL] 예상 키워드: {normalized_expected}")
            return False
    
    # 우선순위 확인
    if "expected_priority" in test_case:
        max_priority = max((k["priority"] for k in extracted), default=0)
        if max_priority != test_case["expected_priority"]:
            print(f"  [FAIL] 예상 우선순위: {test_case['expected_priority']}, 실제: {max_priority}")
            return False
    
    # 우선순위 순서 확인
    if "expected_priority_order" in test_case:
        priority_order = [k["canonical"] for k in extracted]
        expected_order = test_case["expected_priority_order"]
        
        # 순서가 맞는지 확인 (앞부분만)
        if priority_order[:len(expected_order)] != expected_order:
            print(f"  [FAIL] 예상 순서: {expected_order}, 실제: {priority_order}")
            return False
    
    print(f"  [PASS]")
    return True


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("키워드 추출 테스트 시작")
    print("=" * 60)
    
    # 1. 키워드 사전 로드
    keyword_dict = load_keyword_dict()
    if not keyword_dict:
        return
    
    print(f"[INFO] 키워드 사전 로드 완료")
    print(f"[INFO] 총 키워드 수: {len(keyword_dict.get('keywords', {}))}")
    
    # 2. 테스트 실행
    passed = 0
    failed = 0
    
    for test_case in TEST_CASES:
        if run_test(test_case, keyword_dict):
            passed += 1
        else:
            failed += 1
    
    # 3. 결과 출력
    print("\n" + "=" * 60)
    print("테스트 결과")
    print("=" * 60)
    print(f"총 {len(TEST_CASES)}개 테스트 중 {passed}개 통과, {failed}개 실패")
    
    if failed == 0:
        print("[SUCCESS] 모든 테스트 통과!")
    else:
        print(f"[WARNING] {failed}개 테스트 실패")


if __name__ == "__main__":
    main()
