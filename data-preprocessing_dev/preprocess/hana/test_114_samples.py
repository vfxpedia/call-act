# 114개 샘플 테스트 스크립트 (57 카테고리 × 2개)
import sys
import csv
import json
import time
from pathlib import Path
from collections import defaultdict
sys.path.append(str(Path(__file__).parent))

from preprocess_hana import normalize_all_masking_v2, extract_scenario_tags

csv_path = Path(__file__).parent.parent.parent / 'data' / 'hana' / 'TS_하나카드_통합 - 시트1.csv'
output_dir = Path(__file__).parent / 'test_results' / 'samples_114'
output_dir.mkdir(parents=True, exist_ok=True)

print(f"[INFO] Output directory: {output_dir}")
print(f"[INFO] Reading CSV file...")

# 카테고리별로 최대 2개 row 수집
category_rows = defaultdict(list)
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        cat = row.get('consulting_category', '')
        if cat and len(category_rows[cat]) < 2:
            category_rows[cat].append(row)

# 총 샘플 수 계산
total_samples = sum(len(rows) for rows in category_rows.values())
print(f"[INFO] Found {len(category_rows)} categories")
print(f"[INFO] Total samples to process: {total_samples}")
print(f"[INFO] Starting test...\n")

# 결과 저장용
results = []
all_slot_types = set()
all_scenario_tags = set()

# 전체 시간 측정
start_time = time.time()

sample_idx = 0
for category in sorted(category_rows.keys()):
    rows = category_rows[category]
    
    for row_idx, row in enumerate(rows):
        sample_idx += 1
        source_id = row.get('source_id', '')
        content = row.get('consulting_content', '')
        
        print(f"[{sample_idx:3}/{total_samples}] Category: {category[:25]:<25} | source_id: {source_id}")
        
        try:
            row_start = time.time()
            
            # 마스킹 처리
            cleaned_text, slot_types = normalize_all_masking_v2(content, use_llm=True)
            
            # 시나리오 태그 추출
            scenario_tags = extract_scenario_tags(cleaned_text)
            
            row_elapsed = time.time() - row_start
            
            # 슬롯 타입과 시나리오 태그 수집
            all_slot_types.update(slot_types)
            all_scenario_tags.update(scenario_tags)
            
            result = {
                "source_id": source_id,
                "category": category,
                "sample_index": row_idx + 1,
                "slot_types": slot_types,
                "scenario_tags": scenario_tags,
                "text_length": len(cleaned_text),
                "processing_time": round(row_elapsed, 2),
                "status": "success"
            }
            
            # 개별 파일 저장 (sample_1, sample_2 구분)
            output_file = output_dir / f"test_{source_id}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# source_id: {source_id}\n")
                f.write(f"# category: {category}\n")
                f.write(f"# sample_index: {row_idx + 1}/2\n")
                f.write(f"# slot_types: {slot_types}\n")
                f.write(f"# scenario_tags: {scenario_tags}\n")
                f.write(f"# processing_time: {row_elapsed:.2f}s\n")
                f.write("=" * 60 + "\n")
                f.write(cleaned_text)
            
            print(f"         → time: {row_elapsed:.2f}s | slots: {len(slot_types)} | tags: {len(scenario_tags)} | [OK]")
            
        except Exception as e:
            result = {
                "source_id": source_id,
                "category": category,
                "sample_index": row_idx + 1,
                "slot_types": [],
                "scenario_tags": [],
                "text_length": 0,
                "processing_time": 0,
                "status": f"error: {str(e)}"
            }
            print(f"         → [ERROR] {str(e)}")
        
        results.append(result)

# 전체 소요 시간
total_elapsed = time.time() - start_time

# 전체 요약 저장
summary = {
    "total_categories": len(category_rows),
    "total_samples": total_samples,
    "success_count": sum(1 for r in results if r["status"] == "success"),
    "error_count": sum(1 for r in results if r["status"] != "success"),
    "total_processing_time_seconds": round(total_elapsed, 2),
    "average_time_per_sample": round(total_elapsed / total_samples, 2) if total_samples > 0 else 0,
    "all_slot_types": sorted(list(all_slot_types)),
    "all_slot_types_count": len(all_slot_types),
    "all_scenario_tags": sorted(list(all_scenario_tags)),
    "all_scenario_tags_count": len(all_scenario_tags),
    "results": results
}

summary_file = output_dir / "summary.json"
with open(summary_file, 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print()
print("=" * 60)
print(f"[COMPLETE] Processed {total_samples} samples from {len(category_rows)} categories")
print(f"[COMPLETE] Success: {summary['success_count']}, Errors: {summary['error_count']}")
print(f"[COMPLETE] Total time: {total_elapsed/60:.2f} minutes ({total_elapsed:.1f}s)")
print(f"[COMPLETE] Average per sample: {summary['average_time_per_sample']:.2f}s")
print(f"[COMPLETE] Unique slot types: {len(all_slot_types)}")
print(f"[COMPLETE] Unique scenario tags: {len(all_scenario_tags)}")
print(f"[COMPLETE] Summary saved to: {summary_file}")
print()
print("[SLOT TYPES]:")
for st in sorted(all_slot_types):
    print(f"  - {st}")
print()
print("[SCENARIO TAGS]:")
for st in sorted(all_scenario_tags):
    print(f"  - {st}")

