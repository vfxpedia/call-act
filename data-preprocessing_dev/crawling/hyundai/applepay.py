import argparse
import json
import re
import ssl
from pathlib import Path

import urllib3
from bs4 import BeautifulSoup
from bs4.element import Comment

BASE_URL = "https://www.hyundaicard.com"
SECTION_PATHS = {
    "usage_places": "/docfiles/cms/cusSer/guide/creampay/PCCPUUG4001_02_CMS01.html",
    "transportation": "/docfiles/cms/cusSer/guide/creampay/PCCPUUG4001_06_CMS01.html",
    "overseas": "/docfiles/cms/cusSer/guide/creampay/PCCPUUG4001_04_CMS01.html",
    "merchants": "/docfiles/cms/cusSer/guide/creampay/PCCPUUG4001_05_CMS01.html",
    "faq": "/docfiles/cms/cusSer/guide/creampay/PCCPUUG4001_03_CMS01.html",
}

WHITESPACE_RE = re.compile(r"\s+")
SKIP_LINE_EXACT = {"이전", "다음"}
SKIP_LINE_SUFFIXES = ("이미지", "아이콘", "로고")


def dedupe(items):
    return list(dict.fromkeys(item for item in items if item))


def get_lines(root=None, *, selector=None, tags=None, texts=None, filter_lines=False):
    if texts is not None:
        items = texts
    elif root is None:
        return []
    elif selector:
        items = root.select(selector)
    elif tags:
        items = root.find_all(tags)
    else:
        items = [root]

    lines = []
    for item in items:
        if item is None:
            continue
        if hasattr(item, "get_text"):
            raw = item.get_text(" ", strip=True)
        else:
            raw = str(item)
        text = WHITESPACE_RE.sub(" ", raw or "").strip()
        if filter_lines and (not text or text in SKIP_LINE_EXACT or text.endswith(SKIP_LINE_SUFFIXES)):
            continue
        if text:
            lines.append(text)
    return dedupe(lines)


def get_first_line(*args, **kwargs):
    lines = get_lines(*args, **kwargs)
    return lines[0] if lines else None


