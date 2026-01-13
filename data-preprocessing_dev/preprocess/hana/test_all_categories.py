# 57개 전체 카테고리 테스트 스크립트
import sys
import csv
import json
from pathlib import Path
from collections import defaultdict
sys.path.append(str(Path(__file__).parent))

from preprocess_hana import normalize_all_masking_v2, extract_scenario_tags

csv_path = Path(__file__).parent.parent.parent / 'data' / 'hana' / 'TS_하나카드_통합 - 시트1.csv'
output_dir = Path(__file__).parent / 'test_results' / 'all_categories'
output_dir.mkdir(parents=True, exist_ok=True)

print(f"[INFO] Output directory: {output_dir}")
print(f"[INFO] Reading CSV file...")

# 카테고리별로 첫 번째 row 수집
category_rows = {}
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        cat = row.get('consulting_category', '')
        if cat and cat not in category_rows:
            category_rows[cat] = row

print(f"[INFO] Found {len(category_rows)} categories")
print(f"[INFO] Starting test for all categories...\n")

# 결과 저장용
results = []
all_slot_types = set()
all_scenario_tags = set()

for i, (category, row) in enumerate(sorted(category_rows.items()), 1):
    source_id = row.get('source_id', '')
    content = row.get('consulting_content', '')
    
    print(f"[{i:2}/{len(category_rows)}] Processing: {category}")
    print(f"         source_id: {source_id}")
    
    try:
        # 마스킹 처리
        cleaned_text, slot_types = normalize_all_masking_v2(content, use_llm=True)
        
        # 시나리오 태그 추출
        scenario_tags = extract_scenario_tags(cleaned_text)
        
        # 슬롯 타입과 시나리오 태그 수집
        all_slot_types.update(slot_types)
        all_scenario_tags.update(scenario_tags)
        
        result = {
            "source_id": source_id,
            "category": category,
            "slot_types": slot_types,
            "scenario_tags": scenario_tags,
            "text_length": len(cleaned_text),
            "status": "success"
        }
        
        # 개별 파일 저장
        output_file = output_dir / f"test_{source_id}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# source_id: {source_id}\n")
            f.write(f"# category: {category}\n")
            f.write(f"# slot_types: {slot_types}\n")
            f.write(f"# scenario_tags: {scenario_tags}\n")
            f.write("=" * 60 + "\n")
            f.write(cleaned_text)
        
        print(f"         slot_types: {slot_types[:3]}..." if len(slot_types) > 3 else f"         slot_types: {slot_types}")
        print(f"         [OK] Saved to {output_file.name}\n")
        
    except Exception as e:
        result = {
            "source_id": source_id,
            "category": category,
            "slot_types": [],
            "scenario_tags": [],
            "text_length": 0,
            "status": f"error: {str(e)}"
        }
        print(f"         [ERROR] {str(e)}\n")
    
    results.append(result)

# 전체 요약 저장
summary = {
    "total_categories": len(category_rows),
    "success_count": sum(1 for r in results if r["status"] == "success"),
    "error_count": sum(1 for r in results if r["status"] != "success"),
    "all_slot_types": sorted(list(all_slot_types)),
    "all_scenario_tags": sorted(list(all_scenario_tags)),
    "results": results
}

summary_file = output_dir / "summary.json"
with open(summary_file, 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print("=" * 60)
print(f"[COMPLETE] Processed {len(results)} categories")
print(f"[COMPLETE] Success: {summary['success_count']}, Errors: {summary['error_count']}")
print(f"[COMPLETE] All slot types used: {len(all_slot_types)}")
print(f"[COMPLETE] All scenario tags used: {len(all_scenario_tags)}")
print(f"[COMPLETE] Summary saved to: {summary_file}")
print()
print("[SLOT TYPES]:")
for st in sorted(all_slot_types):
    print(f"  - {st}")
print()
print("[SCENARIO TAGS]:")
for st in sorted(all_scenario_tags):
    print(f"  - {st}")

