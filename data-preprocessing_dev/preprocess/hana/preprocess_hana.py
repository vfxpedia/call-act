# Hana Card Consultation Data Preprocessing Script

import csv
import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import hashlib
import os
import shutil
import sys
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / '.env')

# ===== Constants =====
FILLER_WORDS = {'네', '예', '아', '음', '어', '그'}
MAX_TEXT_LENGTH = 10000
MAX_RETRY_COUNT = 2  # 검증 실패 시 최대 재시도 횟수
DEFAULT_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4.1-mini')  # 기본 LLM 모델

# ===== 시간 포맷팅 유틸리티 =====
def format_time(seconds: float) -> str:
    """
    초를 읽기 쉬운 형식으로 변환 (예: "3분 14초", "45초")
    
    Args:
        seconds: 초 단위 시간
    
    Returns:
        포맷된 시간 문자열
    """
    if seconds < 60:
        return f"{seconds:.1f}초"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        if secs < 1:
            return f"{minutes}분"
        else:
            return f"{minutes}분 {secs:.1f}초"

# 반복 불용어 패턴 (축소용)
DUPLICATE_FILLER_PATTERNS = [
    # 네/예 반복 패턴
    (r'네[,\s]*네[\s]*네[\s]*네\.?', '네.'),
    (r'네[,\s]*네[\s]*네\.?', '네.'),
    (r'네[,\s]*네\.?(?!\s*네)', '네.'),
    (r'예[,\s]*예[\s]*예[\s]*예\.?', '예.'),
    (r'예[,\s]*예[\s]*예\.?', '예.'),
    (r'예[,\s]*예\.?(?!\s*예)', '예.'),
    # 그/아 반복 패턴
    (r'그 그 그', '그'),
    (r'그 그', '그'),
    (r'아 아 아', '아'),
    (r'아 아', '아'),
    # 구두점 중복 패턴
    (r'네\.,', '네.'),
    (r'예\.,', '예.'),
]

# 태그 형식 정규식
TAG_PATTERN = re.compile(r'\[[^\]]+#\d+\]')

# ===== 1. Personal Information Masking =====
def normalize_card_masking(text: str) -> str:
    """정확히 16자리 ▲를 [카드번호#1]로 변환 (앞뒤로 ▲가 없는 경우)"""
    return re.sub(r'(?<!▲)▲{16}(?!▲)', '[카드번호#1]', text)

def normalize_long_masking(text: str) -> str:
    """
    12-15자리 연속 ▲를 [마스킹블록]으로 변환
    LLM이 문맥에 따라 적절한 태그로 변환할 수 있도록 함
    """
    return re.sub(r'(?<!▲)▲{12,15}(?!▲)', '[마스킹블록]', text)

def normalize_phone_masking(text: str) -> str:
    """
    정확히 10-11자리 ▲를 [전화번호#1]로 변환
    
    제외 조건:
    - 앞뒤로 ▲가 더 있는 경우 (연속체의 일부)
    - "원"이 바로 뒤에 오는 경우 (금액)
    - "요건"이 바로 뒤에 오는 경우 (금액 관련 표현)
    """
    # 정확히 11자리: 앞뒤로 ▲가 없고, "원" 또는 "요건"도 뒤에 없는 경우
    text = re.sub(r'(?<!▲)▲{11}(?!▲)(?!원|요건)', '[전화번호#1]', text)
    # 정확히 10자리: 앞뒤로 ▲가 없고, "원" 또는 "요건"도 뒤에 없는 경우
    text = re.sub(r'(?<!▲)▲{10}(?!▲)(?!원|요건)', '[전화번호#1]', text)
    return text

def normalize_generic_masking(text: str) -> str:
    """나머지 ▲를 [개인정보]로 변환"""
    return re.sub(r'▲{2,}', '[개인정보]', text)

def normalize_all_masking(text: str) -> str:
    """
    모든 개인정보 마스킹 정규화 (긴 패턴부터 처리)
    
    처리 순서:
    1. 16자리 → [카드번호#1]
    2. 12-15자리 → [마스킹블록] (LLM이 문맥 판단)
    3. 10-11자리 → [전화번호#1]
    4. 나머지 → [개인정보]
    """
    text = normalize_card_masking(text)      # 16자리
    text = normalize_long_masking(text)      # 12-15자리
    text = normalize_phone_masking(text)     # 10-11자리
    text = normalize_generic_masking(text)   # 나머지
    return text

