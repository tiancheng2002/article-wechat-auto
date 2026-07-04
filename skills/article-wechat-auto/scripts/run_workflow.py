#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re


def safe_name(text):
    text = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", text, flags=re.UNICODE).strip("-")
    return text or "ai-news"


def main():
    parser = argparse.ArgumentParser(description="Print the recommended WeChat article workflow files.")
    parser.add_argument("--topic-hint", default="latest AI news")
    parser.add_argument("--work-dir", default=os.getcwd())
    parser.add_argument("--article-dir", default="article")
    args = parser.parse_args()

    date = dt.date.today().isoformat()
    root = Path(args.work_dir).resolve()
    article_root = Path(args.article_dir)
    if not article_root.is_absolute():
        article_root = root / article_root
    article_root.mkdir(parents=True, exist_ok=True)

    seq = 1
    while (article_root / f"{date}_{seq}").exists():
        seq += 1
    output_dir = article_root / f"{date}_{seq}"
    output_dir.mkdir(parents=True, exist_ok=False)

    stem = safe_name(args.topic_hint)
    result = {
        "topic_hint": args.topic_hint,
        "output_dir": str(output_dir),
        "brief_file": str(output_dir / "news-brief.md"),
        "markdown_file": str(output_dir / f"{stem}.md"),
        "cover_source_file": str(output_dir / "cover-source.png"),
        "cover_image_file": str(output_dir / "cover.jpg"),
        "html_file": str(output_dir / f"{stem}-wechat.html"),
        "workflow": [
            "Use article-search to gather and verify current AI news.",
            "Use article-writing to create and review the Markdown article.",
            "Use article-cover-image to generate cover-source.png and normalize cover.jpg.",
            "Use article-format to create one copyable WeChat HTML file.",
            "Use article-publish with --cover-image cover.jpg only after explicit confirmation and valid credentials.",
        ],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
