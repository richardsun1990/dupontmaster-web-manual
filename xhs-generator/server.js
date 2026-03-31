/**
 * 小红书图片生成API
 * 
 * 功能：
 * 1. 分析用户输入内容
 * 2. 生成多张小红书风格的图片
 * 3. 合并多张图片为一张长图
 * 
 * 依赖：
 * - baoyu-image-gen: 图片生成
 * - 图片合并库
 */

const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs').promises;
const { spawn } = require('child_process');

// 配置
const CONFIG = {
    port: 3001,
    outputDir: path.join(__dirname, 'outputs'),
    maxImages: 6,
    imageWidth: 1080,
    imageHeight: 1920, // 9:16 小红书竖版
};

const app = express();
app.use(express.json({ limit: '10mb' }));

// 确保输出目录存在
async function ensureDirectories() {
    const dirs = [CONFIG.outputDir, path.join(CONFIG.outputDir, 'images')];
    for (const dir of dirs) {
        await fs.mkdir(dir, { recursive: true });
    }
}

// 生成唯一ID
function generateId() {
    return `xhs_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

// 分析内容，生成图片提示词
function analyzeContent(content, style, layout, imageCount) {
    const prompts = [];
    
    // 封面
    prompts.push({
        type: 'cover',
        prompt: `小红书风格封面图：${content.substring(0, 100)}
        
设计要求：
- 吸引眼球的标题风格
- 清晰的信息层次
- 适合小红书平台的配色
- 风格：${style} / 布局：${layout}
- 竖版比例 9:16
- 包含适当的装饰元素
- 中文文字清晰可见`
    });
    
    // 内容页
    const contentParts = splitContent(content, imageCount - 2);
    contentParts.forEach((part, index) => {
        prompts.push({
            type: 'content',
            prompt: `小红书风格内容图（第${index + 2}页）：${part}
            
设计要求：
- 保持视觉一致性
- 信息密度适中
- 风格：${style} / 布局：${layout}
- 竖版比例 9:16
- 中文排版美观
- 适当的留白和装饰`
        });
    });
    
    // 结尾页
    prompts.push({
        type: 'ending',
        prompt: `小红书风格结尾图：
        
设计要求：
- 引导关注/收藏的呼吁
- 简洁有力的收尾
- 风格：${style}
- 竖版比例 9:16
- 包含适当的CTA元素
- 中文文字清晰可见`
    });
    
    return prompts;
}

// 拆分内容
function splitContent(content, parts) {
    const sentences = content.split(/[。！？\n]/).filter(s => s.trim());
    const partSize = Math.ceil(sentences.length / parts);
    const result = [];
    
    for (let i = 0; i < parts; i++) {
        const start = i * partSize;
        const end = start + partSize;
        const part = sentences.slice(start, end).join('。');
        if (part) result.push(part);
    }
    
    return result;
}

// 执行图片生成
async function generateImageWithScript(prompt, outputPath, sessionId) {
    return new Promise((resolve, reject) => {
        const bunPath = process.platform === 'win32' ? 'bun.cmd' : 'bun';
        const scriptPath = path.join(__dirname, 'scripts', 'generate_image.ts');
        
        const args = [
            scriptPath,
            '--prompt', prompt,
            '--image', outputPath,
            '--ar', '9:16',
            '--quality', '2k',
            '--sessionId', sessionId
        ];
        
        const proc = spawn(bunPath, args, {
            stdio: ['ignore', 'pipe', 'pipe'],
            shell: false
        });
        
        let stdout = '';
        let stderr = '';
        
        proc.stdout.on('data', (data) => {
            stdout += data.toString();
            console.log('[stdout]', data.toString().trim());
        });
        
        proc.stderr.on('data', (data) => {
            stderr += data.toString();
            console.error('[stderr]', data.toString().trim());
        });
        
        proc.on('close', (code) => {
            if (code === 0) {
                resolve(outputPath);
            } else {
                reject(new Error(`生成失败: ${stderr || stdout}`));
            }
        });
        
        proc.on('error', (err) => {
            reject(err);
        });
        
        // 超时处理
        setTimeout(() => {
            proc.kill();
            reject(new Error('生成超时'));
        }, 120000);
    });
}

// 合并图片
async function mergeImages(imagePaths, outputPath) {
    // 使用Canvas API合并
    const createCanvas = require('canvas');
    const canvas = createCanvas(CONFIG.imageWidth, CONFIG.imageHeight * imagePaths.length);
    const ctx = canvas.getContext('2d');
    
    for (let i = 0; i < imagePaths.length; i++) {
        const img = await loadImage(imagePaths[i]);
        ctx.drawImage(img, 0, i * CONFIG.imageHeight);
    }
    
    const buffer = canvas.toBuffer('image/png');
    await fs.writeFile(outputPath, buffer);
}

// 加载图片
function loadImage(filePath) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => resolve(img);
        img.onerror = reject;
        img.src = `file://${filePath}`;
    });
}

// API: 生成图片
app.post('/api/generate-xhs-images', async (req, res) => {
    try {
        const { content, style, layout, imageCount } = req.body;
        
        if (!content) {
            return res.status(400).json({ error: '内容不能为空' });
        }
        
        const id = generateId();
        const sessionDir = path.join(CONFIG.outputDir, 'images', id);
        await fs.mkdir(sessionDir, { recursive: true });
        
        // 分析内容生成提示词
        const prompts = analyzeContent(content, style, layout, imageCount);
        
        const images = [];
        const sessionId = `xhs-${id}`;
        
        // 逐个生成图片
        for (let i = 0; i < prompts.length; i++) {
            const outputPath = path.join(sessionDir, `${i + 1}.png`);
            
            // 检查是否已有生成的图片（支持断点续传）
            if (await fs.access(outputPath).then(() => true).catch(() => false)) {
                images.push(`/outputs/images/${id}/${i + 1}.png`);
                continue;
            }
            
            try {
                await generateImageWithScript(prompts[i].prompt, outputPath, sessionId);
                images.push(`/outputs/images/${id}/${i + 1}.png`);
            } catch (err) {
                console.error(`生成第${i + 1}张图片失败:`, err);
                // 继续生成后续图片
            }
        }
        
        // 合并图片
        const mergedPath = path.join(sessionDir, 'merged.png');
        try {
            await mergeImages(
                images.map(p => path.join(CONFIG.outputDir, '..', p)),
                mergedPath
            );
        } catch (err) {
            console.error('合并图片失败:', err);
        }
        
        res.json({
            success: true,
            sessionId: id,
            images: images,
            mergedImage: `/outputs/images/${id}/merged.png`
        });
        
    } catch (error) {
        console.error('生成失败:', error);
        res.status(500).json({ error: error.message });
    }
});

// API: 获取生成状态
app.get('/api/status/:sessionId', (req, res) => {
    const { sessionId } = req.params;
    const sessionDir = path.join(CONFIG.outputDir, 'images', sessionId);
    
    fs.readdir(sessionDir)
        .then(files => {
            res.json({
                sessionId,
                images: files.filter(f => f.endsWith('.png')).length,
                status: 'completed'
            });
        })
        .catch(() => {
            res.status(404).json({ error: 'Session not found' });
        });
});

// 启动服务器
async function start() {
    await ensureDirectories();
    
    app.listen(CONFIG.port, () => {
        console.log(`小红书图片生成服务已启动: http://localhost:${CONFIG.port}`);
        console.log(`输出目录: ${CONFIG.outputDir}`);
    });
}

start().catch(console.error);

// 错误处理
process.on('uncaughtException', (err) => {
    console.error('未捕获的异常:', err);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('未处理的Promise拒绝:', reason);
});