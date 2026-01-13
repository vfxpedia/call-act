"""
현대카드 기프트카드 JSON 파일 형식 변환 스크립트

기존 형식:
{
  "item": "제목"
  "details": "본문"
}

새 형식
{
  "id": "...",
  "title": "제목",
  "content": "본문",
  "text": "제목 본문",
  "metadata": {
    "category1": "대분류",
    "category2": "중분류"
  }
}
"""

import json
import os
from pathlib import Path

def convert_item(item, index, filename):
    title = item.get("item", "")
    content = item.get("details", "")
    new_text = f"{title} {content}"
    
    new_item = {
        "id": f"{filename}_{index}",
        "title": title,
        "content": content,
        "text": new_text,
        "metadata": {
            "category1": filename,
            "category2": title
        }
    }
    
    return new_item

def convert_json_file(input_path, output_path=None):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    filename = Path(input_path).stem
    converted_data = [convert_item(item, i, filename) for i, item in enumerate(data)]
    
    if output_path is None:
        output_path = input_path
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(converted_data, f, ensure_ascii=False, indent=2)

def main():
    current_dir = Path("./json")
    json_files = [f for f in current_dir.iterdir() if f.is_file() and f.suffix == '.json' and f.name != 'package.json' and f.name != 'tsconfig.json']
 
    for json_file in sorted(json_files):
        try:
            convert_json_file(str(json_file))
        except Exception as e:
            pass

if __name__ == "__main__":
    main()
