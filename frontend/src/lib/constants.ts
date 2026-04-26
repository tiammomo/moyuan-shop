export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  projects: '/api/projects',
  products: '/api/projects/:projectId/products',
  product: '/api/products/:productId',
  assets: {
    upload: '/api/assets',
    uploadUrl: '/api/assets/upload-url',
    complete: '/api/assets/complete',
    get: '/api/assets/:assetId',
    delete: '/api/assets/:assetId',
  },
  generationTasks: {
    list: '/api/generation-tasks',
    create: '/api/generation-tasks',
    promptPreview: '/api/generation-tasks/prompt-preview',
    get: '/api/generation-tasks/:taskId',
    cancel: '/api/generation-tasks/:taskId/cancel',
    retry: '/api/generation-tasks/:taskId/retry',
    variants: '/api/generation-tasks/:taskId/variants',
    results: '/api/generation-tasks/:taskId/results',
  },
  generationResults: {
    update: '/api/generation-results/:resultId',
    delete: '/api/generation-results/:resultId',
    export: '/api/generation-results/:resultId/export',
  },
  templates: {
    list: '/api/prompt-templates',
    create: '/api/prompt-templates',
    get: '/api/prompt-templates/:templateId',
    update: '/api/prompt-templates/:templateId',
    delete: '/api/prompt-templates/:templateId',
  },
};

export const IMAGE_SIZES = {
  '1024x1024': { label: '1:1 (方形)', width: 1024, height: 1024 },
  '1536x1024': { label: '3:2 (横向)', width: 1536, height: 1024 },
  '1024x1536': { label: '2:3 (竖向)', width: 1024, height: 1536 },
};

export const IMAGE_QUALITIES = {
  low: { label: '快速', creditCost: 1 },
  medium: { label: '标准', creditCost: 2 },
  high: { label: '高清', creditCost: 5 },
};

export const IMAGE_TYPES = {
  main_image: { label: '商品主图', icon: '◫' },
  lifestyle_scene: { label: '场景图', icon: '◬' },
  detail_image: { label: '详情页单图', icon: '◭' },
  detail_set: { label: '详情页套图', icon: '◭' },
  campaign: { label: '营销海报', icon: '◮' },
  social_post: { label: '社交媒体', icon: '◯' },
  variant_batch: { label: '批量变体', icon: '◱' },
};

export const TASK_STATUS_LABELS: Record<string, { label: string; color: string }> = {
  created: { label: '已创建', color: '#6B7280' },
  queued: { label: '排队中', color: '#3B82F6' },
  running: { label: '生成中', color: '#F59E0B' },
  succeeded: { label: '已完成', color: '#10B981' },
  failed: { label: '失败', color: '#EF4444' },
  cancelled: { label: '已取消', color: '#6B7280' },
  expired: { label: '已过期', color: '#9CA3AF' },
};
