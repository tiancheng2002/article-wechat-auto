#!/usr/bin/env python3
import argparse
import re
import sys


def main():
    parser = argparse.ArgumentParser(description="Review a WeChat article Markdown draft.")
    parser.add_argument("path")
    args = parser.parse_args()

    with open(args.path, "r", encoding="utf-8") as f:
        content = f.read()

    issues = []
    if not re.search(r"(?m)^#\s+.+", content):
        issues.append("Missing H1 title.")

    h2_matches = list(re.finditer(r"(?m)^##\s+.+$", content))
    if len(h2_matches) < 6:
        issues.append(f"Only {len(h2_matches)} H2 sections found; expected digest, opening, 4+ body sections, and conclusion.")

    if len(h2_matches) >= 2:
        start = h2_matches[0].end()
        end = h2_matches[1].start()
        digest = re.sub(r"[\r\n]", "", content[start:end]).strip()
        if len(digest) < 80 or len(digest) > 128:
            issues.append(f"Digest length is {len(digest)}, expected 80-128 Chinese characters.")
    else:
        issues.append("Could not parse digest from first H2 section.")

    body_for_length = content[h2_matches[1].start():] if len(h2_matches) >= 2 else content
    plain_body = re.sub(r"(?m)^#.*$", "", body_for_length)
    plain_body = re.sub(r"(?m)^##.*$", "", plain_body)
    plain_body = re.sub(r"https?://\S+", "", plain_body)
    chinese_chars = re.findall(r"[\u4e00-\u9fff]", plain_body)
    if len(chinese_chars) < 1200:
        issues.append(f"Article body is {len(chinese_chars)} Chinese characters; expected at least 1200.")
    if re.search(r"(?m)^##\s*(来源|参考|参考来源|资料来源|Source|Sources)\b", content, re.IGNORECASE):
        issues.append("Remove the final source/reference section from the publishable Markdown.")
    if re.search(r"https?://", content):
        issues.append("Remove source URLs from the publishable Markdown; keep sources in research notes only.")
    if "觉得有用？点个关注" in content or "持续获取优质内容" in content:
        issues.append("Remove the follow/attention call-to-action line.")
    if not content.strip():
        issues.append("Article is empty after trimming.")
    if re.search(r"TODO|TBD", content):
        issues.append("Contains placeholder text.")

    if issues:
        print("FAIL: Review issues found:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("PASS: Markdown article structure looks ready for editorial review.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
