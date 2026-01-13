"""
신한카드 약관 배치 처리 스크립트 (Stage 1-3 통합)
- 86개 TXT 파일 자동 처리
- 파싱 + 청크 생성 통합 실행
- 통계 및 메타데이터 생성
"""

import re
import json
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

# 경로 설정
BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = BASE_DIR / "data" / "sinhan_terms" / "raw_data"
OUTPUT_DIR = BASE_DIR / "data" / "sinhan_terms" / "intermediate"
REPORTS_DIR = BASE_DIR / "data" / "sinhan_terms" / "reports"

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

# Category2 정규화
CATEGORY2_NORMALIZATION = {
    "총칙": "총칙",
    "카드의 발급 및 관리 등": "카드발급/관리",
    "카드의 발급 및 관리": "카드발급/관리",
    "카드 거래 관련": "카드거래",
    "카드의 이용": "카드이용",
    "청구 및 지급": "대금결제",
    "손실 배상": "손해배상",
    "보칙": "기타약관"
}

# 정규식 패턴
PATTERN_CHAPTER = re.compile(r'^제(\d+)장\s*(.+)$')
PATTERN_ARTICLE = re.compile(r'^제(\d+)조\s*\((.+)\)$')
PATTERN_ARTICLE_NO_PAREN = re.compile(r'^제(\d+)조\s*(.+)$')
PATTERN_PARAGRAPH = re.compile(r'^([①②③④⑤⑥⑦⑧⑨⑩]+)\s*(.+)$')
PATTERN_APPENDIX = re.compile(r'^부\s*칙')


# ============ 텍스트 정규화 함수들 ============

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
    name = re.sub(r'[^\w가-힣]', '_', name)
    name = re.sub(r'_+', '_', name)[:30]
    return name


# ============ 분류 및 ID 생성 ============

def categorize_by_filename(filename: str) -> str:
    """파일명 기반 category1 자동 분류"""
    for category, keywords in CATEGORY1_MAPPING.items():
        if any(keyword in filename for keyword in keywords):
            return category
    return "기타서비스"


def normalize_chapter_name(chapter_name: str) -> str:
    """장 제목 정규화"""
    return CATEGORY2_NORMALIZATION.get(chapter_name, chapter_name)


def generate_id(category1: str, filename: str, index: int) -> str:
    """
    ID 생성: sinhan_terms_{category_code}_{file_code}_{index:03d}
    """
    category_code = CATEGORY_CODE_MAP.get(category1, "misc")
    file_code = sanitize_filename(filename)
    return f"sinhan_terms_{category_code}_{file_code}_{index:03d}"


# ============ 파싱 로직 ============

def parse_terms_file(filepath: Path) -> Dict:
    """
    약관 TXT 파일 파싱
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

        # 일반 텍스트
        if current_article:
            if current_article["content"]:
                current_article["content"] += " " + line
            else:
                current_article["content"] = line

    return result


# ============ 청크 생성 로직 ============

def create_chunks(parsed_data: Dict) -> List[Dict]:
    """
    파싱된 데이터를 조(條) 단위 청크로 변환
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

            # title 생성
            title = f"제{article_num}조({article_title})"

            # content 생성
            content_parts = []
            if article["content"]:
                content_parts.append(article["content"])
            if article["paragraphs"]:
                content_parts.extend(article["paragraphs"])

            content = "\n".join(content_parts)
            content = normalize_text(content)

            # text 생성
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


# ============ 배치 처리 메인 로직 ============

