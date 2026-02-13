# Data 세션 작업 지시: D-7 가이드 metadata card_name 매핑

> **지시자**: AI/ML 팀장 (M 세션)
> **긴급도**: 최상
> **배경 문서**: `docs/levelup/06_RAG_CARD_RETRIEVAL_FIX.md` (근본 원인 분석 전체)

---

## 배경

RAG 카드 검색이 정상 작동하지 않는 근본 원인 중 하나:
**service_guide_documents 1,251건의 `metadata->>'card_name'`이 전부 NULL**

```sql
SELECT COUNT(*) FROM service_guide_documents WHERE metadata->>'card_name' IS NOT NULL;
-- 결과: 0건 (2026-02-10 22:30 확인)
```

그러나 가이드 ID 자체에 카드명이 인코딩되어 있어서, ID 패턴으로 card_name 추출이 가능합니다.

---

## 작업 D-7: service_guide_documents metadata card_name 매핑

### 가이드 ID → 카드명 매핑 규칙

DB 직접 조사 결과, 다음 규칙으로 209건 매핑 가능:

```python
# ID 접두사 → card_name 매핑
ID_PREFIX_TO_CARD = {
    # 한글 접두사 (ID 형식: "접두사_숫자")
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
```

### 예상 매핑 결과

| card_name | 건수 | ID 패턴 |
|-----------|------|---------|
| K패스 | 41건 | `k패스_*`, `K패스_*` |
| Apple Pay | 34건 | `hyundai_applepay_*` |
| 국민행복카드 | 28건 | `국민행복카드_*` |
| 네이버페이카드 | 23건 | `네이버페이카드_*`, `naverpay_*` |
| 나라사랑카드 | 36건 | `나라사랑체크카드_*`, `narasarang_faq_*` |
| 서울시다둥이행복카드 | 19건 | `서울시다둥이행복카드_*` |
| 민생회복소비쿠폰 | 15건 | `minsaeng_faq_*` |
| 쿠팡와우카드 | 8건 | `쿠팡와우카드_*` |
| **합계** | **~209건** | |

나머지 1,042건 (sinhan_terms 988, merged 35, plumb 19)은 일반 약관/가이드 → card_name NULL 유지 (정상)

### 구현 스크립트

파일: `backend_dev/app/db/scripts/modules/populate_guide_card_names.py` (신규 생성)

```python
#!/usr/bin/env python3
"""service_guide_documents metadata에 card_name 매핑.

가이드 ID 접두사에서 카드명을 추출하여 metadata.card_name에 저장합니다.

Usage:
    cd /mnt/c/Users/AI-WS01/projects/call-act
    source ~/miniconda3/bin/activate callact-vllm
    python backend_dev/app/db/scripts/modules/populate_guide_card_names.py
"""
import psycopg2
import json

DB_CONFIG = {
    "host": "localhost",
    "port": 5555,
    "dbname": "callact_db",
    "user": "callact_admin",
    "password": "callact_pwd1",
}

# ID 접두사 → card_name 매핑 규칙
ID_PREFIX_TO_CARD = {
    "나라사랑체크카드": "나라사랑카드",
    "국민행복카드": "국민행복카드",
    "서울시다둥이행복카드": "서울시다둥이행복카드",
    "네이버페이카드": "네이버페이카드",
    "쿠팡와우카드": "쿠팡와우카드",
    "k패스": "K패스",
    "K패스": "K패스",
    "narasarang_faq": "나라사랑카드",
    "naverpay": "네이버페이카드",
    "minsaeng_faq": "민생회복소비쿠폰",
    "hyundai_applepay": "Apple Pay",
}


def extract_card_name(guide_id: str) -> str | None:
    """가이드 ID에서 카드명 추출."""
    for prefix, card_name in ID_PREFIX_TO_CARD.items():
        if guide_id.startswith(prefix):
            return card_name
    return None


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # 현재 상태 확인
    cur.execute(
        "SELECT COUNT(*) FROM service_guide_documents "
        "WHERE metadata->>'card_name' IS NOT NULL AND metadata->>'card_name' != ''"
    )
    before = cur.fetchone()[0]
    print(f"[BEFORE] card_name 있는 가이드: {before}건")

    # 모든 가이드 ID 조회
    cur.execute("SELECT id FROM service_guide_documents ORDER BY id")
    all_ids = [r[0] for r in cur.fetchall()]
    print(f"전체 가이드: {len(all_ids)}건")

    # 매핑 실행
    updated = 0
    card_counts = {}
    for guide_id in all_ids:
        card_name = extract_card_name(guide_id)
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

    print(f"\n[AFTER] card_name 있는 가이드: {after}건 (변경: +{after - before}건)")
    print(f"\n카드별 매핑 건수:")
    for cn, cnt in sorted(card_counts.items(), key=lambda x: -x[1]):
        print(f"  {cn:30s}: {cnt}건")

    # 검증
    cur.execute(
        "SELECT metadata->>'card_name' AS cn, COUNT(*) "
        "FROM service_guide_documents "
        "WHERE metadata->>'card_name' IS NOT NULL AND metadata->>'card_name' != '' "
        "GROUP BY cn ORDER BY COUNT(*) DESC"
    )
    print(f"\n[검증] DB 그룹별 카운트:")
    for cn, cnt in cur.fetchall():
        print(f"  {cn:30s}: {cnt}건")

    cur.close()
    conn.close()
    print(f"\n✅ D-7 완료: {updated}건 매핑")


if __name__ == "__main__":
    main()
```

### 실행 방법

```bash
cd /mnt/c/Users/AI-WS01/projects/call-act
source ~/miniconda3/bin/activate callact-vllm
python backend_dev/app/db/scripts/modules/populate_guide_card_names.py
```

### 검증

```sql
-- 1. 전체 매핑 건수
SELECT COUNT(*) FROM service_guide_documents
WHERE metadata->>'card_name' IS NOT NULL AND metadata->>'card_name' != '';
-- 기대: ~209건

-- 2. 카드별 분포
SELECT metadata->>'card_name' AS cn, COUNT(*)
FROM service_guide_documents
WHERE metadata->>'card_name' IS NOT NULL AND metadata->>'card_name' != ''
GROUP BY cn ORDER BY COUNT(*) DESC;

-- 3. 특정 가이드 확인
SELECT id, title, metadata->>'card_name' AS cn
FROM service_guide_documents
WHERE id LIKE '나라사랑%' OR id LIKE 'narasarang%'
LIMIT 5;
```

### 01a 스크립트 동기화 (중요!)

**D-7은 DB 런타임 수정**입니다. DB를 재생성하면 다시 NULL이 됩니다.
따라서 `01a_setup_callact_db.py`에도 card_name 매핑 로직을 추가하거나,
`01a` 실행 후 `populate_guide_card_names.py`를 자동 실행하도록 연결해주세요.

---

## 완료 후

1. CLAUDE.md Data 섹션에 D-7 완료 기록 (타임스탬프 포함)
2. Backend 세션에 완료 알림 → B-8b 진행 가능
3. M 세션에 검증 결과 공유
