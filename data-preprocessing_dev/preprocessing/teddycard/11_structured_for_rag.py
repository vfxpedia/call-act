"""
테디카드 통합 전처리 - RAG 검색 성능 개선을 위한 구조화 데이터 생성

프론트엔드가 필요로 하는 구조화된 형식을 전처리 단계에서 미리 생성
- service_guide_documents: 문서 타입별 다른 structured 형식 (workflow/information)
- card_products: 카드 정보 형식 structured 생성
- notices: structured 제거 (RAG 검색 미사용)
- 키워드 사전 활용하여 문서 타입 분류 정확도 향상
- LLM을 사용하여 자동 구조화 (프롬프트 기반)
"""

import json
import os
import re
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# 설정 파일 로드
from config import (
    PROJECT_ROOT, OUTPUT_DIR, SERVICE_GUIDES_FILES, NOTICES_FILE,
    EMBEDDING_CONFIG, LLM_CONFIG, STRUCTURE_CONFIG, KEYWORDS_DICT_FILE
)

# 환경 변수 로드 (API 키만 .env에서)
load_dotenv(PROJECT_ROOT / '.env', override=False)

# OpenAI 클라이언트
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

# 경로 설정 (config에서 가져옴)
INPUT_DIR = OUTPUT_DIR

# LLM 설정 (config에서 가져옴)
LLM_MODEL = LLM_CONFIG["model"]
REQUEST_DELAY = EMBEDDING_CONFIG["request_delay"]

# 병렬 처리 설정 (config에서 가져옴, 환경 변수로 오버라이드 가능)
USE_PARALLEL = os.getenv("STRUCTURE_USE_PARALLEL", str(STRUCTURE_CONFIG["use_parallel"])).lower() == "true"
MAX_WORKERS = int(os.getenv("STRUCTURE_MAX_WORKERS", str(STRUCTURE_CONFIG["max_workers"])))

# Rate limit 관리 (config에서 가져옴)
RATE_LIMIT_PER_MINUTE = STRUCTURE_CONFIG["rate_limit_per_minute"]
rate_limit_lock = threading.Lock()
rate_limit_count = 0
rate_limit_reset_time = time.time()

# 키워드 사전 로드
KEYWORDS_DICT = {}
if KEYWORDS_DICT_FILE.exists():
    with open(KEYWORDS_DICT_FILE, 'r', encoding='utf-8') as f:
        KEYWORDS_DICT = json.load(f)
    print(f"[INFO] 키워드 사전 로드 완료: {len(KEYWORDS_DICT)}개 카테고리")
else:
    print(f"[WARNING] 키워드 사전 파일을 찾을 수 없습니다: {KEYWORDS_DICT_FILE}")


def extract_system_path_from_content(content: str) -> str:
    """
    content에서 시스템 경로 추출 (규칙 기반)
    예: "고객관리 > 카드관리 > 분실신고"
    """
    # 패턴 1: "시스템 > ..." 또는 "고객관리 > ..." 형식
    pattern1 = re.search(r'(시스템|고객관리|카드관리|상담관리|결제관리|대출관리)\s*>\s*[^\n]+', content)
    if pattern1:
        return pattern1.group(0).strip()
    
    # 패턴 2: 카테고리 기반 추정
    if "분실" in content or "도난" in content:
        return "고객관리 > 카드관리 > 분실신고"
    elif "재발급" in content:
        return "카드관리 > 재발급관리"
    elif "한도" in content:
        return "카드관리 > 한도관리"
    elif "연체" in content or "이자" in content:
        return "결제관리 > 연체관리"
    elif "포인트" in content or "마일리지" in content:
        return "카드관리 > 포인트관리"
    elif "해외" in content:
        return "카드관리 > 해외이용"
    
    return "시스템 > 일반"


