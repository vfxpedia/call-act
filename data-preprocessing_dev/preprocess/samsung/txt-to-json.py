import json
import re
import os

def process_to_json(target_dir):
    # 불필요한 문장 제거
    exclude_phrases = ["감사해요", "감사합니다", "감사드립니다"]
    
    output_dir = os.path.join(target_dir, 'json')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # txt 파일 순회
    files = [f for f in os.listdir(target_dir) if f.endswith('.txt')]
    print(files)

    for file in files:
        input_path = os.path.join(target_dir, file)
        
        # 원본 파일명을 유지
        output_file = f"{os.path.splitext(file)[0]}.json"
        output_path = os.path.join(output_dir, output_file)

        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        data = {}

        data['title'] = lines[0].strip()
        data['date'] = lines[1].strip()

        content_lines = []
        for line in lines[2:]:
            if any(phrase in line for phrase in exclude_phrases):
                continue
            content_lines.append(line)

        full_content = "".join(content_lines)

        # 가독성 처리
        # \n (줄바꿈) 뒤에 [ \t]* (공백이나 탭이 0개 이상) 오는 패턴이
        # {3,} (3번 이상) 반복되면 -> '\n\n' (줄바꿈 2개)로 변경
        processed_content = re.sub(r'(\n[ \t]*){3,}', '\n\n', full_content)
        
        data['content'] = processed_content.strip()

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"[완료] {file}")

    print("=== 작업 완료 ===")

if __name__ == "__main__":
    TARGET_DIR = 'data/samsung/notice/'
    process_to_json(TARGET_DIR)