import requests
from bs4 import BeautifulSoup
import re, time, os, traceback

BASE      = "https://dorar.net"
INDEX     = "https://dorar.net/tafseer"
DELAY     = 1.0
OUT_DIR   = "dorar_tafseer_md"
QURAN_FILE = "quran-uthmani.txt"

TEST_SURAHS = None if os.environ.get("TEST_SURAHS") == "None" else (
    int(os.environ["TEST_SURAHS"]) if os.environ.get("TEST_SURAHS") else None
)

_TIP_RE        = re.compile(r'\x01(\d+)\x01')
_AYAH_RANGE_RE = re.compile(r'الآيات?\s*\((\d+)(?:-(\d+))?\)')
_quran_db: dict[int, dict[int, str]] = {}


# ══════════════════════════════════════════════
# ملف القرآن
# ══════════════════════════════════════════════

def load_quran_file():
    if _quran_db:
        return
    if not os.path.exists(QURAN_FILE):
        raise SystemExit(f"❌ الملف غير موجود: {QURAN_FILE}")
    with open(QURAN_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("|", 2)
            if len(parts) != 3:
                continue
            s, a, text = int(parts[0]), int(parts[1]), parts[2]
            _quran_db.setdefault(s, {})[a] = text
    total = sum(len(v) for v in _quran_db.values())
    print(f"  [QURAN ✔] {len(_quran_db)} سورة — {total} آية")

def build_ayahs_md(surah_num: int, from_ayah: int, to_ayah: int) -> str:
    surah = _quran_db.get(surah_num, {})
    if not surah:
        print(f"  [QURAN] سورة {surah_num} غير موجودة في الملف")
        return ""

    lines = []
    if from_ayah == 1 and surah_num not in (1, 9):
        lines.append("> بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ\n>")

    found = 0
    for n in range(from_ayah, to_ayah + 1):
        text = surah.get(n)
        if text:
            lines.append(f"> {text} ﴿{n}﴾")
            found += 1

    if not found:
        print(f"  [QURAN] لم تُعثر على آيات {from_ayah}-{to_ayah} في سورة {surah_num}")
        return ""

    return "\n".join(lines) + "\n"

def extract_ayah_range(html) -> tuple[int, int] | None:
    """يستخرج نطاق الآيات من og:title."""
    soup = BeautifulSoup(html, "html.parser")
    if not soup.find("div", id="qpage"):
        return None
    og = soup.find("meta", property="og:title")
    if not og:
        return None
    m = _AYAH_RANGE_RE.search(og.get("content", ""))
    if not m:
        return None
    from_a = int(m.group(1))
    to_a   = int(m.group(2)) if m.group(2) else from_a
    return from_a, to_a


# ══════════════════════════════════════════════
# Session
# ══════════════════════════════════════════════

def make_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent"               : "Mozilla/5.0 (Windows NT 6.1; WOW64) "
                                     "AppleWebKit/537.36 (KHTML, like Gecko) "
                                     "Chrome/109.0.0.0 Safari/537.36",
        "Accept"                   : "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language"          : "ar,en-US;q=0.9,en;q=0.8",
        "Connection"               : "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    })
    return s

def get_page(session, url, referer=INDEX):
    session.headers["Referer"] = referer
    try:
        r = session.get(url, timeout=20)
        print(f"  [{r.status_code}] {url}")
        return r.text if r.status_code == 200 else ""
    except Exception as e:
        print(f"  [ERR] {url} — {e}")
        return ""


# ══════════════════════════════════════════════
# روابط وتنقل
# ══════════════════════════════════════════════

SURAH_RE   = re.compile(r"^/tafseer/(\d+)$")
SECTION_RE = re.compile(r"^/tafseer/(\d+)/(\d+)$")

def get_surah_links(html):
    soup  = BeautifulSoup(html, "html.parser")
    links, seen = [], set()
    for card in soup.find_all("div", class_="card-personal"):
        a = card.find("a", href=SURAH_RE)
        if not a:
            continue
        href  = a["href"]
        title = a.get_text(strip=True)
        if href in seen or not title:
            continue
        seen.add(href)
        num = int(SURAH_RE.match(href).group(1))
        links.append({"url": BASE + href, "title": title, "num": num})
    links.sort(key=lambda x: x["num"])
    return links

def get_first_section_link(html, surah_num):
    soup  = BeautifulSoup(html, "html.parser")
    cands = []
    for a in soup.find_all("a", href=SECTION_RE):
        m = SECTION_RE.match(a["href"])
        if m and int(m.group(1)) == surah_num:
            cands.append((int(m.group(2)), BASE + a["href"]))
    if cands:
        cands.sort()
        return cands[0][1]
    return None

def get_next_link(html):
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=SECTION_RE):
        if "التالي" in a.get_text():
            return BASE + a["href"]
    return None

