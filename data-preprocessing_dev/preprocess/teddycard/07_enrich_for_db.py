"""
07_enrich_for_db.py

DB 적재 전 데이터 보강 스크립트

전처리된 JSON 데이터를 DB 스키마에 맞게 보강:
1. notices: date → start_date, end_date 계산, category/priority 결정
2. card_products: annual_fee 파싱, brand 추출
3. service_guide_documents: document_source 추가

주의사항:
- 실제 데이터를 기반으로 매핑 규칙 적용
- LLM을 사용하여 category/priority 자동 분석
- 임의로 값을 만들지 않고 원본 데이터에서 추출
"""

import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
import sys
import os
from dotenv import load_dotenv

# 환경 변수 로드
BASE_DIR = Path(__file__).resolve().parents[3]  # call-act
load_dotenv(BASE_DIR / '.env', override=False)
load_dotenv(Path(__file__).parent / '.env', override=False)

# OpenAI 클라이언트 (LLM 분석용)
try:
    from openai import OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if OPENAI_API_KEY:
        llm_client = OpenAI(api_key=OPENAI_API_KEY)
        USE_LLM = True
    else:
        llm_client = None
        USE_LLM = False
except ImportError:
    llm_client = None
    USE_LLM = False

# 경로 설정
# 주의: 현재는 data-preprocessing_dev에서 작업, 나중에 data-preprocessing로 옮길 예정
# 옮길 때는 아래 경로를 BASE_DIR / "data-preprocessing" / "data" / "teddycard"로 변경
OUTPUT_DIR = BASE_DIR / "data-preprocessing_dev" / "data" / "teddycard"

# 태그 → 카테고리 매핑 (규칙 기반)
TAG_TO_CATEGORY_MAP = {
    "피해": "emergency",      # 금융사기 피해 관련
    "이벤트": "service",       # 프로모션, 이벤트
    "시스템": "system",        # 시스템 업데이트, 점검
    "교육": "service",         # 교육 관련
    "정책": "service",         # 정책 변경
    "근무": "system",          # 근무 일정
    "복지": "service",         # 복지 관련
    "긴급": "emergency",       # 긴급 공지
}

# 우선순위 결정 키워드
URGENT_KEYWORDS = ["긴급", "NOTICE 발령", "주의", "즉시", "피해", "사기"]
IMPORTANT_KEYWORDS = ["변경", "업데이트", "안내", "공지"]


def parse_notice_date(date_str: str) -> date:
    """'2025.12.03' 형식의 날짜를 date 객체로 변환"""
    try:
        return datetime.strptime(date_str, "%Y.%m.%d").date()
    except ValueError:
        # 다른 형식 시도
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            # 기본값: 오늘 날짜
            return date.today()


def calculate_end_date(start_date: date, content: str, priority: str = "normal") -> Optional[date]:
    """
    end_date 계산:
    1. content에서 종료일 추출 시도
    2. 없으면 기본값 사용 (긴급: 7일, 중요: 14일, 일반: 14일)
    """
    # content에서 날짜 패턴 찾기
    date_patterns = [
        r"(\d{4})\.(\d{1,2})\.(\d{1,2})까지",
        r"~(\d{4})\.(\d{1,2})\.(\d{1,2})",
        r"종료일.*?(\d{4})\.(\d{1,2})\.(\d{1,2})",
        r"(\d{4})-(\d{1,2})-(\d{1,2})까지",
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, content)
        if match:
            try:
                year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
                return date(year, month, day)
            except (ValueError, IndexError):
                continue
    
    # 기본값: priority에 따라 다르게 설정
    if priority == "urgent":
        return start_date + timedelta(days=7)  # 긴급: 1주일
    elif priority == "important":
        return start_date + timedelta(days=14)  # 중요: 2주일
    else:
        return start_date + timedelta(days=14)  # 일반: 2주일


