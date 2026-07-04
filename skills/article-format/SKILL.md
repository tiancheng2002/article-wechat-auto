---
name: article-format
description: Use when converting a Markdown article into one WeChat public account copyable HTML page, visual formatting, typography, paragraph styling, layout themes, or WeChat editor paste-ready content.
---

# Article Format

Convert a Markdown article into one WeChat-editor-friendly HTML copy page. The user must copy rendered rich text from the browser, not raw HTML source.

## Workflow

1. Read the Markdown file.
2. Choose a restrained theme suitable for the article: default is technology commentary.
3. Generate one inline-style HTML file that contains rendered article content and a copy button.
4. If needed, start a local static server and give the user the URL.

## Converter

Run:

```bash
python scripts/convert_markdown_to_wechat_html.py article.md --out-html article_wechat.html
```

Then open the HTML file in a browser. Click the copy button and paste into the WeChat editor body.

## WeChat Copy Rule

Never tell the user to paste raw HTML into WeChat. WeChat will show the source text. The correct path is:

1. Render HTML in a browser.
2. Copy rendered rich text or use Clipboard API.
3. Paste into WeChat editor.

## Quality Rules

- Prefer inline CSS.
- Avoid external stylesheets and scripts except the local copy button.
- Use mobile-friendly font sizes: body around 15-16px, H2 around 20-22px.
- Keep paragraph spacing generous.
- Do not render the Markdown H1 inside the article body; WeChat already displays the article title separately.
- Do not add source/reference sections or final follow/attention lines that are absent from the Markdown.