# ===== 1-2. LLM-based Slot Tagging (GPT-5.2 방식) =====
def classify_slots_with_llm(text: str, model: Optional[str] = None, log_func=None, max_retries: int = 3) -> Dict:
    """
    LLM을 사용하여 ▲ 구간을 문맥 기반 [타입#번호] 태그로 치환

    Args:
        text: ▲ 포함 텍스트 (카드번호/전화번호는 이미 처리됨)
        model: 사용할 OpenAI 모델 (None이면 환경변수 또는 기본값 사용)

    Returns:
        {
            "text": 태그가 적용된 텍스트,
            "slot_types": 사용된 슬롯 타입 목록,
            "entity_mapping": 각 태그의 설명 (디버깅용)
        }
    """
    from openai import OpenAI

    # OpenAI API 키 확인
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        if log_func:
            log_func("[WARNING] OPENAI_API_KEY not found. Skipping LLM processing.")
        else:
            print("[WARNING] OPENAI_API_KEY not found. Skipping LLM processing.")
        return {
            "text": re.sub(r'▲+', '[개인정보]', text),
            "slot_types": [],
            "entity_mapping": {}
        }
    
    # log_func가 없으면 기본값 설정
    if log_func is None:
        log_func = getattr(tqdm, 'write', print)

    client = OpenAI(api_key=api_key)
    
    # 모델 선택
    if model is None:
        model = DEFAULT_MODEL

    # 슬롯 태깅 프롬프트 (v3.0 - 2단계 사고 방식)
    prompt = f"""당신은 카드사 상담 데이터의 개인정보 슬롯 태깅(Slot Tagging) 전문가입니다.

**목표**: ▲로 마스킹된 개인정보 구간을 문맥에 맞는 `[타입#번호]` 형식 태그로 치환합니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**[필수] 2단계 사고 프로세스 (반드시 순서대로 수행)**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**[1단계: 전체 대화 분석 및 개체 식별]**
태깅하기 전에 먼저 전체 대화를 읽고 다음을 파악하세요:

1. **동일 개체 그룹화**:
   - 손님이 말하고 상담사가 확인/반복하는 정보 → 같은 개체
   - 대화 중 여러 번 언급되는 이름, 번호, 금액 → 같은지 다른지 판단

2. **개체 동일성 판단 기준**:
   - **▲의 자릿수(개수)가 다르면** → 무조건 다른 개체
   - **▲의 자릿수가 같고** 손님↔상담사 확인 패턴 → 같은 개체
   - **▲의 자릿수가 같지만** 문맥상 다른 값(예: 기존 한도 vs 추가 금액) → 다른 개체
   - **확실하지 않으면** → 다른 번호 부여 (보수적 접근)

3. **나열 vs 확인 구분**:
   - "A, B, C 은행 가능" → 나열 → 각각 다른 번호
   - 손님: "A은행" / 상담사: "A은행 맞으시죠?" → 확인 → 같은 번호

**[2단계: 번호 할당 및 태깅]**
1단계에서 식별한 개체 그룹에 번호를 할당하고 태깅하세요.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**핵심 원칙**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. **원본 문장/구조는 절대 수정하지 마세요** - 오직 ▲ 구간과 마스킹 안된 개인정보만 태그로 치환
2. **모든 ▲는 반드시 태그로 변환** - 처리되지 않은 ▲가 남아있으면 안됨
3. **마스킹되지 않은 개인정보도 태깅** - 날짜(10월 11일), 금액(100만원) 등
4. **이미 처리된 태그 검증** - `[카드번호#1]`, `[전화번호#1]`이 문맥상 잘못되었으면 수정 가능
   - 예: "사업자번호 확인" 문맥에서 `[전화번호#1]` → `[사업자번호#1]`로 수정

**개체 판단 핵심 규칙 (자릿수 우선)**
- ▲ 자릿수가 **다르면** → 100% 다른 개체 → 다른 번호
- ▲ 자릿수가 **같으면** → 문맥으로 판단 → 확인 패턴이면 같은 번호, 아니면 다른 번호
- **확실하지 않으면** → 다른 번호 (나중에 수정하기 쉬움)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**[추가 규칙] 특수 패턴 처리**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**1. 연속 ▲ 블록 처리 (중요!):**
- 연속된 ▲▲▲▲▲▲...는 **하나의 개체**로 처리
- **각 ▲를 개별 글자로 분리하지 마세요**
- 예: ▲▲▲▲▲▲▲▲▲▲▲▲ (12자리 연속) → [전화번호#1] 또는 [계좌번호#1]
- `[마스킹블록]`이 있으면 문맥에 맞게 적절한 태그로 변환
  - 전화번호 문맥: [전화번호#1]
  - 계좌번호 문맥: [계좌번호#1]
  - 기타: [개인정보#1]

**2. 날짜 Entity Tracking (과도한 넘버링 방지):**
- 같은 날짜를 반복 언급하면 **같은 번호** 사용
- "30일", "말일" 등 같은 의미면 같은 번호
- 예: "결제일이 30일이어서 30일까지 사용하면 다음 달 30일에 청구" 
  → [날짜#1], [날짜#1], [날짜#1]
- 단, 명확히 다른 날짜면 다른 번호 ("1일"과 "15일" 등)

**3. 나열 후 선택 패턴:**
- 상담사가 "A, B, C 가능합니다" → 나열: [은행명#1], [은행명#2], [은행명#3]
- 손님이 그 중 하나를 선택하면 → **나열된 번호 중 하나 사용**
- 예:
  - 상담사: "[은행명#1], [은행명#2], [은행명#3] 있습니다."
  - 손님: "[은행명#1]이요." (첫 번째 선택)
- 자릿수가 같은 것과 매칭하여 번호 결정

**4. 서비스업체명 vs 카드사명 구분:**
- "▲▲에서 ▲▲ 제휴된 카드" 패턴:
  - 첫 번째 ▲▲: [서비스업체명#1] (쿠팡, 스타벅스, 배민 등)
  - 두 번째 ▲▲: [카드사명#1] (하나, 신한, 국민 등)
- "▲▲카드에서 ▲▲ 제휴 카드로 변경":
  - 첫 번째: [카드사명#1] (기존 카드사)
  - 두 번째: [서비스업체명#1] 또는 문맥에 맞게 판단

**구성요소 방식 태깅 (분절된 정보):**
정보를 나눠서 주고받을 때는 `_구성요소` 접미사 사용:
- 계좌번호 분절: `[계좌번호_구성요소#1]`, `[계좌번호_구성요소#2]`, ...
- 전화번호 분절: `[전화번호_구성요소#1]`, `[전화번호_구성요소#2]`, ...
- 카드번호 끝 4자리: `[카드번호_구성요소#1]`, `[카드번호_구성요소#2]`, ...
- 팩스번호 분절: `[팩스번호_구성요소#1]`, `[팩스번호_구성요소#2]`, ...
- 인증번호: `[인증번호#1]`, `[인증번호#2]`, ...

**태그 형식:**
- 기본: `[타입#번호]` (반드시 #번호 포함)
  - 예: `[상담원명#1]`, `[고객명#1]`, `[교육청명#1]`

**학교명/기관명 태깅 규칙:**
- `▲▲▲초등학교` → `[초등학교명#1]` (학교 이름 전체를 하나의 태그로)
- `▲▲▲중학교` → `[중학교명#1]`
- `▲▲▲고등학교` → `[고등학교명#1]`
- `▲▲▲교육청` → `[교육청명#1]`

**태그 타입 목록:**

[인물 관련]
- `상담원명` - 상담원 이름 (처음과 끝에 동일 상담원이면 같은 번호)
- `고객명` - 고객 이름
- `학생명` - 학생 이름
- `영문명` - 영문 이름 (예: HONG GILDONG)

[기관/회사명]
- `교육청명` - 교육청 명칭
- `초등학교명`, `중학교명`, `고등학교명` - 학교 전체 명칭
- `대학교명` - 대학교 명칭
- `카드사명` - 카드사 명칭 (예: ▲▲카드)
- `은행명` - 은행 명칭 (나열→다른번호, 확인→같은번호)
- `보험사명` - 보험사 명칭
- `증권사명` - 증권사 명칭
- `병원명` - 병원/의원 명칭
- `서비스업체명` - 도시가스, 통신사 등 서비스 업체명
- `사업자번호` - 사업자등록번호 (10자리)

[장소 관련]
- `장소명` - 편의점, 커피숍, 매장 등 장소 명칭
- `지점명` - 은행/카드사 지점명 (예: ▲▲점)
- `부서명` - 회사/기관 부서 명칭

[개인정보 - 전체]
- `계좌번호` - 은행 계좌번호 (전체를 한번에 말할 때)
- `생년월일` - 생년월일 (6자리, ▲▲년▲▲월▲▲일 형태 등)
- `이메일아이디` - 이메일 ID 부분

[개인정보 - 구성요소 (분절 시)]
- `계좌번호_구성요소` - 계좌번호를 나눠서 말할 때
- `전화번호_구성요소` - 전화번호를 나눠서 말할 때
- `카드번호_구성요소` - 카드번호 끝 4자리 등
- `팩스번호_구성요소` - 팩스번호를 나눠서 말할 때
- `식별번호_구성요소` - 학생식별번호 등을 나눠서 말할 때
- `인증번호` - SMS/OTP 인증번호

[금융정보]
- `금액` - 금액 정보 (자릿수 같고 확인 패턴→같은번호, 불확실→다른번호)
- `비율` - 금리, 할인율 (▲▲퍼센트, ▲▲% 형태)
- `카드상품명` - 카드 상품명 (예: ▲▲▲▲카드, ▲▲▲▲체크카드)
- `한도금액` - 카드 한도 관련 금액

[시간정보]
- `날짜` - 날짜 정보 (▲▲월 ▲▲일, ▲▲년도, 10월 11일 등 **마스킹 안된 것도 포함**)
- `시간` - 시간 정보 (▲▲시 ▲▲분)

[상품/서비스 관련]
- `자동차정보` - 자동차 회사명, 차종 (예: 그랜저, 현대자동차)

**Few-shot 예시 1 - 학교명:**
입력: `상담사: ▲▲▲▲초등학교 ▲▲▲학생 맞으실까요?`
출력: `상담사: [초등학교명#1] [학생명#1]학생 맞으실까요?`

**Few-shot 예시 2 - Entity Tracking (같은 개체 동일 번호):**
입력: `손님: ▲▲▲입니다. / 상담사: ▲▲▲교육청이고요.`
출력: `손님: [교육청명#1]입니다. / 상담사: [교육청명#1]이고요.`

**Few-shot 예시 3 - 계좌번호 구성요소 (분절):**
입력:
```
상담사: 계좌번호 말씀해 주세요.
손님: ▲▲▲
상담사: ▲▲▲
손님: ▲▲▲▲▲▲▲
상담사: ▲▲▲▲▲▲
손님: ▲▲▲▲▲요.
상담사: ▲▲▲▲▲ 맞으실까요?
```
출력:
```
상담사: 계좌번호 말씀해 주세요.
손님: [계좌번호_구성요소#1]
상담사: [계좌번호_구성요소#1]
손님: [계좌번호_구성요소#2]
상담사: [계좌번호_구성요소#2]
손님: [계좌번호_구성요소#3]요.
상담사: [계좌번호_구성요소#3] 맞으실까요?
```

**Few-shot 예시 4 - 상담원명 동일 번호:**
입력: `상담사: 상담원 ▲▲▲입니다. ... 상담사: 상담원 ▲▲▲이었습니다.`
출력: `상담사: 상담원 [상담원명#1]입니다. ... 상담사: 상담원 [상담원명#1]이었습니다.`

**Few-shot 예시 5 - 은행명 나열 vs 확인:**
입력 (나열): `상담사: 가상 계좌는 ▲▲은행, ▲▲, ▲▲은행 가능한데 어디로 발송해드릴까요?`
출력 (나열): `상담사: 가상 계좌는 [은행명#1], [은행명#2], [은행명#3] 가능한데 어디로 발송해드릴까요?`

입력 (확인): 
```
손님: ▲▲은행으로 해주세요.
상담사: ▲▲은행 확인됩니다.
```
출력 (확인): 
```
손님: [은행명#1]으로 해주세요.
상담사: [은행명#1] 확인됩니다.
```

**Few-shot 예시 6 - 금액 (자릿수로 판단):**
입력:
```
상담사: 아 그러면 지금 한도가 ▲▲▲원인데 그럼 ▲▲원 더 플러스 돼서 ▲▲▲원 말씀이십니까?
손님: 네.
상담사: 네, 총 한도 ▲▲▲원을 일단 진행 먼저 도와드립니다.
```
분석:
- ▲▲▲원 (3자리): 기존 한도, 최종 한도 → 자릿수 같지만 문맥상 다를 수 있음
- ▲▲원 (2자리): 추가 금액 → 자릿수 다름
- 마지막 ▲▲▲원은 "총 한도"로 세 번째 ▲▲▲원을 확인하는 패턴

출력:
```
상담사: 아 그러면 지금 한도가 [금액#1]인데 그럼 [금액#2] 더 플러스 돼서 [금액#3] 말씀이십니까?
손님: 네.
상담사: 네, 총 한도 [금액#3]을 일단 진행 먼저 도와드립니다.
```

**Few-shot 예시 7 - 생년월일과 전화번호 구분:**
입력:
```
상담사: 휴대폰 번호와 생년월일 말씀해 주세요.
손님: ▲▲▲▲▲▲이고요.
손님: ▲▲▲에 ▲▲▲▲요.
```
출력:
```
상담사: 휴대폰 번호와 생년월일 말씀해 주세요.
손님: [생년월일#1]이고요.
손님: [전화번호_구성요소#1]에 [전화번호_구성요소#2]요.
```

**Few-shot 예시 8 - 비율/퍼센트:**
입력: `상담사: 기존 금리 ▲▲ 퍼센트에서 ▲▲ 퍼센트로 금리 인하 되었고요.`
출력: `상담사: 기존 금리 [비율#1]에서 [비율#2]로 금리 인하 되었고요.`

**Few-shot 예시 9 - 카드번호 끝 4자리:**
입력:
```
상담사: 단기 대출 이용하실 카드 번호 끝 네 자리를 말씀해 주시겠습니까?
손님: ▲▲▲▲
상담사: ▲▲▲▲ 확인되셨습니다.
```
출력:
```
상담사: 단기 대출 이용하실 카드 번호 끝 네 자리를 말씀해 주시겠습니까?
손님: [카드번호_구성요소#1]
상담사: [카드번호_구성요소#1] 확인되셨습니다.
```

**Few-shot 예시 10 - 마스킹 안된 날짜도 태깅:**
입력: `손님: 어 11일 날 10월 11일 날 사용한 거요.`
출력: `손님: 어 [날짜#1] 사용한 거요.`

**Few-shot 예시 11 - 팩스번호 구성요소:**
입력:
```
상담사: 완납증명서 받으실 팩스번호 말씀해주시겠습니까?
손님: 예 ▲▲▲
상담사: ▲▲▲
손님: ▲▲▲▲
상담사: 팩스번호 다시 한번 확인하겠습니다. ▲▲▲▲▲▲▲에 ▲▲▲▲ 맞습니까?
```
출력:
```
상담사: 완납증명서 받으실 팩스번호 말씀해주시겠습니까?
손님: 예 [팩스번호_구성요소#1]
상담사: [팩스번호_구성요소#1]
손님: [팩스번호_구성요소#2]
상담사: 팩스번호 다시 한번 확인하겠습니다. [팩스번호_구성요소#3]에 [팩스번호_구성요소#4] 맞습니까?
```

**Few-shot 예시 12 - 정규식 태그 수정 (문맥상 잘못된 경우):**
입력: `상담사: 사업자번호 확인해드리겠습니다. [전화번호#1] 맞으실까요?`
분석: 문맥상 "사업자번호 확인"이므로 [전화번호#1]은 잘못됨
출력: `상담사: 사업자번호 확인해드리겠습니다. [사업자번호#1] 맞으실까요?`

**Few-shot 예시 13 - 2단계 사고 적용 예시:**
입력:
```
상담사: 상담원 ▲▲▲입니다. 고객님 성함이 어떻게 되시죠?
손님: ▲▲▲입니다.
상담사: ▲▲▲ 고객님, ▲▲은행 계좌로 이체 도와드릴까요?
손님: 네, ▲▲은행이요.
상담사: ▲▲▲ 고객님, ▲▲은행 확인됐습니다. 상담원 ▲▲▲이었습니다.
```
[1단계 분석]:
- 상담원명: ▲▲▲ (처음, 끝) → 같은 개체 → #1
- 고객명: ▲▲▲ (손님 답변, 상담사 호칭 2회) → 같은 개체 → #1
- 은행명: ▲▲ (상담사 언급, 손님 확인, 상담사 재확인) → 같은 개체 → #1

[2단계 태깅]:
출력:
```
상담사: 상담원 [상담원명#1]입니다. 고객님 성함이 어떻게 되시죠?
손님: [고객명#1]입니다.
상담사: [고객명#1] 고객님, [은행명#1] 계좌로 이체 도와드릴까요?
손님: 네, [은행명#1]이요.
상담사: [고객명#1] 고객님, [은행명#1] 확인됐습니다. 상담원 [상담원명#1]이었습니다.
```

**Few-shot 예시 14 - 연속 마스킹 (하나의 개체로 처리):**
입력: `손님: ▲▲▲▲▲▲▲▲▲▲▲▲고요.`
분석: 12자리 연속 ▲는 하나의 전화번호 또는 계좌번호
출력: `손님: [전화번호#1]고요.`
(틀린 예: `[전화번호_구성요소#1][전화번호_구성요소#2]...` ← 이렇게 분리하면 안됨)

**Few-shot 예시 15 - 나열 후 선택 패턴:**
입력:
```
상담사: 가상 계좌는 ▲▲은행, ▲▲, ▲▲은행 있습니다. 어떤 은행이 편하십니까?
손님: ▲▲이요.
```
분석: 
- 상담사가 3개 은행 나열 → #1, #2, #3
- 손님이 2자리(▲▲) 선택 → 나열 중 2자리인 #2와 매칭
출력:
```
상담사: 가상 계좌는 [은행명#1], [은행명#2], [은행명#3] 있습니다. 어떤 은행이 편하십니까?
손님: [은행명#2]이요.
```

**Few-shot 예시 16 - 서비스업체명 vs 카드사명:**
입력: `손님: 제가 그 ▲▲에서 ▲▲ 제휴된 카드로 변경을 했었는데`
분석: "▲▲에서 ▲▲ 제휴 카드" 패턴
- 첫 번째 ▲▲: 서비스업체명 (쿠팡, 배민 등)
- 두 번째 ▲▲: 카드사명 (하나, 신한 등)
출력: `손님: 제가 그 [서비스업체명#1]에서 [카드사명#1] 제휴된 카드로 변경을 했었는데`

**Few-shot 예시 17 - 날짜 반복 (같은 날짜는 같은 번호):**
입력:
```
상담사: 결제일이 ▲▲일이어서 ▲▲일까지 사용하신 금액이 다음 달 ▲▲일에 청구됩니다.
손님: 그러면 ▲▲일까지 쓴 건 다음 달 ▲▲일에 나온다는 거죠?
```
분석: 같은 결제일(예: 30일)을 반복 언급 → 같은 번호
출력:
```
상담사: 결제일이 [날짜#1]이어서 [날짜#1]까지 사용하신 금액이 다음 달 [날짜#1]에 청구됩니다.
손님: 그러면 [날짜#1]까지 쓴 건 다음 달 [날짜#1]에 나온다는 거죠?
```

**Few-shot 예시 18 - [마스킹블록] 처리:**
입력: `손님: 휴대폰 번호는 [마스킹블록]입니다.`
분석: [마스킹블록]은 12-15자리 연속 마스킹, 문맥상 전화번호
출력: `손님: 휴대폰 번호는 [전화번호#1]입니다.`

**입력 대화 (▲ 포함, 고정 길이는 이미 처리됨):**
{text}

**출력 형식 (JSON):**
응답은 반드시 다음 JSON 형식으로만 출력하세요.
{{
  "text": "태그가 적용된 대화 전문",
  "slot_types": ["상담원명", "교육청명", ...],
  "entity_mapping": {{
    "상담원명#1": "설명",
    "교육청명#1": "설명"
  }}
}}"""

    # 재시도 로직
    for attempt in range(max_retries):
        try:
            # OpenAI API 호출 (새로운 API 형식)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert in slot tagging for Korean call center data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000,
                timeout=60  # 타임아웃 설정
            )

            # 응답 파싱
            result_text = response.choices[0].message.content.strip()
            
            # HTML 응답 감지 (Cloudflare DNS 에러 등)
            if result_text.strip().startswith('<!DOCTYPE') or '<html' in result_text.lower():
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5  # 5초, 10초, 15초
                    log_func(f"[RETRY {attempt + 1}/{max_retries}] HTML 응답 감지 (네트워크 에러), {wait_time}초 후 재시도...")
                    time.sleep(wait_time)
                    continue
                else:
                    log_func(f"[ERROR] HTML 응답 감지 (네트워크 에러), 최대 재시도 횟수 초과")
                    return {
                        "text": re.sub(r'▲+', '[개인정보]', text),
                        "slot_types": [],
                        "entity_mapping": {}
                    }

            # JSON 추출 (코드 블록으로 감싸진 경우 처리)
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
                result_text = result_text.strip()

            result = json.loads(result_text)
            return result

        except json.JSONDecodeError as e:
            # JSON 파싱 에러 상세 정보 출력
            error_msg = f"[ERROR] LLM JSON parsing failed: {e}\n"
            error_msg += f"  위치: line {e.lineno}, column {e.colno}\n"
            error_msg += f"  응답 길이: {len(result_text)} 문자\n"
            
            # 문제가 있는 부분 주변 출력 (최대 200자)
            if e.pos is not None:
                start = max(0, e.pos - 100)
                end = min(len(result_text), e.pos + 100)
                error_context = result_text[start:end]
                error_msg += f"  문제 부분 주변:\n{error_context}\n"
                error_msg += f"  {' ' * (e.pos - start + 2)}^\n"
            
            # 에러 로그를 파일로 저장 (디버깅용)
            try:
                error_log_dir = Path(__file__).parent / 'test_results' / 'error_logs'
                error_log_dir.mkdir(parents=True, exist_ok=True)
                error_log_file = error_log_dir / f"json_error_{int(time.time())}.txt"
                with open(error_log_file, 'w', encoding='utf-8') as f:
                    f.write(f"=== JSON 파싱 에러 ===\n")
                    f.write(f"에러: {e}\n")
                    f.write(f"위치: line {e.lineno}, column {e.colno}\n")
                    f.write(f"\n=== LLM 응답 전문 ===\n")
                    f.write(result_text)
                error_msg += f"  [DEBUG] 에러 로그 저장됨: {error_log_file}\n"
            except Exception as save_error:
                error_msg += f"  [WARNING] 에러 로그 저장 실패: {save_error}\n"
            
            log_func(error_msg)
            
            # 재시도 가능하면 재시도
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                log_func(f"[RETRY {attempt + 1}/{max_retries}] JSON 파싱 실패, {wait_time}초 후 재시도...")
                time.sleep(wait_time)
                continue
            else:
                # 최대 재시도 횟수 초과
                return {
                    "text": re.sub(r'▲+', '[개인정보]', text),
                    "slot_types": [],
                    "entity_mapping": {}
                }
        except Exception as e:
            # 기타 에러 (네트워크 타임아웃 등)
            error_type = type(e).__name__
            error_msg = f"[ERROR] LLM processing failed ({error_type}): {e}\n"
            
            # 재시도 가능하면 재시도
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                log_func(f"[RETRY {attempt + 1}/{max_retries}] 네트워크 에러, {wait_time}초 후 재시도...")
                time.sleep(wait_time)
                continue
            else:
                # 최대 재시도 횟수 초과
                log_func(f"[ERROR] 최대 재시도 횟수 초과, 폴백 처리")
                return {
                    "text": re.sub(r'▲+', '[개인정보]', text),
                    "slot_types": [],
                    "entity_mapping": {}
                }
    
    # 모든 재시도 실패
    return {
        "text": re.sub(r'▲+', '[개인정보]', text),
        "slot_types": [],
        "entity_mapping": {}
    }

