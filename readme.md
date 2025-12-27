# Nature & Science 月报

一个简易静态站点示例，用于按期刊与学科展示 Nature/Science 月报文章，并支持 Markdown 详情页与 PDF 下载。

## 目录结构

- `data/summary/`：文章元数据 JSON
- `data/md/`：文章 Markdown 内容
- `data/generated/`：由脚本生成的可读 JSON 数据
- `scripts/build-data.mjs`：数据构建脚本

## 快速开始

```bash
npm run build:data
python -m http.server 8000
```

然后访问 `http://localhost:8000` 查看首页。
