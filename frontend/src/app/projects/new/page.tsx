'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { API_BASE_URL } from '@/lib/constants';
import { BUILT_IN_PROMPT_TEMPLATES, getBuiltInPromptTemplate, renderTemplatePrompt } from '@/lib/promptTemplates';
import styles from './page.module.css';

type ImageType = 'main_image' | 'lifestyle_scene' | 'detail_image' | 'detail_set' | 'campaign' | 'social_post' | 'variant_batch';
type ImageSize = '1024x1024' | '1536x1024' | '1024x1536';
type TaskStatus = 'idle' | 'queued' | 'running' | 'succeeded' | 'failed' | 'cancelled' | 'expired';
type GenerationStep = 'idle' | 'optimizing' | 'uploading' | 'creating' | 'queued' | 'running' | 'saving' | 'completed' | 'failed';

interface GenerationTaskResponse {
  data: {
    id: string;
    status: TaskStatus;
    source_asset_ids: string[];
    error_code: string | null;
    error_message: string | null;
  };
}

interface AssetResponse {
  data: {
    id: string;
    url: string;
    width: number | null;
    height: number | null;
    mime_type: string;
  };
}

interface GenerationResult {
  id: string;
  url: string;
  thumbnail_url: string | null;
  width: number;
  height: number;
  format: string;
}

interface GenerationResultsResponse {
  data: GenerationResult[];
}

interface PromptPreviewResponse {
  data: {
    optimized_prompt: string | null;
    rendered_prompt: string;
    warnings: string[];
  };
}

const imageTypes = [
  { id: 'main_image', name: '商品主图', icon: '◫', desc: '白底高清图，适合淘宝、京东等平台', color: '#3B82F6' },
  { id: 'lifestyle_scene', name: '场景图', icon: '◬', desc: '融入生活场景，提升商品表现力', color: '#8B5CF6' },
  { id: 'detail_image', name: '详情页单图', icon: '◭', desc: '聚焦一个卖点，适合详情页段落', color: '#10B981' },
  { id: 'detail_set', name: '详情页套图', icon: '◭', desc: '多图连续叙述，完整展示商品卖点', color: '#14B8A6' },
  { id: 'campaign', name: '营销海报', icon: '◮', desc: '活动推广物料，引流转化', color: '#F59E0B' },
  { id: 'social_post', name: '社交媒体', icon: '◯', desc: '小红书、抖音、Instagram种草图', color: '#EC4899' },
  { id: 'variant_batch', name: '色系变体', icon: '◱', desc: '同角度同光照，生成多色选项展示图', color: '#6366F1' },
];

const sizes = [
  { id: '1024x1024', name: '1:1 方形', desc: '适合主图、详情页' },
  { id: '1536x1024', name: '3:2 横版', desc: '适合海报、Banner' },
  { id: '1024x1536', name: '2:3 竖向', desc: '适合Instagram' },
];

const POLL_INTERVAL_MS = 5000;
const MAX_POLL_ATTEMPTS = 240;
const MAX_SOURCE_IMAGE_COUNT = 16;
const STORAGE_HINT = 'backend/storage/generated';
const WAITING_GIFS = [
  '/gif/waiting-drawing.gif',
  '/gif/waiting-work-12.gif',
  '/gif/waiting-work-13.gif',
];

