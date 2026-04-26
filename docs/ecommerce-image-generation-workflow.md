# 电商辅助生图系统 Spec

## 1. 文档信息

| 字段 | 内容 |
| --- | --- |
| 文档名称 | 电商辅助生图系统 Spec |
| 项目名称 | moyuan-shop / 墨圆 AI 生图 |
| 当前版本 | v0.1 |
| 更新时间 | 2026-04-25 |
| 前端技术栈 | Next.js 16.2.4、React 19.2.4、TypeScript |
| 后端技术栈 | FastAPI |
| 生图模型 | `gpt-image-2` |
| API 文档 | `docs/api.md` |

## 2. 当前同步状态

### 2.1 已同步内容

当前项目已具备以下基础内容：

- 已验证 `gpt-image-2` 最小生图链路，可通过 `/images/generations` 返回 `b64_json` 并保存图片。
- 已有探针脚本：`probe_openai_proxy.py`。
- 已有最小测试脚本：`test_gpt_image_2.py`。
- 已有前端项目：`frontend/`，技术栈为 Next.js 16.2.4 + React 19.2.4。
- 已有前端静态页面：首页、项目列表、新建项目、模板中心。
- 已有前端常量和类型定义：`frontend/src/lib/constants.ts`、`frontend/src/types/api.ts`。
- 已有 API 设计文档：`docs/api.md`。
- 已有 `backend/` FastAPI MVP 骨架。
- 后端当前使用 mock image provider，不直接调用 `gpt-image-2`。
- 已安装前端/设计和电商生图相关本地 skills 到 `.claude/skills/`。

### 2.2 尚未同步或尚未实现内容

当前代码仍处于规划和早期前端原型阶段，以下内容尚未完全实现：

- 前端目前主要是静态 Mock 数据，尚未接入真实 API。
- 前端枚举与 API 文档存在命名差异，后续需要统一。
- 前端尚未实现商品上传、生图任务创建、任务轮询、结果画廊和导出。
- 后端尚未实现真实 `gpt-image-2` provider、Prompt 模板渲染、任务队列、数据库、对象存储和权限系统。

### 2.3 当前需要统一的命名差异

后续实现前应统一以下命名：

| 概念 | 当前前端命名 | API 文档命名 | Spec 推荐 |
| --- | --- | --- | --- |
| 商品主图 | `main` | `main_image` | `main_image` |
| 场景图 | `scene` | `lifestyle_scene` | `lifestyle_scene` |
| 详情页 | `detail_page` / `detail` | `detail_image` / `detail_set` | 按单图/套图区分 |
| 营销海报 | `poster` | `campaign` | `campaign` |
| 社交媒体 | `social` | `social_post` | `social_post` |
| 模板接口 | `/api/templates` | `/api/prompt-templates` | `/api/prompt-templates` |
| 资产类型 | `source/result/thumbnail/export` | `product_source/generated_image/...` | API 文档命名 |

## 3. 产品目标

构建一个面向电商运营、商家、设计师和内容团队的 AI 辅助生图平台，用结构化商品信息、商品素材和营销目标生成可用于电商业务的图片资产。

系统必须支持：

- 商品主图生成
- 商品场景图生成
- 详情页配图生成
- 活动营销图生成
- 社交媒体种草图生成
- 批量变体生成
- 结果审核、收藏、重试和导出

系统必须保证：

- 商品信息真实，不夸大功能
- 商品外观和核心结构不被随意改变
- 所有生成任务可追踪、可复现、可诊断
- 前端不暴露模型 API Key
- 生图调用由后端统一封装

## 4. 非目标

v0.1 不实现以下能力：

- 完整团队权限系统
- 在线支付和计费结算
- 复杂图像编辑、局部重绘、蒙版编辑
- 多模型路由和模型自动选择
- 自动投放广告平台
- 复杂工作流编排器
- 企业级审核流

这些能力可在后续版本扩展。

## 5. 用户角色

