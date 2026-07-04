---
name: article-search
description: Use when searching, browsing, RSS-fetching, or collecting current AI news for article topics, especially latest AI models, AI tools, Codex, Claude Code, Gemini, developer tools, or AI industry updates.
---

# Article Search

Collect recent AI news for a publishable article brief. Prefer official sources, then credible media/RSS feeds, and always verify time-sensitive claims.

## Workflow

1. Confirm the article angle if the user gives one; otherwise gather 5-8 recent AI items.
2. Use web search or RSS. For OpenAI product claims, prefer official OpenAI sources.
3. Record title, date, source, URL, one-sentence summary, and why readers should care.
4. Cross-check high-impact claims against official pages when possible.
5. Output a shortlist and recommend the strongest lead story.

## RSS Helper

Run the bundled helper when RSS collection is useful:

```bash
python scripts/fetch_ai_news_rss.py --out-file ai-news-brief.md
```

Default feeds include OpenAI, Google AI, TechCrunch AI, The Verge AI, Hugging Face, MIT Technology Review AI, and The Decoder. Add feeds with `--feed-url`.

## Output Shape

For each item:

- `标题`
- `日期`
- `来源`
- `链接`
- `摘要`
- `选题价值`

End with `推荐主选题` and explain the editorial reason in 2-4 sentences.

## Quality Rules

- Do not present unstable facts from memory.
- Use absolute dates.
- Distinguish official announcements from media reports.
- Avoid clickbait. Keep article-publisher tone: clear, useful, and calm.
