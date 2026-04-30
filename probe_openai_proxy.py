#!/usr/bin/env python3
import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request


DEFAULT_BASE_URL = "https://w.ciykj.cn/v1"
DEFAULT_IMAGE_PROMPT = "A tiny boy  on a wooden table, soft daylight"
DEFAULT_CHAT_PROMPT = "Reply with exactly OK."
PREFERRED_CHAT_MODELS = [
    "gpt-5.4-mini",
    "gpt-5.4",
    "gpt-5.2",
    "gpt-5.5",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probe an OpenAI-compatible proxy across models, chat, and images"
    )
    parser.add_argument("--base-url", default=os.getenv("OPENAI_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY"))
    parser.add_argument("--chat-model", default=None)
    parser.add_argument("--image-model", default="gpt-image-2")
    parser.add_argument("--chat-prompt", default=DEFAULT_CHAT_PROMPT)
    parser.add_argument("--image-prompt", default=DEFAULT_IMAGE_PROMPT)
    parser.add_argument("--image-size", default="1024x1024")
    parser.add_argument("--image-quality", default="low")
    parser.add_argument("--image-output-format", default="jpeg", choices=["png", "jpeg", "webp"])
    parser.add_argument("--image-output", default="probe_gpt_image_2.jpg")
    parser.add_argument("--image-compression", type=int, default=50)
    parser.add_argument("--skip-chat", action="store_true")
    parser.add_argument("--skip-images", action="store_true")
    parser.add_argument("--timeout", type=int, default=120)
    return parser.parse_args()


def make_request(base_url: str, api_key: str, method: str, path: str, payload: dict | None, timeout: int) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url=base_url.rstrip("/") + path,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    started_at = time.time()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            return {
                "ok": True,
                "status": response.status,
                "body": body,
                "request_id": response.headers.get("x-request-id", ""),
                "elapsed_ms": int((time.time() - started_at) * 1000),
            }
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return {
            "ok": False,
            "status": exc.code,
            "body": body,
            "request_id": exc.headers.get("x-request-id", ""),
            "elapsed_ms": int((time.time() - started_at) * 1000),
        }
    except urllib.error.URLError as exc:
        return {
            "ok": False,
            "status": "network_error",
            "body": str(exc),
            "request_id": "",
            "elapsed_ms": int((time.time() - started_at) * 1000),
        }


def print_probe(name: str, result: dict, extra: str = "") -> None:
    status = "OK" if result["ok"] else "FAIL"
    line = f"[{status}] {name}: status={result['status']} time={result['elapsed_ms']}ms"
    if result["request_id"]:
        line += f" request_id={result['request_id']}"
    if extra:
        line += f" {extra}"
    print(line)


def load_json(body: str) -> dict | list | None:
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return None


def choose_chat_model(model_ids: list[str], requested: str | None) -> str | None:
    if requested:
        return requested
    for model in PREFERRED_CHAT_MODELS:
        if model in model_ids:
            return model
    for model in model_ids:
        if model.startswith("gpt-") and not model.startswith("gpt-image-"):
            return model
    return None


def probe_models(args: argparse.Namespace) -> tuple[dict, list[str]]:
    result = make_request(args.base_url, args.api_key, "GET", "/models", None, args.timeout)
    model_ids: list[str] = []
    payload = load_json(result["body"])
    if isinstance(payload, dict):
        data = payload.get("data", [])
        if isinstance(data, list):
            model_ids = [item.get("id", "") for item in data if isinstance(item, dict) and item.get("id")]
    extra = ""
    if model_ids:
        preview = ",".join(model_ids[:5])
        extra = f"models={len(model_ids)} preview={preview}"
    print_probe("models", result, extra)
    if not result["ok"]:
        print(result["body"])
    return result, model_ids


def probe_chat(args: argparse.Namespace, chat_model: str) -> dict:
    payload = {
        "model": chat_model,
        "messages": [{"role": "user", "content": args.chat_prompt}],
        "max_tokens": 10,
        "temperature": 0,
    }
    result = make_request(args.base_url, args.api_key, "POST", "/chat/completions", payload, args.timeout)
    extra = f"model={chat_model}"
    parsed = load_json(result["body"])
    if isinstance(parsed, dict):
        try:
            content = parsed["choices"][0]["message"]["content"]
            compact = " ".join(str(content).split())
            extra += f" reply={compact[:40]}"
        except (KeyError, IndexError, TypeError):
            pass
    print_probe("chat", result, extra)
    if not result["ok"]:
        print(result["body"])
    return result


def probe_images(args: argparse.Namespace) -> dict:
    payload = {
        "model": args.image_model,
        "prompt": args.image_prompt,
        "size": args.image_size,
        "quality": args.image_quality,
        "output_format": args.image_output_format,
    }
    if args.image_output_format in {"jpeg", "webp"}:
        payload["output_compression"] = args.image_compression

    result = make_request(args.base_url, args.api_key, "POST", "/images/generations", payload, args.timeout)
    extra = f"model={args.image_model}"
    parsed = load_json(result["body"])
    if isinstance(parsed, dict):
        try:
            image_base64 = parsed["data"][0]["b64_json"]
            image_bytes = base64.b64decode(image_base64)
            with open(args.image_output, "wb") as file:
                file.write(image_bytes)
            extra += f" saved={args.image_output}"
        except (KeyError, IndexError, TypeError, ValueError):
            pass
    print_probe("images", result, extra)
    if not result["ok"]:
        print(result["body"])
    return result


def main() -> int:
    args = parse_args()
    if not args.api_key:
        print("Missing OPENAI_API_KEY or --api-key", file=sys.stderr)
        return 2

    _, model_ids = probe_models(args)
    exit_code = 0

    if not args.skip_chat:
        chat_model = choose_chat_model(model_ids, args.chat_model)
        if not chat_model:
            print("[FAIL] chat: no usable chat model found from /models")
            exit_code = 1
        else:
            chat_result = probe_chat(args, chat_model)
            if not chat_result["ok"]:
                exit_code = 1

    if not args.skip_images:
        image_result = probe_images(args)
        if not image_result["ok"]:
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
