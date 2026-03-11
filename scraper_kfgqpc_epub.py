import requests
from bs4 import BeautifulSoup
import re, time, os, traceback, json
from ebooklib import epub

BASE       = "https://dorar.net"
INDEX      = "https://dorar.net/tafseer"
DELAY      = 1.0
OUT_DIR    = "dorar_tafseer_epub"
EPUB_FILE  = os.path.join(OUT_DIR, "موسوعة_التفسير_بالخط_العثماني.epub")
MD_DIR     = os.path.join(OUT_DIR, "md")

KFGQPC_BASE      = "https://cdn.jsdelivr.net/gh/thetruetruth/quran-data-kfgqpc@main"
QURAN_JSON_URL   = f"{KFGQPC_BASE}/hafs-smart/hafs_smart_v8.json"
FONT_URL         = f"{KFGQPC_BASE}/hafs-smart/font/hafssmart.8.ttf"
QURAN_JSON_LOCAL = "hafs_smart_v8.json"
FONT_LOCAL       = "hafssmart.8.ttf"

# صفحات المقدمة والمراجع
FRONT_PAGES = [
    {
        "url"  : f"{BASE}/article/1955",
        "title": "منهج العمل في موسوعة التفسير",
        "slug" : "front_manhaj",
        "static_html": """
<h2>منهج العمل في موسوعة التفسير</h2>
<p><a href="https://dorar.net/article/1984">( اعتماد منهجية الموسوعة )</a></p>

<h3>أوَّلًا: المُقَدِّماتُ بينَ يدَي كُلِّ سورةٍ</h3>
<p>وتَشتَمِلُ على عِدَّةِ أمورٍ:</p>
<p><strong>1- اسمُ السُّورةِ</strong> وما ورد فيه مِن نُصوصٍ مَرفوعةٍ ومَوقوفةٍ، مع الإشارةِ في الحاشيةِ إلى سَبَبِ التَّسميةِ.</p>
<p><strong>2- بَيانُ المَكيِّ والمَدَنيِّ:</strong> والاعتِمادُ فيه على الضَّابطِ الزَّمانيِّ، وهو أنَّ ما نزَلَ قَبلَ الهجرةِ فهو مكِّيٌّ، وما نزَل بعدَها فهو مَدَنيٌّ. وذِكرُ الإجماعاتِ على مكيَّةِ السُّورةِ أو مَدَنيَّتِها، وما يَرِدُ عليه مِن استثناءاتٍ وما يقَعُ مِن خِلافٍ.</p>
<p><strong>3- فَضائلُ السُّورةِ وخَصائِصُها:</strong> ويُذكَرُ تَحتَه ما ثَبَت للسُّورةِ مِن فَضائِلَ، وما اختصَّت به من خَصائصَ.</p>
<p><strong>4- مَقاصِدُ السُّورةِ:</strong> ويُذكَرُ تحتَه المحورُ أو المحاوِرُ التي تدورُ عليها السُّورةُ.</p>
<p><strong>5- موضوعاتُ السُّورةِ:</strong> ويُذكَرُ تحتَه أهمُّ الموضوعاتِ التي تناولَتْها السُّورةُ.</p>

<h3>ثانيًا: في غَريبِ الكَلِماتِ</h3>
<p>1- الاقتِصارُ على الكَلِماتِ الغريبةِ التي يُحتاجُ إلى مَعرفةِ معناها.</p>
<p>2- الاعتِناءُ في التَّعريفِ بذِكرِ معنى الكَلِمة، وأصلِ اشتِقاقِها، والرَّبطِ بينهما إنْ أمكَنَ.</p>
<p>3- الاعتِمادُ في بيانِ الغريبِ على أُمَّاتِ كتُبِ الغريبِ، مِثلُ: غريب القرآن لابن قُتَيبة، ومقاييس اللُّغة لابن فارس، والمفردات للراغب، وغيرها.</p>

<h3>ثالثًا: في مُشكِل الإعرابِ</h3>
<p>1- الاقتِصارُ على بيانِ المشْكِلِ الذي يَخدُمُ التَّفسيرَ ممَّا خفِيَ إعرابُه أو أَشكَل توجيهُه النَّحويُّ.</p>
<p>2- جمْعُ المادَّةِ بالاعتِماد على: مُشكِل إعراب القرآن لمكيٍّ، والتبيان في إعراب القرآن للعُكبري، والدُّرُّ المصون للسَّمين الحَلَبي.</p>

<h3>رابعًا: في المَعنى الإجماليِّ</h3>
<p>يُراعى في هذا التَّفسيرِ الإجماليِّ الاختِصارُ وعَدَمُ التعرُّضِ للتَّفاصيلِ، وهو خُلاصةٌ لِما ذُكِرَ في تفسيرِ الآياتِ.</p>

<h3>خامِسًا: في المُناسَباتِ بين الآياتِ</h3>
<p>1- الاقتِصارُ على ذِكرِ أهمِّ المُناسَباتِ.</p>
<p>2- الابتِعادُ عن المُناسَباتِ المُتكلَّفةِ.</p>

<h3>سادسًا: في القِراءاتِ</h3>
<p>1- الاكتِفاءُ بالقِراءاتِ المتواتِرةِ.</p>
<p>2- الاقتِصارُ على ما له أثرٌ في التَّفسيرِ.</p>
<p>3- عزْوُ القِراءاتِ إلى كِتاب النشر لابن الجَزَري.</p>

<h3>سابعًا: في تَفسيرِ الآياتِ</h3>
<p>1- تَجزِئةُ السُّورةِ إلى مقاطعَ تعتَمِدُ على الوَحدةِ الموضوعيَّةِ لمجموعةِ آياتٍ مُتتاليةٍ.</p>
<p>2- الاعتِمادُ على ما نقَلَه المفسِّرونَ مِن إجماعاتٍ ثابتةٍ وصَحيحةٍ.</p>
<p>3- الاعتِمادُ في اختيارِ معاني الآياتِ على المُبَرِّزينَ والمحقِّقينَ في التَّفسير، مثل: ابن جرير، وابن كثير، وابن تيميَّة، وابن القيِّم، والسعدي، والشِّنقيطي، وابن عثيمين.</p>
<p>4- إذا وُجِد خِلافٌ في معنى الآيةِ، يُذكَرُ المعنى الرَّاجِحُ، مع الإشارةِ إلى الأقوالِ الأخرى إذا كانت قويَّةً.</p>
<p>5- تُذكَرُ أقوالُ السَّلَفِ في الحاشيةِ في المواضعِ المُشْكِلةِ مع عزْوِها إلى مصادِرِها الأصليَّةِ.</p>
<p>6- ذِكرُ ما يُناسِبُ الآيةَ من الآياتِ والأحاديثِ، وبيانُ النَّاسِخِ والمَنسوخِ، وسَبَبِ النُّزولِ إن ثبَتَ.</p>

<h3>ثامنًا: في الفَوائِدِ التَّربويَّةِ</h3>
<p>1- ذِكْرُ ما يَتعلَّق بتَزكيةِ النَّفْسِ وتهذيبِها.</p>
<p>2- ربطُ كلِّ فائدةٍ بالآيةِ التي استُنبِطَت منها مرتَّبةً بحسَبِ ترتيبِ الآياتِ.</p>

<h3>تاسعًا: في الفَوائِدِ العِلميَّةِ واللَّطائِفِ</h3>
<p>1- ذِكرُ فوائِدَ عَقَديَّة أو فقهيَّة أو غير ذلك ممَّا يُستنبَطُ من الآياتِ.</p>
<p>2- الاقتِصارُ على غُرَرِ الفوائدِ والنُّكَت البَديعة دون الواضِحِ أو البَدهيِّ.</p>

<h3>عاشرًا: في بَلاغةِ الآياتِ</h3>
<p>1- إبرازُ جَمالِ ألفاظِ القُرآنِ ومَعانيها، وحُسْنِ تَركيب جُمَله.</p>
<p>2- عدَمُ ذِكرِ الجوانِبِ البَلاغيَّةِ الصِّناعيَّةِ البَحتةِ مِمَّا يَصلُحُ للمُتخَصِّصِ فقط.</p>
<p>3- الاهتِمامُ بتَعريفِ المُصطلَحاتِ البلاغيَّةِ.</p>

<h3>حادي عشر: ضوابِطُ عامَّةٌ</h3>
<p>1- تجنُّبُ ما يخالِفُ اعتِقادَ أهلِ السُّنَّةِ والجماعةِ.</p>
<p>2- الاعتِمادُ على ما صَحَّ من الأحاديثِ المرفوعةِ والموقوفاتِ.</p>
<p>3- حُسنُ العَرضِ وسُهولةُ العبارةِ.</p>
<p>4- عدَمُ التَّعارُضِ بين المُختارِ في التَّفسيرِ وبين المعنى الإجماليِّ والفوائِدِ والبلاغِةِ.</p>
""",
    },
    {
        "url"  : f"{BASE}/article/1984",
        "title": "اعتماد منهج موسوعة التفسير",
        "slug" : "front_i3timad",
        "static_html": """
<h2>اعتماد منهج موسوعة التفسير</h2>
<p><a href="https://dorar.net/article/1955">( منهجية موسوعة التفسير )</a></p>

<h3>لجنة المراجعة العلمية</h3>
<p style="text-align:center"><strong>الشيخ الدكتور خالد بن عثمان السبت</strong><br/>أستاذ التفسير بجامعة الإمام عبدالرحمن بن فيصل</p>
<p style="text-align:center"><strong>الشيخ الدكتور أحمد سعد الخطيب</strong><br/>أستاذ التفسير بجامعة الأزهر</p>
<p style="text-align:center"><strong>الشيخ الدكتور عبدالرحمن بن معاضة الشهري</strong><br/>أستاذ التفسير بجامعة الملك سعود</p>
<p style="text-align:center"><strong>الشيخ الدكتور مساعد بن سليمان الطيار</strong><br/>أستاذ التفسير بجامعة الملك سعود</p>
<p style="text-align:center"><strong>الشيخ الدكتور منصور بن حمد العيدي</strong><br/>أستاذ التفسير بجامعة الإمام عبدالرحمن بن فيصل</p>

<h3>لجنة الإشراف العلمي</h3>
<p>تقوم اللجنة باعتماد منهجيات الموسوعات وقراءة بعض مواد الموسوعات للتأكد من تطبيق المنهجية.</p>
<p><strong>الشيخ الدكتور هتلان بن علي الهتلان</strong> — قاضي بمحكمة الاستئناف بالدمام سابقاً.</p>
<p><strong>الشيخ الدكتور أسامة بن حسن الرتوعي</strong> — المستشار العلمي بمؤسسة الدرر السنية.</p>
<p><strong>الشيخ الدكتور حسن بن علي البار</strong> — عضو الهيئة التعليمية بالكلية التقنية.</p>
<p><strong>الشيخ الدكتور منصور بن حمد العيدي</strong> — الأستاذ بجامعة الإمام عبدالرحمن بن فيصل.</p>
""",
    },
]
BACK_PAGES = [
    {"url": f"{BASE}/refs/tafseer", "title": "مراجع الموسوعة", "slug": "back_refs"},
]

