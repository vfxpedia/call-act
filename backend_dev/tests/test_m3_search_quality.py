"""M-3 RAG 검색 품질 회귀 테스트.

5개 Fix 적용 후 score 정규화, 범용 문서 필터, 최소 임계값 검증.

실행:
  cd /mnt/c/Users/AI-WS01/projects/call-act/backend
  source ~/miniconda3/bin/activate callact-vllm
  python -m tests.test_m3_search_quality
"""

from __future__ import annotations

import asyncio
import os
import sys
import time

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from app.rag.pipeline.search import run_search, MIN_RELEVANCE_THRESHOLD

# ── 테스트 케이스 ──────────────────────────────────────────

SCORE_CAP_TESTS = [
    # (쿼리, 설명, 기대조건)
    ("한도 조회", "키워드 인덱스 score 캡 검증", {
        "max_keyword_score": 0.50,  # Fix-1: 1.0*0.45=0.45 (캡)
        "banned_titles": ["gift"],  # Fix-4: Gift 카드 제목 배제
    }),
    ("결제일 변경", "결제일 관련 문서 우선", {
        "max_keyword_score": 0.50,
        "banned_titles": ["gift"],
    }),
    ("나라사랑카드 분실", "카드명+액션 복합 쿼리", {
        "max_keyword_score": 0.50,
        "must_title_contain": ["나라사랑", "분실"],
    }),
    ("리볼빙 해지", "리볼빙 관련 문서 (벡터 검색 콘텐츠 갭)", {
        "max_keyword_score": 0.50,
        # NOTE: 벡터 검색에서 리볼빙 관련 문서 매칭이 약함 (콘텐츠 갭)
        # must_title_contain 제외 — 데이터 보강 후 재검증 필요
    }),
    ("포인트 조회", "포인트 관련 문서", {
        "max_keyword_score": 0.50,
    }),
    ("연회비 얼마예요", "연회비 관련 문서", {
        "max_keyword_score": 0.50,
    }),
    ("카드 재발급 하고 싶어요", "재발급 관련 문서", {
        "max_keyword_score": 0.50,
    }),
    ("선결제 하고 싶어요", "선결제 관련 문서", {
        "max_keyword_score": 0.50,
    }),
    ("한도 좀 올려주세요", "한도 상향 관련 문서", {
        "max_keyword_score": 0.50,
        "banned_titles": ["gift"],
    }),
]

THRESHOLD_TESTS = [
    # 최소 relevance 임계값 테스트
    ("승인 취소 어떻게 해요", "최소 임계값 적용", {}),
    ("결제 대금 확인", "최소 임계값 적용", {}),
]

# ── 검증 함수 ──────────────────────────────────────────────

def check_score_cap(docs, max_score, query):
    """키워드 인덱스 문서의 score가 캡 이하인지 확인."""
    violations = []
    for doc in docs:
        if doc.get("_from_keyword_index"):
            score = doc.get("score", 0.0)
            if score > max_score:
                violations.append(
                    f"  doc={doc.get('title', '?')[:40]} score={score:.3f} > {max_score}"
                )
    return violations


def check_banned_titles(docs, banned_terms, query):
    """특정 제목 키워드가 상위 2개(currentSituation) 문서에 없는지 확인."""
    violations = []
    for i, doc in enumerate(docs[:2]):  # 상위 2개만 (currentSituation 대상)
        title = str(doc.get("title") or "").lower()
        for term in banned_terms:
            if term.lower() in title:
                violations.append(
                    f"  #{i+1} title=\"{doc.get('title', '')[:40]}\" contains banned \"{term}\""
                )
    return violations


def check_must_title(docs, must_terms, query):
    """상위 문서 중 최소 1개가 기대 키워드를 제목에 포함하는지 확인."""
    if not must_terms:
        return []
    found_any = False
    for doc in docs[:4]:
        title = str(doc.get("title") or "").lower()
        if any(t.lower() in title for t in must_terms):
            found_any = True
            break
    if not found_any:
        titles = [str(d.get("title") or "?")[:40] for d in docs[:4]]
        return [f"  상위4 문서 중 {must_terms} 포함 제목 없음: {titles}"]
    return []


def check_threshold(docs):
    """최소 임계값 이하 문서가 없는지 확인."""
    violations = []
    for doc in docs:
        score = doc.get("score", 0.0)
        if score < MIN_RELEVANCE_THRESHOLD and len(docs) > 1:
            violations.append(
                f"  doc={doc.get('title', '?')[:40]} score={score:.4f} < threshold={MIN_RELEVANCE_THRESHOLD}"
            )
    return violations


