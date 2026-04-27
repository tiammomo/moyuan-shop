# Moyuan Shop 启动说明

这是一个电商 AI 生图项目，包含三个主要部分：

- `frontend/`：Next.js 前端页面
- `backend/`：FastAPI 后端接口和生图任务
- `minio`：Docker 启动的对象存储，用来保存上传图片、生成图片和缩略图

## 1. 端口说明

默认端口如下：

| 服务 | 地址 | 用途 |
| --- | --- | --- |
| 前端 | `http://127.0.0.1:3000` | 浏览器打开的网站 |
| 后端 API | `http://127.0.0.1:8000/api` | 前端调用的接口 |
| MinIO S3 API | `http://127.0.0.1:9000` | 后端连接的对象存储接口 |
| MinIO 控制台 | `http://127.0.0.1:9001` | 浏览器查看桶和文件 |

MinIO 控制台账号：

```text
用户名：moyuan
密码：moyuan_minio_password
桶名：moyuan-images
```

## 2. 第一次启动前准备

进入项目根目录：

```bash
cd /mnt/c/Users/caiyu/Desktop/e-commerce/moyuan-shop
```

### 2.1 启动 MinIO

MinIO 用 Docker 启动：

```bash
docker compose up -d minio
```

查看状态：

```bash
docker compose ps
```

看到 `moyuan-shop-minio-1` 状态是 `healthy` 就可以。

打开 MinIO 控制台：

```text
http://127.0.0.1:9001
```

后端启动时会自动创建 `moyuan-images` 桶。如果控制台里一开始没有桶，先启动后端再刷新。

### 2.2 准备后端环境

进入后端目录：

```bash
cd backend
```

如果还没有 `.env`，复制一份：

```bash
cp .env.example .env
```

安装依赖。项目使用 `uv` 创建的虚拟环境时，推荐这样：

```bash
uv venv
uv pip install -r requirements.txt
```

如果已经有 `.venv`，只需要补依赖：

```bash
uv pip install -r requirements.txt
```

如果你的系统使用普通 Python venv，也可以：

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

确认 `backend/.env` 里至少有这些存储配置：

```env
MOYUAN_STORAGE_BACKEND=minio
MOYUAN_MINIO_ENDPOINT=127.0.0.1:9000
MOYUAN_MINIO_ACCESS_KEY=moyuan
MOYUAN_MINIO_SECRET_KEY=moyuan_minio_password
MOYUAN_MINIO_BUCKET=moyuan-images
MOYUAN_MINIO_SECURE=false
```

如果要用真实生图 provider，确认：

```env
MOYUAN_IMAGE_PROVIDER=openai
OPENAI_BASE_URL=你的 OpenAI 兼容接口地址
OPENAI_API_KEY=你的 key
```

如果只是本地测试，不想消耗真实接口，可以改成：

```env
MOYUAN_IMAGE_PROVIDER=mock
```

### 2.3 准备前端依赖

进入前端目录：

```bash
cd ../frontend
```

安装依赖：

```bash
npm install
```

如果 `node_modules` 已经存在，可以跳过这一步。

## 3. 日常启动顺序

每次开发时，建议开三个终端。

### 终端 1：启动 MinIO

在项目根目录执行：

```bash
cd /mnt/c/Users/caiyu/Desktop/e-commerce/moyuan-shop
docker compose up -d minio
```

确认：

```bash
docker compose ps
```

### 终端 2：启动后端

在项目根目录执行：

```bash
cd /mnt/c/Users/caiyu/Desktop/e-commerce/moyuan-shop/backend
./.venv/bin/uvicorn app.main:app --reload
```

后端默认地址：

```text
http://127.0.0.1:8000
```

检查健康状态：

```bash
curl http://127.0.0.1:8000/api/health
```

检查首页精选图接口：

```bash
curl http://127.0.0.1:8000/api/assets/featured?limit=12
```

刚开始桶里没有生成图时，返回类似：

```json
{"data":[]}
```

这是正常的。生成图片成功后，这里会返回 MinIO 里的图片列表。

### 终端 3：启动前端

在项目根目录执行：

```bash
cd /mnt/c/Users/caiyu/Desktop/e-commerce/moyuan-shop/frontend
npm run dev -- --hostname 127.0.0.1 --port 3000
```

浏览器打开：

```text
http://127.0.0.1:3000
```

正常情况下不用手动设置 `NEXT_PUBLIC_API_URL`，因为前端默认会请求：

```text
http://localhost:8000
```

也就是默认后端地址。

只有当后端不是 `8000` 端口时，才需要显式告诉前端。例如后端跑在 `38110`：

```bash
NEXT_PUBLIC_API_URL=http://127.0.0.1:38110 npm run dev -- --hostname 127.0.0.1 --port 3000
```

## 4. 完整的一组启动命令

