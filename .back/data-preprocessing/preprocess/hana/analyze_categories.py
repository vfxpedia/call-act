# 카테고리별 source_id 분석 스크립트
import csv
from pathlib import Path
from collections import defaultdict

csv_path = Path(__file__).parent.parent.parent / 'data' / 'raw_data' / 'TS_하나카드_통합 - 시트1.csv'

categories = defaultdict(int)
rows_by_cat = defaultdict(list)

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        cat = row.get('consulting_category', '')
        categories[cat] += 1
        if len(rows_by_cat[cat]) < 3:
            rows_by_cat[cat].append(row.get('source_id', ''))

print("=" * 60)
print("카테고리별 건수 (상위 15개)")
print("=" * 60)
for cat, count in sorted(categories.items(), key=lambda x: -x[1])[:15]:
    sample_ids = ', '.join(rows_by_cat[cat][:3])
    print(f"{cat}: {count}건 (샘플: {sample_ids})")

print("\n" + "=" * 60)
print("테스트 권장 source_id (카테고리별 1개씩)")
print("=" * 60)
test_ids = []
for cat, count in sorted(categories.items(), key=lambda x: -x[1])[:10]:
    if rows_by_cat[cat]:
        test_ids.append((cat, rows_by_cat[cat][0]))
        print(f"{cat}: {rows_by_cat[cat][0]}")

print("\n테스트용 source_id 목록:")
print([t[1] for t in test_ids])

