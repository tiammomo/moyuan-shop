import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "墨圆AI生图 - 电商图片生成平台",
  description: "基于AI技术的电商图片生成平台，支持商品主图、场景图、营销海报等多种类型",
  icons: {
    icon: [
      {
        url: "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect fill='%23E85D04' width='100' height='100' rx='20'/><text y='.9em' x='50%' text-anchor='middle' font-size='70' fill='white'>墨</text></svg>",
        type: "image/svg+xml",
      },
    ],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