| 角色 | 主要目标 | 核心权限 |
| --- | --- | --- |
| 商家 | 上传商品，生成可用图片 | 管理自己的项目、商品、任务和结果 |
| 运营 | 批量生成营销素材 | 创建任务、批量变体、导出图片 |
| 设计师 | 维护视觉质量和模板 | 创建和调整 Prompt 模板、品牌风格 |
| 管理员 | 维护系统配置 | 管理模型配置、额度、用户和审计日志 |

v0.1 可先不实现完整鉴权，但 API、数据模型和前端结构必须预留用户与权限字段。

## 6. 核心业务对象

### 6.1 Project

项目用于承载一个店铺、品牌或业务空间。

必须字段：

- `id`
- `name`
- `brand_name`
- `brand_style`
- `owner_id`
- `created_at`
- `updated_at`

### 6.2 Product

商品是生图任务的核心上下文。

必须字段：

- `id`
- `project_id`
- `name`
- `category`
- `description`
- `selling_points`
- `target_audience`
- `price_range`
- `platform`
- `created_at`
- `updated_at`

### 6.3 Asset

资产包括商品原图、参考图、品牌素材、生成图、缩略图和导出包。

必须字段：

- `id`
- `project_id`
- `product_id`
- `asset_type`
- `storage_key`
- `url`
- `mime_type`
- `width`
- `height`
- `file_size`
- `checksum`
- `created_at`

### 6.4 GenerationTask

生图任务记录一次模型调用或一组模型调用的业务上下文。

必须字段：

- `id`
- `project_id`
- `product_id`
- `created_by`
- `status`
- `image_type`
- `template_id`
- `template_version`
- `input_params`
- `rendered_prompt`
- `model`
- `model_params`
- `request_id`
- `error_code`
- `error_message`
- `started_at`
- `finished_at`
- `created_at`
- `updated_at`

### 6.5 GenerationResult

生成结果指一个任务产出的单张图片。

必须字段：

- `id`
- `task_id`
- `asset_id`
- `thumbnail_asset_id`
- `width`
- `height`
- `format`
- `is_favorite`
- `score`
- `metadata`
- `created_at`

### 6.6 PromptTemplate

Prompt 模板用于把结构化业务参数渲染为最终模型 Prompt。

必须字段：

- `id`
- `name`
- `image_type`
- `version`
- `content`
- `variables`
- `constraints`
- `is_active`
- `created_by`
- `created_at`
- `updated_at`

## 7. 图片类型规范

### 7.1 `main_image` 商品主图

目标：生成适合电商平台展示的商品主图。

必须满足：

- 商品是画面主体。
- 背景干净，不喧宾夺主。
- 商品边缘清晰，缩略图可识别。
- 不添加未经确认的 Logo、证书、价格、评分、折扣和配件。
- 默认比例为 `1:1`。

### 7.2 `lifestyle_scene` 商品场景图

目标：把商品放入真实使用场景，提高购买想象力。

必须满足：

- 场景与商品品类相关。
- 商品尺寸、材质和使用方式合理。
- 道具不得改变商品事实。
- 人物、手部、环境可选，但不得暗示未证实功效。

### 7.3 `detail_image` 详情页单图

目标：解释一个商品卖点或一个使用信息。

必须满足：

- 一张图只表达一个核心信息。
- 文案应尽量由前端后处理叠加，避免依赖模型生成精确文字。
- 可展示材质、尺寸、功能、步骤、包装清单等。

### 7.4 `detail_set` 详情页套图

目标：生成一组结构化详情页图片。

必须满足：

- 每张图有明确段落目标。
- 支持单张重试，不要求整套重跑。
- 结果按顺序展示和导出。

### 7.5 `campaign` 活动营销图

目标：生成促销、节日、新品或广告创意图片。

必须满足：

- 支持更强视觉风格和主题表达。
- 精确价格、折扣、CTA 优先由前端文字层叠加。
- 保留安全区和负空间。
- 不使用受保护品牌、角色、名人或竞品 Logo。

### 7.6 `social_post` 社交媒体图

目标：生成适合小红书、抖音、Instagram 等渠道的种草视觉。

必须满足：

- 支持更生活化、编辑化或内容化表达。
- 保持商品真实展示。
- 支持竖图比例，例如 `4:5`、`9:16`。

### 7.7 `variant_batch` 批量变体