def determine_notice_priority(title: str, content: str, tag: str) -> str:
    """
    우선순위 결정 (규칙 기반):
    - "긴급", "NOTICE 발령", "주의", "피해", "사기" → urgent
    - "변경", "업데이트" → important
    - 기타 → normal
    """
    text = f"{title} {content[:200]} {tag}".lower()
    
    if any(kw in text for kw in URGENT_KEYWORDS):
        return "urgent"
    elif any(kw in text for kw in IMPORTANT_KEYWORDS):
        return "important"
    else:
        return "normal"


def analyze_notice_category_with_llm(title: str, content: str, tag: str) -> Dict[str, str]:
    """
    LLM을 사용하여 notice의 category와 priority 결정
    tag가 없거나 불명확한 경우에만 사용
    """
    if not USE_LLM:
        # LLM 사용 불가 시 규칙 기반으로 fallback
        category = TAG_TO_CATEGORY_MAP.get(tag, "service")
        priority = determine_notice_priority(title, content, tag)
        return {"category": category, "priority": priority}
    
    try:
        prompt = f"""
다음 공지사항을 분석하여 카테고리와 우선순위를 결정하세요.

제목: {title}
태그: {tag}
내용: {content[:500]}

카테고리 선택지:
- system: 시스템 업데이트, 점검, 근무 일정 등
- service: 이벤트, 프로모션, 교육, 정책 변경 등
- emergency: 금융사기 피해, 긴급 공지, 보안 경고 등

우선순위 선택지:
- urgent: 긴급 공지, 즉시 조치 필요
- important: 중요 공지, 주의 필요
- normal: 일반 공지

JSON 형식으로 응답:
{{"category": "system|service|emergency", "priority": "urgent|important|normal"}}
"""
        
        response = llm_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        return {
            "category": result.get("category", "service"),
            "priority": result.get("priority", "normal")
        }
    except Exception as e:
        print(f"[WARNING] LLM 분석 실패: {e}, 규칙 기반으로 fallback")
        category = TAG_TO_CATEGORY_MAP.get(tag, "service")
        priority = determine_notice_priority(title, content, tag)
        return {"category": category, "priority": priority}


def determine_notice_status(start_date: date, end_date: Optional[date]) -> str:
    """
    status 결정:
    - 현재 날짜 < start_date → inactive (예정)
    - start_date <= 현재 날짜 <= end_date → active
    - 현재 날짜 > end_date → inactive (종료)
    """
    today = date.today()
    if today < start_date:
        return "inactive"  # 예정
    elif end_date and today > end_date:
        return "inactive"  # 종료
    else:
        return "active"


def parse_korean_number(text: str) -> Optional[int]:
    """
    한국어 숫자 → 정수 변환
    예: "2만 7천원" → 27000, "1만 5천원" → 15000
    """
    if not text or text in ["없음", "기본연회비", "기본 연회비"]:
        return None
    
    # 텍스트 정리
    text = text.replace('원', '').replace(',', '').replace(' ', '').strip()
    
    # "만" 단위 처리
    if '만' in text:
        parts = text.split('만')
        man_str = parts[0].strip()
        man = int(re.findall(r'\d+', man_str)[0]) if re.findall(r'\d+', man_str) else 0
        
        cheon = 0
        if len(parts) > 1:
            cheon_str = parts[1].strip()
            if '천' in cheon_str:
                cheon = int(re.findall(r'\d+', cheon_str)[0]) if re.findall(r'\d+', cheon_str) else 0
        
        return man * 10000 + cheon * 1000
    
    # "천" 단위만 있는 경우
    if '천' in text:
        cheon_str = text.replace('천', '').strip()
        cheon = int(re.findall(r'\d+', cheon_str)[0]) if re.findall(r'\d+', cheon_str) else 0
        return cheon * 1000
    
    # 숫자만 있는 경우 (예: "27000")
    numbers = re.findall(r'\d+', text)
    if numbers:
        return int(numbers[0])
    
    return None


