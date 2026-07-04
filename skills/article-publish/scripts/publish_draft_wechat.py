#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path
import sys
import urllib.parse
import urllib.request
import uuid


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = SCRIPT_DIR.parent / "wechat_publish_config.json"


def load_config(path):
    if not path:
        return {}

    config_path = Path(path).expanduser()
    if not config_path.is_absolute():
        config_path = Path.cwd() / config_path

    if not config_path.exists():
        if config_path == DEFAULT_CONFIG_PATH:
            return {}
        raise SystemExit(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid JSON config: {config_path} ({exc})") from exc

    if not isinstance(data, dict):
        raise SystemExit(f"Config must be a JSON object: {config_path}")
    return data


def first_value(*values):
    for value in values:
        if value not in (None, ""):
            return value
    return ""


def as_comment_flag(value, name):
    if value in (0, 1):
        return value
    if isinstance(value, str) and value.strip() in ("0", "1"):
        return int(value.strip())
    raise SystemExit(f"{name} must be 0 or 1.")


def get_json(url, timeout=30):
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def post_json(url, payload, timeout=30):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def post_multipart_file(url, field_name, file_path, mime_type, timeout=60):
    boundary = f"----CodexWechatBoundary{uuid.uuid4().hex}"
    path = Path(file_path)
    header = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{field_name}"; filename="{path.name}"\r\n'
        f"Content-Type: {mime_type}\r\n\r\n"
    ).encode("utf-8")
    footer = f"\r\n--{boundary}--\r\n".encode("utf-8")
    data = header + path.read_bytes() + footer
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def extract_wechat_content(html_text):
    start_marker = "<!-- WECHAT_CONTENT_START -->"
    end_marker = "<!-- WECHAT_CONTENT_END -->"
    start = html_text.find(start_marker)
    end = html_text.find(end_marker)
    if start != -1 and end != -1 and end > start:
        return html_text[start + len(start_marker):end].strip()
    return html_text


def image_mime_type(path):
    suffix = Path(path).suffix.lower()
    if suffix in (".jpg", ".jpeg"):
        return "image/jpeg"
    if suffix == ".png":
        return "image/png"
    if suffix == ".gif":
        return "image/gif"
    if suffix == ".bmp":
        return "image/bmp"
    raise SystemExit("Cover image must be JPG, JPEG, PNG, GIF, or BMP.")


def upload_image_material(access_token, image_path):
    path = Path(image_path).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    if not path.exists():
        raise SystemExit(f"Cover image not found: {path}")
    query = urllib.parse.urlencode({"access_token": access_token, "type": "image"})
    return post_multipart_file(
        f"https://api.weixin.qq.com/cgi-bin/material/add_material?{query}",
        "media",
        path,
        image_mime_type(path),
    )


def build_article_payload(title, author, digest, content, need_open_comment, only_fans_can_comment, thumb_media_id="", content_source_url=""):
    article = {
        "title": title,
        "author": author,
        "digest": digest,
        "content": content,
        "need_open_comment": need_open_comment,
        "only_fans_can_comment": only_fans_can_comment,
    }
    if thumb_media_id:
        article["thumb_media_id"] = thumb_media_id
    if content_source_url:
        article["content_source_url"] = content_source_url
    return {"articles": [article]}


def resolve_thumb_media_id(explicit_thumb_media_id, cover_image, configured_thumb_media_id, access_token):
    if explicit_thumb_media_id:
        return explicit_thumb_media_id, None
    if cover_image:
        upload_resp = upload_image_material(access_token, cover_image)
        uploaded_media_id = upload_resp.get("media_id", "")
        if not uploaded_media_id:
            return "", upload_resp
        return uploaded_media_id, upload_resp
    return configured_thumb_media_id, None


def main():
    parser = argparse.ArgumentParser(description="Create a WeChat Official Account draft article.")
    parser.add_argument(
        "--config",
        default=os.environ.get("WECHAT_PUBLISH_CONFIG", str(DEFAULT_CONFIG_PATH)),
        help="Path to JSON config. Defaults to the skill's wechat_publish_config.json.",
    )
    parser.add_argument("--title", required=True)
    parser.add_argument("--digest", required=True)
    parser.add_argument("--content-html", required=True)
    parser.add_argument("--author", default=None)
    parser.add_argument("--thumb-media-id", default=None)
    parser.add_argument("--cover-image", default="")
    parser.add_argument("--content-source-url", default=None)
    parser.add_argument("--need-open-comment", choices=("0", "1"), default=None)
    parser.add_argument("--only-fans-can-comment", choices=("0", "1"), default=None)
    args = parser.parse_args()

    config = load_config(args.config)

    appid = first_value(os.environ.get("WECHAT_APPID"), config.get("wechat_appid"))
    secret = first_value(os.environ.get("WECHAT_SECRET"), config.get("wechat_secret"))
    explicit_thumb_media_id = first_value(args.thumb_media_id)
    configured_thumb_media_id = first_value(os.environ.get("WECHAT_THUMB_MEDIA_ID"), config.get("thumb_media_id"))
    author = first_value(args.author, config.get("author"))
    content_source_url = first_value(args.content_source_url, config.get("content_source_url"))
    need_open_comment = as_comment_flag(
        first_value(args.need_open_comment, config.get("need_open_comment"), 0),
        "need_open_comment",
    )
    only_fans_can_comment = as_comment_flag(
        first_value(args.only_fans_can_comment, config.get("only_fans_can_comment"), 0),
        "only_fans_can_comment",
    )

    if not appid or not secret:
        raise SystemExit("Missing wechat_appid or wechat_secret. Fill wechat_publish_config.json or set WECHAT_APPID/WECHAT_SECRET.")

    with open(args.content_html, "r", encoding="utf-8") as f:
        content = extract_wechat_content(f.read())

    query = urllib.parse.urlencode({"grant_type": "client_credential", "appid": appid, "secret": secret})
    token_resp = get_json(f"https://api.weixin.qq.com/cgi-bin/token?{query}")
    token = token_resp.get("access_token")
    if not token:
        print(json.dumps(token_resp, ensure_ascii=False, indent=2))
        raise SystemExit("Failed to obtain WeChat access token.")

    thumb_media_id, upload_resp = resolve_thumb_media_id(
        explicit_thumb_media_id,
        args.cover_image,
        configured_thumb_media_id,
        token,
    )
    if upload_resp:
        if not thumb_media_id:
            print(json.dumps(upload_resp, ensure_ascii=False, indent=2))
            raise SystemExit("Failed to upload cover image material.")
        print(json.dumps({"uploaded_thumb_media_id": thumb_media_id}, ensure_ascii=False, indent=2))

    payload = build_article_payload(
        args.title,
        author,
        args.digest,
        content,
        need_open_comment,
        only_fans_can_comment,
        thumb_media_id=thumb_media_id,
        content_source_url=content_source_url,
    )

    resp = post_json(f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={urllib.parse.quote(token)}", payload)
    print(json.dumps(resp, ensure_ascii=False, indent=2))
    if resp.get("errcode", 0) not in (0, None):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
