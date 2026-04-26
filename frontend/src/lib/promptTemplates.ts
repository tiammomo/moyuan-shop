export type BuiltInPromptTemplate = {
  id: string;
  name: string;
  imageType: 'main_image' | 'lifestyle_scene' | 'detail_image' | 'detail_set' | 'campaign' | 'social_post' | 'variant_batch';
  description: string;
  prompt: string;
  placeholders: string[];
  suggestedSize: '1024x1024' | '1536x1024' | '1024x1536';
};

export const BUILT_IN_PROMPT_TEMPLATES: BuiltInPromptTemplate[] = [
  {
    id: 'white-background-main',
    name: '白底主图（平台合规）',
    imageType: 'main_image',
    description: '纯白背景、主体居中、无道具无文字，适合淘宝、亚马逊、拼多多主图。',
    suggestedSize: '1024x1024',
    placeholders: ['[YOUR PRODUCT]', 'square 1:1 composition'],
    prompt: `Ultra-realistic studio photograph of [YOUR PRODUCT] on a pure white seamless background,
centered composition, product fills 85-90% of frame,
shot with 85mm prime lens, f/8 sharpness, ISO 100,
softbox high-key lighting with gentle contact shadow under product,
natural accurate colors, no props, no text, no logos, no watermark,
square 1:1 composition, commercial product photography`,
  },
  {
    id: 'forty-five-degree',
    name: '45度角展示图',
    imageType: 'detail_image',
    description: '展示立体感和设计细节，适合作为套图中的第 2-3 张。',
    suggestedSize: '1024x1024',
    placeholders: ['[YOUR PRODUCT]'],
    prompt: `Professional product photograph of [YOUR PRODUCT],
three-quarter view at 45-degree angle from slightly above,
on a seamless light gray gradient background (#f0f0f0 to #ffffff),
studio softbox lighting from upper left with subtle fill light from right,
f/5.6 aperture for slight depth of field,
sharp focus on product front, gentle bokeh on rear edge,
natural material textures preserved, no artificial smoothing,
commercial e-commerce photography style`,
  },
  {
    id: 'lifestyle-scene',
    name: '生活场景图',
    imageType: 'lifestyle_scene',
    description: '传达产品使用氛围，帮助买家想象拥有后的体验。',
    suggestedSize: '1536x1024',
    placeholders: ['[YOUR PRODUCT]', '[SCENE SETTING]', '[SURFACE DESCRIPTION]', '[2-3 COMPLEMENTARY PROPS]'],
    prompt: `Lifestyle product photography of [YOUR PRODUCT] in a [SCENE SETTING],
natural window light from the left side creating soft warm shadows,
product placed on [SURFACE DESCRIPTION],
surrounded by [2-3 COMPLEMENTARY PROPS],
shallow depth of field f/2.8 with product in sharp focus,
warm color temperature 5500K, cozy and inviting atmosphere,
editorial style composition with rule of thirds placement,
high resolution commercial photography`,
  },
  {
    id: 'macro-detail',
    name: '产品细节特写图',
    imageType: 'detail_image',
    description: '突出材质、工艺和品质感，适合详情页卖点局部图。',
    suggestedSize: '1024x1024',
    placeholders: ['[PRODUCT DETAIL AREA]', '[SPECIFIC TEXTURE/DETAIL]'],
    prompt: `Extreme close-up macro product photography of [PRODUCT DETAIL AREA],
shot with 100mm macro lens at f/4,
focused on [SPECIFIC TEXTURE/DETAIL],
single directional studio light from upper right creating texture-revealing shadows,
preserve natural grain and material texture, no plastic sheen,
dark background gradient from #1a1a2e to #16213e for contrast,
showing fine craftsmanship details, stitching, and material quality,
ultra-sharp commercial photography, 8K detail level`,
  },
  {
    id: 'size-reference',
    name: '尺寸参照对比图',
    imageType: 'detail_image',
    description: '用常见物体建立尺寸预期，减少尺寸理解偏差。',
    suggestedSize: '1024x1024',
    placeholders: ['[YOUR PRODUCT]', '[COMMON REFERENCE OBJECT]'],
    prompt: `Product size reference photograph of [YOUR PRODUCT]
placed next to [COMMON REFERENCE OBJECT] for scale comparison,
both items on a clean white surface,
top-down flat lay composition shot directly from above,
even studio lighting with minimal shadows,
f/11 for maximum depth of field ensuring both items in sharp focus,
neutral color temperature, accurate color reproduction,
clean informational style, commercial product photography`,
  },
  {
    id: 'color-variant',
    name: '多色系变体展示图',
    imageType: 'variant_batch',
    description: '保持角度、光照和构图一致，用于同链接多颜色选项展示。',
    suggestedSize: '1024x1024',
    placeholders: ['[YOUR PRODUCT]', '[COLOR]'],
    prompt: `Product color variant display of [YOUR PRODUCT] in [COLOR],
identical three-quarter view at 30-degree angle,
on pure white background,
consistent softbox lighting setup: key light upper left,
fill light right side, rim light from behind,
f/8 sharpness, same exact camera position and framing,
accurate color reproduction matching real product color,
uniform white balance D65, commercial product photography`,
  },
  {
    id: 'in-use-demo',
    name: '产品使用演示图',
    imageType: 'lifestyle_scene',
    description: '展示产品被使用时的状态，适合功能性产品和穿戴类产品。',
    suggestedSize: '1536x1024',
    placeholders: ['[USAGE SCENARIO]', '[ENVIRONMENT DETAILS]'],
    prompt: `Product in-use demonstration photograph of [USAGE SCENARIO],
natural lifestyle setting with [ENVIRONMENT DETAILS],
product clearly visible and in focus as the main subject,
candid natural pose, not overly staged,
warm natural lighting simulating golden hour,
f/3.5 aperture creating natural background separation,
authentic and relatable atmosphere,
editorial commercial photography style,
high resolution output`,
  },
  {
    id: 'complete-set-flatlay',
    name: '组合套装图 / 全家福',
    imageType: 'detail_set',
    description: '展示套装产品或配件组合的完整内容物，适合清单式详情图。',
    suggestedSize: '1024x1024',
    placeholders: ['[PRODUCT SET]', '[BACKGROUND SURFACE]'],
    prompt: `Product flatlay photograph showing complete set contents of [PRODUCT SET],
all items arranged in organized grid layout on [BACKGROUND SURFACE],
top-down overhead perspective shot directly from above,
each item clearly separated with equal spacing,
even diffused studio lighting with no harsh shadows,
f/11 maximum sharpness across all items,
clean minimal style, accurate colors,
items labeled with subtle positioning,
commercial catalog photography style`,
  },
];

export function getBuiltInPromptTemplate(id: string | null) {
  return BUILT_IN_PROMPT_TEMPLATES.find((template) => template.id === id) || null;
}

export function renderTemplatePrompt(template: BuiltInPromptTemplate, productName: string, productDesc: string) {
  const productValue = productDesc || productName || '[YOUR PRODUCT]';
  return template.prompt
    .replaceAll('[YOUR PRODUCT]', productValue)
    .replaceAll('[PRODUCT SET]', productValue);
}