def process_all_files():
    """86개 TXT 파일 배치 처리"""

    # 출력 디렉토리 생성
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # TXT 파일 스캔
    txt_files = sorted(RAW_DATA_DIR.glob("*.txt"))

    if not txt_files:
        print("[ERROR] TXT 파일을 찾을 수 없습니다.")
        return

    print(f"[INFO] 발견된 약관 파일: {len(txt_files)}개\n")

    # 통계 변수
    all_chunks = []
    file_metadata = []
    category1_stats = defaultdict(int)
    category2_stats = defaultdict(int)
    errors = []

    # 각 파일 처리
    for idx, txt_file in enumerate(txt_files, 1):
        print(f"[{idx}/{len(txt_files)}] 처리중: {txt_file.name}")

        try:
            # 파싱
            parsed_data = parse_terms_file(txt_file)

            # 청크 생성
            chunks = create_chunks(parsed_data)

            # 통계 수집
            category1 = parsed_data["category1"]
            total_articles = sum(len(ch["articles"]) for ch in parsed_data["chapters"])

            category1_stats[category1] += len(chunks)
            for chunk in chunks:
                category2_stats[chunk["metadata"]["category2"]] += 1

            # 파일 메타데이터 저장
            file_meta = {
                "filename": txt_file.name,
                "category1": category1,
                "chapters": len(parsed_data["chapters"]),
                "articles": total_articles,
                "chunks": len(chunks),
                "avg_chunk_size": sum(len(c["text"]) for c in chunks) // len(chunks) if chunks else 0
            }
            file_metadata.append(file_meta)

            # 청크 통합
            all_chunks.extend(chunks)

            print(f"  - Category1: {category1}")
            print(f"  - 청크 수: {len(chunks)}")
            print(f"  - 평균 크기: {file_meta['avg_chunk_size']}자\n")

        except Exception as e:
            error_msg = f"{txt_file.name}: {str(e)}"
            errors.append(error_msg)
            print(f"  [ERROR] {error_msg}\n")

    # ============ 결과 저장 ============

    # 1. 전체 청크 JSON 저장
    chunks_output = OUTPUT_DIR / "chunks_all.json"
    with open(chunks_output, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    # 2. 파일 메타데이터 저장
    metadata_output = REPORTS_DIR / "file_metadata.json"
    with open(metadata_output, 'w', encoding='utf-8') as f:
        json.dump(file_metadata, f, ensure_ascii=False, indent=2)

    # 3. 처리 통계 리포트 생성
    total_text_length = sum(len(chunk['text']) for chunk in all_chunks)
    avg_text_length = total_text_length / len(all_chunks) if all_chunks else 0

    report = {
        "summary": {
            "total_files": len(txt_files),
            "processed_files": len(file_metadata),
            "failed_files": len(errors),
            "total_chunks": len(all_chunks),
            "avg_chunk_size": int(avg_text_length)
        },
        "category1_distribution": dict(category1_stats),
        "category2_distribution": dict(category2_stats),
        "errors": errors
    }

    report_output = REPORTS_DIR / "processing_report.json"
    with open(report_output, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # ============ 최종 출력 ============

    print("\n" + "="*60)
    print("[SUCCESS] 배치 처리 완료!")
    print("="*60)
    print(f"\n[통계]")
    print(f"  - 처리된 파일: {len(file_metadata)}/{len(txt_files)}개")
    print(f"  - 생성된 청크: {len(all_chunks)}개")
    print(f"  - 평균 청크 크기: {int(avg_text_length)}자")
    print(f"  - 총 텍스트 길이: {total_text_length:,}자")

    print(f"\n[Category1 분포]")
    for cat, count in sorted(category1_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {cat}: {count}개")

    print(f"\n[Category2 분포 (상위 10개)]")
    top_cat2 = sorted(category2_stats.items(), key=lambda x: x[1], reverse=True)[:10]
    for cat, count in top_cat2:
        print(f"  - {cat}: {count}개")

    if errors:
        print(f"\n[에러]")
        for error in errors:
            print(f"  - {error}")

    print(f"\n[저장된 파일]")
    print(f"  - 청크 데이터: {chunks_output}")
    print(f"  - 파일 메타데이터: {metadata_output}")
    print(f"  - 처리 리포트: {report_output}")
    print()


if __name__ == "__main__":
    process_all_files()
