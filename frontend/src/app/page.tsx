import Link from "next/link";
import type { CSSProperties } from "react";
import { API_BASE_URL } from "@/lib/constants";
import type { FeaturedImage } from "@/types/api";
import styles from "./page.module.css";

const navItems = [
  { label: "项目", href: "/projects", icon: "□" },
  { label: "模板", href: "/templates", icon: "▧" },
  { label: "新建", href: "/projects/new", icon: "＋" },
];

const promptCards = [
  { title: "主图焕新", tone: "warm", angle: -8 },
  { title: "场景换图", tone: "interior", angle: -3 },
  { title: "模特展示", tone: "portrait", angle: 2 },
  { title: "卖点海报", tone: "village", angle: 6 },
  { title: "套图生成", tone: "sky", angle: 10 },
];

const cases = [
  { title: "春季女包上新海报", size: "poster", tone: "caseHero" },
  { title: "家电厨房场景图", size: "wide", tone: "tower" },
  { title: "男装质感详情首屏", size: "poster", tone: "warrior" },
  { title: "家具生活方式图", size: "small", tone: "room" },
  { title: "茶饮礼盒节日海报", size: "wide", tone: "water" },
  { title: "户外装备九宫格", size: "mosaic", tone: "cabin" },
  { title: "母婴用品卖点套图", size: "wide", tone: "campus" },
  { title: "美妆新品氛围图", size: "small", tone: "street" },
  { title: "智能灯具夜景展示", size: "tall", tone: "villa" },
  { title: "办公桌搭配详情图", size: "small", tone: "study" },
  { title: "酒店香氛空间海报", size: "wide", tone: "lounge" },
  { title: "数码配件主图构图", size: "small", tone: "product" },
];

type StaticCase = (typeof cases)[number];

export default async function Home() {
  const featuredImages = await getFeaturedImages();
  const galleryItems = featuredImages.length > 0 ? featuredImages : cases;

  return (
    <div className={styles.shell}>
      <aside className={styles.sidebar} aria-label="主导航">
        <Link href="/" className={styles.brandMark} aria-label="墨圆AI电商宣传图">
          <span>墨</span>
        </Link>
        <nav className={styles.sideNav}>
          {navItems.map((item) => (
            <Link
              key={item.label}
              href={item.href}
              className={styles.sideNavItem}
            >
              <span>{item.icon}</span>
              <small>{item.label}</small>
            </Link>
          ))}
        </nav>
      </aside>

      <div className={styles.workspace}>
        <main className={styles.main}>
          <section className={styles.hero}>
            <div className={styles.heroTitle}>
              <span className={styles.heroLogo}>墨</span>
              <div>
                <h1>墨圆AI 电商宣传图制作台</h1>
                <p>为商品主图、详情页、场景图和活动海报而设计</p>
              </div>
            </div>

            <div className={styles.promptStack}>
              <div className={styles.promptBox}>
                <div className={styles.promptCards}>
                  {promptCards.map((card) => (
                    <div
                      key={card.title}
                      className={`${styles.promptCard} ${styles[card.tone]}`}
                      style={{ "--rotate": `${card.angle}deg` } as CSSProperties}
                    >
                      <strong>{card.title}</strong>
                      <span className={styles.cardImage}>
                        <i />
                      </span>
                    </div>
                  ))}
                </div>
                <div className={styles.promptCopy}>
                  <h2>电商宣传图制作</h2>
                  <p>上传商品图，选择模板或填写卖点，快速生成适合电商平台的主图、场景图、详情页和活动海报素材。</p>
                </div>
                <div className={styles.promptActions}>
                  <Link href="/projects/new" className={styles.submitButton} aria-label="开始制作宣传图">
                    <span>开始制作宣传图</span>
                    <strong>↑</strong>
                  </Link>
                  <Link href="/templates" className={styles.modelButton}>查看宣传图模板</Link>
                </div>
              </div>
            </div>
          </section>

          <section className={styles.gallerySection}>
            <div className={styles.galleryHeader}>
              <h2>精选案例</h2>
              <div className={styles.tabs}>
                <Link href="/templates" className={styles.tabActive}>推荐</Link>
                <Link href="/projects">最新</Link>
              </div>
            </div>
            <div className={styles.caseGrid}>
              {galleryItems.map((item, index) => {
                const layout = cases[index % cases.length];
                const image = "url" in item ? item : null;
                const staticCase = (image ? layout : item) as StaticCase;
                const title = image ? getFeaturedTitle(image, index) : staticCase.title;
                return (
                  <Link
                    key={image?.storage_key || title}
                    href="/projects/new"
                    className={`${styles.caseCard} ${styles[layout.size]} ${image ? styles.imageCase : styles[staticCase.tone]}`}
                  >
                    {image && (
                      <img
                        src={`${API_BASE_URL}${image.url}`}
                        alt={title}
                        className={styles.caseImage}
                        loading={index < 4 ? "eager" : "lazy"}
                      />
                    )}
                    <div className={styles.caseTexture}>
                      <span>{title}</span>
                    </div>
                  </Link>
                );
              })}
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}

async function getFeaturedImages(): Promise<FeaturedImage[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/assets/featured?limit=12`, {
      cache: "no-store",
    });
    if (!response.ok) {
      return [];
    }
    const payload = (await response.json()) as { data?: FeaturedImage[] };
    return payload.data || [];
  } catch {
    return [];
  }
}

function getFeaturedTitle(image: FeaturedImage, index: number) {
  const createdAt = new Date(image.created_at);
  if (Number.isNaN(createdAt.getTime())) {
    return `精选生成图 ${index + 1}`;
  }
  return `精选生成图 ${createdAt.toLocaleDateString("zh-CN")}`;
}