def get_page_title(html):
    soup = BeautifulSoup(html, "html.parser")
    og   = soup.find("meta", property="og:title")
    if og and og.get("content"):
        return og["content"].split(" - ", 1)[-1].strip()
    t = soup.find("title")
    if t:
        return t.get_text().split(" - ")[-1].strip()
    return ""


# ══════════════════════════════════════════════
# استخراج المحتوى
# ══════════════════════════════════════════════

def convert_inner_soup(soup_tag):
    for inner in soup_tag.find_all("span", class_="aaya"):
        inner.replace_with(f"﴿{inner.get_text(strip=True)}﴾")
    for inner in soup_tag.find_all("span", class_="hadith"):
        inner.replace_with(inner.get_text(strip=True))
    for inner in soup_tag.find_all("span", class_="sora"):
        t = inner.get_text(strip=True)
        if t:
            inner.replace_with(f" {t} ")

def get_tip_text(tip):
    _marker = re.compile(r'\x01\d+\x01')
    for attr in ("data-original-title", "title", "data-content", "data-tippy-content"):
        val = tip.get(attr, "").strip()
        if val:
            inner_soup = BeautifulSoup(val, "html.parser")
            convert_inner_soup(inner_soup)
            result = re.sub(r'\s+', ' ', inner_soup.get_text()).strip()
            return _marker.sub('', result).strip()
    convert_inner_soup(tip)
    result = re.sub(r'\s+', ' ', tip.get_text(strip=True)).strip()
    return _marker.sub('', result).strip()

