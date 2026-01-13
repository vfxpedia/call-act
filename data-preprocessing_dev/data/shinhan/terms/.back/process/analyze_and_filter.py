"""
신한카드 약관 데이터 상세 분석 및 필터링 스크립트
- 전체 청크 품질 검증
- 문제 청크 식별 및 리포트
- 3000자 초과 청크 필터링
- 최종 정제 데이터 생성
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# 경로 설정
BASE_DIR = Path(__file__).resolve().parents[2]
INPUT_FILE = BASE_DIR / "data" / "sinhan_terms" / "intermediate" / "chunks_validated.json"
OUTPUT_DIR = BASE_DIR / "data" / "sinhan_terms" / "final"
REPORTS_DIR = BASE_DIR / "data" / "sinhan_terms" / "reports"

# 검증 기준
MAX_TEXT_LENGTH = 3000
MIN_TEXT_LENGTH = 10
MAX_TITLE_LENGTH = 100


def load_chunks(file_path: Path):
    """청크 로드"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_chunk_quality(chunks):
    """
    청크 품질 상세 분석

    Returns:
        {
            "total": int,
            "issues": List[Dict],
            "stats": Dict,
            "problematic_files": Dict
        }
    """
    issues = []
    length_distribution = defaultdict(int)
    file_stats = defaultdict(lambda: {"count": 0, "total_length": 0, "issues": 0})

    for idx, chunk in enumerate(chunks, 1):
        chunk_id = chunk.get("id", f"chunk_{idx}")
        title = chunk.get("title", "")
        text = chunk.get("text", "")
        metadata = chunk.get("metadata", {})

        text_length = len(text)

        # 파일별 통계
        # ID에서 파일명 추출: sinhan_terms_category_filename_001
        id_parts = chunk_id.split("_")
        if len(id_parts) >= 4:
            file_code = "_".join(id_parts[2:-1])
        else:
            file_code = "unknown"

        file_stats[file_code]["count"] += 1
        file_stats[file_code]["total_length"] += text_length

        # 길이 분포 (100자 단위)
        length_bucket = (text_length // 100) * 100
        length_distribution[length_bucket] += 1

        # 문제 감지
        issue_details = []

        # 1. 텍스트 길이 문제
        if text_length > MAX_TEXT_LENGTH:
            issue_details.append(f"텍스트 너무 김: {text_length}자")
            file_stats[file_code]["issues"] += 1

        if text_length < MIN_TEXT_LENGTH:
            issue_details.append(f"텍스트 너무 짧음: {text_length}자")
            file_stats[file_code]["issues"] += 1

        # 2. 제목 검증
        if not title:
            issue_details.append("제목 없음")
            file_stats[file_code]["issues"] += 1
        elif len(title) > MAX_TITLE_LENGTH:
            issue_details.append(f"제목 너무 김: {len(title)}자")
            file_stats[file_code]["issues"] += 1

        # 3. 제목이 "제N조" 패턴인지 확인
        if title and not re.match(r'^제\d+조', title):
            issue_details.append(f"비정상 제목 패턴: {title[:50]}")

        # 4. text에 title이 포함되어 있는지
        if title and title not in text:
            issue_details.append("text에 title 미포함")
            file_stats[file_code]["issues"] += 1

        # 5. 메타데이터 검증
        if not metadata.get("category1"):
            issue_details.append("category1 누락")
            file_stats[file_code]["issues"] += 1

        if not metadata.get("category2"):
            issue_details.append("category2 누락")
            file_stats[file_code]["issues"] += 1

        # 6. 중복 조항 번호 체크 (같은 파일 내에서 제1조가 여러 번 등장)
        if "제1조" in title and text_length > 5000:
            issue_details.append("전체 약관이 하나의 청크에 포함된 것으로 추정")
            file_stats[file_code]["issues"] += 1

        # 문제가 있는 청크 기록
        if issue_details:
            issues.append({
                "index": idx,
                "id": chunk_id,
                "file": file_code,
                "title": title,
                "text_length": text_length,
                "category1": metadata.get("category1", "unknown"),
                "category2": metadata.get("category2", "unknown"),
                "issues": issue_details
            })

    # 통계 계산
    text_lengths = [len(c["text"]) for c in chunks]
    stats = {
        "total_chunks": len(chunks),
        "avg_length": sum(text_lengths) // len(text_lengths) if text_lengths else 0,
        "min_length": min(text_lengths) if text_lengths else 0,
        "max_length": max(text_lengths) if text_lengths else 0,
        "over_3000": sum(1 for l in text_lengths if l > 3000),
        "under_10": sum(1 for l in text_lengths if l < 10),
        "length_distribution": dict(sorted(length_distribution.items()))
    }

    # 문제 파일 식별
    problematic_files = {
        file_code: data
        for file_code, data in file_stats.items()
        if data["issues"] > 0
    }

    return {
        "total": len(chunks),
        "issues": issues,
        "stats": stats,
        "file_stats": dict(file_stats),
        "problematic_files": problematic_files
    }


def filter_chunks(chunks, max_length=MAX_TEXT_LENGTH):
    """
    길이 기준으로 청크 필터링

    Returns:
        (filtered_chunks, removed_chunks)
    """
    filtered = []
    removed = []

    for chunk in chunks:
        text_length = len(chunk.get("text", ""))

        if text_length <= max_length and text_length >= MIN_TEXT_LENGTH:
            filtered.append(chunk)
        else:
            removed.append({
                "id": chunk.get("id"),
                "title": chunk.get("title"),
                "text_length": text_length,
                "reason": "too_long" if text_length > max_length else "too_short"
            })

    return filtered, removed


def generate_analysis_report(analysis, removed_chunks):
    """상세 분석 리포트 생성"""

    report = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_chunks": analysis["total"],
            "chunks_with_issues": len(analysis["issues"]),
            "problematic_files": len(analysis["problematic_files"]),
            "removed_chunks": len(removed_chunks)
        },
        "statistics": analysis["stats"],
        "problematic_files": analysis["problematic_files"],
        "issues_detail": analysis["issues"][:50],  # 최대 50개만
        "removed_chunks": removed_chunks,
        "recommendations": []
    }

    # 권장 사항 생성
    if analysis["stats"]["over_3000"] > 0:
        report["recommendations"].append(
            f"{analysis['stats']['over_3000']}개 청크가 3000자 초과. 원본 파일 재파싱 권장."
        )

    if analysis["stats"]["under_10"] > 0:
        report["recommendations"].append(
            f"{analysis['stats']['under_10']}개 청크가 10자 미만. 빈 청크 제거 권장."
        )

    if len(analysis["problematic_files"]) > 0:
        top_problematic = sorted(
            analysis["problematic_files"].items(),
            key=lambda x: x[1]["issues"],
            reverse=True
        )[:5]

        report["recommendations"].append(
            f"문제가 많은 파일 상위 5개: {', '.join([f[0] for f in top_problematic])}"
        )

    return report


