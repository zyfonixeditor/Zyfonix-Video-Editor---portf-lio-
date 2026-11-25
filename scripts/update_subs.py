"""Stiahne aktuálne počty odberateľov z YouTube a zapíše ich do subs.json.

Spúšťa ho denne GitHub Actions (.github/workflows/update-subs.yml).
Kľúče zodpovedajú objektu `clients` v index.html.
"""
import json
import os
import re
import urllib.request
from datetime import datetime, timezone

CHANNELS = {
    "mgfitman": "https://www.youtube.com/@MGFitman",
    "mgfitman_gaming": "https://www.youtube.com/@MGFitmanGaming",
    "skyf": "https://www.youtube.com/@SkyfCS",
    "twiler": "https://www.youtube.com/channel/UCvT293-aCO9EbKaPJM3tA7Q",
    "nardosk": "https://www.youtube.com/@Nardosk1",
    "stepsirl": "https://www.youtube.com/channel/UCuQwP1mNT0Nl0LBu4tSXhgw",
    "mgfitman_roblox": "https://www.youtube.com/@MGFitmanRoblox",
    "shrnuto": "https://www.youtube.com/@Shrnuto",
}
TIKTOK = {
    "drago_hauls": "https://www.tiktok.com/@drago_hauls",
}
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "subs.json")

# počet v hlavičke kanála; "subscriberCountText" by chytil aj odporúčané kanály
HEADER_RE = re.compile(r'"content":"([\d.,]+[KM]?) subscribers"')
TT_RE = re.compile(r'"followerCount":(\d+)')


def short(n):
    """18500 -> '18.5K', rovnako ako YouTube (3 platné číslice)."""
    for div, suf in ((1e6, "M"), (1e3, "K")):
        if n >= div:
            return f"{n / div:.3g}{suf}"
    return str(n)


def fetch(url):
    req = urllib.request.Request(url + ("&" if "?" in url else "?") + "hl=en&persist_hl=1", headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36",
        "Accept-Language": "en",
        "Cookie": "CONSENT=YES+1",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def main():
    try:
        with open(OUT, encoding="utf-8") as f:
            old = json.load(f).get("subs", {})
    except (OSError, ValueError):
        old = {}
    subs = dict(old)
    sources = [(k, u, HEADER_RE) for k, u in CHANNELS.items()] + [(k, u, TT_RE) for k, u in TIKTOK.items()]
    for key, url, rx in sources:
        try:
            m = rx.search(fetch(url))
        except Exception as e:
            print(f"{key}: chyba {e}")
            continue
        if m:
            val = short(int(m.group(1))) if rx is TT_RE else m.group(1)
            subs[key] = val.replace(".", ",") + "+"  # rovnaký formát ako na webe, napr. 4,17K+
            print(f"{key}: {subs[key]}")
        else:
            print(f"{key}: počet sa nenašiel, nechávam {old.get(key)}")
    if subs:
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump({"updated": datetime.now(timezone.utc).isoformat(timespec="seconds"), "subs": subs}, f, ensure_ascii=False, indent=2)
            f.write("\n")


if __name__ == "__main__":
    main()
