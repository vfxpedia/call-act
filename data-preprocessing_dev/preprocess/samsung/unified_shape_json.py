# 각 json 파일을 벡터 DB에 적재하기 위해 형식 통일화

import json
import os
from pathlib import Path
from typing import Dict, List, Any
import re


def sanitize_filename_for_id(filename: str) -> str:
    name = filename.replace('.json', '')
    name = re.sub(r'[^\w가-힣-]', '_', name)
    return name

def determine_category_from_filename(filename: str) -> str:
    filename_lower = filename.lower()
    if 'loan' in filename_lower or '대출' in filename_lower:
        return '대출'
    elif 'cash' in filename_lower or '현금' in filename_lower:
        return '현금서비스'
    elif 'prime' in filename_lower:
        return '프라임론'
    else:
        return '금융상품'

# 신용카드 소비자 가이드
def transform_creditcard_guide(data: Dict, filename: str) -> List[Dict]:
    results = []
    title = data.get('title', '')
    items = data.get('items', [])
    
    for idx, item in enumerate(items):
        subject = item.get('subject', '')
        content = item.get('content', '')
        
        transformed = {
            "id": f"{sanitize_filename_for_id(filename)}_{idx}",
            "text": f"{subject}\n{content}",
            "metadata": {
                "title": "소비자가이드",
                "category": "신용카드",
                "content": content
            }
        }
        results.append(transformed)
    
    return results

# 금융상품
def transform_finance(data: Dict, filename: str) -> List[Dict]:
    results = []
    category = determine_category_from_filename(filename)
    
    accordion_list = data.get('accordion_list', [])
    for idx, item in enumerate(accordion_list):
        title = item.get('title', '')
        content = item.get('content', '')
        
        transformed = {
            "id": f"{sanitize_filename_for_id(filename)}_{idx}",
            "text": f"{title}\n{content}",
            "metadata": {
                "title": "금융상품",
                "category": category,
                "content": content
            }
        }
        results.append(transformed)
    
    extra_info = data.get('extra_info', [])
    if extra_info:
        extra_content = '\n'.join(extra_info)
        transformed = {
            "id": f"{sanitize_filename_for_id(filename)}_extra",
            "text": f"추가정보\n{extra_content}",
            "metadata": {
                "title": "금융상품",
                "category": category,
                "content": extra_content
            }
        }
        results.append(transformed)
    
    footer_notice = data.get('footer_notice', [])
    for idx, item in enumerate(footer_notice):
        notice_title = item.get('title', '')
        notice_content = item.get('content', '')
        
        transformed = {
            "id": f"{sanitize_filename_for_id(filename)}_notice_{idx}",
            "text": f"{notice_title}\n{notice_content}",
            "metadata": {
                "title": "금융상품",
                "category": category,
                "content": notice_content
            }
        }
        results.append(transformed)
    
    return results

# 공지사항
def transform_news(data: Dict, filename: str) -> List[Dict]:
    title = data.get('title', '')
    content = data.get('content', '')
    
    transformed = {
        "id": f"{sanitize_filename_for_id(filename)}_0",
        "text": f"{title}\n{content}",
        "metadata": {
            "title": "뉴스",
            "category": "공지사항",
            "content": content
        }
    }
    
    return [transformed]

# 소비자주의경보
def transform_notice(data: Dict, filename: str) -> List[Dict]:
    title = data.get('title', '')
    content = data.get('content', '')
    
    transformed = {
        "id": f"{sanitize_filename_for_id(filename)}_0",
        "text": f"{title}\n{content}",
        "metadata": {
            "title": "소비자가이드",
            "category": "금융사기예방",
            "content": content
        }
    }
    
    return [transformed]


def identify_and_transform(data: Dict, filepath: Path) -> List[Dict]:
    filename = filepath.name
    parent_dir = filepath.parent.name
    
    if parent_dir == 'creditcard-guide':
        return transform_creditcard_guide(data, filename)
    elif parent_dir == 'finance':
        return transform_finance(data, filename)
    elif parent_dir == 'json' and 'news' in str(filepath.parent.parent):
        return transform_news(data, filename)
    elif parent_dir == 'json' and 'notice' in str(filepath.parent.parent):
        return transform_notice(data, filename)
    else:
        if 'items' in data and isinstance(data.get('items'), list):
            return transform_creditcard_guide(data, filename)
        elif 'accordion_list' in data:
            return transform_finance(data, filename)
        else:
            return transform_news(data, filename)

def process_json_file(filepath: Path, dry_run: bool = False) -> bool:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        transformed_data = identify_and_transform(data, filepath)
        
        if dry_run:
            print(f"  Would transform: {filepath}")
            print(f"  Result: {len(transformed_data)} entries")
            return True
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(transformed_data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Transformed: {filepath} ({len(transformed_data)} entries)")
        return True
        
    except Exception as e:
        print(f"✗ Error processing {filepath}: {e}")
        return False


def main():
    base_dir = Path(__file__).parent / 'data' / 'samsung'
    
    if not base_dir.exists():
        print(f"Error: Directory not found: {base_dir}")
        return
    
    json_files = list(base_dir.rglob('*.json'))
    
    print(f"Found {len(json_files)} JSON files in {base_dir}")
    print("=" * 60)
    
    response = input("Do you want to proceed with transformation? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Transformation cancelled.")
        return
    
    success_count = 0
    failed_count = 0
    
    for json_file in json_files:
        if process_json_file(json_file):
            success_count += 1
        else:
            failed_count += 1
    
    print("=" * 60)
    print(f"Transformation complete!")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {failed_count}")
    print(f"  Total: {len(json_files)}")

if __name__ == '__main__':
    main()