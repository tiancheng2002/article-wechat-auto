---
name: article-wechat-auto
description: Use when the user wants an end-to-end WeChat public account article workflow from latest AI news discovery through Markdown writing, cover image generation, one copyable HTML file, and optional WeChat draft creation.
---

# Article WeChat Auto

Run the complete AI-news-to-WeChat workflow. This is the orchestrator skill; use the sub-skills for each stage.

## Required Sub-Skills

- **article-search**: collect current AI news and recommend a lead topic.
- **article-writing**: turn the selected item into a structured Markdown article and review it.
- **article-cover-image**: generate and normalize a blue minimalist article cover image.
- **article-format**: convert Markdown into one WeChat-ready copyable HTML page.
- **article-publish**: optionally create a WeChat draft through the Official Account API.

## Workflow

1. Use `article-search` to collect current AI news. Prefer official sources and RSS.
2. Pick the strongest topic or ask the user to choose if multiple are equally strong.
3. Create a run folder under `article/YYYY-MM-DD_N`, where `N` increments for each run on the same date.
4. Use `article-writing` to draft Markdown with digest, opening, longer body, and conclusion. Do not add source/reference notes or a follow/attention line.
5. Review the Markdown for structure, digest length, body length, typos, grammar, and overclaiming.
6. Use `article-cover-image` to create `cover-source.png` and normalized `cover.jpg` in the run folder.
7. Use `article-format` to create one copyable WeChat HTML file.
8. Give the user the Markdown path, cover path, and copyable HTML path.
9. If the user explicitly wants API upload, use `article-publish --cover-image cover.jpg` to add the article to the draft box only.

## Defaults

- Topic domain: latest AI models, AI tools, Codex, Claude Code, Gemini, developer tools, and AI industry shifts.
- Writing style: clear technology commentary for WeChat readers.
- Format theme: restrained technology editorial layout.
- Cover theme: blue minimalist technology illustration with a short title.
- Publishing mode: draft box, not mass send.
- Output folder: `article/YYYY-MM-DD_N`, for example `article/2026-07-03_1`.

## Stop Points

Ask for confirmation before:

- selecting a topic when the user has not approved one and the choice materially changes the article angle;
- using WeChat API credentials;
- creating a draft in the official account;
- making any public or irreversible publishing action.

## One-Command Helper

The bundled script creates the output folder and prints the recommended sequence and file naming conventions:

```bash
python scripts/run_workflow.py --topic-hint "Codex 最新能力"
```

Use the script as an operator checklist; the agent still performs source verification, writing, image inspection, and editorial judgment.
