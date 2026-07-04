---
name: article-writing
description: Use when turning one AI news item or brief into a WeChat public account Markdown article, including title, digest, structured opening, longer mobile-friendly body, conclusion, and editorial proofreading.
---

# Article Writing

Write a publishable WeChat article from one selected AI news item. The target reader is a public-account reader who wants useful AI trend interpretation, not a raw translation.

## Required Structure

1. Title
2. `## 摘要`: 80-128 Chinese characters
3. `## 开头`: 2-3 short paragraphs
4. Body with 4-6 numbered or descriptive sections
5. `## 结尾`: 1-2 paragraphs plus a memorable sentence

Do not add a final source/reference section. Do not add the line `觉得有用？点个关注，持续获取优质内容。`

## Opening Styles

Choose one:

- 提问式: pain point or trend question
- 场景式: small story or conversation
- 数据式: trend/data-led topic
- 金句式: opinion article
- 直给式: tutorial/list article

## Writing Rules

- Target 1200-1800 Chinese characters for the article body, excluding title and digest.
- Keep paragraphs mobile-friendly: usually 3-5 lines in WeChat.
- Use transition sentences between sections.
- Explain why the news matters, not only what happened.
- Use absolute dates for current events.
- Verify facts from sources during research, but do not append source URLs or reference notes to the final Markdown.
- Do not invent claims absent from the source.

## Review

After drafting, run:

```bash
python scripts/review_article_markdown.py article.md
```

Fix any reported structure, digest length, body length, forbidden source/reference ending, or forbidden follow line. Then manually review for grammar, repeated wording, awkward transitions, typo-prone names, and overclaiming.
