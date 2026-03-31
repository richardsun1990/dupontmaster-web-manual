# 🎨 小红书图片生成器

DuPont Master 财务分析内容创作工具

## 功能特性

- 📝 **智能分析**: 自动分析输入内容，提取关键信息
- 🎨 **多风格选择**: 支持知识卡片、教程、黑板、可爱、简约等风格
- 📊 **多种布局**: 密集型、平衡型、稀疏型、列表、流程、对比
- 📱 **多图拼接**: 多张独立图自动合并为一张长图，适合小红书发布
- 🚀 **一键生成**: 简单输入，快速生成专业级小红书图片

## 快速开始

### 方式1: 完整版（需要Node.js后端）

```bash
# 1. 进入目录
cd xhs-generator

# 2. 安装依赖
npm install

# 3. 启动服务
npm start

# 4. 访问 http://localhost:3001
```

### 方式2: 纯前端版（无需安装）

直接在浏览器打开 `standalone.html`

### 方式3: 集成到现有网站

将 `index.html` 和相关资源部署到现有网站即可。

## API 使用

### 生成图片

```bash
curl -X POST http://localhost:3001/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "content": "泸州老窖2024年财务分析：营收增长15%，净利润创新高...",
    "style": "notion",
    "layout": "dense",
    "count": 4
  }'
```

### 查询状态

```bash
curl http://localhost:3001/api/status/{sessionId}
```

## 配置说明

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| PORT | 3001 | 服务端口 |
| IMAGE_PROVIDER | dashscope | 图片生成服务商 |
| IMAGE_MODEL | qwen-image-2.0-pro | 使用的模型 |
| DASHSCOPE_API_KEY | - | 阿里云API密钥 |

### 设置API密钥

```bash
# Linux/Mac
export DASHSCOPE_API_KEY=your_api_key_here

# Windows PowerShell
$env:DASHSCOPE_API_KEY="your_api_key_here"
```

## 部署到 Vercel

1. 将整个 `xhs-generator` 目录推送到GitHub
2. 在Vercel创建新项目，导入仓库
3. 添加环境变量 `DASHSCOPE_API_KEY`
4. 部署

注意：Vercel无状态部署，每次生成会重置。建议使用独立服务器或云函数。

## 样式预设

| 预设 | 风格 | 布局 | 适用场景 |
|------|------|------|----------|
| 知识卡片 | notion | dense | 干货知识、概念科普 |
| 教程步骤 | chalkboard | flow | 操作指南、流程说明 |
| 清单列表 | notion | list | 排行榜、必备清单 |
| 产品对比 | fresh | comparison | 对比分析、测评 |

## 目录结构

```
xhs-generator/
├── index.html          # 主界面
├── standalone.html     # 独立版（无需后端）
├── server-simple.js    # 简化版服务端
├── server.js           # 完整版服务端
├── package.json        # Node.js配置
└── README.md           # 说明文档
```

## 依赖

- Node.js >= 16
- canvas (用于图片合并)
- baoyu-image-gen (用于AI图片生成，需要单独安装)

## 技术方案

### 前端
- HTML5 + CSS3 + Vanilla JS
- 响应式设计，适配移动端
- Canvas API 本地图片合并

### 后端
- Express.js 轻量级服务
- 集成 baoyu-image-gen 生成图片
- 会话管理，图片存储

### 图片生成
- 使用阿里云通义万相 (DashScope)
- 支持多种风格和布局
- 9:16 竖版比例（小红书标准）

## 常见问题

### Q: 生成的图片不清晰？
A: 确保API密钥有效，调整 `--quality` 参数为 `2k`

### Q: 如何修改风格？
A: 在前端界面选择不同的预设，或直接调用API指定 `style` 和 `layout`

### Q: 支持其他图片尺寸吗？
A: 当前固定为9:16比例，可修改代码中的 `imageHeight` 和 `imageWidth`

## License

MIT License - DuPont Master