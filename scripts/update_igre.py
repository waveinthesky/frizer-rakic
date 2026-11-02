"""
Povlači igre koje izlaze na PlayStation 5 s RAWG.io i sprema ih u data/igre.json.
Svakoj igri izračuna dvije boje iz njene naslovne slike, pa aplikacija
može taj dan u kalendaru obojiti bojama igre.

Pokreće se automatski preko GitHub Actions (.github/workflows/igre.yml).
Treba tajni ključ RAWG_KEY (besplatan, s rawg.io/apidocs).

Podešavanja (nisu obavezna, postavljaju se kao env varijable):
  MIN_ADDED  koliko igrača mora imati igru na listi da uđe u kalendar (zadano 15)
  DAYS       koliko dana unaprijed se gleda (zadano 365)
"""
import colorsys
import datetime as dt
import io
import json
import os
import sys

import requests
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "igre.json")
SPECIAL = os.path.join(ROOT, "data", "posebno.json")
API = "https://api.rawg.io/api/games"
PS5 = 187  # RAWG oznaka za PlayStation 5

KEY = os.environ.get("RAWG_KEY", "").strip()
MIN_ADDED = int(os.environ.get("MIN_ADDED", "15"))
DAYS = int(os.environ.get("DAYS", "365"))


def fetch(start, end):
    games, page = [], 1
    while page <= 6:
        r = requests.get(
            API,
            params={
                "key": KEY,
                "platforms": PS5,
                "dates": f"{start},{end}",
                "ordering": "-added",
                "page_size": 40,
                "page": page,
            },
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        games += data.get("results") or []
        if not data.get("next"):
            break
        page += 1
    return games


def hexc(rgb):
    return "#%02X%02X%02X" % tuple(int(v) for v in rgb)


def palette(img_url):
    """Dvije najživlje boje iz slike igre."""
    if not img_url:
        return []
    try:
        url = img_url.replace("/media/games/", "/media/crop/600/400/games/")
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return colors_from_bytes(r.content)
    except Exception as e:  # slika nije obavezna
        print(f"Boja nije izračunata za {img_url}: {e}", file=sys.stderr)
        return []


def colors_from_bytes(content):
    im = Image.open(io.BytesIO(content)).convert("RGB")
    im.thumbnail((160, 160))
    q = im.quantize(colors=8, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()
    found = []
    for count, idx in q.getcolors() or []:
        rgb = pal[idx * 3: idx * 3 + 3]
        h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in rgb))
        light_ok = 1.0 if 0.18 < l < 0.80 else 0.25
        found.append(((count ** 0.5) * (0.15 + s) ** 1.6 * light_ok, rgb, h, l))
    found.sort(key=lambda x: x[0], reverse=True)
    picked = []
    for _, rgb, h, l in found:
        if all(abs(h - ph) > 0.06 or abs(l - pl) > 0.25 for _, ph, pl in picked):
            picked.append((rgb, h, l))
        if len(picked) == 2:
            break
    out = []
    for rgb, h, l in picked:  # malo jače boje da kalendar izgleda živo
        _, _, s = colorsys.rgb_to_hls(*(v / 255 for v in rgb))
        r, g, b = colorsys.hls_to_rgb(h, min(max(l, 0.32), 0.62), min(1.0, s * 1.2 + 0.05))
        out.append(hexc((r * 255, g * 255, b * 255)))
    return out


def load(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    if not KEY:
        print("Nedostaje RAWG_KEY. Dodaj ga u Settings > Secrets and variables > Actions.")
        sys.exit(1)

    old = {str(g.get("id")): g for g in load(OUT).get("stavke", []) if g.get("id")}
    today = dt.date.today()
    end = today + dt.timedelta(days=DAYS)
    raw = fetch(today.isoformat(), end.isoformat())

    items = []
    for g in raw:
        released = g.get("released")
        if g.get("tba") or not released:
            continue
        if released.endswith("-12-31"):  # često znači samo "negdje te godine"
            continue
        if (g.get("added") or 0) < MIN_ADDED:
            continue
        gid = str(g["id"])
        img = g.get("background_image") or ""
        prev = old.get(gid)
        boje = prev["boje"] if prev and prev.get("slika") == img and prev.get("boje") else palette(img)
        platforms = sorted(
            p["platform"]["name"] for p in (g.get("platforms") or []) if p.get("platform")
        )
        items.append({
            "id": gid,
            "datum": released,
            "naziv": (g.get("name") or "").strip(),
            "platforme": ", ".join(platforms),
            "boje": boje,
            "slika": img,
            "link": f"https://rawg.io/games/{g.get('slug', gid)}",
        })

    for s in load(SPECIAL).get("stavke", []):
        items = [i for i in items if i["naziv"].lower() != s.get("naziv", "").lower()]
        items.append(s)

    items = [i for i in items if i.get("datum", "") >= today.isoformat()]
    items.sort(key=lambda i: (i["datum"], i["naziv"].lower()))
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    out = {"izvor": "RAWG.io", "azurirano": now, "stavke": items}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"Spremljeno {len(items)} igara u data/igre.json")


if __name__ == "__main__":
    main()
