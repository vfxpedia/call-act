# 57개 카테고리 샘플 데이터 분석 스크립트
import csv
import re
from pathlib import Path
from collections import defaultdict, Counter

csv_path = Path(__file__).parent.parent.parent / 'data' / 'raw_data' / 'TS_하나카드_통합 - 시트1.csv'
output_path = Path(__file__).parent.parent.parent / 'test_results' / 'category_analysis.txt'

print("[INFO] Analyzing all 57 categories...")

# 카테고리별로 첫 번째 row 수집
category_rows = {}
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        cat = row.get('consulting_category', '')
        if cat and cat not in category_rows:
            category_rows[cat] = row

# 분석 결과 저장
with open(output_path, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("57개 카테고리 샘플 데이터 분석\n")
    f.write("=" * 80 + "\n\n")
    
    # 마스킹 패턴 분석
    all_patterns = Counter()
    category_patterns = {}
    
    for i, (category, row) in enumerate(sorted(category_rows.items()), 1):
        source_id = row.get('source_id', '')
        content = row.get('consulting_content', '')
        
        # ▲ 패턴 분석
        mask_patterns = re.findall(r'▲+', content)
        mask_lengths = [len(p) for p in mask_patterns]
        length_counter = Counter(mask_lengths)
        
        # 문맥 패턴 분석 (▲ 주변 텍스트)
        context_patterns = []
        
        # 학교 관련
        if re.search(r'▲+초등학교', content):
            context_patterns.append('초등학교명')
        if re.search(r'▲+중학교', content):
            context_patterns.append('중학교명')
        if re.search(r'▲+고등학교', content):
            context_patterns.append('고등학교명')
        if re.search(r'▲+대학교', content):
            context_patterns.append('대학교명')
        if re.search(r'▲+교육청', content):
            context_patterns.append('교육청명')
        
        # 금융 관련
        if re.search(r'▲+은행', content):
            context_patterns.append('은행명')
        if re.search(r'▲+카드', content):
            context_patterns.append('카드사명')
        if re.search(r'▲+보험', content):
            context_patterns.append('보험사명')
        if re.search(r'▲+증권', content):
            context_patterns.append('증권사명')
        
        # 금액 관련
        if re.search(r'▲+원', content):
            context_patterns.append('금액')
        if re.search(r'▲+만원', content):
            context_patterns.append('금액(만원)')
        
        # 날짜/시간 관련
        if re.search(r'▲+년', content):
            context_patterns.append('년도')
        if re.search(r'▲+월', content):
            context_patterns.append('월')
        if re.search(r'▲+일', content):
            context_patterns.append('일')
        if re.search(r'▲+시', content):
            context_patterns.append('시간')
        
        # 장소 관련
        if re.search(r'▲+점', content):
            context_patterns.append('지점/매장명')
        if re.search(r'▲+병원', content):
            context_patterns.append('병원명')
        if re.search(r'▲+약국', content):
            context_patterns.append('약국명')
        
        # 회사/기관 관련
        if re.search(r'▲+회사', content):
            context_patterns.append('회사명')
        if re.search(r'▲+센터', content):
            context_patterns.append('센터명')
        if re.search(r'▲+부서', content) or re.search(r'▲+팀', content):
            context_patterns.append('부서명')
        
        # 상품/서비스 관련
        if '카드론' in content or '카드대출' in content:
            context_patterns.append('카드대출관련')
        if '할부' in content:
            context_patterns.append('할부관련')
        if '포인트' in content or '마일리지' in content:
            context_patterns.append('포인트관련')
        if '가상계좌' in content:
            context_patterns.append('가상계좌관련')
        if '바우처' in content:
            context_patterns.append('바우처관련')
        
        # 개인정보 관련
        if '생년월일' in content:
            context_patterns.append('생년월일')
        if '휴대폰' in content or '핸드폰' in content:
            context_patterns.append('휴대폰번호')
        if '주민등록' in content:
            context_patterns.append('주민등록번호')
        if '계좌번호' in content or '계좌' in content:
            context_patterns.append('계좌번호')
        
        category_patterns[category] = {
            'source_id': source_id,
            'mask_count': len(mask_patterns),
            'length_distribution': dict(length_counter),
            'context_patterns': list(set(context_patterns)),
            'content_preview': content[:300] + '...' if len(content) > 300 else content
        }
        
        for p in context_patterns:
            all_patterns[p] += 1
        
        # 파일에 작성
        f.write(f"\n{'='*80}\n")
        f.write(f"[{i:2}/57] 카테고리: {category}\n")
        f.write(f"{'='*80}\n")
        f.write(f"source_id: {source_id}\n")
        f.write(f"마스킹(▲) 개수: {len(mask_patterns)}\n")
        f.write(f"마스킹 길이 분포: {dict(length_counter)}\n")
        f.write(f"감지된 패턴: {context_patterns}\n")
        f.write(f"\n[샘플 대화 (처음 500자)]:\n")
        f.write(content[:500] + '...\n' if len(content) > 500 else content + '\n')
    
    # 전체 요약
    f.write("\n\n" + "=" * 80 + "\n")
    f.write("전체 요약\n")
    f.write("=" * 80 + "\n\n")
    
    f.write("[감지된 패턴 빈도 (전체 57개 카테고리 중)]:\n")
    for pattern, count in all_patterns.most_common():
        f.write(f"  - {pattern}: {count}개 카테고리\n")
    
    f.write("\n[현재 코드에 없는 것으로 추정되는 패턴]:\n")
    new_patterns = ['증권사명', '약국명', '센터명', '회사명', '카드대출관련', 
                    '할부관련', '포인트관련', '가상계좌관련', '바우처관련',
                    '주민등록번호', '계좌번호', '지점/매장명']
    for p in new_patterns:
        if all_patterns[p] > 0:
            f.write(f"  - {p}: {all_patterns[p]}개 카테고리\n")

print(f"[INFO] Analysis saved to: {output_path}")
print(f"\n[DETECTED PATTERNS]:")
for pattern, count in all_patterns.most_common():
    print(f"  - {pattern}: {count} categories")

