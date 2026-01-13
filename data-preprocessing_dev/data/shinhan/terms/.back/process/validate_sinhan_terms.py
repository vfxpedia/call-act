"""
신한카드 약관 데이터 검증 스크립트 (Stage 4)
- 필수 필드 존재 확인
- ID 형식 검증
- 텍스트 길이 검증
- 중복 제거
- 카테고리 유효성 검증
- 상세 검증 리포트 생성
"""

import re
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

# 경로 설정
BASE_DIR = Path(__file__).resolve().parents[2]
INPUT_DIR = BASE_DIR / "data" / "sinhan_terms" / "intermediate"
OUTPUT_DIR = INPUT_DIR
REPORTS_DIR = BASE_DIR / "data" / "sinhan_terms" / "reports"

# 검증 규칙
REQUIRED_FIELDS = ["id", "title", "content", "text", "metadata"]
METADATA_REQUIRED_FIELDS = ["category1", "category2"]
ID_PATTERN = re.compile(r'^sinhan_terms_\w+_[\w가-힣_]+_\d{3}$')

MIN_TEXT_LENGTH = 10
MAX_TEXT_LENGTH = 3000

VALID_CATEGORY1 = [
    "신용카드", "대출/여신", "앱/디지털결제", "포인트/리워드",
    "계좌/송금", "전자금융", "가맹점/제휴", "선불카드",
    "자동차금융", "기타서비스"
]


