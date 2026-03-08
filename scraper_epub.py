import requests
from bs4 import BeautifulSoup
import re, time, os, traceback
from ebooklib import epub

BASE       = "https://dorar.net"
INDEX      = "https://dorar.net/tafseer"
DELAY      = 1.0
OUT_DIR    = "dorar_tafseer_epub"
EPUB_FILE  = os.path.join(OUT_DIR, "موسوعة_التفسير_بالخط_العثماني.epub")
QURAN_FILE = "quran-uthmani.txt"

TEST_SURAHS = None if os.environ.get("TEST_SURAHS") == "None" else (
    int(os.environ["TEST_SURAHS"]) if os.environ.get("TEST_SURAHS") else None
)

_TIP_RE            = re.compile(r'\x01(\d+)\x01')
_AYAH_RANGE_RE     = re.compile(r'الآيات?\s*\((\d+)(?:-(\d+))?\)')
_quran_db: dict[int, dict[int, str]] = {}
_amiri_font_bytes  = None

AMIRI_QURAN_URL = "https://github.com/aliftype/amiri/raw/main/AmiriQuran.ttf"

ARABIC_CSS = """
@charset "UTF-8";

@font-face {
    font-family: "AmiriQuran";
    src: url("../fonts/AmiriQuran.ttf") format("truetype");
}

body {
    direction: rtl;
    text-align: justify;
    font-family: "Amiri", "Scheherazade New", "Traditional Arabic", "Arabic Typesetting",
                 "Dubai", "Segoe UI", "Arial Unicode MS", serif;
    font-size: 1em;
    line-height: 2.0;
    margin: 1.2em 1.8em;
    color: #1a1a1a;
}

h1 { font-size: 1em; text-align: right; border-bottom: 2px solid #444; padding-bottom: 0.3em; margin-top: 1em; font-weight: bold; }
h2 { font-size: 1em; text-align: right; color: #2c2c2c; margin-top: 1.5em; font-weight: bold; }
h3 { font-size: 1em; text-align: right; color: #3a3a3a; margin-top: 1em; font-weight: bold; }
h4 { font-size: 1em; text-align: right; color: #555; margin-top: 0.8em; font-weight: bold; }

p { margin: 0.6em 0; }

.source { color: #777; font-size: 0.85em; margin-bottom: 1em; text-align: right; }
.section-title { font-weight: bold; color: #333; }
hr { border: none; border-top: 1px solid #ccc; margin: 1.5em 0; }

.quran {
    font-family: "AmiriQuran", "Amiri Quran", "KFGQPC Uthmanic Script HAFS",
                 "Scheherazade New", "Traditional Arabic", serif;
    color: #1a4a1a;
}

.qpage-block {
    direction: rtl;
    text-align: justify;
    margin: 1em 0;
    padding: 0.8em 1em;
    background: #f7f4ef;
    border-right: 3px solid #6a8a3a;
    font-family: "AmiriQuran", "Amiri Quran", "KFGQPC Uthmanic Script HAFS",
                 "Scheherazade New", "Traditional Arabic", serif;
    font-size: 1em;
    line-height: 2.2;
}

.quran-ayah {
    font-family: "AmiriQuran", "Amiri Quran", "KFGQPC Uthmanic Script HAFS",
                 "Scheherazade New", "Traditional Arabic", serif;
}

.quran-marker {
    font-family: "AmiriQuran", "Amiri Quran", "Scheherazade New", serif;
    color: #6a8a3a;
    font-size: 0.9em;
}

.quran-basmala {
    display: block;
    text-align: center;
    font-family: "AmiriQuran", "Amiri Quran", "KFGQPC Uthmanic Script HAFS",
                 "Scheherazade New", serif;
    margin: 0.5em 0;
    color: #2a4a2a;
}

sup.fn-ref { font-size: 0.72em; line-height: 0; vertical-align: super; }
sup.fn-ref a { color: #0055aa; text-decoration: none; border-bottom: 1px dotted #0055aa; }

.footnotes {
    margin-top: 2.5em;
    border-top: 2px solid #bbb;
    padding-top: 1em;
    font-size: 0.83em;
    color: #444;
    text-align: right;
}
.footnotes h3 { font-size: 1em; color: #555; margin-bottom: 0.8em; }
.footnote-item { margin: 0.5em 0; padding-right: 0.3em; border-right: 2px solid #ddd; }
.footnote-back { color: #0055aa; text-decoration: none; font-size: 0.85em; margin-right: 0.4em; }
"""


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

