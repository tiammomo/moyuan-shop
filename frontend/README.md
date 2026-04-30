# Moyuan Shop Frontend

这是墨圆电商 AI 生图项目的 Next.js 前端。

完整启动说明请优先看仓库根目录的 [README.md](../README.md)。

## 启动

进入前端目录：

```bash
cd /mnt/c/Users/caiyu/Desktop/e-commerce/moyuan-shop/frontend
```

安装依赖：

```bash
npm install
```

启动开发服务器：

```bash
npm run dev -- --hostname 127.0.0.1 --port 3000
```

浏览器打开：

```text
http://127.0.0.1:3000
```

默认情况下，前端会请求后端：

```text
http://localhost:8000
```

如果后端使用了其他端口，需要指定 `NEXT_PUBLIC_API_URL`：

```bash
NEXT_PUBLIC_API_URL=http://127.0.0.1:38110 npm run dev -- --hostname 127.0.0.1 --port 3000
```

## 常见问题

### 3000 端口被占用

换端口启动：

```bash
npm run dev -- --hostname 127.0.0.1 --port 3001
```

然后打开：

```text
http://127.0.0.1:3001
```

### 检查类型

```bash
npx tsc --noEmit
```

### 生产构建

```bash
npm run build
```