def extract_required_checks(content: str) -> List[str]:
    """
    content에서 필수 확인 사항 추출 (규칙 기반)
    """
    checks = []
    
    # 패턴 1: "✓" 또는 "•"로 시작하는 항목
    pattern1 = re.findall(r'[✓•]\s*([^\n]+)', content)
    checks.extend([c.strip() for c in pattern1 if c.strip()])
    
    # 패턴 2: "본인 확인" 관련
    if "본인" in content or "확인" in content:
        if "주민번호" in content:
            checks.append("본인 확인: 주민번호 뒷자리 4자리 필수")
        elif "생년월일" in content:
            checks.append("본인 확인: 생년월일 확인")
        elif "전화번호" in content:
            checks.append("본인 확인: 전화번호 확인")
    
    # 패턴 3: "필수" 또는 "반드시" 관련
    pattern3 = re.findall(r'(필수|반드시)[^\n]*([^\n]+)', content)
    for match in pattern3:
        checks.append(f"✓ {match[1].strip()}")
    
    return checks[:5]  # 최대 5개


def extract_exceptions(content: str) -> List[str]:
    """
    content에서 예외 사항 추출 (규칙 기반)
    """
    exceptions = []
    
    # 패턴 1: "⚠️" 또는 "※"로 시작하는 항목
    pattern1 = re.findall(r'[⚠️※]\s*([^\n]+)', content)
    exceptions.extend([e.strip() for e in pattern1 if e.strip()])
    
    # 패턴 2: "예외" 또는 "제외" 관련
    pattern2 = re.findall(r'(예외|제외)[^\n]*([^\n]+)', content)
    for match in pattern2:
        exceptions.append(f"⚠️ {match[1].strip()}")
    
    return exceptions[:3]  # 최대 3개


def extract_regulation(content: str) -> str:
    """
    content에서 규정/약관 정보 추출
    """
    # 패턴 1: "제N조" 형식
    pattern1 = re.search(r'제\d+조[^\n]*', content)
    if pattern1:
        return pattern1.group(0).strip()
    
    # 패턴 2: "약관" 관련
    pattern2 = re.search(r'[^\n]*(약관|규정|법률)[^\n]*', content)
    if pattern2:
        return pattern2.group(0).strip()
    
    return ""


def classify_document_type(doc: Dict[str, Any]) -> str:
    """
    문서 타입 분류: 'workflow' (업무 처리) 또는 'information' (정보 제공)
    키워드 사전을 활용하여 분류 정확도 향상
    """
    title = doc.get("title", "").lower()
    content = doc.get("content", "") or doc.get("text", "")
    content_lower = content.lower() if content else ""
    category = doc.get("category", "").lower()
    doc_keywords = doc.get("keywords", [])
    
    # 키워드 사전에서 업무 처리 관련 카테고리 추출
    workflow_score = 0
    info_score = 0
    
    if KEYWORDS_DICT:
        for cat, keywords in KEYWORDS_DICT.items():
            cat_lower = cat.lower()
            # 업무 처리 관련 카테고리
            if any(kw in cat_lower for kw in ["분실", "재발급", "정지", "신청", "결제", "변경", "해지"]):
                # 문서의 키워드와 사전 키워드 매칭
                matched = sum(1 for kw in doc_keywords if any(kw.lower() in dict_kw.lower() for dict_kw in keywords))
                workflow_score += matched * 2  # 키워드 매칭은 가중치 2배
            # 정보 제공 관련 카테고리
            elif any(kw in cat_lower for kw in ["혜택", "이용", "가이드", "안내", "용어", "선택", "방법", "활용"]):
                matched = sum(1 for kw in doc_keywords if any(kw.lower() in dict_kw.lower() for dict_kw in keywords))
                info_score += matched * 2
    
    # 기본 키워드 매칭
    workflow_keywords = ["분실", "신고", "재발급", "정지", "처리", "절차", "신청", "해지", "변경", "결제"]
    info_keywords = ["혜택", "이용", "가이드", "안내", "용어", "선택", "방법", "활용", "관리", "포인트"]
    
    workflow_score += sum(1 for kw in workflow_keywords if kw in title or kw in content_lower)
    info_score += sum(1 for kw in info_keywords if kw in title or kw in content_lower)
    
    # document_type 기반 판단
    doc_type = doc.get("document_type", "").lower()
    if "terms" in doc_type or "faq" in doc_type or "usage_guide" in doc_type:
        info_score += 2
    elif "service_guide" in doc_type:
        workflow_score += 1
    
    if workflow_score > info_score:
        return "workflow"
    elif info_score > workflow_score:
        return "information"
    else:
        # category 기반 판단
        if any(kw in category for kw in ["분실", "재발급", "정지", "신청", "결제"]):
            return "workflow"
        else:
            return "information"


