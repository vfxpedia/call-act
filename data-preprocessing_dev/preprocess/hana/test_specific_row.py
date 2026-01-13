import sys
import csv
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from preprocess_hana import normalize_all_masking_v2, extract_scenario_tags

csv_path = Path(__file__).parent.parent.parent / 'data' / 'hana' / 'TS_하나카드_통합 - 시트1.csv'

target_source_id = '21749'

print(f"[INFO] Testing source_id: {target_source_id}")
print(f"[INFO] Using LLM-based slot tagging (GPT-5.2 방식)\n")

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row.get('source_id') == target_source_id:
            content = row.get('consulting_content', '')

            print("[INFO] Original text (first 200 chars):")
            print(content[:200] + "...")
            print()

            # v2 함수 사용: LLM 슬롯 태깅 (불용어 제거 안 함)
            print("[INFO] Processing with normalize_all_masking_v2()...")
            cleaned_text, slot_types = normalize_all_masking_v2(content, use_llm=True)

            # 시나리오 태그 추출
            print("[INFO] Extracting scenario tags...")
            scenario_tags = extract_scenario_tags(cleaned_text)

            # 결과 저장 폴더 생성
            test_output_dir = Path(__file__).parent / 'test_results'
            test_output_dir.mkdir(parents=True, exist_ok=True)
            
            # 결과 저장 (텍스트)
            output_path = test_output_dir / f'test_{target_source_id}.txt'
            with open(output_path, 'w', encoding='utf-8') as out:
                out.write(cleaned_text)

            # 결과 저장 (JSON)
            output_json_path = test_output_dir / f'test_{target_source_id}.json'
            result = {
                "source_id": target_source_id,
                "text": cleaned_text,
                "slot_types": slot_types,
                "scenario_tags": scenario_tags
            }
            with open(output_json_path, 'w', encoding='utf-8') as out:
                json.dump(result, out, ensure_ascii=False, indent=2)

            print(f"\n[SUCCESS] Processed source_id {target_source_id}")
            print(f"[SUCCESS] Text saved to: {output_path}")
            print(f"[SUCCESS] JSON saved to: {output_json_path}")
            print(f"\n[RESULT] Slot types: {slot_types}")
            print(f"[RESULT] Scenario tags: {scenario_tags}")
            print(f"\n[PREVIEW] Processed text (first 500 chars):")
            print(cleaned_text[:500])
            break
    else:
        print(f"[ERROR] source_id {target_source_id} not found")
