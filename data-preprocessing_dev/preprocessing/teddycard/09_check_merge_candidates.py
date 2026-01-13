"""
merge 대상 확인 스크립트

현대/신한 데이터에서 merge_by_category2를 적용할 수 있는 문서 그룹을 확인
"""

import json
from pathlib import Path
from typing import Dict
from collections import defaultdict, Counter

BASE_DIR = Path(__file__).resolve().parents[3]
OUTPUT_DIR = BASE_DIR / "data-preprocessing_dev" / "preprocessing" / "output"


def check_merge_candidates(file_path: Path) -> Dict:
    """merge 대상 확인"""
    if not file_path.exists():
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        documents = json.load(f)
    
    # category2 기준으로 그룹화
    grouped = defaultdict(list)
    for doc in documents:
        category2 = doc.get('metadata', {}).get('original_category2', '')
        if category2:
            grouped[category2].append(doc)
    
    # 2개 이상인 그룹만 merge 대상
    merge_candidates = {cat: docs for cat, docs in grouped.items() if len(docs) > 1}
    
    # 통계
    total_docs = len(documents)
    merge_groups = len(merge_candidates)
    merge_target_docs = sum(len(docs) for docs in merge_candidates.values())
    merged_count = sum(len(docs) for docs in merge_candidates.values())  # 통합될 문서 수
    after_merge_count = total_docs - merged_count + merge_groups  # merge 후 예상 문서 수
    
    return {
        "file": file_path.name,
        "total_docs": total_docs,
        "merge_groups": merge_groups,
        "merge_target_docs": merge_target_docs,
        "after_merge_count": after_merge_count,
        "reduction": merged_count - merge_groups,
        "merge_candidates": {cat: len(docs) for cat, docs in sorted(merge_candidates.items(), key=lambda x: len(x[1]), reverse=True)[:10]}
    }


def main():
    """메인 함수"""
    print("=" * 80)
    print("merge 대상 확인 스크립트")
    print("=" * 80)
    
    files_to_check = [
        OUTPUT_DIR / "teddycard_service_guides_hyundai.json",
        OUTPUT_DIR / "teddycard_service_guides_shinhan.json",
    ]
    
    results = []
    for file_path in files_to_check:
        print(f"\n[INFO] 확인 중: {file_path.name}")
        result = check_merge_candidates(file_path)
        if result:
            results.append(result)
            
            print(f"  총 문서 수: {result['total_docs']}건")
            print(f"  merge 그룹 수: {result['merge_groups']}개")
            print(f"  merge 대상 문서: {result['merge_target_docs']}건")
            print(f"  merge 후 예상 문서 수: {result['after_merge_count']}건 (감소: {result['reduction']}건)")
            
            if result['merge_candidates']:
                print(f"  상위 merge 대상:")
                for cat, count in list(result['merge_candidates'].items())[:5]:
                    print(f"    - {cat}: {count}개 문서")
    
    # 결론
    print("\n" + "=" * 80)
    print("결론")
    print("=" * 80)
    
    for result in results:
        if result['merge_groups'] > 0:
            print(f"\n[{result['file']}]")
            if result['reduction'] > 10:  # 10건 이상 감소하면 merge 권장
                print(f"  → merge 권장: {result['reduction']}건 감소")
            else:
                print(f"  → merge 선택적: {result['reduction']}건 감소 (효과 미미)")
        else:
            print(f"\n[{result['file']}]")
            print(f"  → merge 불필요: merge 대상 없음")


if __name__ == '__main__':
    main()
