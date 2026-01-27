# 데이터 커버리지 분석 스크립트
import csv
from pathlib import Path
from collections import Counter

csv_path = Path(__file__).parent.parent.parent / 'data' / 'raw_data' / 'TS_하나카드_통합 - 시트1.csv'

source_ids = set()
categories = Counter()

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        source_ids.add(row.get('source_id', ''))
        categories[row.get('consulting_category', '')] += 1

print('=' * 60)
print('전체 데이터 통계')
print('=' * 60)
print(f'총 source_id 개수: {len(source_ids)}')
print(f'총 카테고리 수: {len(categories)}')
print()

print('=' * 60)
print('카테고리별 분포 (전체)')
print('=' * 60)
for i, (cat, count) in enumerate(categories.most_common(), 1):
    pct = count / sum(categories.values()) * 100
    print(f'{i:2}. {cat}: {count}건 ({pct:.1f}%)')
print()

print('=' * 60)
print('테스트한 10개 카테고리 커버리지')
print('=' * 60)
tested_categories = [
    '선결제/즉시출금',
    '이용내역 안내',
    '한도상향 접수/처리',
    '도난/분실 신청/해제',
    '결제대금 안내',
    '승인취소/매출취소 안내',
    '이벤트 안내',
    '정부지원 바우처 (등유, 임신 등)',
    '연체대금 즉시출금',
    '한도 안내'
]

tested_count = 0
print('테스트한 카테고리:')
for cat in tested_categories:
    if cat in categories:
        tested_count += categories[cat]
        print(f'  - {cat}: {categories[cat]}건')
    else:
        print(f'  - {cat}: 0건 (존재하지 않음)')

total_count = sum(categories.values())
print()
print(f'테스트한 카테고리 총 건수: {tested_count}건')
print(f'전체 건수: {total_count}건')
print(f'커버리지: {tested_count/total_count*100:.1f}%')
print()

print('=' * 60)
print('테스트되지 않은 카테고리')
print('=' * 60)
untested = []
for cat, count in categories.most_common():
    if cat not in tested_categories:
        untested.append((cat, count))

for cat, count in untested:
    pct = count / total_count * 100
    print(f'  - {cat}: {count}건 ({pct:.1f}%)')

print()
print(f'미테스트 카테고리 수: {len(untested)}개')
print(f'미테스트 카테고리 건수: {sum(c for _, c in untested)}건')

# 결과를 파일로 저장
output_path = Path(__file__).parent.parent.parent / 'test_results' / 'coverage_analysis.txt'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('=' * 60 + '\n')
    f.write('전체 데이터 통계\n')
    f.write('=' * 60 + '\n')
    f.write(f'총 source_id 개수: {len(source_ids)}\n')
    f.write(f'총 카테고리 수: {len(categories)}\n\n')
    
    f.write('=' * 60 + '\n')
    f.write('카테고리별 분포 (전체)\n')
    f.write('=' * 60 + '\n')
    for i, (cat, count) in enumerate(categories.most_common(), 1):
        pct = count / sum(categories.values()) * 100
        f.write(f'{i:2}. {cat}: {count}건 ({pct:.1f}%)\n')
    f.write('\n')
    
    f.write('=' * 60 + '\n')
    f.write('테스트한 10개 카테고리 커버리지\n')
    f.write('=' * 60 + '\n')
    f.write('테스트한 카테고리:\n')
    for cat in tested_categories:
        if cat in categories:
            f.write(f'  - {cat}: {categories[cat]}건\n')
    f.write(f'\n테스트한 카테고리 총 건수: {tested_count}건\n')
    f.write(f'전체 건수: {total_count}건\n')
    f.write(f'커버리지: {tested_count/total_count*100:.1f}%\n\n')
    
    f.write('=' * 60 + '\n')
    f.write('테스트되지 않은 카테고리\n')
    f.write('=' * 60 + '\n')
    for cat, count in untested:
        pct = count / total_count * 100
        f.write(f'  - {cat}: {count}건 ({pct:.1f}%)\n')
    f.write(f'\n미테스트 카테고리 수: {len(untested)}개\n')
    f.write(f'미테스트 카테고리 건수: {sum(c for _, c in untested)}건\n')

print(f'\n결과 저장됨: {output_path}')

