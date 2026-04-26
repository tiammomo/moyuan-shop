import Link from "next/link";
import styles from "./page.module.css";

const templates = [
  { id: 'main_image', name: '商品主图', desc: '白底高清主图，适合电商平台', icon: '◫', color: '#3B82F6' },
  { id: 'lifestyle_scene', name: '场景图', desc: '融入生活场景，提升表现力', icon: '◬', color: '#8B5CF6' },
  { id: 'detail_set', name: '详情页套图', desc: '多图连续叙述，完整展示', icon: '◭', color: '#10B981' },
  { id: 'campaign', name: '营销海报', desc: '活动推广物料，引流转化', icon: '◮', color: '#F59E0B' },
];

const features = [
  { icon: '✨', title: 'AI智能生成', desc: '基于先进AI模型，快速生成高质量图片' },
  { icon: '📋', title: '模板复用', desc: '保存优秀Prompt模板，一键复用高效创作' },
  { icon: '📊', title: '批量变体', desc: '一键生成多种变体，方便A/B测试' },
  { icon: '🔒', title: '安全合规', desc: '商品真实展示，符合平台规范要求' },
];

const stats = [
  { value: '10,000+', label: '已生成图片' },
  { value: '98%', label: '成功率' },
  { value: '500+', label: '活跃用户' },
  { value: '50+', label: '精选模板' },
];

export default function Home() {
  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.headerContent}>
          <div className={styles.logo}>
            <span className={styles.logoIcon}>墨</span>
            <span className={styles.logoText}>墨圆AI生图</span>
          </div>
          <nav className={styles.nav}>
            <Link href="/" className={styles.navItem}>首页</Link>
            <Link href="/projects" className={styles.navItem}>项目</Link>
            <Link href="/templates" className={styles.navItem}>模板</Link>
            <Link href="/settings" className={styles.navItem}>设置</Link>
          </nav>
          <div className={styles.headerActions}>
            <Link href="/projects/new" className={styles.btnPrimary}>
              开始生成
            </Link>
          </div>
        </div>
      </header>

      <main className={styles.main}>
        <section className={styles.hero}>
          <h1 className={styles.heroTitle}>
            让电商图片创作
            <span className={styles.heroHighlight}>更简单</span>
          </h1>
          <p className={styles.heroDesc}>
            基于AI技术，快速生成商品主图、场景图、营销海报等多种类型
          </p>
          <div className={styles.heroActions}>
            <Link href="/projects/new" className={styles.btnPrimaryLarge}>
              立即开始
            </Link>
            <Link href="/templates" className={styles.btnSecondaryLarge}>
              浏览模板
            </Link>
          </div>
        </section>

        <section className={styles.templates}>
          <h2 className={styles.sectionTitle}>选择图片类型</h2>
          <div className={styles.templateGrid}>
            {templates.map((tmpl) => (
              <Link
                key={tmpl.id}
                href={`/projects/new?type=${tmpl.id}`}
                className={styles.templateCard}
                style={{ '--template-color': tmpl.color } as React.CSSProperties}
              >
                <span className={styles.templateIcon} style={{ color: tmpl.color }}>{tmpl.icon}</span>
                <span className={styles.templateName}>{tmpl.name}</span>
                <span className={styles.templateDesc}>{tmpl.desc}</span>
              </Link>
            ))}
          </div>
        </section>

        <section className={styles.features}>
          <h2 className={styles.sectionTitle}>核心能力</h2>
          <div className={styles.featureGrid}>
            {features.map((feature, index) => (
              <div key={index} className={styles.featureCard}>
                <span className={styles.featureIcon}>{feature.icon}</span>
                <div>
                  <h3 className={styles.featureTitle}>{feature.title}</h3>
                  <p className={styles.featureDesc}>{feature.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className={styles.stats}>
          {stats.map((stat, index) => (
            <div key={index} className={styles.statCard}>
              <span className={styles.statValue}>{stat.value}</span>
              <span className={styles.statLabel}>{stat.label}</span>
            </div>
          ))}
        </section>
      </main>

      <footer className={styles.footer}>
        <p>© 2024 墨圆AI生图 · 让创作更简单</p>
      </footer>
    </div>
  );
}