TEST_SURAHS = None if os.environ.get("TEST_SURAHS") == "None" else (
    int(os.environ["TEST_SURAHS"]) if os.environ.get("TEST_SURAHS") else None
)

_TIP_RE        = re.compile(r'\x01(\d+)\x01')
_AYAH_RANGE_RE = re.compile(r'الآيات?\s*\((\d+)(?:-(\d+))?\)')

_surah_cache:       dict[int, dict[int, str]] = {}
_kfgqpc_font_bytes = None

ARABIC_CSS = """
@charset "UTF-8";

@font-face {
    font-family: "hafssmart8";
    src: url("../fonts/hafssmart.8.ttf") format("truetype");
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
    font-family: "Scheherazade New", "Traditional Arabic", "Amiri", serif;
    color: #1a4a1a;
}

.qpage-block {
    direction: rtl;
    text-align: justify;
    margin: 1em 0;
    padding: 0.8em 1em;
    background: #f7f4ef;
    border-right: 3px solid #6a8a3a;
    font-family: "hafssmart8", "KFGQPC Uthmanic Script HAFS", serif;
    font-size: 1em;
    line-height: 2.2;
}

.quran-ayah   { font-family: "hafssmart8", "KFGQPC Uthmanic Script HAFS", serif; }
.quran-marker { font-family: "hafssmart8", "KFGQPC Uthmanic Script HAFS", serif; color: #6a8a3a; font-size: 0.9em; }
.quran-basmala {
    display: block;
    text-align: center;
    font-family: "hafssmart8", "KFGQPC Uthmanic Script HAFS", serif;
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
# نصوص القرآن
# ══════════════════════════════════════════════

def _load_quran_cache():
    if _surah_cache:
        return
    data = None
    if os.path.exists(QURAN_JSON_LOCAL):
        try:
            with open(QURAN_JSON_LOCAL, encoding="utf-8") as f:
                data = json.load(f)
            print(f"  [QURAN ✔] محلي — {len(data)} سجل")
        except Exception as e:
            print(f"  [QURAN ERR] محلي — {e}")
    if data is None:
        try:
            r = requests.get(QURAN_JSON_URL, timeout=60)
            if r.status_code == 200:
                data = r.json()
                print(f"  [QURAN ✔] CDN — {len(data)} سجل")
            else:
                print(f"  [QURAN ERR] CDN HTTP {r.status_code}")
        except Exception as e:
            print(f"  [QURAN ERR] CDN — {e}")
    if not data:
        print("  [QURAN ERR] فشل تحميل بيانات القرآن")
        return
    for item in data:
        sura = int(item["sura_no"])
        aya  = int(item["aya_no"])
        text = item.get("aya_text", "").strip()
        if text:
            _surah_cache.setdefault(sura, {})[aya] = text
    total = sum(len(v) for v in _surah_cache.values())
    print(f"  [QURAN ✔] {len(_surah_cache)} سورة — {total} آية")


def fetch_surah(surah_num: int) -> dict[int, str]:
    if not _surah_cache:
        _load_quran_cache()
    return _surah_cache.get(surah_num, {})


def build_ayahs_html(surah_num: int, from_ayah: int, to_ayah: int) -> str:
    surah = fetch_surah(surah_num)
    if not surah:
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
    og   = soup.find("meta", property="og:title")
    if not og:
        return ""
    m = _AYAH_RANGE_RE.search(og.get("content", ""))
    if not m:
        return ""
    from_ayah = int(m.group(1))
    to_ayah   = int(m.group(2)) if m.group(2) else from_ayah
    print(f"  [QURAN] سورة {surah_num} آيات {from_ayah}-{to_ayah}")
    return build_ayahs_html(surah_num, from_ayah, to_ayah)


# ══════════════════════════════════════════════
# خط KFGQPC
# ══════════════════════════════════════════════

def fetch_kfgqpc_font() -> bytes | None:
    global _kfgqpc_font_bytes
    if _kfgqpc_font_bytes is not None:
        return _kfgqpc_font_bytes
    if os.path.exists(FONT_LOCAL):
        try:
            with open(FONT_LOCAL, "rb") as f:
                _kfgqpc_font_bytes = f.read()
            print(f"  [FONT ✔] محلي — {len(_kfgqpc_font_bytes)//1024} KB")
            return _kfgqpc_font_bytes
        except Exception as e:
            print(f"  [FONT ERR] محلي — {e}")
    try:
        r = requests.get(FONT_URL, timeout=30)
        if r.status_code == 200:
            _kfgqpc_font_bytes = r.content
            print(f"  [FONT ✔] CDN — {len(r.content)//1024} KB")
            return _kfgqpc_font_bytes
        print(f"  [FONT ERR] {r.status_code}")
    except Exception as e:
        print(f"  [FONT ERR] {e}")
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
# بناء HTML وMarkdown
# ══════════════════════════════════════════════

def extract_article_content(html):
    """استخراج محتوى صفحات المقالات والمراجع."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(["nav", "header", "footer", "script", "style", "form"]):
        tag.decompose()

    # صفحة المراجع: div#cntnt
    cntnt = soup.find("div", id="cntnt")
    if cntnt:
        parts = []
        for art in cntnt.find_all("article"):
            h = art.find("h5")
            title = f"<strong>{h.get_text(strip=True)}</strong> — " if h else ""
            details = []
            for strong in art.find_all("strong"):
                label = strong.get_text(strip=True).replace(":", "").strip()
                val_span = strong.find("span", class_="primary-text-color")
                if not val_span:
                    val_span = strong.find("span")
                val = val_span.get_text(strip=True) if val_span else ""
                if label and val:
                    details.append(f"{label}: {val}")
            para = "، ".join(details) + "." if details else ""
            parts.append(f"<p>{title}{para}</p>")
        return {"text_html": "\n".join(parts), "footnotes": [], "quran_block": ""}

    # صفحات المقالات: amiri_custom_content
    custom = soup.find("div", class_="amiri_custom_content")
    if custom:
        text = custom.get_text(separator="\n", strip=True)
        text = re.sub(r'\n{2,}', '</p>\n<p>', text).strip()
        return {"text_html": f"<p>{text}</p>", "footnotes": [], "quran_block": ""}

    return {"text_html": "", "footnotes": [], "quran_block": ""}


