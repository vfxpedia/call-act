# 별개 파일로 크롤링된 news & notice 데이터를 각 하나의 파일로 병합하는 스크립트

import json
import os
from pathlib import Path

json_dir = Path("data/samsung/notice/json")
output_file = json_dir / "notice.json"

total = []
counter = 1

json_files = sorted(json_dir.glob("*.json"))

for json_file in json_files:
    if json_file.name == "notice.json":
        continue
    
    print(f"Processing: {json_file.name}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        for item in data:
            item['id'] = f"소비자주의경보_{counter}"
            total.append(item)
            counter += 1
    else:
        data['id'] = f"소비자주의경보_{counter}"
        total.append(data)
        counter += 1

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(total, f, ensure_ascii=False, indent=2)

print(f"\n✓ Successfully merged {len(total)} items into {output_file}")
print(f"Total files processed: {len(json_files) - (1 if any(f.name == 'notice.json' for f in json_files) else 0)}")
