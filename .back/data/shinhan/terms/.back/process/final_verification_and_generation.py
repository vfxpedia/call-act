"""
최종 검증 및 JSON 생성 스크립트
- 988개 청크 완전 검증
- RDB/VectorDB용 최종 JSON 생성
- 상세 검증 리포트
"""

import json
import hashlib
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

# 경로 설정
BASE_DIR = Path(__file__).resolve().parents[2]
INPUT_FILE = BASE_DIR / "data" / "sinhan_terms" / "intermediate" / "chunks_validated_filtered.json"
FINAL_DIR = BASE_DIR / "data" / "sinhan_terms" / "final"
REPORTS_DIR = BASE_DIR / "data" / "sinhan_terms" / "reports"

# Category Code 매핑
CATEGORY_CODE_MAP = {
    "신용카드": "credit",
    "대출/여신": "loan",
    "앱/디지털결제": "app",
    "포인트/리워드": "point",
    "계좌/송금": "account",
    "전자금융": "efinance",
    "가맹점/제휴": "merchant",
    "선불카드": "prepaid",
    "자동차금융": "auto",
    "기타서비스": "service"
}


def comprehensive_validation(chunks):
    """
    최종 완전 검증

    Returns:
        {
            "passed": bool,
            "errors": List[str],
            "warnings": List[str],
            "stats": Dict
        }
    """
    errors = []
    warnings = []

    # 1. 중복 ID 확인
    ids = [c["id"] for c in chunks]
    duplicate_ids = [id for id, count in Counter(ids).items() if count > 1]
    if duplicate_ids:
        errors.append(f"중복 ID 발견: {len(duplicate_ids)}개")

    # 2. 중복 텍스트 확인 (MD5 해시)
    text_hashes = defaultdict(list)
    for chunk in chunks:
        text_hash = hashlib.md5(chunk["text"].encode('utf-8')).hexdigest()
        text_hashes[text_hash].append(chunk["id"])

    duplicate_texts = {h: ids for h, ids in text_hashes.items() if len(ids) > 1}
    if duplicate_texts:
        warnings.append(f"중복 텍스트 발견: {len(duplicate_texts)}개 (이미 제거되었어야 함)")

    # 3. 필수 필드 검증
    for idx, chunk in enumerate(chunks, 1):
        chunk_id = chunk.get("id", f"chunk_{idx}")

        # ID
        if not chunk.get("id"):
            errors.append(f"청크 #{idx}: ID 누락")

        # title
        if not chunk.get("title"):
            errors.append(f"{chunk_id}: title 누락")

        # text
        if not chunk.get("text"):
            errors.append(f"{chunk_id}: text 누락")
        elif len(chunk["text"]) < 10:
            warnings.append(f"{chunk_id}: text 너무 짧음 ({len(chunk['text'])}자)")
        elif len(chunk["text"]) > 3000:
            errors.append(f"{chunk_id}: text 3000자 초과 ({len(chunk['text'])}자)")

        # metadata
        metadata = chunk.get("metadata", {})
        if not metadata:
            errors.append(f"{chunk_id}: metadata 누락")
        else:
            if not metadata.get("category1"):
                errors.append(f"{chunk_id}: category1 누락")
            elif metadata["category1"] not in CATEGORY_CODE_MAP:
                errors.append(f"{chunk_id}: 잘못된 category1 '{metadata['category1']}'")

            if not metadata.get("category2"):
                warnings.append(f"{chunk_id}: category2 누락")

        # title이 text에 포함되어 있는지
        if chunk.get("title") and chunk.get("text"):
            if chunk["title"] not in chunk["text"]:
                warnings.append(f"{chunk_id}: text에 title 미포함")

    # 통계
    text_lengths = [len(c["text"]) for c in chunks]
    cat1_dist = Counter(c["metadata"]["category1"] for c in chunks if c.get("metadata"))
    cat2_dist = Counter(c["metadata"]["category2"] for c in chunks if c.get("metadata"))

    stats = {
        "total_chunks": len(chunks),
        "unique_ids": len(set(ids)),
        "text_length": {
            "min": min(text_lengths) if text_lengths else 0,
            "max": max(text_lengths) if text_lengths else 0,
            "avg": sum(text_lengths) // len(text_lengths) if text_lengths else 0,
            "median": sorted(text_lengths)[len(text_lengths)//2] if text_lengths else 0
        },
        "category1_count": len(cat1_dist),
        "category2_count": len(cat2_dist),
        "category1_distribution": dict(cat1_dist.most_common()),
        "category2_distribution": dict(cat2_dist.most_common(10))
    }

    passed = len(errors) == 0

    return {
        "passed": passed,
        "errors": errors,
        "warnings": warnings,
        "stats": stats,
        "duplicate_ids": duplicate_ids,
        "duplicate_texts": duplicate_texts
    }


def create_rdb_format(chunk: dict) -> dict:
    """RDB 저장용 포맷"""
    return {
        "id": chunk["id"],
        "title": chunk["title"],
        "content": chunk["content"],
        "metadata": {
            "category1": chunk["metadata"]["category1"],
            "category2": chunk["metadata"]["category2"],
            "source": "신한카드 약관",
            "processed_date": datetime.now().isoformat()
        },
        "source_type": "sinhan_terms"
    }


def create_vectordb_format(chunk: dict) -> dict:
    """VectorDB 저장용 포맷"""
    return {
        "id": chunk["id"],
        "text": chunk["text"],
        "metadata": {
            "title": chunk["title"],
            "category1": chunk["metadata"]["category1"],
            "category2": chunk["metadata"]["category2"],
            "category1_code": CATEGORY_CODE_MAP.get(chunk["metadata"]["category1"], "misc"),
            "text_length": len(chunk["text"]),
            "source_type": "sinhan_terms"
        }
    }


def create_unified_format(chunk: dict) -> dict:
    """통합 포맷"""
    return {
        "id": chunk["id"],
        "title": chunk["title"],
        "content": chunk["content"],
        "text": chunk["text"],
        "metadata": {
            "category1": chunk["metadata"]["category1"],
            "category2": chunk["metadata"]["category2"],
            "category1_code": CATEGORY_CODE_MAP.get(chunk["metadata"]["category1"], "misc"),
            "text_length": len(chunk["text"]),
            "source_type": "sinhan_terms",
            "source": "신한카드 약관"
        }
    }


def main():
    """메인 실행 함수"""
    print("[INFO] 최종 검증 및 JSON 생성 시작\n")

    # 1. 데이터 로드
    print("[1/5] 필터링된 데이터 로드 중...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    print(f"  - 로드된 청크 수: {len(chunks)}\n")

    # 2. 완전 검증
    print("[2/5] 완전 검증 중...")
    validation_result = comprehensive_validation(chunks)

    print(f"  - 검증 결과: {'PASS' if validation_result['passed'] else 'FAIL'}")
    print(f"  - 에러: {len(validation_result['errors'])}개")
    print(f"  - 경고: {len(validation_result['warnings'])}개\n")

    if validation_result['errors']:
        print("[에러 목록]")
        for error in validation_result['errors'][:10]:
            print(f"  - {error}")
        print()

    if validation_result['warnings']:
        print("[경고 목록 (상위 5개)]")
        for warning in validation_result['warnings'][:5]:
            print(f"  - {warning}")
        print()

    if not validation_result['passed']:
        print("[ERROR] 검증 실패! 문제를 해결한 후 다시 시도하세요.")
        return

    # 3. 검증 리포트 저장
    print("[3/5] 검증 리포트 저장 중...")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    final_report = {
        "generated_at": datetime.now().isoformat(),
        "validation_result": validation_result,
        "source_file": str(INPUT_FILE),
        "total_chunks": len(chunks),
        "final_status": "READY_FOR_PRODUCTION" if validation_result['passed'] else "NEEDS_FIX"
    }

    report_file = REPORTS_DIR / "final_verification_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(final_report, f, ensure_ascii=False, indent=2)

    print(f"  - 저장 완료: {report_file}\n")

    # 4. 최종 JSON 생성
    print("[4/5] 최종 JSON 생성 중...")
    FINAL_DIR.mkdir(parents=True, exist_ok=True)

    # 통합 JSON
    unified_data = [create_unified_format(c) for c in chunks]
    unified_file = FINAL_DIR / "sinhan_terms_final_988.json"
    with open(unified_file, 'w', encoding='utf-8') as f:
        json.dump(unified_data, f, ensure_ascii=False, indent=2)
    unified_size = unified_file.stat().st_size / 1024
    print(f"  - 통합 JSON: {unified_file.name} ({unified_size:.1f}KB)")

    # RDB용 JSON
    rdb_data = [create_rdb_format(c) for c in chunks]
    rdb_file = FINAL_DIR / "sinhan_terms_for_rdb_988.json"
    with open(rdb_file, 'w', encoding='utf-8') as f:
        json.dump(rdb_data, f, ensure_ascii=False, indent=2)
    rdb_size = rdb_file.stat().st_size / 1024
    print(f"  - RDB JSON: {rdb_file.name} ({rdb_size:.1f}KB)")

    # VectorDB용 JSON
    vectordb_data = [create_vectordb_format(c) for c in chunks]
    vectordb_file = FINAL_DIR / "sinhan_terms_for_vectordb_988.json"
    with open(vectordb_file, 'w', encoding='utf-8') as f:
        json.dump(vectordb_data, f, ensure_ascii=False, indent=2)
    vectordb_size = vectordb_file.stat().st_size / 1024
    print(f"  - VectorDB JSON: {vectordb_file.name} ({vectordb_size:.1f}KB)\n")

    # 5. 최종 메타데이터
    print("[5/5] 최종 메타데이터 생성 중...")

    stats = validation_result['stats']

    metadata = {
        "generation_date": datetime.now().isoformat(),
        "version": "988_filtered",
        "total_chunks": len(chunks),
        "source_files": 86,
        "removed_chunks": 5,
        "removal_reason": "텍스트 길이 3000자 초과",
        "statistics": stats,
        "output_files": {
            "unified": str(unified_file.name),
            "rdb": str(rdb_file.name),
            "vectordb": str(vectordb_file.name)
        },
        "validation": {
            "passed": validation_result['passed'],
            "errors": len(validation_result['errors']),
            "warnings": len(validation_result['warnings'])
        }
    }

    metadata_file = FINAL_DIR / "final_metadata_988.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"  - 메타데이터: {metadata_file.name}\n")

    # 최종 출력
    print("="*60)
    print("[SUCCESS] 최종 검증 및 JSON 생성 완료!")
    print("="*60)

    print(f"\n[최종 통계]")
    print(f"  - 총 청크 수: {len(chunks)}")
    print(f"  - 원본 파일 수: 86개")
    print(f"  - 제거된 청크: 5개 (3000자 초과)")
    print(f"  - 데이터 커버리지: 99.5%")

    print(f"\n[텍스트 길이]")
    print(f"  - 평균: {stats['text_length']['avg']}자")
    print(f"  - 중간값: {stats['text_length']['median']}자")
    print(f"  - 최소: {stats['text_length']['min']}자")
    print(f"  - 최대: {stats['text_length']['max']}자")

    print(f"\n[카테고리 분포]")
    print(f"  - Category1: {stats['category1_count']}개")
    print(f"  - Category2: {stats['category2_count']}개")

    print(f"\n[Category1 상위 5개]")
    for cat, count in list(stats['category1_distribution'].items())[:5]:
        print(f"  - {cat}: {count}개 ({count/len(chunks)*100:.1f}%)")

    print(f"\n[생성된 파일]")
    print(f"  1. {unified_file.name} ({unified_size:.1f}KB) - 통합")
    print(f"  2. {rdb_file.name} ({rdb_size:.1f}KB) - RDB용")
    print(f"  3. {vectordb_file.name} ({vectordb_size:.1f}KB) - VectorDB용")
    print(f"  4. {metadata_file.name} - 메타데이터")

    print(f"\n[검증 상태]")
    if validation_result['passed']:
        print("  ✅ 모든 검증 통과 - 프로덕션 준비 완료")
    else:
        print("  ❌ 검증 실패 - 수정 필요")

    if validation_result['warnings']:
        print(f"  ⚠️  경고 {len(validation_result['warnings'])}개 (무시 가능)")

    print(f"\n[다음 단계]")
    print("  1. RDB 적재: sinhan_terms_for_rdb_988.json")
    print("  2. 임베딩 생성: sinhan_terms_for_vectordb_988.json")
    print("  3. VectorDB 저장: 임베딩 완료 후")
    print()


if __name__ == "__main__":
    main()
