"""
테디카드 통합 전처리 - 신한카드 약관 변환

shinhan/terms/*.json 파일을 읽어서 service_guide_documents 형식의 JSON으로 변환
- 텍스트 내 "신한" 관련 표현을 "테디"로 치환
- 임베딩 생성 전 단계 (06_generate_embeddings.py에서 임베딩 생성)
"""

import json
from pathlib import Path
from typing import List, Dict, Any
import sys

# 상위 디렉토리를 경로에 추가
sys.path.append(str(Path(__file__).parent))
from text_replacement import replace_card_brand

# 프로젝트 루트 디렉토리 (data-preprocessing_dev/)
BASE_DIR = Path(__file__).parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data-preprocessing" / "data"
OUTPUT_DIR = BASE_DIR / "data-preprocessing_dev" / "data" / "teddycard"


def convert_shinhan_terms() -> List[Dict[str, Any]]:
    """
    신한카드 약관 데이터를 service_guide_documents 형식으로 변환
    
    Returns:
        service_guide_documents 형식의 리스트
    """
    output_docs = []
    
    # shinhan/terms/final/sinhan_terms_for_vectordb.json 처리
    terms_file = DATA_DIR / "shinhan" / "terms" / "final" / "sinhan_terms_for_vectordb.json"
    if terms_file.exists():
        with open(terms_file, 'r', encoding='utf-8') as f:
            terms_data = json.load(f)
        
        for item in terms_data:
            # 텍스트 치환
            text = replace_card_brand(item.get('text', ''), 'shinhan')
            title = item.get('metadata', {}).get('title', '')
            title = replace_card_brand(title, 'shinhan') if title else ''
            
            # service_guide_documents 형식으로 변환
            doc = {
                'id': item.get('id', ''),
                'document_type': 'terms',
                'category': item.get('metadata', {}).get('category1', ''),
                'title': title,
                'content': text,  # 약관은 text 필드를 content로 사용
                'text': text,  # 임베딩 생성용 텍스트
                'keywords': [],
                'metadata': {
                    'original_source': 'shinhan',
                    'original_id': item.get('id', ''),
                    'original_category1': item.get('metadata', {}).get('category1', ''),
                    'original_category2': item.get('metadata', {}).get('category2', ''),
                    'original_title': item.get('metadata', {}).get('title', ''),
                    'preprocessing_date': '2026-01-11',
                    'preprocessing_version': '1.0'
                }
            }
            output_docs.append(doc)
    
    return output_docs


def main():
    """메인 실행 함수"""
    print("=" * 80)
    print("신한카드 약관 데이터 변환 스크립트")
    print("=" * 80)
    
    # 출력 디렉토리 생성
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 데이터 변환
    print("\n[INFO] 신한카드 약관 데이터 변환 중...")
    docs = convert_shinhan_terms()
    
    print(f"[INFO] 변환 완료: {len(docs)}건")
    
    # JSON 파일로 저장
    output_file = OUTPUT_DIR / "teddycard_service_guides_shinhan.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    
    print(f"[INFO] 저장 완료: {output_file}")
    print("\n" + "=" * 80)
    print("다음 단계: 06_generate_embeddings.py 실행하여 임베딩 생성")
    print("=" * 80)


if __name__ == '__main__':
    main()
