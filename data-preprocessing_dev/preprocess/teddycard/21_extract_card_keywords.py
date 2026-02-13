"""
Step 2: 키워드 없는 카드 상품 195건에 키워드 자동 추출

추출 소스:
1. structured.mainBenefits → 핵심 혜택 키워드
2. card name → 카드 특성 키워드 (K-패스, 체크, 법인 등)
3. main_benefits 텍스트 → 패턴 매칭
4. 공통 기본 키워드 (연회비, 혜택)

재적재 호환: JSON 파일의 keywords 필드를 수정
→ load_teddycard.py가 doc.get("keywords", []) 으로 읽으므로 자동 반영
"""

import json
import os
import re
from datetime import datetime
from collections import Counter

# ─── 경로 설정 ───
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIRS = [
    os.path.join(BASE, "..", "..", "data", "teddycard"),
    os.path.join(BASE, "..", "..", "..", "..", "backend_dev", "app", "db", "data", "teddycard"),
]
FILENAME = "teddycard_card_products_with_embeddings.json"

# ─── 키워드 추출 규칙 ───

# 카드명에서 추출할 패턴
NAME_PATTERNS = {
    r"K-?패스|케이패스": "K-패스",
    r"체크": "체크카드",
    r"법인": "법인카드",
    r"국민행복": "국민행복카드",
    r"나라사랑": "나라사랑카드",
    r"다둥이|다자녀": "다둥이카드",
    r"시니어": "시니어카드",
    r"민생": "민생카드",
    r"프리미엄|플래티넘|PLATINUM": "프리미엄",
    r"골드|GOLD": "골드",
    r"기업|비즈": "기업카드",
}

# 혜택 텍스트에서 추출할 패턴
BENEFIT_PATTERNS = {
    r"할인": "할인",
    r"적립|포인트|마일리지|캐시백": "포인트",
    r"대출|현금서비스": "대출",
    r"할부": "할부",
    r"교통|대중교통|버스|지하철": "교통",
    r"해외|글로벌|overseas": "해외이용",
    r"간편결제|Pay|페이": "간편결제",
    r"자동이체|자동납부": "자동이체",
    r"보험|보상": "보험",
    r"쇼핑|온라인|오프라인": "쇼핑",
    r"주유|충전": "주유",
    r"통신|통신료|SKT|KT|LG": "통신",
    r"항공|마일|대한항공|아시아나": "항공마일리지",
    r"ETC|하이패스|톨게이트": "ETC",
    r"기프트|선물": "기프트카드",
    r"전월.{0,5}실적": "실적조건",
}

# 카드 타입별 기본 키워드
BASE_KEYWORDS = {
    "credit": ["연회비", "혜택"],
    "debit": ["혜택"],
}


def extract_keywords_from_card(doc):
    """카드 상품에서 키워드 추출"""
    keywords = set()
    name = doc.get("name", "")
    card_type = doc.get("card_type", "credit")
    structured = doc.get("structured", {}) or {}
    main_benefits = doc.get("main_benefits", "")
    benefits_list = structured.get("mainBenefits", []) or []

    # 1. 기본 키워드
    for kw in BASE_KEYWORDS.get(card_type, ["혜택"]):
        keywords.add(kw)

    # 2. 카드명 패턴
    for pattern, kw in NAME_PATTERNS.items():
        if re.search(pattern, name, re.IGNORECASE):
            keywords.add(kw)

    # 3. structured.mainBenefits 에서 혜택 패턴
    benefits_text = " ".join(benefits_list) if benefits_list else ""
    all_text = f"{benefits_text} {main_benefits}"

    for pattern, kw in BENEFIT_PATTERNS.items():
        if re.search(pattern, all_text, re.IGNORECASE):
            keywords.add(kw)

    # 4. structured.benefitDetails 키에서 추출
    benefit_details = structured.get("benefitDetails", {}) or {}
    if isinstance(benefit_details, dict):
        if benefit_details.get("pointAccrual"):
            keywords.add("포인트")
        if benefit_details.get("conditions"):
            keywords.add("실적조건")

    # 5. 연회비 정보 확인
    annual_fee = structured.get("annualFee", {}) or {}
    if isinstance(annual_fee, dict):
        domestic = annual_fee.get("domestic")
        if domestic and domestic not in ("None", "없음", None):
            keywords.add("연회비")

    # 최소 3개 보장
    if len(keywords) < 3:
        keywords.add("카드")

    # 최대 10개 제한, 정렬
    return sorted(list(keywords))[:10]


def process_file(filepath):
    """카드 상품 JSON 파일 처리"""
    print(f"\n{'='*60}")
    print(f"Processing: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        docs = json.load(f)

    total = len(docs)
    before_no_kw = sum(1 for d in docs if not d.get("keywords") or len(d["keywords"]) == 0)
    print(f"Total: {total}, No keywords: {before_no_kw} ({before_no_kw*100//total}%)")

    # 키워드 추출
    filled = 0
    all_new_kws = []
    for doc in docs:
        if not doc.get("keywords") or len(doc["keywords"]) == 0:
            new_kws = extract_keywords_from_card(doc)
            doc["keywords"] = new_kws
            filled += 1
            all_new_kws.extend(new_kws)

    after_no_kw = sum(1 for d in docs if not d.get("keywords") or len(d["keywords"]) == 0)
    print(f"Filled: {filled} documents")
    print(f"After: No keywords: {after_no_kw} ({after_no_kw*100//total}%)")

    # 추출된 키워드 분포
    kw_counter = Counter(all_new_kws)
    print(f"\nNew keywords distribution (top 15):")
    for kw, count in kw_counter.most_common(15):
        print(f"  {kw}: {count}")

    # 샘플 출력
    no_kw_docs = [d for d in docs if filled > 0]
    sample_filled = [(d["name"], d["keywords"]) for d in docs if d.get("_just_filled")][:5]

    return docs, filled


def main():
    print("=" * 60)
    print("Step 2: 카드 상품 키워드 추출")
    print(f"Date: {datetime.now().isoformat()}")
    print("=" * 60)

    for data_dir in DATA_DIRS:
        filepath = os.path.join(data_dir, FILENAME)
        if not os.path.exists(filepath):
            print(f"\nSKIP: {filepath}")
            continue

        # 메타 백업
        backup_dir = os.path.join(data_dir, ".back")
        os.makedirs(backup_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")

        with open(filepath, "r", encoding="utf-8") as f:
            docs_orig = json.load(f)
        meta = [{"id": d["id"], "keywords": d.get("keywords", [])} for d in docs_orig]
        backup_path = os.path.join(backup_dir, f"card_products_keywords_before_step2_{ts}.json.meta")
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        print(f"\nBackup: {backup_path}")

        docs, filled = process_file(filepath)

        if filled > 0:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(docs, f, ensure_ascii=False)
            print(f"\nSAVED: {filepath}")

    print(f"\n{'='*60}")
    print("Step 2 COMPLETE")
    print("재적재 시 자동 반영됨")


if __name__ == "__main__":
    main()
