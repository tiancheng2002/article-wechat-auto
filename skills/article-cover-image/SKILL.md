---
name: article-cover-image
description: Use when generating or preparing a WeChat public account article cover image for an AI news article, especially blue minimalist illustration covers saved into article/YYYY-MM-DD_N folders and normalized for WeChat draft upload.
---

# Article Cover Image

Generate and prepare a WeChat article cover image for the current article run folder.

## Workflow

1. Read the article Markdown title and infer a short cover title of 6-10 Chinese characters.
2. Use the built-in `imagegen` skill/tool to generate a blue minimalist technology illustration that reflects the article title.
3. Save the generated original as `cover-source.png` in the current `article/YYYY-MM-DD_N` folder.
4. Run the normalizer to create `cover.jpg` in the same folder:

```bash
python scripts/normalize_cover_image.py --input cover-source.png --output cover.jpg
```

5. Use `cover.jpg` as the `--cover-image` input for `article-publish`.

## Default Cover Spec

- Size: 900x383.
- Palette: blue-first, aligned with the article HTML style.
- Style: clean, simple editorial illustration for AI and technology news.
- Text: include a short title, not the full article title.
- Avoid: logos, watermarks, dense UI screenshots, tiny text, photorealistic people, cluttered backgrounds.

## Prompt Template

Use built-in `imagegen` with a prompt like:

```text
Use case: ads-marketing
Asset type: WeChat public account article cover
Primary request: blue minimalist editorial illustration for an AI news article
Subject: {article title}
Text (verbatim): "{short cover title}"
Style/medium: clean vector-like digital illustration, modern technology editorial style
Composition/framing: wide 900:383 cover composition, central readable visual metaphor, generous margins
Color palette: deep blue, bright blue, white, subtle cyan accents
Constraints: no logo, no watermark, no photorealistic people, no dense small text
```

## Quality Rules

- Inspect the generated image before publishing.
- If the short title text is misspelled or unreadable, regenerate once with fewer characters.
- Always keep the normalized `cover.jpg` in the same run folder as the Markdown and HTML.
