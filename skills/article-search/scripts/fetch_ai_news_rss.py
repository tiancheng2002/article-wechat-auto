#!/usr/bin/env python3
import argparse
import html
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET

DEFAULT_FEEDS = [
    "https://openai.com/news/rss.xml",
    "https://blog.google/technology/ai/rss/",
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "https://huggingface.co/blog/feed.xml",
    "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
    "https://the-decoder.com/feed/",
]


def text(node, name):
    found = node.find(name)
    if found is None or found.text is None:
        return ""
    return html.unescape(found.text.strip())


def link_for(item):
    link = text(item, "link")
    if link:
        return link
    link_node = item.find("{http://www.w3.org/2005/Atom}link") or item.find("link")
    if link_node is not None:
        return link_node.attrib.get("href", "")
    return ""


def parse_feed(content, feed_url, per_feed):
    root = ET.fromstring(content)
    items = []
    channel = root.find("channel")
    if channel is not None:
        items = channel.findall("item")
    else:
        items = root.findall("{http://www.w3.org/2005/Atom}entry") or root.findall("entry")

    rows = []
    for item in items[:per_feed]:
        title = text(item, "title") or text(item, "{http://www.w3.org/2005/Atom}title")
        date = (
            text(item, "pubDate")
            or text(item, "updated")
            or text(item, "published")
            or text(item, "{http://www.w3.org/2005/Atom}updated")
            or text(item, "{http://www.w3.org/2005/Atom}published")
        )
        rows.append({"feed": feed_url, "date": date, "title": title, "link": link_for(item)})
    return rows


def fetch(url, timeout):
    req = urllib.request.Request(url, headers={"User-Agent": "article-search-skill/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def main():
    parser = argparse.ArgumentParser(description="Fetch latest AI RSS items.")
    parser.add_argument("--feed-url", action="append", dest="feeds", help="RSS/Atom feed URL. May be repeated.")
    parser.add_argument("--per-feed", type=int, default=5)
    parser.add_argument("--out-file", default="")
    parser.add_argument("--timeout", type=int, default=25)
    args = parser.parse_args()

    feeds = args.feeds or DEFAULT_FEEDS
    rows = []
    for url in feeds:
        try:
            rows.extend(parse_feed(fetch(url, args.timeout), url, args.per_feed))
        except Exception as exc:
            rows.append({"feed": url, "date": "", "title": f"ERROR: {exc}", "link": ""})

    if args.out_file:
        lines = ["# AI RSS Brief", ""]
        lines.extend(f"- {r['date']} | {r['title']} | {r['link']}" for r in rows)
        with open(args.out_file, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines) + "\n")
    else:
        json.dump(rows, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
