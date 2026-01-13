# 상담사 교육용 시나리오 생성 스크립트
# LLM을 활용하여 태그를 문맥에 맞는 자연스러운 값으로 치환

import os
import re
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv(Path(__file__).parent.parent.parent / '.env')


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


# ===== 컨텍스트 분석 및 태그 그룹화 =====
def analyze_tag_context(tagged_text: str) -> Dict[str, List[str]]:
    """
    태그의 문맥을 분석하여 같은 의미의 태그를 그룹화
    
    Args:
        tagged_text: 태그가 포함된 대화 텍스트
    
    Returns:
        태그 그룹 정보 (예: {"금액_기본연회비": ["금액#1", "금액#4"], ...})
    """
    import re
    from collections import defaultdict
    
    # 태그 추출
    tags = re.findall(r'\[([^\]]+#\d+)\]', tagged_text)
    
    # 문맥 키워드 기반 그룹화
    groups = defaultdict(list)
    
    # 금액 태그의 문맥 분석
    for tag in tags:
        tag_type, tag_num = tag.split('#')
        if tag_type == '금액':
            # 태그 주변 문맥 추출
            pattern = rf'\[{re.escape(tag)}\]'
            matches = list(re.finditer(pattern, tagged_text))
            for match in matches:
                start, end = match.span()
                context_before = tagged_text[max(0, start-20):start]
                context_after = tagged_text[end:min(len(tagged_text), end+20)]
                context = context_before + context_after
                
                # 키워드 기반 그룹화
                if '기본 연회비' in context or '기본연회비' in context:
                    groups['금액_기본연회비'].append(tag)
                elif '제휴' in context and '연회비' in context:
                    groups['금액_제휴연회비'].append(tag)
                elif '연회비' in context:
                    groups['금액_연회비'].append(tag)
                elif '자동차' in context or '오토' in context:
                    groups['금액_자동차'].append(tag)
                elif '카드론' in context or '대출' in context:
                    groups['금액_대출'].append(tag)
                elif '한도' in context:
                    groups['금액_한도'].append(tag)
    
    return dict(groups)


