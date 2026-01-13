import json
import os
from pathlib import Path

def extract_title_from_text(text):
    lines = text.split('\n')
    return lines[0].strip() if lines else ""

def transform_item(item, category):
    """
    JSON 항목을 새로운 구조로 변환
    - title: text의 첫 줄로 변경
    - category: 중분류만 유지 (기존 metadata.category)
    - content, subcategory 등 제거
    """
    new_item = {
        "id": item["id"],
        "text": item["text"],
        "metadata": {
            "title": extract_title_from_text(item["text"]),
            "category": category
        }
    }
    return new_item

def process_directory(directory_path, output_filename, category_name):
    directory = Path(directory_path)
    all_items = []
    
    json_files = sorted(directory.glob("*.json"))
    
    for json_file in json_files:
        print(f"  📄 {json_file.name}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 각 항목 변환
        if isinstance(data, list):
            for item in data:
                # 기존 metadata.category를 사용 (중분류)
                original_category = item.get("metadata", {}).get("category", category_name)
                transformed = transform_item(item, original_category)
                all_items.append(transformed)
        else:
            original_category = data.get("metadata", {}).get("category", category_name)
            transformed = transform_item(data, original_category)
            all_items.append(transformed)
    
    # 통합 파일 저장
    output_path = directory.parent / output_filename
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    
    # 카테고리별 개수 표시
    category_count = {}
    for item in all_items:
        cat = item["metadata"]["category"]
        category_count[cat] = category_count.get(cat, 0) + 1
    
    print(f"\n카테고리별 분포:")
    for cat, count in sorted(category_count.items()):
        print(f"  - {cat}: {count}개")
    
    return all_items

def main():
    base_path = Path("data/samsung")

    # 1. creditcard-guide 처리
    creditcard_items = process_directory(
        directory_path=base_path / "creditcard-guide",
        output_filename="creditcard-guide.json",
        category_name="신용카드"
    )
    
    # 2. finance 처리
    finance_items = process_directory(
        directory_path=base_path / "finance",
        output_filename="finance-products.json",
        category_name="금융상품"
    )
    
    print("작업 완료")

if __name__ == "__main__":
    main()