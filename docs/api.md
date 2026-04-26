# API 设计文档

## 1. 概述

本文档定义当前电商辅助生图系统的后端 API 设计。系统前端使用 Next.js 16，后端使用 FastAPI，核心能力围绕商品素材管理、结构化 Prompt、`gpt-image-2` 生图任务、生成结果管理、批量变体和导出。

API 设计目标：

- 前端只提交结构化业务参数，不直接调用模型接口
- 后端统一负责鉴权、参数校验、Prompt 渲染、模型调用、任务编排和结果存储
- 生图过程使用异步任务模型，避免长请求阻塞
- 所有生成结果可追溯：记录 Prompt、模型参数、请求 ID、耗时、错误和输出资产
- 支持从 MVP 的本地文件存储平滑升级到对象存储和队列

## 2. 基础约定

### 2.1 Base URL

开发环境建议：

```text
http://localhost:8000/api
```

生产环境示例：

```text
https://api.example.com/api
```

### 2.2 数据格式

请求和响应默认使用 JSON：

```http
Content-Type: application/json
Accept: application/json
```

文件上传接口可使用：

```http
multipart/form-data
```

或使用预签名上传 URL。

### 2.3 鉴权方式

MVP 阶段可先预留鉴权结构。生产环境建议使用 Bearer Token：

```http
Authorization: Bearer <access_token>
```

后端必须持有并保护以下敏感配置，禁止暴露给前端：

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- 对象存储 Access Key
- 数据库连接串

### 2.4 通用响应结构

单对象响应：

```json
{
  "data": {}
}
```

列表响应：

```json
{
  "data": [],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 100
  }
}
```