def parse_annual_fee(fee_str: str, full_content: str) -> Optional[int]:
    """
    연회비 파싱:
    1. fee_str이 이미 파싱된 숫자면 그대로 사용
    2. "없음" → None
    3. "기본연회비" 또는 None → full_content에서 테이블 파싱
    4. 숫자 추출 (예: "2만 7천원" → 27000)
    """
    # fee_str이 이미 정수면 그대로 반환
    if isinstance(fee_str, int):
        return fee_str
    
    # fee_str이 문자열이고 숫자면 변환
    if fee_str and isinstance(fee_str, str):
        # 숫자만 있는 경우
        if fee_str.isdigit():
            return int(fee_str)
        # "없음"이면 None
        if fee_str in ["없음", "기본연회비", "기본 연회비"]:
            pass  # 아래 테이블 파싱 시도
        else:
            # 한국어 숫자 파싱 시도
            parsed = parse_korean_number(fee_str)
            if parsed:
                return parsed
    
    # full_content에서 연회비 테이블 파싱 시도
    # 패턴 1: | 국내전용 | Local | 2만 7천원 | ...
    patterns = [
        r'국내전용[^\n]*\|\s*Local[^\|]*\|\s*([^\|]+)',  # 국내전용 Local 행
        r'국내전용[^\n]*\|\s*([^\|]+)\s*\|\s*Local',     # 순서 다른 경우
        r'총\s*연회비[^\n]*\n[^\n]*\n\|\s*국내전용[^\|]*\|\s*([^\|]+)',  # 총연회비 헤더 있는 경우
    ]
    
    for pattern in patterns:
        match = re.search(pattern, full_content, re.MULTILINE)
        if match:
            fee_text = match.group(1).strip()
            parsed = parse_korean_number(fee_text)
            if parsed:
                return parsed
    
    return None


def extract_brand(full_content: str) -> Optional[str]:
    """
    브랜드 추출:
    - "Local" → "local"
    - "VISA" → "visa"
    - "Mastercard" → "mastercard"
    - "AMEX" → "amex"
    """
    content_upper = full_content.upper()
    
    if "LOCAL" in content_upper or "국내전용" in full_content:
        return "local"
    elif "VISA" in content_upper:
        return "visa"
    elif "MASTERCARD" in content_upper:
        return "mastercard"
    elif "AMEX" in content_upper or "AMERICAN EXPRESS" in content_upper:
        return "amex"
    elif "UNIONPAY" in content_upper or "유니온페이" in full_content:
        return "unionpay"
    
    return None