def get_reference_scenarios(category: str, base_dir: Path, limit: int = 2) -> List[str]:
    """
    카테고리와 유사한 완성된 시나리오를 찾아서 예시로 제공
    
    Args:
        category: 상담 카테고리
        base_dir: 기본 디렉토리
        limit: 최대 반환 개수
    
    Returns:
        완성된 시나리오 예시 리스트 (대화 내용만)
    """
    examples = []
    
    # .back 폴더에서 완성된 시나리오 검색
    back_dir = base_dir.parent.parent / '.back' / 'data-preprocessing' / 'preprocess' / 'hana' / 'test_results'
    
    if not back_dir.exists():
        return examples
    
    # 모든 scenarios_llm_v* 폴더 검색
    for scenario_dir in sorted(back_dir.glob('scenarios_llm_v*')):
        if not scenario_dir.is_dir():
            continue
        
        for scenario_file in scenario_dir.glob('test_scenario_*.txt'):
            try:
                with open(scenario_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 카테고리 확인
                if f'# 카테고리: {category}' in content:
                    # 대화 내용만 추출
                    lines = content.split('\n')
                    dialogue_start = False
                    dialogue_lines = []
                    
                    for line in lines:
                        if line.startswith('='):
                            dialogue_start = True
                            continue
                        if dialogue_start and line.strip():
                            dialogue_lines.append(line)
                    
                    if dialogue_lines:
                        examples.append('\n'.join(dialogue_lines))
                        if len(examples) >= limit:
                            return examples
            except Exception:
                continue
    
    return examples


def get_category_guide(category: str) -> str:
    """
    카테고리별 특화 가이드 반환
    
    Args:
        category: 상담 카테고리
    
    Returns:
        카테고리별 가이드 문자열
    """
    guides = {
        "연회비 안내": """
**연회비 안내 카테고리 특화 가이드**:
- [금액#N] (연회비 관련): 현실적인 범위 사용 필수
  - 일반 카드: 1만원~5만원 (1만원, 1만5천원, 2만원, 3만원, 5만원)
  - 프리미엄 카드: 10만원~30만원 (10만원, 15만원, 20만원, 30만원)
  - **절대 일반 카드에 15만원 연회비 사용 금지** (비현실적)
- [카드상품명#N]: 실제 카드 상품명 사용 (하나카드 플래티넘, 하나카드 골드 등)
- 문맥상 같은 의미의 금액 태그는 같은 값 사용 (예: "기본 연회비 [금액#1]"과 "기본 연회비 [금액#4]"는 같은 값)
""",
        "자동차 관련": """
**자동차 관련 카테고리 특화 가이드**:
- [금액#N]: 1,000만원~5,000만원 범위 사용 (1,500만원, 2,000만원, 3,000만원 등)
- **절대 15만원 같은 소액 사용 금지** (비현실적)
""",
        "카드론": """
**카드론/대출 카테고리 특화 가이드**:
- [금액#N]: 100만원~1,000만원 범위 사용 (200만원, 500만원, 800만원 등)
""",
        "한도": """
**한도 관련 카테고리 특화 가이드**:
- [금액#N]: 500만원~5,000만원 범위 사용 (1,000만원, 2,000만원, 3,000만원 등)
""",
    }
    
    # 카테고리 키워드 매칭
    for key, guide in guides.items():
        if key in category:
            return guide
    
    return ""


# ===== LLM 기반 시나리오 생성 =====
def generate_scenario_with_llm(tagged_text: str, category: str, model: str = 'gpt-4.1-mini', base_dir: Optional[Path] = None) -> str:
    """
    LLM을 활용하여 태그를 문맥에 맞는 자연스러운 값으로 치환
    
    Args:
        tagged_text: 태그가 포함된 대화 텍스트
        category: 상담 카테고리
        model: 사용할 OpenAI 모델
        base_dir: 기본 디렉토리 (참고 시나리오 검색용)
    
    Returns:
        자연스러운 시나리오 텍스트
    """
    from openai import OpenAI
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("[WARNING] OPENAI_API_KEY not found. Using fallback method.")
        return replace_tags_with_fallback(tagged_text)
    
    client = OpenAI(api_key=api_key)
    
    # 컨텍스트 분석 및 태그 그룹화
    tag_groups = analyze_tag_context(tagged_text)
    
    # 참고 시나리오 예시 가져오기
    if base_dir is None:
        base_dir = Path(__file__).parent
    reference_examples = get_reference_scenarios(category, base_dir, limit=2)
    
    # 카테고리별 특화 가이드
    category_guide = get_category_guide(category)
    
    # 태그 그룹 정보를 프롬프트에 포함
    tag_group_info = ""
    if tag_groups:
        tag_group_info = "\n[태그 그룹 정보 - 같은 의미의 태그는 같은 값 사용]\n"
        for group_name, tags in tag_groups.items():
            unique_tags = list(set(tags))
            if len(unique_tags) > 1:
                tag_group_info += f"- {group_name}: {', '.join(unique_tags)} → 모두 같은 값 사용\n"
    
    # 참고 예시 정보
    example_info = ""
    if reference_examples:
        example_info = "\n[참고 예시 - 유사한 완성된 시나리오]\n"
        for i, example in enumerate(reference_examples, 1):
            example_info += f"\n--- 예시 {i} ---\n{example[:500]}...\n"  # 처음 500자만
        example_info += "\n위 예시들을 참고하여 자연스럽고 일관된 시나리오를 작성하세요.\n"
    
    prompt = f"""당신은 카드사 상담사 교육용 시나리오 작성 전문가입니다.

[작업]
태그([타입#번호])가 포함된 상담 대화를 실제 상담 사례처럼 자연스러운 시나리오로 변환하세요.

[필수 규칙]
1. **같은 태그 번호 = 같은 값**: [금액#1]이 여러 번 나오면 모두 동일한 금액 사용
2. **단위 중복 방지**: 
   - "[금액#1]원" → "15만원" (O)
   - "[금액#1]원" → "15만원원" (X - 절대 금지)
   - "[날짜#1]일" → "25일" (O)
   - "[날짜#1]일" → "25일일" (X - 절대 금지)
3. **문맥 일관성**: 대화 흐름에 맞게 값 선택
   - 같은 거래를 언급하면 같은 금액/날짜 사용
   - 손님이 말한 값을 상담사가 확인할 때 동일한 값 사용
   - **다른 번호의 태그는 반드시 다른 값 사용**
     - [금액#1] = 15만원, [금액#2] = 30만원 (다른 값)
     - [고객명#1] = 홍길동, [고객명#2] = 박철수 (다른 값)
     - 같은 번호만 같은 값, 다른 번호는 절대 같은 값 사용 금지
4. **문맥 오류 자동 감지 및 수정 (가장 중요!)**:
   **원칙**: 태그가 문맥상 자연스럽지 않거나 의미가 통하지 않으면, 태그를 제거하고 문맥에 맞는 자연스러운 표현으로 수정하세요.
   
   **감지 기준**:
   - 태그 뒤에 오는 동사/명사가 태그 타입과 맞지 않는 경우
     예: "[금액#N]을 전화해서" → 금액은 전화할 수 없음 → "가맹점에 전화해서" 또는 "전화해서"
   - 태그가 문법적으로 어색한 위치에 있는 경우
     예: "[금액#N]을 물어보니까" → "전화해서 물어보니까" 또는 "가맹점에 물어보니까"
   - 태그가 대화 흐름을 방해하는 경우
     예: "[날짜#N]을 확인해보니" → "확인해보니" 또는 "내역을 확인해보니"
   
   **수정 방법**:
   - 문맥상 명확한 주체가 있으면 그 주체 사용 (가맹점, 고객센터, 카드사 등)
   - 주체가 불명확하면 태그만 제거하고 자연스러운 표현 사용
   - 절대 무의미한 태그를 그대로 두지 마세요
   
   **예시**:
   - "[금액#2]원을 전화해서 물어보니까" → "가맹점에 전화해서 물어보니까"
   - "[금액#N]을 확인해보니" → "내역을 확인해보니" 또는 "승인 내역을 확인해보니"
   - "[날짜#N]을 문의했는데" → "고객센터에 문의했는데"
   - "[은행명#N]을 결제했어요" → "[은행명#N]으로 결제했어요" (조사 수정)
   - "[전화번호#1] 요건" → "15만원 요건" 또는 "금액 요건" (전화번호 태그는 문맥상 금액이어야 함)
   - "[날짜#1] [날짜#2]" → "25일" 또는 "26일" (단일 날짜로 자연스럽게)
   - "[카드상품명#2] 만들고서" → "하나카드 플래티넘 만들고서" (태그를 실제 카드명으로 치환)
   - "제이든 15만원 30만원" → 문맥상 이상하면 자연스러운 표현으로 수정 (예: "각 카드마다 연회비가 별도로 부과되는 거죠")
5. **원문 구조 유지**: 대화 형식(상담사:/손님:) 절대 변경 금지
6. **카드사명**: 하나카드 교육용이므로 "[카드사명#1]" → "하나카드"로 통일
7. **자연스러운 대화 흐름**: 모든 문장이 실제 상담처럼 자연스럽고 이해하기 쉬워야 함
8. **문맥 기반 태그 그룹화**: 같은 의미의 태그는 반드시 같은 값 사용
   - 예: "기본 연회비 [금액#1]"과 "기본 연회비 [금액#4]"는 같은 값
   - 예: "제휴 [금액#2]"와 "제휴 [금액#5]"는 같은 값
   - 태그 번호가 다르더라도 문맥상 같은 의미면 같은 값 사용

{tag_group_info}

{category_guide}

{example_info}

[태그별 치환 가이드]
- [상담원명#N]: 한국인 이름 (예: 김민정, 이수진, 박지현, 최영희, 정다은) - **각 시나리오마다 다른 이름 사용**
- [고객명#N]: 한국인 이름 (예: 홍길동, 박철수, 이영희, 최지원, 정태웅, 한소율) - **각 시나리오마다 다른 이름 사용**
  - **중요**: 같은 시나리오 내에서는 같은 번호가 같은 이름이지만, 다른 시나리오에서는 다른 이름 사용
- [은행명#N]: 실제 은행명 (국민은행, 신한은행, 우리은행, 하나은행 등)
- [금액#N]: 문맥에 맞는 금액 - **중요: 다른 번호는 다른 금액 사용, 문맥에 맞는 금액 범위 선택**
  - **일반 결제/이용**: 5만원~50만원 (15만원, 30만원, 50만원 등)
  - **자동차 관련 (오토캐시백, 자동차 구매)**: 1,000만원~5,000만원 (1,500만원, 2,000만원, 3,000만원 등)
  - **카드론/대출**: 100만원~1,000만원 (200만원, 500만원, 800만원 등)
  - **한도 관련**: 500만원~5,000만원 (1,000만원, 2,000만원, 3,000만원 등)
  - 같은 번호만 같은 값, 다른 번호는 반드시 다른 값
  - **문맥을 반드시 고려**: 자동차 상담에서 15만원은 부적절 → 1,500만원 이상 사용
- [날짜#N]: 자연스러운 날짜 (10일, 25일, 3월 15일 등)
- [시간#N]: 시간 (오전 10시, 오후 3시 30분 등)
- [전화번호#N]: 010-XXXX-XXXX 형식 (실제 전화번호처럼, XXXX는 숫자로)
  - 예: "010-1234-5678", "010-9876-5432" 등
- [전화번호_구성요소#N]: 전화번호를 나눠서 말할 때 - **중요: 자연스럽게 조합**
  - 상담사: "핸드폰 번호 [전화번호_구성요소#1] 다음 어떻게 되세요?"
  - 손님: "[전화번호_구성요소#2]에 [전화번호_구성요소#3]요."
  - → "010-1234-5678" 형식으로 자연스럽게 조합
  - **절대 "XXXX" 같은 플레이스홀더 사용 금지**
  - **각 구성요소는 실제 숫자로 치환** (예: "010", "1234", "5678")
- [생년월일#N]: YYMMDD 형식 (850315, 901122 등)
- [식별번호_구성요소#N]: 학생식별번호 등을 나눠서 말할 때
  - 숫자 부분: "20230456", "20240012" 등 (학생식별번호의 숫자 부분)
  - **생년월일과 구분**: 생년월일은 YYMMDD(6자리), 식별번호는 더 긴 숫자
- [영문명#N]: 영문 이름 (학생식별번호 앞부분)
  - 예: "KHS", "SJH", "LJM" 등 (대문자 3자리 영문)
  - **한국인 이름과 구분**: "홍길동" 같은 한국 이름이 아님
- [장소명#N]: 가맹점/매장명 (에터미아자몰, 쿠팡, 스타벅스 등)
- [카드사명#N]: 하나카드 (고정)
- [카드상품명#N]: 실제 카드 상품명으로 치환
  - 예: "하나카드 플래티넘", "하나카드 골드", "하나카드 클래식", "하나카드 신한카드 제휴", "하나카드 삼성카드 제휴" 등
  - **절대 "[카드상품명#N]" 그대로 두지 말 것**
  - 문맥에 맞는 실제 카드 상품명 사용
- [서비스업체명#N]: 실제 서비스명으로 치환
  - 하나카드 관련: "하나페이", "하나카드 앱", "하나카드 앱카드" 등
  - 다른 카드사: "삼성페이", "신한페이" 등 (문맥에 맞게)
  - **절대 "서비스업체명" 그대로 두지 말 것**
- [연회비#N]: 연회비 관련 금액 - **중요: 현실적인 범위 사용**
  - **일반 연회비**: 1만원~5만원 (1만원, 1만5천원, 2만원, 3만원, 5만원 등)
  - **프리미엄 카드**: 10만원~30만원 (10만원, 15만원, 20만원, 30만원 등)
  - **절대 일반 카드에 15만원 연회비 사용 금지** (비현실적)
  - 문맥을 반드시 고려: "기본 연회비 15만원"은 부적절 → "기본 연회비 1만5천원" 또는 "프리미엄 카드 연회비 15만원"
- [날짜#N]: 자연스러운 날짜 표현
  - "25일", "3월 15일", "말일" 등
  - **"25일 26일" 같은 어색한 표현 금지** → "25일" 또는 "26일"로 단일 날짜 사용

[카테고리]: {category}

[입력 대화]
{tagged_text}

[출력 형식]
변환된 시나리오만 출력하세요. 설명이나 주석 없이 대화 내용만 출력합니다.
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert in creating realistic call center training scenarios in Korean. Output only the converted dialogue without any explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        result = response.choices[0].message.content.strip()
        return result
        
    except Exception as e:
        print(f"[ERROR] LLM call failed: {e}")
        return replace_tags_with_fallback(tagged_text)


def replace_tags_with_fallback(text: str) -> str:
    """
    LLM 실패 시 간단한 규칙 기반 치환 (백업용)
    단위 중복 문제 해결 포함
    """
    # 태그별 기본값
    defaults = {
        "상담원명": "김민정",
        "고객명": "홍길동",
        "학생명": "김하늘",
        "은행명": "국민은행",
        "카드사명": "하나카드",
        "금액": "15만",  # '원'은 붙이지 않음
        "날짜": "25",    # '일'은 붙이지 않음
        "시간": "오후 3시",
        "전화번호": "010-1234-5678",
        "생년월일": "850315",
        "장소명": "에터미아자몰",
    }
    
    used_values = {}
    
    def replace_tag(match):
        tag_type = match.group(1)
        tag_number = match.group(2)
        key = f"{tag_type}#{tag_number}"
        
        if key not in used_values:
            base_type = tag_type.replace("_구성요소", "")
            if base_type in defaults:
                used_values[key] = defaults[base_type]
            else:
                used_values[key] = f"[값{tag_number}]"
        
        return used_values[key]
    
    # 태그 치환
    result = re.sub(r'\[([^\]#]+)#(\d+)\]', replace_tag, text)
    
    # 번호 없는 태그 처리
    result = re.sub(r'\[개인정보\]', '***', result)
    result = re.sub(r'\[마스킹블록\]', '***', result)
    
    return result


def generate_scenario_from_file(input_path: Path, output_path: Path, use_llm: bool = True) -> Dict:
    """
    전처리된 파일에서 시나리오 생성
    
    Args:
        input_path: 입력 파일 경로 (전처리된 .txt)
        output_path: 출력 파일 경로 (시나리오 .txt)
        use_llm: LLM 사용 여부 (기본값 True)
    
    Returns:
        생성 결과 정보
    """
    start_time = time.time()
    
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 메타데이터 파싱
    lines = content.split('\n')
    metadata = {}
    content_start = 0
    
    for i, line in enumerate(lines):
        if line.startswith('# '):
            key_value = line[2:].split(': ', 1)
            if len(key_value) == 2:
                metadata[key_value[0]] = key_value[1]
        elif line.startswith('='):
            content_start = i + 1
            break
    
    # 실제 대화 내용 추출
    dialogue_lines = lines[content_start:]
    dialogue_text = '\n'.join(dialogue_lines)
    
    # 태그 수 카운트
    tag_count = len(re.findall(r'\[[^\]]+#\d+\]', dialogue_text))
    
    # 시나리오 생성
    category = metadata.get('category', '')
    base_dir = Path(__file__).parent
    if use_llm:
        scenario_text = generate_scenario_with_llm(dialogue_text, category, base_dir=base_dir)
    else:
        scenario_text = replace_tags_with_fallback(dialogue_text)
    
    elapsed = time.time() - start_time
    
    # 출력 파일 생성
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# 상담사 교육용 시나리오\n")
        f.write(f"# 원본 source_id: {metadata.get('source_id', 'N/A')}\n")
        f.write(f"# 카테고리: {category}\n")
        f.write(f"# 시나리오 태그: {metadata.get('scenario_tags', 'N/A')}\n")
        f.write(f"# 생성 방식: {'LLM' if use_llm else 'Fallback'}\n")
        f.write(f"# 생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# 처리 시간: {elapsed:.2f}s\n")
        f.write("=" * 60 + "\n\n")
        f.write(scenario_text)
    
    return {
        "source_id": metadata.get('source_id', 'N/A'),
        "category": category,
        "input_path": str(input_path),
        "output_path": str(output_path),
        "original_length": len(dialogue_text),
        "scenario_length": len(scenario_text),
        "tags_replaced": tag_count,
        "processing_time": round(elapsed, 2),
        "method": "LLM" if use_llm else "Fallback"
    }


def generate_scenarios_batch(source_ids: List[str], input_dir: Path, output_dir: Path, use_llm: bool = True) -> List[Dict]:
    """
    여러 source_id에 대해 시나리오 일괄 생성
    
    Args:
        source_ids: 처리할 source_id 목록
        input_dir: 입력 디렉토리 (전처리된 .txt 파일들)
        output_dir: 출력 디렉토리 (시나리오 .txt 파일들)
        use_llm: LLM 사용 여부
    
    Returns:
        생성 결과 목록
    """
    results = []
    total = len(source_ids)
    
    # tqdm 진행률 표시
    pbar = tqdm(total=total, desc="Generating scenarios", unit="scenario", ncols=100)
    
    for idx, source_id in enumerate(source_ids, 1):
        input_path = input_dir / f"test_{source_id}.txt"
        output_path = output_dir / f"test_scenario_{source_id}.txt"
        
        if not input_path.exists():
            pbar.set_postfix({'status': f'SKIP: {source_id}'})
            pbar.update(1)
            continue
        
        try:
            result = generate_scenario_from_file(input_path, output_path, use_llm=use_llm)
            results.append(result)
            pbar.set_postfix({
                'source_id': source_id,
                'time': format_time(result['processing_time']),
                'tags': result['tags_replaced']
            })
        except Exception as e:
            pbar.set_postfix({'status': f'ERROR: {source_id}'})
            results.append({
                "source_id": source_id,
                "error": str(e)
            })
        
        pbar.update(1)
    
    pbar.close()
    return results


def get_next_version_number(base_dir: Path, prefix: str = 'scenarios_llm_v') -> int:
    """
    기존 버전 폴더를 확인하여 다음 버전 번호 반환
    
    Args:
        base_dir: test_results 디렉토리 경로
        prefix: 버전 폴더 접두사
    
    Returns:
        다음 버전 번호 (예: 1, 2, 3...)
    """
    test_results_dir = base_dir / 'test_results'
    if not test_results_dir.exists():
        return 1
    
    # 기존 버전 폴더 찾기
    existing_versions = []
    for item in test_results_dir.iterdir():
        if item.is_dir() and item.name.startswith(prefix):
            try:
                # scenarios_llm_v01 -> 1
                version_str = item.name.replace(prefix, '')
                version_num = int(version_str)
                existing_versions.append(version_num)
            except ValueError:
                continue
    
    if not existing_versions:
        return 1
    
    return max(existing_versions) + 1


def main():
    """CLI 실행 진입점"""
    import sys
    
    base_dir = Path(__file__).parent
    
    # 입력 디렉토리 설정 (명령줄 인자 또는 기본값)
    if len(sys.argv) > 1 and sys.argv[1] == '--full-run':
        # 전체 데이터 처리 후 시나리오 생성
        input_dir = base_dir / 'test_results' / 'full_run'
    elif len(sys.argv) > 1 and sys.argv[1].startswith('--input='):
        # 사용자 지정 입력 디렉토리
        input_dir = Path(sys.argv[1].split('=')[1])
    else:
        # 기본값: 테스트용 samples_114
        input_dir = base_dir / 'test_results' / 'samples_114'
    
    # 버전 번호 결정 (명령줄 인자 또는 자동)
    if len(sys.argv) > 1 and sys.argv[1].startswith('--version='):
        try:
            version_num = int(sys.argv[1].split('=')[1])
        except (ValueError, IndexError):
            print("[WARNING] Invalid version format. Using auto-increment.")
            version_num = get_next_version_number(base_dir)
    else:
        version_num = get_next_version_number(base_dir)
    
    # 출력 디렉토리 설정 (버전 포함)
    output_dir = base_dir / 'test_results' / f'scenarios_llm_v{version_num:02d}'
    
    # samples_114 폴더에서 카테고리별로 첫 번째 샘플만 선택 (테스트용)
    if input_dir.exists():
        from collections import defaultdict
        
        # 카테고리별로 샘플 그룹화
        category_samples = defaultdict(list)
        
        for txt_file in sorted(input_dir.glob('test_*.txt')):
            source_id = txt_file.stem.replace('test_', '')
            if not source_id.isdigit():
                continue
            
            # 파일에서 카테고리 정보 읽기
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('# category:'):
                            category = line.split(': ', 1)[1].strip()
                            category_samples[category].append(source_id)
                            break
            except Exception as e:
                print(f"[WARNING] Failed to read category from {txt_file.name}: {e}")
                continue
        
        # 입력 디렉토리 확인: full_run 또는 samples_114
        is_full_run = 'full_run' in str(input_dir)
        
        if is_full_run:
            # 전체 데이터 처리 후: 카테고리별 2개씩 선택
            target_ids = []
            for category in sorted(category_samples.keys()):
                samples = category_samples[category]
                # 최대 2개 선택
                target_ids.extend(samples[:2])
            
            if not target_ids:
                print(f"[ERROR] No test files found in {input_dir}")
                return
            
            print(f"[INFO] Full run mode: 2 samples per category")
            print(f"[INFO] Selected {len(target_ids)} samples from {len(category_samples)} categories")
        else:
            # 테스트 모드: 카테고리별 1개씩 선택
            target_ids = []
            for category in sorted(category_samples.keys()):
                if category_samples[category]:
                    target_ids.append(category_samples[category][0])  # 첫 번째만
            
            if not target_ids:
                print(f"[ERROR] No test files found in {input_dir}")
                return
            
            print(f"[INFO] Test mode: 1 sample per category")
            print(f"[INFO] Selected {len(target_ids)} samples from {len(category_samples)} categories")
    else:
        print(f"[ERROR] Input directory not found: {input_dir}")
        return
    
    print("=" * 60)
    print("상담사 교육용 시나리오 생성 (LLM 기반)")
    print("=" * 60)
    print(f"[INFO] Input directory: {input_dir}")
    print(f"[INFO] Output directory: {output_dir}")
    print(f"[INFO] Version: v{version_num:02d}")
    print(f"[INFO] Target scenarios: {len(target_ids)}")
    print(f"[INFO] Method: OpenAI LLM (gpt-4.1-mini)")
    print()
    
    start_time = time.time()
    results = generate_scenarios_batch(target_ids, input_dir, output_dir, use_llm=True)
    total_time = time.time() - start_time
    
    # 요약
    success_count = sum(1 for r in results if 'error' not in r)
    error_count = sum(1 for r in results if 'error' in r)
    
    print()
    print("=" * 60)
    print(f"[COMPLETE] Generated: {success_count}, Errors: {error_count}")
    print(f"[COMPLETE] Total time: {format_time(total_time)}")
    print(f"[COMPLETE] Output directory: {output_dir}")
    
    # 결과 JSON 저장
    summary_path = output_dir / "generation_summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump({
            "version": f"v{version_num:02d}",
            "total_targets": len(target_ids),
            "success_count": success_count,
            "error_count": error_count,
            "total_time_seconds": round(total_time, 2),
            "method": "LLM (gpt-4.1-mini)",
            "created_at": datetime.now().isoformat(),
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"[COMPLETE] Summary saved to: {summary_path}")


if __name__ == '__main__':
    main()
