import requests
from bs4 import BeautifulSoup

url = "https://dorar.net/tafseer/2/1"  # غيّرها لأي صفحة فيها حواشي
s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0"
html = s.get(url, timeout=20).text

soup = BeautifulSoup(html, "html.parser")
tips = soup.find_all("span", class_="tip")
print(f"عدد span.tip: {len(tips)}\n")

for i, tip in enumerate(tips[:5]):
    print(f"── حاشية {i+1} ──")
    print(f"  get_text()       : {repr(tip.get_text(strip=True)[:100])}")
    print(f"  title attr       : {repr(tip.get('title', ''))[:100]}")
    print(f"  data-orig-title  : {repr(tip.get('data-original-title', ''))[:100]}")
    print(f"  HTML كامل        : {str(tip)[:300]}")
    print()