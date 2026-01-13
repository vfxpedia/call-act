import json

def remove_duplicates_by_newline(data_list):
    cleaned_data = []
    
    for item in data_list:
        new_item = item.copy()
        
        if "text" in new_item and isinstance(new_item["text"], str):
            new_item["text"] = new_item["text"].split('\n')[0].strip()
            
        if "content" in new_item and isinstance(new_item["content"], str):
            new_item["content"] = new_item["content"].split('\n')[0].strip()
            
        cleaned_data.append(new_item)
        
    return cleaned_data

input_path = "./../../data/special_card/special_terms.json"

try:
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"파일을 찾을 수 없습니다: {input_path}")
    data = []

if data:
    cleaned_result = remove_duplicates_by_newline(data)

    with open(input_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_result, f, ensure_ascii=False, indent=2)
    
    print(f"저장 완료: {input_path}")