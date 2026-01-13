"""
신한카드 약관 파싱 스크립트 (Stage 1-2)
- TXT 파일 읽기
- 장/조/항/호 구조 파싱
- 구조화된 JSON 생성
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 경로 설정
BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = BASE_DIR / "data" / "sinhan_terms" / "raw_data"
OUTPUT_DIR = BASE_DIR / "data" / "sinhan_terms" / "intermediate"

# Category1 매핑
CATEGORY1_MAPPING = {
    "신용카드": ["신용카드", "체크카드", "법인회원", "개인회원"],
    "대출/여신": ["대출", "여신", "마이너스", "스피드론", "대환"],
    "앱/디지털결제": ["앱카드", "페이", "간편결제", "CARPAY", "CarPay", "LG페이", "TV간편결제", "더치페이"],
    "포인트/리워드": ["포인트", "마일리지", "하이세이브", "기프트카드"],
    "계좌/송금": ["오픈뱅킹", "자동이체", "계좌통합", "서울페이", "송금"],
    "전자금융": ["전자금융", "전자지급", "위치기반", "본인확인", "인증서", "전자문서"],
    "가맹점/제휴": ["가맹점", "로컬카드", "제휴", "올댓"],
    "선불카드": ["선불", "폰빌", "직불", "콤보"],
    "자동차금융": ["렌터카", "리스"],
    "기타서비스": ["MyData", "스마트생활", "BILL&PAY"]
}

# 정규식 패턴
PATTERN_CHAPTER = re.compile(r'^제(\d+)장\s*(.+)$')  # 장
PATTERN_ARTICLE = re.compile(r'^제(\d+)조\s*\((.+)\)$')  # 조
PATTERN_ARTICLE_NO_PAREN = re.compile(r'^제(\d+)조\s*(.+)$')  # 조 (괄호 없음)
PATTERN_PARAGRAPH = re.compile(r'^([①②③④⑤⑥⑦⑧⑨⑩]+)\s*(.+)$')  # 항
PATTERN_CLAUSE = re.compile(r'^(\d+)\.\s*(.+)$')  # 호
PATTERN_APPENDIX = re.compile(r'^부\s*칙')  # 부칙


def categorize_by_filename(filename: str) -> str:
    """파일명 기반 category1 자동 분류"""
    for category, keywords in CATEGORY1_MAPPING.items():
        if any(keyword in filename for keyword in keywords):
            return category
    return "기타서비스"


def normalize_chapter_name(chapter_name: str) -> str:
    """장 제목 정규화"""
    normalization = {
        "총칙": "총칙",
        "카드의 발급 및 관리 등": "카드발급/관리",
        "카드의 발급 및 관리": "카드발급/관리",
        "카드 거래 관련": "카드거래",
        "카드의 이용": "카드이용",
        "청구 및 지급": "대금결제",
        "손실 배상": "손해배상",
        "보칙": "기타약관"
    }
    return normalization.get(chapter_name, chapter_name)


def parse_terms_file(filepath: Path) -> Dict:
    """
    약관 TXT 파일 파싱

    Returns:
        {
            "filename": "신용카드 개인회원 약관.txt",
            "category1": "신용카드",
            "structure_type": "chapter_article",  # or "section", "simple"
            "chapters": [
                {
                    "chapter_num": 1,
                    "chapter_name": "총칙",
                    "articles": [
                        {
                            "article_num": 1,
                            "article_title": "목적",
                            "content": "이 약관은...",
                            "paragraphs": ["① ...", "② ..."],
                            "clauses": ["1....", "2...."]
                        }
                    ]
                }
            ],
            "appendix": ["본 약관은 2023년 7월 3일부터 시행합니다."]
        }
    """
    filename = filepath.name
    category1 = categorize_by_filename(filename)

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    result = {
        "filename": filename,
        "category1": category1,
        "structure_type": "chapter_article",
        "chapters": [],
        "appendix": []
    }

    current_chapter = None
    current_article = None
    in_appendix = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 부칙 감지
        if PATTERN_APPENDIX.match(line):
            in_appendix = True
            continue

        if in_appendix:
            result["appendix"].append(line)
            continue

        # 장 감지
        chapter_match = PATTERN_CHAPTER.match(line)
        if chapter_match:
            chapter_num = int(chapter_match.group(1))
            chapter_name = chapter_match.group(2).strip()
            current_chapter = {
                "chapter_num": chapter_num,
                "chapter_name": chapter_name,
                "category2": normalize_chapter_name(chapter_name),
                "articles": []
            }
            result["chapters"].append(current_chapter)
            current_article = None
            continue

        # 조 감지
        article_match = PATTERN_ARTICLE.match(line) or PATTERN_ARTICLE_NO_PAREN.match(line)
        if article_match:
            article_num = int(article_match.group(1))
            article_title = article_match.group(2).strip()
            current_article = {
                "article_num": article_num,
                "article_title": article_title,
                "content": "",
                "paragraphs": []
            }
            if current_chapter:
                current_chapter["articles"].append(current_article)
            else:
                # 장 없는 조 (단순 구조)
                if not result["chapters"]:
                    result["chapters"].append({
                        "chapter_num": 0,
                        "chapter_name": "본문",
                        "category2": "본문",
                        "articles": []
                    })
                    current_chapter = result["chapters"][0]
                current_chapter["articles"].append(current_article)
            continue

        # 항 감지
        paragraph_match = PATTERN_PARAGRAPH.match(line)
        if paragraph_match and current_article:
            paragraph_marker = paragraph_match.group(1)
            paragraph_text = paragraph_match.group(2).strip()
            current_article["paragraphs"].append(f"{paragraph_marker} {paragraph_text}")
            continue

        # 호 감지 또는 일반 텍스트
        if current_article:
            if current_article["content"]:
                current_article["content"] += " " + line
            else:
                current_article["content"] = line

    return result


def main():
    """프로토타입: 1개 파일 테스트"""
    test_file = RAW_DATA_DIR / "신용카드 개인회원 약관.txt"

    if not test_file.exists():
        print(f"[ERROR] 파일을 찾을 수 없습니다: {test_file}")
        return

    print(f"[INFO] 파싱 시작: {test_file.name}")

    # 파싱 실행
    parsed_data = parse_terms_file(test_file)

    # 결과 출력 (요약)
    print(f"\n[SUCCESS] 파싱 완료!")
    print(f"  - 파일명: {parsed_data['filename']}")
    print(f"  - Category1: {parsed_data['category1']}")
    print(f"  - 구조 타입: {parsed_data['structure_type']}")
    print(f"  - 장(章) 수: {len(parsed_data['chapters'])}")

    total_articles = sum(len(ch['articles']) for ch in parsed_data['chapters'])
    print(f"  - 조(條) 수: {total_articles}")
    print(f"  - 부칙: {len(parsed_data['appendix'])}줄")

    # 샘플 출력
    if parsed_data['chapters']:
        first_chapter = parsed_data['chapters'][0]
        print(f"\n[SAMPLE] 첫 번째 장:")
        print(f"  제{first_chapter['chapter_num']}장 {first_chapter['chapter_name']}")
        print(f"  Category2: {first_chapter['category2']}")
        print(f"  조항 수: {len(first_chapter['articles'])}")

        if first_chapter['articles']:
            first_article = first_chapter['articles'][0]
            print(f"\n  제{first_article['article_num']}조({first_article['article_title']})")
            content_preview = first_article['content'][:100] + "..." if len(first_article['content']) > 100 else first_article['content']
            print(f"  내용: {content_preview}")
            print(f"  항 수: {len(first_article['paragraphs'])}")

    # JSON 저장
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / "parsed_structure_prototype.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(parsed_data, f, ensure_ascii=False, indent=2)

    print(f"\n[SAVED] 저장 완료: {output_file}")


if __name__ == "__main__":
    main()