def build_ayahs_html(surah_num: int, from_ayah: int, to_ayah: int) -> str:
    surah = _quran_db.get(surah_num, {})
    if not surah:
        print(f"  [QURAN] سورة {surah_num} غير موجودة في الملف")
        return ""

    parts = []
    if from_ayah == 1 and surah_num not in (1, 9):
        parts.append('<span class="quran-basmala">بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ</span>')

    found = 0
    for n in range(from_ayah, to_ayah + 1):
        text = surah.get(n)
        if text:
            parts.append(
                f'<span class="quran-ayah">{text}</span>'
                f'<span class="quran-marker">\uFD3F{n}\uFD3E</span>'
            )
            found += 1

    if not found:
        print(f"  [QURAN] لم تُعثر على آيات {from_ayah}-{to_ayah} في سورة {surah_num}")
        return ""

    return '<div class="qpage-block">' + " ".join(parts) + '</div>'

def extract_quran_block(html, surah_num: int) -> str:
    soup = BeautifulSoup(html, "html.parser")
    if not soup.find("div", id="qpage"):
        return ""
    og = soup.find("meta", property="og:title")
    if not og:
        print(f"  [QURAN] لا يوجد og:title")
        return ""
    content = og.get("content", "")
    m = _AYAH_RANGE_RE.search(content)
    if not m:
        print(f"  [QURAN] لم يُطابق الـ regex: {content}")
        return ""
    from_ayah = int(m.group(1))
    to_ayah   = int(m.group(2)) if m.group(2) else from_ayah
    print(f"  [QURAN] سورة {surah_num} آيات {from_ayah}-{to_ayah}")
    return build_ayahs_html(surah_num, from_ayah, to_ayah)


# ══════════════════════════════════════════════
# خط Amiri Quran
# ══════════════════════════════════════════════

def fetch_amiri_font():
    global _amiri_font_bytes
    if _amiri_font_bytes is not None:
        return _amiri_font_bytes
    try:
        r = requests.get(AMIRI_QURAN_URL, timeout=30)
        if r.status_code == 200:
            _amiri_font_bytes = r.content
            print(f"  [FONT ✔] Amiri Quran — {len(r.content)//1024} KB")
            return _amiri_font_bytes
        print(f"  [FONT ERR] Amiri Quran — {r.status_code}")
    except Exception as e:
        print(f"  [FONT ERR] Amiri Quran — {e}")
    return None


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

    all_html  = []
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
            span.replace_with(f'<span class="quran">﴿{span.get_text(strip=True)}﴾</span>')
        for span in art.find_all("span", class_="sora"):
            span.replace_with(f" {span.get_text(strip=True)} ")
        for span in art.find_all("span", class_="hadith"):
            span.replace_with(span.get_text(strip=True))
        for span in art.find_all("span", class_="title-2"):
            span.replace_with(f'<h4>{span.get_text(strip=True)}</h4>')
        for span in art.find_all("span", class_="title-1"):
            span.replace_with(f'<h4 class="section-title">{span.get_text(strip=True)}</h4>')
        for a in art.find_all("a"):
            if re.search(r"السابق|التالي|الصفحة|المراجع|اعتماد", a.get_text()):
                a.decompose()
        for i in range(1, 7):
            for h in art.find_all(f"h{i}"):
                h.replace_with(f'<h{min(i+2,6)}>{h.get_text(strip=True)}</h{min(i+2,6)}>')
        for p in art.find_all("p"):
            p.insert_before("\n\n")
            p.insert_after("\n\n")

        text = art.get_text(separator="\n", strip=False)

        def replace_marker(m, _tips=tips_map, _fns=footnotes):
            tid  = int(m.group(1))
            body = _tips.get(tid, '')
            gid  = len(_fns) + 1
            _fns.append((gid, body))
            return (f'<sup class="fn-ref">'
                    f'<a id="fnref{gid}" href="#fn{gid}">[{gid}]</a>'
                    f'</sup>')

        text = _TIP_RE.sub(replace_marker, text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'(?<!\n)\n(?![\n])', ' ', text)
        text = re.sub(r'\n{2,}', '</p>\n<p>', text).strip()
        text = f"<p>{text}</p>" if text else ""

        if text:
            all_html.append(text)

    return {"text_html": "\n".join(all_html), "footnotes": footnotes}


# ══════════════════════════════════════════════
# بناء HTML صفحة
# ══════════════════════════════════════════════

def build_page_html(title, source_url, parsed):
    parts = [
        f'<h1>{title}</h1>',
        f'<p class="source">{source_url}</p>',
        '<hr/>',
    ]

    quran_block = parsed.get("quran_block", "")
    if quran_block:
        parts.append(quran_block)
        parts.append('<hr/>')

    text_html = parsed.get("text_html", "")
    footnotes = parsed.get("footnotes", [])

    if text_html:
        parts.append(text_html)

    if footnotes:
        parts.append('<div class="footnotes"><h3>الحواشي</h3>')
        for (fid, body) in footnotes:
            parts.append(
                f'<p class="footnote-item" id="fn{fid}">'
                f'<strong>[{fid}]</strong> {body} '
                f'<a class="footnote-back" href="#fnref{fid}" title="رجوع">↩</a>'
                f'</p>'
            )
        parts.append('</div>')

    return "\n".join(parts)

