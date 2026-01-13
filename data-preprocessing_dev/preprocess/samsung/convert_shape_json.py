"""
삼성카드 JSON 파일 형식 변환 스크립트

기존 형식:
{
  "id": "...",
  "text": "...",
  "metadata": {
    "title": "...",
    "category": "..."
  }
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

# text에서 제목과 본문을 추출
# 첫 번째 줄을 제목으로, 나머지를 본문으로 처리
def extract_title_content(text):
    lines = text.split('\n', 1)

    if len(lines) == 2:
        title = lines[0].strip()
        content = lines[1].strip()
    else:
        # 줄바꿈이 없는 경우 전체를 제목으로
        title = text.strip()
        content = text.strip()
    
    return title, content


def convert_item(item):
    # 기존 데이터 추출
    extracted_title, content = extract_title_content(item.get("text", ""))
    new_text = f"{extracted_title} {content}"
    
    # 새로운 형식으로 변환
    new_item = {
        "id": item.get("id", ""),
        "title": extracted_title,
        "content": content,
        "text": new_text,
        "metadata": {
            "category1": item.get("metadata", {}).get("title", ""),
            "category2": item.get("metadata", {}).get("category", "")
        }
    }
    
    # date 필드가 존재하면 유지
    if "date" in item.get("metadata", {}):
        new_item["metadata"]["date"] = item["metadata"]["date"]
    
    return new_item


def convert_json_file(input_path, output_path=None):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    sorted_data = [convert_item(item) for item in data]
    
    # date 필드가 있는 경우 날짜 기준 내림차순 정렬
    sorted_data.sort(key=lambda x: x.get("metadata", {}).get("date", ""), reverse=True)
    
    if output_path is None:
        output_path = input_path
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sorted_data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 변환 완료: {input_path}")


def main():
    samsung_dir = Path("data/samsung")

    # JSON 파일 목록 가져오기 (하위 디렉토리 제외)
    json_files = [f for f in samsung_dir.iterdir() if f.is_file() and f.suffix == '.json']
 
    # 각 파일 변환
    for json_file in sorted(json_files):
        try:
            convert_json_file(str(json_file))
        except Exception as e:
            print(f"❌ 오류 발생 ({json_file.name}): {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n모든 파일 변환 완료")


if __name__ == "__main__":
    main()
