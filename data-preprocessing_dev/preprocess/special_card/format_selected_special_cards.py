import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[2] / "data" / "special_card"

PREFIX_MAP = {
    "서울시다둥이행복카드": "dadungi",
    "네이버페이카드": "naverpay",
    "삼성카드 라이프파트너": "lifepartner",
    "라이프파트너": "lifepartner",
}

KOR_ALNUM = r"[0-9A-Za-z가-힣]"


def strip_links(text: str) -> str:
    if not text:
        return ""
    t = re.sub(r"https?://\S+", "", text)
    t = re.sub(r"\bwww\.\S+", "", t)
    return t


def squash_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def normalize_newlines(text: str) -> str:
    if not text:
        return ""
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    t = re.sub(fr"({KOR_ALNUM})\n({KOR_ALNUM})", r"\1\2", t)
    t = re.sub(r"[ \t]*\n[ \t]*", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    parts = re.split(r"\n{2,}", t.strip())
    parts = [squash_ws(p) for p in parts if squash_ws(p)]
    return "\n\n".join(parts)


def first_sentence_split(text: str) -> tuple[str, str]:
    t = text.strip()
    if not t:
        return "", ""

    m = re.search(r"^(.{5,140}?(?:입니다\.|합니다\.|됩니다\.|임\.)).*$", t)
    if m:
        title = m.group(1).strip()
        rest = t[len(title):].strip()
        return title, rest

    m2 = re.search(r"^(.{5,140}?[.!?])\s+(.+)$", t)
    if m2:
        return m2.group(1).strip(), m2.group(2).strip()

    title = t[:80].strip()
    rest = t[80:].strip()
    return title, rest


def to_title_content(raw_text: str) -> tuple[str, str]:
    t = normalize_newlines(strip_links(raw_text))
    if not t:
        return "", ""

    paras = re.split(r"\n{2,}", t)
    first_para = squash_ws(paras[0]) if paras else ""
    rest_para = squash_ws(" ".join(paras[1:])) if len(paras) > 1 else ""

    if 0 < len(first_para) <= 70 and rest_para:
        title = first_para
        content = rest_para
    else:
        flat = squash_ws(t.replace("\n", " "))
        title, content = first_sentence_split(flat)

    if content and content.startswith(title):
        content = squash_ws(content[len(title):].lstrip(" .:-"))

    if not content:
        content = title

    return title, content


def normalize_entry(item: dict) -> dict | None:
    meta = item.get("metadata", {}) or {}
    card_name_raw = meta.get("title", "") or meta.get("card_name", "")

    prefix = None
    card_name = None
    for key, val in PREFIX_MAP.items():
        if key in card_name_raw:
            prefix = val
            card_name = key
            break
    if not prefix or not card_name:
        return None

    raw_text = item.get("text") or item.get("title") or card_name_raw
    title, body = to_title_content(raw_text)

    if not title:
        return None

    if "[TABLE]" in title or "[TABLE]" in body:
        return None
    if "table" in (item.get("id") or "").lower():
        return None

    return {
        "id": item.get("id", ""),
        "title": title,
        "content": body,
        "metadata": {
            "card_name": card_name,
            "category": meta.get("category", ""),
        },
        "prefix": prefix,
    }


def convert_items(items: list[dict]) -> list[dict]:
    out = []
    for item in items:
        norm = normalize_entry(item)
        if norm:
            out.append(norm)
    return out


def assign_ids(items: list[dict]) -> list[dict]:
    counters = {}
    for item in items:
        prefix = item.pop("prefix")
        counters[prefix] = counters.get(prefix, 0) + 1
        item["id"] = f"{prefix}_{counters[prefix]:03d}"

        t = item["title"]
        c = item.get("content", "")
        if c and c != t:
            item["text"] = f"{t}\n{c}"
        else:
            item["text"] = t

    return items


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    terms_raw = load_json(BASE / "special_terms.json")
    faq_raw = load_json(BASE / "special_faq.json")
    senior_raw = load_json(BASE / "senior_faq.json")

    terms = convert_items(terms_raw)
    faq = convert_items(faq_raw) + convert_items(senior_raw)

    terms_out = assign_ids(terms)
    faq_out = assign_ids(faq)

    (BASE / "special_terms_formatted.json").write_text(
        json.dumps(terms_out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (BASE / "special_faq_formatted.json").write_text(
        json.dumps(faq_out, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"[OK] terms: {len(terms_out)} -> {BASE / 'special_terms_formatted.json'}")
    print(f"[OK] faq:   {len(faq_out)} -> {BASE / 'special_faq_formatted.json'}")


if __name__ == "__main__":
    main()
