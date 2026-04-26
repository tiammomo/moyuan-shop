import Link from 'next/link';
import { BUILT_IN_PROMPT_TEMPLATES } from '@/lib/promptTemplates';
import styles from './page.module.css';

const typeLabels: Record<string, string> = {
  main_image: '商品主图',
  lifestyle_scene: '场景图',
  campaign: '营销海报',
  detail_image: '详情页单图',
  detail_set: '详情页套图',
  social_post: '社交媒体',
  variant_batch: '色系变体',
};

const typeIcons: Record<string, string> = {
  main_image: '◫',
  lifestyle_scene: '◬',
  campaign: '◮',
  detail_image: '◭',
  detail_set: '◭',
  social_post: '◯',
  variant_batch: '◱',
};

export default function TemplatesPage() {
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
            <button className={styles.btnPrimary}>
              新建模板
            </button>
          </div>
        </div>
      </header>

      <main className={styles.main}>
        <div className={styles.pageHeader}>
          <h1 className={styles.title}>模板中心</h1>
          <p className={styles.subtitle}>管理和使用你的图片生成模板</p>
        </div>

        <div className={styles.filters}>
          <button className={`${styles.filterBtn} ${styles.active}`}>全部</button>
          <button className={styles.filterBtn}>商品主图</button>
          <button className={styles.filterBtn}>场景图</button>
          <button className={styles.filterBtn}>营销海报</button>
          <button className={styles.filterBtn}>详情页</button>
          <button className={styles.filterBtn}>社交媒体</button>
        </div>

        <div className={styles.templatesGrid}>
          {BUILT_IN_PROMPT_TEMPLATES.map((tmpl) => (
            <div key={tmpl.id} className={styles.templateCard}>
              <div className={styles.templatePreview}>
                <span className={styles.templateIcon}>
                  {typeIcons[tmpl.imageType]}
                </span>
              </div>
              <div className={styles.templateInfo}>
                <h3 className={styles.templateName}>{tmpl.name}</h3>
                <span className={styles.templateType}>{typeLabels[tmpl.imageType]}</span>
                <p className={styles.templateDesc}>{tmpl.description}</p>
                <p className={styles.templatePrompt}>{tmpl.prompt.split('\n')[0]}</p>
                <div className={styles.templateMeta}>
                  <span>内置模板</span>
                  <span>·</span>
                  <span>{tmpl.placeholders.length} 个可替换参数</span>
                </div>
              </div>
              <div className={styles.templateActions}>
                <Link
                  className={styles.actionBtn}
                  href={`/projects/new?template=${tmpl.id}&type=${tmpl.imageType}`}
                >
                  使用
                </Link>
                <button className={styles.actionBtn}>编辑</button>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