def wrap_xhtml(title, body_html):
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<!DOCTYPE html>'
        '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ar" dir="rtl">'
        '<head>'
        f'<title>{title}</title>'
        '<meta charset="utf-8"/>'
        '<link rel="stylesheet" href="../style/main.css" type="text/css"/>'
        '</head>'
        f'<body>{body_html}</body>'
        '</html>'
    ).encode("utf-8")


# ══════════════════════════════════════════════
# حفظ EPUB
# ══════════════════════════════════════════════

def save_epub(book_data, session):
    os.makedirs(OUT_DIR, exist_ok=True)
    book = epub.EpubBook()
    book.set_identifier("dorar-tafseer-001")
    book.set_title("موسوعة التفسير")
    book.set_language("ar")
    book.add_author("موسوعة الدرر السنية")
    book.set_direction("rtl")

    css = epub.EpubItem(
        uid="style", file_name="style/main.css",
        media_type="text/css", content=ARABIC_CSS.encode("utf-8"),
    )
    book.add_item(css)

    # تضمين خط Amiri Quran
    amiri_bytes = fetch_amiri_font()
    if amiri_bytes:
        book.add_item(epub.EpubItem(
            uid="font_amiri_quran",
            file_name="fonts/AmiriQuran.ttf",
            media_type="font/truetype",
            content=amiri_bytes,
        ))
        print("  [FONT ✔] Amiri Quran مضمّن في EPUB")
    else:
        print("  [FONT ⚠] تعذّر تضمين Amiri Quran")

    spine = ["nav"]
    toc   = []

    for entry in book_data:
        snum     = entry["surah_num"]
        stitle   = entry["surah_title"]
        surl     = entry["surah_url"]
        intro    = entry["intro"]
        sections = entry["sections"]

        surah_items = []

        # صفحة التعريف
        intro_html = build_page_html(f"{stitle} — تعريف السورة", surl, intro)
        intro_item = epub.EpubHtml(
            title=f"{stitle} — تعريف",
            file_name=f"s{snum:03d}_intro.xhtml",
            lang="ar", direction="rtl",
        )
        intro_item.content = wrap_xhtml(f"{stitle} — تعريف", intro_html)
        intro_item.add_item(css)
        book.add_item(intro_item)
        spine.append(intro_item)
        surah_items.append(intro_item)

        # صفحة لكل مقطع
        for i, sec in enumerate(sections, 1):
            sec_html = build_page_html(sec["title"], sec["url"], sec)
            item     = epub.EpubHtml(
                title=sec["title"],
                file_name=f"s{snum:03d}_sec{i:03d}.xhtml",
                lang="ar", direction="rtl",
            )
            item.content = wrap_xhtml(sec["title"], sec_html)
            item.add_item(css)
            book.add_item(item)
            spine.append(item)
            surah_items.append(item)

        sub_links = [epub.Link(p.file_name, p.title, p.file_name) for p in surah_items]
        toc.append((epub.Section(stitle, href=f"s{snum:03d}_intro.xhtml"), sub_links))

    book.toc   = toc
    book.spine = spine
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    epub.write_epub(EPUB_FILE, book)
    print(f"\n✔ EPUB محفوظ: {EPUB_FILE}")


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

        book_data = []

        for surah in surah_links:
            snum   = surah["num"]
            stitle = surah["title"]
            surl   = surah["url"]

            print(f"\n{'='*50}")
            print(f"[{snum}] {stitle}")

            html_surah = get_page(session, surl, referer=INDEX)
            time.sleep(DELAY)
            if not html_surah:
                continue

            intro                = extract_content(html_surah)
            intro["quran_block"] = ""
            first_url            = get_first_section_link(html_surah, snum)
            print(f"  تعريف: {len(intro['text_html'])} حرف")

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
                title           = get_page_title(html_sec)
                parsed          = extract_content(html_sec)
                qblock          = extract_quran_block(html_sec, snum)
                parsed["quran_block"] = qblock
                print(f"    [{sec_idx}] {title[:50]}  →  {len(parsed['text_html'])} حرف"
                      + ("  [✔ آيات]" if qblock else ""))
                sections.append({"url": next_url, "title": title, **parsed})
                next_url = get_next_link(html_sec)
                sec_idx += 1

            print(f"  → {len(sections)} مقطع")

            book_data.append({
                "surah_num"  : snum,
                "surah_title": stitle,
                "surah_url"  : surl,
                "intro"      : intro,
                "sections"   : sections,
            })

        print("\n④ بناء EPUB...")
        save_epub(book_data, session)
        print("\n✔ اكتمل.")

    except SystemExit as e:
        print(e)
    except Exception:
        traceback.print_exc()