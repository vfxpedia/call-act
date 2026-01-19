"""
테디카드 통합 전처리 - 텍스트 치환 모듈

데이터 소스별 화이트리스트 방식으로 카드사 이름을 테디카드로 치환합니다.
- shinhan: 신한 관련 모든 표현 → 테디
- hyundai: 현대 관련 모든 표현 → 테디
- samsung: 삼성 관련 모든 표현 → 테디
- special_card: 치환하지 않음 (제휴 카드 정보 보존)
"""

from typing import List, Tuple


def replace_card_brand(text: str, source: str) -> str:
    """
    카드사 이름을 테디카드로 치환 (데이터 소스별 화이트리스트)
    
    Args:
        text: 치환할 텍스트
        source: 데이터 소스 ('shinhan', 'hyundai', 'samsung', 'special_card' 등)
    
    Returns:
        치환된 텍스트
    """
    
    # shinhan 데이터: 신한 관련 모든 표현 치환
    if source == 'shinhan':
        replacements: List[Tuple[str, str]] = [
            ('신한카드사', '테디카드사'),      # 긴 패턴부터 먼저
            ('신한 카드', '테디 카드'),
            ('신한카드', '테디카드'),
            ('신한은행', '테디은행'),
            ('신한 SOL페이', '테디 SOL페이'),
            ('신한 SOL', '테디 SOL'),
            ('신한', '테디'),                  # 마지막에 적용
            ('shinhan', 'teddy'),             # 영문도 치환
            ('Shinhan', 'Teddy'),
        ]
        # 긴 패턴부터 먼저 치환 (중복 치환 방지)
        for old, new in sorted(replacements, key=lambda x: len(x[0]), reverse=True):
            text = text.replace(old, new)
    
    # hyundai 데이터: 현대 관련 모든 표현 치환
    elif source == 'hyundai':
        replacements: List[Tuple[str, str]] = [
            ('현대카드사', '테디카드사'),
            ('현대 카드', '테디 카드'),
            ('현대카드', '테디카드'),
            ('현대은행', '테디은행'),
            ('현대', '테디'),
            ('hyundai', 'teddy'),
            ('Hyundai', 'Teddy'),
        ]
        for old, new in sorted(replacements, key=lambda x: len(x[0]), reverse=True):
            text = text.replace(old, new)
    
    # samsung 데이터: 삼성 관련 모든 표현 치환
    elif source == 'samsung':
        replacements: List[Tuple[str, str]] = [
            ('삼성카드사', '테디카드사'),
            ('삼성 카드', '테디 카드'),
            ('삼성카드', '테디카드'),
            ('삼성', '테디'),
            ('samsung', 'teddy'),
            ('Samsung', 'Teddy'),
        ]
        for old, new in sorted(replacements, key=lambda x: len(x[0]), reverse=True):
            text = text.replace(old, new)
    
    # special_card 데이터: 치환하지 않음 (제휴 카드 정보 보존)
    # hyundai, samsung, shinhan 이외 데이터 소스: 치환하지 않음
    
    return text


if __name__ == '__main__':
    # 테스트 코드
    test_cases = [
        # shinhan 테스트
        ("신한은행 최초고시 전신환 매도율을 적용한 후, 신한카드사가 부과하는...", "shinhan", 
         "테디은행 최초고시 전신환 매도율을 적용한 후, 테디카드사가 부과하는..."),
        ("신한 SOL페이로 국내 결제 시 0.1% 추가 적립", "shinhan",
         "테디 SOL페이로 국내 결제 시 0.1% 추가 적립"),
        ("신한카드 Deep Dream", "shinhan",
         "테디카드 Deep Dream"),
        
        # hyundai 테스트
        ("현대카드 Apple Pay 이용처", "hyundai",
         "테디카드 Apple Pay 이용처"),
        ("현대백화점", "hyundai",
         "테디백화점"),
        
        # samsung 테스트
        ("삼성카드 신용카드 이용 가이드", "samsung",
         "테디카드 신용카드 이용 가이드"),
        
        # special_card 테스트 (치환하지 않음)
        ("KB국민은행 최초고시 전신환 매도율...", "special_card",
         "KB국민은행 최초고시 전신환 매도율..."),
    ]
    
    print("텍스트 치환 함수 테스트")
    print("=" * 80)
    
    all_passed = True
    for original, source, expected in test_cases:
        result = replace_card_brand(original, source)
        passed = result == expected
        all_passed = all_passed and passed
        
        status = "PASS" if passed else "FAIL"
        print(f"\n{status} - Source: {source}")
        print(f"  Original: {original[:50]}...")
        print(f"  Expected: {expected[:50]}...")
        print(f"  Result:   {result[:50]}...")
        
        if not passed:
            print(f"  ERROR: 치환 결과가 예상과 다릅니다!")
    
    print("\n" + "=" * 80)
    if all_passed:
        print("모든 테스트 통과!")
    else:
        print("일부 테스트 실패")
        exit(1)
