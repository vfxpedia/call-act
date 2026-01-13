"""
테디카드 통합 전처리 - 하나카드 데이터에서 키워드 사전 생성

하나카드 상담 데이터(hana_vectordb.json)에서 키워드를 수집하여
기존 keywords_dict.json을 보완하는 스크립트

1. 하나카드 데이터의 metadata.keywords 수집
2. 카테고리별 키워드 통계 분석
3. (선택적) LLM 보완을 위한 샘플 선택 및 처리
4. 기존 keywords_dict.json과 병합
5. 최종 키워드 사전 저장
"""

import json
import os
import random
from pathlib import Path
from typing import Dict, List, Set, Any
from collections import defaultdict, Counter
from dotenv import load_dotenv

# 설정 파일 로드
from config import PROJECT_ROOT, HANA_DATA_FILE, KEYWORDS_DICT_FILE, SCRIPT_DIR

# 환경 변수 로드 (API 키만 .env에서)
load_dotenv(PROJECT_ROOT / '.env', override=False)

# OpenAI 클라이언트 (LLM 보완용)
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
OUTPUT_DIR = SCRIPT_DIR
OUTPUT_FILE = OUTPUT_DIR / "keywords_dict_updated.json"
BACKUP_FILE = OUTPUT_DIR / "keywords_dict_backup.json"

# 카테고리 매핑: 하나카드 카테고리 → 테디카드 카테고리
CATEGORY_MAPPING = {
    "도난/분실 신청/해제": "분실도난",
    "이용내역 안내": "결제",
    "오토할부/오토캐쉬백 안내/신청/취소": "대출",
    "선결제/즉시출금": "대출",
    "한도상향 접수/처리": "대출",
    "연회비 안내": "연회비",
    "포인트/마일리지 안내": "포인트",
    "할인/혜택 안내": "혜택",
    "해외이용 안내": "해외",
    "본인확인/인증": "본인확인",
    "가맹점 문의": "가맹점",
    "모바일/앱 관련": "모바일",
    "신용도/신용등급": "신용도",
    "연체/이자": "연체",
    # 추가 매핑은 필요에 따라 확장
}


def load_hana_data() -> List[Dict[str, Any]]:
    """하나카드 데이터 로드"""
    if not HANA_DATA_FILE.exists():
        raise FileNotFoundError(f"하나카드 데이터 파일을 찾을 수 없습니다: {HANA_DATA_FILE}")
    
    print(f"[INFO] 하나카드 데이터 로드 중: {HANA_DATA_FILE}")
    with open(HANA_DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"[INFO] 총 {len(data)}건의 상담 데이터 로드 완료")
    return data