最常用版本：

```bash
cd /mnt/c/Users/caiyu/Desktop/e-commerce/moyuan-shop
docker compose up -d minio
```

```bash
cd /mnt/c/Users/caiyu/Desktop/e-commerce/moyuan-shop/backend
./.venv/bin/uvicorn app.main:app --reload
```

```bash
cd /mnt/c/Users/caiyu/Desktop/e-commerce/moyuan-shop/frontend
npm run dev -- --hostname 127.0.0.1 --port 3000
```

然后打开：

```text
http://127.0.0.1:3000
```

## 5. 图片保存和首页展示逻辑

当前图片存储逻辑：

| 图片类型 | MinIO 路径 |
| --- | --- |
| 上传的商品图 / 参考图 | `assets/...` |
| 生成图 | `generated/...` |
| 缩略图 | `thumbnails/...` |

每次生成任务成功后：

1. 后端拿到模型返回的图片 bytes。
2. 后端把生成图保存到 MinIO 的 `generated/`。
3. 后端生成缩略图，保存到 MinIO 的 `thumbnails/`。
4. 前端结果页通过 `/api/assets/{asset_id}/file` 渲染图片。
5. 首页通过 `/api/assets/featured` 从 MinIO 的 `generated/` 读取最新图片。
6. 如果 MinIO 里还没有生成图，首页会显示静态精选案例兜底。

相关接口：

```text
GET /api/assets/featured?limit=12
GET /api/assets/file?storage_key=generated/{filename}
GET /api/assets/{asset_id}/file
```

## 6. 常见问题

### 6.1 前端启动报 `EADDRINUSE: address already in use 127.0.0.1:3000`

说明 `3000` 端口已经被占用了。

最快解决：换端口启动：

```bash
npm run dev -- --hostname 127.0.0.1 --port 3001
```

然后打开：

```text
http://127.0.0.1:3001
```

如果想关掉占用 `3000` 的进程，在 WSL 里查：

```bash
lsof -iTCP:3000 -sTCP:LISTEN -n -P
```

看到 PID 后：

```bash
kill PID
```

如果还停不掉：

```bash
kill -9 PID
```

如果 WSL 查不到，但仍然提示占用，可能是 Windows 侧占用了端口。用 PowerShell：

```powershell
netstat -ano | findstr :3000
taskkill /PID 进程ID /F
```

### 6.2 后端启动时报 MinIO 连接失败

先确认 MinIO 是否启动：

```bash
docker compose ps
```

如果没有启动：

```bash
docker compose up -d minio
```

确认 `backend/.env`：

```env
MOYUAN_STORAGE_BACKEND=minio
MOYUAN_MINIO_ENDPOINT=127.0.0.1:9000
MOYUAN_MINIO_ACCESS_KEY=moyuan
MOYUAN_MINIO_SECRET_KEY=moyuan_minio_password
MOYUAN_MINIO_BUCKET=moyuan-images
MOYUAN_MINIO_SECURE=false
```

### 6.3 首页没有显示 MinIO 图片

先检查精选图接口：

```bash
curl http://127.0.0.1:8000/api/assets/featured?limit=12
```

如果返回：

```json
{"data":[]}
```

说明 MinIO 的 `generated/` 里还没有生成图。先去前端创建一次生成任务，成功后刷新首页。

也可以登录 MinIO 控制台查看：

```text
http://127.0.0.1:9001
```

进入 `moyuan-images` 桶，看 `generated/` 下是否有图片。

### 6.4 前端请求不到后端

确认后端是否在 `8000`：

```bash
curl http://127.0.0.1:8000/api/health
```

如果后端不是 `8000`，启动前端时需要指定：

```bash
NEXT_PUBLIC_API_URL=http://127.0.0.1:你的后端端口 npm run dev -- --hostname 127.0.0.1 --port 3000
```

### 6.5 后端提示缺少 `minio` 包

进入后端目录安装依赖：

```bash
cd /mnt/c/Users/caiyu/Desktop/e-commerce/moyuan-shop/backend
uv pip install -r requirements.txt
```

如果使用普通 pip：

```bash
. .venv/bin/activate
pip install -r requirements.txt
```

## 7. 停止服务

停止前端或后端：

```text
在对应终端按 Ctrl+C
```

停止 MinIO 容器：

```bash
docker compose stop minio
```

停止并删除 MinIO 容器，但保留数据卷：

```bash
docker compose down
```

如果要连 MinIO 数据卷也删除，谨慎使用：

```bash
docker compose down -v
```

`-v` 会删除 MinIO 里的图片数据。

## 8. 开发验证命令

后端语法检查：

```bash
python3 -m compileall backend/app
```

前端类型检查：

```bash
cd frontend
npx tsc --noEmit
```

前端生产构建：

```bash
cd frontend
npm run build
```
