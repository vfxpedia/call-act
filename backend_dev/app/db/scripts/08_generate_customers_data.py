"""
고객 데이터 생성 스크립트

기능:
- 2,500명의 mock 고객 데이터 생성
- 12개 페르소나별 분포에 따른 고객 특성 할당
- 실제 데이터 분포 기반 성별/연령대 분배 (여55%, 남45%)
- LLM 상담 가이던스 메시지 생성
- customersData.json 저장
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

# config.py에서 경로 가져오기
from config import CUSTOMERS_DATA_FILE, DB_DIR, CARD_PRODUCTS_FILE

# 재현성을 위한 랜덤 시드 고정
# 모든 팀원이 동일한 데이터를 생성하도록 보장
random.seed(42)

# 상수
TOTAL_CUSTOMERS = 2500

# ============================================================
# 카드 상품 분류 (실제 상품명 사용)
# ============================================================

def load_real_card_products() -> List[str]:
    """실제 카드 상품명 로드 (398개)"""
    try:
        print(f"\n[카드 상품 로드]")
        print(f"  경로: {CARD_PRODUCTS_FILE}")

        if not CARD_PRODUCTS_FILE.exists():
            print(f"  [오류] 파일이 존재하지 않습니다!")
            print(f"  [해결방법] data-preprocessing 서브모듈을 업데이트하세요:")
            print(f"    git submodule update --init --recursive")
            return []

        with open(CARD_PRODUCTS_FILE, 'r', encoding='utf-8') as f:
            products = json.load(f)

        # name 필드 추출 (JSON 구조: id, name, card_type, brand, ...)
        card_names = [p.get('name', '') for p in products if p.get('name')]

        if not card_names:
            print(f"  [오류] JSON에서 'name' 필드를 찾을 수 없습니다!")
            print(f"  [디버그] JSON 첫 번째 항목의 키: {list(products[0].keys()) if products else '없음'}")
            return []

        print(f"  [성공] {len(card_names)}개 카드 상품 로드 완료")
        return card_names

    except json.JSONDecodeError as e:
        print(f"  [오류] JSON 파싱 실패: {e}")
        print(f"  [해결방법] JSON 파일 형식을 확인하세요")
        return []
    except Exception as e:
        print(f"  [오류] 카드 상품 로드 실패: {e}")
        return []


def categorize_card_products(card_names: List[str]) -> Dict[str, List[str]]:
    """카드 상품을 카테고리별로 분류"""
    categories = {
        'premium': [],      # 프리미엄/플래티넘 카드
        'cashback': [],     # 캐시백 카드
        'point': [],        # 포인트 적립 카드
        'travel': [],       # 여행/항공 카드
        'shopping': [],     # 쇼핑/제휴 카드
        'check': [],        # 체크카드
        'basic': [],        # 일반 카드
    }

    premium_keywords = ['플래티넘', '프리미엄', 'Platinum', 'Premium', 'VIP', 'VVIP', '프레스티지']
    cashback_keywords = ['캐시백', 'Cashback', 'Cash', '환급']
    point_keywords = ['포인트', 'Point', '적립', 'Reward']
    travel_keywords = ['여행', '항공', 'Travel', 'Air', '마일', 'Mile', '해외']
    shopping_keywords = ['쇼핑', '백화점', '마트', '11번가', '쿠팡', 'CJ', 'GS', 'AK', '롯데', '현대']
    check_keywords = ['체크', 'Check', 'CMA']

    for card_name in card_names:
        name_upper = card_name.upper()

        if any(kw in card_name for kw in premium_keywords):
            categories['premium'].append(card_name)
        elif any(kw in card_name for kw in cashback_keywords):
            categories['cashback'].append(card_name)
        elif any(kw in card_name for kw in travel_keywords):
            categories['travel'].append(card_name)
        elif any(kw in card_name for kw in shopping_keywords):
            categories['shopping'].append(card_name)
        elif any(kw in card_name for kw in check_keywords):
            categories['check'].append(card_name)
        elif any(kw in card_name for kw in point_keywords):
            categories['point'].append(card_name)
        else:
            categories['basic'].append(card_name)

    return categories


# 등급별 카드 카테고리 매핑
GRADE_CARD_CATEGORIES = {
    'VIP': ['premium'],
    'GOLD': ['premium', 'cashback', 'travel'],
    'SILVER': ['cashback', 'point', 'shopping'],
    'GENERAL': ['point', 'shopping', 'check', 'basic'],
}

# 실제 카드 상품 로드 및 분류 (전역 변수)
_REAL_CARD_NAMES = None
_CARD_CATEGORIES = None


def get_card_categories() -> Dict[str, List[str]]:
    """카드 카테고리 가져오기 (지연 로딩)"""
    global _REAL_CARD_NAMES, _CARD_CATEGORIES

    if _CARD_CATEGORIES is None:
        _REAL_CARD_NAMES = load_real_card_products()
        if _REAL_CARD_NAMES:
            _CARD_CATEGORIES = categorize_card_products(_REAL_CARD_NAMES)
            print(f"\n[카드 카테고리 분류 결과]")
            category_names = {
                'premium': '프리미엄',
                'cashback': '캐시백',
                'point': '포인트',
                'travel': '여행/항공',
                'shopping': '쇼핑/제휴',
                'check': '체크카드',
                'basic': '일반',
            }
            for cat, cards in _CARD_CATEGORIES.items():
                cat_name = category_names.get(cat, cat)
                print(f"  - {cat_name}: {len(cards)}개")
        else:
            # Fallback - 실제 카드 상품 로드 실패 시
            _CARD_CATEGORIES = {
                'premium': ['테디카드 프리미엄', '테디카드 플래티넘'],
                'cashback': ['테디카드 캐시백'],
                'point': ['테디카드 포인트'],
                'travel': ['테디카드 여행'],
                'shopping': ['테디카드 쇼핑'],
                'check': ['테디카드 체크'],
                'basic': ['테디카드 베이직', '테디카드 골드', '테디카드 실버'],
            }
            print("\n[경고] 실제 카드 상품 로드 실패 → 기본 테디카드 타입 사용")
            print("       팀 레포의 data-preprocessing 서브모듈을 확인하세요!")

    return _CARD_CATEGORIES


def select_card_for_grade(grade: str) -> str:
    """등급에 맞는 카드 선택"""
    card_categories = get_card_categories()
    allowed_categories = GRADE_CARD_CATEGORIES.get(grade, ['basic'])

    # 허용된 카테고리에서 카드 목록 수집
    available_cards = []
    for cat in allowed_categories:
        available_cards.extend(card_categories.get(cat, []))

    # 카드가 없으면 모든 카테고리에서 선택
    if not available_cards:
        for cards in card_categories.values():
            available_cards.extend(cards)

    return random.choice(available_cards) if available_cards else '테디카드 기본'

# ============================================================
# 한국 이름 풀
# ============================================================

# 성씨 (100개) - 빈도 기반 가중치
LAST_NAMES = [
    ('김', 21.5), ('이', 14.7), ('박', 8.4), ('최', 4.7), ('정', 4.3),
    ('강', 2.3), ('조', 2.1), ('윤', 2.0), ('장', 2.0), ('임', 1.7),
    ('한', 1.5), ('오', 1.5), ('서', 1.5), ('신', 1.5), ('권', 1.4),
    ('황', 1.4), ('안', 1.3), ('송', 1.3), ('류', 0.9), ('전', 0.9),
    ('홍', 0.8), ('고', 0.8), ('문', 0.7), ('양', 0.7), ('손', 0.7),
    ('배', 0.6), ('조', 0.6), ('백', 0.6), ('허', 0.5), ('유', 0.5),
    ('남', 0.5), ('심', 0.5), ('노', 0.4), ('하', 0.4), ('곽', 0.4),
    ('성', 0.4), ('차', 0.4), ('주', 0.4), ('우', 0.3), ('구', 0.3),
    ('신', 0.3), ('민', 0.3), ('진', 0.3), ('지', 0.3), ('엄', 0.3),
    ('채', 0.3), ('원', 0.3), ('천', 0.2), ('방', 0.2), ('공', 0.2),
    ('현', 0.2), ('함', 0.2), ('변', 0.2), ('염', 0.2), ('여', 0.2),
    ('추', 0.2), ('도', 0.2), ('소', 0.2), ('석', 0.2), ('선', 0.2),
    ('설', 0.2), ('마', 0.1), ('길', 0.1), ('연', 0.1), ('위', 0.1),
    ('표', 0.1), ('명', 0.1), ('기', 0.1), ('반', 0.1), ('라', 0.1),
    ('왕', 0.1), ('금', 0.1), ('옥', 0.1), ('육', 0.1), ('인', 0.1),
    ('맹', 0.1), ('제', 0.1), ('모', 0.1), ('탁', 0.1), ('국', 0.1),
    ('어', 0.1), ('은', 0.1), ('편', 0.1), ('용', 0.1), ('예', 0.1),
    ('경', 0.1), ('봉', 0.1), ('사', 0.1), ('부', 0.1), ('황보', 0.1),
    ('제갈', 0.1), ('남궁', 0.1), ('선우', 0.1), ('독고', 0.1), ('사공', 0.1),
    ('동방', 0.1), ('서문', 0.1), ('단', 0.1), ('복', 0.1), ('빈', 0.1),
]

# 남성 이름 (100개)
MALE_FIRST_NAMES = [
    '민수', '현우', '준호', '성민', '지훈', '동현', '승현', '재윤', '정우', '태현',
    '우진', '준혁', '민재', '시우', '예준', '도윤', '주원', '하준', '서준', '지호',
    '건우', '현준', '민준', '유준', '선우', '정민', '윤서', '민호', '승우', '지원',
    '재민', '준영', '연우', '시현', '태윤', '민규', '영민', '승민', '도현', '우성',
    '현석', '태민', '준수', '정현', '성훈', '동욱', '영호', '재혁', '지성', '민석',
    '준희', '상현', '현수', '진우', '상민', '성준', '경민', '기현', '대현', '정훈',
    '태준', '서진', '진혁', '세준', '민혁', '수호', '성현', '한결', '은우', '지한',
    '동건', '승준', '재원', '준서', '현빈', '재현', '도훈', '용민', '정호', '진수',
    '병철', '광호', '원식', '창수', '종현', '상우', '영수', '상호', '재호', '명수',
    '철수', '영철', '동수', '기철', '종호', '석진', '진호', '세영', '광민', '찬혁',
]

# 여성 이름 (100개)
FEMALE_FIRST_NAMES = [
    '서연', '민지', '수빈', '지은', '하은', '지민', '예은', '유진', '수진', '지현',
    '은서', '민서', '소연', '혜진', '유나', '서현', '지영', '예진', '소희', '윤서',
    '하윤', '민정', '수아', '지아', '다은', '채원', '나은', '서윤', '가은', '예원',
    '민아', '유빈', '수민', '나연', '지우', '소미', '은지', '정은', '현지', '수연',
    '예나', '서영', '민영', '지수', '소영', '미나', '혜원', '정민', '유미', '선영',
    '다영', '은수', '주연', '주희', '진아', '미영', '현정', '세연', '수정', '연서',
    '연우', '은영', '아영', '채은', '시아', '하린', '서희', '윤아', '미선', '보라',
    '세희', '아름', '지혜', '다연', '나영', '정아', '은비', '승아', '민경', '수현',
    '효진', '혜림', '예림', '지원', '소정', '예솔', '나현', '주아', '유경', '미정',
    '정희', '영숙', '순옥', '복순', '말숙', '옥순', '영자', '순자', '영희', '명숙',
]

# ============================================================
# 페르소나 정의 (8개 유형) - 2026-01-23 확정
# ============================================================

PERSONAS = {
    # 일반 고객 유형 (N: Normal) - 60%
    'N1': {
        'name': '실용주의형',
        'description': '불필요한 말 없이 바로 문의사항을 말함',
        'personality_tags': ['practical', 'direct', 'efficient'],
        'communication_style': {'speed': 'fast', 'tone': 'direct'},
        'llm_guidance': '바로 본론으로 진행하세요. 간결하고 명확하게 답변해주세요.',
        'ratio': 0.25,
    },
    'N2': {
        'name': '친화적수다형',
        'description': '사적인 이야기나 본인 상황을 길게 설명함',
        'personality_tags': ['friendly', 'talkative', 'personal'],
        'communication_style': {'speed': 'moderate', 'tone': 'warm'},
        'llm_guidance': '고객의 이야기를 경청하고 공감해주세요. 친근하게 응대하세요.',
        'ratio': 0.20,
    },
    'N3': {
        'name': '신중/보안중시형',
        'description': '신중하고 의심을 보임',
        'personality_tags': ['cautious', 'security_conscious', 'suspicious'],
        'communication_style': {'speed': 'slow', 'tone': 'formal'},
        'llm_guidance': '본인 확인 절차를 상세히 안내하고, 보안 관련 우려를 해소해주세요.',
        'ratio': 0.15,
    },
    # 특수 고객 유형 (S: Special) - 40%
    'S1': {
        'name': '급한성격형',
        'description': '빠른 처리를 선호함',
        'personality_tags': ['impatient', 'urgent', 'busy'],
        'communication_style': {'speed': 'fast', 'tone': 'concise'},
        'llm_guidance': '신속하게 처리해주세요. 핵심만 간결하게 전달하세요.',
        'ratio': 0.15,
    },
    'S2': {
        'name': '꼼꼼상세형',
        'description': '상세한 설명을 요구함',
        'personality_tags': ['detailed', 'analytical', 'thorough'],
        'communication_style': {'speed': 'slow', 'tone': 'thorough'},
        'llm_guidance': '단계별로 상세하게 설명해주세요. 모든 내용을 빠짐없이 안내하세요.',
        'ratio': 0.10,
    },
    'S3': {
        'name': '이해부족형',
        'description': '설명을 잘 이해하지 못하여 반복적으로 확인함',
        'personality_tags': ['confused', 'needs_repetition', 'patient_required'],
        'communication_style': {'speed': 'slow', 'tone': 'patient'},
        'llm_guidance': '쉬운 용어로 천천히 설명해주세요. 이해했는지 확인하고 필요시 반복 안내하세요.',
        'ratio': 0.07,
    },
    'S4': {
        'name': '반복민원형',
        'description': '과거의 상담 이력을 언급하며 해결되지 않은 불만을 제기함',
        'personality_tags': ['repeat_caller', 'frustrated', 'unresolved'],
        'communication_style': {'speed': 'moderate', 'tone': 'solution_focused'},
        'llm_guidance': '이전 상담 이력을 확인하고 근본적인 해결책을 제시하세요. 진심으로 사과하세요.',
        'ratio': 0.05,
    },
    'S5': {
        'name': '불만형',
        'description': '분노, 짜증을 드러냄',
        'personality_tags': ['angry', 'frustrated', 'demanding'],
        'communication_style': {'speed': 'moderate', 'tone': 'calm_professional'},
        'llm_guidance': '차분하게 경청하고 공감해주세요. 감정을 누그러뜨린 후 해결 방안을 제시하세요.',
        'ratio': 0.03,
    },
}

# ============================================================
# 연령대 분포 (hana_rdb_metadata.json 분석 결과)
# ============================================================

AGE_GROUP_DISTRIBUTION = {
    '10대': 0.004,   # 0.4%
    '20대': 0.057,   # 5.7%
    '30대': 0.126,   # 12.6%
    '40대': 0.249,   # 24.9%
    '50대': 0.283,   # 28.3% (최다)
    '60대': 0.216,   # 21.6%
    '70대': 0.065,   # 6.5%
}

# 성별 분포
GENDER_DISTRIBUTION = {
    'female': 0.545,  # 54.5%
    'male': 0.455,    # 45.5%
}

# 고객 등급 분포
GRADE_DISTRIBUTION = {
    'VIP': 0.03,      # 3%
    'GOLD': 0.12,     # 12%
    'SILVER': 0.25,   # 25%
    'GENERAL': 0.60,  # 60%
}

# 카드 타입 (Fallback용 - 실제로는 실제 상품명 사용)
CARD_TYPES_FALLBACK = [
    '테디카드 프리미엄',
    '테디카드 플래티넘',
    '테디카드 골드',
    '테디카드 실버',
    '테디카드 베이직',
    '테디카드 포인트',
    '테디카드 캐시백',
    '테디카드 여행',
    '테디카드 쇼핑',
    '테디카드 주유',
]

# 카드 브랜드
CARD_BRANDS = ['visa', 'mastercard', 'local']


def weighted_choice(items: List[Tuple], weights: List[float] = None) -> str:
    """가중치 기반 랜덤 선택"""
    if weights:
        return random.choices(items, weights=weights, k=1)[0]
    else:
        # items가 (name, weight) 튜플 리스트인 경우
        names = [item[0] for item in items]
        weights = [item[1] for item in items]
        return random.choices(names, weights=weights, k=1)[0]


def generate_phone_number() -> str:
    """전화번호 생성 (010-XXXX-XXXX)"""
    middle = random.randint(1000, 9999)
    last = random.randint(1000, 9999)
    return f"010-{middle}-{last}"


def generate_card_number_last4() -> str:
    """카드번호 마지막 4자리 생성"""
    return str(random.randint(1000, 9999))


def generate_card_dates(customer_id: str = None) -> Tuple[str, str]:
    """
    카드 발급일과 만료일 생성

    Args:
        customer_id: 고객 ID (재현성을 위한 시드용)

    Returns:
        (card_issue_date, card_expiry_date) - YYYY-MM-DD 형식
    """
    from datetime import date, timedelta
    import hashlib

    # customer_id 기반 시드 생성 (재현성 보장)
    if customer_id:
        seed_value = int(hashlib.md5((customer_id + "_card").encode()).hexdigest()[:8], 16)
        local_random = random.Random(seed_value)
    else:
        local_random = random

    today = date.today()

    # 안전한 연도 변경 함수 (윤년 2월 29일 처리)
    def safe_add_years(d, years):
        try:
            return d.replace(year=d.year + years)
        except ValueError:
            # 2월 29일 → 2월 28일로 조정
            return d.replace(day=28, year=d.year + years)

    # 발급일: 1~8년 전 (카드 유효기간 보통 5년)
    days_ago = local_random.randint(365, 365 * 8)  # 1~8년 전
    issue_date = today - timedelta(days=days_ago)

    # 만료일: 발급일로부터 5년 후
    expiry_date = safe_add_years(issue_date, 5)

    # 만료일이 과거인 경우 재발급 시뮬레이션 (5년 연장)
    if expiry_date < today:
        issue_date = safe_add_years(issue_date, 5)
        expiry_date = safe_add_years(expiry_date, 5)

    return issue_date.strftime("%Y-%m-%d"), expiry_date.strftime("%Y-%m-%d")


def select_age_group() -> str:
    """연령대 선택"""
    age_groups = list(AGE_GROUP_DISTRIBUTION.keys())
    weights = list(AGE_GROUP_DISTRIBUTION.values())
    return random.choices(age_groups, weights=weights, k=1)[0]


def generate_birth_date(age_group: str, customer_id: str = None) -> str:
    """
    age_group 기반 생년월일 생성 (재현성 보장)
    
    Args:
        age_group: 연령대 (예: "30대")
        customer_id: 고객 ID (재현성을 위한 시드용, 선택)
    
    Returns:
        생년월일 (YYYY-MM-DD 형식)
    """
    from datetime import date
    import hashlib
    
    # customer_id 기반 시드 생성 (재현성 보장)
    if customer_id:
        seed_value = int(hashlib.md5(customer_id.encode()).hexdigest()[:8], 16)
        local_random = random.Random(seed_value)
    else:
        local_random = random
    
    # 현재 연도 기준으로 연령대별 출생 연도 범위 계산
    current_year = date.today().year
    
    if age_group == "10대":
        birth_year = local_random.randint(current_year - 19, current_year - 10)
    elif age_group == "20대":
        birth_year = local_random.randint(current_year - 29, current_year - 20)
    elif age_group == "30대":
        birth_year = local_random.randint(current_year - 39, current_year - 30)
    elif age_group == "40대":
        birth_year = local_random.randint(current_year - 49, current_year - 40)
    elif age_group == "50대":
        birth_year = local_random.randint(current_year - 59, current_year - 50)
    elif age_group == "60대":
        birth_year = local_random.randint(current_year - 69, current_year - 60)
    elif age_group == "70대":
        birth_year = local_random.randint(current_year - 79, current_year - 70)
    else:
        # 기본값: 30대
        birth_year = local_random.randint(current_year - 39, current_year - 30)
    
    # 월일 생성 (간단하게 28일까지로 제한)
    month = local_random.randint(1, 12)
    day = local_random.randint(1, 28)
    
    return f"{birth_year}-{month:02d}-{day:02d}"


def generate_address(customer_id: str = None) -> str:
    """
    한국 주소 생성 (재현성 보장, 세분화된 주소)
    
    Args:
        customer_id: 고객 ID (재현성을 위한 시드용, 선택)
    
    Returns:
        주소 문자열 (예: "서울시 강남구 테헤란로 123")
    """
    import hashlib
    
    # customer_id 기반 시드 생성 (재현성 보장)
    if customer_id:
        seed_value = int(hashlib.md5(customer_id.encode()).hexdigest()[:8], 16)
        local_random = random.Random(seed_value)
    else:
        local_random = random
    
    # 시/도 목록 (인구 비중 고려)
    cities = [
        "서울시", "부산시", "대구시", "인천시", "광주시", "대전시", "울산시",
        "세종시", "수원시", "고양시", "용인시", "성남시", "부천시", "화성시",
        "안산시", "안양시", "평택시", "시흥시", "김포시", "의정부시", "광명시",
        "청주시", "천안시", "전주시", "포항시", "창원시", "제주시"
    ]
    
    # 시/도별 구/군/시 매핑 (실제 행정구역 구조)
    city_districts = {
        "서울시": [
            "강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구",
            "금천구", "노원구", "도봉구", "동대문구", "동작구", "마포구", "서대문구",
            "서초구", "성동구", "성북구", "송파구", "양천구", "영등포구", "용산구",
            "은평구", "종로구", "중구", "중랑구"
        ],
        "부산시": [
            "중구", "서구", "동구", "영도구", "부산진구", "동래구", "남구", "북구",
            "해운대구", "사하구", "금정구", "강서구", "연제구", "수영구", "사상구",
            "기장군"
        ],
        "대구시": [
            "중구", "동구", "서구", "남구", "북구", "수성구", "달서구", "달성군"
        ],
        "인천시": [
            "중구", "동구", "미추홀구", "연수구", "남동구", "부평구", "계양구",
            "서구", "강화군", "옹진군"
        ],
        "광주시": [
            "동구", "서구", "남구", "북구", "광산구"
        ],
        "대전시": [
            "동구", "중구", "서구", "유성구", "대덕구"
        ],
        "울산시": [
            "중구", "남구", "동구", "북구", "울주군"
        ],
        "수원시": [
            "영통구", "팔달구", "장안구", "권선구"
        ],
        "고양시": [
            "덕양구", "일산동구", "일산서구"
        ],
        "용인시": [
            "처인구", "기흥구", "수지구"
        ],
        "성남시": [
            "수정구", "중원구", "분당구"
        ],
        "부천시": [
            "원미구", "소사구", "오정구"
        ],
        "청주시": [
            "상당구", "서원구", "흥덕구", "청원구"
        ],
        "천안시": [
            "동남구", "서북구"
        ],
        "전주시": [
            "완산구", "덕진구"
        ],
        "포항시": [
            "남구", "북구"
        ],
        "창원시": [
            "의창구", "성산구", "마산합포구", "마산회원구", "진해구"
        ],
        "제주시": [
            "제주시", "서귀포시"
        ]
    }
    
    # 도로명 주소 패턴 (실제 도로명 주소 체계)
    street_patterns = {
        "서울시": [
            "테헤란로", "강남대로", "서초대로", "올림픽대로", "한강대로",
            "을지로", "종로", "명동길", "인사동길", "이태원로", "홍대입구로",
            "신촌로", "압구정로", "청담로", "삼성로", "봉은사로", "역삼로",
            "논현로", "선릉로", "도곡로", "개포로", "반포대로", "잠실로"
        ],
        "부산시": [
            "중앙대로", "해운대해변로", "광안해변로", "부산진로", "동래로",
            "남해고속도로", "경부고속도로", "수영로", "해운대로", "영도대로"
        ],
        "대구시": [
            "동대구로", "중앙대로", "달구벌대로", "수성못로", "팔공산로",
            "경부고속도로", "중앙고속도로", "칠곡로", "범어로"
        ],
        "인천시": [
            "송도대로", "인천대로", "경인고속도로", "영종대로", "중앙로",
            "송도국제대로", "연수대로", "남동대로"
        ],
        "광주시": [
            "충장로", "무등로", "상무대로", "첨단과기로", "하남대로"
        ],
        "대전시": [
            "유성대로", "대덕대로", "한밭대로", "도안대로", "계룡로"
        ],
        "울산시": [
            "번영로", "삼산로", "무거로", "신정로", "울산대로"
        ],
        "수원시": [
            "경수대로", "영통로", "팔달로", "장안로", "권선로"
        ],
        "고양시": [
            "중앙로", "화정로", "일산로", "백석로", "덕양로"
        ],
        "용인시": [
            "용인대로", "기흥로", "수지로", "처인로", "동백로"
        ],
        "성남시": [
            "분당로", "성남대로", "중앙로", "판교로", "정자로"
        ],
        "부천시": [
            "부천로", "원미로", "소사로", "오정로", "상동로"
        ],
        "청주시": [
            "상당로", "서원로", "흥덕로", "청원로", "오송로"
        ],
        "천안시": [
            "천안대로", "동남로", "서북로", "불당로"
        ],
        "전주시": [
            "완산로", "덕진로", "전주대로", "기린대로"
        ],
        "포항시": [
            "남구", "북구", "포항대로", "해안로"
        ],
        "창원시": [
            "중앙대로", "의창대로", "성산로", "마산대로", "진해대로"
        ],
        "제주시": [
            "연오로", "일주동로", "일주서로", "조천로"
        ]
    }
    
    # 기본 도로명 (시/도별 매핑이 없을 때)
    default_streets = [
        "중앙로", "대학로", "문화로", "평화로", "자유로", "번영로",
        "신흥로", "새마을로", "해안로", "산업로", "공단로", "테크노로"
    ]
    
    # 시/도 선택
    city = local_random.choice(cities)
    
    # 구/군/시 선택
    if city in city_districts:
        district = local_random.choice(city_districts[city])
    else:
        # 기본 구/군 목록
        default_districts = ["중구", "남구", "북구", "동구", "서구"]
        district = local_random.choice(default_districts)
    
    # 도로명 선택
    if city in street_patterns:
        street = local_random.choice(street_patterns[city])
    else:
        street = local_random.choice(default_streets)
    
    # 건물번호 생성 (1~999)
    building_number = local_random.randint(1, 999)
    
    return f"{city} {district} {street} {building_number}"


def select_gender() -> str:
    """성별 선택"""
    genders = list(GENDER_DISTRIBUTION.keys())
    weights = list(GENDER_DISTRIBUTION.values())
    return random.choices(genders, weights=weights, k=1)[0]


def select_grade() -> str:
    """고객 등급 선택"""
    grades = list(GRADE_DISTRIBUTION.keys())
    weights = list(GRADE_DISTRIBUTION.values())
    return random.choices(grades, weights=weights, k=1)[0]


def select_persona() -> str:
    """페르소나 선택"""
    persona_ids = list(PERSONAS.keys())
    weights = [PERSONAS[p]['ratio'] for p in persona_ids]
    return random.choices(persona_ids, weights=weights, k=1)[0]


def generate_korean_name(gender: str) -> str:
    """한국 이름 생성"""
    last_name = weighted_choice(LAST_NAMES)

    if gender == 'male':
        first_name = random.choice(MALE_FIRST_NAMES)
    else:
        first_name = random.choice(FEMALE_FIRST_NAMES)

    return f"{last_name}{first_name}"


def generate_llm_guidance(persona_id: str, name: str, grade: str) -> str:
    """LLM 가이던스 메시지 생성"""
    persona = PERSONAS[persona_id]
    base_guidance = persona['llm_guidance']

    # 등급별 추가 가이던스
    grade_suffix = ""
    if grade == 'VIP':
        grade_suffix = " VIP 고객이므로 최우선으로 응대해주세요."
    elif grade == 'GOLD':
        grade_suffix = " 우수 고객입니다."

    return f"{name} 고객님: {base_guidance}{grade_suffix}"


def adjust_persona_for_age(persona_id: str, age_group: str) -> str:
    """연령대에 따른 페르소나 조정"""
    # 60대, 70대는 이해부족형(S3) 비율 높임
    if age_group in ['60대', '70대'] and random.random() < 0.3:
        return 'S3'  # 이해부족형

    # 10대, 20대는 실용주의형(N1) 비율 높임
    if age_group in ['10대', '20대'] and random.random() < 0.2:
        return 'N1'  # 실용주의형

    return persona_id


def generate_customer(idx: int) -> Dict:
    """단일 고객 데이터 생성"""
    # 기본 정보
    customer_id = f"CUST-TEDDY-{idx:05d}"
    gender = select_gender()
    name = generate_korean_name(gender)
    phone = generate_phone_number()
    age_group = select_age_group()
    grade = select_grade()

    # 페르소나 선택 (연령대 조정 적용)
    persona_id = select_persona()
    persona_id = adjust_persona_for_age(persona_id, age_group)
    persona = PERSONAS[persona_id]

    # 카드 정보 (등급에 맞는 실제 카드 상품 선택)
    card_type = select_card_for_grade(grade)
    card_number_last4 = generate_card_number_last4()
    card_brand = random.choice(CARD_BRANDS)
    card_issue_date, card_expiry_date = generate_card_dates(customer_id)

    # LLM 가이던스 생성
    llm_guidance = generate_llm_guidance(persona_id, name, grade)

    # 생년월일 및 주소 생성 (재현성 보장을 위해 customer_id 전달)
    birth_date = generate_birth_date(age_group, customer_id)
    address = generate_address(customer_id)
    
    return {
        'id': customer_id,
        'name': name,
        'phone': phone,
        'gender': gender,
        'age_group': age_group,
        'birth_date': birth_date,
        'address': address,
        'grade': grade,
        'card_type': card_type,
        'card_number_last4': card_number_last4,
        'card_brand': card_brand,
        'card_issue_date': card_issue_date,
        'card_expiry_date': card_expiry_date,
        'current_type_code': persona_id,  # 현재 주요 유형 (N1, S1 등)
        'type_history': [],  # 유형 이력 (상담 후 업데이트됨)
        'personality_tags': persona['personality_tags'],
        'communication_style': persona['communication_style'],
        'customer_type_codes': [persona_id],  # 복합 유형 배열 (여러 특성 보유 시)
        'llm_guidance': llm_guidance,
        'total_consultations': 0,  # 나중에 재배정 스크립트에서 업데이트
        'resolved_first_call': 0,  # 나중에 FCR 계산 스크립트에서 업데이트
        'last_consultation_date': None,
        'created_at': datetime.now().isoformat(),
        'updated_at': None,
        '_persona_id': persona_id,  # 디버깅용 메타데이터
        '_persona_name': persona['name'],  # 디버깅용 메타데이터
    }


def validate_distribution(customers: List[Dict]) -> None:
    """분포 검증"""

    # 성별 분포
    gender_counts = {}
    for c in customers:
        gender = c['gender']
        gender_counts[gender] = gender_counts.get(gender, 0) + 1

    print("\n[성별 분포]")
    for gender, count in gender_counts.items():
        pct = count / len(customers) * 100
        expected = GENDER_DISTRIBUTION.get(gender, 0) * 100
        print(f"  {gender}: {count}명 ({pct:.1f}%) - 목표: {expected:.1f}%")

    # 연령대 분포
    age_counts = {}
    for c in customers:
        age = c['age_group']
        age_counts[age] = age_counts.get(age, 0) + 1

    print("\n[연령대 분포]")
    for age in ['10대', '20대', '30대', '40대', '50대', '60대', '70대']:
        count = age_counts.get(age, 0)
        pct = count / len(customers) * 100
        expected = AGE_GROUP_DISTRIBUTION.get(age, 0) * 100
        print(f"  {age}: {count}명 ({pct:.1f}%) - 목표: {expected:.1f}%")

    # 등급 분포
    grade_counts = {}
    for c in customers:
        grade = c['grade']
        grade_counts[grade] = grade_counts.get(grade, 0) + 1

    print("\n[등급 분포]")
    for grade in ['VIP', 'GOLD', 'SILVER', 'GENERAL']:
        count = grade_counts.get(grade, 0)
        pct = count / len(customers) * 100
        expected = GRADE_DISTRIBUTION.get(grade, 0) * 100
        print(f"  {grade}: {count}명 ({pct:.1f}%) - 목표: {expected:.1f}%")

    # 페르소나 분포
    persona_counts = {}
    for c in customers:
        pid = c['_persona_id']
        persona_counts[pid] = persona_counts.get(pid, 0) + 1

    print("\n[페르소나 분포]")
    for pid in sorted(PERSONAS.keys()):
        count = persona_counts.get(pid, 0)
        pct = count / len(customers) * 100
        expected = PERSONAS[pid]['ratio'] * 100
        name = PERSONAS[pid]['name']
        print(f"  {pid} ({name}): {count}명 ({pct:.1f}%) - 목표: {expected:.1f}%")


def migrate_existing_customers_data(input_file: Path, output_file: Path = None) -> None:
    """
    기존 customersData.json에 birth_date와 address 필드 추가 (마이그레이션)
    
    Args:
        input_file: 기존 customersData.json 경로
        output_file: 출력 파일 경로 (None이면 input_file 덮어쓰기)
    """
    if output_file is None:
        output_file = input_file
    
    print(f"\n[INFO] 기존 고객 데이터 마이그레이션 시작...")
    print(f"  입력 파일: {input_file}")
    print(f"  출력 파일: {output_file}")
    
    # 기존 데이터 로드
    if not input_file.exists():
        print(f"[ERROR] 파일을 찾을 수 없습니다: {input_file}")
        return
    
    with open(input_file, 'r', encoding='utf-8') as f:
        customers = json.load(f)
    
    print(f"[INFO] 총 {len(customers)}명의 고객 데이터 로드됨")
    
    # 각 고객에 birth_date와 address 추가
    updated_count = 0
    for customer in customers:
        # birth_date가 없으면 생성 (재현성 보장을 위해 customer_id 전달)
        if 'birth_date' not in customer or not customer.get('birth_date'):
            age_group = customer.get('age_group')
            customer_id = customer.get('id')
            if age_group:
                customer['birth_date'] = generate_birth_date(age_group, customer_id)
                updated_count += 1
            else:
                customer['birth_date'] = None
        
        # address가 없으면 생성 (재현성 보장을 위해 customer_id 전달)
        if 'address' not in customer or not customer.get('address'):
            customer_id = customer.get('id')
            customer['address'] = generate_address(customer_id)
            updated_count += 1

        # card_issue_date, card_expiry_date가 없으면 생성
        if 'card_issue_date' not in customer or not customer.get('card_issue_date'):
            customer_id = customer.get('id')
            issue_date, expiry_date = generate_card_dates(customer_id)
            customer['card_issue_date'] = issue_date
            customer['card_expiry_date'] = expiry_date
            updated_count += 1

        # customer_type_codes가 없으면 _persona_id 기반으로 생성
        if 'customer_type_codes' not in customer or not customer.get('customer_type_codes'):
            persona_id = customer.get('_persona_id')
            if persona_id:
                customer['customer_type_codes'] = [persona_id]
            else:
                customer['customer_type_codes'] = ['N1']  # 기본값
            updated_count += 1

        # current_type_code가 없으면 _persona_id 기반으로 생성
        if 'current_type_code' not in customer or not customer.get('current_type_code'):
            persona_id = customer.get('_persona_id')
            customer['current_type_code'] = persona_id if persona_id else 'N1'
            updated_count += 1

        # type_history가 없으면 빈 배열로 초기화
        if 'type_history' not in customer:
            customer['type_history'] = []
            updated_count += 1

    # 백업 파일 생성
    backup_file = input_file.parent / f"{input_file.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    print(f"[INFO] 백업 파일 생성: {backup_file}")
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(customers, f, ensure_ascii=False, indent=2)
    
    # 업데이트된 데이터 저장
    print(f"[INFO] 업데이트된 데이터 저장 중...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(customers, f, ensure_ascii=False, indent=2)
    
    print(f"[SUCCESS] 마이그레이션 완료!")
    print(f"  - 업데이트된 고객 수: {updated_count}명")
    print(f"  - 백업 파일: {backup_file}")
    print(f"  - 출력 파일: {output_file}")


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='고객 데이터 생성 또는 마이그레이션')
    parser.add_argument('--migrate', action='store_true', 
                       help='기존 customersData.json에 birth_date와 address 필드 추가 (마이그레이션)')
    parser.add_argument('--input', type=str, 
                       help='마이그레이션 입력 파일 경로 (기본값: customersData.json)')
    parser.add_argument('--output', type=str,
                       help='마이그레이션 출력 파일 경로 (기본값: 입력 파일과 동일)')
    
    args = parser.parse_args()
    
    # 마이그레이션 모드
    if args.migrate:
        input_file = Path(args.input) if args.input else CUSTOMERS_DATA_FILE
        output_file = Path(args.output) if args.output else None
        migrate_existing_customers_data(input_file, output_file)
        return
    
    # 일반 생성 모드
    print("=" * 60)
    print("고객 데이터 생성 스크립트")
    print("=" * 60)
    print(f"  랜덤 시드: 42 (재현성 보장 - 누가 돌려도 동일한 결과)")
    print(f"  대상 인원: {TOTAL_CUSTOMERS}명")
    print("=" * 60)

    print(f"\n[1단계] {TOTAL_CUSTOMERS}명의 고객 데이터 생성 중...")

    # 고객 데이터 생성
    customers = []
    for idx in range(1, TOTAL_CUSTOMERS + 1):
        customer = generate_customer(idx)
        customers.append(customer)

        if idx % 500 == 0:
            print(f"[INFO] {idx}/{TOTAL_CUSTOMERS}명 생성 완료")

    print(f"\n[1단계 완료] 총 {len(customers)}명 생성 완료")

    # 분포 검증
    print(f"\n[2단계] 분포 검증")
    validate_distribution(customers)

    # 데이터 디렉토리 생성
    data_dir = DB_DIR / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    # JSON 저장
    output_file = CUSTOMERS_DATA_FILE
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(customers, f, ensure_ascii=False, indent=2)

    print(f"\n[3단계 완료] 고객 데이터 저장")
    print(f"  저장 경로: {output_file}")

    # 샘플 출력
    print("\n[샘플 데이터 확인] (첫 3명)")
    for i, c in enumerate(customers[:3]):
        print(f"\n--- 고객 {i+1} ---")
        print(f"  ID: {c['id']}")
        print(f"  이름: {c['name']}")
        print(f"  전화번호: {c['phone']}")
        print(f"  성별: {c['gender']}")
        print(f"  연령대: {c['age_group']}")
        print(f"  생년월일: {c.get('birth_date', 'N/A')}")
        print(f"  주소: {c.get('address', 'N/A')}")
        print(f"  등급: {c['grade']}")
        print(f"  카드: {c['card_type']} ({c['card_brand']})")
        print(f"  카드발급일: {c.get('card_issue_date', 'N/A')}")
        print(f"  카드만료일: {c.get('card_expiry_date', 'N/A')}")
        print(f"  고객유형코드: {c.get('customer_type_codes', [])}")
        print(f"  페르소나: {c['_persona_name']} ({c['_persona_id']})")
        print(f"  LLM 가이던스: {c['llm_guidance']}")

    # 완료 메시지
    print("\n" + "=" * 60)
    print("✓ 고객 데이터 생성 완료")
    print("=" * 60)
    print("\n[다음 단계]")
    print("  python 08a_load_customers_to_db.py  # DB 적재")
    print("  python 08b_reassign_consultations.py  # 상담-고객 연결")
    print("\n[기존 데이터 마이그레이션]")
    print("  python 08_generate_customers_data.py --migrate  # birth_date, address 추가")
    print("")


if __name__ == "__main__":
    main()