def validate_chunk(chunk: Dict, index: int) -> List[str]:
    """
    단일 청크 검증

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # 1. 필수 필드 존재 확인
    for field in REQUIRED_FIELDS:
        if field not in chunk:
            errors.append(f"청크 #{index}: 필수 필드 누락 - '{field}'")
            return errors  # 필수 필드 없으면 추가 검증 불가

    # 2. Metadata 필수 필드 확인
    metadata = chunk.get("metadata", {})
    for field in METADATA_REQUIRED_FIELDS:
        if field not in metadata:
            errors.append(f"청크 #{index}: metadata 필드 누락 - '{field}'")

    # 3. ID 형식 검증
    chunk_id = chunk.get("id", "")
    if not ID_PATTERN.match(chunk_id):
        errors.append(f"청크 #{index}: 잘못된 ID 형식 - '{chunk_id}'")

    # 4. 텍스트 길이 검증
    text = chunk.get("text", "")
    text_length = len(text)

    if text_length < MIN_TEXT_LENGTH:
        errors.append(f"청크 #{index} ({chunk_id}): 텍스트가 너무 짧음 - {text_length}자 (최소 {MIN_TEXT_LENGTH}자)")

    if text_length > MAX_TEXT_LENGTH:
        errors.append(f"청크 #{index} ({chunk_id}): 텍스트가 너무 김 - {text_length}자 (최대 {MAX_TEXT_LENGTH}자)")

    # 5. Category1 유효성 검증
    category1 = metadata.get("category1", "")
    if category1 and category1 not in VALID_CATEGORY1:
        errors.append(f"청크 #{index} ({chunk_id}): 잘못된 category1 - '{category1}'")

    # 6. 빈 필드 검증
    if not chunk.get("title", "").strip():
        errors.append(f"청크 #{index} ({chunk_id}): title이 비어있음")

    if not chunk.get("content", "").strip():
        errors.append(f"청크 #{index} ({chunk_id}): content가 비어있음")

    # 7. text 필드가 title을 포함하는지 확인
    title = chunk.get("title", "")
    if title and title not in text:
        errors.append(f"청크 #{index} ({chunk_id}): text에 title이 포함되지 않음")

    return errors


def detect_duplicates(chunks: List[Dict]) -> Dict[str, List[str]]:
    """
    중복 청크 탐지 (text 해시 기반)

    Returns:
        Dict[hash, List[chunk_ids]]
    """
    hash_to_ids = defaultdict(list)

    for chunk in chunks:
        text = chunk.get("text", "")
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        chunk_id = chunk.get("id", "unknown")
        hash_to_ids[text_hash].append(chunk_id)

    # 중복된 항목만 반환
    duplicates = {h: ids for h, ids in hash_to_ids.items() if len(ids) > 1}
    return duplicates


def check_encoding(chunks: List[Dict]) -> List[str]:
    """
    인코딩 이슈 확인
    """
    errors = []

    for idx, chunk in enumerate(chunks, 1):
        chunk_id = chunk.get("id", f"chunk_{idx}")

        for field in ["title", "content", "text"]:
            value = chunk.get(field, "")
            if not value:
                continue

            # 깨진 문자 패턴 확인
            if '�' in value:
                errors.append(f"청크 {chunk_id}: '{field}' 필드에 깨진 문자 발견")

            # 비정상적인 제어 문자 확인
            if re.search(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', value):
                errors.append(f"청크 {chunk_id}: '{field}' 필드에 제어 문자 발견")

    return errors


def generate_statistics(chunks: List[Dict]) -> Dict:
    """
    통계 생성
    """
    category1_count = defaultdict(int)
    category2_count = defaultdict(int)
    text_lengths = []

    for chunk in chunks:
        metadata = chunk.get("metadata", {})
        category1 = metadata.get("category1", "unknown")
        category2 = metadata.get("category2", "unknown")

        category1_count[category1] += 1
        category2_count[category2] += 1

        text_length = len(chunk.get("text", ""))
        text_lengths.append(text_length)

    stats = {
        "total_chunks": len(chunks),
        "category1_distribution": dict(category1_count),
        "category2_distribution": dict(category2_count),
        "text_length_stats": {
            "min": min(text_lengths) if text_lengths else 0,
            "max": max(text_lengths) if text_lengths else 0,
            "avg": sum(text_lengths) // len(text_lengths) if text_lengths else 0
        }
    }

    return stats


def validate_all_chunks():
    """
    전체 청크 검증 메인 함수
    """
    input_file = INPUT_DIR / "chunks_all.json"

    if not input_file.exists():
        print(f"[ERROR] 파일을 찾을 수 없습니다: {input_file}")
        return

    print(f"[INFO] 검증 시작: {input_file.name}\n")

    # JSON 로드
    with open(input_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)

    print(f"[INFO] 로드된 청크 수: {len(chunks)}\n")

    # ============ 검증 실행 ============

    all_errors = []

    # 1. 개별 청크 검증
    print("[1/4] 개별 청크 검증 중...")
    for idx, chunk in enumerate(chunks, 1):
        errors = validate_chunk(chunk, idx)
        all_errors.extend(errors)

    print(f"  - 발견된 오류: {len(all_errors)}개\n")

    # 2. 중복 탐지
    print("[2/4] 중복 청크 탐지 중...")
    duplicates = detect_duplicates(chunks)
    duplicate_count = sum(len(ids) - 1 for ids in duplicates.values())

    print(f"  - 중복 그룹: {len(duplicates)}개")
    print(f"  - 중복 청크: {duplicate_count}개\n")

    # 3. 인코딩 검증
    print("[3/4] 인코딩 검증 중...")
    encoding_errors = check_encoding(chunks)
    all_errors.extend(encoding_errors)

    print(f"  - 인코딩 오류: {len(encoding_errors)}개\n")

    # 4. 통계 생성
    print("[4/4] 통계 생성 중...")
    stats = generate_statistics(chunks)
    print(f"  - 통계 생성 완료\n")

    # ============ 검증 리포트 생성 ============

    validation_report = {
        "validation_summary": {
            "total_chunks": len(chunks),
            "valid_chunks": len(chunks) - len(all_errors),
            "total_errors": len(all_errors),
            "duplicate_groups": len(duplicates),
            "duplicate_chunks": duplicate_count
        },
        "errors": all_errors[:100],  # 최대 100개만 저장
        "duplicate_details": {
            hash_val: ids for hash_val, ids in list(duplicates.items())[:20]  # 최대 20개만 저장
        },
        "statistics": stats,
        "validation_passed": len(all_errors) == 0 and duplicate_count == 0
    }

    # 리포트 저장
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_file = REPORTS_DIR / "validation_report.json"

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(validation_report, f, ensure_ascii=False, indent=2)

    # ============ 중복 제거 및 검증된 청크 저장 ============

    # 중복 제거
    seen_hashes: Set[str] = set()
    validated_chunks = []
    removed_count = 0

    for chunk in chunks:
        text = chunk.get("text", "")
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()

        if text_hash not in seen_hashes:
            seen_hashes.add(text_hash)
            validated_chunks.append(chunk)
        else:
            removed_count += 1

    # 검증된 청크 저장
    validated_file = OUTPUT_DIR / "chunks_validated.json"

    with open(validated_file, 'w', encoding='utf-8') as f:
        json.dump(validated_chunks, f, ensure_ascii=False, indent=2)

    # ============ 최종 출력 ============

    print("\n" + "="*60)
    print("[SUCCESS] 검증 완료!")
    print("="*60)

    print(f"\n[검증 결과]")
    print(f"  - 총 청크 수: {len(chunks)}")
    print(f"  - 유효 청크 수: {len(validated_chunks)}")
    print(f"  - 중복 제거: {removed_count}개")
    print(f"  - 발견된 오류: {len(all_errors)}개")

    if all_errors:
        print(f"\n[오류 샘플 (최대 10개)]")
        for error in all_errors[:10]:
            print(f"  - {error}")

    if duplicates:
        print(f"\n[중복 샘플 (최대 5개)]")
        for idx, (hash_val, ids) in enumerate(list(duplicates.items())[:5], 1):
            print(f"  {idx}. 중복 {len(ids)}개: {', '.join(ids[:3])}")

    print(f"\n[통계]")
    print(f"  - 평균 텍스트 길이: {stats['text_length_stats']['avg']}자")
    print(f"  - 최소 텍스트 길이: {stats['text_length_stats']['min']}자")
    print(f"  - 최대 텍스트 길이: {stats['text_length_stats']['max']}자")

    print(f"\n[저장된 파일]")
    print(f"  - 검증 리포트: {report_file}")
    print(f"  - 검증된 청크: {validated_file}")
    print(f"  - 파일 크기: {validated_file.stat().st_size / 1024:.1f}KB")

    if validation_report["validation_passed"]:
        print(f"\n[PASS] 모든 검증 통과!")
    else:
        print(f"\n[WARNING] 일부 오류가 발견되었습니다. 리포트를 확인하세요.")

    print()


if __name__ == "__main__":
    validate_all_chunks()