def load_soup(http, path):
    url = f"{BASE_URL}{path}"
    resp = http.request("GET", url)
    if resp.status != 200:
        raise RuntimeError(f"Failed to fetch {url} (status {resp.status})")
    soup = BeautifulSoup(resp.data.decode("utf-8", "ignore"), "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        comment.extract()
    return soup


def compose_heading(section_label, item_title):
    if section_label and item_title and section_label != item_title:
        return f"{section_label} - {item_title}"
    return item_title or section_label


def wrap_text(text, limit):
    parts = []
    start = 0
    while start < len(text):
        end = min(len(text), start + limit)
        chunk = text[start:end]
        if end < len(text):
            space = chunk.rfind(" ")
            if space > 0:
                end = start + space
                chunk = text[start:end]
        parts.append(chunk)
        start = end
        if start < len(text) and text[start] == " ":
            start += 1
    return parts


def pack_lines(heading, lines, max_chars, max_body_len):
    chunks = []
    current = []
    current_len = len(heading)
    for line in lines:
        if len(line) > max_body_len:
            if current:
                chunks.append("\n".join(current))
                current = []
                current_len = len(heading)
            for part in wrap_text(line, max_body_len):
                chunks.append(part)
            continue
        projected = current_len + len(line) + 1
        if current and projected > max_chars:
            chunks.append("\n".join(current))
            current = [line]
            current_len = len(heading) + len(line) + 1
        else:
            current.append(line)
            current_len = projected
    if current:
        chunks.append("\n".join(current))
    return chunks


def build_text_chunks(heading, body_lines, max_chars):
    heading_lines = get_lines(texts=[heading]) if heading else []
    heading = heading_lines[0] if heading_lines else ""
    lines = get_lines(texts=body_lines, filter_lines=True)
    if not heading and lines:
        heading = lines.pop(0)
    if not heading:
        return []
    if max_chars < 50:
        max_chars = 50
    max_body_len = max_chars - len(heading) - 1
    if max_body_len < 20:
        max_body_len = max_chars
    contents = pack_lines(heading, lines, max_chars, max_body_len)
    return [(heading, content) for content in contents]


def add_chunks(chunks, heading, body_lines, meta_title, meta_category, max_chars):
    meta_title = meta_title or "unknown"
    meta_category = meta_category or meta_title
    for title, content in build_text_chunks(heading, body_lines, max_chars):
        text = f"{title} {content}".strip() if content else title
        chunks.append(
            {
                "id": None,
                "title": title,
                "content": content,
                "text": text,
                "metadata": {"category1": meta_title, "category2": meta_category},
            }
        )


def iter_records(sections):
    usage = sections.get("usage_places", {})
    if usage:
        label = usage.get("label") or usage.get("title") or "usage_places"
        section_title = usage.get("title") or label
        if usage.get("intro"):
            yield (section_title, usage["intro"], label, section_title)
        for category in usage.get("categories", []):
            name = category.get("category") or label
            lines = (category.get("stores") or []) + (category.get("details") or [])
            yield (compose_heading(label, name), lines, label, name)

    transport = sections.get("transportation", {})
    if transport:
        label = transport.get("label") or transport.get("title") or "transportation"
        section_title = transport.get("title") or label
        highlights = transport.get("highlights") or []
        if highlights:
            lines = []
            for item in highlights:
                title = item.get("title")
                desc = item.get("description")
                lines.append(f"{title} - {desc}" if title and desc else title or desc)
            yield (section_title, lines, label, section_title)
        for step in transport.get("steps", []):
            step_title = step.get("title") or label
            lines = []
            lines.extend(step.get("summary") or [])
            lines.extend(step.get("bullets") or [])
            instructions = step.get("instructions")
            if isinstance(instructions, dict):
                for key, steps in instructions.items():
                    lines.append(key)
                    lines.extend(steps)
            elif instructions:
                lines.extend(instructions)
            yield (compose_heading(label, step_title), lines, label, step_title)
        usage_places = transport.get("usage_places") or []
        if usage_places:
            title = transport.get("usage_places_title") or "usage_places"
            yield (compose_heading(label, title), usage_places, label, title)
        excluded = transport.get("charge_excluded_cards") or []
        if excluded:
            title = transport.get("charge_excluded_title") or "charge_excluded_cards"
            yield (compose_heading(label, title), excluded, label, title)

    overseas = sections.get("overseas", {})
    if overseas:
        label = overseas.get("label") or overseas.get("title") or "overseas"
        offline = overseas.get("offline", {})
        for box in offline.get("intro_boxes", []):
            title = box.get("title") or label
            yield (compose_heading(label, title), [box.get("description")], label, title)
        for method in offline.get("methods", []):
            title = method.get("title") or label
            lines = (method.get("description") or []) + (method.get("steps") or []) + (method.get("notes") or [])
            yield (compose_heading(label, title), lines, label, title)
        express = offline.get("express_mode")
        if express:
            title = express.get("title") or label
            lines = (express.get("description") or []) + (express.get("steps") or []) + (express.get("notes") or [])
            yield (compose_heading(label, title), lines, label, title)
        mark_notes = offline.get("mark_notes")
        if mark_notes:
            title = mark_notes.get("title") or label
            lines = [mark_notes.get("notes_heading")] if mark_notes.get("notes_heading") else []
            lines.extend(mark_notes.get("notes") or [])
            yield (compose_heading(label, title), lines, label, title)
        online = overseas.get("online", {})
        for box in online.get("intro_boxes", []):
            title = box.get("title") or label
            yield (compose_heading(label, title), [box.get("description")], label, title)
        process_headings = online.get("process_headings") or []
        if process_headings:
            yield (label, process_headings, label, process_headings[0] or label)
        notes = online.get("notes") or []
        if notes:
            lines = [online.get("notes_heading")] if online.get("notes_heading") else []
            lines.extend(notes)
            yield (label, lines, label, online.get("notes_heading") or label)
        transit = overseas.get("transit_cards_by_country", {})
        if transit:
            title = transit.get("title") or "transit_cards"
            lines = []
            for card in transit.get("cards", []):
                country = card.get("country")
                brands = card.get("brands")
                lines.append(f"{country}: {brands}" if country and brands else country or brands)
            lines.extend(transit.get("notes") or [])
            yield (compose_heading(label, title), lines, label, title)

    merchants = sections.get("merchants", {})
    if merchants:
        label = merchants.get("label") or "merchants"
        hero = merchants.get("hero", {})
        if hero:
            title = hero.get("title") or label
            lines = [hero.get("subtitle"), hero.get("description")]
            yield (compose_heading(label, title), lines, label, title)
        terminal = merchants.get("terminal_check", {})
        if terminal:
            title = terminal.get("title") or label
            lines = [terminal.get("description")] + (terminal.get("notes") or [])
            yield (compose_heading(label, title), lines, label, title)
        promo = merchants.get("promotional_materials", {})
        if promo:
            title = promo.get("title") or label
            lines = (promo.get("description") or []) + (promo.get("items") or [])
            yield (compose_heading(label, title), lines, label, title)
        van_list = merchants.get("van_companies") or []
        if van_list:
            title = merchants.get("van_companies_title") or "van_companies"
            lines = [item.get("name") for item in van_list if item.get("name")]
            yield (compose_heading(label, title), lines, label, title)
        disclaimer = merchants.get("disclaimer") or []
        if disclaimer:
            yield (label, disclaimer, label, "disclaimer")

    faq = sections.get("faq", {})
    if faq:
        label = faq.get("label") or faq.get("title") or "faq"
        if faq.get("intro"):
            heading = faq.get("title") or label
            yield (heading, [faq["intro"]], label, heading)
        for category in faq.get("categories", []):
            category_title = category.get("category") or label
            for qa in category.get("qas", []):
                yield (qa.get("question"), qa.get("answer") or [], label, category_title)


def build_chunks(sections, max_chars):
    chunks = []
    for heading, lines, title, category in iter_records(sections):
        add_chunks(chunks, heading, lines, title, category, max_chars)
    for idx, chunk in enumerate(chunks):
        chunk["id"] = f"hyundai_applepay_{idx:04d}"
    return chunks


def parse_tab_label(soup):
    return get_first_line(soup, selector=".tab_box .ui_tab_common .btn.current")


def get_first_heading(container):
    return get_first_line(container.find(["h1", "h2", "h3", "h4"])) if container else None


def parse_usage_places(soup):
    label = parse_tab_label(soup)
    container = soup.select_one("div.applepay_cont.use_applepay")
    title = get_first_heading(container)
    intro = []
    if container:
        for child in container.children:
            if getattr(child, "name", None) is None:
                continue
            if child.name == "div" and "use_applepay_content" in (child.get("class") or []):
                break
            if child.name in ("p", "h2", "h3"):
                text = get_first_line(child)
                if text and text != title:
                    intro.append(text)
    intro = dedupe(intro)

    categories = []
    for entry in container.select("ul.box_line_store > li.list") if container else []:
        name = get_first_line(entry.find("h3"))
        if not name:
            continue
        stores = get_lines(entry, selector="ul.store_list li.store p")
        details = get_lines(entry.find("div", class_="accodSlide"), tags=("p", "li"))
        category = {"category": name, "stores": stores}
        if details:
            category["details"] = details
        categories.append(category)

    return {"label": label, "title": title, "intro": intro, "categories": categories}


def parse_slide_instructions(step_div):
    slide_tabs = step_div.find("div", class_="slide_tabs")
    if slide_tabs:
        labels = get_lines(step_div, selector=".tab_list li")
        instruction_sets = {}
        list_divs = [
            div
            for div in slide_tabs.find_all("div", recursive=False)
            if any(cls.startswith("list") for cls in (div.get("class") or []))
        ]
        for idx, list_div in enumerate(list_divs):
            key = labels[idx] if idx < len(labels) else f"list{idx}"
            steps = get_lines(list_div, selector=".sld_txt")
            if steps:
                instruction_sets[key] = steps
        return instruction_sets
    return get_lines(step_div, selector=".slide_wrap .sld_txt")


def parse_transportation(soup):
    label = parse_tab_label(soup)
    container = soup.find("div", class_="transit_cont")
    title = get_first_heading(container)

    highlights = []
    if container:
        for info in container.select("div.cont02 .info"):
            heading = get_first_line(info.find("strong"))
            desc = get_first_line(info.find("span"))
            if heading or desc:
                highlights.append({"title": heading, "description": desc})

    steps = []
    for step_div in container.select("div.step") if container else []:
        step_title = get_first_line(step_div.find(["h3", "h4"]))
        area = step_div.find("div", class_="area")
        summary = []
        if area:
            for paragraph in area.find_all("p"):
                if paragraph.find_parent(class_="slide_wrap") or paragraph.find_parent(class_="procedure_list"):
                    continue
                text = get_first_line(paragraph)
                if text:
                    summary.append(text)
        summary = dedupe(summary)

        bullets = []
        if area:
            for ul in area.find_all("ul", class_=lambda c: c and "bul_list" in " ".join(c)):
                bullets.extend(get_lines(ul, tags="li"))
        bullets = dedupe(bullets)

        instructions = parse_slide_instructions(step_div)
        step = {"title": step_title}
        if summary:
            step["summary"] = summary
        if bullets:
            step["bullets"] = bullets
        if instructions:
            step["instructions"] = instructions
        steps.append(step)

    usage_places = []
    usage_places_title = None
    if container:
        use_list = container.select_one("ul.use_list")
        if use_list:
            usage_places_title = get_first_line(use_list.find_previous(["h2", "h3", "h4"]))
        usage_places = get_lines(container, selector="ul.use_list li")

    charge_excluded_cards = []
    charge_excluded_title = None
    pop = soup.find(id="popTCardList")
    if pop:
        charge_excluded_title = get_first_line(pop.find(["h1", "h2", "h3"]))
        charge_excluded_cards = get_lines(pop, tags="li")

    return {
        "label": label,
        "title": title,
        "highlights": highlights,
        "steps": steps,
        "usage_places": usage_places,
        "usage_places_title": usage_places_title,
        "charge_excluded_cards": charge_excluded_cards,
        "charge_excluded_title": charge_excluded_title,
    }


def parse_infoboxes(container):
    boxes = []
    for box in container.select(".use_infobox") if container else []:
        title = get_first_line(box.select_one(".uif_tit"))
        desc = get_first_line(box.select_one(".uif_txt"))
        item = {"title": title}
        if desc:
            item["description"] = desc
        boxes.append(item)
    return boxes


def parse_procedure_steps(container):
    return get_lines(container, selector=".procedure_list .sld_txt") if container else []


def parse_method_block(block, title_tags):
    title = get_first_line(block.find(title_tags))
    description = []
    for paragraph in block.find_all("p"):
        if paragraph.find_parent(class_="procedure_list") or paragraph.find_parent("div", class_="alC"):
            continue
        text = get_first_line(paragraph)
        if text:
            description.append(text)
    description = dedupe(description)
    steps = parse_procedure_steps(block)
    notes = get_lines(block, selector="div.alC p")
    result = {"title": title}
    if description:
        result["description"] = description
    if steps:
        result["steps"] = steps
    if notes:
        result["notes"] = notes
    return result


def parse_overseas_offline(offline):
    if not offline:
        return {}
    result = {}
    infobox_wrap = offline.find("div", class_="use_infobox_wrap")
    if infobox_wrap:
        result["intro_boxes"] = parse_infoboxes(infobox_wrap)

    methods = []
    for block in offline.find_all("div", class_="mt160", recursive=False):
        methods.append(parse_method_block(block, ("h3", "h4")))
    if methods:
        result["methods"] = methods

    tip_block = offline.select_one("div.content_wrap.mt80")
    if tip_block:
        result["express_mode"] = parse_method_block(tip_block, ("h4",))

    mark_block = offline.select_one("div.content_wrap.bd_none")
    if mark_block:
        heading_text = get_first_line(mark_block, selector="h4")
        notes_heading = get_first_line(mark_block, selector="p.h4_b_lt")
        notes = get_lines(mark_block, selector="ul li")
        mark_notes = {"title": heading_text, "notes": notes}
        if notes_heading:
            mark_notes["notes_heading"] = notes_heading
        result["mark_notes"] = mark_notes

    return result


def parse_overseas_online(online):
    if not online:
        return {}
    result = {}
    content = online.find("div", class_="content_wrap")
    if not content:
        return result
    intro_boxes = parse_infoboxes(content)
    if intro_boxes:
        result["intro_boxes"] = intro_boxes

    process_headings = get_lines(content, selector="div.mt160 h2")
    if process_headings:
        result["process_headings"] = process_headings

    useinfo = content.find("div", class_="useinfo")
    if useinfo:
        notes_heading = get_first_line(useinfo.find(["p", "h4"], class_="h4_b_lt"))
        notes = get_lines(useinfo, tags="li")
        if notes:
            result["notes"] = notes
        if notes_heading:
            result["notes_heading"] = notes_heading

    return result


def parse_transit_cards_by_country(soup):
    pop = soup.find(id="popnation")
    if not pop:
        return {}
    title = get_first_line(pop.find(["h1", "h2", "h3"]))
    cards = []
    for entry in pop.select("div.trans_cardlist dl"):
        country = get_first_line(entry.find("dt"))
        brands = get_first_line(entry.find("dd"))
        if country or brands:
            cards.append({"country": country, "brands": brands})
    notes = get_lines(pop, selector="ul.bul_list02 li")
    result = {"cards": cards}
    if title:
        result["title"] = title
    if notes:
        result["notes"] = notes
    return result


def parse_overseas(soup):
    return {
        "label": parse_tab_label(soup),
        "title": get_first_heading(soup.find("div", class_="applepay_cont")),
        "offline": parse_overseas_offline(soup.find("div", class_="item_offline_only")),
        "online": parse_overseas_online(soup.find("div", class_="item_online_only")),
        "transit_cards_by_country": parse_transit_cards_by_country(soup),
    }


def parse_merchants(soup):
    label = parse_tab_label(soup)
    container = soup.find("div", class_="applepay_cont")

    hero = {}
    hero_section = container.find("div", class_="mt60") if container else None
    if hero_section:
        hero["title"] = get_first_line(hero_section.find("h3"))
        hero["subtitle"] = get_first_line(hero_section.find("h4"))
        hero["description"] = get_first_line(hero_section.find("p"))
        hero = {k: v for k, v in hero.items() if v}

    terminal_check = {}
    terminal_block = container.find("div", class_="box_customer02") if container else None
    if terminal_block:
        terminal_check["title"] = get_first_line(terminal_block.find("h3"))
        terminal_check["description"] = get_first_line(terminal_block.find("p"))
        notes = get_lines(terminal_block, selector="div.fc_m_a64 p span")
        if notes:
            terminal_check["notes"] = notes
        terminal_check = {k: v for k, v in terminal_check.items() if v}

    promotional_materials = {}
    promo_block = container.find("ul", class_="promotion_items") if container else None
    promo_section = promo_block.find_parent() if promo_block else None
    if promo_section:
        promotional_materials["title"] = get_first_line(promo_section.find("h3"))
        descriptions = []
        for tag in promo_section.find_all("p"):
            if tag.find_parent("ul", class_="promotion_items"):
                continue
            text = get_first_line(tag)
            if text:
                descriptions.append(text)
        descriptions = dedupe(descriptions)
        if descriptions:
            promotional_materials["description"] = descriptions
        items = get_lines(promo_block, selector="li p")
        if items:
            promotional_materials["items"] = items
        promotional_materials = {k: v for k, v in promotional_materials.items() if v}

    disclaimer = get_lines(container, selector="ul.bul_list li") if container else []

    van_companies = []
    van_companies_title = None
    pop = soup.find(id="popVanList")
    if pop:
        van_companies_title = get_first_line(pop.find(["h1", "h2", "h3"]))
        van_companies = [{"name": name} for name in get_lines(pop, selector="ul.van_list li")]

    return {
        "label": label,
        "hero": hero,
        "terminal_check": terminal_check,
        "promotional_materials": promotional_materials,
        "van_companies": van_companies,
        "van_companies_title": van_companies_title,
        "disclaimer": disclaimer,
    }


def parse_faq(soup):
    label = parse_tab_label(soup)
    container = soup.find("div", class_="applepay_cont")
    intro = get_first_line(container.find("p")) if container else None

    categories = []
    for category in soup.select("div.sub_accod > div.accodWrap"):
        category_title = get_first_line(category, selector="div.tit a")
        qas = []
        qna_list = category.select_one("ul.accod_list.qna_type")
        if qna_list:
            for item in qna_list.select("li.accodWrap"):
                question = get_first_line(item, selector="div.box_tit p")
                answer = get_lines(item.find("div", class_="accodSlide"), tags=("p", "li"))
                qas.append({"question": question, "answer": answer})
        categories.append({"category": category_title, "qas": qas})

    return {"label": label, "title": get_first_heading(container), "intro": intro, "categories": categories}


SECTIONS = {
    "usage_places": (SECTION_PATHS["usage_places"], parse_usage_places),
    "transportation": (SECTION_PATHS["transportation"], parse_transportation),
    "overseas": (SECTION_PATHS["overseas"], parse_overseas),
    "merchants": (SECTION_PATHS["merchants"], parse_merchants),
    "faq": (SECTION_PATHS["faq"], parse_faq),
}


def parse_args():
    parser = argparse.ArgumentParser(description="Crawl Hyundai Card Apple Pay guide sections.")
    parser.add_argument(
        "--output",
        default=str(Path(__file__).resolve().parents[2] / "data" / "hyundai" / "applepay.json"),
        help="Output JSON path.",
    )
    parser.add_argument("--max-chars", type=int, default=1000, help="Maximum characters per chunk.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument(
        "--unicode",
        action="store_true",
        help="Write Unicode characters instead of \\u escapes.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    ctx = ssl.create_default_context()
    ctx.options |= ssl.OP_LEGACY_SERVER_CONNECT
    http = urllib3.PoolManager(ssl_context=ctx)

    sections = {key: fn(load_soup(http, path)) for key, (path, fn) in SECTIONS.items()}
    chunks = build_chunks(sections, args.max_chars)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(
            chunks,
            handle,
            ensure_ascii=not args.unicode,
            indent=2 if args.pretty else None,
        )
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