def extract_time_estimate(content: str) -> str:
    """
    content에서 처리 시간 추정
    """
    # 패턴 1: "약 N분" 또는 "N-N분"
    pattern1 = re.search(r'약?\s*(\d+)\s*[-~]?\s*(\d+)?\s*분', content)
    if pattern1:
        if pattern1.group(2):
            return f"처리 시간: 약 {pattern1.group(1)}-{pattern1.group(2)}분"
        else:
            return f"처리 시간: 약 {pattern1.group(1)}분"
    
    # 패턴 2: "즉시" 또는 "실시간"
    if "즉시" in content or "실시간" in content:
        return "처리 시간: 즉시"
    
    # 기본값
    return "처리 시간: 약 3-5분"


def check_rate_limit():
    """Rate limit 체크 및 대기 (Thread-safe)"""
    global rate_limit_count, rate_limit_reset_time
    
    with rate_limit_lock:
        current_time = time.time()
        
        # 1분 경과 시 카운터 리셋
        if current_time - rate_limit_reset_time >= 60:
            rate_limit_count = 0
            rate_limit_reset_time = current_time
        
        # Rate limit 초과 시 대기
        if rate_limit_count >= RATE_LIMIT_PER_MINUTE:
            wait_time = 60 - (current_time - rate_limit_reset_time)
            if wait_time > 0:
                time.sleep(wait_time)
                rate_limit_count = 0
                rate_limit_reset_time = time.time()
        
        rate_limit_count += 1


def extract_full_terms(content: str) -> str:
    """
    content에서 약관 전문 추출 (제N조 형식으로 시작하는 긴 텍스트)
    """
    # 패턴: "제1조" 또는 "제1장"으로 시작하는 긴 텍스트 블록
    pattern = re.search(r'(제\d+[조장]\s*\([^)]+\)[^\n]*\n(?:[^\n]+\n){10,})', content, re.MULTILINE)
    if pattern:
        return pattern.group(0).strip()[:2000]  # 최대 2000자
    
    # 패턴 2: "약관" 키워드 주변 텍스트
    pattern2 = re.search(r'([^\n]*(?:약관|규정|법률)[^\n]*\n(?:[^\n]+\n){5,})', content)
    if pattern2:
        return pattern2.group(0).strip()[:2000]
    
    return ""


def generate_workflow_structured_with_llm(title: str, content: str) -> Optional[Dict[str, Any]]:
    """
    업무 처리 형식 structured 필드 생성 (LLM)
    """
    if not USE_LLM:
        return None
    
    check_rate_limit()
    
    try:
        full_terms = extract_full_terms(content)
        content_preview = content[:2000]
        
        prompt = f"""
다음 카드 상담 업무 처리 가이드 문서를 프론트엔드 칸반보드 형식으로 구조화하세요.

제목: {title}
내용: {content_preview}
약관 전문: {full_terms[:1000] if full_terms else "없음"}

다음 JSON 형식으로 응답하세요:
{{
  "title": "문서 제목 (간결하게)",
  "content": "핵심 내용 요약 (1-2문장)",
  "systemPath": "시스템 경로 (예: 고객관리 > 카드관리 > 분실신고)",
  "requiredChecks": ["필수 확인 사항 1", "필수 확인 사항 2", ...],
  "exceptions": ["예외 사항 1", "예외 사항 2", ...],
  "regulation": "관련 규정/약관 (예: 카드업무 취급요령 제34조)",
  "detailContent": "상세 내용 (원본 내용의 핵심 부분, 1000자 이내)",
  "fullTerms": "약관 전문 (있는 경우만, 2000자 이내)",
  "time": "처리 시간 (예: 약 3-5분)",
  "note": "추가 안내 사항 (있으면)"
}}

요구사항:
1. title: 원본 제목을 간결하게 요약
2. content: 핵심 내용을 1-2문장으로 요약
3. systemPath: 카드 상담 시스템의 메뉴 경로 형식
4. requiredChecks: 상담사가 반드시 확인해야 할 사항 (최대 5개)
5. exceptions: 특별한 경우나 주의사항 (최대 3개)
6. regulation: 관련 규정이나 약관 조항
7. detailContent: 원본 내용의 핵심 부분 (1000자 이내)
8. fullTerms: 약관 전문이 있으면 포함 (2000자 이내, 없으면 빈 문자열)
9. time: 예상 처리 시간
10. note: 추가 안내 (없으면 빈 문자열)

JSON 형식으로만 응답하세요.
"""
        
        response = llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "당신은 카드 상담 가이드 구조화 전문가입니다. JSON 형식으로만 응답하세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=LLM_CONFIG["temperature"],
            max_tokens=2000  # detailContent, fullTerms 포함하여 증가
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # JSON 파싱
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        result = json.loads(response_text)
        # fullTerms가 없으면 빈 문자열로 설정
        if "fullTerms" not in result:
            result["fullTerms"] = full_terms[:2000] if full_terms else ""
        return result
    
    except Exception as e:
        print(f"[WARNING] LLM 구조화 실패: {e}")
        return None