def enrich_notices(notices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """notices 데이터 보강"""
    enriched = []
    
    print(f"[INFO] notices 보강 중: {len(notices)}건")
    
    for idx, notice in enumerate(notices):
        # date → start_date
        date_str = notice.get("date", "")
        if not date_str:
            print(f"[WARNING] notice {notice.get('id')}에 date가 없습니다. 오늘 날짜 사용.")
            start_date = date.today()
        else:
            start_date = parse_notice_date(date_str)
        
        # category, priority 결정
        tag = notice.get("tag", "")
        title = notice.get("title", "")
        content = notice.get("content", "")
        
        if tag and tag in TAG_TO_CATEGORY_MAP:
            # 규칙 기반 매핑
            category = TAG_TO_CATEGORY_MAP[tag]
            priority = determine_notice_priority(title, content, tag)
        else:
            # LLM 분석 또는 기본값
            if USE_LLM and (not tag or tag not in TAG_TO_CATEGORY_MAP):
                llm_result = analyze_notice_category_with_llm(title, content, tag)
                category = llm_result["category"]
                priority = llm_result["priority"]
            else:
                category = TAG_TO_CATEGORY_MAP.get(tag, "service")
                priority = determine_notice_priority(title, content, tag)
        
        # end_date 계산
        end_date = calculate_end_date(start_date, content, priority)
        
        # status 결정
        status = determine_notice_status(start_date, end_date)
        
        enriched_notice = {
            **notice,
            "category": category,
            "priority": priority,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat() if end_date else None,
            "status": status,
            "is_pinned": False,  # 기본값
            "created_by": None,  # NULL 가능
        }
        
        # 원본 필드 제거 (DB에 저장하지 않음)
        enriched_notice.pop("date", None)
        enriched_notice.pop("tag", None)  # tag는 category로 변환되었으므로 제거
        
        enriched.append(enriched_notice)
        
        if (idx + 1) % 10 == 0:
            print(f"  진행: {idx + 1}/{len(notices)}")
    
    print(f"[INFO] notices 보강 완료: {len(enriched)}건")
    return enriched


def enrich_card_products(cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """card_products 데이터 보강"""
    enriched = []
    
    print(f"[INFO] card_products 보강 중: {len(cards)}건")
    
    for idx, card in enumerate(cards):
        # annual_fee 파싱 (국내/해외 분리)
        full_content = card.get("full_content", "")
        
        # 국내 연회비 파싱
        annual_fee_domestic = parse_annual_fee(
            card.get("annual_fee_domestic"),
            full_content
        )
        
        # 해외 연회비 파싱 (full_content에서 직접 추출)
        annual_fee_global = None
        if not annual_fee_global:
            # 해외겸용 행에서 연회비 추출
            global_patterns = [
                r'해외겸용[^\n]*\|\s*VISA[^\|]*\|\s*([^\|]+)',
                r'해외겸용[^\n]*\|\s*Mastercard[^\|]*\|\s*([^\|]+)',
                r'해외겸용[^\n]*\|\s*([^\|]+)\s*\|\s*VISA',
            ]
            for pattern in global_patterns:
                match = re.search(pattern, full_content, re.MULTILINE)
                if match:
                    fee_text = match.group(1).strip()
                    annual_fee_global = parse_korean_number(fee_text)
                    if annual_fee_global:
                        break
        
        # brand 추출
        brand = extract_brand(full_content)
        
        # brand가 없으면 테이블에서 추출 시도
        if not brand:
            brand_match = re.search(r'국내전용[^\n]*\|\s*(Local|VISA|Mastercard|AMEX)', full_content, re.IGNORECASE)
            if brand_match:
                brand_str = brand_match.group(1).upper()
                if brand_str == "LOCAL":
                    brand = "local"
                elif brand_str == "VISA":
                    brand = "visa"
                elif brand_str == "MASTERCARD":
                    brand = "mastercard"
                elif brand_str == "AMEX":
                    brand = "amex"
        
        # 해외겸용이 있으면 해외 브랜드도 확인
        if not brand or brand == "local":
            global_brand_match = re.search(r'해외겸용[^\n]*\|\s*(Local|VISA|Mastercard|AMEX)', full_content, re.IGNORECASE)
            if global_brand_match:
                brand_str = global_brand_match.group(1).upper()
                if brand_str == "VISA":
                    brand = "visa"
                elif brand_str == "MASTERCARD":
                    brand = "mastercard"
                elif brand_str == "AMEX":
                    brand = "amex"
        
        enriched_card = {
            **card,
            "annual_fee_domestic": annual_fee_domestic,
            "annual_fee_global": annual_fee_global if annual_fee_global else card.get("annual_fee_global"),
            "brand": brand,
            # full_content는 metadata에 저장 (DB에는 없음)
            "metadata": {
                **card.get("metadata", {}),
                "full_content": card.get("full_content", "")
            }
        }
        
        enriched.append(enriched_card)
        
        if (idx + 1) % 10 == 0:
            print(f"  진행: {idx + 1}/{len(cards)}")
    
    print(f"[INFO] card_products 보강 완료: {len(enriched)}건")
    return enriched


def enrich_service_guides(guides: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """service_guide_documents 데이터 보강"""
    enriched = []
    
    print(f"[INFO] service_guide_documents 보강 중: {len(guides)}건")
    
    for idx, guide in enumerate(guides):
        # document_source 추가
        document_source = guide.get("metadata", {}).get("original_source", "")
        
        enriched_guide = {
            **guide,
            "document_source": document_source,
            "priority": "normal",  # 기본값
            "usage_count": 0,  # 기본값
            "last_used": None,  # 기본값
        }
        
        enriched.append(enriched_guide)
        
        if (idx + 1) % 50 == 0:
            print(f"  진행: {idx + 1}/{len(guides)}")
    
    print(f"[INFO] service_guide_documents 보강 완료: {len(enriched)}건")
    return enriched


def main():
    """메인 함수"""
    print("=" * 80)
    print("DB 적재 전 데이터 보강 스크립트")
    print("=" * 80)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n[INFO] 출력 디렉토리: {OUTPUT_DIR}")
    print(f"[INFO] LLM 사용 가능: {USE_LLM}")
    
    # 1. notices 보강
    # 주의: 파일명은 teddycard로 통일 (서비스명: 테디카드)
    notices_file = OUTPUT_DIR / "teddycard_notices.json"
    print(f"\n[STEP 1] notices 보강")
    print(f"[INFO] 파일 경로 확인: {notices_file}")
    print(f"[INFO] 파일 존재 여부: {notices_file.exists()}")
    
    if notices_file.exists():
        with open(notices_file, 'r', encoding='utf-8') as f:
            notices = json.load(f)
        print(f"[INFO] 로드된 notices 수: {len(notices)}건")
        
        enriched_notices = enrich_notices(notices)
        
        output_file = OUTPUT_DIR / "teddycard_notices_enriched.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enriched_notices, f, ensure_ascii=False, indent=2)
        print(f"[INFO] 저장 완료: {output_file}")
    
    # 2. card_products 보강
    cards_file = OUTPUT_DIR / "teddycard_card_products.json"
    print(f"\n[STEP 2] card_products 보강")
    print(f"[INFO] 파일 경로 확인: {cards_file}")
    print(f"[INFO] 파일 존재 여부: {cards_file.exists()}")
    
    if cards_file.exists():
        with open(cards_file, 'r', encoding='utf-8') as f:
            cards = json.load(f)
        print(f"[INFO] 로드된 card_products 수: {len(cards)}건")
        
        enriched_cards = enrich_card_products(cards)
        
        output_file = OUTPUT_DIR / "teddycard_card_products_enriched.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enriched_cards, f, ensure_ascii=False, indent=2)
        print(f"[INFO] 저장 완료: {output_file} ({len(enriched_cards)}건)")
    else:
        print(f"[WARNING] 파일을 찾을 수 없습니다: {cards_file}")
    
    # 3. service_guide_documents 보강 (각 소스별)
    guide_files = [
        OUTPUT_DIR / "teddycard_service_guides_samsung.json",
        OUTPUT_DIR / "teddycard_service_guides_hyundai.json",
        OUTPUT_DIR / "teddycard_service_guides_shinhan.json",
        OUTPUT_DIR / "teddycard_service_guides_special.json",
    ]
    
    all_enriched_guides = []
    for guide_file in guide_files:
        if guide_file.exists():
            print(f"\n[STEP 3] service_guide_documents 보강: {guide_file.name}")
            with open(guide_file, 'r', encoding='utf-8') as f:
                guides = json.load(f)
            
            enriched_guides = enrich_service_guides(guides)
            all_enriched_guides.extend(enriched_guides)
    
    if all_enriched_guides:
        output_file = OUTPUT_DIR / "teddycard_service_guides_enriched.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_enriched_guides, f, ensure_ascii=False, indent=2)
        print(f"[INFO] 저장 완료: {output_file} (총 {len(all_enriched_guides)}건)")
    
    print("\n" + "=" * 80)
    print("데이터 보강 완료")
    print("=" * 80)
    print("\n다음 단계:")
    print("1. 06_generate_embeddings.py 실행하여 임베딩 생성")
    print("2. DB 적재 스크립트 실행")


if __name__ == "__main__":
    main()
