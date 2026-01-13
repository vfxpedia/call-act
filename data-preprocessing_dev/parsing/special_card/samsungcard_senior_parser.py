import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pdfplumber

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_PDF = PROJECT_ROOT / "parsing" / "special_card" / "raw" / "라이프파트너삼성카드이용안내장.pdf"
OUT = PROJECT_ROOT / "data" / "special_card" / "samsungcard_senior.json"
KST = timezone(timedelta(hours=9))

KEY_TITLES = [
    "보험료 연 할인",
    "보험료 월 할인",
    "주유",
    "할인점",
    "의료",
    "영화",
    "연회비",
    "유의사항",
]

FOOTER_PATTERNS = [
    r"삼성카드 홈페이지\s*www\.samsungcard\.com\s*대표전화\s*1588-8700",
    r"삼성카드\s*대표전화\s*1588-8700",
    r"www\.samsungcard\.com",
]


def clean(s: str) -> str:
    return " ".join((s or "").replace("\xa0", " ").split()).strip()


def strip_footer(text: str) -> str:
    t = text or ""
    for pat in FOOTER_PATTERNS:
        t = re.sub(pat, " ", t)
    return clean(t)


def page_to_section(text: str) -> tuple[str | None, str]:

    lines = [clean(x) for x in (text or "").splitlines() if clean(x)]
    if not lines:
        return None, ""

    head = " ".join(lines[:6])

    title = None
    for kw in KEY_TITLES:
        if kw in head:
            title = kw
            break

    content = strip_footer(" ".join(lines))
    return title, content


def parse_pdf(pdf_path: Path) -> list[dict]:
    sections = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            # 요약(2페이지) 제외함
            if i == 2:
                continue

            t = page.extract_text() or ""
            title, content = page_to_section(t)
            if not title:
                continue
            sections.append({"title": title, "content": content})

    return sections


def main():
    sections = parse_pdf(RAW_PDF)
    data = {
        "source": "samsungcard",
        "name": "삼성카드 라이프파트너",
        "local_path": str(RAW_PDF),
        "crawled_at": datetime.now(KST).isoformat(timespec="seconds"),
        "sections": sections,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] saved -> {OUT} (sections: {len(sections)})")


if __name__ == "__main__":
    main()