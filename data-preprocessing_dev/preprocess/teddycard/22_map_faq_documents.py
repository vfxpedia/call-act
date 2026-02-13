"""
Step 3: FAQ related_document_id를 실 문서 ID로 매핑

변경 대상: backend_dev/app/db/scripts/modules/load_frequent_inquiries.py
  - CATEGORY_CONTENT_MAP의 related_document_id (5건)
  - DEFAULT_CONTENT_TEMPLATE의 related_document_id (1건)
  - FALLBACK_INQUIRIES_DATA의 related_document_id (5건)

매핑 근거: service_guide_documents의 guide 타입 문서 74건 중
카테고리별 키워드/제목/내용 매칭으로 최적 문서 선정

재적재 호환: Python 코드 직접 수정 → 01a_setup_callact_db.py 재실행 시 자동 반영 ✅
"""

import json
import os

# ─── 매핑 테이블 (이 파일은 검증/문서용) ───

FAQ_DOCUMENT_MAPPING = {
    # CATEGORY_CONTENT_MAP (상담 데이터 기반 FAQ)
    "category_content_map": {
        "청구문의/청구서": {
            "old_id": "billing-1-1-1",
            "new_id": "카드대금 납부_merged",
            "new_title": "카드대금 납부",
            "reason": "청구/결제일/납부 관련 가장 직접적인 가이드"
        },
        "이용내역 안내": {
            "old_id": "usage-1-1-1",
            "new_id": "신용카드_활용법_merged",
            "new_title": "신용카드 활용법",
            "reason": "이용내역, 명세서, 결제 관련 종합 가이드"
        },
        "한도관련 문의/처리": {
            "old_id": "limit-1-1-1",
            "new_id": "카드상품별_거래조건_이자율__수수료_등__merged",
            "new_title": "카드상품별 거래조건(이자율, 수수료 등)",
            "reason": "한도, 이자율, 수수료 등 거래조건 포함"
        },
        "분실/도난 신청/처리": {
            "old_id": "card-1-1-1",
            "new_id": "카드분실_도난_관련피해_예방_및_대응방법_merged",
            "new_title": "카드분실·도난 관련 피해 예방 및 대응방법",
            "reason": "분실/도난 대응 정확 일치"
        },
        "결제방식 안내": {
            "old_id": "payment-1-1-1",
            "new_id": "신용카드_관련주요_용어_안내_merged",
            "new_title": "신용카드 관련 주요 용어 안내",
            "reason": "결제, 할부, 리볼빙 등 결제방식 용어 설명"
        }
    },

    # DEFAULT_CONTENT_TEMPLATE (매핑 없는 카테고리 기본값)
    "default_template": {
        "old_id": "general-1-1-1",
        "new_id": "신용카드의_종류_merged",
        "new_title": "신용카드의 종류",
        "reason": "일반적인 신용카드 정보 안내"
    },

    # FALLBACK_INQUIRIES_DATA (상담 데이터 없을 때 폴백)
    "fallback_data": {
        "카드 분실": {
            "old_id": "card-1-1-1",
            "new_id": "카드분실_도난_관련피해_예방_및_대응방법_merged",
            "new_title": "카드분실·도난 관련 피해 예방 및 대응방법",
            "reason": "분실/도난 대응 정확 일치"
        },
        "해외 결제": {
            "old_id": "card-2-1-1",
            "new_id": "해외여행_시IC카드_이용팁_merged",
            "new_title": "해외여행 시 IC카드 이용팁",
            "reason": "해외 이용 관련 가이드"
        },
        "포인트 적립": {
            "old_id": "card-1-2-1",
            "new_id": "신용카드_포인트활용방법_merged",
            "new_title": "신용카드 포인트 활용방법",
            "reason": "포인트 적립/활용 정확 일치"
        },
        "연회비 환불": {
            "old_id": "card-3-1-1",
            "new_id": "신용카드_선택_시_고려사항_merged",
            "new_title": "신용카드 선택 시 고려사항",
            "reason": "연회비 키워드 포함, 카드 선택 시 고려사항"
        },
        "한도 증액": {
            "old_id": "card-4-1-1",
            "new_id": "카드상품별_거래조건_이자율__수수료_등__merged",
            "new_title": "카드상품별 거래조건(이자율, 수수료 등)",
            "reason": "한도, 이자율 등 거래조건 포함"
        }
    }
}


def verify_mapping():
    """매핑 유효성 검증"""
    print("=" * 60)
    print("Step 3: FAQ 실 문서 매핑 검증")
    print("=" * 60)

    # 1. 실 문서 ID 존재 확인
    base = os.path.dirname(os.path.abspath(__file__))
    guides_path = os.path.join(base, "..", "..", "data", "teddycard",
                               "teddycard_service_guides_with_embeddings.json")

    if not os.path.exists(guides_path):
        print(f"SKIP: {guides_path} not found")
        return

    with open(guides_path, "r", encoding="utf-8") as f:
        guides = json.load(f)

    guide_ids = {d["id"] for d in guides}
    print(f"\nTotal service_guide_documents: {len(guide_ids)}")

    # 2. 모든 매핑 ID 검증
    all_new_ids = set()

    print("\n--- CATEGORY_CONTENT_MAP ---")
    for cat, mapping in FAQ_DOCUMENT_MAPPING["category_content_map"].items():
        exists = mapping["new_id"] in guide_ids
        status = "OK" if exists else "MISSING!"
        print(f"  {status}: {cat}")
        print(f"    {mapping['old_id']} → {mapping['new_id']}")
        all_new_ids.add(mapping["new_id"])

    print("\n--- DEFAULT_CONTENT_TEMPLATE ---")
    default = FAQ_DOCUMENT_MAPPING["default_template"]
    exists = default["new_id"] in guide_ids
    status = "OK" if exists else "MISSING!"
    print(f"  {status}: {default['old_id']} → {default['new_id']}")
    all_new_ids.add(default["new_id"])

    print("\n--- FALLBACK_INQUIRIES_DATA ---")
    for kw, mapping in FAQ_DOCUMENT_MAPPING["fallback_data"].items():
        exists = mapping["new_id"] in guide_ids
        status = "OK" if exists else "MISSING!"
        print(f"  {status}: {kw}")
        print(f"    {mapping['old_id']} → {mapping['new_id']}")
        all_new_ids.add(mapping["new_id"])

    # 3. Python 소스 코드 mock ID 잔존 확인
    loader_path = os.path.join(base, "..", "..", "..", "..", "backend_dev",
                                "app", "db", "scripts", "modules",
                                "load_frequent_inquiries.py")

    if os.path.exists(loader_path):
        with open(loader_path, "r", encoding="utf-8") as f:
            source = f.read()

        mock_ids = ["billing-1-1-1", "usage-1-1-1", "limit-1-1-1",
                    "card-1-1-1", "card-2-1-1", "card-1-2-1",
                    "card-3-1-1", "card-4-1-1", "payment-1-1-1", "general-1-1-1"]

        print("\n--- Mock ID 잔존 검사 ---")
        remaining = [m for m in mock_ids if m in source]
        if remaining:
            for m in remaining:
                print(f"  FAIL: {m} still in source!")
        else:
            print("  PASS: 모든 mock ID 제거됨")

    print(f"\n고유 실 문서 매핑: {len(all_new_ids)}건")
    print("=" * 60)
    print("Step 3 검증 COMPLETE")


if __name__ == "__main__":
    verify_mapping()