def normalize_all_masking_v2(text: str, use_llm: bool = True, validate: bool = True, 
                             merge_semantic_tags: bool = True, semantic_use_llm: bool = False) -> tuple:
    """
    개선된 마스킹 함수 (v3.2 - 문맥 기반 태그 통합 추가)

    Args:
        text: 원본 대화 텍스트 (▲ 포함)
        use_llm: LLM 사용 여부 (기본값 True)
        validate: 검증 수행 여부 (기본값 True)
        merge_semantic_tags: 문맥 기반 태그 통합 수행 여부 (기본값 True, v3.2 추가)
        semantic_use_llm: 태그 통합 시 LLM 사용 여부 (기본값 False, 빠른 규칙 기반)

    Returns:
        (태그가 적용된 텍스트, slot_types 목록)
    
    처리 순서:
        1. 16자리 → [카드번호#1]
        2. 12-15자리 → [마스킹블록] (LLM이 문맥 판단)
        3. 10-11자리 → [전화번호#1]
        4. 나머지 ▲ → LLM으로 처리
        5. 문맥 기반 태그 통합 (v3.2 추가)
    """
    # 1. 고정 길이 패턴 (정규식) - 긴 것부터 처리
    text = normalize_card_masking(text)      # 16자리
    text = normalize_long_masking(text)      # 12-15자리 → [마스킹블록]
    text = normalize_phone_masking(text)     # 10-11자리

    # 2. 나머지 ▲는 LLM으로 처리
    if use_llm:
        # log_func는 normalize_all_masking_v2 호출 시점에 전달 불가능하므로
        # tqdm.write를 기본값으로 사용 (process_csv_file에서 tee_logger로 리다이렉트됨)
        log_func = getattr(tqdm, 'write', print)
        result = classify_slots_with_llm(text, log_func=log_func)
        processed_text = result['text']
        slot_types = result['slot_types']
        
        # 3. 검증 (옵션)
        if validate:
            retry_count = 0
            while retry_count < MAX_RETRY_COUNT:
                validation = validate_all(processed_text, use_entity_check=(retry_count == 0))
                
                if validation['valid']:
                    break
                
                # 검증 실패 시 상세 정보 출력 (tqdm.write 사용하여 진행바와 충돌 방지)
                retry_count += 1
                # tqdm이 사용 가능한 경우 tqdm.write, 아니면 print
                log_func = getattr(tqdm, 'write', print)
                log_func(f"\n[RETRY {retry_count}] Validation failed, retrying...")
                
                # mask_check 실패 상세 정보
                if not validation['mask_check']['valid']:
                    mask_info = validation['mask_check']
                    log_func(f"  [MASK_CHECK FAILED] 남은 ▲ 개수: {mask_info['remaining_count']}")
                    if mask_info['remaining_positions']:
                        log_func(f"  [DEBUG] 남은 ▲ 위치 (최대 3개):")
                        for i, pos_info in enumerate(mask_info['remaining_positions'][:3]):
                            log_func(f"    위치 {i+1}: {pos_info['mask_text']} (문맥: ...{pos_info['context']}...)")
                
                # tag_check 실패 상세 정보
                if not validation['tag_check']['valid']:
                    tag_info = validation['tag_check']
                    log_func(f"  [TAG_CHECK FAILED] 잘못된 태그 개수: {len(tag_info['invalid_tags'])}")
                    if tag_info['invalid_tags']:
                        log_func(f"  [DEBUG] 잘못된 태그 목록 (최대 5개): {tag_info['invalid_tags'][:5]}")
                
                # entity_check 실패 상세 정보 (첫 번째 재시도에서만)
                if retry_count == 1 and 'entity_check' in validation:
                    entity_info = validation['entity_check']
                    if entity_info['consistency_score'] < 0.9:
                        log_func(f"  [ENTITY_CHECK FAILED] 일관성 점수: {entity_info['consistency_score']:.3f} (기준: 0.9)")
                        if entity_info.get('issues'):
                            log_func(f"  [DEBUG] 발견된 문제점 (최대 3개):")
                            for i, issue in enumerate(entity_info['issues'][:3]):
                                issue_type = issue.get('type', 'unknown')
                                issue_desc = issue.get('description', 'N/A')
                                log_func(f"    문제 {i+1} [{issue_type}]: {issue_desc}")
                
                # ▲ 잔존 시 재처리
                if not validation['mask_check']['valid']:
                    log_func(f"  [ACTION] 남은 ▲ 처리 위해 LLM 재호출...")
                    result = classify_slots_with_llm(processed_text, log_func=log_func)
                    processed_text = result['text']
                    slot_types = list(set(slot_types + result['slot_types']))
                elif not validation['tag_check']['valid']:
                    log_func(f"  [ACTION] 잘못된 태그 수정 위해 LLM 재호출...")
                    result = classify_slots_with_llm(processed_text, log_func=log_func)
                    processed_text = result['text']
                    slot_types = list(set(slot_types + result['slot_types']))
                elif 'entity_check' in validation and validation['entity_check']['consistency_score'] < 0.9:
                    log_func(f"  [ACTION] Entity 일관성 개선 위해 LLM 재호출...")
                    result = classify_slots_with_llm(processed_text, log_func=log_func)
                    processed_text = result['text']
                    slot_types = list(set(slot_types + result['slot_types']))
            
            # 최종 검증 결과와 함께 반환
            final_validation = validate_all(processed_text, use_entity_check=False)
            
            # 여전히 ▲가 남아있으면 강제 처리
            if not final_validation['mask_check']['valid']:
                remaining_count = final_validation['mask_check']['remaining_count']
                log_func = getattr(tqdm, 'write', print)
                log_func(f"\n[WARNING] 최종 검증 후에도 ▲ {remaining_count}개 남아있음. [개인정보]로 강제 처리합니다.")
                processed_text = re.sub(r'▲+', '[개인정보]', processed_text)
        
        # 4. 후처리: 연속 구성요소 태그 병합
        processed_text = merge_consecutive_component_tags(processed_text)
        
        # 5. 후처리 추가: 문맥 기반 태그 통합 (v3.2) - 조건부 실행 (성능 최적화)
        if merge_semantic_tags:
            # 복잡한 케이스(같은 타입 태그가 3개 이상)만 실행하여 성능 개선
            tag_pattern_temp = re.compile(r'\[([^\]]+#\d+)\]')
            all_tags_temp = tag_pattern_temp.findall(processed_text)
            
            if all_tags_temp:
                # 태그 타입별 개수 확인
                from collections import Counter
                tag_types = []
                for tag in all_tags_temp:
                    if '#' in tag:
                        try:
                            tag_type, _ = tag.split('#', 1)
                            tag_types.append(tag_type)
                        except (ValueError, IndexError):
                            continue
                
                if tag_types:
                    type_counts = Counter(tag_types)
                    # 같은 타입이 3개 이상인 경우만 문맥 통합 실행 (복잡한 케이스)
                    has_complex_case = any(count >= 3 for count in type_counts.values())
                    
                    if has_complex_case:
                        processed_text = merge_semantic_duplicate_tags(
                            processed_text, 
                            use_llm=semantic_use_llm,
                            model=DEFAULT_MODEL
                        )
        
        # 6. 반복 불용어 축소
        processed_text = reduce_duplicate_fillers(processed_text)
        
        return processed_text, slot_types
    else:
        # LLM 없이는 보수적으로 [개인정보]로 처리
        text = re.sub(r'▲+', '[개인정보]', text)
        text = merge_consecutive_component_tags(text)
        text = reduce_duplicate_fillers(text)
        return text, []


