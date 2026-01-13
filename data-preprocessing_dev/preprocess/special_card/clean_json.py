import os
import json

# 제거할 문구 목록
exclude_phrases = [
    "국민행복카드를 이용해 주셔서 감사합니다.",
    "국민행복카드에 대한 관심 감사합니다.",
    "감사해요.",
    "감사합니다.",
    "감사드립니다.",
    "•",
    "※",
    '/',
    "·",
    '[',
    ']',
    '\n',
    ' 〮'
]

TARGET_DIR = "./../../data/special_card"


def remove_exclude_phrases_from_value(value: str) -> str:
    for phrase in exclude_phrases:
        value = value.replace(phrase, "")
    return value.strip()


def clean_json(obj):
    if isinstance(obj, dict):
        return {k: clean_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_json(item) for item in obj]
    elif isinstance(obj, str):
        return remove_exclude_phrases_from_value(obj)
    else:
        return obj


for filename in os.listdir(TARGET_DIR):
    if not filename.endswith(".json"):
        continue

    file_path = os.path.join(TARGET_DIR, filename)

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned_data = clean_json(data)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

    print(f"정리 완료: {filename}")
