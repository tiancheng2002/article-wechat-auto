#!/usr/bin/env python3
import argparse
import html
import os
import re


FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Hiragino Sans GB','Microsoft YaHei',Arial,sans-serif"


def enc(text):
    return html.escape(text, quote=True)


def p(text):
    return f'<p style="margin:0 0 16px;font-size:16px;line-height:2;color:#374151;">{enc(text)}</p>'


def extract_title(markdown):
    markdown = markdown.lstrip("\ufeff")
    match = re.search(r"(?m)^#\s+(.+)$", markdown)
    return match.group(1).strip() if match else "微信复制助手"


def convert(markdown):
    markdown = markdown.lstrip("\ufeff")
    lines = markdown.splitlines()
    h2_total = len(re.findall(r"(?m)^##\s+", markdown))
    h2_index = 0
    body_no = 0
    inside_digest = False
    inside_conclusion = False
    parts = []

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        if line == "---":
            parts.append('<section style="margin:24px 0;border-top:1px solid #e5e7eb;height:1px;line-height:1px;"></section>')
            continue

        if re.match(r"^#\s+(.+)", line):
            continue

        m = re.match(r"^##\s+(.+)", line)
        if m:
            if inside_digest or inside_conclusion:
                parts.append("</section>")
                inside_digest = False
                inside_conclusion = False

            h2_index += 1
            heading = enc(m.group(1))

            if h2_index == 1:
                parts.append(
                    '<section style="margin:0 0 28px;padding:18px 18px 16px;background:#eff6ff;border-left:4px solid #2563eb;border-radius:8px;">'
                    '<p style="margin:0 0 8px;font-size:14px;line-height:1.6;color:#1d4ed8;font-weight:700;">摘要</p>'
                )
                inside_digest = True
            elif h2_index == 2:
                continue
            elif h2_index == h2_total:
                parts.append(
                    '<section style="margin:32px 0 20px;padding:20px 18px;background:#f9fafb;border-top:3px solid #2563eb;border-radius:8px;">'
                    f'<h2 style="margin:0 0 14px;color:#111827;font-size:21px;line-height:1.45;font-weight:800;letter-spacing:0;">{heading}</h2>'
                )
                inside_conclusion = True
            else:
                body_no += 1
                parts.append(
                    '<section style="margin:30px 0 18px;">'
                    f'<p style="margin:0 0 8px;font-size:13px;line-height:1.5;color:#2563eb;font-weight:700;">{body_no:02d}</p>'
                    f'<h2 style="margin:0;padding:0 0 10px;border-bottom:2px solid #dbeafe;color:#111827;font-size:21px;line-height:1.45;font-weight:800;letter-spacing:0;">{heading}</h2>'
                    '</section>'
                )
            continue

        if re.search(r"https?://", line):
            parts.append(f'<p style="margin:0 0 6px;font-size:13px;line-height:1.8;color:#6b7280;word-break:break-all;">{enc(line)}</p>')
        elif h2_index >= h2_total and len(line) <= 32:
            parts.append(f'<p style="margin:0;padding:14px 16px;background:#ffffff;border-left:4px solid #111827;color:#111827;font-size:18px;line-height:1.9;font-weight:800;">{enc(line)}</p>')
        else:
            parts.append(p(line))

    if inside_digest or inside_conclusion:
        parts.append("</section>")

    article = (
        f'<section id="wechatArticle" style="box-sizing:border-box;max-width:680px;margin:0 auto;padding:28px 18px 40px;background:#ffffff;color:#1f2937;font-family:{FONT};">\n'
        + "\n".join(parts)
        + "\n</section>"
    )
    return article


def helper_html(article, title):
    script = """
<script>
async function copyArticle(){
  const article=document.getElementById('wechatArticle');
  const status=document.getElementById('copyStatus');
  try{
    await navigator.clipboard.write([new ClipboardItem({
      'text/html': new Blob([article.outerHTML],{type:'text/html'}),
      'text/plain': new Blob([article.innerText],{type:'text/plain'})
    })]);
    status.innerText='已复制富文本。去微信公众号平台正文区粘贴即可。';
    status.style.color='#16a34a';
  }catch(e){
    const r=document.createRange(); r.selectNode(article);
    const s=window.getSelection(); s.removeAllRanges(); s.addRange(r);
    document.execCommand('copy');
    status.innerText='正文已选中。如未复制成功，请按 Ctrl+C。';
    status.style.color='#dc2626';
  }
}
</script>
"""
    toolbar = (
        f'<section style="position:sticky;top:0;z-index:10;box-sizing:border-box;max-width:760px;margin:0 auto 16px;padding:14px 16px;background:#ffffff;border-bottom:1px solid #e5e7eb;box-shadow:0 8px 24px rgba(15,23,42,.08);font-family:{FONT};">'
        '<p style="margin:0 0 10px;font-size:14px;line-height:1.7;color:#374151;">点击按钮复制渲染后的富文本，再粘贴到公众号编辑器正文区。</p>'
        '<button onclick="copyArticle()" style="padding:10px 16px;border:0;border-radius:6px;background:#2563eb;color:#fff;font-size:15px;font-weight:700;cursor:pointer;">复制到微信后台</button>'
        '<span id="copyStatus" style="margin-left:10px;font-size:13px;color:#6b7280;">不要复制 HTML 源码。</span>'
        '</section>'
    )
    return (
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>{enc(title)}</title></head>'
        f'<body style="margin:0;background:#eef2f7;">{toolbar}<!-- WECHAT_CONTENT_START -->{article}<!-- WECHAT_CONTENT_END -->{script}</body></html>'
    )


def main():
    parser = argparse.ArgumentParser(description="Convert Markdown into WeChat-compatible HTML.")
    parser.add_argument("markdown")
    parser.add_argument("--out-html", default="")
    parser.add_argument("--out-copy-helper", default="", help=argparse.SUPPRESS)
    args = parser.parse_args()

    with open(args.markdown, "r", encoding="utf-8") as f:
        markdown = f.read()

    out_html = args.out_html or args.out_copy_helper or os.path.splitext(args.markdown)[0] + ".wechat.html"

    title = extract_title(markdown)
    article = convert(markdown)
    with open(out_html, "w", encoding="utf-8", newline="\n") as f:
        f.write(helper_html(article, title))

    print(f"Copyable HTML: {out_html}")


if __name__ == "__main__":
    main()
