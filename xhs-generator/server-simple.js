/**
 * 小红书图片生成工具 - 简化版（前端直接生成）
 * 
 * 这个版本可以在没有后端的情况下工作
 * 直接通过浏览器调用图片生成API
 */

const express = require('express');
const path = require('path');
const fs = require('fs').promises;
const { spawn } = require('child_process');

const CONFIG = {
    port: process.env.PORT || 3001,
    publicDir: path.join(__dirname, 'public'),
    sessionDir: path.join(__dirname, 'sessions'),
    maxImages: 6
};

// 确保目录存在
async function ensureDir(dir) {
    await fs.mkdir(dir, { recursive: true });
}

const app = express();
app.use(express.json());
app.use(express.static(CONFIG.publicDir));

// 分析内容生成提示词
function generatePrompts(content, style, layout, count) {
    const prompts = [];
    const sentences = content.split(/[。！？\n]/).filter(s => s.trim());
    const partSize = Math.ceil(sentences.length / Math.max(count - 2, 1));
    
    const styleMap = {
        'notion': { desc: '知识风格，手绘线条，极简', color: '#f5f5f5' },
        'chalkboard': { desc: '黑板风格，粉笔质感，教育感', color: '#2c3e50' },
        'cute': { desc: '可爱风格，柔和色调，少女风', color: '#ffeaa7' },
        'bold': { desc: '强烈风格，高对比度，冲击力', color: '#e74c3c' },
        'minimal': { desc: '简约风格，大量留白，高级感', color: '#ffffff' }
    };
    
    const layoutDesc = {
        'dense': '信息密集展示',
        'balanced': '平衡布局',
        'sparse': '稀疏留白',
        'list': '清单列表形式',
        'flow': '流程图形式',
        'comparison': '对比展示形式'
    };
    
    const s = styleMap[style] || styleMap['notion'];
    
    // 封面
    prompts.push({
        index: 1,
        type: '封面',
        prompt: `小红书风格封面图：
        
主题：${content.substring(0, 80)}...

设计：${s.desc}，${layoutDesc[layout] || '平衡布局'}
配色：浅色背景配深色文字
比例：9:16 竖版
要求：中文文字清晰，视觉冲击力强，适合小红书平台`
    });
    
    // 内容页
    for (let i = 0; i < count - 2; i++) {
        const start = i * partSize;
        const part = sentences.slice(start, start + partSize).join('。').substring(0, 150);
        prompts.push({
            index: i + 2,
            type: '内容页',
            prompt: `小红书风格内容图（第${i + 2}页）：
            
要点：${part}...

设计：${s.desc}，${layoutDesc[layout] || '平衡布局'}
比例：9:16 竖版
要求：保持风格一致，内容清晰易读`
        });
    }
    
    // 结尾
    prompts.push({
        index: count,
        type: '结尾',
        prompt: `小红书风格结尾图：

设计：${s.desc}，呼吁关注收藏
比例：9:16 竖版
要求：简洁有力，引导互动，中文文字清晰可见`
    });
    
    return prompts;
}

// 生成图片的子进程
async function generateImage(prompt, outputPath, sessionId, index) {
    return new Promise((resolve, reject) => {
        const baseDir = path.join(require('os').homedir(), '.agents/skills/baoyu-image-gen');
        const bunPath = process.platform === 'win32' ? 'bun.cmd' : 'bun';
        const scriptPath = path.join(baseDir, 'scripts', 'main.ts');
        
        // 构建prompt文件
        const promptFile = path.join(CONFIG.sessionDir, sessionId, `prompt-${index}.md`);
        
        require('fs').promises.writeFile(promptFile, prompt).then(() => {
            const args = [
                scriptPath,
                '--promptfiles', promptFile,
                '--image', outputPath,
                '--ar', '9:16',
                '--quality', '2k',
                '--provider', process.env.IMAGE_PROVIDER || 'dashscope'
            ];
            
            if (process.env.IMAGE_MODEL) {
                args.push('--model', process.env.IMAGE_MODEL);
            }
            
            const proc = spawn(bunPath, args, {
                stdio: ['ignore', 'pipe', 'pipe'],
                shell: false
            });
            
            let stdout = '';
            let stderr = '';
            
            proc.stdout.on('data', (data) => {
                stdout += data.toString();
            });
            
            proc.stderr.on('data', (data) => {
                stderr += data.toString();
                console.log('[baoyu-image-gen]', data.toString().trim());
            });
            
            proc.on('close', (code) => {
                if (code === 0) {
                    resolve(outputPath);
                } else {
                    reject(new Error(`生成失败 (code ${code}): ${stderr}`));
                }
            });
            
            proc.on('error', reject);
            
            // 5分钟超时
            setTimeout(() => {
                proc.kill();
                reject(new Error('生成超时'));
            }, 300000);
            
        }).catch(reject);
    });
}

