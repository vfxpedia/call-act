import json
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

URL = "https://www.mnd.go.kr/mbshome/mbs/mnd/subview.jsp?id=mnd_011302010000"
OUT = Path(__file__).resolve().parents[2] / "data" / "special_card" / "narasarang_faq.json"
CARD_NAME = "나라사랑카드"

html = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=20).text
soup = BeautifulSoup(html, "html.parser")
root = soup.select_one("#content") or soup.select_one(".content") or soup.body


def clean(s: str) -> str:
    return " ".join((s or "").replace("\xa0", " ").split()).strip()


def format_table(t):
    rows = []
    for tr in t.select("tr"):
        cells = [clean(x.get_text(" ", strip=True)) for x in tr.select("th, td")]
        cells = [x for x in cells if x]
        if cells:
            rows.append(" | ".join(cells))
    return " / ".join(rows)


def fix_common_ocr_typos(t: str) -> str:
    t = re.sub(r"\bmoble\b", "mobile", t, flags=re.IGNORECASE)
    t = t.replace("http://w ww", "http://www").replace("https://w ww", "https://www")
    t = re.sub(r"w\s+ww", "www", t)
    t = re.sub(r"https?://\s*w\s*ww", "http://www", t, flags=re.IGNORECASE)
    t = re.sub(r"w\s+w", "ww", t)
    t = t.replace("환 불", "환불").replace("에 서", "에서")

    # 끊어진 한글 낱자를 붙여서 단어 복원 (예: 국 방 부 -> 국방부)
    def join_korean_runs(m: re.Match) -> str:
        return re.sub(r"\s+", "", m.group(0))

    t = re.sub(r"\b((?:[가-힣]\s+){1,4}[가-힣])\b", join_korean_runs, t)
    return t


def normalize_urls(t: str) -> str:
    # http: / / 형태도 정규화
    def scheme_repl(m: re.Match) -> str:
        raw = re.sub(r"\s+", "", m.group(0)).lower()
        return "https://" if raw.startswith("https") else "http://"

    def squash_url(m: re.Match) -> str:
        return m.group(0).replace(" ", "")

    t = re.sub(r"(?i)h\s*t\s*t\s*p\s*s?\s*:\s*/\s*/\s*", scheme_repl, t)
    t = re.sub(r"(https?)\s*:\s*/\s*/\s*", r"\1://", t, flags=re.IGNORECASE)
    t = re.sub(r"https?\s*:\s*/\s*/?\s*[\w\.\-/]+(?:\s+[\w\.\-/]+)*", squash_url, t, flags=re.IGNORECASE)
    t = re.sub(r"\bwww\.[\w\.\-/]+(?:\s+[\w\.\-/]+)+", squash_url, t)
    t = re.sub(r"(https?):/([^/])", r"\1://\2", t)
    t = re.sub(r"(https?://\S)(?=[가-힣A-Za-z])", r"\1 ", t)
    return t


def remove_repeated_blocks(t: str) -> str:
    if "`" in t:
        t = t.split("`", 1)[0].strip()

    cut_markers = ["KB국민카드 콜센터", "IBK기업은행 콜센터", "신한카드 콜센터"]
    cut_at = None
    for marker in cut_markers:
        first = t.find(marker)
        if first == -1:
            continue
        second = t.find(marker, first + len(marker))
        if second != -1 and (second - first) < 120:
            cut_at = second if cut_at is None else min(cut_at, second)
    if cut_at is not None:
        t = t[:cut_at].strip()

    service_markers = ["현금인출서비스", "계좌이체서비스", "계좌잔액조회", "물품구매 시 체크카드결제서비스"]
    for marker in service_markers:
        first = t.find(marker)
        if first == -1:
            continue
        second = t.find(marker, first + len(marker))
        if second != -1 and (second - first) < 120:
            t = t[:second].strip()
            break

    return t


