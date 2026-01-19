"""
테디카드 통합 전처리 - 신한카드 카드 정보 변환

shinhan/card_info/*.md 파일을 읽어서 card_products 형식의 JSON으로 변환
- 텍스트 내 "신한" 관련 표현을 "테디"로 치환
- MD 파일 파싱하여 카드 정보 추출
- 임베딩 생성 전 단계 (06_generate_embeddings.py에서 임베딩 생성)
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import sys

# 상위 디렉토리를 경로에 추가
sys.path.append(str(Path(__file__).parent))
from text_replacement import replace_card_brand

# 프로젝트 루트 디렉토리 (data-preprocessing_dev/)
BASE_DIR = Path(__file__).parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data-preprocessing" / "data"
OUTPUT_DIR = BASE_DIR / "data-preprocessing_dev" / "data" / "teddycard"


def parse_markdown_card_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    MD 파일을 파싱하여 카드 정보 추출
    
    Args:
        file_path: MD 파일 경로
    
    Returns:
        카드 정보 딕셔너리 또는 None
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 텍스트 치환
        content = replace_card_brand(content, 'shinhan')
        
        # 파일명에서 카드명 추출
        card_name = file_path.stem
        
        # 기본 정보 추출 (간단한 파싱)
        # 연회비 정보 추출
        annual_fee = None
        annual_fee_match = re.search(r'연회비\s*\|\s*([^\n|]+)', content)
        if annual_fee_match:
            annual_fee = annual_fee_match.group(1).strip()
        
        # 카드 타입 추출 (파일명 기반)
        card_type = 'credit'  # 기본값
        if '체크' in card_name or 'Check' in card_name or 'check' in card_name:
            card_type = 'debit'
        
        # 카드 정보 생성
        card_info = {
            'id': f'CARD-SHINHAN-{card_name.replace(" ", "-").replace(".", "-")}',
            'name': replace_card_brand(card_name, 'shinhan'),
            'card_type': card_type,
            'brand': None,  # 나중에 추출
            'annual_fee_domestic': annual_fee if annual_fee and annual_fee != '없음' else None,
            'annual_fee_global': None,
            'performance_condition': None,
            'main_benefits': content[:500] if len(content) > 500 else content,  # 간단하게 처음 500자
            'full_content': content,  # 전체 내용
            'status': 'active',
            'metadata': {
                'original_source': 'shinhan',
                'original_file_name': file_path.name,
                'preprocessing_date': '2026-01-11',
                'preprocessing_version': '1.0'
            }
        }
        
        return card_info
    
    except Exception as e:
        print(f"[ERROR] 파일 파싱 실패: {file_path} - {e}")
        return None


def convert_shinhan_cards() -> List[Dict[str, Any]]:
    """
    신한카드 MD 파일들을 card_products 형식으로 변환
    
    Returns:
        card_products 형식의 리스트
    """
    output_cards = []
    
    # shinhan/card_info/*.md 파일 처리
    card_info_dir = DATA_DIR / "shinhan" / "card_info"
    if card_info_dir.exists():
        md_files = list(card_info_dir.glob("*.md"))
        print(f"[INFO] 발견된 MD 파일: {len(md_files)}개")
        
        for md_file in md_files:
            card_info = parse_markdown_card_file(md_file)
            if card_info:
                output_cards.append(card_info)
    
    return output_cards


def main():
    """메인 실행 함수"""
    print("=" * 80)
    print("신한카드 카드 정보 변환 스크립트")
    print("=" * 80)
    
    # 출력 디렉토리 생성
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 데이터 변환
    print("\n[INFO] 신한카드 카드 정보 데이터 변환 중...")
    cards = convert_shinhan_cards()
    
    print(f"[INFO] 변환 완료: {len(cards)}건")
    
    # JSON 파일로 저장
    output_file = OUTPUT_DIR / "teddycard_card_products.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)
    
    print(f"[INFO] 저장 완료: {output_file}")
    print("\n" + "=" * 80)
    print("다음 단계: 06_generate_embeddings.py 실행하여 임베딩 생성")
    print("=" * 80)


if __name__ == '__main__':
    main()
