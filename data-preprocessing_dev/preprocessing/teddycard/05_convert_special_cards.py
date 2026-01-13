"""
테디카드 통합 전처리 - 스페셜 카드 변환

special_card/*.json 파일을 읽어서 card_products 및 service_guide_documents 형식의 JSON으로 변환
- 스페셜 카드는 치환하지 않음 (제휴 카드 정보 보존)
- 임베딩 생성 전 단계 (06_generate_embeddings.py에서 임베딩 생성)
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import sys

# 상위 디렉토리를 경로에 추가
sys.path.append(str(Path(__file__).parent))
from text_replacement import replace_card_brand

# 프로젝트 루트 디렉토리 (data-preprocessing_dev/)
BASE_DIR = Path(__file__).parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data-preprocessing" / "data"
OUTPUT_DIR = BASE_DIR / "data-preprocessing_dev" / "preprocessing" / "output"


def convert_special_cards() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    스페셜 카드 데이터를 변환 (치환하지 않음)
    
    Returns:
        (card_products 리스트, service_guide_documents 리스트) 튜플
    """
    card_products = []
    service_guides = []
    
    # special_card/*.json 파일들 처리
    special_card_dir = DATA_DIR / "special_card"
    if special_card_dir.exists():
        # special_terms.json, special_terms_formatted.json 처리 → service_guide_documents
        for json_file in special_card_dir.glob("special_*.json"):
            if json_file.name in ['special_terms.json', 'special_terms_formatted.json']:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for item in data:
                    # 스페셜 카드는 치환하지 않음
                    title = item.get('title', '')
                    content = item.get('content', '')
                    text = item.get('text', '')
                    
                    # service_guide_documents 형식으로 변환
                    doc = {
                        'id': item.get('id', ''),
                        'document_type': 'terms',
                        'category': item.get('metadata', {}).get('category', ''),
                        'title': title,
                        'content': content if content else text,
                        'text': text,
                        'keywords': [],
                        'metadata': {
                            'original_source': 'special_card',
                            'original_id': item.get('id', ''),
                            'original_category': item.get('metadata', {}).get('category', ''),
                            'original_card_name': item.get('metadata', {}).get('card_name', ''),
                            'preprocessing_date': '2026-01-11',
                            'preprocessing_version': '1.0'
                        }
                    }
                    service_guides.append(doc)
        
        # FAQ 파일들도 service_guide_documents로 변환
        for json_file in special_card_dir.glob("*_faq.json"):
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for item in data:
                # 스페셜 카드는 치환하지 않음
                title = item.get('title', '')
                content = item.get('content', '')
                text = item.get('text', '')
                
                doc = {
                    'id': item.get('id', ''),
                    'document_type': 'faq',
                    'category': item.get('metadata', {}).get('category', ''),
                    'title': title,
                    'content': content if content else text,
                    'text': text,
                    'keywords': [],
                    'metadata': {
                        'original_source': 'special_card',
                        'original_id': item.get('id', ''),
                        'original_category': item.get('metadata', {}).get('category', ''),
                        'original_card_name': item.get('metadata', {}).get('card_name', ''),
                        'preprocessing_date': '2026-01-11',
                        'preprocessing_version': '1.0'
                    }
                }
                service_guides.append(doc)
    
    return card_products, service_guides


def main():
    """메인 실행 함수"""
    print("=" * 80)
    print("스페셜 카드 데이터 변환 스크립트")
    print("=" * 80)
    
    # 출력 디렉토리 생성
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 데이터 변환
    print("\n[INFO] 스페셜 카드 데이터 변환 중...")
    card_products, service_guides = convert_special_cards()
    
    print(f"[INFO] 변환 완료: card_products {len(card_products)}건, service_guides {len(service_guides)}건")
    
    # JSON 파일로 저장
    if card_products:
        output_file = OUTPUT_DIR / "teddycard_card_products_special.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(card_products, f, ensure_ascii=False, indent=2)
        print(f"[INFO] 저장 완료: {output_file}")
    
    if service_guides:
        output_file = OUTPUT_DIR / "teddycard_service_guides_special.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(service_guides, f, ensure_ascii=False, indent=2)
        print(f"[INFO] 저장 완료: {output_file}")
    
    print("\n" + "=" * 80)
    print("다음 단계: 06_generate_embeddings.py 실행하여 임베딩 생성")
    print("=" * 80)


if __name__ == '__main__':
    main()