# ===== 1-3. Validation Functions =====
def validate_mask_remaining(text: str) -> Dict:
    """
    ▲ 잔존 검사: 태깅 후 남은 ▲가 있는지 확인
    
    Returns:
        {
            "valid": bool,
            "remaining_count": int,
            "remaining_positions": list of (start, end, text)
        }
    """
    pattern = re.compile(r'▲+')
    matches = list(pattern.finditer(text))
    
    remaining = []
    for m in matches:
        # 전후 문맥 포함 (최대 20자)
        start = max(0, m.start() - 20)
        end = min(len(text), m.end() + 20)
        context = text[start:end]
        remaining.append({
            "position": (m.start(), m.end()),
            "mask_text": m.group(),
            "context": context
        })
    
    return {
        "valid": len(remaining) == 0,
        "remaining_count": len(remaining),
        "remaining_positions": remaining
    }


def validate_tag_format(text: str) -> Dict:
    """
    태그 형식 검사: 모든 태그가 [타입#번호] 형식인지 확인
    
    Returns:
        {
            "valid": bool,
            "invalid_tags": list of invalid tag strings,
            "valid_tags": list of valid tag strings
        }
    """
    # 모든 [] 형태 찾기
    all_brackets = re.findall(r'\[[^\]]+\]', text)
    
    valid_tags = []
    invalid_tags = []
    
    for tag in all_brackets:
        if TAG_PATTERN.match(tag):
            valid_tags.append(tag)
        else:
            # [개인정보]는 예외 허용 (폴백)
            if tag != '[개인정보]':
                invalid_tags.append(tag)
    
    return {
        "valid": len(invalid_tags) == 0,
        "invalid_tags": invalid_tags,
        "valid_tags": valid_tags
    }


def validate_entity_consistency(text: str, model: Optional[str] = None, log_func=None, max_retries: int = 3) -> Dict:
    """
    Entity 일관성 검사: LLM을 통해 동일 개체가 같은 번호로 태깅되었는지 확인
    
    Returns:
        {
            "valid": bool,
            "consistency_score": float (0.0 ~ 1.0),
            "issues": list of issue descriptions
        }
    """
    from openai import OpenAI
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return {"valid": True, "consistency_score": 1.0, "issues": []}
    
    client = OpenAI(api_key=api_key)
    
    # log_func가 없으면 기본값 설정
    if log_func is None:
        log_func = getattr(tqdm, 'write', print)
    
    # 모델 선택
    if model is None:
        model = DEFAULT_MODEL
    
    prompt = f"""당신은 슬롯 태깅 검증 전문가입니다. 아래 대화에서 Entity Tracking이 올바르게 되었는지 검증하세요.

**검증 규칙:**
1. 같은 개체(같은 금액, 같은 은행, 같은 사람 등)는 반드시 같은 번호를 사용해야 함
2. 서로 다른 개체는 다른 번호를 사용해야 함
3. 은행명이 나열될 때 (예: "A은행, B은행, C은행") 각각 다른 번호 필요
4. 상담사와 손님이 같은 정보를 확인할 때 같은 번호 유지

**대화:**
{text}

**출력 형식 (JSON):**
{{
  "consistent": true/false,
  "score": 0.0~1.0,
  "issues": [
    {{"type": "same_entity_different_number", "description": "설명"}},
    {{"type": "different_entity_same_number", "description": "설명"}}
  ]
}}
"""
    
    # 재시도 로직
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an entity tracking validator. Output only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000,
                timeout=60  # 타임아웃 설정
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # HTML 응답 감지 (Cloudflare DNS 에러 등)
            if result_text.strip().startswith('<!DOCTYPE') or '<html' in result_text.lower():
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    log_func(f"[RETRY {attempt + 1}/{max_retries}] HTML 응답 감지 (네트워크 에러), {wait_time}초 후 재시도...")
                    time.sleep(wait_time)
                    continue
                else:
                    log_func(f"[WARNING] Entity consistency validation failed: HTML 응답 감지 (네트워크 에러)")
                    return {"valid": True, "consistency_score": 1.0, "issues": []}
            
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
                result_text = result_text.strip()
            
            result = json.loads(result_text)
            
            return {
                "valid": result.get("consistent", True),
                "consistency_score": result.get("score", 1.0),
                "issues": result.get("issues", [])
            }
        except json.JSONDecodeError as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                log_func(f"[RETRY {attempt + 1}/{max_retries}] JSON 파싱 실패, {wait_time}초 후 재시도...")
                time.sleep(wait_time)
                continue
            else:
                log_func(f"[WARNING] Entity consistency validation failed: JSON 파싱 에러 - {e}")
                return {"valid": True, "consistency_score": 1.0, "issues": []}
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                log_func(f"[RETRY {attempt + 1}/{max_retries}] 네트워크 에러, {wait_time}초 후 재시도...")
                time.sleep(wait_time)
                continue
            else:
                log_func(f"[WARNING] Entity consistency validation failed: {e}")
                return {"valid": True, "consistency_score": 1.0, "issues": []}
    
    # 모든 재시도 실패
    return {"valid": True, "consistency_score": 1.0, "issues": []}


def validate_all(text: str, use_entity_check: bool = True) -> Dict:
    """
    전체 검증 수행
    
    Args:
        text: 태깅 완료된 텍스트
        use_entity_check: Entity 일관성 검사 수행 여부 (LLM 호출)
    
    Returns:
        {
            "valid": bool,
            "mask_check": {...},
            "tag_check": {...},
            "entity_check": {...} (optional)
        }
    """
    mask_check = validate_mask_remaining(text)
    tag_check = validate_tag_format(text)
    
    result = {
        "valid": mask_check["valid"] and tag_check["valid"],
        "mask_check": mask_check,
        "tag_check": tag_check
    }
    
    if use_entity_check:
        # log_func는 validate_all 호출 시점에 전달 불가능하므로
        # tqdm.write를 기본값으로 사용
        log_func = getattr(tqdm, 'write', print)
        entity_check = validate_entity_consistency(text, log_func=log_func)
        result["entity_check"] = entity_check
        # Entity 검사는 score 0.9 이상이면 통과
        if entity_check["consistency_score"] < 0.9:
            result["valid"] = False
    
    return result


def reduce_duplicate_fillers(text: str) -> str:
    """
    반복 불용어 축소: "네, 네 네." → "네."
    
    Args:
        text: 입력 텍스트
    
    Returns:
        축소된 텍스트
    """
    for pattern, replacement in DUPLICATE_FILLER_PATTERNS:
        text = re.sub(pattern, replacement, text)
    return text