def main():
    """메인 실행 함수"""
    print("[INFO] 신한카드 약관 데이터 상세 분석 및 필터링\n")

    # 1. 데이터 로드
    print("[1/6] 데이터 로드 중...")
    chunks = load_chunks(INPUT_FILE)
    print(f"  - 로드된 청크 수: {len(chunks)}\n")

    # 2. 품질 분석
    print("[2/6] 품질 분석 중...")
    analysis = analyze_chunk_quality(chunks)
    print(f"  - 분석 완료")
    print(f"  - 문제 발견된 청크: {len(analysis['issues'])}개")
    print(f"  - 문제 파일: {len(analysis['problematic_files'])}개\n")

    # 3. 문제 청크 출력
    if analysis["issues"]:
        print("[문제 청크 상세 (상위 10개)]")
        for issue in analysis["issues"][:10]:
            print(f"\n  [{issue['index']}] {issue['title']}")
            print(f"    - ID: {issue['id']}")
            print(f"    - 파일: {issue['file']}")
            print(f"    - 길이: {issue['text_length']}자")
            print(f"    - Category: {issue['category1']} > {issue['category2']}")
            print(f"    - 문제:")
            for prob in issue['issues']:
                print(f"      * {prob}")

    # 4. 필터링
    print(f"\n[3/6] 청크 필터링 중 (최대 {MAX_TEXT_LENGTH}자)...")
    filtered_chunks, removed_chunks = filter_chunks(chunks)
    print(f"  - 유효 청크: {len(filtered_chunks)}개")
    print(f"  - 제거된 청크: {len(removed_chunks)}개\n")

    # 제거된 청크 상세
    if removed_chunks:
        print("[제거된 청크 상세]")
        for removed in removed_chunks:
            print(f"  - {removed['title']}: {removed['text_length']}자 ({removed['reason']})")
        print()

    # 5. 분석 리포트 생성
    print("[4/6] 분석 리포트 생성 중...")
    report = generate_analysis_report(analysis, removed_chunks)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_file = REPORTS_DIR / "quality_analysis_report.json"

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"  - 저장 완료: {report_file}\n")

    # 6. 필터링된 데이터 저장
    print("[5/6] 필터링된 데이터 저장 중...")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # chunks_validated_filtered.json
    filtered_file = BASE_DIR / "data" / "sinhan_terms" / "intermediate" / "chunks_validated_filtered.json"
    with open(filtered_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_chunks, f, ensure_ascii=False, indent=2)

    print(f"  - 저장 완료: {filtered_file}")
    print(f"  - 파일 크기: {filtered_file.stat().st_size / 1024:.1f}KB\n")

    # 7. 최종 통계
    print("[6/6] 최종 통계")
    print("="*60)
    print(f"  원본 청크 수: {len(chunks)}")
    print(f"  필터링 후 청크 수: {len(filtered_chunks)}")
    print(f"  제거된 청크 수: {len(removed_chunks)}")
    print(f"  유효율: {len(filtered_chunks)/len(chunks)*100:.1f}%")

    print(f"\n[길이 통계]")
    filtered_lengths = [len(c["text"]) for c in filtered_chunks]
    print(f"  - 평균: {sum(filtered_lengths)//len(filtered_lengths)}자")
    print(f"  - 최소: {min(filtered_lengths)}자")
    print(f"  - 최대: {max(filtered_lengths)}자")

    print(f"\n[권장 사항]")
    for idx, rec in enumerate(report["recommendations"], 1):
        print(f"  {idx}. {rec}")

    print("\n" + "="*60)
    print("[SUCCESS] 분석 및 필터링 완료!\n")

    # 다음 단계 안내
    print("[다음 단계]")
    print("  1. quality_analysis_report.json 검토")
    print("  2. 문제 파일들의 원본 TXT 확인 (필요 시)")
    print("  3. finalize_sinhan_terms.py 실행 (필터링된 데이터로)")
    print()


if __name__ == "__main__":
    main()
