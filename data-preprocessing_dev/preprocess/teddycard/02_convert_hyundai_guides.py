"""
테디카드 통합 전처리 - 현대카드 가이드 변환

hyundai/*.json 파일을 읽어서 service_guide_documents 형식의 JSON으로 변환
- 텍스트 내 "현대" 관련 표현을 "테디"로 치환
- 임베딩 생성 전 단계 (06_generate_embeddings.py에서 임베딩 생성)
"""

import json
from pathlib import Path
from typing import List, Dict, Any
import sys

# 상위 디렉토리를 경로에 추가
sys.path.append(str(Path(__file__).parent))
from text_replacement import replace_card_brand
from merge_utils import merge_by_category2

# 프로젝트 루트 디렉토리 (data-preprocessing_dev/)
BASE_DIR = Path(__file__).parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data-preprocessing" / "data"
OUTPUT_DIR = BASE_DIR / "data-preprocessing_dev" / "data" / "teddycard"


def convert_hyundai_guides() -> List[Dict[str, Any]]:
    """
    현대카드 가이드 데이터를 service_guide_documents 형식으로 변환
    
    Returns:
        service_guide_documents 형식의 리스트
    """
    output_docs = []
    
    # hyundai/applepay.json 처리
    applepay_file = DATA_DIR / "hyundai" / "applepay.json"
    if applepay_file.exists():
        with open(applepay_file, 'r', encoding='utf-8') as f:
            applepay_data = json.load(f)
        
        for item in applepay_data:
            # 텍스트 치환
            title = replace_card_brand(item.get('title', ''), 'hyundai')
            content = replace_card_brand(item.get('content', ''), 'hyundai')
            text = replace_card_brand(item.get('text', ''), 'hyundai')
            
            # service_guide_documents 형식으로 변환
            doc = {
                'id': item.get('id', ''),
                'document_type': 'usage_guide',
                'category': item.get('metadata', {}).get('category1', ''),
                'title': title,
                'content': content,
                'text': text,  # 임베딩 생성용 텍스트
                'keywords': [],  # 키워드는 나중에 추출하거나 빈 배열로 시작
                'metadata': {
                    'original_source': 'hyundai',
                    'original_id': item.get('id', ''),
                    'original_category1': item.get('metadata', {}).get('category1', ''),
                    'original_category2': item.get('metadata', {}).get('category2', ''),
                    'preprocessing_date': '2026-01-11',
                    'preprocessing_version': '1.0'
                }
            }
            output_docs.append(doc)
    
    # hyundai/hyundai_giftcard.json 처리
    giftcard_file = DATA_DIR / "hyundai" / "hyundai_giftcard.json"
    if giftcard_file.exists():
        with open(giftcard_file, 'r', encoding='utf-8') as f:
            giftcard_data = json.load(f)
        
        for item in giftcard_data:
            # 텍스트 치환
            title = replace_card_brand(item.get('title', ''), 'hyundai')
            content = replace_card_brand(item.get('content', ''), 'hyundai')
            text = replace_card_brand(item.get('text', ''), 'hyundai')
            
            # service_guide_documents 형식으로 변환
            doc = {
                'id': item.get('id', ''),
                'document_type': 'service_guide',
                'category': item.get('metadata', {}).get('category1', ''),
                'title': title,
                'content': content,
                'text': text,
                'keywords': [],
                'metadata': {
                    'original_source': 'hyundai',
                    'original_id': item.get('id', ''),
                    'original_category1': item.get('metadata', {}).get('category1', ''),
                    'original_category2': item.get('metadata', {}).get('category2', ''),
                    'preprocessing_date': '2026-01-11',
                    'preprocessing_version': '1.0'
                }
            }
            output_docs.append(doc)
    
    return output_docs


def main():
    """메인 실행 함수"""
    print("=" * 80)
    print("현대카드 가이드 데이터 변환 스크립트")
    print("=" * 80)
    
    # 출력 디렉토리 생성
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 데이터 변환
    print("\n[INFO] 현대카드 가이드 데이터 변환 중...")
    docs = convert_hyundai_guides()
    
    print(f"[INFO] 변환 완료: {len(docs)}건")
    
    # Category2 기준 통합 (선택적)
    print("\n[INFO] Category2 기준 문서 통합 중...")
    docs_before = len(docs)
    docs = merge_by_category2(docs)
    docs_after = len(docs)
    merged_count = docs_before - docs_after
    
    if merged_count > 0:
        print(f"[INFO] 통합 완료: {docs_before}건 → {docs_after}건 (통합: {merged_count}건)")
    else:
        print(f"[INFO] 통합 대상 없음: {docs_after}건 유지")
    
    # JSON 파일로 저장 (임베딩 생성 전 단계)
    output_file = OUTPUT_DIR / "teddycard_service_guides_hyundai.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    
    print(f"[INFO] 저장 완료: {output_file}")
    print("\n" + "=" * 80)
    print("다음 단계: 06_generate_embeddings.py 실행하여 임베딩 생성")
    print("=" * 80)


if __name__ == '__main__':
    main()