目标：围绕一个商品或任务生成多组 A/B 测试创意。

必须满足：

- 每次批量只变化有限维度。
- 提交前展示任务数量和预计消耗。
- 每个子任务独立记录状态和结果。
- 支持单张收藏、评分、重试和导出。

## 8. 端到端业务流程

### 8.1 单商品生图流程

```text
1. 用户创建或选择项目。
2. 用户创建或选择商品。
3. 用户上传商品原图或参考图。
4. 用户选择图片类型。
5. 用户填写场景、风格、背景、构图、平台和尺寸参数。
6. 前端调用 Prompt 预览接口，后端优化用户提示词并渲染最终 Prompt。
7. 前端展示优化后的最终 Prompt，用户确认。
8. 前端提交结构化请求到 FastAPI。
9. 后端校验参数和资产权限。
10. 后端选择 Prompt 模板并渲染最终 Prompt。
11. 后端创建 GenerationTask，状态为 queued。
12. Worker 调用 gpt-image-2。
13. 后端解码 b64_json，保存生成图和缩略图。
14. 后端更新任务状态和结果数据。
15. 前端轮询任务状态，等待过程中展示阶段、已耗时和长任务提示。
16. 前端展示结果图和原图对比。
17. 成功后的图片暂存到本地 `storage/generated/`，前端提供下载入口。
18. 用户收藏、重试、创建变体或导出。
```

### 8.2 批量变体流程

```text
1. 用户选择基础商品或基础任务。
2. 用户选择变体维度，例如背景、场景、构图、风格。
3. 系统计算将生成的任务数量和消耗。
4. 用户确认。
5. 后端展开为多个子任务。
6. 队列按并发限制执行。
7. 前端以矩阵方式展示结果。
8. 用户筛选、评分、收藏和导出。
```

### 8.3 详情页套图流程

```text
1. 用户选择详情页套图模板。
2. 系统根据商品卖点生成多个段落。
3. 用户确认每个段落的视觉重点。
4. 后端创建一组 detail_image 任务。
5. 每张图独立生成和重试。
6. 前端按详情页顺序展示。
7. 用户导出图片包或详情页草稿。
```

## 9. 系统架构规范

### 9.1 总体架构

```text
Next.js 16 Frontend
        |
        | JSON / multipart / polling
        v
FastAPI Backend
        |
        | prompt rendering / task orchestration / provider wrapper
        v
Image Provider: gpt-image-2
        |
        v
Database + File/Object Storage
```

### 9.2 前端职责

Next.js 前端负责：

- 页面路由和 UI 展示
- 表单输入和客户端校验
- 商品、项目、模板、任务和结果的可视化
- 图片上传交互
- 任务状态轮询
- 图片画廊、对比、收藏、导出入口
- 不处理模型密钥和模型直连调用

### 9.3 后端职责

FastAPI 后端负责：

- API 鉴权和权限校验
- Pydantic 参数校验
- Prompt 模板渲染
- `gpt-image-2` Provider 封装
- 任务创建、执行、重试和取消
- 图片保存、缩略图生成和导出
- 数据库持久化
- 错误映射和可观测日志

## 10. 前端 Spec

### 10.1 技术要求

必须使用：

- Next.js 16.2.4
- React 19.2.4
- TypeScript
- App Router
- CSS Modules 或项目现有 CSS 变量体系

在修改 Next.js 代码前，必须遵守 `frontend/AGENTS.md`：读取 `node_modules/next/dist/docs/` 中相关 Next.js 16 文档，避免使用过时 API。

### 10.2 已有页面

当前已有页面：

| 页面 | 路由 | 状态 |
| --- | --- | --- |
| 首页 | `/` | 静态原型已存在 |
| 项目列表 | `/projects` | 静态 Mock 已存在 |
| 新建项目/生图入口 | `/projects/new` | 静态 Mock 已存在 |
| 模板中心 | `/templates` | 静态 Mock 已存在 |

### 10.3 必须补齐页面