def generate_information_structured_with_llm(title: str, content: str) -> Optional[Dict[str, Any]]:
    """
    정보 제공 형식 structured 필드 생성 (LLM)
    """
    if not USE_LLM:
        return None
    
    check_rate_limit()
    
    try:
        full_terms = extract_full_terms(content)
        content_preview = content[:2000]
        
        prompt = f"""
다음 카드 정보 제공 문서를 정보 제공 형식으로 구조화하세요.

제목: {title}
내용: {content_preview}
약관 전문: {full_terms[:1000] if full_terms else "없음"}

다음 JSON 형식으로 응답하세요:
{{
  "title": "문서 제목 (간결하게)",
  "content": "핵심 내용 요약 (1-2문장)",
  "keyPoints": ["핵심 포인트 1", "핵심 포인트 2", ...],
  "benefits": ["혜택 1", "혜택 2", ...],
  "usageGuide": "이용 방법 안내",
  "relatedTopics": ["관련 주제 1", "관련 주제 2", ...],
  "detailContent": "상세 내용 (원본 내용의 핵심 부분, 1000자 이내)",
  "fullTerms": "약관 전문 (있는 경우만, 2000자 이내)",
  "note": "추가 안내 사항 (있으면)"
}}

요구사항:
1. title: 원본 제목을 간결하게 요약
2. content: 핵심 내용을 1-2문장으로 요약
3. keyPoints: 핵심 포인트 리스트 (최대 5개)
4. benefits: 혜택 리스트 (최대 5개, 혜택이 없는 경우 빈 배열)
5. usageGuide: 이용 방법 안내 (간단한 설명)
6. relatedTopics: 관련 주제 리스트 (최대 5개)
7. detailContent: 원본 내용의 핵심 부분 (1000자 이내)
8. fullTerms: 약관 전문이 있으면 포함 (2000자 이내, 없으면 빈 문자열)
9. note: 추가 안내 (없으면 빈 문자열)

JSON 형식으로만 응답하세요.
"""
        
        response = llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "당신은 카드 정보 구조화 전문가입니다. JSON 형식으로만 응답하세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=LLM_CONFIG["temperature"],
            max_tokens=2000
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # JSON 파싱
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        result = json.loads(response_text)
        # fullTerms가 없으면 빈 문자열로 설정
        if "fullTerms" not in result:
            result["fullTerms"] = full_terms[:2000] if full_terms else ""
        return result
    
    except Exception as e:
        print(f"[WARNING] LLM 구조화 실패: {e}")
        return None