def merge_consecutive_component_tags(text: str) -> str:
    """
    연속된 구성요소 태그를 하나로 병합 (후처리)
    
    LLM이 연속 마스킹을 개별 구성요소로 분리한 경우 하나의 태그로 병합합니다.
    예: [전화번호_구성요소#1][전화번호_구성요소#2]... → [전화번호#1]
    
    Args:
        text: 태깅된 텍스트
    
    Returns:
        병합된 텍스트
    """
    # 전화번호 구성요소 연속 3개 이상 → [전화번호#N]
    text = re.sub(
        r'(\[전화번호_구성요소#\d+\]){3,}',
        '[전화번호#1]',
        text
    )
    
    # 계좌번호 구성요소 연속 3개 이상 → [계좌번호#N]
    text = re.sub(
        r'(\[계좌번호_구성요소#\d+\]){3,}',
        '[계좌번호#1]',
        text
    )
    
    # 카드번호 구성요소 연속 3개 이상 → [카드번호#N]
    text = re.sub(
        r'(\[카드번호_구성요소#\d+\]){3,}',
        '[카드번호#1]',
        text
    )
    
    # 팩스번호 구성요소 연속 3개 이상 → [팩스번호#N]
    text = re.sub(
        r'(\[팩스번호_구성요소#\d+\]){3,}',
        '[팩스번호#1]',
        text
    )
    
    # 식별번호 구성요소 연속 5개 이상 → [식별번호#N]
    text = re.sub(
        r'(\[식별번호_구성요소#\d+\]){5,}',
        '[식별번호#1]',
        text
    )
    
    return text


# ===== 1-4. 문맥 기반 태그 통합 (범용 함수) =====
def merge_semantic_duplicate_tags(text: str, use_llm: bool = False, model: str = 'gpt-4o-mini') -> str:
    """
    문맥상 같은 의미의 태그를 같은 번호로 통합 (범용 함수)
    
    모든 태그 타입에 적용 가능:
    - 금액: "기본 연회비 [금액#1]"과 "기본 연회비 [금액#4]" → 통합
    - 날짜: "25일 [날짜#1]"과 "25일 [날짜#3]" → 통합
    - 이름: 손님이 말한 이름과 상담사가 확인한 이름 → 통합
    
    Args:
        text: 태그가 포함된 텍스트
        use_llm: LLM을 사용하여 문맥 유사도 분석 (기본값 False, 더 정확하지만 느림)
        model: LLM 모델명 (use_llm=True일 때만 사용)
    
    Returns:
        태그가 통합된 텍스트
    """
    import re
    from collections import defaultdict
    
    tag_pattern = re.compile(r'\[([^\]]+#\d+)\]')
    all_tags = tag_pattern.findall(text)
    
    if not all_tags:
        return text
    
    # 태그 타입별로 그룹화 (안전한 파싱)
    tags_by_type = defaultdict(list)
    log_func = getattr(tqdm, 'write', print)
    
    for tag in set(all_tags):
        try:
            # split('#', 1)로 첫 번째 #만 분리하여 안전하게 파싱
            if '#' in tag:
                tag_type, _ = tag.split('#', 1)
                tags_by_type[tag_type].append(tag)
            else:
                # #이 없는 태그는 건너뛰기
                continue
        except (ValueError, IndexError) as e:
            # 파싱 실패 시 로그 출력 후 건너뛰기
            log_func(f"[WARNING] 태그 파싱 실패 (건너뜀): {tag} - {e}")
            continue
    
    # 각 태그 타입별로 문맥 분석
    tag_mapping = {}
    
    for tag_type, tags in tags_by_type.items():
        if len(tags) <= 1:
            continue
        
        # 각 태그의 문맥 추출
        tag_contexts = {}
        for tag in tags:
            contexts = []
            for match in tag_pattern.finditer(text):
                if match.group(1) == tag:
                    start, end = match.span()
                    # 앞뒤 50자 문맥 추출
                    context_before = text[max(0, start-50):start]
                    context_after = text[end:min(len(text), end+50)]
                    context = (context_before + context_after).lower()
                    contexts.append(context)
            tag_contexts[tag] = contexts
        
        # 문맥 유사도 기반 그룹화
        if use_llm:
            # LLM을 사용한 정확한 문맥 분석
            groups = _group_tags_with_llm(tag_type, tags, tag_contexts, text, model)
        else:
            # 규칙 기반 빠른 분석
            groups = _group_tags_with_rules(tag_type, tags, tag_contexts)
        
        # 같은 그룹 내 태그를 가장 작은 번호로 통합
        for group_tags in groups:
            if len(group_tags) > 1:
                try:
                    # 안전한 파싱으로 번호 추출
                    tag_numbers = []
                    for tag in group_tags:
                        if '#' in tag:
                            try:
                                _, num_str = tag.split('#', 1)
                                tag_numbers.append(int(num_str))
                            except (ValueError, IndexError):
                                continue
                    
                    if tag_numbers:
                        min_num = min(tag_numbers)
                        base_tag = f"{tag_type}#{min_num}"
                        
                        # 모든 태그를 base_tag로 매핑
                        for tag in group_tags:
                            if tag != base_tag:
                                tag_mapping[tag] = base_tag
                except Exception as e:
                    # 통합 실패 시 로그 출력 후 건너뛰기
                    log_func(f"[WARNING] 태그 통합 실패 (건너뜀): {group_tags} - {e}")
                    continue
    
    # 태그 치환
    result = text
    for old_tag, new_tag in tag_mapping.items():
        result = result.replace(f'[{old_tag}]', f'[{new_tag}]')
    
    return result


def _group_tags_with_rules(tag_type: str, tags: List[str], tag_contexts: Dict[str, List[str]]) -> List[List[str]]:
    """
    규칙 기반 태그 그룹화 (빠른 방법)
    
    문맥 키워드 유사도, 위치, 패턴 등을 기반으로 그룹화
    """
    from collections import defaultdict
    
    groups = []
    processed = set()
    
    for tag in tags:
        if tag in processed:
            continue
        
        # 현재 태그와 같은 그룹에 속할 태그들
        current_group = [tag]
        processed.add(tag)
        
        # 다른 태그들과 비교
        for other_tag in tags:
            if other_tag in processed or tag == other_tag:
                continue
            
            # 문맥 유사도 계산
            similarity = _calculate_context_similarity(
                tag_contexts[tag], 
                tag_contexts[other_tag]
            )
            
            # 유사도가 높으면 같은 그룹
            if similarity > 0.6:  # 임계값 조정 가능
                current_group.append(other_tag)
                processed.add(other_tag)
        
        if current_group:
            groups.append(current_group)
    
    return groups


def _calculate_context_similarity(contexts1: List[str], contexts2: List[str]) -> float:
    """
    두 태그의 문맥 유사도 계산 (0.0 ~ 1.0)
    
    방법:
    1. 공통 키워드 비율 (Jaccard 유사도)
    2. 특정 키워드 보너스
    """
    if not contexts1 or not contexts2:
        return 0.0
    
    # 모든 문맥을 합쳐서 비교
    combined1 = ' '.join(contexts1)
    combined2 = ' '.join(contexts2)
    
    # 공통 단어 추출
    words1 = set(combined1.split())
    words2 = set(combined2.split())
    
    if not words1 or not words2:
        return 0.0
    
    # Jaccard 유사도
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    if union == 0:
        return 0.0
    
    jaccard = intersection / union
    
    # 특정 키워드가 있으면 가중치 증가
    important_keywords = ['기본', '제휴', '연회비', '확인', '맞으', '같은', '동일', '같이']
    keyword_bonus = 0.0
    for keyword in important_keywords:
        if keyword in combined1 and keyword in combined2:
            keyword_bonus += 0.1
    
    similarity = min(1.0, jaccard + keyword_bonus)
    return similarity


def _group_tags_with_llm(tag_type: str, tags: List[str], tag_contexts: Dict[str, List[str]], 
                         full_text: str, model: str) -> List[List[str]]:
    """
    LLM을 사용한 정확한 문맥 분석 및 태그 그룹화
    """
    from openai import OpenAI
    import os
    import json
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        # LLM 실패 시 규칙 기반으로 fallback
        return _group_tags_with_rules(tag_type, tags, tag_contexts)
    
    client = OpenAI(api_key=api_key)
    
    # 태그와 문맥 정보를 JSON으로 정리
    tag_info = []
    for tag in tags:
        tag_info.append({
            "tag": tag,
            "contexts": tag_contexts[tag][:3]  # 처음 3개만
        })
    
    prompt = f"""다음은 상담 대화에서 추출한 {tag_type} 타입 태그들입니다.
각 태그의 문맥을 분석하여 같은 의미를 가진 태그들을 그룹으로 묶어주세요.

태그 정보:
{json.dumps(tag_info, ensure_ascii=False, indent=2)}

전체 대화 (일부):
{full_text[:2000]}

같은 의미의 태그 그룹을 JSON 배열로 반환하세요:
[
  ["{tag_type}#1", "{tag_type}#3"],
  ["{tag_type}#2", "{tag_type}#5"]
]

태그 번호가 다르더라도 문맥상 같은 값(이름, 금액, 날짜 등)을 나타내면 같은 그룹으로 묶으세요.
JSON만 반환하세요.
"""
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert in analyzing context similarity for slot tagging. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        result = response.choices[0].message.content.strip()
        # JSON 파싱
        if result.startswith('```'):
            result = result.split('```')[1]
            if result.startswith('json'):
                result = result[4:]
        groups = json.loads(result)
        return groups
    except Exception as e:
        # tqdm.write 사용하여 진행바와 충돌 방지
        log_func = getattr(tqdm, 'write', print)
        log_func(f"[WARNING] LLM grouping failed: {e}, using rule-based method")
        return _group_tags_with_rules(tag_type, tags, tag_contexts)


# ===== 2. Filler Word Removal =====
def remove_standalone_fillers(text: str) -> str:
    """독립된 불용어만 제거 (문장 내 포함된 것은 유지)"""
    pattern = r'\b(' + '|'.join(FILLER_WORDS) + r')\b[,.]?\s*'
    return re.sub(pattern, '', text)

# ===== 3. Client ID Generation =====
def generate_client_id(source_id: str, gender: str, age: str) -> str:
    """source_id 기반 가상 client_id 생성"""
    combined = f"{source_id}_{gender}_{age}"
    hash_value = hashlib.md5(combined.encode()).hexdigest()[:8]
    return f"HANA_CLT_{hash_value}"