| 页面 | 路由 | 说明 |
| --- | --- | --- |
| 项目详情 | `/projects/[projectId]` | 展示商品、任务、最近结果 |
| 商品详情 | `/projects/[projectId]/products/[productId]` | 商品信息、素材、生成历史 |
| 创建生图任务 | `/projects/[projectId]/generations/new` | 结构化生图表单 |
| 任务详情 | `/projects/[projectId]/generations/[taskId]` | 状态、Prompt 摘要、结果 |
| 设置页 | `/settings` | 模型默认参数、额度、品牌风格入口 |

### 10.4 关键组件

必须逐步沉淀以下组件：

- `ProductImageUploader`
- `ProductFactsForm`
- `GenerationTypeSelector`
- `GenerationParamForm`
- `PromptSummaryCard`
- `PromptPreviewPanel`
- `GenerationProgressCard`
- `ResultGallery`
- `ImageComparePanel`
- `VariantMatrix`
- `ExportPanel`

当前 MVP 可先在页面内实现等待体验、结果画廊和下载入口，后续再拆分为上述组件。

### 10.5 前端状态规范

- 服务端数据通过 API 获取，不长期写死在页面组件中。
- 表单状态保留在页面或局部组件中。
- 创建任务前先预览优化后的最终 Prompt，用户确认后再提交生图任务。
- 长任务使用轮询，默认间隔 5 秒，最长自动检查 20 分钟。
- 等待过程必须展示当前阶段、已耗时和长任务说明，避免只显示静态 loading。
- 等待过程可展示 `frontend/public/gif/` 下的动效资源；每次任务开始随机选择一个，长等待时每 15 秒切换一次。前端引用应优先使用 ASCII 文件名，避免中文、空格和括号导致静态资源路径兼容问题。
- 任务状态为 `succeeded`、`failed`、`cancelled` 时停止轮询。
- 错误展示必须面向用户，不直接暴露上游原始错误。
- 任务成功后必须展示生成结果，并提供下载入口。

### 10.6 视觉规范

现有全局 CSS 变量可继续使用：

- 主色：`--color-accent: #E85D04`
- 背景：`--color-bg-primary: #F8FAFC`
- 字体：`Noto Sans SC`
- 圆角：`--radius-sm` 到 `--radius-xl`
- 状态色：success、warning、error、info

后续 UI 应保持“清爽、可信、偏电商运营工具”的风格，避免过度 AI 感、过度渐变和无意义装饰。

## 11. 后端 Spec

### 11.1 推荐目录

```text
backend/
  app/
    main.py
    api/
      routes/
        health.py
        projects.py
        products.py
        assets.py
        prompt_templates.py
        generation_tasks.py
        generation_results.py
        exports.py
        usage.py
        settings.py
    core/
      config.py
      logging.py
      security.py
    schemas/
      project.py
      product.py
      asset.py
      prompt_template.py
      generation.py
      export.py
    services/
      image_provider.py
      prompt_builder.py
      storage.py
      thumbnail.py
      usage_meter.py
    workers/
      generation_worker.py
    db/
      models.py
      session.py
```

### 11.2 MVP 必须实现 API

MVP 只要求实现：

```http
GET  /api/health
POST /api/assets
GET  /api/assets/{asset_id}/file
POST /api/generation-tasks/prompt-preview
POST /api/generation-tasks
GET  /api/generation-tasks/{task_id}
GET  /api/generation-tasks/{task_id}/results
```

完整 API 以 `docs/api.md` 为准。

### 11.2.1 多参考图图生图流程

前端允许用户一次选择一张或多张商品参考图，用于生成单张目标图或按 `count` 生成多张目标图。多图输入流程如下：

```text
1. 用户选择多张商品参考图，最多 16 张
2. 前端调用 POST /api/generation-tasks/prompt-preview，按选择数量传入临时 source_asset_ids，展示优化后的 Prompt
3. 用户开始生成后，前端逐张调用 POST /api/assets 上传参考图
4. 前端收集所有返回的 asset_id，并在 POST /api/generation-tasks 中写入 source_asset_ids
5. 后端校验每个 source_asset_id 对应的资产存在且为 image/*
6. ImageProvider 在同一次图生图请求中使用全部 source_images 作为参考输入；OpenAI 图片编辑请求使用重复的 multipart `image` 字段传递多张图
7. 生成成功后，前端展示生成图和全部参考图对比，并提供下载入口
```

