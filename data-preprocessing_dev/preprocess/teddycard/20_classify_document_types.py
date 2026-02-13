"""
Step 1: service_guide_documents의 document_type 정규화

현재 값 → 변경:
  terms (1092)       → terms (유지)
  faq (107)          → faq (유지)
  usage_guide (42)   → guide
  service_guide (32) → guide

재적재 호환: JSON 파일의 document_type 필드를 수정
→ load_teddycard.py가 doc.get("document_type") 으로 읽으므로 자동 반영
"""

import json
import os
import shutil
from datetime import datetime
from collections import Counter

# ─── 경로 설정 ───
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIRS = [
    os.path.join(BASE, "..", "..", "data", "teddycard"),                              # data-preprocessing_dev
    os.path.join(BASE, "..", "..", "..", "..", "backend_dev", "app", "db", "data", "teddycard"),  # backend_dev
]

FILENAME = "teddycard_service_guides_with_embeddings.json"

# ─── 매핑 규칙 ───
TYPE_MAP = {
    "terms": "terms",
    "faq": "faq",
    "usage_guide": "guide",
    "service_guide": "guide",
}


def classify_documents(filepath):
    """JSON 파일의 document_type을 정규화"""
    print(f"\n{'='*60}")
    print(f"Processing: {filepath}")
    print(f"{'='*60}")

    with open(filepath, "r", encoding="utf-8") as f:
        docs = json.load(f)

    print(f"Total documents: {len(docs)}")

    # 변경 전 분포
    before = Counter(d.get("document_type", "none") for d in docs)
    print(f"\nBEFORE:")
    for dt, count in before.most_common():
        print(f"  {dt}: {count}")

    # 분류 적용
    changed = 0
    for doc in docs:
        old_type = doc.get("document_type", "service_guide")
        new_type = TYPE_MAP.get(old_type, "general")  # 미매핑 → general

        if old_type != new_type:
            doc["document_type"] = new_type
            changed += 1

    # 변경 후 분포
    after = Counter(d.get("document_type", "none") for d in docs)
    print(f"\nAFTER:")
    for dt, count in after.most_common():
        print(f"  {dt}: {count}")

    print(f"\nChanged: {changed} documents")
    return docs, changed


def main():
    print("=" * 60)
    print("Step 1: document_type 정규화")
    print(f"Date: {datetime.now().isoformat()}")
    print("=" * 60)

    for data_dir in DATA_DIRS:
        filepath = os.path.join(data_dir, FILENAME)

        if not os.path.exists(filepath):
            print(f"\nSKIP (not found): {filepath}")
            continue

        # 백업
        backup_dir = os.path.join(data_dir, ".back")
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"service_guides_before_step1_{timestamp}.json.meta")

        # 메타데이터만 백업 (전체 파일은 너무 큼, 임베딩 제외)
        with open(filepath, "r", encoding="utf-8") as f:
            docs_orig = json.load(f)
        meta_backup = [{"id": d["id"], "document_type": d.get("document_type", "")} for d in docs_orig]
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(meta_backup, f, ensure_ascii=False, indent=2)
        print(f"\nBackup saved: {backup_path} ({len(meta_backup)} entries)")

        # 분류 실행
        docs, changed = classify_documents(filepath)

        if changed > 0:
            # 저장
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(docs, f, ensure_ascii=False)
            print(f"\nSAVED: {filepath}")
        else:
            print(f"\nNO CHANGES needed for: {filepath}")

    print(f"\n{'='*60}")
    print("Step 1 COMPLETE")
    print("재적재 시 자동 반영됨 (load_teddycard.py → doc.get('document_type'))")
    print("='*60")


if __name__ == "__main__":
    main()