// 合并图片
async function mergeImages(imagePaths, outputPath) {
    try {
        const { createCanvas } = require('canvas');
        const canvas = createCanvas(1080, 1920 * imagePaths.length);
        const ctx = canvas.getContext('2d');
        
        for (let i = 0; i < imagePaths.length; i++) {
            const img = await loadImage(imagePaths[i]);
            ctx.drawImage(img, 0, i * 1920, 1080, 1920);
        }
        
        const buffer = canvas.toBuffer('image/png');
        await fs.writeFile(outputPath, buffer);
    } catch (err) {
        console.error('合并失败:', err);
        // 如果合并失败，返回第一张图片
        if (imagePaths.length > 0) {
            return imagePaths[0];
        }
        throw err;
    }
}

function loadImage(filePath) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => resolve(img);
        img.onerror = reject;
        img.src = `file://${filePath}`;
    });
}

// API: 生成图片
app.post('/api/generate', async (req, res) => {
    const { content, style = 'notion', layout = 'dense', count = 4 } = req.body;
    
    if (!content || content.trim().length < 10) {
        return res.status(400).json({ error: '内容太短，至少需要10个字符' });
    }
    
    const sessionId = `xhs_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`;
    const sessionPath = path.join(CONFIG.sessionDir, sessionId);
    
    try {
        await ensureDir(sessionPath);
        
        const prompts = generatePrompts(content, style, layout, Math.min(count, CONFIG.maxImages));
        const images = [];
        
        // 逐个生成
        for (let i = 0; i < prompts.length; i++) {
            const p = prompts[i];
            const outputPath = path.join(sessionPath, `${p.index}.png`);
            
            // 发送进度（通过Server-Sent Events或轮询）
            console.log(`[${sessionId}] 正在生成第 ${p.index}/${prompts.length} 张...`);
            
            try {
                await generateImage(p.prompt, outputPath, sessionId, p.index);
                images.push(`/sessions/${sessionId}/${p.index}.png`);
            } catch (err) {
                console.error(`生成第${p.index}张失败:`, err.message);
                // 跳过失败的图片继续
            }
        }
        
        // 合并
        let mergedPath = null;
        if (images.length > 1) {
            mergedPath = path.join(sessionPath, 'merged.png');
            try {
                const fullPaths = images.map(img => path.join(CONFIG.sessionDir, img));
                await mergeImages(fullPaths, mergedPath);
                mergedPath = `/sessions/${sessionId}/merged.png`;
            } catch (err) {
                console.error('合并失败:', err);
                mergedPath = images[images.length - 1]; // 用最后一张
            }
        } else if (images.length === 1) {
            mergedPath = images[0];
        }
        
        res.json({
            success: true,
            sessionId,
            images,
            mergedImage: mergedPath,
            count: images.length
        });
        
    } catch (error) {
        console.error('生成失败:', error);
        res.status(500).json({ error: error.message });
    }
});

// 状态查询
app.get('/api/status/:sessionId', async (req, res) => {
    const { sessionId } = req.params;
    const sessionPath = path.join(CONFIG.sessionDir, sessionId);
    
    try {
        const files = await fs.readdir(sessionPath);
        const images = files.filter(f => f.match(/^\d+\.png$/));
        
        res.json({
            sessionId,
            images: images.length,
            files
        });
    } catch {
        res.status(404).json({ error: 'Session not found' });
    }
});

// 列出所有sessions
app.get('/api/sessions', async (req, res) => {
    try {
        const dirs = await fs.readdir(CONFIG.sessionDir);
        res.json({ sessions: dirs });
    } catch {
        res.json({ sessions: [] });
    }
});

// 启动
async function main() {
    await ensureDir(CONFIG.publicDir);
    await ensureDir(CONFIG.sessionDir);
    
    app.listen(CONFIG.port, () => {
        console.log(`
╔══════════════════════════════════════════════════════╗
║        🎨 小红书图片生成器 - DuPont Master             ║
╠══════════════════════════════════════════════════════╣
║  访问地址: http://localhost:${CONFIG.port}                    ║
║  输出目录: ${CONFIG.sessionDir}                          
║  API端点: POST /api/generate                            ║
╚══════════════════════════════════════════════════════╝
        `);
    });
}

main().catch(console.error);