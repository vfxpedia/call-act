import json
import os
from collections import defaultdict

TARGET_DIR = "./../../data/special_card"

INPUT_FILES = [
    os.path.join(TARGET_DIR, "kpass_faq.json"),
    os.path.join(TARGET_DIR, "national_happiness_faq.json"),
    os.path.join(TARGET_DIR, "special_cards_vector.json")
]

OUTPUT_FILE = os.path.join(TARGET_DIR, "special_converted.json")

def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def convert():
    result = []
    card_counters = defaultdict(int)

    for file_path in INPUT_FILES:
        file_name = os.path.basename(file_path)
        base_name = os.path.splitext(file_name)[0]

        data = load_json(file_path)

        for item in data:
            # kpass_faq
            if base_name == "kpass_faq":
                card_name = "k패스"
                text = f"{item['question']}\n{item['answer']}"
                title = item["question"]
                category = ""

            # national_happiness_faq
            elif base_name == "national_happiness_faq":
                card_name = "국민행복카드"
                text = f"{item['question']}\n{item['answer']}"
                title = item["question"]
                category = ""

            # special_cards_vector
            elif base_name == "special_cards_vector":
                meta = item.get("metadata", {})
                card_name = meta.get("card_name", "기타")
                text = f"{item.get('text', '')}\n{meta.get('content', '')}".strip()
                title = meta.get("card_name", "")
                category = meta.get("category", "")

            else:
                continue

            card_counters[card_name] += 1
            new_id = f"{card_name}_{card_counters[card_name]}"

            result.append({
                "id": new_id,
                "text": text,
                "metadata": {
                    "title": title,
                    "category": category,
                }
            })

    return result


converted = convert()

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(converted, f, ensure_ascii=False, indent=2)

print(f"변환 완료 : {OUTPUT_FILE}, 총 {len(converted)}개")
