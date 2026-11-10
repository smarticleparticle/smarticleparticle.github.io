#!/usr/bin/env python3
"""
Script to turn Substack posts into blog posts that link back to Substack.
Reads the Substack RSS feed and writes one file per post into _posts/.
"""

import json
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path

FEED_URL = "https://astralalisa.substack.com/feed"
POSTS_DIR = Path(__file__).resolve().parent.parent / "_posts"


def fetch_feed(url):
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return ET.fromstring(response.read())


def yaml_string(value):
    # JSON strings are valid double-quoted YAML strings
    return json.dumps(value.strip(), ensure_ascii=False)


def build_post(item):
    title = item.findtext("title", "")
    link = item.findtext("link", "")
    description = item.findtext("description", "") or ""
    date = parsedate_to_datetime(item.findtext("pubDate"))
    slug = link.rstrip("/").split("/")[-1]

    front_matter = [
        "---",
        f"title: {yaml_string(title)}",
        f"date: {date.strftime('%Y-%m-%d')}",
        f"permalink: /posts/{date.strftime('%Y/%m')}/{slug}/",
        f"link: {yaml_string(link)}",
        f"excerpt: {yaml_string(description)}",
        "read_time: false",
        "comments: false",
        "substack: true",
        "---",
    ]
    body = f"{description.strip()}\n\n**[Read the full post on Substack →]({link})**\n"
    filename = f"{date.strftime('%Y-%m-%d')}-{slug}.md"
    return filename, "\n".join(front_matter) + "\n\n" + body


def main():
    feed = fetch_feed(FEED_URL)
    POSTS_DIR.mkdir(exist_ok=True)
    for item in feed.iter("item"):
        filename, content = build_post(item)
        path = POSTS_DIR / filename
        if path.exists() and path.read_text() == content:
            continue
        path.write_text(content)
        print(f"Wrote {path.name}")


if __name__ == "__main__":
    main()
