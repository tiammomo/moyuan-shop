# Moyuan Shop Backend

FastAPI MVP backend for the ecommerce image-generation workflow.

Current behavior can use the mock image provider or the OpenAI-compatible image provider.
Generated images are stored through the configured storage backend.

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

## MinIO Storage

Start the local MinIO service from the repository root:

```bash
docker compose up -d minio
```

MinIO endpoints:

```text
S3 API:  http://127.0.0.1:9000
Console: http://127.0.0.1:9001
User:    moyuan
Pass:    moyuan_minio_password
Bucket:  moyuan-images
```

The backend creates the bucket automatically on startup when `MOYUAN_STORAGE_BACKEND=minio`.
Generated images are saved under `generated/`, thumbnails under `thumbnails/`, and uploaded reference images under `assets/`.
The homepage reads featured images from `GET /api/assets/featured`, which lists the latest files in `generated/`.

## Environment

Copy the example file for local development:

```bash
cp .env.example .env
```

Important defaults:

```text
MOYUAN_IMAGE_PROVIDER=mock
MOYUAN_STORAGE_DIR=storage
MOYUAN_STORAGE_BACKEND=minio
MOYUAN_DEFAULT_MODEL=gpt-image-2
MOYUAN_MAX_GENERATION_COUNT=4
```

Use `MOYUAN_IMAGE_PROVIDER=mock` for local smoke tests, or `MOYUAN_IMAGE_PROVIDER=openai` for the OpenAI-compatible provider.
`OPENAI_API_KEY` and `OPENAI_BASE_URL` are only used by the `openai` provider.

Never put provider secrets in frontend env files. Frontend may only use public variables such as `NEXT_PUBLIC_API_URL`.

## MVP Endpoints

```text
GET  /api/health
GET  /api/settings/image-generation
POST /api/assets
GET  /api/assets/{asset_id}/file
GET  /api/assets/featured
GET  /api/assets/file?storage_key=generated/{filename}
POST /api/generation-tasks
GET  /api/generation-tasks/{task_id}
GET  /api/generation-tasks/{task_id}/results
```

## Mock Provider

With local storage, the backend writes generated images to `backend/storage/generated/` and thumbnails to `backend/storage/thumbnails/`.
With MinIO storage, it writes the same logical keys to the configured bucket.
Use `/api/assets/{asset_id}/file?download=1` when the frontend needs a browser download flow.
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
| `MOYUAN_STORAGE_BACKEND` | `local` | `local` or `minio` |
| `MOYUAN_PUBLIC_ASSET_BASE_URL` | empty | Optional absolute asset base URL for later deployments |
| `MOYUAN_MINIO_ENDPOINT` | `127.0.0.1:9000` | MinIO S3 API endpoint |
| `MOYUAN_MINIO_ACCESS_KEY` | `moyuan` | MinIO access key |
| `MOYUAN_MINIO_SECRET_KEY` | `moyuan_minio_password` | MinIO secret key |
| `MOYUAN_MINIO_BUCKET` | `moyuan-images` | Bucket for image assets |
| `MOYUAN_MINIO_SECURE` | `false` | Use HTTPS for MinIO |
| `MOYUAN_IMAGE_PROVIDER` | `mock` | `mock` now, `openai` later |
| `MOYUAN_DEFAULT_MODEL` | `gpt-image-2` | Model name stored in task metadata |
| `MOYUAN_DEFAULT_SIZE` | `1024x1024` | Default output size |
| `MOYUAN_DEFAULT_QUALITY` | `low` | Default generation quality |
| `MOYUAN_DEFAULT_OUTPUT_FORMAT` | `jpeg` | Default output format |
| `MOYUAN_DEFAULT_OUTPUT_COMPRESSION` | `50` | JPEG/WebP compression setting |
| `MOYUAN_GENERATION_TIMEOUT_SECONDS` | `900` | Upstream image provider timeout for long-running generations |
| `MOYUAN_MAX_GENERATION_COUNT` | `4` | Max images per task request |
| `MOYUAN_DATABASE_URL` | SQLite placeholder | Future database URL |
| `MOYUAN_REDIS_URL` | Redis placeholder | Future queue/cache URL |
| `OPENAI_BASE_URL` | proxy placeholder | Future provider base URL, currently unused |
| `OPENAI_API_KEY` | empty | Future provider key, currently unused |
