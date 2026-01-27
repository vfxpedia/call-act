# 다양한 카테고리의 source_id를 테스트하는 스크립트
import sys
import csv
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from preprocess_hana import normalize_all_masking_v2, extract_scenario_tags

csv_path = Path(__file__).parent.parent.parent / 'data' / 'raw_data' / 'TS_하나카드_통합 - 시트1.csv'
output_dir = Path(__file__).parent.parent.parent / 'test_results'
output_dir.mkdir(parents=True, exist_ok=True)

# 테스트할 source_id 목록 (카테고리별 1개씩)
TEST_IDS = [
    '20597',  # 선결제/즉시출금
    '20594',  # 이용내역 안내
    '20598',  # 한도상향 접수/처리
    '20593',  # 도난/분실 신청/해제
    '20625',  # 이용대금 안내
    '20618',  # 결제방법/결제대금 안내
    '20713',  # 이벤트 안내
    '20628',  # 프리미엄 바우처
    '20611',  # 결제계좌 변경요청
    '20634',  # 한도 안내
]

print(f"[INFO] Testing {len(TEST_IDS)} source_ids")
print(f"[INFO] Output directory: {output_dir}\n")

# CSV에서 테스트 대상 행 추출
test_rows = {}
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row.get('source_id') in TEST_IDS:
            test_rows[row['source_id']] = row

# 각 source_id 처리
results = []
for source_id in TEST_IDS:
    if source_id not in test_rows:
        print(f"[WARNING] source_id {source_id} not found")
        continue
    
    row = test_rows[source_id]
    category = row.get('consulting_category', '')
    content = row.get('consulting_content', '')
    
    print(f"[PROCESSING] source_id: {source_id}")
    print(f"  Category: {category}")
    print(f"  Original length: {len(content)} chars")
    
    # 마스킹 처리
    cleaned_text, slot_types = normalize_all_masking_v2(content, use_llm=True)
    
    # 시나리오 태그 추출
    scenario_tags = extract_scenario_tags(cleaned_text)
    
    result = {
        "source_id": source_id,
        "category": category,
        "slot_types": slot_types,
        "scenario_tags": scenario_tags,
        "text": cleaned_text
    }
    results.append(result)
    
    # 개별 파일 저장
    output_file = output_dir / f"test_{source_id}.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# source_id: {source_id}\n")
        f.write(f"# category: {category}\n")
        f.write(f"# slot_types: {slot_types}\n")
        f.write(f"# scenario_tags: {scenario_tags}\n")
        f.write("=" * 60 + "\n")
        f.write(cleaned_text)
    
    print(f"  Slot types: {slot_types}")
    print(f"  Scenario tags: {scenario_tags[:5]}..." if len(scenario_tags) > 5 else f"  Scenario tags: {scenario_tags}")
    print(f"  Saved to: {output_file}\n")

# 전체 결과 JSON 저장
summary_file = output_dir / "test_summary.json"
with open(summary_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("=" * 60)
print(f"[SUCCESS] Processed {len(results)} source_ids")
print(f"[SUCCESS] Summary saved to: {summary_file}")
print("\n[SLOT TYPES USED ACROSS ALL TESTS]:")
all_slot_types = set()
for r in results:
    all_slot_types.update(r['slot_types'])
for st in sorted(all_slot_types):
    print(f"  - {st}")

