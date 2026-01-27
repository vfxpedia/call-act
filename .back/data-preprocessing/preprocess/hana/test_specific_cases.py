# 특정 source_id만 재테스트하는 스크립트
import sys
import csv
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from preprocess_hana import normalize_all_masking_v2, extract_scenario_tags

csv_path = Path(__file__).parent.parent.parent / 'data' / 'raw_data' / 'TS_하나카드_통합 - 시트1.csv'
output_dir = Path(__file__).parent.parent.parent / 'test_results'

# 문제가 있었던 source_id만 테스트
TEST_IDS = ['20597', '20598']

# CSV에서 테스트 대상 행 추출
test_rows = {}
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row.get('source_id') in TEST_IDS:
            test_rows[row['source_id']] = row

for source_id in TEST_IDS:
    if source_id not in test_rows:
        continue
    
    row = test_rows[source_id]
    content = row.get('consulting_content', '')
    category = row.get('consulting_category', '')
    
    print(f"\n[TEST] source_id: {source_id}, Category: {category}")
    
    # 마스킹 처리
    cleaned_text, slot_types = normalize_all_masking_v2(content, use_llm=True)
    
    # 시나리오 태그 추출
    scenario_tags = extract_scenario_tags(cleaned_text)
    
    # 결과 저장
    output_file = output_dir / f"test_{source_id}_v2.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# source_id: {source_id}\n")
        f.write(f"# category: {category}\n")
        f.write(f"# slot_types: {slot_types}\n")
        f.write(f"# scenario_tags: {scenario_tags}\n")
        f.write("=" * 60 + "\n")
        f.write(cleaned_text)
    
    print(f"[SAVED] {output_file}")
    print(f"[SLOT TYPES]: {slot_types}")
    print(f"[SCENARIO TAGS]: {scenario_tags}")
    
    # 문제 체크
    if '[전화번호#1]원' in cleaned_text:
        print("[ERROR] Found '[전화번호#1]원' - should be [금액#N]")
    elif '[전화번호#1][금액' in cleaned_text:
        print("[WARNING] Found '[전화번호#1][금액' - may need review")
    else:
        print("[OK] No problematic patterns found")