多参考图用于融合商品外观、结构、颜色、材质、包装、细节或不同角度信息；输出数量仍由 `count` 控制，`source_asset_ids` 的数量不代表输出图片数量。超过 16 张时前端应截取并提示，后端必须拒绝创建任务，避免静默丢图。

### 11.3 ImageProvider 规范

后端必须封装 `ImageProvider`，业务路由不得直接拼接上游 HTTP 请求。

接口要求：

```python
class ImageProvider:
    async def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        ...
```

`gpt-image-2` 默认参数：

```json
{
  "model": "gpt-image-2",
  "size": "1024x1024",
  "quality": "low",
  "output_format": "jpeg",
  "output_compression": 50
}
```

每次调用必须记录：

- `model`
- `prompt`
- `size`
- `quality`
- `output_format`
- `output_compression`
- `request_id`
- `elapsed_ms`
- 成功或失败状态

### 11.4 任务执行规范

MVP 可以使用简单后台任务或同步线程实现，但 API 语义必须保持异步任务模型：

```text
created -> queued -> running -> succeeded
created -> queued -> running -> failed
created -> queued -> cancelled
```

生产版本必须使用队列，例如 Celery、Dramatiq 或 RQ。

## 12. Prompt Spec

### 12.1 Prompt 构建原则

- 前端提交结构化字段。
- 后端先将用户提示词优化为电商可用创意方向。
- 前端可展示优化后的最终 Prompt 供用户确认。
- 后端根据 `image_type` 选择模板。
- 后端渲染最终 Prompt。
- 任务保存模板 ID、模板版本、变量和最终 Prompt。
- 不允许只保存用户原始输入而丢失最终 Prompt。

### 12.2 Prompt 分层

最终 Prompt 应包含：

1. 任务角色和目标
2. 商品事实
3. 图片类型
4. 场景和视觉风格
5. 平台和比例要求
6. 商品真实性约束
7. 合规和禁止项

### 12.3 默认约束

所有电商生图 Prompt 默认包含：

- 保持商品主体清晰突出。
- 不改变商品核心外观、颜色和结构。
- 不添加未经确认的配件、Logo、认证、价格和评分。
- 不夸大商品功能或效果。
- 不使用受保护品牌、角色、名人或竞品元素。
- exact text 优先由前端叠加，不依赖模型生成。

### 12.4 MVP 内置 Prompt 模板

MVP 阶段先把常用电商 Prompt 模板写入前端共享常量，代码位置为 `frontend/src/lib/promptTemplates.ts`。`/templates` 模板中心和 `/projects/new` 新建任务页必须读取同一份内置模板，避免展示模板和实际可用模板不一致。

当前内置模板：

| 模板 ID | 名称 | 默认图片类型 | 建议尺寸 | 用途 |
| --- | --- | --- | --- | --- |
| `white-background-main` | 白底主图（平台合规） | `main_image` | `1024x1024` | 平台白底主图，无道具、无文字、无 Logo |
| `forty-five-degree` | 45度角展示图 | `detail_image` | `1024x1024` | 展示产品立体感和设计细节 |
| `lifestyle-scene` | 生活场景图 | `lifestyle_scene` | `1536x1024` | 展示使用氛围和生活方式场景 |
| `macro-detail` | 产品细节特写图 | `detail_image` | `1024x1024` | 展示材质、纹理、工艺和品质感 |
| `size-reference` | 尺寸参照对比图 | `detail_image` | `1024x1024` | 用常见参照物帮助理解尺寸 |
| `color-variant` | 多色系变体展示图 | `variant_batch` | `1024x1024` | 保持角度和光照一致，生成不同颜色选项 |
| `in-use-demo` | 产品使用演示图 | `lifestyle_scene` | `1536x1024` | 展示产品被使用时的自然状态 |
| `complete-set-flatlay` | 组合套装图 / 全家福 | `detail_set` | `1024x1024` | 展示套装和配件完整内容物 |