def build_page_html(title, source_url, parsed):
    parts = [f'<h1>{title}</h1>', f'<p class="source">{source_url}</p>', '<hr/>']
    quran_block = parsed.get("quran_block", "")
    if quran_block:
        parts.append(quran_block)
        parts.append('<hr/>')
    if parsed.get("text_html"):
        parts.append(parsed["text_html"])
    footnotes = parsed.get("footnotes", [])
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


def build_page_md(title, source_url, parsed):
    lines = [f"# {title}", f"", f"> المصدر: {source_url}", ""]
    quran_block = parsed.get("quran_block", "")
    if quran_block:
        # استخرج النص النظيف من الـ HTML
        qs = BeautifulSoup(quran_block, "html.parser")
        lines += ["---", "", qs.get_text(" ", strip=True), "", "---", ""]
    text_html = parsed.get("text_html", "")
    if text_html:
        ts = BeautifulSoup(text_html, "html.parser")
        lines.append(ts.get_text("\n", strip=True))
    footnotes = parsed.get("footnotes", [])
    if footnotes:
        lines += ["", "---", "## الحواشي", ""]
        for (fid, body) in footnotes:
            lines.append(f"[{fid}] {body}")
    return "\n".join(lines)


def save_md(slug, content_md):
    os.makedirs(MD_DIR, exist_ok=True)
    path = os.path.join(MD_DIR, f"{slug}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content_md)


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

def save_epub(front_data, book_data, back_data, session):
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

    font_bytes = fetch_kfgqpc_font()
    if font_bytes:
        book.add_item(epub.EpubItem(
            uid="font_hafssmart", file_name="fonts/hafssmart.8.ttf",
            media_type="font/truetype", content=font_bytes,
        ))
        print("  [FONT ✔] hafssmart مضمّن في EPUB")
    else:
        print("  [FONT ⚠] تعذّر تضمين hafssmart")

    spine = ["nav"]
    toc   = []

    # ── المقدمة ──
    for pg in front_data:
        html = build_page_html(pg["title"], pg["url"], pg["parsed"])
        item = epub.EpubHtml(
            title=pg["title"], file_name=f"{pg['slug']}.xhtml",
            lang="ar", direction="rtl",
        )
        item.content = wrap_xhtml(pg["title"], html)
        item.add_item(css)
        book.add_item(item)
        spine.append(item)
        toc.append(epub.Link(item.file_name, pg["title"], item.file_name))

    # ── السور ──
    for entry in book_data:
        snum, stitle, surl = entry["surah_num"], entry["surah_title"], entry["surah_url"]
        surah_items = []

        intro_html = build_page_html(f"{stitle} — تعريف السورة", surl, entry["intro"])
        intro_item = epub.EpubHtml(
            title=f"{stitle} — تعريف", file_name=f"s{snum:03d}_intro.xhtml",
            lang="ar", direction="rtl",
        )
        intro_item.content = wrap_xhtml(f"{stitle} — تعريف", intro_html)
        intro_item.add_item(css)
        book.add_item(intro_item)
        spine.append(intro_item)
        surah_items.append(intro_item)

        for i, sec in enumerate(entry["sections"], 1):
            sec_html = build_page_html(sec["title"], sec["url"], sec)
            item     = epub.EpubHtml(
                title=sec["title"], file_name=f"s{snum:03d}_sec{i:03d}.xhtml",
                lang="ar", direction="rtl",
            )
            item.content = wrap_xhtml(sec["title"], sec_html)
            item.add_item(css)
            book.add_item(item)
            spine.append(item)
            surah_items.append(item)

        sub_links = [epub.Link(p.file_name, p.title, p.file_name) for p in surah_items]
        toc.append((epub.Section(stitle, href=f"s{snum:03d}_intro.xhtml"), sub_links))

    # ── المراجع ──
    for pg in back_data:
        html = build_page_html(pg["title"], pg["url"], pg["parsed"])
        item = epub.EpubHtml(
            title=pg["title"], file_name=f"{pg['slug']}.xhtml",
            lang="ar", direction="rtl",
        )
        item.content = wrap_xhtml(pg["title"], html)
        item.add_item(css)
        book.add_item(item)
        spine.append(item)
        toc.append(epub.Link(item.file_name, pg["title"], item.file_name))

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
        os.makedirs(MD_DIR,  exist_ok=True)

        print("\n⓪ تحميل بيانات القرآن...")
        _load_quran_cache()

        session = make_session()

        print("\n① تهيئة الجلسة...")
        get_page(session, INDEX, referer=BASE)
        time.sleep(1.5)

        # ── صفحات المقدمة (محتوى مضمّن) ──
        print("\n② تجهيز صفحات المقدمة...")
        front_data = []
        for pg in FRONT_PAGES:
            parsed = {"text_html": pg["static_html"], "footnotes": [], "quran_block": ""}
            front_data.append({**pg, "parsed": parsed})
            save_md(pg["slug"], build_page_md(pg["title"], pg["url"], parsed))
            print(f"  ✔ {pg['title']}")

        # ── جلب صفحات المراجع ──
        print("\n③ جلب صفحات المراجع...")
        back_data = []
        for pg in BACK_PAGES:
            html = get_page(session, pg["url"], referer=BASE)
            time.sleep(DELAY)
            if not html:
                print(f"  [SKIP] {pg['url']}")
                continue
            parsed = extract_article_content(html)
            back_data.append({**pg, "parsed": parsed})
            save_md(pg["slug"], build_page_md(pg["title"], pg["url"], parsed))
            print(f"  ✔ {pg['title']} — {len(parsed['text_html'])} حرف")

        # ── جلب الصفحة الرئيسية ──
        print("\n④ جلب الصفحة الرئيسية...")
        html_main = get_page(session, INDEX, referer=BASE)
        time.sleep(2)
        if not html_main:
            raise SystemExit("فشل جلب الصفحة الرئيسية")

        surah_links = get_surah_links(html_main)
        print(f"\n⑤ {len(surah_links)} سورة\n")

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

            # حفظ MD للتعريف
            save_md(f"s{snum:03d}_intro",
                    build_page_md(f"{stitle} — تعريف", surl, intro))

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
                title                 = get_page_title(html_sec)
                parsed                = extract_content(html_sec)
                qblock                = extract_quran_block(html_sec, snum)
                parsed["quran_block"] = qblock
                print(f"    [{sec_idx}] {title[:50]}  →  {len(parsed['text_html'])} حرف"
                      + ("  [✔ آيات]" if qblock else ""))
                sections.append({"url": next_url, "title": title, **parsed})
                save_md(f"s{snum:03d}_sec{sec_idx:03d}",
                        build_page_md(title, next_url, parsed))
                next_url = get_next_link(html_sec)
                sec_idx += 1

            print(f"  → {len(sections)} مقطع")
            book_data.append({
                "surah_num": snum, "surah_title": stitle,
                "surah_url": surl, "intro": intro, "sections": sections,
            })

        print("\n⑥ بناء EPUB...")
        save_epub(front_data, book_data, back_data, session)
        print(f"✔ ملفات MD محفوظة في: {MD_DIR}")
        print("\n✔ اكتمل.")

    except SystemExit as e:
        print(e)
    except Exception:
        traceback.print_exc()