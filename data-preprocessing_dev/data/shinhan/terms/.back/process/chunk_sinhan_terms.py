"""
신한카드 약관 청크 생성 스크립트 (Stage 3)
- 파싱된 구조를 조(條) 단위 청크로 변환
- 사용자 요청 형식에 맞게 JSON 생성
"""

import re
import json
from pathlib import Path
from typing import Dict, List

# 경로 설정
BASE_DIR = Path(__file__).resolve().parents[2]
INPUT_DIR = BASE_DIR / "data" / "sinhan_terms" / "intermediate"
OUTPUT_DIR = INPUT_DIR

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

# 텍스트 정규화 함수들
def strip_links(text: str) -> str:
    """URL 제거"""
    if not text:
        return ""
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'www\.\S+', '', text)
    return text


def squash_ws(text: str) -> str:
    """연속된 공백 제거"""
    return re.sub(r'\s+', ' ', text or "").strip()


def normalize_newlines(text: str) -> str:
    """줄바꿈 정규화"""
    if not text:
        return ""
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # 3회 이상 줄바꿈을 2회로 압축
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def normalize_text(text: str) -> str:
    """전체 텍스트 정규화 파이프라인"""
    text = strip_links(text)
    text = normalize_newlines(text)
    text = squash_ws(text)
    return text


def sanitize_filename(filename: str) -> str:
    """파일명을 ID 친화적으로 변환"""
    name = filename.replace('.txt', '').lower()
    # 한글은 유지하고 특수문자만 언더스코어로
    name = re.sub(r'[^\w가-힣]', '_', name)
    name = re.sub(r'_+', '_', name)[:30]  # 최대 30자
    return name


def generate_id(category1: str, filename: str, index: int) -> str:
    """
    ID 생성: sinhan_terms_{category_code}_{file_code}_{index:03d}

    예: sinhan_terms_credit_main_001
    """
    category_code = CATEGORY_CODE_MAP.get(category1, "misc")
    file_code = sanitize_filename(filename)
    return f"sinhan_terms_{category_code}_{file_code}_{index:03d}"


def create_chunks(parsed_data: Dict) -> List[Dict]:
    """
    파싱된 데이터를 조(條) 단위 청크로 변환

    Returns:
        [
            {
                "id": "sinhan_terms_credit_main_001",
                "title": "제1조(목적)",
                "content": "이 약관은...",
                "text": "제1조(목적)\n이 약관은...",
                "metadata": {
                    "category1": "신용카드",
                    "category2": "총칙"
                }
            },
            ...
        ]
    """
    chunks = []
    filename = parsed_data["filename"]
    category1 = parsed_data["category1"]

    index = 1

    for chapter in parsed_data["chapters"]:
        category2 = chapter["category2"]

        for article in chapter["articles"]:
            article_num = article["article_num"]
            article_title = article["article_title"]

            # title 생성: "제N조(주제명)"
            title = f"제{article_num}조({article_title})"

            # content 생성: 조항 본문 + 항들
            content_parts = []

            # content 필드 (조항 본문)
            if article["content"]:
                content_parts.append(article["content"])

            # paragraphs (항들)
            if article["paragraphs"]:
                content_parts.extend(article["paragraphs"])

            content = "\n".join(content_parts)

            # 텍스트 정규화
            content = normalize_text(content)

            # text 생성: title + "\n" + content
            text = f"{title}\n{content}"

            # 청크 생성
            chunk = {
                "id": generate_id(category1, filename, index),
                "title": title,
                "content": content,
                "text": text,
                "metadata": {
                    "category1": category1,
                    "category2": category2
                }
            }

            chunks.append(chunk)
            index += 1

    return chunks


def main():
    """프로토타입: 1개 파일 청크 생성 테스트"""
    input_file = INPUT_DIR / "parsed_structure_prototype.json"

    if not input_file.exists():
        print(f"[ERROR] 파일을 찾을 수 없습니다: {input_file}")
        return

    print(f"[INFO] 청크 생성 시작: {input_file.name}")

    # 파싱 데이터 로드
    with open(input_file, 'r', encoding='utf-8') as f:
        parsed_data = json.load(f)

    # 청크 생성
    chunks = create_chunks(parsed_data)

    print(f"\n[SUCCESS] 청크 생성 완료!")
    print(f"  - 생성된 청크 수: {len(chunks)}")
    print(f"  - 파일: {parsed_data['filename']}")
    print(f"  - Category1: {parsed_data['category1']}")

    # 통계 계산
    total_text_length = sum(len(chunk['text']) for chunk in chunks)
    avg_text_length = total_text_length / len(chunks) if chunks else 0
    print(f"  - 평균 청크 크기: {avg_text_length:.0f}자")

    # 샘플 출력
    if chunks:
        print(f"\n[SAMPLE] 첫 번째 청크:")
        first_chunk = chunks[0]
        print(f"  ID: {first_chunk['id']}")
        print(f"  Title: {first_chunk['title']}")
        content_preview = first_chunk['content'][:100] + "..." if len(first_chunk['content']) > 100 else first_chunk['content']
        print(f"  Content: {content_preview}")
        print(f"  Category1: {first_chunk['metadata']['category1']}")
        print(f"  Category2: {first_chunk['metadata']['category2']}")

    # JSON 저장
    output_file = OUTPUT_DIR / "chunks_raw_prototype.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"\n[SAVED] 저장 완료: {output_file}")
    print(f"  - 파일 크기: {output_file.stat().st_size / 1024:.1f}KB")


if __name__ == "__main__":
    main()
