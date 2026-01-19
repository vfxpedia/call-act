"""
문서 길이 분석 스크립트

전처리된 JSON 파일들의 문서 길이를 분석하여:
1. 청킹 필요 여부 판단
2. OpenAI 임베딩 토큰 제한 확인 (text-embedding-3-small: 최대 8191 토큰)
3. 통계 정보 수집
"""

import json
from pathlib import Path
from typing import List, Dict, Any
import statistics

# BASE_DIR 설정
BASE_DIR = Path(__file__).resolve().parents[4]  # call-act
OUTPUT_DIR = BASE_DIR / "data-preprocessing_dev" / "data" / "teddycard"


def estimate_tokens(text: str) -> int:
    """
    한국어 텍스트의 대략적인 토큰 수 추정
    - 한국어: 평균 1자 = 1.3 토큰
    - 영어/숫자: 평균 1자 = 0.25 토큰
    """
    korean_chars = sum(1 for c in text if ord(c) >= 0xAC00 and ord(c) <= 0xD7A3)
    other_chars = len(text) - korean_chars
    return int(korean_chars * 1.3 + other_chars * 0.25)


def analyze_file(file_path: Path, field_name: str = "content") -> Dict[str, Any]:
    """JSON 파일의 문서 길이 분석"""
    if not file_path.exists():
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        data = [data]
    
    lengths = []
    token_counts = []
    long_docs = []  # 3000자 이상 문서
    
    for doc in data:
        # content 또는 text 필드 사용
        text = doc.get(field_name, "") or doc.get("text", "")
        length = len(text)
        tokens = estimate_tokens(text)
        
        lengths.append(length)
        token_counts.append(tokens)
        
        if length > 3000:
            long_docs.append({
                "id": doc.get("id", "unknown"),
                "title": doc.get("title", "")[:50],
                "length": length,
                "tokens": tokens
            })
    
    return {
        "file": file_path.name,
        "count": len(data),
        "length_stats": {
            "min": min(lengths) if lengths else 0,
            "max": max(lengths) if lengths else 0,
            "avg": int(statistics.mean(lengths)) if lengths else 0,
            "median": int(statistics.median(lengths)) if lengths else 0,
        },
        "token_stats": {
            "min": min(token_counts) if token_counts else 0,
            "max": max(token_counts) if token_counts else 0,
            "avg": int(statistics.mean(token_counts)) if token_counts else 0,
            "median": int(statistics.median(token_counts)) if token_counts else 0,
        },
        "long_docs_count": len(long_docs),
        "long_docs": long_docs[:10],  # 상위 10개만
        "needs_chunking": max(token_counts) > 8000 if token_counts else False,  # OpenAI 제한: 8191 토큰
    }


def main():
    """메인 함수"""
    print("=" * 80)
    print("문서 길이 분석 스크립트")
    print("=" * 80)
    
    files_to_analyze = [
        (OUTPUT_DIR / "teddycard_service_guides_samsung.json", "content"),
        (OUTPUT_DIR / "teddycard_service_guides_hyundai.json", "content"),
        (OUTPUT_DIR / "teddycard_service_guides_shinhan.json", "content"),
        (OUTPUT_DIR / "teddycard_service_guides_special.json", "content"),
        (OUTPUT_DIR / "teddycard_notices.json", "content"),
        (OUTPUT_DIR / "teddycard_card_products.json", "full_content"),
    ]
    
    results = []
    
    for file_path, field_name in files_to_analyze:
        print(f"\n[INFO] 분석 중: {file_path.name}")
        result = analyze_file(file_path, field_name)
        if result:
            results.append(result)
    
    # 결과 출력
    print("\n" + "=" * 80)
    print("분석 결과")
    print("=" * 80)
    
    for result in results:
        print(f"\n[FILE] {result['file']}")
        print(f"  문서 수: {result['count']}개")
        print(f"  길이 통계:")
        print(f"    - 최소: {result['length_stats']['min']:,}자")
        print(f"    - 최대: {result['length_stats']['max']:,}자")
        print(f"    - 평균: {result['length_stats']['avg']:,}자")
        print(f"    - 중간값: {result['length_stats']['median']:,}자")
        print(f"  토큰 통계 (추정):")
        print(f"    - 최소: {result['token_stats']['min']:,}토큰")
        print(f"    - 최대: {result['token_stats']['max']:,}토큰")
        print(f"    - 평균: {result['token_stats']['avg']:,}토큰")
        print(f"    - 중간값: {result['token_stats']['median']:,}토큰")
        print(f"  긴 문서 (3000자 이상): {result['long_docs_count']}개")
        
        if result['needs_chunking']:
            print(f"  [WARNING] 청킹 필요: 최대 토큰 수가 8000을 초과합니다!")
        else:
            print(f"  [OK] 청킹 불필요: 모든 문서가 OpenAI 제한 내입니다.")
        
        if result['long_docs']:
            print(f"  긴 문서 예시:")
            for doc in result['long_docs'][:5]:
                print(f"    - {doc['id']}: {doc['title']} ({doc['length']:,}자, {doc['tokens']:,}토큰)")
    
    # 전체 요약
    print("\n" + "=" * 80)
    print("전체 요약")
    print("=" * 80)
    
    total_docs = sum(r['count'] for r in results)
    needs_chunking_files = [r['file'] for r in results if r['needs_chunking']]
    
    print(f"총 문서 수: {total_docs:,}개")
    print(f"청킹이 필요한 파일: {len(needs_chunking_files)}개")
    if needs_chunking_files:
        print(f"  - {', '.join(needs_chunking_files)}")
    else:
        print("  [OK] 모든 파일이 청킹 없이 처리 가능합니다.")
    
    print("\n" + "=" * 80)
    print("결론")
    print("=" * 80)
    
    if needs_chunking_files:
        print("[WARNING] 일부 문서는 청킹이 필요할 수 있습니다.")
        print("   하지만 대부분의 문서는 적절한 크기이므로,")
        print("   현재는 청킹 없이 진행하고, 필요 시 개별 문서만 청킹하는 것을 권장합니다.")
    else:
        print("[OK] 모든 문서가 OpenAI 임베딩 제한(8191 토큰) 내에 있습니다.")
        print("   청킹 없이 바로 임베딩 생성 및 DB 적재가 가능합니다.")
    
    print("=" * 80)


if __name__ == "__main__":
    main()
