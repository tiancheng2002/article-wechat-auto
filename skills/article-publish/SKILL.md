---
name: article-publish
description: Use when publishing or uploading a finished WeChat public account article and optional generated cover image to the official account draft box via the WeChat Official Account API for human review.
---

# Article Publish

Publish a finished article to the WeChat Official Account draft box, not directly to users. Treat this as a high-impact external action: verify credentials, request confirmation, and leave the draft for human review.

## Requirements

The WeChat draft API requires official account credentials. Prefer passing a generated cover image with `--cover-image`; the helper uploads it to WeChat permanent material first and uses the returned `media_id` as `thumb_media_id`.

Default config file:

- `wechat_publish_config.json`

Fill this file before publishing:

```json
{
  "wechat_appid": "your_appid",
  "wechat_secret": "your_appsecret",
  "thumb_media_id": "",
  "author": "author_name",
  "content_source_url": "",
  "need_open_comment": 0,
  "only_fans_can_comment": 0
}
```

The helper automatically reads `wechat_publish_config.json` from this skill directory. You can override it with `--config path/to/config.json` or the `WECHAT_PUBLISH_CONFIG` environment variable.

Environment variables still work as overrides:

- `WECHAT_APPID`
- `WECHAT_SECRET`
- `WECHAT_THUMB_MEDIA_ID`

## Workflow

1. Read the final HTML and digest.
2. Read `wechat_publish_config.json` and verify `wechat_appid` and `wechat_secret` are present.
3. Confirm the user wants to create a WeChat draft.
4. Verify current WeChat API requirements from official docs if anything is uncertain.
5. Run the helper script with `--cover-image article/YYYY-MM-DD_N/cover.jpg` when a generated cover exists.
6. Report returned `media_id`, uploaded cover `media_id`, and any warnings. Do not mass-send.

## Publish Helper

```bash
python scripts/publish_draft_wechat.py --title "Article title" --digest "Article digest" --content-html article_wechat.html --cover-image cover.jpg
```

The script obtains an access token, uploads `--cover-image` through `cgi-bin/material/add_material?type=image` when needed, then calls the draft add endpoint. Thumb media priority is explicit `--thumb-media-id`, uploaded `--cover-image`, then environment/config `thumb_media_id`. If all are empty, it omits `thumb_media_id`. It exits non-zero on API errors. It never prints `wechat_secret`.

## Safety Rules

- Never call mass-send APIs unless the user explicitly asks and confirms.
- Never print secrets.
- Use absolute file paths when reading final HTML and cover image.
- If the draft API or material API rejects content, preserve the response and explain the actionable fix.
