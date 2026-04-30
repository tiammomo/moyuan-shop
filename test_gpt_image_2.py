#!/usr/bin/env python3
import argparse
import base64
import json
import os
import socket
import sys
import urllib.error
import urllib.request


DEFAULT_BASE_URL = "https://w.ciykj.cn/v1"
DEFAULT_PROMPT = "牛仔裤，白色背景，单色，简约，写实，高清，正面"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Minimal gpt-image-2 test script")
    parser.add_argument("--base-url", default=os.getenv("OPENAI_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY"))
    parser.add_argument("--model", default="gpt-image-2")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--size", default="1024x1024")
    parser.add_argument("--quality", default="low")
    parser.add_argument("--output-format", default="jpeg", choices=["png", "jpeg", "webp"])
    parser.add_argument("--output", default="test_gpt_image_2.jpg")
    parser.add_argument("--compression", type=int, default=50)
    parser.add_argument("--timeout", type=int, default=120, help="Request timeout in seconds. Use 0 to disable timeout.")
    return parser.parse_args()


def build_payload(args: argparse.Namespace) -> bytes:
    payload = {
        "model": args.model,
        "prompt": args.prompt,
        "size": args.size,
        "quality": args.quality,
        "output_format": args.output_format,
    }
    if args.output_format in {"jpeg", "webp"}:
        payload["output_compression"] = args.compression
    return json.dumps(payload).encode("utf-8")


def main() -> int:
    args = parse_args()
    if not args.api_key:
        print("Missing OPENAI_API_KEY or --api-key", file=sys.stderr)
        return 2

    url = args.base_url.rstrip("/") + "/images/generations"
    request = urllib.request.Request(
        url=url,
        data=build_payload(args),
        method="POST",
        headers={
            "Authorization": f"Bearer {args.api_key}",
            "Content-Type": "application/json",
        },
    )

    try:
        timeout = None if args.timeout == 0 else args.timeout
        timeout_label = "none" if timeout is None else f"{timeout}s"
        print(f"Requesting {url} with model={args.model}, timeout={timeout_label}")
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            request_id = response.headers.get("x-request-id", "")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"HTTP {exc.code}", file=sys.stderr)
        request_id = exc.headers.get("x-request-id", "")
        if request_id:
            print(f"x-request-id: {request_id}", file=sys.stderr)
        print(body, file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        return 1
    except TimeoutError as exc:
        print(f"Request timed out after {args.timeout}s: {exc}", file=sys.stderr)
        return 1
    except socket.timeout as exc:
        print(f"Request timed out after {args.timeout}s: {exc}", file=sys.stderr)
        return 1

    try:
        result = json.loads(body)
        image_base64 = result["data"][0]["b64_json"]
    except (KeyError, IndexError, json.JSONDecodeError) as exc:
        print(f"Unexpected response: {exc}", file=sys.stderr)
        print(body, file=sys.stderr)
        return 1

    image_bytes = base64.b64decode(image_base64)
    with open(args.output, "wb") as file:
        file.write(image_bytes)

    print(f"Saved image to {args.output}")
    if request_id:
        print(f"x-request-id: {request_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