def dedup_marker_blocks(t: str) -> str:
    markers = [
        "KB국민카드 콜센터",
        "IBK기업은행 콜센터",
        "신한카드 콜센터",
    ]

    used = set()
    out_parts = []
    idx = 0
    n = len(t)

    while idx < n:
        found = [(t.find(m, idx), m) for m in markers if t.find(m, idx) != -1]
        if not found:
            tail = t[idx:].strip()
            if tail:
                out_parts.append(tail)
            break

        pos, marker = min(found, key=lambda x: x[0])

        if pos > idx:
            pre = t[idx:pos].strip()
            if pre:
                out_parts.append(pre)

        if marker in used:
            next_positions = [t.find(m, pos + 1) for m in markers if t.find(m, pos + 1) != -1]
            idx = min(next_positions) if next_positions else n
            continue

        used.add(marker)
        next_positions = [t.find(m, pos + 1) for m in markers if t.find(m, pos + 1) != -1]
        end = min(next_positions) if next_positions else n
        out_parts.append(t[pos:end].strip())
        idx = end

    return " ".join(out_parts)


def dedup_slash_blocks_if_no_url(t: str) -> str:
    if "http" in t or "www." in t:
        return t
    blocks = [b.strip() for b in re.split(r"\s*[\/\|]\s*", t) if b.strip()]
    seen = set()
    out = []
    for b in blocks:
        if b in seen:
            continue
        seen.add(b)
        out.append(b)
    return " / ".join(out)


def dedup_sentences(t: str) -> str:
    sents = re.split(r"(?:(?<=[.!?])|(?<=다\.)|(?<=요\.)|(?<=니다\.))\s+", t)
    seen = set()
    out = []
    for s in sents:
        s = s.strip()
        if not s:
            continue
        if s in seen:
            continue
        seen.add(s)
        out.append(s)
    return " ".join(out)


def dedup_segments(text: str) -> str:
    t = clean(text)
    t = fix_common_ocr_typos(t)
    t = normalize_urls(t)
    t = re.sub(r"[ /]+$", "", t).strip()
    t = remove_repeated_blocks(t)
    t = dedup_marker_blocks(t)
    t = dedup_slash_blocks_if_no_url(t)
    t = re.sub(r"\s*/\s*", "/", t)
    t = dedup_sentences(t)
    return t


def split_into_chunks(text: str, max_len: int = 400) -> list[str]:
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


data = []
cid = 0

for h4 in root.select("h4"):
    q = clean(h4.get_text(" ", strip=True))
    if not q or "만족" in q or "의견쓰기" in q:
        continue

    parts = []
    for el in h4.next_elements:
        name = getattr(el, "name", None)
        if name == "h4":
            break
        if name == "table":
            t = format_table(el)
            if t:
                parts.append(t)
        elif name in ("p", "li"):
            t = clean(el.get_text(" ", strip=True))
            if t:
                parts.append(t)

    if parts:
        cid += 1
        data.append(
            {
                "id": cid,
                "question": q,
                "answer": clean(" ".join(parts)),
            }
        )


def categorize_by_text(q: str, a: str) -> str:
    t = f"{q} {a}".lower()

    if any(kw in t for kw in ["발급", "신청", "대상", "재발급"]):
        return "발급/신청"
    if any(kw in t for kw in ["연회비", "수수료", "이자", "해외", "금리"]):
        return "수수료/금융정보"
    if any(kw in t for kw in ["할인", "적립", "포인트", "혜택", "보험", "보장", "바우처"]):
        return "혜택/할인"
    if any(kw in t for kw in ["실적", "제외", "이용금액", "사용", "이용", "확인사항", "시간 제한", "대상점", "가능", "불가", "기간", "업종", "한도"]):
        return "이용안내"
    if any(kw in t for kw in ["고객센터", "문의", "안내", "유의사항", "변경", "환불", "환급", "해지"]):
        return "고객지원/기타"
    return "기타"


def build_faq_items(items: list[dict]) -> list[dict]:
    normalized = []
    for idx, item in enumerate(items, start=1):
        q = clean(item.get("question", ""))
        a_raw = item.get("answer", "")
        a = dedup_segments(a_raw)
        if not q or not a:
            continue

        full_text = f"{q}\n{a}"
        category = categorize_by_text(q, a)
        normalized.append(
            {
                "id": f"narasarang_faq_{idx:03d}",
                "title": q,
                "content": a,
                "text": full_text,
                "metadata": {
                    "card_name": CARD_NAME,
                    "category": category,
                },
            }
        )
    return normalized


faq_items = build_faq_items(data)

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(faq_items, ensure_ascii=False, indent=2), encoding="utf-8")

print("saved:", len(faq_items), "faqs ->", OUT)
