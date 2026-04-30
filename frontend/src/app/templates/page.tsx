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
    <div className={styles.shell}>
      <aside className={styles.sidebar} aria-label="主导航">
        <Link href="/" className={styles.brandMark} aria-label="墨圆AI电商宣传图">
          <span>墨</span>
        </Link>
        <nav className={styles.sideNav}>
          <Link href="/projects" className={styles.sideNavItem}><span>□</span><small>项目</small></Link>
          <Link href="/templates" className={`${styles.sideNavItem} ${styles.sideNavItemActive}`}><span>▧</span><small>模板</small></Link>
          <Link href="/projects/new" className={styles.sideNavItem}><span>＋</span><small>新建</small></Link>
        </nav>
      </aside>

      <div className={styles.workspace}>
        <main className={styles.main}>
          <div className={styles.pageHeader}>
            <div>
              <h1 className={styles.title}>模板中心</h1>
              <p className={styles.subtitle}>管理和使用电商宣传图生成模板</p>
            </div>
            <Link className={styles.btnPrimary} href="/projects/new">
              新建生成任务
            </Link>
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
    </div>
  );
}
