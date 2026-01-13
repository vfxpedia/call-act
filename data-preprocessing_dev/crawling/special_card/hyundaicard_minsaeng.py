import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

URL = "https://www.hyundaicard.com/cpb/gs/CPBGS2011_01.hc"
OUT_FAQ = Path(__file__).resolve().parents[2] / "data" / "special_card" / "minsaeng_faq.json"
OUT_TERMS = Path(__file__).resolve().parents[2] / "data" / "special_card" / "minsaeng_terms.json"
CARD_NAME = "민생회복 소비쿠폰"
KST = timezone(timedelta(hours=9))


def clean(text: str) -> str:
    return " ".join((text or "").replace("\xa0", " ").split()).strip()


def strip_links(text: str) -> str:
    if not text:
        return ""
    t = re.sub(r"https?://\S+", "", text)
    t = re.sub(r"\bwww\.\S+", "", t)
    return " ".join(t.split())


def uniq_keep_order(items):
    out, seen = [], set()
    for x in items:
        if not x or x in seen:
            continue
        seen.add(x)
        out.append(x)
    return out


def build_driver() -> webdriver.Chrome:
    opt = Options()
    if os.getenv("HEADLESS", "1") != "0":
        opt.add_argument("--headless=new")
    opt.add_argument("--disable-gpu")
    opt.add_argument("--no-sandbox")
    opt.add_argument("--lang=ko-KR")
    driver_path = ChromeDriverManager().install()
    driver = webdriver.Chrome(service=Service(driver_path), options=opt)
    driver.implicitly_wait(5)
    return driver


def fetch_html(url: str) -> str:
    driver = build_driver()
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tabContents_1")))
        return driver.page_source
    finally:
        driver.quit()


def extract_sections(container: BeautifulSoup, labels: list[str]) -> dict:
    lines = [clean(x) for x in container.get_text("\n", strip=True).split("\n") if clean(x)]
    stop = set(labels) | {"확인", "닫기", "신청하기", "자세히 보기"}
    result = {}

    for i, line in enumerate(lines):
        if line not in labels or line in result:
            continue

        parts = []
        for nxt in lines[i + 1 :]:
            if nxt in stop or nxt in labels:
                break
            if "조회하기" in nxt:
                continue
            if len(nxt) <= 1:
                continue
            parts.append(nxt)

        if parts:
            result[line] = " ".join(uniq_keep_order(parts))

    return result


def parse_rounds(soup: BeautifulSoup) -> dict:
    labels = ["신청 대상", "지급 금액", "신청 일시", "대상 카드"]
    rounds = {}
    for name, tab_id in [("1차", "tabContents_1"), ("2차", "tabContents_2")]:
        section = soup.select_one(f"div#{tab_id}")
        if not section:
            continue
        fields = extract_sections(section, labels)
        if fields:
            rounds[name] = fields
    return rounds


def parse_usage(soup: BeautifulSoup) -> dict:
    labels = ["사용 기간", "사용처", "사용 가능 업종", "사용 불가 업종"]
    return extract_sections(soup, labels)


def parse_faq(soup: BeautifulSoup) -> list[dict]:
    items = []
    for idx, li in enumerate(soup.select("ul#resultList li.accodWrap"), start=1):
        q_el = li.select_one(".box_tit")
        q = clean(q_el.get_text(" ", strip=True)) if q_el else ""
        q = re.sub(r"^(질문|Q[.:]?)\s*", "", q)

        a_parts = []
        slide = li.select_one(".accodSlide")
        if slide:
            for blk in slide.select("p, li"):
                t = clean(blk.get_text(" ", strip=True))
                if t and "조회하기" not in t:
                    a_parts.append(t)

        a = " ".join(uniq_keep_order(a_parts))
        if q and a:
            items.append({"id": idx, "question": q, "answer": a})
    return items


def split_into_chunks(text: str, max_len: int = 350) -> list[str]:
    t = clean(text)
    if len(t) <= max_len:
        return [t]

    sentences = re.split(r"(?:(?<=[.!?])|(?<=다\.)|(?<=요\.)|(?<=니다\.))\s+", t)
    pieces: list[str] = []
    cur: list[str] = []
    cur_len = 0

    for sent in sentences:
        s = sent.strip()
        if not s:
            continue
        if len(s) > max_len and not pieces and not cur:
            return [s]
        add = len(s) + (1 if cur else 0)
        if cur and cur_len + add > max_len:
            pieces.append(" ".join(cur))
            cur = [s]
            cur_len = len(s)
        else:
            cur.append(s)
            cur_len += add

    if cur:
        pieces.append(" ".join(cur))
    return pieces


def segment_by_markers(text: str, markers: list[str]) -> list[str]:
    t = clean(text)
    positions = []
    for m in markers:
        idx = t.find(m)
        if idx != -1:
            positions.append((idx, m))
    positions = sorted(set(positions))
    if not positions:
        return [t]

    pieces = []
    last = 0
    for idx, _ in positions:
        if idx > last:
            pieces.append(t[last:idx].strip())
        last = idx
    if last < len(t):
        pieces.append(t[last:].strip())
    return [p for p in pieces if p]