错误响应：

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求参数不合法",
    "details": {}
  }
}
```

### 2.5 时间格式

所有时间字段使用 ISO 8601 UTC 字符串：

```text
2026-04-25T12:30:00Z
```

### 2.6 ID 约定

建议使用 UUID 或 ULID：

```text
01HWABCDEF1234567890XYZ
```

## 3. 核心枚举

### 3.1 图片类型 `image_type`

```text
main_image        商品主图
lifestyle_scene   商品场景图
detail_image      详情页单图
detail_set        详情页套图
campaign          活动营销图
social_post       社媒种草图
variant_batch     批量变体
```

### 3.2 任务状态 `status`

```text
created      已创建
queued       已入队
running      生成中
succeeded    成功
failed       失败
cancelled    已取消
expired      已过期
```

### 3.3 资产类型 `asset_type`

```text
product_source       商品原始图
reference_image      参考图
brand_asset          品牌素材
generated_image      生成结果图
thumbnail            缩略图
export_zip           导出包
```

### 3.4 输出格式 `output_format`

```text
jpeg
png
webp
```

### 3.5 任务质量 `quality`

```text
low
medium
high
```

首版默认使用 `low`，以降低成本和延迟。

## 4. 健康检查

### 4.1 获取服务状态

```http
GET /api/health
```

响应：

```json
{
  "data": {
    "status": "ok",
    "service": "moyuan-shop-api",
    "version": "0.1.0"
  }
}
```

## 5. 项目 API

项目用于区分不同店铺、品牌或业务空间。

### 5.1 获取项目列表

```http
GET /api/projects?page=1&page_size=20
```

响应：

```json
{
  "data": [
    {
      "id": "project_01",
      "name": "默认店铺",
      "brand_name": "Moyuan",
      "brand_style": "clean, modern, ecommerce friendly",
      "created_at": "2026-04-25T12:00:00Z",
      "updated_at": "2026-04-25T12:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 1
  }
}
```

### 5.2 创建项目

```http
POST /api/projects
```

请求：

```json
{
  "name": "女装店铺",
  "brand_name": "Example Brand",
  "brand_style": "editorial, soft daylight, warm neutral colors"
}
```

响应：

```json
{
  "data": {
    "id": "project_01",
    "name": "女装店铺",
    "brand_name": "Example Brand",
    "brand_style": "editorial, soft daylight, warm neutral colors",
    "created_at": "2026-04-25T12:00:00Z",
    "updated_at": "2026-04-25T12:00:00Z"
  }
}
```

### 5.3 获取项目详情

```http
GET /api/projects/{project_id}
```

### 5.4 更新项目

```http
PATCH /api/projects/{project_id}
```

请求：

```json
{
  "name": "女装旗舰店",
  "brand_style": "minimal, clean, premium, natural light"
}
```

### 5.5 删除项目

```http
DELETE /api/projects/{project_id}
```

响应：

```json
{
  "data": {
    "deleted": true
  }
}
```

## 6. 商品 API

商品是生图任务的核心上下文。建议先创建商品，再围绕商品上传素材和创建生图任务。

### 6.1 获取项目下商品列表

```http
GET /api/projects/{project_id}/products?page=1&page_size=20&keyword=杯子
```

响应：

```json
{
  "data": [
    {
      "id": "product_01",
      "project_id": "project_01",
      "name": "便携保温杯",
      "category": "水杯",
      "description": "适合通勤和户外使用的不锈钢保温杯",
      "selling_points": ["长效保温", "轻便易携", "防漏杯盖"],
      "target_audience": "通勤上班族、学生、户外人群",
      "price_range": "100-200 CNY",
      "platform": "taobao",
      "cover_asset_id": "asset_01",
      "created_at": "2026-04-25T12:00:00Z",
      "updated_at": "2026-04-25T12:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 1
  }
}
```

### 6.2 创建商品

```http
POST /api/projects/{project_id}/products
```

请求：

```json
{
  "name": "便携保温杯",
  "category": "水杯",
  "description": "适合通勤和户外使用的不锈钢保温杯",
  "selling_points": ["长效保温", "轻便易携", "防漏杯盖"],
  "target_audience": "通勤上班族、学生、户外人群",
  "price_range": "100-200 CNY",
  "platform": "taobao"
}
```

### 6.3 获取商品详情

```http
GET /api/products/{product_id}
```

### 6.4 更新商品

```http
PATCH /api/products/{product_id}
```

请求：

```json
{
  "selling_points": ["长效保温", "单手开合", "杯身轻量化"]
}
```

### 6.5 删除商品

```http
DELETE /api/products/{product_id}
```

## 7. 资产 API

资产包括商品原图、参考图、生成图、缩略图和导出包。

MVP 可先使用 `multipart/form-data` 直传到 FastAPI。生产环境建议使用预签名 URL 直传对象存储。

### 7.1 直接上传资产

```http
POST /api/assets
Content-Type: multipart/form-data
```

表单字段：

```text
project_id: string
product_id: string optional
asset_type: product_source | reference_image | brand_asset
file: binary
```

响应：

```json
{
  "data": {
    "id": "asset_01",
    "project_id": "project_01",
    "product_id": "product_01",
    "asset_type": "product_source",
    "url": "/api/assets/asset_01/file",
    "mime_type": "image/jpeg",
    "width": 1024,
    "height": 1024,
    "file_size": 84520,
    "created_at": "2026-04-25T12:00:00Z"
  }
}
```

### 7.2 获取上传 URL

```http
POST /api/assets/upload-url
```

请求：

```json
{
  "project_id": "project_01",
  "product_id": "product_01",
  "asset_type": "product_source",
  "filename": "cup.jpg",
  "mime_type": "image/jpeg",
  "file_size": 84520
}
```

响应：

```json
{
  "data": {
    "upload_url": "https://storage.example.com/presigned-url",
    "storage_key": "projects/project_01/products/product_01/source/asset_01.jpg",
    "expires_in": 900
  }
}
```

### 7.3 完成上传

```http
POST /api/assets/complete
```

请求：

```json
{
  "project_id": "project_01",
  "product_id": "product_01",
  "asset_type": "product_source",
  "storage_key": "projects/project_01/products/product_01/source/asset_01.jpg",
  "filename": "cup.jpg",
  "mime_type": "image/jpeg",
  "file_size": 84520
}
```

### 7.4 获取资产详情

```http
GET /api/assets/{asset_id}
```

### 7.5 获取资产文件

```http
GET /api/assets/{asset_id}/file
```

MVP 可直接返回文件流。前端需要触发浏览器下载时可追加查询参数：

```http
GET /api/assets/{asset_id}/file?download=1
```

带 `download=1` 时后端返回附件文件名，便于成功生图后提供下载入口。生产环境可返回重定向或签名 URL。

### 7.6 删除资产

```http
DELETE /api/assets/{asset_id}
```

## 8. Prompt 模板 API

Prompt 模板由后端使用，用于把结构化业务参数渲染为最终 `gpt-image-2` Prompt。

MVP 阶段允许先在前端代码中提供系统内置模板，代码位置为 `frontend/src/lib/promptTemplates.ts`。这些模板用于快速填充 `params.prompt`，最终仍必须经由 `POST /api/generation-tasks/prompt-preview` 和 `POST /api/generation-tasks` 交给后端优化、渲染和保存。后续实现本章 API 后，应将内置模板迁移为后端可管理的系统预置模板。

### 8.1 获取模板列表

```http
GET /api/prompt-templates?image_type=main_image&page=1&page_size=20
```

响应：

```json
{
  "data": [
    {
      "id": "template_01",
      "name": "商品主图基础模板",
      "image_type": "main_image",
      "version": 1,
      "description": "适合生成干净、可信、商品主体突出的电商主图",
      "variables": ["product_name", "category", "selling_points", "background", "style"],
      "is_active": true,
      "created_at": "2026-04-25T12:00:00Z",
      "updated_at": "2026-04-25T12:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 1
  }
}
```

### 8.2 创建模板

```http
POST /api/prompt-templates
```

请求：

```json
{
  "name": "商品主图基础模板",
  "image_type": "main_image",
  "description": "适合生成干净、可信、商品主体突出的电商主图",
  "content": "Create a high-quality ecommerce {{image_type}} for {{product_name}}...",
  "variables": ["product_name", "category", "selling_points", "background", "style"],
  "constraints": ["Preserve product appearance", "Do not add unsupported claims"]
}
```

### 8.3 获取模板详情

```http
GET /api/prompt-templates/{template_id}
```

### 8.4 更新模板

```http
PATCH /api/prompt-templates/{template_id}
```

说明：模板内容变更应创建新版本，历史生成任务必须保留旧版本引用。

### 8.5 停用模板

```http
POST /api/prompt-templates/{template_id}/deactivate
```

### 8.6 预览 Prompt

```http
POST /api/prompt-templates/{template_id}/preview
```

请求：

```json
{
  "product_id": "product_01",
  "params": {
    "image_type": "main_image",
    "background": "clean warm beige studio background",
    "style": "premium minimal ecommerce photography",
    "lighting": "soft daylight",
    "composition": "centered product hero with safe margins"
  }
}
```

响应：

```json
{
  "data": {
    "template_id": "template_01",
    "template_version": 1,
    "rendered_prompt": "Create a high-quality ecommerce main image...",
    "warnings": []
  }
}
```

## 9. 生图任务 API

生图任务是系统核心。前端创建任务后立即得到 `task_id`，再通过轮询或事件接口获取状态。

### 9.1 预览优化后的 Prompt

前端在创建任务前应先调用该接口，将结构化字段交给后端优化并渲染最终 Prompt。前端展示 `rendered_prompt` 给用户确认，随后使用同一组结构化参数创建生图任务。后端创建任务时仍会重新渲染最终 Prompt，确保任务记录可追溯。

```http
POST /api/generation-tasks/prompt-preview
```

请求：同 `POST /api/generation-tasks` 的请求体，可在尚未正式上传源图时使用临时 `source_asset_ids` 仅用于 Prompt 预览。若前端已选择多张参考图但尚未上传，可按选择数量传入多个临时 ID，便于后端在 Prompt 预览中识别这是多图图生图任务。

响应：

```json
{
  "data": {
    "optimized_prompt": "Refined creative direction: Product name: ...",
    "rendered_prompt": "Create a high-quality ecommerce product main image...",
    "warnings": []
  }
}
```

### 9.2 创建生图任务

```http
POST /api/generation-tasks
```

请求：

```json
{
  "project_id": "project_01",
  "product_id": "product_01",
  "image_type": "main_image",
  "template_id": "template_01",
  "source_asset_ids": ["asset_01", "asset_02", "asset_03"],
  "params": {
    "platform": "taobao",
    "aspect_ratio": "1:1",
    "size": "1024x1024",
    "quality": "low",
    "output_format": "jpeg",
    "output_compression": 50,
    "background": "warm beige studio background",
    "style": "premium minimal ecommerce photography",
    "lighting": "soft daylight",
    "composition": "centered product hero with safe margins",
    "scene": null,
    "include_text": false,
    "text_requirements": null
  },
  "negative_constraints": [
    "Do not change the product color",
    "Do not add logos or fake certification badges",
    "Do not add extra accessories"
  ],
  "count": 1
}
```

说明：

- `source_asset_ids` 可为空；为空时按纯文本生图处理。
- `source_asset_ids` 可包含一张或多张 `product_source` / `reference_image` 资产，最多 16 张；包含多张时，后端必须把这些源图作为同一次图生图请求的参考输入，目标仍是生成一张或多张输出图，由 `count` 决定输出数量。
- 前端上传多张图时应先逐张调用 `POST /api/assets`，收集返回的 `asset_id` 后再创建任务。

响应：

```json
{
  "data": {
    "id": "task_01",
    "project_id": "project_01",
    "product_id": "product_01",
    "status": "queued",
    "image_type": "main_image",
    "template_id": "template_01",
    "template_version": 1,
    "count": 1,
    "created_at": "2026-04-25T12:00:00Z",
    "updated_at": "2026-04-25T12:00:00Z"
  }
}
```

### 9.3 获取任务列表

```http
GET /api/generation-tasks?project_id=project_01&product_id=product_01&status=succeeded&page=1&page_size=20
```

响应字段建议：

```json
{
  "data": [
    {
      "id": "task_01",
      "project_id": "project_01",
      "product_id": "product_01",
      "status": "succeeded",
      "image_type": "main_image",
      "result_count": 1,
      "thumbnail_url": "/api/assets/asset_thumb_01/file",
      "created_at": "2026-04-25T12:00:00Z",
      "finished_at": "2026-04-25T12:01:05Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 1
  }
}
```

### 9.4 获取任务详情

```http
GET /api/generation-tasks/{task_id}
```

响应：

```json
{
  "data": {
    "id": "task_01",
    "project_id": "project_01",
    "product_id": "product_01",
    "status": "succeeded",
    "image_type": "main_image",
    "template_id": "template_01",
    "template_version": 1,
    "input_params": {
      "platform": "taobao",
      "aspect_ratio": "1:1",
      "size": "1024x1024",
      "quality": "low",
      "output_format": "jpeg"
    },
    "rendered_prompt": "Create a high-quality ecommerce main image...",
    "model": "gpt-image-2",
    "model_params": {
      "size": "1024x1024",
      "quality": "low",
      "output_format": "jpeg",
      "output_compression": 50
    },
    "request_id": "81630a0d-3cfe-4fd2-ae40-cb9309653bb3",
    "elapsed_ms": 61747,
    "error_code": null,
    "error_message": null,
    "created_at": "2026-04-25T12:00:00Z",
    "started_at": "2026-04-25T12:00:03Z",
    "finished_at": "2026-04-25T12:01:05Z",
    "updated_at": "2026-04-25T12:01:05Z"
  }
}
```

### 9.5 获取任务结果

```http
GET /api/generation-tasks/{task_id}/results
```

响应：

```json
{
  "data": [
    {
      "id": "result_01",
      "task_id": "task_01",
      "asset_id": "asset_generated_01",
      "thumbnail_asset_id": "asset_thumb_01",
      "url": "/api/assets/asset_generated_01/file",
      "thumbnail_url": "/api/assets/asset_thumb_01/file",
      "width": 1024,
      "height": 1024,
      "format": "jpeg",
      "is_favorite": false,
      "score": null,
      "metadata": {
        "variant_key": null
      },
      "created_at": "2026-04-25T12:01:05Z"
    }
  ]
}
```

### 9.6 取消任务

```http
POST /api/generation-tasks/{task_id}/cancel
```

说明：只有 `created` 或 `queued` 状态可靠可取消。`running` 状态可标记取消，但上游模型请求可能无法中断。

### 9.7 重试任务

```http
POST /api/generation-tasks/{task_id}/retry
```

请求：

```json
{
  "reuse_prompt": true,
  "override_params": {
    "quality": "medium"
  }
}
```

响应：返回新任务。

```json
{
  "data": {
    "id": "task_02",
    "parent_task_id": "task_01",
    "status": "queued"
  }
}
```

### 9.8 创建变体任务

```http
POST /api/generation-tasks/{task_id}/variants
```

请求：

```json
{
  "variant_dimensions": {
    "background": ["warm beige studio", "clean white studio", "soft gray gradient"],
    "composition": ["centered hero", "slightly angled hero"]
  },
  "max_count": 6
}
```

响应：

```json
{
  "data": {
    "parent_task_id": "task_01",
    "batch_id": "batch_01",
    "task_ids": ["task_03", "task_04", "task_05", "task_06", "task_07", "task_08"],
    "estimated_count": 6,
    "status": "queued"
  }
}
```

## 10. 生成结果 API

### 10.1 更新结果元数据

```http
PATCH /api/generation-results/{result_id}
```

请求：

```json
{
  "is_favorite": true,
  "score": 5,
  "review_notes": "商品主体清晰，适合作为主图"
}
```

### 10.2 删除结果

```http
DELETE /api/generation-results/{result_id}
```

### 10.3 导出单个结果

```http
POST /api/generation-results/{result_id}/export
```

请求：

```json
{
  "format": "jpeg",
  "quality": 90,
  "filename": "cup-main-image.jpg"
}
```

响应：

```json
{
  "data": {
    "download_url": "/api/exports/export_01/file",
    "expires_at": "2026-04-25T13:00:00Z"
  }
}
```

## 11. 批量导出 API

### 11.1 创建导出任务

```http
POST /api/exports
```

请求：

```json
{
  "project_id": "project_01",
  "result_ids": ["result_01", "result_02"],
  "format": "zip",
  "include_metadata": true
}
```

响应：

```json
{
  "data": {
    "id": "export_01",
    "status": "queued",
    "created_at": "2026-04-25T12:00:00Z"
  }
}
```

### 11.2 获取导出详情

```http
GET /api/exports/{export_id}
```

响应：

```json
{
  "data": {
    "id": "export_01",
    "status": "succeeded",
    "download_url": "/api/exports/export_01/file",
    "expires_at": "2026-04-25T13:00:00Z"
  }
}
```

### 11.3 下载导出文件

```http
GET /api/exports/{export_id}/file
```

## 12. 用量 API

用于展示额度、成本和调用统计。

### 12.1 获取项目用量

```http
GET /api/usage?project_id=project_01&from=2026-04-01&to=2026-04-25
```

响应：

```json
{
  "data": {
    "project_id": "project_01",
    "task_count": 120,
    "succeeded_count": 104,
    "failed_count": 16,
    "generated_image_count": 180,
    "average_elapsed_ms": 58000,
    "credits_used": 180,
    "credits_remaining": 820
  }
}
```

## 13. 设置 API

### 13.1 获取模型配置

```http
GET /api/settings/image-generation
```

响应：

```json
{
  "data": {
    "default_model": "gpt-image-2",
    "default_size": "1024x1024",
    "default_quality": "low",
    "default_output_format": "jpeg",
    "default_output_compression": 50,
    "max_batch_count": 12,
    "poll_interval_seconds": 5,
    "max_poll_duration_seconds": 1200
  }
}
```

### 13.2 更新模型配置

```http
PATCH /api/settings/image-generation
```

请求：

```json
{
  "default_quality": "medium",
  "max_batch_count": 8
}
```

说明：只有管理员可以调用。

## 14. 事件接口

MVP 可先使用轮询。后续可增加 SSE。

### 14.1 订阅任务事件

```http
GET /api/generation-tasks/{task_id}/events
Accept: text/event-stream
```

事件示例：

```text
event: task.updated
data: {"task_id":"task_01","status":"running"}

event: task.succeeded
data: {"task_id":"task_01","result_count":1}
```

## 15. 错误码

| 错误码 | HTTP 状态 | 说明 |
| --- | --- | --- |
| `VALIDATION_ERROR` | 422 | 请求参数不合法 |
| `UNAUTHORIZED` | 401 | 未登录或 token 无效 |
| `FORBIDDEN` | 403 | 无权限访问资源 |
| `NOT_FOUND` | 404 | 资源不存在 |
| `CONFLICT` | 409 | 状态冲突，例如任务已完成不能取消 |
| `RATE_LIMITED` | 429 | 请求过于频繁或超出并发限制 |
| `QUOTA_EXCEEDED` | 402 | 额度不足 |
| `PROVIDER_AUTH_FAILED` | 502 | 上游模型鉴权失败 |
| `PROVIDER_RATE_LIMITED` | 503 | 上游模型限流 |
| `PROVIDER_TIMEOUT` | 504 | 上游模型超时 |
| `PROVIDER_ERROR` | 502 | 上游模型未知错误 |
| `STORAGE_ERROR` | 500 | 文件保存或对象存储失败 |
| `INTERNAL_ERROR` | 500 | 服务内部错误 |

## 16. 前端调用建议

### 16.1 创建任务并轮询

前端流程：

```text
1. POST /api/generation-tasks/prompt-preview 预览优化后的最终 Prompt
2. 用户确认后 POST /api/generation-tasks
3. 保存返回的 task_id
4. 每 5 秒 GET /api/generation-tasks/{task_id}，最长自动检查 20 分钟
5. 等待过程中展示阶段状态、已耗时、轮询说明、长任务提示和等待动效
6. status 为 succeeded 时 GET /api/generation-tasks/{task_id}/results
7. 成功后展示结果图，并用 `/api/assets/{asset_id}/file?download=1` 提供下载入口
8. status 为 failed 时展示 error_message 和重试入口
```

### 16.2 上传一张或多张商品参考图并创建任务

前端流程：

```text
1. POST /api/generation-tasks/prompt-preview 预览优化后的最终 Prompt
2. 用户可选择一张或多张商品参考图，最多 16 张
3. 对每张参考图分别 POST /api/assets 上传，资产类型使用 product_source 或 reference_image
4. 创建或更新商品 cover_asset_id；多图场景可用第一张作为封面
5. POST /api/generation-tasks，source_asset_ids 包含全部参考图 asset_id
6. 轮询任务状态
7. 展示生成图和全部参考图对比
8. 提供生成图下载入口
```

### 16.3 批量变体

前端流程：

```text
1. 用户选择一个成功任务作为基础
2. POST /api/generation-tasks/{task_id}/variants
3. 展示 batch_id 和多个子任务
4. 分别轮询子任务或使用 batch 查询接口
5. 在 VariantMatrix 中展示结果
```

## 17. MVP 实现范围

首版建议只实现以下 API：

```http
GET  /api/health
POST /api/assets
GET  /api/assets/{asset_id}/file
POST /api/generation-tasks/prompt-preview
POST /api/generation-tasks
GET  /api/generation-tasks/{task_id}
GET  /api/generation-tasks/{task_id}/results
```

MVP 可简化：

- 暂不实现用户系统
- 暂不实现团队权限
- 暂不实现预签名上传
- 暂不实现 SSE
- 暂不实现对象存储
- 任务可先用内存或 SQLite，后续迁移 PostgreSQL
- 图片可先保存到本地 `storage/generated/`，缩略图保存到 `storage/thumbnails/`

## 18. 与当前 gpt-image-2 链路的映射

当前脚本参数与 API 参数映射：

| 当前脚本参数 | API 字段 |
| --- | --- |
| `--model gpt-image-2` | `model_params.model`，后端固定或配置 |
| `--prompt` | `rendered_prompt`，后端模板生成 |
| `--size 1024x1024` | `params.size` |
| `--quality low` | `params.quality` |
| `--output-format jpeg` | `params.output_format` |
| `--compression 50` | `params.output_compression` |
| `b64_json` | 后端解码后保存为 `generated_image` asset |
| `x-request-id` | `generation_tasks.request_id` |

`gpt-image-2` 请求体由后端 `ImageProvider` 统一生成：

```json
{
  "model": "gpt-image-2",
  "prompt": "<rendered_prompt>",
  "size": "1024x1024",
  "quality": "low",
  "output_format": "jpeg",
  "output_compression": 50
}
```

## 19. 后续扩展

后续可扩展：

- `GET /api/generation-batches/{batch_id}` 查询批量任务整体进度
- `POST /api/generation-results/{result_id}/upscale` 放大图片
- `POST /api/generation-results/{result_id}/crop` 生成平台裁切版本
- `POST /api/generation-results/{result_id}/text-overlay` 添加可编辑营销文字
- `POST /api/reviews/generation-results/{result_id}` 记录人工审核结论
- `GET /api/platform-presets` 获取平台尺寸和规范预设
