"""
Povlači najnovije vijesti s HCL.hr (RSS) i sprema ih u data/vijesti.json.
Pokreće se automatski preko GitHub Actions (.github/workflows/vijesti.yml).
Ako HCL nekad ne odgovori, ostaju stare vijesti i ništa se ne kvari.
"""
import datetime as dt
import html
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "vijesti.json")
FEEDS = ["https://www.hcl.hr/feed/", "https://www.hcl.hr/vijesti/feed/"]
MAX = int(os.environ.get("MAX_VIJESTI", "15"))
HEADERS = {"User-Agent": "FrizerRakic/1.0 (+github actions; RSS citac)"}


def clean(t):
    t = html.unescape(re.sub(r"<[^>]+>", "", t or "")).strip()
    return re.sub(r"\s+", " ", t)[:200]


def from_rss(xml_bytes):
    root = ET.fromstring(xml_bytes)
    items = []
    for it in root.iter("item"):
        title = clean(it.findtext("title"))
        link = (it.findtext("link") or "").strip()
        if title and link.startswith("https://"):
            items.append({"naslov": title, "link": link, "izvor": "HCL"})
        if len(items) >= MAX:
            break
    return items


def from_homepage(text):
    items, seen = [], set()
    for m in re.finditer(r'<h2[^>]*>\s*<a href="(https://www\.hcl\.hr/(?:vijest|video|najave|recenzija)/[^"]+)"[^>]*>(.*?)</a>', text, re.S):
        link, title = m.group(1), clean(m.group(2))
        if title and link not in seen:
            seen.add(link)
            items.append({"naslov": title, "link": link, "izvor": "HCL"})
        if len(items) >= MAX:
            break
    return items


def main():
    items = []
    for url in FEEDS:
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            r.raise_for_status()
            items = from_rss(r.content)
            if items:
                break
        except Exception as e:
            print(f"RSS {url} nije uspio: {e}", file=sys.stderr)
    if not items:
        try:
            r = requests.get("https://www.hcl.hr/", headers=HEADERS, timeout=30)
            r.raise_for_status()
            items = from_homepage(r.text)
        except Exception as e:
            print(f"Naslovna nije uspjela: {e}", file=sys.stderr)
    if not items:
        print("Nema novih vijesti, ostaju stare.")
        return
    old = {}
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            old = json.load(f)
    if [i["link"] for i in old.get("stavke", [])] == [i["link"] for i in items]:
        print("Vijesti su iste kao prije.")
        return
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"izvor": "HCL.hr", "azurirano": now, "stavke": items}, f, ensure_ascii=False, indent=1)
    print(f"Spremljeno {len(items)} vijesti.")


if __name__ == "__main__":
    main()
