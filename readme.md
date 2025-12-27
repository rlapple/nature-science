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

## 使用指南

### 生成月度报告（含文章简要信息）

```bash
node scripts/build-report.mjs --month 2024-08
```

输出文件位于 `data/generated/report-YYYY-MM.json`，包含：
- 当月文章清单
- 期刊/学科统计
- 按参考格式生成的文章简要信息（`briefs` 字段）

### 前端查看

1. 启动静态服务：
   ```bash
   python -m http.server 8000
   ```
2. 打开 `http://localhost:8000/report.html?month=YYYY-MM` 查看可视化报告。
3. 在页面右上角选择月份，切换到对应的月报与简要信息列表。

### 定时生成（示例：Linux/macOS）

使用 `cron` 每月 1 号自动生成上个月的报告：

```bash
crontab -e
```

添加：

```bash
0 3 1 * * cd /workspace/nature-science && node scripts/build-report.mjs --month "$(date -d 'last month' +\%Y-\%m)"
```

如果你的系统不支持 `date -d`，可改为手动指定月份，或在脚本中自行计算月份。
