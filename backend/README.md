# Moyuan Shop Backend

FastAPI MVP backend for the ecommerce image-generation workflow.

Current behavior uses a mock image provider and does **not** call `gpt-image-2` directly.

## Setup

Using `uv`:

```bash
cd backend
uv venv
uv pip install -r requirements.txt
. .venv/bin/activate
uvicorn app.main:app --reload
```

Using standard Python, if `pip` is available:

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API base URL:

```text
http://localhost:8000/api
```

## Environment

Copy the example file for local development:

```bash
cp .env.example .env
```

Important defaults:

```text
MOYUAN_IMAGE_PROVIDER=mock
MOYUAN_STORAGE_DIR=storage
MOYUAN_DEFAULT_MODEL=gpt-image-2
MOYUAN_MAX_GENERATION_COUNT=4
```

`MOYUAN_IMAGE_PROVIDER=mock` must stay enabled until the real OpenAI-compatible provider is implemented.
`OPENAI_API_KEY` and `OPENAI_BASE_URL` are placeholders only right now and are not used by the mock provider.

Never put provider secrets in frontend env files. Frontend may only use public variables such as `NEXT_PUBLIC_API_URL`.

## MVP Endpoints

```text
GET  /api/health
GET  /api/settings/image-generation
POST /api/assets
GET  /api/assets/{asset_id}/file
POST /api/generation-tasks
GET  /api/generation-tasks/{task_id}
GET  /api/generation-tasks/{task_id}/results
```

## Mock Provider

The backend writes deterministic placeholder images to `backend/storage/generated/`.
It preserves the task lifecycle and metadata shape needed for the real `gpt-image-2` provider later.

## Configuration Reference

| Variable | Default | Description |
| --- | --- | --- |
| `MOYUAN_APP_NAME` | `moyuan-shop-api` | Service name returned by health check |
| `MOYUAN_APP_VERSION` | `0.1.0` | Service version |
| `MOYUAN_ENVIRONMENT` | `development` | `development`, `test`, or `production` |
| `MOYUAN_DEBUG` | `true` | Enables development behavior |
| `MOYUAN_API_PREFIX` | `/api` | API route prefix |
| `MOYUAN_CORS_ORIGINS` | localhost frontend origins | Allowed browser origins |
| `MOYUAN_STORAGE_DIR` | `storage` | Local file storage directory |
| `MOYUAN_PUBLIC_ASSET_BASE_URL` | empty | Optional absolute asset base URL for later deployments |
| `MOYUAN_IMAGE_PROVIDER` | `mock` | `mock` now, `openai` later |
| `MOYUAN_DEFAULT_MODEL` | `gpt-image-2` | Model name stored in task metadata |
| `MOYUAN_DEFAULT_SIZE` | `1024x1024` | Default output size |
| `MOYUAN_DEFAULT_QUALITY` | `low` | Default generation quality |
| `MOYUAN_DEFAULT_OUTPUT_FORMAT` | `jpeg` | Default output format |
| `MOYUAN_DEFAULT_OUTPUT_COMPRESSION` | `50` | JPEG/WebP compression setting |
| `MOYUAN_GENERATION_TIMEOUT_SECONDS` | `120` | Future provider timeout |
| `MOYUAN_MAX_GENERATION_COUNT` | `4` | Max images per task request |
| `MOYUAN_DATABASE_URL` | SQLite placeholder | Future database URL |
| `MOYUAN_REDIS_URL` | Redis placeholder | Future queue/cache URL |
| `OPENAI_BASE_URL` | proxy placeholder | Future provider base URL, currently unused |
| `OPENAI_API_KEY` | empty | Future provider key, currently unused |
