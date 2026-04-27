import Link from 'next/link';
import styles from './page.module.css';

const projects = [
  { id: '1', name: '2024夏季新品', brand: '时尚服饰', products: 24, tasks: 89, updated: '2分钟前', status: 'active' },
  { id: '2', name: '智能家居系列', brand: '科技生活', products: 56, tasks: 234, updated: '1小时前', status: 'active' },
  { id: '3', name: '美妆护肤', brand: '美丽在线', products: 38, tasks: 156, updated: '3小时前', status: 'active' },
  { id: '4', name: '母婴用品', brand: '宝贝成长', products: 42, tasks: 198, updated: '昨天', status: 'paused' },
];

export default function ProjectsPage() {
  return (
    <div className={styles.shell}>
      <aside className={styles.sidebar} aria-label="主导航">
        <Link href="/" className={styles.brandMark} aria-label="墨圆AI电商宣传图">
          <span>墨</span>
        </Link>
        <nav className={styles.sideNav}>
          <Link href="/projects" className={`${styles.sideNavItem} ${styles.sideNavItemActive}`}><span>□</span><small>项目</small></Link>
          <Link href="/templates" className={styles.sideNavItem}><span>▧</span><small>模板</small></Link>
          <Link href="/projects/new" className={styles.sideNavItem}><span>＋</span><small>新建</small></Link>
        </nav>
      </aside>

      <div className={styles.workspace}>
        <main className={styles.main}>
          <div className={styles.pageHeader}>
            <div>
              <h1 className={styles.title}>我的项目</h1>
              <p className={styles.subtitle}>管理你的电商宣传图制作项目</p>
            </div>
            <Link href="/projects/new" className={styles.btnPrimary}>新建项目</Link>
          </div>

          <div className={styles.projectsGrid}>
            {projects.map((project) => (
              <Link key={project.id} href={`/projects/${project.id}`} className={styles.projectCard}>
                <div className={styles.projectHeader}>
                  <div className={styles.projectAvatar}>
                    {project.name.charAt(0)}
                  </div>
                  <span className={`${styles.projectStatus} ${styles[project.status]}`}>
                    {project.status === 'active' ? '进行中' : '已暂停'}
                  </span>
                </div>
                <h3 className={styles.projectName}>{project.name}</h3>
                <span className={styles.projectBrand}>{project.brand}</span>
                <div className={styles.projectStats}>
                  <span>{project.products} 个商品</span>
                  <span>·</span>
                  <span>{project.tasks} 个任务</span>
                </div>
                <div className={styles.projectFooter}>
                  <span className={styles.projectUpdated}>最后更新：{project.updated}</span>
                </div>
              </Link>
            ))}

            <Link href="/projects/new" className={styles.addProjectCard}>
              <span className={styles.addIcon}>+</span>
              <span className={styles.addText}>创建新项目</span>
            </Link>
          </div>
        </main>
      </div>
    </div>
  );
}
