import json
import os
import pdfplumber


root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
pdf_path = os.path.join(
    root_dir,
    "parsing",
    "special_card",
    "raw",
    "라이프파트너삼성카드이용안내장.pdf",
)
out_vec = os.path.join(root_dir, "data", "special_card", "samsungcard_senior_vectors.json")

CHUNK_SIZE = 900
SECTION_KEYWORDS = ["보험료 연 할인", "보험료 월 할인", "주유", "할인점", "의료", "영화", "연회비", "유의사항"]
PAGE_SECTION_HINTS = {3: "보험료 연 할인", 4: "보험료 월 할인", 5: "주유", 6: "할인점", 7: "의료", 8: "영화", 9: "연회비", 10: "유의사항"}
SKIP_PAGES = {1, 2}
TABLE_TAG = "[TABLE]"


def clean(s):
    if not s:
        return ""
    return " ".join(s.replace("\xa0", " ").split()).strip()


def chunk_text(text, max_len=CHUNK_SIZE):
    chunks, buf = [], []
    for line in (text or "").splitlines():
        line = line.strip()
        if not line:
            continue
        candidate = clean(" ".join(buf + [line]))
        if len(candidate) > max_len and buf:
            chunks.append(clean(" ".join(buf)))
            buf = [line]
        else:
            buf.append(line)
    if buf:
        chunks.append(clean(" ".join(buf)))
    return chunks


def detect_section(text):
    for kw in SECTION_KEYWORDS:
        if kw in text:
            return kw
    return None


def resolve_section(page_no, text, last_section):
    return PAGE_SECTION_HINTS.get(page_no) or detect_section(text) or last_section


def extract_chunks():
    chunks = []
    last_section = None
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            if i in SKIP_PAGES:  # 표지/요약은 스킵
                continue
            print(f"--- pdfplumber {i}페이지 처리 중... ---")
            text = page.extract_text() or ""
            tables = page.extract_tables() or []
            lines = []
            for tbl in tables:
                for row in tbl:
                    cells = [clean(c) for c in (row or []) if clean(c)]
                    if cells:
                        lines.append(" | ".join(cells))

            # 본문 청크
            text_chunks = chunk_text(text)
            for ci, ck in enumerate(text_chunks, start=1):
                sec = resolve_section(i, ck, last_section)
                if sec:
                    last_section = sec
                chunks.append(
                    {
                        "id": f"plumb_{i}_{ci}",
                        "page": i,
                        "category": "paragraph",
                        "chunk_index": ci,
                        "text": ck,
                        "has_table": False,
                        "section": sec,
                    }
                )

            # 테이블 청크를 따로 추가해 표가 잘리지 않도록
            table_text = "\n".join(lines)
            if table_text:
                sec = resolve_section(i, table_text, last_section)
                if sec:
                    last_section = sec
                chunks.append(
                    {
                        "id": f"plumb_{i}_table",
                        "page": i,
                        "category": "table",
                        "chunk_index": len(text_chunks) + 1,
                        "text": TABLE_TAG + "\n" + table_text,
                        "has_table": True,
                        "section": sec,
                    }
                )
    return chunks


def main():
    chunks = extract_chunks()

    os.makedirs(os.path.dirname(out_vec), exist_ok=True)
    vector_chunks = [
        {
            "id": c["id"],
            "text": c["text"],
            "metadata": {
                "title": c.get("section") or c.get("category"),
                "category": "삼성카드 라이프파트너",
            },
        }
        for c in chunks
    ]

    with open(out_vec, "w", encoding="utf-8") as f:
        json.dump(
            {
                "source": "samsungcard",
                "name": "삼성카드 라이프파트너",
                "url": None,
                "crawled_at": None,
                "vector_chunks": vector_chunks,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"작업 완료: {out_vec} (vectors: {len(vector_chunks)})")


if __name__ == "__main__":
    main()
