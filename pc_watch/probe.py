#!/usr/bin/env python3
"""Mini-PC listing availability/search probe. Standard library only.

Diagnostic: tests publicly accessible search pages without bypassing access controls.
No personal data, no purchase operations, and no paid API.
"""
import datetime as dt
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from html.parser import HTMLParser

UA = "MiniPCWatch/0.1 (personal price research; contact via GitHub repository)"
KEYWORDS = ["ミニPC", "Ryzen ミニPC", "GEEKOM", "MINISFORUM"]
HOSTS = {
    "mercari": "https://jp.mercari.com",
    "yahoo": "https://paypayfleamarket.yahoo.co.jp",
}
PATTERNS = {
    "mercari": re.compile(r"(?:https?://jp\.mercari\.com)?(/item/m\d{9,12})"),
    "yahoo": re.compile(r"(?:https?://paypayfleamarket\.yahoo\.co\.jp)?(/item/[a-zA-Z0-9]+)"),
}

class ListingLinks(HTMLParser):
    def __init__(self, pattern):
        super().__init__(convert_charrefs=True)
        self.pattern = pattern
        self.items = []
        self.seen = set()
    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        attrs = dict(attrs)
        href = attrs.get("href", "")
        match = self.pattern.search(href)
        if match and match.group(1) not in self.seen:
            self.seen.add(match.group(1))
            self.items.append(match.group(1))

def url_for(site, keyword):
    if site == "mercari":
        return HOSTS[site] + "/search?" + urllib.parse.urlencode({
            "keyword": keyword,
            "status": "on_sale",
            "sort": "created_time",
            "order": "desc",
        })
    return HOSTS[site] + "/search/" + urllib.parse.quote(keyword) + "?sort=-created"

def fetch(url, timeout=18):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "ja,en;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read(4_000_000)
            return resp.status, resp.geturl(), data.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, url, ""
    except (urllib.error.URLError, TimeoutError) as e:
        print("FETCH_ERROR", url.split("?")[0], str(e)[:200], flush=True)
        return 0, url, ""

def robot_allows(site, url):
    robots_url = HOSTS[site] + "/robots.txt"
    status, _, robots = fetch(robots_url)
    if status != 200:
        print("ROBOTS_UNAVAILABLE", site, status, "skip", flush=True)
        return False
    parser = urllib.robotparser.RobotFileParser()
    parser.parse(robots.splitlines())
    result = parser.can_fetch(UA, url)
    if not result:
        print("ROBOTS_DISALLOW", site, urllib.parse.urlparse(url).path, flush=True)
    return result

def main():
    print("START", dt.datetime.now(dt.timezone.utc).isoformat(), flush=True)
    found = {}
    for site in HOSTS:
        total = []
        for keyword in KEYWORDS:
            url = url_for(site, keyword)
            if not robot_allows(site, url):
                continue
            status, final_url, page = fetch(url)
            parser = ListingLinks(PATTERNS[site])
            if status == 200:
                parser.feed(page)
            print("SEARCH", site, repr(keyword), "http", status,
                  "bytes", len(page), "item_links", len(parser.items),
                  "first_three", parser.items[:3], flush=True)
            total.extend(HOSTS[site] + x for x in parser.items[:10])
        found[site] = list(dict.fromkeys(total))[:10]
    print("SUMMARY", json.dumps({k: len(v) for k, v in found.items()}, ensure_ascii=False), flush=True)
    if not any(found.values()):
        print("UNVERIFIED_NO_LISTINGS: source inaccessible or parser needs revision; do not treat as no deals.", flush=True)
        return 2
    print("PROBE_ONLY: no purchases, alerts, or issue creation.", flush=True)
    return 0

if __name__ == "__main__":
    sys.exit(main())
