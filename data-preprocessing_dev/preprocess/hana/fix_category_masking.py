# 이전 데이터 일괄 처리 스크립트
# category 마스킹 및 scenario_tags 개선

import json
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# 제거할 일반적 scenario_tags
COMMON_TAGS_TO_REMOVE = {'본인확인', '상담완료', '개인정보동의'}

def fix_category_masking(text: str) -> str:
    """
    category 필드의 ▲를 [서비스명#1] 등으로 치환
    
    간단한 패턴 매칭 사용:
    - ▲▲페이 → [서비스명#1]페이
    - ▲▲카드 → [카드사명#1]카드
    - ▲▲은행 → [은행명#1]은행
    - 기타 ▲▲ → [서비스명#1]
    """
    if '▲' not in text:
        return text
    
    # 패턴별 치환
    # ▲▲페이, ▲▲페이서비스 등
    text = re.sub(r'▲+페이', '[서비스명#1]페이', text)
    # ▲▲카드
    text = re.sub(r'▲+카드', '[카드사명#1]카드', text)
    # ▲▲은행
    text = re.sub(r'▲+은행', '[은행명#1]은행', text)
    # 나머지 ▲▲는 [서비스명#1]로 치환
    text = re.sub(r'▲+', '[서비스명#1]', text)
    
    return text

def filter_scenario_tags(tags: List[str]) -> List[str]:
    """
    scenario_tags에서 일반적 태그 제거
    
    Args:
        tags: 원본 태그 리스트
    
    Returns:
        필터링된 태그 리스트
    """
    if not tags:
        return []
    
    filtered = [tag for tag in tags if tag not in COMMON_TAGS_TO_REMOVE]
    return filtered

def process_vectordb_file(vectordb_path: Path, backup: bool = True) -> Dict:
    """
    VectorDB JSON 파일 처리
    
    Returns:
        처리 결과 통계
    """
    print(f"[INFO] VectorDB 파일 처리 시작: {vectordb_path}")
    
    # 백업 생성
    if backup and vectordb_path.exists():
        backup_path = vectordb_path.with_suffix('.json.backup2')
        shutil.copy2(vectordb_path, backup_path)
        print(f"[INFO] 백업 생성: {backup_path}")
    
    # 파일 로드
    with open(vectordb_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"[INFO] 총 {len(data)}개 항목 로드")
    
    # 처리 통계
    stats = {
        'total': len(data),
        'category_fixed': 0,
        'title_fixed': 0,
        'scenario_tags_filtered': 0,
        'items_modified': 0
    }
    
    # 각 항목 처리
    for item in data:
        modified = False
        
        # 1. metadata.category 수정
        if 'metadata' in item and 'category' in item['metadata']:
            original_category = item['metadata']['category']
            if '▲' in original_category:
                fixed_category = fix_category_masking(original_category)
                item['metadata']['category'] = fixed_category
                stats['category_fixed'] += 1
                modified = True
        
        # 2. title 수정 (category 기반이므로)
        if 'title' in item:
            original_title = item['title']
            if '▲' in original_title:
                fixed_title = fix_category_masking(original_title)
                item['title'] = fixed_title
                stats['title_fixed'] += 1
                modified = True
        
        # 3. scenario_tags 필터링
        if 'metadata' in item and 'scenario_tags' in item['metadata']:
            original_tags = item['metadata']['scenario_tags']
            if isinstance(original_tags, list):
                filtered_tags = filter_scenario_tags(original_tags)
                if len(filtered_tags) != len(original_tags):
                    item['metadata']['scenario_tags'] = filtered_tags
                    stats['scenario_tags_filtered'] += 1
                    modified = True
        
        if modified:
            stats['items_modified'] += 1
    
    # 파일 저장
    with open(vectordb_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"[INFO] VectorDB 파일 저장 완료")
    return stats

def process_rdb_file(rdb_path: Path, backup: bool = True) -> Dict:
    """
    RDB JSON 파일 처리
    
    Returns:
        처리 결과 통계
    """
    print(f"[INFO] RDB 파일 처리 시작: {rdb_path}")
    
    # 백업 생성
    if backup and rdb_path.exists():
        backup_path = rdb_path.with_suffix('.json.backup2')
        shutil.copy2(rdb_path, backup_path)
        print(f"[INFO] 백업 생성: {backup_path}")
    
    # 파일 로드
    with open(rdb_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"[INFO] 총 {len(data)}개 항목 로드")
    
    # 처리 통계
    stats = {
        'total': len(data),
        'category_fixed': 0,
        'items_modified': 0
    }
    
    # 각 항목 처리
    for item in data:
        modified = False
        
        # consulting_category 수정
        if 'consulting_category' in item:
            original_category = item['consulting_category']
            if '▲' in original_category:
                fixed_category = fix_category_masking(original_category)
                item['consulting_category'] = fixed_category
                stats['category_fixed'] += 1
                modified = True
        
        if modified:
            stats['items_modified'] += 1
    
    # 파일 저장
    with open(rdb_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"[INFO] RDB 파일 저장 완료")
    return stats

def main():
    """메인 실행 함수"""
    base_dir = Path(__file__).parent.parent.parent
    vectordb_path = base_dir / 'data' / 'hana' / 'hana_vectordb.json'
    rdb_path = base_dir / 'data' / 'hana' / 'hana_rdb_metadata.json'
    
    print("=" * 60)
    print("[INFO] 이전 데이터 일괄 처리 시작")
    print(f"[INFO] 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 파일 존재 확인
    if not vectordb_path.exists():
        print(f"[ERROR] VectorDB 파일을 찾을 수 없습니다: {vectordb_path}")
        return
    
    if not rdb_path.exists():
        print(f"[ERROR] RDB 파일을 찾을 수 없습니다: {rdb_path}")
        return
    
    # VectorDB 처리
    print("\n[1/2] VectorDB 파일 처리 중...")
    vectordb_stats = process_vectordb_file(vectordb_path)
    
    # RDB 처리
    print("\n[2/2] RDB 파일 처리 중...")
    rdb_stats = process_rdb_file(rdb_path)
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("[COMPLETE] 일괄 처리 완료")
    print("=" * 60)
    print(f"[VectorDB 통계]")
    print(f"  - 총 항목: {vectordb_stats['total']}개")
    print(f"  - category 수정: {vectordb_stats['category_fixed']}개")
    print(f"  - title 수정: {vectordb_stats['title_fixed']}개")
    print(f"  - scenario_tags 필터링: {vectordb_stats['scenario_tags_filtered']}개")
    print(f"  - 수정된 항목: {vectordb_stats['items_modified']}개")
    print()
    print(f"[RDB 통계]")
    print(f"  - 총 항목: {rdb_stats['total']}개")
    print(f"  - category 수정: {rdb_stats['category_fixed']}개")
    print(f"  - 수정된 항목: {rdb_stats['items_modified']}개")
    print()
    print(f"[INFO] 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == '__main__':
    main()

