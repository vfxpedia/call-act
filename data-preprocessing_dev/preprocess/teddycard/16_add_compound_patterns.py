"""
복합 키워드 패턴 추가 스크립트

주요 키워드에 복합 키워드 패턴을 추가합니다.
복합 키워드는 여러 키워드가 결합된 표현으로, 더 구체적인 의미를 가집니다.
"""

import json
import re
from pathlib import Path
from typing import Dict, List

# 설정 파일 로드
from config import SCRIPT_DIR

# 파일 경로 (우선순위: with_synonyms > v2)
def get_input_file():
    """입력 파일 경로 결정 (우선순위 순)"""
    candidates = [
        SCRIPT_DIR / "keywords_dict_v2_with_synonyms.json",
        SCRIPT_DIR / "keywords_dict_v2.json"
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]  # 기본값

INPUT_FILE = get_input_file()
OUTPUT_FILE = SCRIPT_DIR / "keywords_dict_v2_with_patterns.json"
BACKUP_FILE = SCRIPT_DIR / "keywords_dict_v2_patterns_backup.json"

# 복합 키워드 패턴 정의
COMPOUND_PATTERNS = {
    "분실": [
        {
            "pattern": r"해외.*카드.*분실",
            "priority": 10,
            "category": "분실도난",
            "keywords": ["해외", "카드", "분실"],
            "context": ["해외", "여행", "출국"]
        },
        {
            "pattern": r"카드.*분실",
            "priority": 9,
            "category": "분실도난",
            "keywords": ["카드", "분실"]
        },
        {
            "pattern": r"분실.*신고",
            "priority": 9,
            "category": "분실도난",
            "keywords": ["분실", "신고"]
        }
    ],
    "도난": [
        {
            "pattern": r"도난.*카드",
            "priority": 10,
            "category": "분실도난",
            "keywords": ["도난", "카드"]
        },
        {
            "pattern": r"도난.*신고",
            "priority": 9,
            "category": "분실도난",
            "keywords": ["도난", "신고"]
        }
    ],
    "정지": [
        {
            "pattern": r"카드.*정지",
            "priority": 10,
            "category": "분실도난",
            "keywords": ["카드", "정지"]
        },
        {
            "pattern": r"정지.*해제",
            "priority": 8,
            "category": "분실도난",
            "keywords": ["정지", "해제"]
        }
    ],
    "연체": [
        {
            "pattern": r"연체.*이자",
            "priority": 9,
            "category": "연체",
            "keywords": ["연체", "이자"]
        },
        {
            "pattern": r"연체.*수수료",
            "priority": 9,
            "category": "연체",
            "keywords": ["연체", "수수료"]
        }
    ],
    "한도": [
        {
            "pattern": r"한도.*증액",
            "priority": 8,
            "category": "한도",
            "keywords": ["한도", "증액"]
        },
        {
            "pattern": r"한도.*변경",
            "priority": 8,
            "category": "한도",
            "keywords": ["한도", "변경"]
        }
    ],
    "결제": [
        {
            "pattern": r"결제.*거부",
            "priority": 8,
            "category": "결제",
            "keywords": ["결제", "거부"]
        },
        {
            "pattern": r"결제.*취소",
            "priority": 7,
            "category": "결제",
            "keywords": ["결제", "취소"]
        }
    ],
    "해외": [
        {
            "pattern": r"해외.*이용",
            "priority": 7,
            "category": "해외",
            "keywords": ["해외", "이용"]
        },
        {
            "pattern": r"해외.*수수료",
            "priority": 7,
            "category": "해외",
            "keywords": ["해외", "수수료"]
        }
    ]
}


def add_compound_patterns(keyword_dict: Dict) -> Dict:
    """
    키워드 사전에 복합 키워드 패턴 추가
    
    Args:
        keyword_dict: 키워드 사전
    
    Returns:
        업데이트된 키워드 사전
    """
    keywords = keyword_dict.get("keywords", {})
    
    added_count = 0
    
    for keyword, patterns in COMPOUND_PATTERNS.items():
        if keyword not in keywords:
            print(f"[WARNING] 키워드가 사전에 없습니다: {keyword}")
            continue
        
        # 기존 패턴이 있으면 병합, 없으면 새로 추가
        if "compound_patterns" not in keywords[keyword]:
            keywords[keyword]["compound_patterns"] = []
        
        # 중복 패턴 확인
        existing_patterns = {p["pattern"] for p in keywords[keyword]["compound_patterns"]}
        
        for pattern_info in patterns:
            if pattern_info["pattern"] not in existing_patterns:
                keywords[keyword]["compound_patterns"].append(pattern_info)
                existing_patterns.add(pattern_info["pattern"])
                added_count += 1
        
        print(f"[INFO] {keyword}: {len(patterns)}개 패턴 추가")
    
    keyword_dict["keywords"] = keywords
    
    print(f"[INFO] 총 {added_count}개 패턴 추가됨")
    
    return keyword_dict


def validate_patterns(keyword_dict: Dict) -> bool:
    """
    패턴 유효성 검증
    
    Args:
        keyword_dict: 키워드 사전
    
    Returns:
        유효성 여부
    """
    keywords = keyword_dict.get("keywords", {})
    is_valid = True
    
    for keyword, data in keywords.items():
        patterns = data.get("compound_patterns", [])
        
        for pattern_info in patterns:
            pattern = pattern_info["pattern"]
            
            try:
                # 정규식 컴파일 테스트
                re.compile(pattern)
            except re.error as e:
                print(f"[ERROR] 잘못된 패턴 ({keyword}): {pattern}")
                print(f"  오류: {e}")
                is_valid = False
    
    return is_valid


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("복합 키워드 패턴 추가 시작")
    print("=" * 60)
    
    # 1. 입력 파일 확인
    if not INPUT_FILE.exists():
        print(f"[ERROR] 입력 파일이 없습니다: {INPUT_FILE}")
        print(f"[INFO] 먼저 14_convert_keyword_dict_structure.py를 실행하세요.")
        return
    
    # 2. 백업 생성
    if not BACKUP_FILE.exists():
        print(f"[INFO] 백업 파일 생성: {BACKUP_FILE}")
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
    
    # 3. 키워드 사전 로드
    print(f"[INFO] 키워드 사전 로드: {INPUT_FILE}")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        keyword_dict = json.load(f)
    
    # 4. 복합 키워드 패턴 추가
    print("[INFO] 복합 키워드 패턴 추가 중...")
    updated_dict = add_compound_patterns(keyword_dict)
    
    # 5. 패턴 유효성 검증
    print("[INFO] 패턴 유효성 검증 중...")
    if not validate_patterns(updated_dict):
        print("[ERROR] 잘못된 패턴이 발견되었습니다. 수정 후 다시 실행하세요.")
        return
    
    # 6. 결과 저장
    print(f"[INFO] 결과 저장: {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(updated_dict, f, ensure_ascii=False, indent=2)
    
    # 7. 통계 출력
    total_patterns = sum(
        len(v.get("compound_patterns", [])) 
        for v in updated_dict["keywords"].values()
    )
    
    print("[SUCCESS] 처리 완료!")
    print(f"[INFO] 총 복합 키워드 패턴 수: {total_patterns}")
    print(f"[INFO] 결과 파일: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
