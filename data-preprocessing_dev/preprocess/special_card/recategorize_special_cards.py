import json
import os
from collections import defaultdict

def get_card_name_from_id(item_id):
    card_name = item_id.split('_')[0]
    
    card_name_map = {
        'k패스': 'K패스',
        '국민행복카드': '국민행복카드',
        '나라사랑체크카드': '나라사랑체크카드',
        '쿠팡와우카드': '쿠팡와우카드',
        '서울시다둥이행복카드': '서울시다둥이행복카드',
        '네이버페이카드': '네이버페이카드',
        'hyundaicard_minsaeng': '현대카드 민생',
        'narasarang': '나라사랑카드',
        'samsungcard_senior': '삼성카드 라이프파트너',
        'plumb': '삼성카드 라이프파트너'
    }
    
    return card_name_map.get(card_name, card_name)

def categorize_by_text(item):
    text = item['text'].lower()
    
    # 1. 연회비
    if '연회비' in text:
        return '연회비'
    
    # 3. 혜택/할인 - 할인, 적립, 포인트, 캐시 관련
    if any(keyword in text for keyword in ['할인', '적립', '포인트', '캐시', '환급']):
        return '혜택/할인'

    # 2. 발급/신청
    if any(keyword in text for keyword in ['발급', '신청', '가입', '대상']):
        return '발급/신청'
    
    # 바우처, 보험 관련도 혜택
    if any(keyword in text for keyword in ['바우처', '보험', '보장']):
        return '혜택/할인'
    
    # 4. 수수료/금융정보 - 연체, 이자, 수수료, 해외이용
    if any(keyword in text for keyword in ['연체', '이자', '수수료', '해외', '금리']):
        return '수수료/금융정보'
    
    # 5. 이용안내 - 사용처, 실적, 제외 대상, 이용금액
    if any(keyword in text for keyword in ['실적', '제외', '이용금액', '사용', '이용', '확인사항', '시간 제한', '대상점']):
        return '이용안내'
    
    # 6. 고객지원/기타 - 고객센터, 안내, 유의사항, 변경
    if any(keyword in text for keyword in ['고객센터', '안내', '유의사항', '변경', '금융소비자']):
        return '고객지원/기타'
    
    return '기타'

files_to_process = [
    'data/special_card/hyundaicard_minsaeng_vectors.json',
    'data/special_card/narasarang_vectors.json',
    'data/special_card/samsungcard_senior_vectors.json',
]

for file_path in files_to_process:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, dict) and 'vector_chunks' in data:
        items = data['vector_chunks']
        is_wrapped = True
    else:
        items = data
        is_wrapped = False
    
    print(f"Total entries: {len(items)}")
    
    title_changed = 0
    category_changed = 0
    
    for item in items:
        old_title = item['metadata']['title']
        new_title = get_card_name_from_id(item['id'])
        
        if old_title != new_title:
            title_changed += 1
            item['metadata']['title'] = new_title
        
        old_category = item['metadata']['category']
        new_category = categorize_by_text(item)
        
        if old_category != new_category:
            category_changed += 1
            print(f"  {item['id']}: '{old_category}' → '{new_category}'")
        
        item['metadata']['category'] = new_category
    
    categories = defaultdict(int)
    for item in items:
        categories[item['metadata']['category']] += 1
    
    print(f"\n새 카테고리 분포:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}개")
    
    # 원본 파일명 앞에 fixed를 붙여 저장
    dir_path = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    output_file = os.path.join(dir_path, f"fixed_{file_name}")
    
    # 결과물 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        if is_wrapped:
            json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            json.dump(items, f, ensure_ascii=False, indent=2)
    
    print(f"\n작업 완료")