def collect_keywords_from_hana(data: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    하나카드 데이터에서 키워드 수집 및 통계 분석
    
    Returns:
        {
            "카테고리명": {
                "keywords": [키워드 리스트],
                "frequency": {키워드: 빈도},
                "doc_count": 문서 수
            }
        }
    """
    category_keywords = defaultdict(lambda: {"keywords": [], "frequency": Counter(), "doc_count": 0})
    
    for doc in data:
        metadata = doc.get("metadata", {})
        category = metadata.get("category", "기타")
        keywords = metadata.get("keywords", [])
        
        # 카테고리 매핑 적용
        mapped_category = CATEGORY_MAPPING.get(category, category)
        
        # 키워드 수집
        for keyword in keywords:
            if keyword and isinstance(keyword, str):
                keyword_lower = keyword.lower().strip()
                if keyword_lower:
                    category_keywords[mapped_category]["keywords"].append(keyword_lower)
                    category_keywords[mapped_category]["frequency"][keyword_lower] += 1
        
        category_keywords[mapped_category]["doc_count"] += 1
    
    # 중복 제거 및 빈도 정렬
    result = {}
    for category, info in category_keywords.items():
        # 빈도순으로 정렬하여 상위 키워드 추출
        top_keywords = [kw for kw, _ in info["frequency"].most_common(50)]
        result[category] = {
            "keywords": list(set(top_keywords)),  # 중복 제거
            "frequency": dict(info["frequency"]),
            "doc_count": info["doc_count"]
        }
    
    return result


def select_samples_for_llm(data: List[Dict[str, Any]], samples_per_category: int = 5) -> List[Dict[str, Any]]:
    """
    LLM 보완을 위한 샘플 선택
    카테고리별로 대표 샘플 선택 (빈도 기반 + 랜덤)
    """
    # 카테고리별 문서 그룹화
    category_docs = defaultdict(list)
    for doc in data:
        metadata = doc.get("metadata", {})
        category = metadata.get("category", "기타")
        mapped_category = CATEGORY_MAPPING.get(category, category)
        category_docs[mapped_category].append(doc)
    
    selected_samples = []
    
    for category, docs in category_docs.items():
        if len(docs) == 0:
            continue
        
        # 샘플 수 결정 (카테고리별 문서 수에 비례, 최소 3개, 최대 samples_per_category개)
        sample_count = min(max(3, len(docs) // 10), samples_per_category)
        sample_count = min(sample_count, len(docs))
        
        # 빈도 기반 샘플: 키워드가 많은 문서 우선
        docs_with_keyword_count = [(doc, len(doc.get("metadata", {}).get("keywords", []))) for doc in docs]
        docs_with_keyword_count.sort(key=lambda x: x[1], reverse=True)
        
        # 상위 50%에서 선택
        top_half = docs_with_keyword_count[:max(1, len(docs_with_keyword_count) // 2)]
        
        # 빈도 기반 샘플 선택 (60%)
        freq_samples = [doc for doc, _ in top_half[:int(sample_count * 0.6)]]
        
        # 랜덤 샘플 선택 (40%, 다양성 확보)
        remaining_docs = [doc for doc, _ in docs_with_keyword_count if doc not in freq_samples]
        random_samples = random.sample(remaining_docs, min(int(sample_count * 0.4), len(remaining_docs)))
        
        selected_samples.extend(freq_samples + random_samples)
    
    print(f"[INFO] LLM 보완을 위한 샘플 {len(selected_samples)}건 선택 완료")
    return selected_samples


def extract_keywords_with_llm(title: str, content: str, existing_keywords: List[str]) -> List[str]:
    """LLM을 사용하여 추가 키워드 추출"""
    if not USE_LLM:
        return []
    
    try:
        prompt = f"""
다음 카드 상담 문서에서 고객이 자주 묻는 핵심 키워드를 추출하세요.
기존 키워드 사전에 없는 새로운 키워드를 찾아주세요.

제목: {title}
내용: {content[:1500]}

기존 키워드: {', '.join(existing_keywords[:10]) if existing_keywords else '없음'}

요구사항:
1. 기존 키워드와 중복되지 않는 추가 키워드만 추출
2. 카드 상담 맥락에서 의미있는 키워드만 추출
3. 최대 10개까지 추출
4. 키워드는 한글 또는 영문으로 작성

JSON 형식으로 응답:
{{"keywords": ["키워드1", "키워드2", ...]}}
"""
        
        response = llm_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 카드 상담 키워드 추출 전문가입니다. JSON 형식으로만 응답하세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # JSON 파싱
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        result = json.loads(response_text)
        keywords = result.get("keywords", [])
        
        return [kw.lower().strip() for kw in keywords if kw and isinstance(kw, str)]
    
    except Exception as e:
        print(f"[WARNING] LLM 키워드 추출 실패: {e}")
        return []


def merge_keywords_dicts(
    existing_dict: Dict[str, List[str]],
    hana_keywords: Dict[str, Dict[str, Any]],
    llm_keywords: Dict[str, Set[str]] = None
) -> Dict[str, List[str]]:
    """
    기존 키워드 사전과 하나카드 키워드 병합
    
    병합 전략:
    1. 하나카드 키워드가 우선 (실제 사용 빈도 기반)
    2. 기존 사전은 하나카드에 없는 키워드 추가
    3. LLM 보완 키워드 추가
    """
    merged = {}
    
    # 모든 카테고리 수집
    all_categories = set(existing_dict.keys()) | set(hana_keywords.keys())
    if llm_keywords:
        all_categories |= set(llm_keywords.keys())
    
    for category in all_categories:
        merged_keywords = set()
        
        # 1. 하나카드 키워드 추가 (우선순위 1)
        if category in hana_keywords:
            hana_kws = hana_keywords[category]["keywords"]
            merged_keywords.update(hana_kws)
        
        # 2. 기존 사전 키워드 추가 (하나카드에 없는 것만)
        if category in existing_dict:
            existing_kws = [kw.lower() for kw in existing_dict[category]]
            merged_keywords.update(existing_kws)
        
        # 3. LLM 보완 키워드 추가
        if llm_keywords and category in llm_keywords:
            merged_keywords.update(llm_keywords[category])
        
        # 정렬하여 리스트로 변환
        merged[category] = sorted(list(merged_keywords))
    
    return merged


def main():
    """메인 실행 함수"""
    print("=" * 80)
    print("하나카드 데이터에서 키워드 사전 생성")
    print("=" * 80)
    
    # 1. 기존 키워드 사전 로드
    existing_dict = {}
    if KEYWORDS_DICT_FILE.exists():
        with open(KEYWORDS_DICT_FILE, 'r', encoding='utf-8') as f:
            existing_dict = json.load(f)
        print(f"[INFO] 기존 키워드 사전 로드: {len(existing_dict)}개 카테고리")
        
        # 백업 생성
        with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
            json.dump(existing_dict, f, ensure_ascii=False, indent=2)
        print(f"[INFO] 기존 키워드 사전 백업: {BACKUP_FILE}")
    else:
        print("[WARNING] 기존 키워드 사전을 찾을 수 없습니다. 새로 생성합니다.")
    
    # 2. 하나카드 데이터 로드
    hana_data = load_hana_data()
    
    # 3. 키워드 수집 및 통계 분석
    print("\n[INFO] 하나카드 데이터에서 키워드 수집 중...")
    hana_keywords = collect_keywords_from_hana(hana_data)
    
    print(f"\n[INFO] 카테고리별 키워드 통계:")
    for category, info in sorted(hana_keywords.items(), key=lambda x: x[1]["doc_count"], reverse=True):
        print(f"  {category}: {len(info['keywords'])}개 키워드, {info['doc_count']}건 문서")
    
    # 4. LLM 보완 (선택적)
    llm_keywords = defaultdict(set)
    if USE_LLM:
        print("\n[INFO] LLM 보완을 위한 샘플 선택 및 처리 중...")
        samples = select_samples_for_llm(hana_data, samples_per_category=5)
        
        print(f"[INFO] LLM 키워드 추출 진행 중... (총 {len(samples)}건)")
        for idx, doc in enumerate(samples, 1):
            if idx % 10 == 0:
                print(f"  진행 중: {idx}/{len(samples)}")
            
            metadata = doc.get("metadata", {})
            category = metadata.get("category", "기타")
            mapped_category = CATEGORY_MAPPING.get(category, category)
            
            title = doc.get("title", "")
            content = doc.get("content", "")[:2000]  # 처음 2000자만
            existing_kws = metadata.get("keywords", [])
            
            new_keywords = extract_keywords_with_llm(title, content, existing_kws)
            if new_keywords:
                llm_keywords[mapped_category].update(new_keywords)
        
        print(f"[INFO] LLM 보완 완료: {sum(len(kws) for kws in llm_keywords.values())}개 추가 키워드")
    else:
        print("\n[INFO] LLM 보완 건너뜀 (OPENAI_API_KEY 없음)")
    
    # 5. 키워드 사전 병합
    print("\n[INFO] 키워드 사전 병합 중...")
    merged_dict = merge_keywords_dicts(existing_dict, hana_keywords, llm_keywords)
    
    # 6. 최종 키워드 사전 저장
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(merged_dict, f, ensure_ascii=False, indent=2)
    
    print(f"\n[INFO] 최종 키워드 사전 저장: {OUTPUT_FILE}")
    print(f"[INFO] 총 {len(merged_dict)}개 카테고리, {sum(len(kws) for kws in merged_dict.values())}개 키워드")
    
    # 통계 출력
    print("\n" + "=" * 80)
    print("키워드 사전 업데이트 완료")
    print("=" * 80)
    print(f"기존: {len(existing_dict)}개 카테고리, {sum(len(kws) for kws in existing_dict.values())}개 키워드")
    print(f"업데이트: {len(merged_dict)}개 카테고리, {sum(len(kws) for kws in merged_dict.values())}개 키워드")
    print(f"\n백업 파일: {BACKUP_FILE}")
    print(f"새 파일: {OUTPUT_FILE}")
    print("\n[INFO] keywords_dict.json을 업데이트하려면 수동으로 복사하거나 이름을 변경하세요.")


if __name__ == "__main__":
    main()