def extract_content(html):
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all(["nav", "header", "footer", "script", "style", "form"]):
        tag.decompose()
    for pat in [
        re.compile(r"\bmodal\b"), re.compile(r"\balert-dorar\b"),
        re.compile(r"\btitle-manhag\b"), re.compile(r"\bdefault-gradient\b"),
        re.compile(r"\bfooter-copyright\b"), re.compile(r"\bcard-personal\b"),
    ]:
        for tag in soup.find_all(True, class_=pat):
            tag.decompose()

    block = None
    card  = soup.find("div", class_="card-body")
    if card:
        for pane in card.find_all("div", class_="tab-pane"):
            if "active" not in pane.get("class", []):
                continue
            if pane.find("article") or len(pane.get_text(strip=True)) > 200:
                block = pane
                break
        if not block:
            for pane in card.find_all("div", class_="tab-pane"):
                if pane.find("article"):
                    block = pane
                    break

    if not block:
        block = soup.find("body") or soup

    articles = block.find_all("article")
    if not articles:
        articles = soup.find_all("article") or [block]

    all_text  = []
    footnotes = []

    for art in articles:
        tips_map    = {}
        tip_counter = [1]
        for tip in reversed(list(art.find_all("span", class_="tip"))):
            tip_text = get_tip_text(tip)
            if tip_text:
                tips_map[tip_counter[0]] = tip_text
                tip.replace_with(f"\x01{tip_counter[0]}\x01")
                tip_counter[0] += 1
            else:
                tip.decompose()

        for span in art.find_all("span", class_="aaya"):
            span.replace_with(f"﴿{span.get_text(strip=True)}﴾")
        for span in art.find_all("span", class_="sora"):
            span.replace_with(f" {span.get_text(strip=True)} ")
        for span in art.find_all("span", class_="hadith"):
            span.replace_with(span.get_text(strip=True))
        for span in art.find_all("span", class_="title-2"):
            span.replace_with(f"\n#### {span.get_text(strip=True)}\n")
        for span in art.find_all("span", class_="title-1"):
            span.replace_with(f"\n##### {span.get_text(strip=True)}\n")
        for a in art.find_all("a"):
            if re.search(r"السابق|التالي|الصفحة|المراجع|اعتماد", a.get_text()):
                a.decompose()
        for i in range(1, 7):
            for h in art.find_all(f"h{i}"):
                h.replace_with(f"\n{'#' * (i + 2)} {h.get_text(strip=True)}\n")
        for p in art.find_all("p"):
            p.insert_before("\n\n")
            p.insert_after("\n\n")

        text     = art.get_text(separator="\n", strip=False)
        local_fn = [len(footnotes) + 1]

        def replace_marker(m, _tips=tips_map, _fns=footnotes, _ctr=local_fn):
            tid  = int(m.group(1))
            body = _tips.get(tid, '')
            _fns.append(f"[^{_ctr[0]}]: {body}")
            ref  = f" [^{_ctr[0]}]"
            _ctr[0] += 1
            return ref

        text = _TIP_RE.sub(replace_marker, text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'(?<!\n)\n(?![\n#>﴿\d])', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()

        if text:
            all_text.append(text)

    clean = re.sub(r'\n{3,}', '\n\n', "\n\n".join(all_text)).strip()
    return {"text": clean, "footnotes": footnotes}


# ══════════════════════════════════════════════
# حفظ Markdown
# ══════════════════════════════════════════════

def fix_multiline_footnotes(text):
    lines  = text.splitlines()
    result = []
    fn_def = re.compile(r'^\[\^\d+\]:')
    i = 0
    while i < len(lines):
        line = lines[i]
        if fn_def.match(line):
            parts = [line.rstrip()]
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if nxt == '' or fn_def.match(nxt):
                    break
                parts.append(nxt.strip())
                i += 1
            result.append(' '.join(p for p in parts if p))
        else:
            result.append(line)
            i += 1
    return '\n'.join(result)

def renum(text, fns, global_fn_ref):
    if not fns:
        return text, []
    local_map = {}
    for fn in fns:
        m = re.match(r'\[\^(\d+)\]:', fn)
        if m and m.group(1) not in local_map:
            local_map[m.group(1)] = global_fn_ref[0]
            global_fn_ref[0] += 1
    for loc in local_map:
        text = re.sub(
            rf'(?<!\d)\[\^{re.escape(loc)}\](?!\d)',
            f'\x02{loc}\x02', text
        )
    for loc, gbl in local_map.items():
        text = text.replace(f'\x02{loc}\x02', f'[^{gbl}]')
    new_fns = []
    for fn in fns:
        m = re.match(r'\[\^(\d+)\]:(.*)', fn, re.DOTALL)
        if m:
            loc = m.group(1)
            gbl = local_map.get(loc)
            if gbl is not None:
                new_fns.append(f"[^{gbl}]:{m.group(2)}")
    return text, new_fns

def save_markdown(surah_title, surah_num, intro, sections):
    safe     = re.sub(r'[^\w\u0600-\u06FF]', '_', surah_title)[:40]
    filepath = os.path.join(OUT_DIR, f"{surah_num:03d}_{safe}.md")

    lines         = [f"# {surah_title}\n\n",
                     f"> المصدر: {BASE}/tafseer/{surah_num}\n\n",
                     "---\n\n"]
    all_footnotes = []
    global_fn_ref = [1]

    if intro.get("text"):
        lines.append("## تعريف السورة\n\n")
        text, fns = renum(intro["text"], intro.get("footnotes", []), global_fn_ref)
        lines.append(f"{text}\n\n")
        all_footnotes.extend(fns)
        lines.append("---\n\n")

    for sec in sections:
        lines.append(f"## {sec['title']}\n\n")
        lines.append(f"> {sec['url']}\n\n")

        # ── الآيات
        if sec.get("ayahs_md"):
            lines.append(sec["ayahs_md"])
            lines.append("\n\n")

        if sec.get("text"):
            text, fns = renum(sec["text"], sec.get("footnotes", []), global_fn_ref)
            lines.append(f"{text}\n\n")
            all_footnotes.extend(fns)

        lines.append("---\n\n")

    if all_footnotes:
        lines.append("\n")
        for fn in all_footnotes:
            lines.append(f"{fn}\n")

    content = fix_multiline_footnotes("".join(lines))
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    total = len(intro.get("text", "")) + sum(len(s.get("text", "")) for s in sections)
    print(f"    ✔ {filepath}  |  {len(sections)} مقطع  |  ~{total//1024} KB  |  {len(all_footnotes)} حاشية")
    return filepath


# ══════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════

if __name__ == "__main__":
    try:
        os.makedirs(OUT_DIR, exist_ok=True)

        print("⓪ تحميل ملف القرآن...")
        load_quran_file()

        session = make_session()

        print("\n① تهيئة الجلسة...")
        get_page(session, INDEX, referer=BASE)
        time.sleep(1.5)

        print("\n② جلب الصفحة الرئيسية...")
        html_main = get_page(session, INDEX, referer=BASE)
        time.sleep(2)
        if not html_main:
            raise SystemExit("فشل جلب الصفحة الرئيسية")

        surah_links = get_surah_links(html_main)
        print(f"\n③ {len(surah_links)} سورة\n")

        if TEST_SURAHS:
            surah_links = surah_links[:TEST_SURAHS]
            print(f"   وضع الاختبار: أول {TEST_SURAHS} سور فقط\n")

        for surah in surah_links:
            snum   = surah["num"]
            stitle = surah["title"]
            surl   = surah["url"]

            safe     = re.sub(r'[^\w\u0600-\u06FF]', '_', stitle)[:40]
            filepath = os.path.join(OUT_DIR, f"{snum:03d}_{safe}.md")
            if os.path.exists(filepath):
                print(f"  ← موجود، تخطي: {filepath}")
                continue

            print(f"\n{'='*50}")
            print(f"[{snum}] {stitle}")

            html_surah = get_page(session, surl, referer=INDEX)
            time.sleep(DELAY)
            if not html_surah:
                continue

            intro     = extract_content(html_surah)
            first_url = get_first_section_link(html_surah, snum)
            print(f"  تعريف: {len(intro['text'])} حرف")

            sections = []
            next_url = first_url
            visited  = set()
            sec_idx  = 1

            while next_url and next_url not in visited:
                visited.add(next_url)
                html_sec = get_page(session, next_url, referer=surl)
                time.sleep(DELAY)
                if not html_sec:
                    break

                title  = get_page_title(html_sec)
                parsed = extract_content(html_sec)

                # ── استخراج الآيات
                ayahs_md = ""
                rng = extract_ayah_range(html_sec)
                if rng:
                    from_a, to_a = rng
                    ayahs_md = build_ayahs_html(snum, from_a, to_a)
                    flag = f"  [آيات {from_a}-{to_a}]" if ayahs_md else "  [⚠ آيات لم تُجلب]"
                else:
                    flag = ""

                print(f"    [{sec_idx}] {title[:50]}  →  {len(parsed['text'])} حرف{flag}")
                sections.append({"url": next_url, "title": title,
                                  "ayahs_md": ayahs_md, **parsed})
                next_url = get_next_link(html_sec)
                sec_idx += 1

            print(f"  → {len(sections)} مقطع مكتمل")
            save_markdown(stitle, snum, intro, sections)

        print("\n✔ اكتمل.")

    except SystemExit as e:
        print(e)
    except Exception:
        traceback.print_exc() 