def split_round_value(label: str, val: str) -> list[str]:

    t = clean(val)
    if label != "신청 일시":
        return [t]

    parts: list[str] = []
    work = t

    # 1) 요일제 표 분리
    table_pat = re.compile(r"출생\s*연도\s*끝자리\s*별\s*요일제\s*안내\s*표")
    table_match = table_pat.search(work)
    table_text = None
    if table_match:
        table_text = work[table_match.start() :].strip()
        work = work[: table_match.start()].strip()

    time_pat = re.compile(r"매일[^.]*?신청\s*불가")
    time_match = time_pat.search(work)
    if time_match:
        time_block = work[time_match.start() : time_match.end()].strip()
        pre = work[: time_match.start()].strip()
        post = work[time_match.end() :].strip()
        work = " ".join([p for p in [pre, post] if p]).strip()
        if time_block:
            parts.append(time_block)

    week_idx = work.find("신청 첫 주")
    if week_idx != -1:
        pre = work[:week_idx].strip()
        week = work[week_idx:].strip()
        if pre:
            parts.insert(0, pre)
        if week:
            parts.append(week)
    else:
        if work:
            parts.insert(0, work)

    if table_text:
        parts.append(table_text)

    return [p for p in parts if p]


def categorize_by_text(q: str, a: str) -> str:
    t = f"{q} {a}".lower()

    if any(kw in t for kw in ["발급", "신청", "대상", "재발급", "확인"]):
        return "발급/신청"
    if any(kw in t for kw in ["연회비", "수수료", "이자", "해외", "금리"]):
        return "수수료/금융정보"
    if any(kw in t for kw in ["할인", "적립", "포인트", "혜택", "보험", "보장", "바우처", "지급"]):
        return "혜택/할인"
    if any(kw in t for kw in ["실적", "제외", "이용금액", "사용", "이용", "확인사항", "시간 제한", "대상점", "가능", "불가", "기간", "업종", "한도"]):
        return "이용안내"
    if any(kw in t for kw in ["고객센터", "문의", "안내", "유의사항", "변경", "환불", "환급", "해지", "지원센터"]):
        return "고객지원/기타"
    return "기타"


def build_faq_items(data: dict) -> list[dict]:
    items = []
    n = 0
    faq_markers = ["기한 :", "접수처 :", "소득 상위 10% 확인", "세대 내 세대주 변경"]

    for item in data.get("faq", []):
        q = strip_links(clean(item.get("question", "")))
        a_raw = item.get("answer", "")
        a = strip_links(clean(re.sub(r"\[[^\]]+\]", "", a_raw)))
        if not q or not a:
            continue

        segments = segment_by_markers(a, faq_markers)
        for seg in segments:
            for piece in split_into_chunks(seg, max_len=600):
                piece = strip_links(piece)
                n += 1
                items.append(
                    {
                        "id": f"minsaeng_faq_{n:03d}",
                        "title": q,
                        "content": piece,
                        "text": f"{q}\n{piece}",
                        "metadata": {
                            "card_name": CARD_NAME,
                            "category": categorize_by_text(q, piece),
                        },
                    }
                )
    return items


def categorize_term(label: str) -> str:
    if label in ["신청 대상", "신청 일시", "대상 카드"]:
        return "발급/신청"
    if label in ["지급 금액"]:
        return "혜택/할인"
    return "이용안내"


def build_terms_items(data: dict) -> list[dict]:
    items = []
    n = 0

    for round_name, fields in (data.get("rounds") or {}).items():
        for label, val in fields.items():
            text = strip_links(clean(val))
            if not text:
                continue
            n += 1
            title = f"{round_name} {label}"
            items.append(
                {
                    "id": f"minsaeng_term_{n:03d}",
                    "title": title,
                    "content": text,
                    "text": f"{title}\n{text}",
                    "metadata": {
                        "card_name": CARD_NAME,
                        "category": categorize_term(label),
                    },
                }
            )

    for label, val in (data.get("usage") or {}).items():
        text = strip_links(clean(val))
        if not text:
            continue
        n += 1
        title = label
        items.append(
            {
                "id": f"minsaeng_term_{n:03d}",
                "title": title,
                "content": text,
                "text": f"{title}\n{text}",
                "metadata": {
                    "card_name": CARD_NAME,
                    "category": "이용안내",
                },
            }
        )

    return items


def main():
    html = fetch_html(URL)
    soup = BeautifulSoup(html, "html.parser")

    data = {
        "source": "hyundaicard",
        "name": "민생회복 소비쿠폰",
        "url": URL,
        "crawled_at": datetime.now(KST).isoformat(timespec="seconds"),
        "rounds": parse_rounds(soup),
        "usage": parse_usage(soup),
        "faq": parse_faq(soup),
    }
    faq_items = build_faq_items(data)
    terms_items = build_terms_items(data)

    OUT_FAQ.parent.mkdir(parents=True, exist_ok=True)
    OUT_FAQ.write_text(json.dumps(faq_items, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_TERMS.write_text(json.dumps(terms_items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] saved -> {OUT_FAQ} (faq chunks: {len(faq_items)})")
    print(f"[OK] saved -> {OUT_TERMS} (terms: {len(terms_items)})")


if __name__ == "__main__":
    main()
