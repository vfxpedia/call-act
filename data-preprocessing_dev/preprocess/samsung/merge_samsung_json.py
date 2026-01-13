import json
import os
from pathlib import Path

TARGET_DIR = "finance"

def merge_samsung_json():
    source_dir = Path(f"data/samsung/{TARGET_DIR}")
    output_file = source_dir.parent / f"{TARGET_DIR}.json"
    
    # JSON 파일 목록 가져오기
    json_files = sorted(source_dir.glob("*.json"))
    
    # 통합할 데이터를 저장할 리스트
    consolidated_data = []
    
    # 전역 카운터
    global_counter = 1
    
    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 각 항목 처리
        for item in data:
            # 기존 id에서 마지막 숫자를 제거하여 title 생성
            # 예: "신용카드_관련주요_용어_안내_0" → "신용카드_관련주요_용어_안내"
            old_id = item['id']
            
            # 마지막 '_숫자' 부분 제거
            if '_' in old_id:
                parts = old_id.rsplit('_', 1)
                # 마지막 부분이 숫자인지 확인
                if len(parts) == 2 and parts[1].isdigit():
                    new_title = parts[0]
                else:
                    new_title = old_id
            else:
                new_title = old_id
            
            # 새로운 데이터 구조 생성
            new_item = {
                "id": f"소비자가이드_{global_counter}",
                "text": item['text'],
                "metadata": {
                    "title": new_title,
                    "category": item['metadata']['category']
                }
            }
            
            consolidated_data.append(new_item)
            global_counter += 1

# 통합된 데이터 저장
if consolidated_data:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(consolidated_data, f, ensure_ascii=False, indent=2)
    
    print("통합 완료!")

if __name__ == "__main__":
    merge_samsung_json()