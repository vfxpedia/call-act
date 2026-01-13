import json

with open('data/special_card/special_converted.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def get_card_name_from_id(item_id):
    card_name = item_id.split('_')[0]
    
    # Normalize card names
    card_name_map = {
        'k패스': 'K패스',
        '국민행복카드': '국민행복카드',
        '나라사랑체크카드': '나라사랑체크카드',
        '쿠팡와우카드': '쿠팡와우카드',
        '서울시다둥이행복카드': '서울시다둥이행복카드',
        '네이버페이카드': '네이버페이카드'
    }
    
    return card_name_map.get(card_name, card_name)

def categorize_by_text(item):
    text = item['text'].lower()
    title = item['metadata']['title'].lower()
    
    # 1. 기본정보 - 연회비, 발급, 신청 관련
    if any(keyword in text or keyword in title for keyword in ['연회비', '발급', '신청', '가입', '대상']):
        if '반환' in text:
            return '기본정보'
        if '연회비' in text or '연회비' in title:
            return '연회비'
        if '발급' in text or '신청' in text or '대상' in text:
            return '발급/신청'
    
    # 2. 혜택/할인 - 할인, 적립, 포인트, 캐시 관련
    if any(keyword in text or keyword in title for keyword in ['할인', '적립', '포인트', '캐시', '환급', '혜택', '서비스', '바우처', '보장', '보험']):
        if '할인' in text or '적립' in text or '포인트' in text or '캐시' in text:
            return '혜택/할인'
        if '바우처' in text or '보험' in text or '보장' in text:
            return '혜택/할인'
        if '제외' in text or '제외' in text:
            return '이용안내'

    # 3. 수수료/금융정보 - 연체, 이자, 수수료, 해외이용
    if any(keyword in text or keyword in title for keyword in ['연체', '이자', '수수료', '해외', '금리']):
        return '수수료/금융정보'
    
    # 4. 이용안내 - 사용처, 실적, 제외 대상, 이용금액
    if any(keyword in text or keyword in title for keyword in ['실적', '제외', '이용금액', '사용', '이용', '확인사항', '시간 제한']):
        if '해외' in text:
            return '수수료/금융정보'
        return '이용안내'
    
    # 5. 고객지원/기타 - 고객센터, 안내, 유의사항, 변경
    if any(keyword in text or keyword in title for keyword in ['고객센터', '안내', '유의사항', '변경', '금융소비자']):
        return '고객지원/기타'
    
    return '기타'

title_changed_count = 0
for item in data:
    old_title = item['metadata']['title']
    new_title = get_card_name_from_id(item['id'])
    
    if old_title != new_title:
        title_changed_count += 1
    
    item['metadata']['title'] = new_title

start_index = -1
for i, item in enumerate(data):
    if item['id'] == '국민행복카드_18':
        start_index = i
        break

recategorized_count = 0
for i in range(start_index, len(data)):
    old_category = data[i]['metadata']['category']
    new_category = categorize_by_text(data[i])
    
    if old_category != new_category:
        recategorized_count += 1
        print(f"{data[i]['id']}: '{old_category}' → '{new_category}'")
    
    data[i]['metadata']['category'] = new_category

from collections import defaultdict
new_categories = defaultdict(int)
for i in range(start_index, len(data)):
    new_categories[data[i]['metadata']['category']] += 1

for cat, count in sorted(new_categories.items()):
    print(f"  {cat}: {count}")

# 저장
output_file = 'data/special_card/fixed_special_converted.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n작업 완료")