# ===== 4. Keyword Extraction =====
def extract_keywords(category: str, content: str) -> List[str]:
    """카테고리와 내용 기반 키워드 추출 (규칙 기반)"""
    keywords = []

    if category:
        keywords.append(category)

    keyword_patterns = [
        r'카드', r'분실', r'도난', r'재발급', r'해외', r'결제',
        r'수수료', r'할부', r'일시불', r'취소', r'환불', r'정지',
        r'신청', r'해제', r'발급', r'연체', r'이용', r'한도'
    ]

    for pattern in keyword_patterns:
        if re.search(pattern, content):
            match = re.search(pattern, content)
            if match and match.group() not in keywords:
                keywords.append(match.group())

    return keywords[:5]

def extract_scenario_tags(content: str) -> List[str]:
    """
    상담 내용에서 시나리오 태그 추출 (GPT-5.2 제안)

    Args:
        content: 상담 대화 텍스트

    Returns:
        시나리오 태그 목록 (예: "교육비", "자동납부신청", "본인확인" 등)
    """
    tags = []

    # 시나리오 패턴 정의 (구체적 → 일반적 순서)
    scenario_patterns = {
        # 카드 관련
        '카드분실신고': r'카드.*분실.*신고|분실.*카드.*신고',
        '카드재발급': r'재발급|신규.*발급',
        '카드정지': r'카드.*정지|사용.*정지',
        '카드해제': r'정지.*해제|사용.*재개',
        '카드교체발급': r'교체.*발급|갱신.*카드|새.*카드.*받',
        '카드유효기간만료': r'유효.*기간.*만료|유효.*기간.*다',

        # 결제 관련
        '해외결제': r'해외.*결제|해외.*사용',
        '일시불전환': r'일시불.*전환|할부.*일시불',
        '할부신청': r'할부.*신청',
        '결제일문의': r'결제일|청구.*언제|다음.*달.*청구|청구.*되',
        '가상계좌발급': r'가상.*계좌|입금.*계좌.*발급',

        # 수수료/이자 관련
        '수수료문의': r'수수료.*문의|수수료.*얼마',
        '이자문의': r'이자.*문의|이자.*얼마',
        '연회비문의': r'연회비.*문의|연회비.*얼마',

        # 한도 관련
        '한도증액': r'한도.*증액|한도.*올',
        '한도조회': r'한도.*조회|한도.*확인',
        '카드론안내': r'카드론|장기.*카드.*대출|한도.*부여',

        # 자동납부/이체 관련
        '자동납부신청': r'자동납부.*신청|자동이체.*신청',
        '자동납부해지': r'자동납부.*해지|자동이체.*해지',

        # 본인확인/동의 (일반적 태그는 제거 - 거의 모든 상담에 나타나므로)
        # '본인확인': r'본인.*확인|본인.*맞|생년월일.*말씀',  # 제거: 구분력 낮음
        '대체카드동의': r'다른.*카드.*동의|대체.*카드|유효한.*카드',
        # '개인정보동의': r'개인정보.*동의|정보.*제공.*동의',  # 제거: 구분력 낮음

        # 교육/학교 관련
        '교육비납부': r'교육비|수익자.*부담.*경비|학비',
        '학생식별번호확인': r'학생.*식별.*번호|학생.*번호',
        '학교승인필요': r'학교.*승인|최종.*승인',

        # SMS/알림 서비스
        'SMS서비스가입': r'문자.*가입|알림톡.*동의|엘엠에스.*가입',
        'SMS서비스해지': r'문자.*해지|알림톡.*해지|엘엠에스.*해지',
        
        # 앱/페이 관련
        '앱카드등록': r'앱.*카드.*등록|어플.*등록|페이.*등록',
        '간편결제등록': r'간편.*결제.*등록|페이.*추가',

        # 처리 기간/안내
        '처리기간_최대7일': r'최대.*7일|일주일.*소요',
        '문자안내': r'문자.*받|문자.*안내|SMS.*보내',
        '배송안내': r'배송.*안내|배송.*예정',

        # 일반 상담 (일반적 태그는 제거)
        # '상담완료': r'상담원.*이었습니다|감사합니다.*상담원',  # 제거: 구분력 낮음
        '추가문의': r'다른.*문의|추가.*문의',
    }

    # 패턴 매칭
    for tag, pattern in scenario_patterns.items():
        if re.search(pattern, content, re.IGNORECASE):
            tags.append(tag)

    # 중복 제거 및 최대 10개
    tags = list(dict.fromkeys(tags))[:10]
    
    # 일반적 태그 제거 (구분력이 낮은 태그)
    common_tags_to_remove = {'본인확인', '상담완료', '개인정보동의'}
    tags = [tag for tag in tags if tag not in common_tags_to_remove]

    return tags

# ===== 5. JSON Transformation =====
def create_vectordb_entry(row: Dict, cleaned_text: str, slot_types: List[str], scenario_tags: List[str], category: str = None) -> Dict:
    """
    VectorDB용 JSON 엔트리 생성 (Frontend 구조 정렬)
    
    Frontend 기대 필드:
    - id: 고유 ID
    - consultation_id: 상담 ID (Frontend API 호환)
    - document_type: 문서 타입
    - title: 상담 제목 (카테고리 기반)
    - content: 상담 대화 내용 (text → content로 변경)
    - metadata: 메타데이터 (slot_types, scenario_tags, created_at 포함)
    
    Args:
        category: 이미 마스킹 처리된 category (None이면 row에서 가져옴)
    """
    source_id = row.get('source_id', '')
    if category is None:
        category = row.get('consulting_category', '')
    keywords = extract_keywords(category, cleaned_text)

    return {
        "id": f"hana_consultation_{source_id}",
        "consultation_id": f"CS-HANA-{source_id}",
        "document_type": "consultation_transcript",
        "title": f"{category} 상담" if category else "상담",
        "content": cleaned_text,
        "metadata": {
            "source_id": source_id,
            "category": category,
            "keywords": keywords,
            "slot_types": slot_types,
            "scenario_tags": scenario_tags,
            "summary": None,
            "created_at": datetime.now().isoformat()
        }
    }

def create_rdb_metadata(row: Dict, keywords: List[str], client_id: str, category: str = None) -> Dict:
    """
    RDB용 메타데이터 생성
    
    Args:
        category: 이미 마스킹 처리된 category (None이면 row에서 가져옴)
    """
    source_id = row.get('source_id', '')
    if category is None:
        category = row.get('consulting_category', '')

    return {
        "id": f"hana_consultation_{source_id}",
        "source_id": source_id,
        "consulting_category": category,
        "status": "완료",
        "client_id": client_id,
        "client_name": "[고객명#1]",
        "client_phone": "[전화번호#1]",
        "client_gender": row.get('client_gender', ''),
        "client_age": row.get('client_age', ''),
        "call_start_time": None,
        "call_end_time": None,
        "call_duration": int(row.get('consulting_length', 0)) if row.get('consulting_length') else 0,
        "consulting_turns": int(row.get('consulting_turns', 0)) if row.get('consulting_turns') else 0,
        "recording_file_path": None,
        "summary": None,
        "keywords": ','.join(keywords),
        "next_steps": None,
        "timeline": None,
        "referenced_doc_ids": None
    }

# ===== 6. CSV Processing =====
def process_csv_row(row: Dict, idx: int) -> Dict:
    """CSV 1행을 처리하여 통합 JSON 생성 (GPT-5.2 방식 적용)"""
    content = row.get('consulting_content', '')

    # v2 함수 사용: LLM 슬롯 태깅 + 불용어 제거 중단
    cleaned_text, slot_types = normalize_all_masking_v2(content, use_llm=True)

    # 시나리오 태그 추출
    scenario_tags = extract_scenario_tags(cleaned_text)

    source_id = row.get('source_id', '')
    gender = row.get('client_gender', '')
    age = row.get('client_age', '')
    client_id = generate_client_id(source_id, gender, age)

    category = row.get('consulting_category', '')
    
    # category 마스킹 처리 (▲가 있으면 치환)
    if '▲' in category:
        # 간단한 패턴 매칭 사용 (LLM 호출 불필요)
        category = re.sub(r'▲+페이', '[서비스명#1]페이', category)
        category = re.sub(r'▲+카드', '[카드사명#1]카드', category)
        category = re.sub(r'▲+은행', '[은행명#1]은행', category)
        category = re.sub(r'▲+', '[서비스명#1]', category)
    
    keywords = extract_keywords(category, cleaned_text)

    vectordb_entry = create_vectordb_entry(row, cleaned_text, slot_types, scenario_tags)
    rdb_metadata = create_rdb_metadata(row, keywords, client_id)

    return {
        "vectordb": vectordb_entry,
        "rdb": rdb_metadata
    }

