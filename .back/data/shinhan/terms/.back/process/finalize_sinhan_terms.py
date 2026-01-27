"""
신한카드 약관 최종 JSON 생성 스크립트 (Stage 5)
- 검증된 청크 로드
- 최종 통합 JSON 생성
- RDB용 JSON 생성 (메타데이터 중심)
- VectorDB용 JSON 생성 (임베딩 대상)
"""

import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# 경로 설정
BASE_DIR = Path(__file__).resolve().parents[2]
INPUT_DIR = BASE_DIR / "data" / "sinhan_terms" / "intermediate"
FINAL_DIR = BASE_DIR / "data" / "sinhan_terms" / "final"

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


def create_rdb_format(chunk: Dict) -> Dict:
    """
    RDB 저장용 포맷 생성

    service_guide_documents 테이블 스키마에 맞춤:
    - id: TEXT (PRIMARY KEY)
    - title: TEXT
    - content: TEXT
    - metadata: JSONB (category1, category2 포함)
    - source_type: TEXT ('sinhan_terms')
    - created_at: TIMESTAMP
    """
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


def create_vectordb_format(chunk: Dict) -> Dict:
    """
    VectorDB 저장용 포맷 생성

    임베딩 대상 텍스트 포함:
    - id: 고유 식별자
    - text: 임베딩할 텍스트 (title + content)
    - metadata: 검색 필터링용 메타데이터
    """
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


def create_unified_format(chunk: Dict) -> Dict:
    """
    통합 포맷 (모든 필드 포함)
    """
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


def generate_final_files():
    """
    최종 JSON 파일 생성 메인 함수
    """
    input_file = INPUT_DIR / "chunks_validated.json"

    if not input_file.exists():
        print(f"[ERROR] 파일을 찾을 수 없습니다: {input_file}")
        return

    print(f"[INFO] 최종 JSON 생성 시작\n")

    # 검증된 청크 로드
    with open(input_file, 'r', encoding='utf-8') as f:
        validated_chunks = json.load(f)

    print(f"[INFO] 로드된 청크 수: {len(validated_chunks)}\n")

    # 출력 디렉토리 생성
    FINAL_DIR.mkdir(parents=True, exist_ok=True)

    # ============ 1. 통합 JSON 생성 ============

    print("[1/3] 통합 JSON 생성 중...")
    unified_data = [create_unified_format(chunk) for chunk in validated_chunks]

    unified_file = FINAL_DIR / "sinhan_terms_final.json"
    with open(unified_file, 'w', encoding='utf-8') as f:
        json.dump(unified_data, f, ensure_ascii=False, indent=2)

    unified_size = unified_file.stat().st_size / 1024
    print(f"  - 저장 완료: {unified_file.name}")
    print(f"  - 파일 크기: {unified_size:.1f}KB\n")

    # ============ 2. RDB용 JSON 생성 ============

    print("[2/3] RDB용 JSON 생성 중...")
    rdb_data = [create_rdb_format(chunk) for chunk in validated_chunks]

    rdb_file = FINAL_DIR / "sinhan_terms_for_rdb.json"
    with open(rdb_file, 'w', encoding='utf-8') as f:
        json.dump(rdb_data, f, ensure_ascii=False, indent=2)

    rdb_size = rdb_file.stat().st_size / 1024
    print(f"  - 저장 완료: {rdb_file.name}")
    print(f"  - 파일 크기: {rdb_size:.1f}KB\n")

    # ============ 3. VectorDB용 JSON 생성 ============

    print("[3/3] VectorDB용 JSON 생성 중...")
    vectordb_data = [create_vectordb_format(chunk) for chunk in validated_chunks]

    vectordb_file = FINAL_DIR / "sinhan_terms_for_vectordb.json"
    with open(vectordb_file, 'w', encoding='utf-8') as f:
        json.dump(vectordb_data, f, ensure_ascii=False, indent=2)

    vectordb_size = vectordb_file.stat().st_size / 1024
    print(f"  - 저장 완료: {vectordb_file.name}")
    print(f"  - 파일 크기: {vectordb_size:.1f}KB\n")

    # ============ 통계 및 메타데이터 생성 ============

    from collections import Counter

    category1_dist = Counter(chunk["metadata"]["category1"] for chunk in validated_chunks)
    category2_dist = Counter(chunk["metadata"]["category2"] for chunk in validated_chunks)

    text_lengths = [len(chunk["text"]) for chunk in validated_chunks]

    final_metadata = {
        "generation_date": datetime.now().isoformat(),
        "total_chunks": len(validated_chunks),
        "source_files": 86,
        "category1_distribution": dict(category1_dist),
        "category2_distribution": dict(category2_dist),
        "text_length_stats": {
            "min": min(text_lengths),
            "max": max(text_lengths),
            "avg": sum(text_lengths) // len(text_lengths)
        },
        "output_files": {
            "unified": str(unified_file.name),
            "rdb": str(rdb_file.name),
            "vectordb": str(vectordb_file.name)
        }
    }

    metadata_file = FINAL_DIR / "final_metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(final_metadata, f, ensure_ascii=False, indent=2)

    # ============ 최종 출력 ============

    print("\n" + "="*60)
    print("[SUCCESS] 최종 JSON 생성 완료!")
    print("="*60)

    print(f"\n[생성된 파일]")
    print(f"  1. 통합 JSON: {unified_file.name} ({unified_size:.1f}KB)")
    print(f"  2. RDB용 JSON: {rdb_file.name} ({rdb_size:.1f}KB)")
    print(f"  3. VectorDB용 JSON: {vectordb_file.name} ({vectordb_size:.1f}KB)")
    print(f"  4. 메타데이터: {metadata_file.name}")

    print(f"\n[데이터 통계]")
    print(f"  - 총 청크 수: {len(validated_chunks)}")
    print(f"  - 원본 파일 수: 86개")
    print(f"  - Category1 분류: {len(category1_dist)}개")
    print(f"  - Category2 분류: {len(category2_dist)}개")

    print(f"\n[텍스트 통계]")
    print(f"  - 평균 길이: {final_metadata['text_length_stats']['avg']}자")
    print(f"  - 최소 길이: {final_metadata['text_length_stats']['min']}자")
    print(f"  - 최대 길이: {final_metadata['text_length_stats']['max']}자")

    print(f"\n[Category1 분포 (상위 5개)]")
    top_cat1 = sorted(category1_dist.items(), key=lambda x: x[1], reverse=True)[:5]
    for cat, count in top_cat1:
        print(f"  - {cat}: {count}개")

    print(f"\n[저장 위치]")
    print(f"  {FINAL_DIR.resolve()}")

    print(f"\n[다음 단계]")
    print(f"  1. RDB 적재: sinhan_terms_for_rdb.json")
    print(f"  2. 임베딩 생성: sinhan_terms_for_vectordb.json 사용")
    print(f"  3. VectorDB 저장: 임베딩 완료 후 pgvector에 저장")
    print()


if __name__ == "__main__":
    generate_final_files()
