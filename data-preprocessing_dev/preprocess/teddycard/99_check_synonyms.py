"""
키워드 사전의 동의어/유의어 확인 스크립트
"""

import json
from pathlib import Path
from collections import defaultdict

# 경로 설정
BASE_DIR = Path(__file__).parent.parent.parent.parent
KEYWORDS_DICT_FILE = BASE_DIR / "data-preprocessing_dev" / "data" / "teddycard" / "keywords_dict_v2_with_patterns.json"


def check_synonyms():
    """동의어/유의어 데이터 확인"""
    print(f"키워드 사전 로드 중: {KEYWORDS_DICT_FILE}")
    
    with open(KEYWORDS_DICT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    keywords = data.get('keywords', {})
    print(f"총 키워드 수: {len(keywords)}개\n")
    
    # synonyms 확인
    synonyms_keywords = []
    for keyword, info in keywords.items():
        synonyms = info.get('synonyms', [])
        if synonyms and len(synonyms) > 0:
            synonyms_keywords.append((keyword, synonyms))
    
    print(f"[synonyms 필드]")
    print(f"  동의어가 있는 키워드: {len(synonyms_keywords)}개")
    print(f"  총 동의어 수: {sum(len(s) for _, s in synonyms_keywords)}개\n")
    
    if synonyms_keywords:
        print("예시 (최대 10개):")
        for keyword, synonyms in synonyms_keywords[:10]:
            print(f"  - {keyword}: {synonyms}")
    else:
        print("  동의어가 있는 키워드가 없습니다.\n")
    
    # variations 확인
    variations_keywords = []
    for keyword, info in keywords.items():
        variations = info.get('variations', [])
        if variations and len(variations) > 0:
            variations_keywords.append((keyword, variations))
    
    print(f"\n[variations 필드]")
    print(f"  변형이 있는 키워드: {len(variations_keywords)}개")
    print(f"  총 변형 수: {sum(len(v) for _, v in variations_keywords)}개\n")
    
    if variations_keywords:
        print("예시 (최대 10개):")
        for keyword, variations in variations_keywords[:10]:
            print(f"  - {keyword}: {variations}")
    else:
        print("  변형이 있는 키워드가 없습니다.\n")
    
    # compound_patterns 확인
    patterns_keywords = []
    for keyword, info in keywords.items():
        patterns = info.get('compound_patterns', [])
        if patterns and len(patterns) > 0:
            patterns_keywords.append((keyword, patterns))
    
    print(f"\n[compound_patterns 필드]")
    print(f"  패턴이 있는 키워드: {len(patterns_keywords)}개")
    print(f"  총 패턴 수: {sum(len(p) for _, p in patterns_keywords)}개\n")
    
    if patterns_keywords:
        print("예시 (최대 5개):")
        for keyword, patterns in patterns_keywords[:5]:
            print(f"  - {keyword}: {len(patterns)}개 패턴")
            for pattern in patterns[:3]:
                pattern_str = pattern.get('pattern', 'N/A')
                print(f"    * {pattern_str}")
    
    # 전체 필드 구조 확인
    print(f"\n[필드 구조 확인]")
    sample_keyword = list(keywords.keys())[0]
    sample_data = keywords[sample_keyword]
    print(f"샘플 키워드: {sample_keyword}")
    print(f"필드 목록: {list(sample_data.keys())}")
    print(f"\n샘플 데이터 구조:")
    for key, value in sample_data.items():
        if isinstance(value, list):
            print(f"  {key}: [{len(value)}개 항목]")
        elif isinstance(value, dict):
            print(f"  {key}: {{dict with {len(value)} keys}}")
        else:
            print(f"  {key}: {type(value).__name__}")


if __name__ == "__main__":
    check_synonyms()
