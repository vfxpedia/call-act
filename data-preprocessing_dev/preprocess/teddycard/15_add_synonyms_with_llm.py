"""
LLM을 사용한 동의어/변형 표현 추가 스크립트

키워드 사전에 동의어와 변형 표현을 자동으로 추가합니다.
LLM을 사용하여 동의어를 추출하고, 수동 검토 후 적용합니다.
"""

import json
import os
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

# 설정 파일 로드
from config import PROJECT_ROOT, SCRIPT_DIR, LLM_CONFIG

# 환경 변수 로드
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

# 파일 경로
INPUT_FILE = SCRIPT_DIR / "keywords_dict_v2.json"
OUTPUT_FILE = SCRIPT_DIR / "keywords_dict_v2_with_synonyms.json"
BACKUP_FILE = SCRIPT_DIR / "keywords_dict_v2_backup.json"


def extract_synonyms_with_llm(keyword: str, category: str) -> Dict[str, List[str]]:
    """
    LLM을 사용하여 동의어와 변형 표현 추출
    
    Args:
        keyword: 키워드
        category: 카테고리
    
    Returns:
        {"synonyms": [...], "variations": [...]}
    """
    if not USE_LLM or not llm_client:
        return {"synonyms": [], "variations": []}
    
    prompt = f"""다음 키워드의 동의어와 변형 표현을 추출하세요.

키워드: {keyword}
카테고리: {category}

요구사항:
1. 동의어: 의미가 동일하거나 매우 유사한 표현 (예: "분실" → "잃어버림", "분실신고")
2. 변형 표현: 문법적 변형 (어미 변화, 존댓말 등) (예: "분실" → "분실했어요", "분실됐어요")
3. 카드 상담 맥락에서 실제로 사용될 수 있는 표현만 추출
4. 각각 최대 5개까지 추출

JSON 형식으로 응답:
{{
    "synonyms": ["동의어1", "동의어2", ...],
    "variations": ["변형1", "변형2", ...]
}}"""

    try:
        response = llm_client.chat.completions.create(
            model=LLM_CONFIG["model"],
            temperature=LLM_CONFIG["temperature"],
            max_tokens=500,
            messages=[
                {"role": "system", "content": "당신은 카드 상담 키워드 분석 전문가입니다."},
                {"role": "user", "content": prompt}
            ]
        )
        
        content = response.choices[0].message.content.strip()
        
        # JSON 추출 (마크다운 코드 블록 제거)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        result = json.loads(content)
        return {
            "synonyms": result.get("synonyms", []),
            "variations": result.get("variations", [])
        }
    except Exception as e:
        print(f"[WARNING] LLM 추출 실패 ({keyword}): {e}")
        return {"synonyms": [], "variations": []}


def add_synonyms_to_keyword(
    keyword_data: Dict,
    keyword: str,
    use_llm: bool = False
) -> Dict:
    """
    키워드에 동의어와 변형 표현 추가
    
    Args:
        keyword_data: 키워드 데이터
        keyword: 키워드
        use_llm: LLM 사용 여부
    
    Returns:
        업데이트된 키워드 데이터
    """
    # 이미 동의어가 있으면 스킵
    if keyword_data.get("synonyms") or keyword_data.get("variations"):
        return keyword_data
    
    # LLM으로 동의어 추출
    if use_llm:
        category = keyword_data["categories"][0]["category"] if keyword_data.get("categories") else "기타"
        synonyms_data = extract_synonyms_with_llm(keyword, category)
        
        keyword_data["synonyms"] = synonyms_data["synonyms"]
        keyword_data["variations"] = synonyms_data["variations"]
    
    return keyword_data


def process_keywords(
    keyword_dict: Dict,
    target_keywords: Optional[List[str]] = None,
    use_llm: bool = False
) -> Dict:
    """
    키워드 사전에 동의어 추가
    
    Args:
        keyword_dict: 키워드 사전
        target_keywords: 처리할 키워드 리스트 (None이면 모든 키워드)
        use_llm: LLM 사용 여부
    
    Returns:
        업데이트된 키워드 사전
    """
    keywords = keyword_dict.get("keywords", {})
    
    if target_keywords:
        # 특정 키워드만 처리
        keywords_to_process = [k for k in target_keywords if k in keywords]
    else:
        # 모든 키워드 처리 (긴급 키워드 우선)
        keywords_to_process = sorted(
            keywords.keys(),
            key=lambda k: max(
                (cat["priority"] for cat in keywords[k].get("categories", [])),
                default=5
            ),
            reverse=True
        )
    
    print(f"[INFO] 처리할 키워드 수: {len(keywords_to_process)}")
    
    for idx, keyword in enumerate(keywords_to_process, 1):
        print(f"[{idx}/{len(keywords_to_process)}] 처리 중: {keyword}")
        
        keyword_data = keywords[keyword]
        updated_data = add_synonyms_to_keyword(keyword_data, keyword, use_llm)
        keywords[keyword] = updated_data
        
        if updated_data.get("synonyms") or updated_data.get("variations"):
            print(f"  - 동의어: {len(updated_data.get('synonyms', []))}개")
            print(f"  - 변형 표현: {len(updated_data.get('variations', []))}개")
    
    keyword_dict["keywords"] = keywords
    return keyword_dict


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description="키워드 사전에 동의어 추가")
    parser.add_argument("--keyword", type=str, help="특정 키워드만 처리")
    parser.add_argument("--use-llm", action="store_true", help="LLM 사용")
    parser.add_argument("--all", action="store_true", help="모든 키워드 처리")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("동의어/변형 표현 추가 시작")
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
    
    # 4. 처리할 키워드 결정
    target_keywords = None
    if args.keyword:
        target_keywords = [args.keyword]
        print(f"[INFO] 특정 키워드 처리: {args.keyword}")
    elif args.all:
        print("[INFO] 모든 키워드 처리")
    else:
        # 기본값: 긴급 키워드만 처리
        urgent_keywords = ["분실", "도난", "정지", "연체", "해지"]
        target_keywords = urgent_keywords
        print(f"[INFO] 긴급 키워드만 처리: {target_keywords}")
    
    # 5. 동의어 추가
    if args.use_llm:
        if not USE_LLM:
            print("[ERROR] LLM을 사용할 수 없습니다. OPENAI_API_KEY를 확인하세요.")
            return
        print(f"[INFO] LLM 모델: {LLM_CONFIG['model']}")
    
    updated_dict = process_keywords(
        keyword_dict,
        target_keywords=target_keywords,
        use_llm=args.use_llm
    )
    
    # 6. 결과 저장
    print(f"[INFO] 결과 저장: {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(updated_dict, f, ensure_ascii=False, indent=2)
    
    # 7. 통계 출력
    total_synonyms = sum(
        len(v.get("synonyms", [])) 
        for v in updated_dict["keywords"].values()
    )
    total_variations = sum(
        len(v.get("variations", [])) 
        for v in updated_dict["keywords"].values()
    )
    
    print("[SUCCESS] 처리 완료!")
    print(f"[INFO] 총 동의어 수: {total_synonyms}")
    print(f"[INFO] 총 변형 표현 수: {total_variations}")
    print(f"[INFO] 결과 파일: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
