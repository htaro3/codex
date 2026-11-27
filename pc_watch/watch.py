#!/usr/bin/env python3
"""Conservative Yahoo! Flea Market mini-PC deal watch.

Only public HTML, robot policy respected, maximum 1 search page per run.
No bypass of CAPTCHAs/login/anti-bot measures. GitHub Issues are used only
for verified strong candidates and deduplicated by exact item ID.
Mercari is intentionally not claimed as monitored by this worker.
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from html.parser import HTMLParser

ROOT = "https://paypayfleamarket.yahoo.co.jp"
SEARCH = ROOT + "/search/" + urllib.parse.quote("ミニPC")
USER_AGENT = "MiniPCWatch/0.2 (personal listing research)"
REPO = os.environ.get("GITHUB_REPOSITORY", "")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
NOW = dt.datetime.now(dt.timezone.utc)
MAX_AGE_MINUTES = 20
MAX_DETAIL_REQUESTS = 4

# Price thresholds: deliberately tighter than an ordinary good deal.
CPU_LIMITS = {
    "7430U": 37000, "7530U": 38000, "5825U": 43000,
    "7730U": 43000, "5800H": 40000, "6800H": 49000,
    "6800U": 48000, "6850H": 50000, "7735HS": 52000,
    "7840HS": 62000, "7940HS": 65000, "8845HS": 66000,
    "13900HK": 62000, "12600H": 45000, "12700H": 50000,
}
BLOCK = [
    "ベアボーン", "ジャンク", "部品取り", "biosのみ", "biosまで",
    "動作未確認", "未チェック", "メモリなし", "メモリ無し",
    "ssdなし", "ssd無し", "osなし", "os無し",
    "液晶割れ", "起動しません", "電源入りません", "不具合",
    "ブルースクリーン", "再起動を繰り返", "本体のみジャンク",
    "パーツ", "ケースのみ", "パーツ取り",
]

class JSONScript(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_next = False
        self.next_data = ""
    def handle_starttag(self, tag, attributes):
        if tag == "script" and dict(attributes).get("id") == "__NEXT_DATA__":
            self.in_next = True
    def handle_data(self, data):
        if self.in_next:
            self.next_data += data
    def handle_endtag(self, tag):
        if tag == "script":
            self.in_next = False

def retrieve(url, *, timeout=15):
    request = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "ja,en;q=0.8",
    })
    with urllib.request.urlopen(request, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError("HTTP %s" % response.status)
        return response.read(2_000_000).decode("utf-8", "replace")

def public_allowed(url):
    robots_url = ROOT + "/robots.txt"
    try:
        raw = retrieve(robots_url)
    except Exception as exc:
        print("ROBOTS_UNAVAILABLE", type(exc).__name__, "skip", flush=True)
        return False
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(raw.splitlines())
    ok = rp.can_fetch(USER_AGENT, url)
    if not ok:
        print("ROBOTS_DISALLOW", url, flush=True)
    return ok

def next_json(page):
    parser = JSONScript()
    parser.feed(page)
    if not parser.next_data:
        raise ValueError("__NEXT_DATA__ not found")
    return json.loads(parser.next_data)

def parsed_time(iso):
    try:
        result = dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return result.astimezone(dt.timezone.utc)
    except (TypeError, ValueError, AttributeError):
        return None

def is_recent(iso):
    value = parsed_time(iso)
    if not value:
        return False
    delta = (NOW - value).total_seconds()
    return -180 <= delta <= MAX_AGE_MINUTES * 60

def cpu_model(text):
    s = text.upper()
    # Avoid assuming the CPU from marketing phrases like "faster than 6800H".
    m = re.search(r"(?:CPU|プロセッサ|搭載|RYZEN|CORE I[3579]).{0,35}?(7430U|7530U|5825U|7730U|5800H|6800H|6800U|6850H|7735HS|7840HS|7940HS|8845HS|13900HK|12600H|12700H)", s)
    if m: return m.group(1)
    return None

def installed_ram_gb(title, description):
    t = title + "\n" + description
    # Reject explicit conflicting configurations and "supports up to 64GB" advertising.
    pairs = []
    for line in t.splitlines():
        low = line.lower()
        if any(w in low for w in ("最大", "拡張可能", "増設可能", "max ", "up to", "対応", "別売")):
            continue
        if re.search(r"(?:メモリ|ram|memory|ddr[45])", low):
            for m in re.finditer(r"(?<!\d)(32|48|64)\s*(?:gb|g)(?!\d)", low):
                pairs.append(int(m.group(1)))
    if not pairs:
        # Common short listing titles: "... /32GB/1TB"
        for m in re.finditer(r"(?<!\d)(32|48|64)\s*GB\s*[/＋+]\s*(?:512\s*GB|1\s*TB|2\s*TB)", title, flags=re.I):
            pairs.append(int(m.group(1)))
    return min(pairs) if pairs else None

def installed_ssd_gb(title, description):
    t = title + "\n" + description
    vals = []
    for line in t.splitlines():
        low = line.lower()
        if any(w in low for w in ("最大", "拡張可能", "増設可能", "max ", "up to", "対応", "別売")):
            continue
        if re.search(r"ssd|ストレージ|m\.2|rom", low) or re.search(r"\b(?:32|48|64)\s*gb\s*[/＋+]", low):
            for num, unit in re.findall(r"(?<!\d)(256|500|512|1000|1024|2000|2048|1|2|4)\s*(TB|GB)\b", line, flags=re.I):
                value = int(num) * (1024 if unit.upper() == "TB" else 1)
                if value >= 256:
                    vals.append(value)
    return max(vals) if vals else None

def eligible(item):
    title = item.get("title", "")
    description = item.get("description", "")
    low = (title + "\n" + description).lower()
    if any(b.lower() in low for b in BLOCK):
        return None, "blocked condition"
    if item.get("status") != "OPEN":
        return None, "not for sale"
    if not is_recent(item.get("createDate")):
        return None, "not new"
    if not re.search(r"ミニ\s*(?:pc|パソコン)|mini\s*pc|nucbox|ser[56789]|um7|geekom|nipogi|beelink|minisforum|acemu?agic|gmktec", low, re.I):
        return None, "not a mini pc"
    cpu = cpu_model(title) or cpu_model(description)
    if not cpu:
        return None, "cpu unknown"
    price = item.get("price")
    if not isinstance(price, int) or price > CPU_LIMITS[cpu]:
        return None, "above buy threshold"
    ram = installed_ram_gb(title, description)
    if ram is None or ram < 32:
        return None, "32GB installed unverified"
    ssd = installed_ssd_gb(title, description)
    if ssd is None or ssd < 512:
        return None, "512GB installed unverified"
    if not re.search(r"動作確認|問題なく|正常|起動確認|不具合なし|動作品|美品|未使用|新品", low):
        return None, "working condition unverified"
    return {"id": item["id"], "title": title, "cpu": cpu,
            "ram": ram, "ssd": ssd, "price": price,
            "url": ROOT + "/item/" + item["id"],
            "listed": item.get("createDate"),
            "seller": (item.get("seller") or {}).get("nickname", "")}, "eligible"

def github_api(path, *, method="GET", data=None):
    if not (REPO and TOKEN):
        raise RuntimeError("missing GitHub Actions token/repo")
    payload = json.dumps(data, ensure_ascii=False).encode("utf-8") if data is not None else None
    req = urllib.request.Request(
        "https://api.github.com/repos/" + REPO + path, data=payload, method=method,
        headers={"Authorization": "Bearer " + TOKEN,
                 "Accept": "application/vnd.github+json",
                 "Content-Type": "application/json",
                 "X-GitHub-Api-Version": "2022-11-28"},
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response)

def already_alerted(item_id):
    # Issues are the persistent deduplication store; no notification for existing IDs.
    issues = github_api("/issues?state=all&per_page=100")
    return any(("[PC WATCH " + item_id + "]") in x.get("title", "") for x in issues)

def report(result, dry_run):
    title = "[PC WATCH %s] %s ¥%s" % (result["id"], result["cpu"], result["price"])
    if already_alerted(result["id"]) and not dry_run:
        print("DUPLICATE", result["id"])
        return
    print("CANDIDATE", json.dumps(result, ensure_ascii=False), flush=True)
    if dry_run:
        return
    body = ("@htaro3\n\n"
            "**購入候補（最終確認は購入者自身が実施）**\n\n"
            "- 商品: " + result["title"] + "\n"
            "- 価格: ¥" + format(result["price"], ",") + "\n"
            "- CPU: " + result["cpu"] + "\n"
            "- 搭載メモリ: " + str(result["ram"]) + "GB\n"
            "- SSD: " + str(result["ssd"]) + "GB\n"
            "- 出品日時: " + str(result["listed"]) + "\n"
            "- URL: " + result["url"] + "\n\n"
            "**理由**: 新着かつ32GB以上の完成品で、CPU別の厳格な購入価格基準を満たします。\n"
            "**注意**: 出品説明を機械判定した結果です。価格・付属品・OS認証・販売状態を購入直前に再確認してください。\n")
    created = github_api("/issues", method="POST", data={"title": title, "body": body})
    print("NOTIFICATION_CREATED", created.get("html_url"), flush=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    print("WATCH_STARTED", NOW.isoformat(), "dry_run", args.dry_run, flush=True)
    if not public_allowed(SEARCH):
        return 0
    try:
        state = next_json(retrieve(SEARCH))["props"]["initialState"]
        results = state["searchState"]["search"]["result"]["items"]
    except Exception as exc:
        print("SOURCE_FAILED", type(exc).__name__, str(exc)[:150], flush=True)
        return 0
    # Search results are ranked by provider; sort the returned pool locally.
    # Not a guarantee of complete site-wide newest-10 coverage.
    recent = [x for x in results if is_recent(x.get("openTime"))]
    recent.sort(key=lambda x: x.get("openTime", ""), reverse=True)
    newest_ten = recent[:10]
    print("POOL", len(results), "RECENT", len(recent), "TOP10", len(newest_ten), flush=True)
    count = 0
    for row in newest_ten:
        if count >= MAX_DETAIL_REQUESTS: break
        title = row.get("title", "")
        price = row.get("price", 0)
        if not isinstance(price, int) or price > 70000 or not re.search(r"ミニ|mini|beelink|gmktec|geekom|nucbox|ser[56789]|um7", title, re.I):
            continue
        if any(s.lower() in title.lower() for s in BLOCK):
            continue
        item_url = ROOT + "/item/" + str(row.get("id", ""))
        if not public_allowed(item_url):
            continue
        count += 1
        try:
            item = next_json(retrieve(item_url))["props"]["initialState"]["itemsState"]["items"]["item"]
            result, why = eligible(item)
            print("CHECK", row.get("id"), why, flush=True)
            if result:
                report(result, args.dry_run)
        except urllib.error.HTTPError as exc:
            print("ITEM_HTTP", exc.code, row.get("id"), flush=True)
            if exc.code in (403, 429):
                break
        except Exception as exc:
            print("ITEM_FAILED", row.get("id"), type(exc).__name__, str(exc)[:140], flush=True)
    print("WATCH_COMPLETE", flush=True)
    return 0

if __name__ == "__main__":
    sys.exit(main())
