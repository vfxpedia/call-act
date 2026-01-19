"""
테디카드 통합 전처리 - 삼성카드 가이드 변환

samsung/*.json 파일을 읽어서 service_guide_documents 및 notices 형식의 JSON으로 변환
- 텍스트 내 "삼성" 관련 표현을 "테디"로 치환
- 임베딩 생성 전 단계 (06_generate_embeddings.py에서 임베딩 생성)
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import sys

# 상위 디렉토리를 경로에 추가
sys.path.append(str(Path(__file__).parent))
from text_replacement import replace_card_brand
from merge_utils import merge_by_category2

# 프로젝트 루트 디렉토리 (data-preprocessing_dev/)
BASE_DIR = Path(__file__).parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data-preprocessing" / "data"
OUTPUT_DIR = BASE_DIR / "data-preprocessing_dev" / "data" / "teddycard"


def convert_samsung_guides() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    삼성카드 가이드 데이터를 변환
    
    Returns:
        (service_guide_documents 리스트, notices 리스트) 튜플
    """
    service_guides = []
    notices = []
    
    # samsung/creditcard_guide.json 처리 → service_guide_documents
    guide_file = DATA_DIR / "samsung" / "creditcard_guide.json"
    if guide_file.exists():
        with open(guide_file, 'r', encoding='utf-8') as f:
            guide_data = json.load(f)
        
        for item in guide_data:
            # 텍스트 치환
            title = replace_card_brand(item.get('title', ''), 'samsung')
            content = replace_card_brand(item.get('content', ''), 'samsung')
            text = replace_card_brand(item.get('text', ''), 'samsung')
            
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
                    'original_source': 'samsung',
                    'original_id': item.get('id', ''),
                    'original_category1': item.get('metadata', {}).get('category1', ''),
                    'original_category2': item.get('metadata', {}).get('category2', ''),
                    'preprocessing_date': '2026-01-11',
                    'preprocessing_version': '1.0'
                }
            }
            service_guides.append(doc)
    
    # samsung/notice.json 처리 → notices
    notice_file = DATA_DIR / "samsung" / "notice.json"
    if notice_file.exists():
        with open(notice_file, 'r', encoding='utf-8') as f:
            notice_data = json.load(f)
        
        for item in notice_data:
            # 텍스트 치환
            title = replace_card_brand(item.get('title', ''), 'samsung')
            content = replace_card_brand(item.get('content', ''), 'samsung')
            
            # notices 형식으로 변환
            notice = {
                'id': item.get('id', ''),
                'tag': item.get('tag', ''),
                'title': title,
                'content': content,
                'date': item.get('date', ''),
                'metadata': {
                    'original_source': 'samsung',
                    'original_id': item.get('id', ''),
                    'preprocessing_date': '2026-01-11',
                    'preprocessing_version': '1.0'
                }
            }
            notices.append(notice)
    
    return service_guides, notices


def main():
    """메인 실행 함수"""
    print("=" * 80)
    print("삼성카드 가이드 데이터 변환 스크립트")
    print("=" * 80)
    
    # 출력 디렉토리 생성
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 데이터 변환
    print("\n[INFO] 삼성카드 가이드 데이터 변환 중...")
    service_guides, notices = convert_samsung_guides()
    
    print(f"[INFO] 변환 완료: service_guides {len(service_guides)}건, notices {len(notices)}건")
    
    # Category2 기준 통합
    print("\n[INFO] Category2 기준 문서 통합 중...")
    service_guides_before = len(service_guides)
    service_guides = merge_by_category2(service_guides)
    service_guides_after = len(service_guides)
    merged_count = service_guides_before - service_guides_after
    
    if merged_count > 0:
        print(f"[INFO] 통합 완료: {service_guides_before}건 → {service_guides_after}건 (통합: {merged_count}건)")
    else:
        print(f"[INFO] 통합 대상 없음: {service_guides_after}건 유지")
    
    # JSON 파일로 저장
    if service_guides:
        output_file = OUTPUT_DIR / "teddycard_service_guides_samsung.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(service_guides, f, ensure_ascii=False, indent=2)
        print(f"[INFO] 저장 완료: {output_file}")
    
    if notices:
        output_file = OUTPUT_DIR / "teddycard_notices.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(notices, f, ensure_ascii=False, indent=2)
        print(f"[INFO] 저장 완료: {output_file}")
    
    print("\n" + "=" * 80)
    print("다음 단계: 06_generate_embeddings.py 실행하여 임베딩 생성")
    print("=" * 80)


if __name__ == '__main__':
    main()
