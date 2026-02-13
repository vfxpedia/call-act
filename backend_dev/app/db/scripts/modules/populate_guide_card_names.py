"""service_guide_documents metadata에 card_name 매핑.

가이드 ID 접두사에서 카드명을 추출하여 metadata.card_name에 저장합니다.
01a_setup_callact_db.py에서 테디카드 데이터 적재 후 자동 호출됩니다.

단독 실행:
    cd backend_dev/app/db/scripts
    python -m modules.populate_guide_card_names
"""
from psycopg2.extensions import connection as psycopg2_connection


# ID 접두사 → card_name 매핑 규칙
ID_PREFIX_TO_CARD = {
    # 한글 접두사
    "나라사랑체크카드": "나라사랑카드",
    "국민행복카드": "국민행복카드",
    "서울시다둥이행복카드": "서울시다둥이행복카드",
    "네이버페이카드": "네이버페이카드",
    "쿠팡와우카드": "쿠팡와우카드",
    "k패스": "K패스",
    "K패스": "K패스",
    # 영문 접두사
    "narasarang_faq": "나라사랑카드",
    "naverpay": "네이버페이카드",
    "minsaeng_faq": "민생회복소비쿠폰",
    "hyundai_applepay": "Apple Pay",
}


def _extract_card_name(guide_id: str):
    """가이드 ID에서 카드명 추출."""
    for prefix, card_name in ID_PREFIX_TO_CARD.items():
        if guide_id.startswith(prefix):
            return card_name
    return None


def populate_guide_card_names(conn: psycopg2_connection):
    """service_guide_documents metadata에 card_name 매핑 실행."""
    print("\n" + "=" * 60)
    print("[D-7] service_guide_documents card_name 매핑")
    print("=" * 60)

    cur = conn.cursor()

    # 현재 상태 확인
    cur.execute(
        "SELECT COUNT(*) FROM service_guide_documents "
        "WHERE metadata->>'card_name' IS NOT NULL AND metadata->>'card_name' != ''"
    )
    before = cur.fetchone()[0]
    print(f"  [BEFORE] card_name 있는 가이드: {before}건")

    # 모든 가이드 ID 조회
    cur.execute("SELECT id FROM service_guide_documents ORDER BY id")
    all_ids = [r[0] for r in cur.fetchall()]
    print(f"  전체 가이드: {len(all_ids)}건")

    # 매핑 실행
    updated = 0
    card_counts = {}
    for guide_id in all_ids:
        card_name = _extract_card_name(guide_id)
        if card_name:
            cur.execute(
                "UPDATE service_guide_documents "
                "SET metadata = COALESCE(metadata, '{}'::jsonb) || jsonb_build_object('card_name', %s) "
                "WHERE id = %s",
                (card_name, guide_id),
            )
            updated += 1
            card_counts[card_name] = card_counts.get(card_name, 0) + 1

    conn.commit()

    # 결과 확인
    cur.execute(
        "SELECT COUNT(*) FROM service_guide_documents "
        "WHERE metadata->>'card_name' IS NOT NULL AND metadata->>'card_name' != ''"
    )
    after = cur.fetchone()[0]

    print(f"  [AFTER] card_name 있는 가이드: {after}건 (변경: +{after - before}건)")
    for cn, cnt in sorted(card_counts.items(), key=lambda x: -x[1]):
        print(f"    {cn:30s}: {cnt}건")

    cur.close()
    print(f"  [D-7] 완료: {updated}건 매핑")


if __name__ == "__main__":
    from modules import connect_db
    conn = connect_db()
    try:
        populate_guide_card_names(conn)
    finally:
        conn.close()