模板中的 `[YOUR PRODUCT]` 和 `[PRODUCT SET]` 可由前端根据商品名称或商品描述自动替换；其他占位符应保留在 Prompt 中，提醒用户继续补充场景、材质、参照物或颜色等关键信息。

后续实现 `PromptTemplate` API 和数据库后，应将这些内置模板迁移为系统预置模板，并继续保持模板 ID 稳定，便于旧任务追溯和复用。

## 13. 存储 Spec

### 13.1 MVP 存储

MVP 可使用本地存储：

```text
storage/
  assets/
  generated/
  thumbnails/
  exports/
```

MVP 生成图固定暂存到后端工作目录下的 `storage/generated/`，缩略图暂存到 `storage/thumbnails/`。当前已有调试输出位于 `output/`，后续应用级产物应迁移到 `storage/`。

### 13.2 生产存储

生产环境建议使用对象存储：

```text
projects/{project_id}/products/{product_id}/source/{asset_id}.jpg
projects/{project_id}/generations/{task_id}/results/{result_id}.jpg
projects/{project_id}/generations/{task_id}/thumbs/{result_id}.jpg
exports/{project_id}/{export_id}.zip
```

### 13.3 图片处理

保存生成图后必须生成：

- 原始输出图
- Web 预览 URL
- 缩略图
- 图片尺寸和格式元数据
- 文件大小和 checksum

## 14. 安全与合规 Spec

### 14.1 密钥安全

- `OPENAI_API_KEY` 只能在后端环境变量中出现。
- 前端不得出现模型密钥、对象存储密钥或数据库连接信息。
- `.env` 文件不得提交到版本库。

### 14.2 商品真实性

系统必须避免：

- 改变商品颜色、形状、结构、数量。
- 添加不存在的配件。
- 虚构功效、认证、材质、价格、评分。
- 生成误导性对比图。

### 14.3 内容风险

系统必须避免：

- 未授权品牌 Logo。
- 名人、角色、影视 IP 和竞品元素。
- 医疗、金融、安全等高风险夸大表达。
- 平台政策明显不允许的营销话术。

## 15. 可观测性 Spec

每个生成任务必须记录结构化日志字段：

- `task_id`
- `project_id`
- `product_id`
- `user_id`
- `model`
- `request_id`
- `status`
- `elapsed_ms`
- `error_code`

系统后续应统计：

- 任务总数
- 成功率
- 平均耗时
- P95 耗时
- 失败原因分布
- 图片导出率
- 模板使用次数
- 用户额度消耗

## 16. MVP 验收标准

MVP 完成必须满足：

- FastAPI 服务可以启动并返回 `GET /api/health`。
- 前端可以创建一个生图任务。
- 后端可以通过 mock provider 保存图片；切换真实 provider 后可调用 `gpt-image-2`。
- 前端可以轮询任务状态。
- 前端可以展示生成结果。
- 任务详情中可以查看状态、模型参数和错误信息。
- API Key 不出现在前端代码和浏览器请求中。
- 至少保留一次成功任务的最终 Prompt 和输出文件。

## 17. 开发顺序

### 17.1 M0：服务闭环

1. 创建 `backend/` FastAPI 骨架。
2. 封装 ImageProvider 接口，首版使用 mock provider。
3. 实现本地存储。
4. 实现最小任务 API。
5. 前端接入创建任务和轮询结果。

### 17.2 M1：商品上下文

1. 实现 Project 和 Product API。
2. 实现商品图片上传。
3. 用商品信息构建 Prompt。
4. 建立商品详情和任务历史页面。

### 17.3 M2：模板和变体

1. 实现 PromptTemplate API。
2. 实现模板预览。
3. 实现批量变体任务。
4. 实现结果收藏、评分和重试。

### 17.4 M3：生产化

1. 引入数据库。
2. 引入任务队列。
3. 引入对象存储。
4. 增加权限、额度和审计日志。
5. 增加监控和错误告警。

## 18. 变更规则

修改本 Spec 时必须同步检查：

- `docs/api.md`
- `frontend/src/lib/constants.ts`
- `frontend/src/types/api.ts`
- 后端 Pydantic schemas
- 前端页面路由和组件名称

如果 API 枚举发生变化，必须同步更新前端常量和类型定义。