export default function NewProjectPage() {
  const [selectedType, setSelectedType] = useState<ImageType>('main_image');
  const [selectedSize, setSelectedSize] = useState<ImageSize>('1024x1024');
  const [prompt, setPrompt] = useState('');
  const [selectedTemplateId, setSelectedTemplateId] = useState<string | null>(null);
  const [productName, setProductName] = useState('');
  const [productDesc, setProductDesc] = useState('');
  const [sourceFiles, setSourceFiles] = useState<File[]>([]);
  const [sourcePreviewUrls, setSourcePreviewUrls] = useState<string[]>([]);
  const [uploadedAssets, setUploadedAssets] = useState<AssetResponse['data'][]>([]);
  const [uploadWarning, setUploadWarning] = useState<string | null>(null);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [taskStatus, setTaskStatus] = useState<TaskStatus>('idle');
  const [results, setResults] = useState<GenerationResult[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [optimizedPrompt, setOptimizedPrompt] = useState<string | null>(null);
  const [promptWarnings, setPromptWarnings] = useState<string[]>([]);
  const [generationStep, setGenerationStep] = useState<GenerationStep>('idle');
  const [startedAt, setStartedAt] = useState<number | null>(null);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [waitingGif, setWaitingGif] = useState(WAITING_GIFS[0]);

  useEffect(() => {
    const searchParams = new URLSearchParams(window.location.search);
    const type = searchParams.get('type');
    if (imageTypes.some((item) => item.id === type)) {
      setSelectedType(type as ImageType);
    }
    const template = getBuiltInPromptTemplate(searchParams.get('template'));
    if (template) {
      setSelectedTemplateId(template.id);
      setSelectedType(template.imageType);
      setSelectedSize(template.suggestedSize);
      setPrompt(renderTemplatePrompt(template, productName, productDesc));
    }
  }, []);

  useEffect(() => {
    if (sourceFiles.length === 0) {
      setSourcePreviewUrls([]);
      return;
    }
    const objectUrls = sourceFiles.map((file) => URL.createObjectURL(file));
    setSourcePreviewUrls(objectUrls);
    return () => {
      objectUrls.forEach((objectUrl) => URL.revokeObjectURL(objectUrl));
    };
  }, [sourceFiles]);

  useEffect(() => {
    if (!startedAt || ['idle', 'completed', 'failed'].includes(generationStep)) {
      return;
    }
    const timer = window.setInterval(() => {
      setElapsedSeconds(Math.floor((Date.now() - startedAt) / 1000));
    }, 1000);
    return () => window.clearInterval(timer);
  }, [generationStep, startedAt]);

  useEffect(() => {
    if (!startedAt || ['idle', 'completed', 'failed'].includes(generationStep)) {
      return;
    }
    const timer = window.setInterval(() => {
      setWaitingGif(getRandomWaitingGif(waitingGif));
    }, 15000);
    return () => window.clearInterval(timer);
  }, [generationStep, startedAt, waitingGif]);

  const handleSubmit = async () => {
    if (isSubmitting) {
      return;
    }

    setIsSubmitting(true);
    setStartedAt(Date.now());
    setElapsedSeconds(0);
    setWaitingGif(getRandomWaitingGif());
    setGenerationStep('optimizing');
    setTaskStatus('queued');
    setTaskId(null);
    setResults([]);
    setErrorMessage(null);

    try {
      await previewPrompt(true);
      setGenerationStep(sourceFiles.length > 0 ? 'uploading' : 'creating');
      const sourceAssetIds = sourceFiles.length > 0 ? await uploadSourceAssets(sourceFiles) : [];
      setGenerationStep('creating');
      const createResponse = await fetch(`${API_BASE_URL}/api/generation-tasks`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(buildTaskRequest(sourceAssetIds)),
      });

      if (!createResponse.ok) {
        throw new Error('创建生图任务失败，请检查后端服务是否正常。');
      }

      const createdTask = await createResponse.json() as GenerationTaskResponse;
      setTaskId(createdTask.data.id);
      setTaskStatus(createdTask.data.status);
      setGenerationStep(createdTask.data.status === 'running' ? 'running' : 'queued');

      const finishedTask = await pollTask(createdTask.data.id);
      setTaskStatus(finishedTask.status);

      if (finishedTask.status === 'succeeded') {
        setGenerationStep('saving');
        const taskResults = await fetchResults(createdTask.data.id);
        setResults(taskResults);
        setGenerationStep('completed');
        return;
      }

      setGenerationStep('failed');
      setErrorMessage(toUserMessage(finishedTask.error_code, finishedTask.error_message));
    } catch (error) {
      setTaskStatus('failed');
      setGenerationStep('failed');
      setErrorMessage(error instanceof Error ? error.message : '生成失败，请稍后重试。');
    } finally {
      setIsSubmitting(false);
    }
  };

  const previewPrompt = async (raiseError = false) => {
    setIsOptimizing(true);
    setErrorMessage(null);
    try {
      const response = await fetch(`${API_BASE_URL}/api/generation-tasks/prompt-preview`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(buildTaskRequest(buildPreviewSourceAssetIds(sourceFiles.length))),
      });
      if (!response.ok) {
        throw new Error('优化提示词失败，请检查后端服务是否正常。');
      }
      const payload = await response.json() as PromptPreviewResponse;
      setOptimizedPrompt(payload.data.rendered_prompt);
      setPromptWarnings(payload.data.warnings);
      return payload.data;
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '优化提示词失败，请稍后重试。');
      if (raiseError) {
        throw error;
      }
      return null;
    } finally {
      setIsOptimizing(false);
    }
  };

  const buildTaskRequest = (sourceAssetIds: string[]) => ({
    project_id: 'project_local',
    product_id: 'product_local',
    image_type: selectedType,
    source_asset_ids: sourceAssetIds,
    params: {
      prompt: buildPrompt(productName, productDesc, prompt),
      size: selectedSize,
      quality: 'low',
      output_format: 'jpeg',
      output_compression: 50,
      background: 'clean ecommerce studio background',
      style: 'clean trustworthy ecommerce product photography',
      composition: 'centered product hero with safe margins',
      include_text: false,
    },
    negative_constraints: [
      'Do not change the product color, shape, material, or structure',
      'Do not add logos, fake certification badges, prices, ratings, or extra accessories',
      'Do not exaggerate product performance or create unsupported claims',
    ],
    count: 1,
  });

  const applyPromptTemplate = (templateId: string) => {
    const template = getBuiltInPromptTemplate(templateId);
    if (!template) {
      setSelectedTemplateId(null);
      return;
    }
    setSelectedTemplateId(template.id);
    setSelectedType(template.imageType);
    setSelectedSize(template.suggestedSize);
    setPrompt(renderTemplatePrompt(template, productName, productDesc));
    setOptimizedPrompt(null);
    setPromptWarnings([]);
  };

  const uploadSourceAssets = async (files: File[]) => {
    const assets: AssetResponse['data'][] = [];
    for (const file of files) {
      assets.push(await uploadSourceAsset(file));
    }
    setUploadedAssets(assets);
    return assets.map((asset) => asset.id);
  };

  const uploadSourceAsset = async (file: File) => {
    const formData = new FormData();
    formData.append('project_id', 'project_local');
    formData.append('product_id', 'product_local');
    formData.append('asset_type', 'product_source');
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/assets`, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) {
      throw new Error('上传商品图失败，请检查文件格式或后端服务。');
    }
    const payload = await response.json() as AssetResponse;
    return payload.data;
  };

  const pollTask = async (id: string) => {
    for (let attempt = 0; attempt < MAX_POLL_ATTEMPTS; attempt += 1) {
      await sleep(POLL_INTERVAL_MS);
      const response = await fetch(`${API_BASE_URL}/api/generation-tasks/${id}`);
      if (!response.ok) {
        throw new Error('查询任务状态失败，请检查后端服务。');
      }
      const payload = await response.json() as GenerationTaskResponse;
      setTaskStatus(payload.data.status);
      if (payload.data.status === 'queued') {
        setGenerationStep('queued');
      }
      if (payload.data.status === 'running') {
        setGenerationStep('running');
      }
      if (['succeeded', 'failed', 'cancelled', 'expired'].includes(payload.data.status)) {
        return payload.data;
      }
    }
    throw new Error('生成时间较长，前端已停止自动检查，请稍后在任务记录中查看结果。');
  };

  const fetchResults = async (id: string) => {
    const response = await fetch(`${API_BASE_URL}/api/generation-tasks/${id}/results`);
    if (!response.ok) {
      throw new Error('获取生成结果失败。');
    }
    const payload = await response.json() as GenerationResultsResponse;
    return payload.data;
  };

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.headerContent}>
          <Link href="/" className={styles.logo}>
            <span className={styles.logoIcon}>墨</span>
            <span className={styles.logoText}>墨圆AI生图</span>
          </Link>
          <nav className={styles.nav}>
            <Link href="/" className={styles.navItem}>首页</Link>
            <Link href="/projects" className={styles.navItem}>项目</Link>
            <Link href="/templates" className={styles.navItem}>模板</Link>
            <Link href="/settings" className={styles.navItem}>设置</Link>
          </nav>
          <div className={styles.headerActions}>
            <Link href="/projects" className={styles.btnSecondary}>
              取消
            </Link>
          </div>
        </div>
      </header>

      <main className={styles.main}>
        <div className={styles.formContainer}>
          <h1 className={styles.title}>新建生成任务</h1>
          <p className={styles.subtitle}>选择图片类型，填写商品信息，开始AI生图</p>

          <div className={styles.section}>
            <h2 className={styles.sectionTitle}>选择图片类型</h2>
            <div className={styles.typeGrid}>
              {imageTypes.map((type) => (
                <button
                  key={type.id}
                  className={`${styles.typeCard} ${selectedType === type.id ? styles.selected : ''}`}
                  onClick={() => setSelectedType(type.id as ImageType)}
                  style={{ '--type-color': type.color } as React.CSSProperties}
                >
                  <span className={styles.typeIcon} style={{ color: type.color }}>{type.icon}</span>
                  <span className={styles.typeName}>{type.name}</span>
                  <span className={styles.typeDesc}>{type.desc}</span>
                </button>
              ))}
            </div>
          </div>

          <div className={styles.section}>
            <h2 className={styles.sectionTitle}>选择尺寸</h2>
            <div className={styles.sizeGrid}>
              {sizes.map((size) => (
                <button
                  key={size.id}
                  className={`${styles.sizeCard} ${selectedSize === size.id ? styles.selected : ''}`}
                  onClick={() => setSelectedSize(size.id as ImageSize)}
                >
                  <span className={styles.sizeName}>{size.name}</span>
                  <span className={styles.sizeDesc}>{size.desc}</span>
                </button>
              ))}
            </div>
          </div>

          <div className={styles.section}>
            <h2 className={styles.sectionTitle}>商品信息</h2>
            <div className={styles.formGroup}>
              <label className={styles.label}>商品原图</label>
              <label className={styles.uploadBox}>
                <input
                  type="file"
                  className={styles.fileInput}
                  accept="image/png,image/jpeg,image/webp"
                  multiple
                  onChange={(event) => {
                    const selectedFiles = Array.from(event.target.files || []);
                    const files = selectedFiles.slice(0, MAX_SOURCE_IMAGE_COUNT);
                    setSourceFiles(files);
                    setUploadedAssets([]);
                    setOptimizedPrompt(null);
                    setPromptWarnings([]);
                    setUploadWarning(
                      selectedFiles.length > MAX_SOURCE_IMAGE_COUNT
                        ? `最多支持 ${MAX_SOURCE_IMAGE_COUNT} 张参考图，已保留前 ${MAX_SOURCE_IMAGE_COUNT} 张。`
                        : null,
                    );
                  }}
                />
                {sourcePreviewUrls.length > 0 ? (
                  <span className={styles.sourcePreviewGrid}>
                    {sourcePreviewUrls.map((previewUrl, index) => (
                      <img
                        key={`${sourceFiles[index]?.name || 'source'}-${previewUrl}`}
                        src={previewUrl}
                        alt={`商品参考图 ${index + 1}`}
                        className={styles.sourcePreview}
                      />
                    ))}
                  </span>
                ) : (
                  <span className={styles.uploadPlaceholder}>
                    可上传一张或多张商品参考图，最多 {MAX_SOURCE_IMAGE_COUNT} 张，用于图生图时综合保持外观、颜色、结构和细节
                  </span>
                )}
              </label>
              {sourceFiles.length > 0 && (
                <div className={styles.uploadMetaList}>
                  <p className={styles.uploadMeta}>
                    已选择 {sourceFiles.length} 张参考图
                    {uploadedAssets.length > 0 ? ` · 已上传 ${uploadedAssets.length} 张` : ''}
                  </p>
                  {sourceFiles.map((file, index) => {
                    const uploadedAsset = uploadedAssets[index];
                    return (
                      <p key={`${file.name}-${file.lastModified}`} className={styles.uploadMeta}>
                        {index + 1}. {file.name} · {Math.max(1, Math.round(file.size / 1024))} KB
                        {uploadedAsset ? ` · ${uploadedAsset.width || '-'} x ${uploadedAsset.height || '-'}` : ''}
                      </p>
                    );
                  })}
                  {uploadWarning && <p className={styles.uploadWarning}>{uploadWarning}</p>}
                </div>
              )}
            </div>
            <div className={styles.formGroup}>
              <label className={styles.label}>商品名称</label>
              <input
                type="text"
                className={styles.input}
                placeholder="输入商品名称"
                value={productName}
                onChange={(e) => setProductName(e.target.value)}
              />
            </div>
            <div className={styles.formGroup}>
              <label className={styles.label}>商品描述</label>
              <textarea
                className={styles.textarea}
                placeholder="描述商品特点、卖点、使用场景等"
                value={productDesc}
                onChange={(e) => setProductDesc(e.target.value)}
                rows={4}
              />
            </div>
          </div>

          <div className={styles.section}>
            <h2 className={styles.sectionTitle}>生成描述</h2>
            <div className={styles.formGroup}>
              <label className={styles.label}>Prompt模板</label>
              <div className={styles.promptTemplateGrid}>
                {BUILT_IN_PROMPT_TEMPLATES.map((template) => (
                  <button
                    key={template.id}
                    className={`${styles.promptTemplateCard} ${selectedTemplateId === template.id ? styles.selected : ''}`}
                    onClick={() => applyPromptTemplate(template.id)}
                  >
                    <span className={styles.promptTemplateName}>{template.name}</span>
                    <span className={styles.promptTemplateDesc}>{template.description}</span>
                  </button>
                ))}
              </div>
            </div>
            <div className={styles.formGroup}>
              <label className={styles.label}>Prompt提示词</label>
              <textarea
                className={styles.textarea}
                placeholder="描述你想要的图片效果，例如：现代简约风格，清新配色，商品居中展示，背景纯白..."
                value={prompt}
                onChange={(e) => {
                  setPrompt(e.target.value);
                  setOptimizedPrompt(null);
                  setPromptWarnings([]);
                }}
                rows={6}
              />
            </div>
            <div className={styles.promptActions}>
              <button
                className={styles.btnSecondary}
                onClick={() => {
                  void previewPrompt();
                }}
                disabled={isOptimizing || isSubmitting}
              >
                {isOptimizing ? '优化中' : '优化提示词'}
              </button>
            </div>
            {optimizedPrompt && (
              <div className={styles.promptPreview}>
                <div className={styles.promptPreviewHeader}>
                  <h3 className={styles.promptPreviewTitle}>优化后的提示词</h3>
                  <span className={styles.promptPreviewMeta}>后端最终 Prompt</span>
                </div>
                <pre className={styles.promptPreviewText}>{optimizedPrompt}</pre>
                {promptWarnings.length > 0 && (
                  <ul className={styles.promptWarningList}>
                    {promptWarnings.map((warning) => (
                      <li key={warning}>{warning}</li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </div>

          <div className={styles.actions}>
            <button className={styles.btnPrimary} onClick={handleSubmit} disabled={isSubmitting}>
              {isSubmitting ? '生成中' : '开始生成'}
            </button>
            <Link href="/projects" className={styles.btnSecondary}>
              取消
            </Link>
          </div>

          {taskStatus !== 'idle' && (
            <section className={styles.statusPanel}>
              <div className={styles.statusHeader}>
                <div>
                  <h2 className={styles.statusTitle}>任务状态</h2>
                  <p className={styles.statusText}>{getStepLabel(generationStep, taskStatus)}</p>
                </div>
                <span className={styles.elapsedTime}>{formatElapsed(elapsedSeconds)}</span>
              </div>
              {['optimizing', 'uploading', 'creating', 'queued', 'running', 'saving'].includes(generationStep) && (
                <div className={styles.waitingVisual}>
                  <img key={waitingGif} src={waitingGif} alt="生成等待动画" className={styles.waitingGif} />
                </div>
              )}
              <div className={styles.progressTrack} aria-label="生成进度">
                <span
                  className={`${styles.progressFill} ${generationStep === 'running' ? styles.progressActive : ''}`}
                  style={{ width: `${getProgressPercent(generationStep, taskStatus)}%` }}
                />
              </div>
              <div className={styles.stepGrid}>
                {['优化提示词', '上传素材', '创建任务', '模型生成', '保存结果'].map((label, index) => (
                  <span
                    key={label}
                    className={`${styles.stepItem} ${index <= getActiveStepIndex(generationStep) ? styles.stepDone : ''}`}
                  >
                    {label}
                  </span>
                ))}
              </div>
              <p className={styles.waitingHint}>
                生图通常需要几十秒到数分钟，页面会每 5 秒自动检查一次，完成后生成图会暂存到 {STORAGE_HINT} 并提供下载。
              </p>
              {taskId && <p className={styles.taskId}>任务 ID：{taskId}</p>}
            </section>
          )}

          {errorMessage && (
            <section className={styles.errorPanel}>
              <h2 className={styles.statusTitle}>生成失败</h2>
              <p className={styles.statusText}>{errorMessage}</p>
            </section>
          )}

          {results.length > 0 && (
            <section className={styles.resultSection}>
              <div className={styles.resultHeader}>
                <div>
                  <h2 className={styles.sectionTitle}>生成结果</h2>
                  <p className={styles.resultHint}>图片已暂存到本地 {STORAGE_HINT}，可先下载使用，后续再接导出组件。</p>
                </div>
              </div>
              {sourcePreviewUrls.length > 0 && (
                <div className={styles.comparePanel}>
                  <div>
                    <span className={styles.compareLabel}>参考图（{sourcePreviewUrls.length} 张）</span>
                    <div className={styles.compareSourceGrid}>
                      {sourcePreviewUrls.map((previewUrl, index) => (
                        <img
                          key={`${sourceFiles[index]?.name || 'compare'}-${previewUrl}`}
                          src={previewUrl}
                          alt={`商品参考图 ${index + 1}`}
                          className={styles.compareImage}
                        />
                      ))}
                    </div>
                  </div>
                  <div>
                    <span className={styles.compareLabel}>生成图</span>
                    <img
                      src={`${API_BASE_URL}${results[0].url}`}
                      alt="生成结果预览"
                      className={styles.compareImage}
                    />
                  </div>
                </div>
              )}
              <div className={styles.resultGrid}>
                {results.map((result) => {
                  const imageUrl = `${API_BASE_URL}${result.url}`;
                  const downloadUrl = `${imageUrl}?download=1`;
                  const filename = `moyuan-${result.id}.${result.format === 'jpeg' ? 'jpg' : result.format}`;
                  return (
                    <div key={result.id} className={styles.resultCard}>
                      <a href={imageUrl} target="_blank" className={styles.resultImageLink}>
                        <img
                          src={imageUrl}
                          alt="生成结果"
                          className={styles.resultImage}
                        />
                      </a>
                      <span className={styles.resultMeta}>
                        {result.width} x {result.height} · {result.format.toUpperCase()}
                      </span>
                      <div className={styles.downloadActions}>
                        <a className={styles.btnPrimarySmall} href={downloadUrl} download={filename}>
                          下载图片
                        </a>
                        <a className={styles.btnSecondarySmall} href={imageUrl} target="_blank">
                          打开预览
                        </a>
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>
          )}
        </div>
      </main>
    </div>
  );
}

function buildPrompt(productName: string, productDesc: string, prompt: string) {
  return [
    productName ? `Product name: ${productName}` : null,
    productDesc ? `Product description: ${productDesc}` : null,
    prompt ? `Creative direction: ${prompt}` : null,
  ].filter(Boolean).join('\n');
}

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function buildPreviewSourceAssetIds(count: number) {
  return Array.from({ length: count }, (_, index) => `preview_source_asset_${index + 1}`);
}

function getStatusLabel(status: TaskStatus) {
  const labels: Record<TaskStatus, string> = {
    idle: '未开始',
    queued: '排队中',
    running: '生成中',
    succeeded: '已完成',
    failed: '失败',
    cancelled: '已取消',
    expired: '已过期',
  };
  return labels[status];
}

function getStepLabel(step: GenerationStep, status: TaskStatus) {
  const labels: Record<GenerationStep, string> = {
    idle: '未开始',
    optimizing: '正在优化提示词',
    uploading: '正在上传商品原图',
    creating: '正在创建生图任务',
    queued: '任务已入队，等待模型处理',
    running: '模型正在生成图片',
    saving: '正在保存生成图和缩略图',
    completed: '已完成，可下载图片',
    failed: '生成失败',
  };
  if (step === 'idle') {
    return getStatusLabel(status);
  }
  return labels[step];
}

function getProgressPercent(step: GenerationStep, status: TaskStatus) {
  if (status === 'succeeded' || step === 'completed') {
    return 100;
  }
  if (status === 'failed' || step === 'failed') {
    return 100;
  }
  const progress: Record<GenerationStep, number> = {
    idle: 0,
    optimizing: 12,
    uploading: 24,
    creating: 36,
    queued: 48,
    running: 72,
    saving: 92,
    completed: 100,
    failed: 100,
  };
  return progress[step];
}

function getActiveStepIndex(step: GenerationStep) {
  const indexes: Record<GenerationStep, number> = {
    idle: -1,
    optimizing: 0,
    uploading: 1,
    creating: 2,
    queued: 2,
    running: 3,
    saving: 4,
    completed: 4,
    failed: 4,
  };
  return indexes[step];
}

function formatElapsed(seconds: number) {
  const minutes = Math.floor(seconds / 60).toString().padStart(2, '0');
  const restSeconds = (seconds % 60).toString().padStart(2, '0');
  return `${minutes}:${restSeconds}`;
}

function getRandomWaitingGif(current?: string) {
  if (WAITING_GIFS.length === 1) {
    return WAITING_GIFS[0];
  }
  const candidates = current ? WAITING_GIFS.filter((item) => item !== current) : WAITING_GIFS;
  return candidates[Math.floor(Math.random() * candidates.length)];
}

function toUserMessage(errorCode: string | null, errorMessage: string | null) {
  if (errorCode === 'PROVIDER_AUTH_FAILED') {
    return '模型服务鉴权失败，请检查后端 OPENAI_API_KEY。';
  }
  if (errorCode === 'PROVIDER_RATE_LIMITED') {
    return '模型服务当前限流，请稍后再试。';
  }
  if (errorCode === 'PROVIDER_TIMEOUT') {
    return '模型生成超时，请稍后重试或降低生成数量。';
  }
  return errorMessage || '生成失败，请稍后重试。';
}
