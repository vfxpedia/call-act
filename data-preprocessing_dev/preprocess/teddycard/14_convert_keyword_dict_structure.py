"""
키워드 사전 구조 변환 스크립트

기존 카테고리별 키워드 리스트 구조를 새로운 키워드 중심 구조로 변환합니다.

변환 규칙:
1. 기존 카테고리별 키워드 리스트 → 키워드 중심 구조로 변환
2. 각 키워드에 priority, urgency 추가
3. 긴급 키워드 우선순위 설정
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Any
from collections import defaultdict

# 설정 파일 로드
from config import SCRIPT_DIR

# 파일 경로
INPUT_FILE = SCRIPT_DIR / "keywords_dict_updated.json"
OUTPUT_FILE = SCRIPT_DIR / "keywords_dict_v2.json"
BACKUP_FILE = SCRIPT_DIR / "keywords_dict_updated_backup.json"

# 긴급 키워드 우선순위 설정
URGENT_KEYWORDS = {
    "분실": {"priority": 10, "urgency": "high"},
    "도난": {"priority": 10, "urgency": "high"},
    "정지": {"priority": 10, "urgency": "high"},
    "연체": {"priority": 9, "urgency": "high"},
    "해지": {"priority": 9, "urgency": "high"},
    "재발급": {"priority": 8, "urgency": "medium"},
    "한도": {"priority": 8, "urgency": "medium"},
}

# 카테고리별 기본 우선순위 (긴급 키워드가 아닌 경우)
CATEGORY_PRIORITY = {
    "분실도난": 9,
    "결제": 7,
    "포인트": 6,
    "연체": 8,
    "혜택": 5,
    "본인확인": 7,
    "해외": 6,
    "카드종류": 5,
}

# 카테고리별 기본 urgency
CATEGORY_URGENCY = {
    "분실도난": "high",
    "연체": "high",
    "결제": "medium",
    "포인트": "medium",
    "혜택": "low",
    "본인확인": "medium",
    "해외": "medium",
    "카드종류": "low",
}

# 하나카드 데이터 빈도수 (실제 데이터 기반)
# 참고: 키워드 사전의 카테고리명과 하나카드 데이터의 카테고리명이 다를 수 있음
# 키워드 사전 카테고리명과 가장 유사한 하나카드 카테고리를 매핑
CATEGORY_FREQUENCY_MAPPING = {
    "분실도난": "도난/분실 신청/해제",  # 398건, 6.1%
    "결제": "결제대금 안내",  # 331건, 5.1% (주요 결제 관련)
    "한도": "한도상향 접수/처리",  # 402건, 6.2%
    "연체": "연체대금 즉시출금",  # 163건, 2.5%
    "이용내역": "이용내역 안내",  # 919건, 14.1%
    "선결제": "선결제/즉시출금",  # 927건, 14.2%
    "이벤트": "이벤트 안내",  # 223건, 3.4%
    "혜택": "이벤트 안내",  # 혜택 관련은 이벤트로 매핑
}

# 하나카드 데이터 빈도수 (상위 10개 카테고리)
CATEGORY_FREQUENCY = {
    "선결제/즉시출금": {"count": 927, "percentage": 14.2},
    "이용내역 안내": {"count": 919, "percentage": 14.1},
    "한도상향 접수/처리": {"count": 402, "percentage": 6.2},
    "도난/분실 신청/해제": {"count": 398, "percentage": 6.1},
    "결제대금 안내": {"count": 331, "percentage": 5.1},
    "승인취소/매출취소 안내": {"count": 301, "percentage": 4.6},
    "이벤트 안내": {"count": 223, "percentage": 3.4},
    "정부지원 바우처": {"count": 167, "percentage": 2.6},
    "연체대금 즉시출금": {"count": 163, "percentage": 2.5},
    "한도 안내": {"count": 162, "percentage": 2.5},
}


def calculate_priority_from_frequency_and_urgency(category: str, urgency: str) -> int:
    """
    빈도수와 긴급성을 고려한 우선순위 계산
    
    Args:
        category: 키워드 사전의 카테고리명
        urgency: 긴급성 ("high", "medium", "low")
    
    Returns:
        우선순위 (1-10)
    """
    # 키워드 사전 카테고리를 하나카드 카테고리로 매핑
    hana_category = CATEGORY_FREQUENCY_MAPPING.get(category)
    
    # 빈도수 점수 계산
    if hana_category and hana_category in CATEGORY_FREQUENCY:
        freq_info = CATEGORY_FREQUENCY[hana_category]
        frequency_score = min(10, freq_info["percentage"] * 10 / 14.2)  # 14.2%를 10점으로 정규화
    else:
        # 매핑되지 않은 카테고리는 기본값 사용
        frequency_score = 5.0
    
    # 긴급성 점수
    urgency_score = {"high": 10, "medium": 5, "low": 2}[urgency]
    
    # 가중 평균 (긴급성 60%, 빈도수 40%)
    priority = int(urgency_score * 0.6 + frequency_score * 0.4)
    
    return max(1, min(10, priority))  # 1-10 범위로 제한


def determine_priority_and_urgency(keyword: str, categories: List[str]) -> tuple:
    """
    키워드의 우선순위와 urgency 결정
    
    Returns:
        (priority, urgency)
    """
    # 1. 긴급 키워드 확인
    if keyword in URGENT_KEYWORDS:
        # 긴급 키워드는 빈도수도 고려하여 우선순위 계산
        urgency = URGENT_KEYWORDS[keyword]["urgency"]
        # 긴급 키워드의 경우 카테고리별로 빈도수 기반 계산
        if categories:
            # 가장 관련성 높은 카테고리로 우선순위 계산
            priority = calculate_priority_from_frequency_and_urgency(categories[0], urgency)
            # 긴급 키워드는 최소 우선순위 보장
            priority = max(priority, URGENT_KEYWORDS[keyword]["priority"] - 1)
            return priority, urgency
        else:
            return URGENT_KEYWORDS[keyword]["priority"], urgency
    
    # 2. 카테고리별 우선순위 계산 (빈도수 반영)
    max_priority = 5
    max_urgency = "medium"
    
    for category in categories:
        cat_urgency = CATEGORY_URGENCY.get(category, "medium")
        # 빈도수와 긴급성을 고려한 우선순위 계산
        cat_priority = calculate_priority_from_frequency_and_urgency(category, cat_urgency)
        
        if cat_priority > max_priority:
            max_priority = cat_priority
        if cat_urgency == "high":
            max_urgency = "high"
        elif cat_urgency == "medium" and max_urgency == "low":
            max_urgency = "medium"
    
    return max_priority, max_urgency


def convert_structure(old_dict: Dict[str, List[str]]) -> Dict[str, Any]:
    """
    기존 구조를 새 구조로 변환
    
    Args:
        old_dict: 기존 카테고리별 키워드 리스트 구조
    
    Returns:
        새로운 키워드 중심 구조
    """
    # 키워드별 카테고리 수집
    keyword_to_categories = defaultdict(list)
    
    for category, keywords in old_dict.items():
        for keyword in keywords:
            if keyword not in keyword_to_categories[keyword]:
                keyword_to_categories[keyword].append(category)
    
    # 새 구조 생성
    new_structure = {
        "keywords": {},
        "metadata": {
            "version": "2.0",
            "total_keywords": len(keyword_to_categories),
            "converted_from": "keywords_dict_updated.json"
        }
    }
    
    for keyword, categories in keyword_to_categories.items():
        priority, urgency = determine_priority_and_urgency(keyword, categories)
        
        # 카테고리 정보 생성 (빈도수 기반 우선순위 계산)
        category_list = []
        for category in categories:
            cat_urgency = CATEGORY_URGENCY.get(category, "medium")
            # 빈도수와 긴급성을 고려한 우선순위 계산
            cat_priority = calculate_priority_from_frequency_and_urgency(category, cat_urgency)
            
            category_list.append({
                "category": category,
                "priority": cat_priority,
                "urgency": cat_urgency,
                "context_hints": [],  # 나중에 추가
                "weight": 1.0
            })
        
        # 키워드 엔트리 생성
        new_structure["keywords"][keyword] = {
            "canonical": keyword,
            "categories": category_list,
            "synonyms": [],  # 나중에 추가
            "variations": [],  # 나중에 추가
            "compound_patterns": [],  # 나중에 추가
            "ambiguity_resolution": {
                "default_category": categories[0] if categories else None,
                "context_rules": []
            }
        }
    
    return new_structure


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("키워드 사전 구조 변환 시작")
    print("=" * 60)
    
    # 1. 입력 파일 확인
    if not INPUT_FILE.exists():
        print(f"[ERROR] 입력 파일이 없습니다: {INPUT_FILE}")
        return
    
    # 2. 백업 생성
    if INPUT_FILE.exists() and not BACKUP_FILE.exists():
        print(f"[INFO] 백업 파일 생성: {BACKUP_FILE}")
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
    
    # 3. 기존 구조 로드
    print(f"[INFO] 기존 키워드 사전 로드: {INPUT_FILE}")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        old_dict = json.load(f)
    
    # 4. 구조 변환
    print("[INFO] 구조 변환 중...")
    new_structure = convert_structure(old_dict)
    
    # 5. 통계 출력
    total_keywords = len(new_structure["keywords"])
    urgent_count = sum(1 for k, v in new_structure["keywords"].items() 
                      if any(cat["urgency"] == "high" for cat in v["categories"]))
    
    print(f"[INFO] 변환 완료:")
    print(f"  - 총 키워드 수: {total_keywords}")
    print(f"  - 긴급 키워드 수: {urgent_count}")
    print(f"  - 일반 키워드 수: {total_keywords - urgent_count}")
    
    # 6. 새 구조 저장
    print(f"[INFO] 새 구조 저장: {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_structure, f, ensure_ascii=False, indent=2)
    
    print("[SUCCESS] 변환 완료!")
    print(f"[INFO] 결과 파일: {OUTPUT_FILE}")
    print(f"[INFO] 백업 파일: {BACKUP_FILE}")


if __name__ == "__main__":
    main()