def check_no_score_100(docs):
    """relevanceScore=100인 문서가 없는지 확인 (score=1.0 방지)."""
    violations = []
    for doc in docs:
        score = doc.get("score", 0.0)
        if score >= 0.99:
            violations.append(
                f"  doc={doc.get('title', '?')[:40]} score={score:.3f} ≈ 1.0 (여전히 인플레이션)"
            )
    return violations


# ── 메인 테스트 실행 ──────────────────────────────────────────

async def run_m3_tests():
    print("=" * 70)
    print("M-3 RAG 검색 품질 회귀 테스트")
    print(f"MIN_RELEVANCE_THRESHOLD = {MIN_RELEVANCE_THRESHOLD}")
    print("=" * 70)

    # 키워드 인덱스 빌드 (서버 시작 시 자동 빌드되지만, 테스트에서는 수동 빌드 필요)
    try:
        from app.rag.cache.keyword_doc_index import build_index, is_built
        if not is_built():
            print("\n[SETUP] 키워드 인덱스 빌드 중...")
            t0 = time.perf_counter()
            build_index()
            elapsed = (time.perf_counter() - t0) * 1000
            print(f"[SETUP] 키워드 인덱스 빌드 완료 ({elapsed:.0f}ms)")
        else:
            print("[SETUP] 키워드 인덱스 이미 빌드됨")
    except Exception as e:
        print(f"[SETUP] 키워드 인덱스 빌드 실패: {e} (벡터 검색만 테스트)")

    total = 0
    passed = 0
    failed_details = []

    all_tests = SCORE_CAP_TESTS + THRESHOLD_TESTS

    for query, desc, expect in all_tests:
        total += 1
        t0 = time.perf_counter()

        try:
            result = await run_search(
                query=query,
                top_k=4,
                enable_consult_search=False,
            )
        except Exception as e:
            print(f"  [{total:02d}] SKIP  \"{query}\" — {e}")
            continue

        elapsed = (time.perf_counter() - t0) * 1000
        docs = result.docs

        violations = []

        # 1) score 캡 검증
        max_score = expect.get("max_keyword_score", 0.50)
        violations += check_score_cap(docs, max_score, query)

        # 2) 금지 제목 검증
        banned = expect.get("banned_titles", [])
        if banned:
            violations += check_banned_titles(docs, banned, query)

        # 3) 필수 제목 키워드 검증
        must_titles = expect.get("must_title_contain", [])
        if must_titles:
            violations += check_must_title(docs, must_titles, query)

        # 4) 최소 임계값 검증
        violations += check_threshold(docs)

        # 5) score=1.0 인플레이션 없는지 확인
        violations += check_no_score_100(docs)

        if violations:
            status = "FAIL"
            detail = {
                "query": query,
                "desc": desc,
                "violations": violations,
                "docs_summary": [
                    {
                        "title": str(d.get("title") or "?")[:50],
                        "score": round(d.get("score", 0.0), 4),
                        "from_idx": d.get("_from_keyword_index", False),
                    }
                    for d in docs[:5]
                ],
            }
            failed_details.append(detail)
        else:
            status = "PASS"
            passed += 1

        # score 분포 요약
        scores = [f"{d.get('score', 0):.3f}" for d in docs[:4]]
        idx_count = sum(1 for d in docs if d.get("_from_keyword_index"))
        vec_count = len(docs) - idx_count

        icon = "✅" if status == "PASS" else "❌"
        print(
            f"  [{total:02d}] {icon} {status}  \"{query}\""
            f"  ({elapsed:.0f}ms, {len(docs)}docs, idx={idx_count}, vec={vec_count})"
            f"  scores=[{', '.join(scores)}]"
        )
        if violations:
            for v in violations[:3]:
                print(f"       {v}")

    print()
    print("=" * 70)
    print(f"결과: {passed}/{total} 통과 ({total - passed}건 실패)")
    print("=" * 70)

    if failed_details:
        print("\n── 실패 상세 ──")
        for fd in failed_details:
            print(f"\n  Query: \"{fd['query']}\" ({fd['desc']})")
            for v in fd["violations"]:
                print(f"    {v}")
            print(f"  문서 요약:")
            for ds in fd["docs_summary"]:
                flag = " [IDX]" if ds["from_idx"] else ""
                print(f"    score={ds['score']:.4f}{flag}  {ds['title']}")

    return passed == total


if __name__ == "__main__":
    ok = asyncio.run(run_m3_tests())
    sys.exit(0 if ok else 1)