def generate_card_info_structured_with_llm(card: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    카드 정보 형식 structured 필드 생성 (LLM)
    """
    if not USE_LLM:
        return None
    
    check_rate_limit()
    
    try:
        card_name = card.get("name", "")
        main_benefits = card.get("main_benefits", "")
        full_content = card.get("full_content", "")
        annual_fee_domestic = card.get("annual_fee_domestic", "")
        annual_fee_global = card.get("annual_fee_global", "")
        performance_condition = card.get("performance_condition", "")
        card_type = card.get("card_type", "")
        
        full_terms = extract_full_terms(full_content)
        
        prompt = f"""
다음 카드 상품 정보를 카드 정보 형식으로 구조화하세요.

카드명: {card_name}
카드 타입: {card_type}
연회비 (국내): {annual_fee_domestic}
연회비 (해외): {annual_fee_global}
실적 조건: {performance_condition}
주요 혜택: {main_benefits[:1000]}
전체 내용: {full_content[:2000]}
약관 전문: {full_terms[:1000] if full_terms else "없음"}

다음 JSON 형식으로 응답하세요:
{{
  "cardName": "카드명",
  "cardType": "신용카드 또는 체크카드",
  "annualFee": {{
    "domestic": "국내 연회비 (예: 27,000원)",
    "global": "해외 연회비 (예: 30,000원)"
  }},
  "mainBenefits": ["주요 혜택 1", "주요 혜택 2", ...],
  "benefitDetails": {{
    "pointAccrual": "포인트 적립률 (예: 5%)",
    "conditions": "적립 조건 (예: 전월 30만원 이상 이용 시)",
    "limit": "적립 한도 (예: 월 1만~3만 포인트)"
  }},
  "performanceConditions": "실적 조건",
  "usageGuide": "이용 방법 안내",
  "detailContent": "상세 내용 (1000자 이내)",
  "fullTerms": "약관 전문 (있는 경우만, 2000자 이내)",
  "note": "추가 안내 (있으면)"
}}

요구사항:
1. cardName: 카드명 그대로 사용
2. cardType: "신용카드" 또는 "체크카드"
3. annualFee: 연회비 정보 (없으면 null)
4. mainBenefits: 주요 혜택 리스트 (최대 5개)
5. benefitDetails: 혜택 상세 정보 (포인트 적립률, 조건, 한도 등)
6. performanceConditions: 실적 조건
7. usageGuide: 이용 방법 안내
8. detailContent: 상세 내용 (1000자 이내)
9. fullTerms: 약관 전문이 있으면 포함 (2000자 이내, 없으면 빈 문자열)
10. note: 추가 안내 (없으면 빈 문자열)

JSON 형식으로만 응답하세요.
"""
        
        response = llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "당신은 카드 상품 정보 구조화 전문가입니다. JSON 형식으로만 응답하세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=LLM_CONFIG["temperature"],
            max_tokens=2000
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # JSON 파싱
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        result = json.loads(response_text)
        # fullTerms가 없으면 빈 문자열로 설정
        if "fullTerms" not in result:
            result["fullTerms"] = full_terms[:2000] if full_terms else ""
        return result
    
    except Exception as e:
        print(f"[WARNING] LLM 구조화 실패: {e}")
        return None


def generate_structured_with_llm(title: str, content: str, doc_type: str, structured_type: str = "workflow") -> Optional[Dict[str, Any]]:
    """
    LLM을 사용하여 구조화된 데이터 생성 (문서 타입별)
    """
    if structured_type == "workflow":
        return generate_workflow_structured_with_llm(title, content)
    elif structured_type == "information":
        return generate_information_structured_with_llm(title, content)
    else:
        return None


def generate_workflow_structured_rule_based(title: str, content: str) -> Dict[str, Any]:
    """
    업무 처리 형식 규칙 기반 구조화 (LLM 실패 시 fallback)
    """
    full_terms = extract_full_terms(content)
    return {
        "title": title[:100] if title else "카드 상담 가이드",
        "content": content[:200] if content else "",
        "systemPath": extract_system_path_from_content(content),
        "requiredChecks": extract_required_checks(content),
        "exceptions": extract_exceptions(content),
        "regulation": extract_regulation(content),
        "detailContent": content[:1000] if content else "",
        "fullTerms": full_terms[:2000] if full_terms else "",
        "time": extract_time_estimate(content),
        "note": ""
    }


def generate_information_structured_rule_based(title: str, content: str) -> Dict[str, Any]:
    """
    정보 제공 형식 규칙 기반 구조화 (LLM 실패 시 fallback)
    """
    full_terms = extract_full_terms(content)
    
    # keyPoints 추출 (번호나 불릿으로 시작하는 항목)
    key_points = []
    lines = content.split('\n')
    for line in lines[:20]:  # 처음 20줄만 확인
        line = line.strip()
        if re.match(r'^[•\-\d+\.]\s+', line) or re.match(r'^[①②③④⑤]', line):
            point = re.sub(r'^[•\-\d+\.\s①②③④⑤]+', '', line).strip()
            if point and len(point) > 5:
                key_points.append(point)
                if len(key_points) >= 5:
                    break
    
    # benefits 추출 (혜택, 할인, 적립 관련)
    benefits = []
    benefit_keywords = ["혜택", "할인", "적립", "포인트", "마일리지", "캐시백"]
    for line in lines[:30]:
        line_lower = line.lower()
        if any(kw in line_lower for kw in benefit_keywords) and len(line.strip()) > 10:
            benefits.append(line.strip()[:100])
            if len(benefits) >= 5:
                break
    
    return {
        "title": title[:100] if title else "카드 정보 가이드",
        "content": content[:200] if content else "",
        "keyPoints": key_points[:5] if key_points else ["정보 제공 문서"],
        "benefits": benefits[:5] if benefits else [],
        "usageGuide": content[:300] if content else "",
        "relatedTopics": [],
        "detailContent": content[:1000] if content else "",
        "fullTerms": full_terms[:2000] if full_terms else "",
        "note": ""
    }


def generate_card_info_structured_rule_based(card: Dict[str, Any]) -> Dict[str, Any]:
    """
    카드 정보 형식 규칙 기반 구조화 (LLM 실패 시 fallback)
    """
    card_name = card.get("name", "")
    main_benefits = card.get("main_benefits", "")
    full_content = card.get("full_content", "")
    annual_fee_domestic = card.get("annual_fee_domestic", "")
    annual_fee_global = card.get("annual_fee_global", "")
    performance_condition = card.get("performance_condition", "")
    card_type = card.get("card_type", "")
    
    full_terms = extract_full_terms(full_content)
    
    # main_benefits에서 혜택 추출
    benefits = []
    if main_benefits:
        lines = main_benefits.split('\n')[:10]
        for line in lines:
            line = line.strip()
            if line and len(line) > 10 and not line.startswith('#'):
                benefits.append(line[:100])
                if len(benefits) >= 5:
                    break
    
    # benefitDetails 추출 (포인트, 할인률 등)
    benefit_details = {}
    if "%" in main_benefits or "포인트" in main_benefits:
        point_match = re.search(r'(\d+)%', main_benefits)
        if point_match:
            benefit_details["pointAccrual"] = f"{point_match.group(1)}%"
    
    return {
        "cardName": card_name,
        "cardType": "신용카드" if card_type == "credit" else "체크카드",
        "annualFee": {
            "domestic": str(annual_fee_domestic) if annual_fee_domestic else None,
            "global": str(annual_fee_global) if annual_fee_global else None
        },
        "mainBenefits": benefits[:5] if benefits else [main_benefits[:200] if main_benefits else ""],
        "benefitDetails": benefit_details if benefit_details else {
            "pointAccrual": "",
            "conditions": "",
            "limit": ""
        },
        "performanceConditions": performance_condition or "",
        "usageGuide": main_benefits[:300] if main_benefits else "",
        "detailContent": full_content[:1000] if full_content else "",
        "fullTerms": full_terms[:2000] if full_terms else "",
        "note": ""
    }


def generate_structured_rule_based(title: str, content: str, doc_type: str, structured_type: str = "workflow", card: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    규칙 기반 구조화 (LLM 실패 시 fallback)
    """
    if structured_type == "card_info" and card:
        return generate_card_info_structured_rule_based(card)
    elif structured_type == "information":
        return generate_information_structured_rule_based(title, content)
    else:
        return generate_workflow_structured_rule_based(title, content)


def process_single_document(doc: Dict[str, Any], doc_type: str = "service_guide") -> Dict[str, Any]:
    """단일 문서 구조화 (병렬 처리용)"""
    title = doc.get("title") or doc.get("id", "")
    content = doc.get("content") or doc.get("text", "")
    
    if not content:
        doc["structured"] = None
        return doc
    
    # 문서 타입 분류 (workflow vs information)
    structured_type = classify_document_type(doc)
    
    # LLM 구조화 시도
    structured = None
    if USE_LLM:
        structured = generate_structured_with_llm(title, content, doc_type, structured_type)
        time.sleep(REQUEST_DELAY)
    
    # LLM 실패 시 규칙 기반
    if not structured:
        structured = generate_structured_rule_based(title, content, doc_type, structured_type)
    
    doc["structured"] = structured
    doc["structured_type"] = structured_type  # 메타데이터로 저장
    return doc


def process_single_card(card: Dict[str, Any]) -> Dict[str, Any]:
    """단일 카드 정보 구조화 (병렬 처리용)"""
    card_name = card.get("name", "")
    main_benefits = card.get("main_benefits", "")
    full_content = card.get("full_content", "")
    content = main_benefits or full_content
    
    if not content:
        card["structured"] = None
        return card
    
    # LLM 구조화 시도
    structured = None
    if USE_LLM:
        structured = generate_card_info_structured_with_llm(card)
        time.sleep(REQUEST_DELAY)
    
    # LLM 실패 시 규칙 기반
    if not structured:
        structured = generate_card_info_structured_rule_based(card)
    
    card["structured"] = structured
    card["structured_type"] = "card_info"  # 메타데이터로 저장
    return card


def process_service_guides():
    """service_guide_documents 파일들 처리 (순차 처리)"""
    all_updated = []
    
    for filename in SERVICE_GUIDES_FILES:
        file_path = INPUT_DIR / filename
        if not file_path.exists():
            print(f"[WARNING] 파일을 찾을 수 없습니다: {file_path}")
            continue
        
        print(f"\n[INFO] 처리 중: {filename} (순차 처리)")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            documents = json.load(f)
        
        updated_docs = []
        for doc in tqdm(documents, desc=f"구조화 중 ({filename})"):
            updated_doc = process_single_document(doc, "service_guide")
            updated_docs.append(updated_doc)
        
        # 기존 파일에 structured 필드 추가하여 저장 (덮어쓰기)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(updated_docs, f, ensure_ascii=False, indent=2)
        
        print(f"[INFO] 저장 완료: {file_path} ({len(updated_docs)}개 문서)")
        all_updated.append((filename, len(updated_docs)))
    
    return all_updated


def process_service_guides_parallel():
    """service_guide_documents 파일들 병렬 처리"""
    all_updated = []
    
    for filename in SERVICE_GUIDES_FILES:
        file_path = INPUT_DIR / filename
        if not file_path.exists():
            print(f"[WARNING] 파일을 찾을 수 없습니다: {file_path}")
            continue
        
        print(f"\n[INFO] 처리 중: {filename} (병렬 처리: {MAX_WORKERS} workers)")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            documents = json.load(f)
        
        # 원본 순서 유지를 위한 ID 매핑
        doc_id_map = {i: doc.get("id", f"doc_{i}") for i, doc in enumerate(documents)}
        
        updated_docs = [None] * len(documents)  # 순서 유지를 위한 리스트
        
        # 병렬 처리
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # 모든 문서를 병렬로 처리
            future_to_index = {
                executor.submit(process_single_document, doc, "service_guide"): i
                for i, doc in enumerate(documents)
            }
            
            # 완료된 작업부터 수집
            for future in tqdm(as_completed(future_to_index), 
                             total=len(documents), 
                             desc=f"구조화 중 ({filename})"):
                index = future_to_index[future]
                try:
                    updated_doc = future.result()
                    updated_docs[index] = updated_doc
                except Exception as e:
                    print(f"[ERROR] 문서 처리 실패 (index {index}): {e}")
                    # 실패한 문서는 규칙 기반으로 처리
                    doc = documents[index]
                    structured = generate_structured_rule_based(
                        doc.get("title") or doc.get("id", ""),
                        doc.get("content") or doc.get("text", ""),
                        "service_guide"
                    )
                    doc["structured"] = structured
                    updated_docs[index] = doc
        
        # 기존 파일에 structured 필드 추가하여 저장 (덮어쓰기)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(updated_docs, f, ensure_ascii=False, indent=2)
        
        print(f"[INFO] 저장 완료: {file_path} ({len(updated_docs)}개 문서)")
        all_updated.append((filename, len(updated_docs)))
    
    return all_updated


def process_card_products():
    """card_products 파일 처리"""
    card_products_file = "teddycard_card_products.json"
    file_path = INPUT_DIR / card_products_file
    if not file_path.exists():
        print(f"[WARNING] 파일을 찾을 수 없습니다: {file_path}")
        return []
    
    print(f"\n[INFO] 처리 중: {card_products_file}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        cards = json.load(f)
    
    updated_cards = []
    for card in tqdm(cards, desc="구조화 중 (card_products)"):
        updated_card = process_single_card(card)
        updated_cards.append(updated_card)
    
    # 기존 파일에 structured 필드 추가하여 저장 (덮어쓰기)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(updated_cards, f, ensure_ascii=False, indent=2)
    
    print(f"[INFO] 저장 완료: {file_path} ({len(updated_cards)}개 카드)")
    return [(card_products_file, len(updated_cards))]


def process_notices():
    """notices 파일 처리 (structured 제거 - RAG 검색 미사용)"""
    file_path = INPUT_DIR / NOTICES_FILE
    if not file_path.exists():
        print(f"[WARNING] 파일을 찾을 수 없습니다: {file_path}")
        return []
    
    print(f"\n[INFO] 처리 중: {NOTICES_FILE} (structured 필드 제거 - RAG 검색 미사용)")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        documents = json.load(f)
    
    updated_docs = []
    for doc in documents:
        # structured 필드 제거
        if "structured" in doc:
            del doc["structured"]
        updated_docs.append(doc)
    
    # 저장
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(updated_docs, f, ensure_ascii=False, indent=2)
    
    print(f"[INFO] 저장 완료: {file_path} ({len(updated_docs)}개 문서, structured 필드 제거됨)")
    return [(NOTICES_FILE, len(updated_docs))]


def main():
    """메인 실행 함수"""
    global USE_PARALLEL
    
    print("=" * 80)
    print("RAG 검색 성능 개선 - 구조화 데이터 생성")
    print("=" * 80)
    
    # LLM 없으면 병렬 처리 비활성화
    if not USE_LLM:
        print("[WARNING] OPENAI_API_KEY가 없습니다. 규칙 기반 구조화만 사용합니다.")
        USE_PARALLEL = False  # LLM 없으면 병렬 처리 불필요
    
    # 처리 방식 안내
    if USE_PARALLEL and USE_LLM:
        print(f"\n[INFO] 병렬 처리 모드 활성화: {MAX_WORKERS} workers")
        print(f"[INFO] Rate limit: 분당 {RATE_LIMIT_PER_MINUTE} requests")
        print("[WARNING] 동일 API 키를 다른 노트북에서 동시 사용 시 rate limit 초과 위험!")
    else:
        print("\n[INFO] 순차 처리 모드")
        if USE_LLM:
            print(f"[INFO] 요청 간 딜레이: {REQUEST_DELAY}초")
    
    # 1. service_guide_documents 처리
    print("\n[1단계] service_guide_documents 구조화")
    if USE_PARALLEL and USE_LLM:
        service_results = process_service_guides_parallel()
    else:
        service_results = process_service_guides()
    
    # 2. card_products 처리
    print("\n[2단계] card_products 구조화")
    card_results = process_card_products()
    
    # 3. notices 처리 (structured 제거)
    print("\n[3단계] notices 처리 (structured 필드 제거)")
    notice_results = process_notices()
    
    # 4. 결과 요약
    print("\n" + "=" * 80)
    print("구조화 완료")
    print("=" * 80)
    
    total_docs = 0
    for filename, count in service_results + card_results + notice_results:
        print(f"  {filename}: {count}개 문서")
        total_docs += count
    
    print(f"\n총 {total_docs}개 문서 구조화 완료")
    print("\n[INFO] 기존 JSON 파일에 structured 필드가 추가되었습니다.")
    print("[INFO] service_guides: workflow/information 타입별 다른 structured 형식")
    print("[INFO] card_products: 카드 정보 형식 structured 추가")
    print("[INFO] notices: structured 필드 제거 (RAG 검색 미사용)")
    print("[INFO] DB 적재 시 structured 필드를 함께 저장하세요.")


if __name__ == "__main__":
    main()