def save_json_incremental(data: List[Dict], file_path: Path, mode: str = 'append') -> None:
    """
    JSON 파일에 증분 저장 (기존 데이터 유지)
    
    Args:
        data: 저장할 데이터 리스트
        file_path: JSON 파일 경로
        mode: 'append' (기존에 추가) 또는 'overwrite' (덮어쓰기)
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    if mode == 'append' and file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                # 기존 데이터와 병합 (중복 제거)
                existing_ids = {item.get('id') for item in existing_data if 'id' in item}
                new_data = [item for item in data if item.get('id') not in existing_ids]
                existing_data.extend(new_data)
                data = existing_data
        except (json.JSONDecodeError, FileNotFoundError):
            # 파일이 손상되었으면 덮어쓰기
            pass
    
    # 백업 생성 (안전장치)
    if file_path.exists():
        backup_path = file_path.with_suffix('.json.backup')
        shutil.copy2(file_path, backup_path)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_checkpoint(checkpoint_file: Path) -> Dict:
    """체크포인트 파일에서 마지막 처리 위치 로드"""
    if checkpoint_file.exists():
        try:
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    return {"last_processed_index": -1, "processed_ids": []}

def save_checkpoint(checkpoint_file: Path, last_index: int, processed_ids: List[str]) -> None:
    """체크포인트 파일에 현재 상태 저장"""
    checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
    with open(checkpoint_file, 'w', encoding='utf-8') as f:
        json.dump({
            "last_processed_index": last_index,
            "processed_ids": processed_ids,
            "timestamp": datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)

class TeeLogger:
    """콘솔과 파일에 동시에 로그를 출력하는 클래스"""
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.file_handle = None
        self.stdout = sys.stdout
        try:
            self.file_handle = open(log_file, 'a', encoding='utf-8')
        except Exception as e:
            # 파일 열기 실패 시 콘솔에만 출력
            print(f"[WARNING] 로그 파일을 열 수 없습니다: {e}")
            print(f"[WARNING] 콘솔에만 로그가 출력됩니다.")
    
    def write(self, message: str):
        """콘솔과 파일에 동시에 쓰기"""
        # 콘솔에는 항상 출력
        try:
            self.stdout.write(message)
            self.stdout.flush()
        except:
            pass
        
        # 파일에는 성공한 경우만 출력
        if self.file_handle:
            try:
                self.file_handle.write(message)
                self.file_handle.flush()  # 즉시 파일에 반영
            except Exception:
                # 파일 쓰기 실패 시 무시 (콘솔 출력은 유지)
                pass
    
    def flush(self):
        """버퍼 플러시"""
        try:
            self.stdout.flush()
            if self.file_handle:
                self.file_handle.flush()
        except:
            pass
    
    def close(self):
        """파일 핸들 닫기"""
        if self.file_handle:
            try:
                self.file_handle.close()
            except:
                pass
            finally:
                self.file_handle = None

def save_sample_txt(sample_dir: Path, source_id: str, category: str, 
                    cleaned_text: str, slot_types: List[str], scenario_tags: List[str],
                    processing_time: float) -> None:
    """
    샘플 txt 파일 저장 (카테고리별 샘플 확인용)
    
    Args:
        sample_dir: 샘플 저장 디렉토리
        source_id: 소스 ID
        category: 상담 카테고리
        cleaned_text: 전처리된 텍스트
        slot_types: 슬롯 타입 목록
        scenario_tags: 시나리오 태그 목록
        processing_time: 처리 시간
    """
    sample_dir.mkdir(parents=True, exist_ok=True)
    output_file = sample_dir / f"sample_{source_id}.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# source_id: {source_id}\n")
        f.write(f"# category: {category}\n")
        f.write(f"# slot_types: {slot_types}\n")
        f.write(f"# scenario_tags: {scenario_tags}\n")
        f.write(f"# processing_time: {processing_time:.2f}s\n")
        f.write("=" * 60 + "\n")
        f.write(cleaned_text)


def process_csv_file(csv_path: Path, output_dir: Path, sample_size: Optional[int] = None,
                     save_interval: int = 30, checkpoint_file: Optional[Path] = None,
                     resume: bool = False) -> None:
    """
    CSV 전체 처리 및 JSON 저장 (중간 저장 + 체크포인트 기능)
    
    Args:
        csv_path: 입력 CSV 파일 경로
        output_dir: 출력 디렉토리
        sample_size: 샘플 크기 (테스트용)
        save_interval: N개 처리마다 JSON 파일에 저장 (기본값: 30, 최적값: 25-50)
        checkpoint_file: 체크포인트 파일 경로 (None이면 자동 생성)
        resume: 재시작 모드 (체크포인트에서 이어서 시작)
    """
    from collections import defaultdict
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 체크포인트 파일 설정
    if checkpoint_file is None:
        checkpoint_file = output_dir / 'checkpoint.json'
    
    # 출력 파일 경로
    vectordb_path = output_dir / 'hana_vectordb.json'
    rdb_path = output_dir / 'hana_rdb_metadata.json'
    
    # 로그 파일 설정
    log_dir = Path(__file__).parent / 'test_results' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f"processing_log_{timestamp}.txt"
    
    # TeeLogger 설정 (콘솔과 파일에 동시 출력)
    tee_logger = TeeLogger(log_file)
    
    def log_print(*args, **kwargs):
        """로그 출력 함수 (콘솔 + 파일)"""
        message = ' '.join(str(arg) for arg in args)
        if kwargs.get('end', '\n') == '\n':
            message += '\n'
        tee_logger.write(message)
    
    # 재시작 모드: 체크포인트에서 이어서 시작
    if resume:
        checkpoint = load_checkpoint(checkpoint_file)
        processed_ids = set(checkpoint.get("processed_ids", []))
        log_print(f"[RESUME] 체크포인트에서 재시작: 이미 처리된 ID: {len(processed_ids)}개")
        
        # 기존 JSON 파일 로드 (ID 기반 중복 제거를 위해)
        try:
            with open(vectordb_path, 'r', encoding='utf-8') as f:
                existing_vectordb = json.load(f)
                # 기존 데이터의 ID 추출
                existing_vectordb_ids = {item.get('id') for item in existing_vectordb if 'id' in item}
                log_print(f"[RESUME] 기존 VectorDB 데이터: {len(existing_vectordb)}개")
        except (FileNotFoundError, json.JSONDecodeError):
            existing_vectordb = []
            existing_vectordb_ids = set()
        
        try:
            with open(rdb_path, 'r', encoding='utf-8') as f:
                existing_rdb = json.load(f)
                existing_rdb_ids = {item.get('id') for item in existing_rdb if 'id' in item}
                log_print(f"[RESUME] 기존 RDB 데이터: {len(existing_rdb)}개")
        except (FileNotFoundError, json.JSONDecodeError):
            existing_rdb = []
            existing_rdb_ids = set()
    else:
        processed_ids = set()
        existing_vectordb = []
        existing_rdb = []
        existing_vectordb_ids = set()
        existing_rdb_ids = set()
        # 기존 파일 백업
        if vectordb_path.exists():
            backup_path = vectordb_path.with_suffix('.json.backup')
            shutil.copy2(vectordb_path, backup_path)
            log_print(f"[INFO] 기존 파일 백업: {backup_path}")
    
    # 샘플 저장 설정 (카테고리별 최대 2개)
    sample_dir = Path(__file__).parent / 'test_results' / 'full_run'
    saved_categories = defaultdict(int)
    max_samples_per_category = 2
    
    # 전체 처리 시간 측정 시작
    total_start_time = time.time()

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

        if sample_size:
            rows = rows[:sample_size]
        
        total_rows = len(rows)
        log_print("\n" + "=" * 60)
        log_print(f"[INFO] 전처리 시작")
        log_print(f"[INFO] 로그 파일: {log_file}")
        log_print("=" * 60)
        log_print(f"모드: {'재시작 (Resume)' if resume else '새로 시작'}")
        log_print(f"총 처리 대상: {total_rows}개 행")
        if resume:
            log_print(f"이미 처리됨: {len(processed_ids)}개 ID (건너뜀)")
            log_print(f"처리할 행: {total_rows - len([r for r in rows if r.get('source_id', '') in processed_ids])}개")
        log_print(f"중간 저장 간격: {save_interval}개마다 (약 {format_time(save_interval * 25)}마다, 평균 25초/행 기준)")
        log_print(f"샘플 저장 위치: {sample_dir}")
        log_print(f"체크포인트 파일: {checkpoint_file}")
        log_print("=" * 60)

        # tqdm 진행률 표시 (재시작 모드면 이미 처리된 수를 초기값으로)
        initial_progress = len(processed_ids) if resume else 0
        pbar = tqdm(total=total_rows, desc="Processing", unit="row", ncols=100, initial=initial_progress)
        
        # tqdm.write를 tee_logger.write로 리다이렉트 (로그 파일에 기록되도록)
        original_tqdm_write = tqdm.write
        def redirected_tqdm_write(s, file=None, end="\n", nolock=False):
            """tqdm.write를 tee_logger.write로 리다이렉트"""
            tee_logger.write(str(s) + end)
        tqdm.write = redirected_tqdm_write
        
        # 메모리 최적화: 중간 저장된 데이터는 별도 추적
        vectordb_data = []
        rdb_data = []
        processed_count = 0
        error_count = 0
        last_saved_index = -1  # 마지막으로 저장된 CSV 행 인덱스
        last_processed_index = -1  # 마지막으로 처리된 CSV 행 인덱스
        
        for idx, row in enumerate(rows):
            row_start_time = time.time()
            
            try:
                source_id = row.get('source_id', '')
                
                # 이미 처리된 ID 건너뛰기 (재시작 모드용)
                if source_id in processed_ids:
                    last_processed_index = idx
                    # initial 값에 이미 포함되어 있으므로 update 불필요
                    continue
                
                # 전처리 수행
                content = row.get('consulting_content', '')
                cleaned_text, slot_types = normalize_all_masking_v2(content, use_llm=True)
                scenario_tags = extract_scenario_tags(cleaned_text)
                
                category = row.get('consulting_category', '')
                # category 마스킹 처리 (▲가 있으면 치환)
                if '▲' in category:
                    category = re.sub(r'▲+페이', '[서비스명#1]페이', category)
                    category = re.sub(r'▲+카드', '[카드사명#1]카드', category)
                    category = re.sub(r'▲+은행', '[은행명#1]은행', category)
                    category = re.sub(r'▲+', '[서비스명#1]', category)
                
                gender = row.get('client_gender', '')
                age = row.get('client_age', '')
                client_id = generate_client_id(source_id, gender, age)
                keywords = extract_keywords(category, cleaned_text)
                
                vectordb_entry = create_vectordb_entry(row, cleaned_text, slot_types, scenario_tags, category=category)
                rdb_metadata = create_rdb_metadata(row, keywords, client_id, category=category)
                
                # ID 기반 중복 체크 (안전장치)
                if vectordb_entry.get('id') not in existing_vectordb_ids:
                    vectordb_data.append(vectordb_entry)
                    existing_vectordb_ids.add(vectordb_entry.get('id'))
                
                if rdb_metadata.get('id') not in existing_rdb_ids:
                    rdb_data.append(rdb_metadata)
                    existing_rdb_ids.add(rdb_metadata.get('id'))
                
                processed_ids.add(source_id)
                processed_count += 1
                last_processed_index = idx
                
                row_elapsed = time.time() - row_start_time
                
                # 카테고리별 샘플 txt 저장 (최대 2개)
                if saved_categories[category] < max_samples_per_category:
                    save_sample_txt(
                        sample_dir, source_id, category,
                        cleaned_text, slot_types, scenario_tags, row_elapsed
                    )
                    saved_categories[category] += 1
                
                # 중간 저장 (save_interval마다, 또는 마지막 행 처리 시)
                should_save = False
                if processed_count % save_interval == 0:
                    should_save = True
                elif idx == total_rows - 1:  # 마지막 행 처리 시
                    should_save = True
                
                if should_save and len(vectordb_data) > 0:
                    save_start_time = time.time()
                    
                    # 기존 데이터와 새 데이터 병합
                    all_vectordb = existing_vectordb + vectordb_data
                    all_rdb = existing_rdb + rdb_data
                    
                    save_json_incremental(all_vectordb, vectordb_path, mode='overwrite')
                    save_json_incremental(all_rdb, rdb_path, mode='overwrite')
                    save_checkpoint(checkpoint_file, last_processed_index, list(processed_ids))
                    
                    save_elapsed = time.time() - save_start_time
                    total_elapsed = time.time() - total_start_time
                    
                    # 저장 완료 후: 기존 데이터에 추가, 메모리 리스트 초기화
                    existing_vectordb = all_vectordb
                    existing_rdb = all_rdb
                    saved_vectordb_count = len(vectordb_data)
                    saved_rdb_count = len(rdb_data)
                    vectordb_data = []
                    rdb_data = []
                    last_saved_index = last_processed_index
                    
                    log_func = getattr(tqdm, 'write', log_print)
                    log_func(f"\n{'='*60}")
                    log_func(f"[SAVED] 중간 저장 완료 ({format_time(total_elapsed)} 경과)")
                    log_func(f"  - 처리 완료: {processed_count}개 행 (총 CSV 인덱스: {last_processed_index}/{total_rows-1})")
                    log_func(f"  - 이번 저장 데이터: {saved_vectordb_count}개 (VectorDB), {saved_rdb_count}개 (RDB)")
                    log_func(f"  - 전체 저장 데이터: {len(all_vectordb)}개 (VectorDB), {len(all_rdb)}개 (RDB)")
                    log_func(f"  - 저장 소요 시간: {format_time(save_elapsed)}")
                    log_func(f"  - 메모리 초기화 완료")
                    if processed_count % save_interval == 0:
                        remaining_until_next = save_interval - (processed_count % save_interval)
                        log_func(f"  - 다음 저장까지: 약 {remaining_until_next}개 행 남음")
                    log_func(f"  - 체크포인트 업데이트: 인덱스 {last_processed_index}, 처리된 ID {len(processed_ids)}개")
                    log_func(f"{'='*60}")
                
                # tqdm 업데이트
                total_elapsed = time.time() - total_start_time
                avg_time = total_elapsed / processed_count if processed_count > 0 else 0
                remaining = avg_time * (total_rows - idx - 1)
                
                pbar.set_postfix({
                    'source_id': source_id,
                    'time': format_time(row_elapsed),
                    'avg': format_time(avg_time),
                    'remaining': format_time(remaining),
                    'saved': processed_count
                })
                
            except KeyboardInterrupt:
                # Ctrl+C로 중단 시 현재까지 저장
                log_func = getattr(tqdm, 'write', log_print)
                total_elapsed = time.time() - total_start_time
                log_func(f"\n{'='*60}")
                log_func(f"[INTERRUPTED] 사용자 중단 감지 ({format_time(total_elapsed)} 경과)")
                log_func(f"  - 처리 완료: {processed_count}개 행")
                log_func(f"  - 마지막 CSV 인덱스: {last_processed_index}/{total_rows-1}")
                log_func(f"  - 메모리 상태: {len(vectordb_data)}개 (VectorDB), {len(rdb_data)}개 (RDB) 남음")
                log_func(f"  - 저장 중...")
                
                try:
                    # 메모리에 남아있는 데이터 저장
                    if len(vectordb_data) > 0 or len(rdb_data) > 0:
                        save_start_time = time.time()
                        all_vectordb = existing_vectordb + vectordb_data
                        all_rdb = existing_rdb + rdb_data
                        save_json_incremental(all_vectordb, vectordb_path, mode='overwrite')
                        save_json_incremental(all_rdb, rdb_path, mode='overwrite')
                        save_checkpoint(checkpoint_file, last_processed_index, list(processed_ids))
                        save_elapsed = time.time() - save_start_time
                        log_func(f"[SAVED] 중단 시점까지 저장 완료:")
                        log_func(f"  - 저장된 데이터: {len(vectordb_data)}개 (VectorDB), {len(rdb_data)}개 (RDB)")
                        log_func(f"  - 전체 저장 데이터: {len(all_vectordb)}개 (VectorDB), {len(all_rdb)}개 (RDB)")
                        log_func(f"  - 저장 소요 시간: {format_time(save_elapsed)}")
                    else:
                        # 변경사항이 없어도 체크포인트는 업데이트
                        save_checkpoint(checkpoint_file, last_processed_index, list(processed_ids))
                        log_func(f"[SAVED] 체크포인트만 업데이트 완료 (메모리에 저장할 데이터 없음)")
                    log_func(f"  - 재시작: python preprocess/hana/preprocess_hana.py --resume")
                except Exception as save_error:
                    log_func(f"[ERROR] 중단 시 저장 실패: {save_error}")
                finally:
                    log_func(f"{'='*60}")
                    # tqdm.write 원래 함수로 복원
                    try:
                        tqdm.write = original_tqdm_write
                    except:
                        pass
                    # 로그 파일 닫기
                    tee_logger.close()
                raise
                
            except Exception as e:
                # 개별 행 처리 실패 시 로그 기록 후 계속 진행
                error_count += 1
                last_processed_index = idx  # 에러가 있어도 인덱스는 추적
                log_func = getattr(tqdm, 'write', log_print)
                log_func(f"\n[ERROR] source_id {row.get('source_id', 'unknown')} 처리 실패: {e}")
                
                # 에러 로그 저장
                error_log_dir = Path(__file__).parent / 'test_results' / 'error_logs'
                error_log_dir.mkdir(parents=True, exist_ok=True)
                error_log_file = error_log_dir / f"processing_error_{int(time.time())}_{error_count}.txt"
                with open(error_log_file, 'w', encoding='utf-8') as f:
                    f.write(f"source_id: {row.get('source_id', 'unknown')}\n")
                    f.write(f"CSV 인덱스: {idx}\n")
                    f.write(f"에러: {e}\n")
                    f.write(f"트레이스백:\n")
                    import traceback
                    f.write(traceback.format_exc())
                
                pbar.update(1)
                continue
            
            pbar.update(1)
        
        pbar.close()

    # 최종 저장 (메모리에 남아있는 데이터가 있으면 저장)
    total_elapsed = time.time() - total_start_time
    log_func = getattr(tqdm, 'write', log_print)
    
    if len(vectordb_data) > 0 or len(rdb_data) > 0:
        save_start_time = time.time()
        all_vectordb = existing_vectordb + vectordb_data
        all_rdb = existing_rdb + rdb_data
        save_json_incremental(all_vectordb, vectordb_path, mode='overwrite')
        save_json_incremental(all_rdb, rdb_path, mode='overwrite')
        save_checkpoint(checkpoint_file, last_processed_index, list(processed_ids))
        save_elapsed = time.time() - save_start_time
        
        log_func(f"\n{'='*60}")
        log_func(f"[FINAL_SAVE] 최종 저장 완료 ({format_time(total_elapsed)} 경과)")
        log_func(f"  - 추가 저장 데이터: {len(vectordb_data)}개 (VectorDB), {len(rdb_data)}개 (RDB)")
        log_func(f"  - 전체 저장 데이터: {len(all_vectordb)}개 (VectorDB), {len(all_rdb)}개 (RDB)")
        log_func(f"  - 저장 소요 시간: {format_time(save_elapsed)}")
        log_func(f"  - 메모리 초기화 완료")
        log_func(f"{'='*60}")
    else:
        # 데이터 변경이 없어도 체크포인트는 업데이트
        save_checkpoint(checkpoint_file, last_processed_index, list(processed_ids))
        all_vectordb = existing_vectordb
        all_rdb = existing_rdb
        log_func(f"\n[FINAL_SAVE] 저장할 추가 데이터 없음 (이미 모두 저장됨)")
        log_func(f"  - 전체 저장 데이터: {len(all_vectordb)}개 (VectorDB), {len(all_rdb)}개 (RDB)")
    
    # 전체 처리 시간
    total_samples = sum(saved_categories.values())
    avg_time_per_row = total_elapsed / processed_count if processed_count > 0 else 0
    
    log_print("\n" + "=" * 60)
    log_print(f"[COMPLETE] 처리 완료 요약")
    log_print("=" * 60)
    log_print(f"총 처리 시간: {format_time(total_elapsed)}")
    log_print(f"처리된 행: {processed_count}개")
    log_print(f"에러 발생: {error_count}개")
    log_print(f"평균 처리 시간/행: {format_time(avg_time_per_row)}")
    log_print(f"샘플 txt 파일: {total_samples}개 (카테고리 {len(saved_categories)}개)")
    log_print()
    log_print(f"[데이터 저장 상태]")
    log_print(f"  - VectorDB: 총 {len(all_vectordb)}개 항목")
    log_print(f"  - RDB: 총 {len(all_rdb)}개 항목")
    log_print(f"  - 처리된 ID: {len(processed_ids)}개")
    log_print(f"  - 마지막 처리 인덱스: {last_processed_index}/{total_rows-1}")
    log_print(f"  - 메모리 상태: {len(vectordb_data)}개 (VectorDB), {len(rdb_data)}개 (RDB) 남음")
    log_print()
    log_print(f"[파일 위치]")
    log_print(f"  - VectorDB: {vectordb_path}")
    log_print(f"  - RDB: {rdb_path}")
    log_print(f"  - 체크포인트: {checkpoint_file}")
    log_print(f"  - 샘플: {sample_dir}")
    log_print(f"  - 로그: {log_file}")
    if processed_count < total_rows:
        log_print()
        log_print(f"[재시작 안내]")
        log_print(f"  - {total_rows - processed_count}개 행이 남아있습니다.")
        log_print(f"  - 재시작 명령: python preprocess/hana/preprocess_hana.py --resume")
    log_print("=" * 60)
    
    # tqdm.write 원래 함수로 복원
    try:
        tqdm.write = original_tqdm_write
    except:
        pass
    
    # 로그 파일 닫기 (항상 실행되도록 finally 블록 없이도 안전)
    try:
        tee_logger.close()
    except:
        pass

# ===== 7. CLI Entry Point =====
def main():
    """CLI 실행 진입점"""
    base_dir = Path(__file__).parent.parent.parent
    csv_path = base_dir / 'data' / 'hana' / 'TS_하나카드_통합 - 시트1.csv'
    output_dir = base_dir / 'data' / 'hana'

    if not csv_path.exists():
        print(f"[ERROR] CSV file not found: {csv_path}")
        return

    import sys
    
    # 명령줄 인자 파싱
    sample_size = None
    save_interval = 30  # 기본값 (25-30초/행 기준 약 12-15분마다 저장)
    resume = False
    
    if '--sample' in sys.argv:
        sample_size = 10
        print(f"[INFO] Running in sample mode (first {sample_size} rows)")
    
    if '--resume' in sys.argv:
        resume = True
        print(f"[INFO] Resume mode: 체크포인트에서 재시작")
    
    # --save-interval 옵션
    for i, arg in enumerate(sys.argv):
        if arg == '--save-interval' and i + 1 < len(sys.argv):
            try:
                save_interval = int(sys.argv[i + 1])
            except ValueError:
                print(f"[WARNING] 잘못된 save-interval 값, 기본값 30 사용")
    
    process_csv_file(csv_path, output_dir, sample_size, 
                     save_interval=save_interval, resume=resume)

if __name__ == '__main__':
    main()
