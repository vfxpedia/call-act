"""
테디카드 통합 전처리 - 키워드 추출

전처리된 JSON 파일들에서 키워드를 추출하여 keywords 필드를 채움
- 방법 1: 단어사전 기반 키워드 매칭
- 방법 2: LLM 기반 키워드 추출 (보완)
- 하이브리드: 단어사전 + LLM

주의: STT 키워드 추출 정밀도 향상을 위해 단어사전 기반 추출이 핵심
"""

import json
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Set
import sys
from collections import defaultdict
from dotenv import load_dotenv

# 환경 변수 로드
BASE_DIR = Path(__file__).resolve().parents[3]  # call-act
load_dotenv(BASE_DIR / '.env', override=False)

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
BASE_DIR = Path(__file__).parent.parent.parent.parent
KEYWORDS_DICT_FILE = Path(__file__).parent / "keywords_dict.json"
OUTPUT_DIR = BASE_DIR / "data-preprocessing_dev" / "preprocessing" / "output"

# 단어사전 로드
def load_keywords_dict() -> Dict[str, List[str]]:
    """키워드 사전 로드"""
    if KEYWORDS_DICT_FILE.exists():
        with open(KEYWORDS_DICT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# 키워드 사전
KEYWORDS_DICT = load_keywords_dict()

# 역인덱스: 키워드 → 카테고리 매핑 (빠른 검색용)
KEYWORD_TO_CATEGORY = {}
for category, keywords in KEYWORDS_DICT.items():
    for keyword in keywords:
        KEYWORD_TO_CATEGORY[keyword.lower()] = category


def extract_keywords_from_dict(text: str) -> List[str]:
    """
    단어사전 기반 키워드 추출
    텍스트에서 키워드 사전에 있는 단어들을 찾아 반환
    """
    if not text:
        return []
    
    found_keywords = set()
    text_lower = text.lower()
    
    # 각 키워드를 텍스트에서 검색
    for keyword, category in KEYWORD_TO_CATEGORY.items():
        if keyword in text_lower:
            found_keywords.add(keyword)
    
    # 카테고리별로 정렬하여 반환 (중요도 순서)
    keyword_list = list(found_keywords)
    return sorted(keyword_list)


def extract_keywords_with_llm(title: str, content: str, existing_keywords: List[str] = None) -> List[str]:
    """
    LLM을 사용하여 추가 키워드 추출
    단어사전에서 찾지 못한 중요한 키워드를 보완
    """
    if not USE_LLM:
        return existing_keywords or []
    
    try:
        prompt = f"""
다음 문서에서 카드 상담 시 고객이 자주 묻는 핵심 키워드를 추출하세요.

제목: {title}
내용: {content[:1000]}

기존 키워드: {', '.join(existing_keywords) if existing_keywords else '없음'}

요구사항:
1. 기존 키워드와 중복되지 않는 추가 키워드만 추출
2. 카드 상담 맥락에서 의미있는 키워드만 추출
3. 최대 5개까지 추출
4. 키워드는 한글 또는 영문으로 작성

JSON 형식으로 응답:
{{"keywords": ["키워드1", "키워드2", ...]}}
"""
        
        response = llm_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        llm_keywords = result.get("keywords", [])
        
        # 기존 키워드와 병합 (중복 제거)
        all_keywords = list(set((existing_keywords or []) + llm_keywords))
        return all_keywords[:10]  # 최대 10개로 제한
    
    except Exception as e:
        print(f"[WARNING] LLM 키워드 추출 실패: {e}, 단어사전 키워드만 사용")
        return existing_keywords or []


def extract_keywords_hybrid(doc: Dict[str, Any], use_llm: bool = False) -> List[str]:
    """
    하이브리드 키워드 추출:
    1. 단어사전 기반 키워드 추출 (필수)
    2. LLM 기반 키워드 추출 (선택적 보완)
    """
    # 텍스트 추출 (title + content/text)
    title = doc.get("title", "")
    content = doc.get("content", "") or doc.get("text", "")
    full_text = f"{title} {content}"
    
    # 1. 단어사전 기반 추출
    dict_keywords = extract_keywords_from_dict(full_text)
    
    # 2. LLM 기반 보완 (옵션)
    if use_llm and USE_LLM:
        all_keywords = extract_keywords_with_llm(title, content, dict_keywords)
    else:
        all_keywords = dict_keywords
    
    # 최대 10개로 제한
    return all_keywords[:10]


def extract_keywords_for_documents(
    documents: List[Dict[str, Any]],
    use_llm: bool = False,
    batch_size: int = 100
) -> List[Dict[str, Any]]:
    """
    문서들에 대해 키워드 추출
    """
    print(f"[INFO] 키워드 추출 시작: {len(documents)}개 문서")
    print(f"[INFO] LLM 사용: {use_llm and USE_LLM}")
    
    results = []
    llm_count = 0
    
    for idx, doc in enumerate(documents):
        # 단어사전 기반 추출
        keywords = extract_keywords_from_dict(
            f"{doc.get('title', '')} {doc.get('content', '') or doc.get('text', '')}"
        )
        
        # LLM 보완 (일부 문서에만 적용 - 성능 최적화)
        if use_llm and USE_LLM:
            # 카테고리나 중요도에 따라 선택적으로 LLM 사용
            # 예: 중요한 문서나 키워드가 적은 문서에만 LLM 사용
            if len(keywords) < 3 or idx % 10 == 0:  # 키워드가 적거나 10개마다 1개씩
                keywords = extract_keywords_with_llm(
                    doc.get("title", ""),
                    doc.get("content", "") or doc.get("text", ""),
                    keywords
                )
                llm_count += 1
        
        # 키워드 업데이트
        doc["keywords"] = keywords
        results.append(doc)
        
        if (idx + 1) % 100 == 0:
            print(f"  진행: {idx + 1}/{len(documents)} (LLM 사용: {llm_count}건)")
    
    print(f"[INFO] 키워드 추출 완료: {len(results)}개 문서 (LLM 사용: {llm_count}건)")
    return results


def process_file(file_path: Path, use_llm: bool = False) -> bool:
    """단일 JSON 파일 처리"""
    if not file_path.exists():
        print(f"[WARNING] 파일을 찾을 수 없습니다: {file_path}")
        return False
    
    print(f"\n[INFO] 처리 중: {file_path.name}")
    
    # JSON 파일 로드
    with open(file_path, 'r', encoding='utf-8') as f:
        documents = json.load(f)
    
    if not isinstance(documents, list):
        documents = [documents]
    
    # 키워드 추출
    documents_with_keywords = extract_keywords_for_documents(documents, use_llm=use_llm)
    
    # 저장
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(documents_with_keywords, f, ensure_ascii=False, indent=2)
    
    print(f"[INFO] 저장 완료: {file_path}")
    
    # 통계 출력
    total_keywords = sum(len(doc.get("keywords", [])) for doc in documents_with_keywords)
    avg_keywords = total_keywords / len(documents_with_keywords) if documents_with_keywords else 0
    docs_with_keywords = sum(1 for doc in documents_with_keywords if doc.get("keywords"))
    
    print(f"[INFO] 통계:")
    print(f"  - 총 문서 수: {len(documents_with_keywords)}건")
    print(f"  - 키워드가 있는 문서: {docs_with_keywords}건 ({docs_with_keywords/len(documents_with_keywords)*100:.1f}%)")
    print(f"  - 평균 키워드 수: {avg_keywords:.1f}개")
    
    return True


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract keywords for TeddyCard documents")
    parser.add_argument('--use-llm', action='store_true', help='Use LLM for keyword extraction (supplement)')
    parser.add_argument('--file', type=str, help='Process specific file only')
    args = parser.parse_args()
    
    print("=" * 80)
    print("테디카드 통합 전처리 - 키워드 추출 스크립트")
    print("=" * 80)
    print(f"[INFO] 단어사전 로드: {len(KEYWORDS_DICT)}개 카테고리, {len(KEYWORD_TO_CATEGORY)}개 키워드")
    print(f"[INFO] LLM 사용 가능: {USE_LLM}")
    print(f"[INFO] LLM 보완 모드: {args.use_llm and USE_LLM}")
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 처리할 파일 목록
    if args.file:
        # 특정 파일만 처리
        file_path = OUTPUT_DIR / args.file
        if file_path.exists():
            process_file(file_path, use_llm=args.use_llm)
        else:
            print(f"[ERROR] 파일을 찾을 수 없습니다: {file_path}")
    else:
        # enriched 파일 우선 처리 (07_enrich_for_db.py 이후 실행 시 enriched 파일 사용)
        files_to_process = []
        
        # enriched 파일 확인 (있으면 사용, 없으면 원본 파일 사용)
        enriched_files = [
            "teddycard_service_guides_enriched.json",
            "teddycard_card_products_enriched.json",
            "teddycard_notices_enriched.json",
        ]
        
        original_files = [
            "teddycard_service_guides_samsung.json",
            "teddycard_service_guides_hyundai.json",
            "teddycard_service_guides_shinhan.json",
            "teddycard_service_guides_special.json",
            "teddycard_card_products.json",
            "teddycard_notices.json",
        ]
        
        # enriched 파일이 있으면 enriched 파일 사용, 없으면 원본 파일 사용
        for enriched_file in enriched_files:
            enriched_path = OUTPUT_DIR / enriched_file
            if enriched_path.exists():
                files_to_process.append(enriched_file)
                print(f"[INFO] enriched 파일 사용: {enriched_file}")
            else:
                # enriched 파일이 없으면 해당하는 원본 파일 사용
                if enriched_file == "teddycard_service_guides_enriched.json":
                    # service_guides는 개별 파일로 분리되어 있음
                    for orig_file in original_files[:4]:  # service_guides 관련 파일들
                        if (OUTPUT_DIR / orig_file).exists():
                            files_to_process.append(orig_file)
                elif enriched_file == "teddycard_card_products_enriched.json":
                    if (OUTPUT_DIR / "teddycard_card_products.json").exists():
                        files_to_process.append("teddycard_card_products.json")
                elif enriched_file == "teddycard_notices_enriched.json":
                    if (OUTPUT_DIR / "teddycard_notices.json").exists():
                        files_to_process.append("teddycard_notices.json")
        
        processed = 0
        for filename in files_to_process:
            file_path = OUTPUT_DIR / filename
            if process_file(file_path, use_llm=args.use_llm):
                processed += 1
        
        print("\n" + "=" * 80)
        print(f"키워드 추출 완료: {processed}/{len(files_to_process)}개 파일 처리")
        print("=" * 80)


if __name__ == '__main__':
    main()
