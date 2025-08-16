# 🎬 VEO3视频生成集成指南

## 📋 功能概述

现在系统已经完整集成了OpenAI双prompt生成和VEO3视频生成功能，实现了：

1. **智能内容分析**: OpenAI分析用户输入，生成专业的视频和音频prompt
2. **AI视频生成**: VEO3根据视频prompt自动生成AI视频
3. **完整工作流**: 一键完成从用户想法到最终视频的全流程

## 🚀 环境配置

### 1. 安装依赖
```bash
pip install aiohttp==3.9.3 aiofiles==23.2.0
```

### 2. 环境变量配置
在 `backend/.env` 文件中添加：
```env
# OpenAI配置
OPENAI_API_KEY=sk-your-openai-key-here

# VEO3配置
VEO3_API_KEY=your-veo3-api-key-here
VEO3_BASE_URL=https://api.qingyuntop.top
VEO3_MODEL=veo3-fast
```

## 📡 API接口

### 1. 完整工作流程接口 (推荐)

**POST** `/content-generation/complete-workflow`

一次调用完成全流程：用户输入 → 内容分析 → prompt生成 → 视频创建

#### 请求示例
```json
{
    "user_input": "制作一个关于日落的唯美视频，配上诗意的旁白",
    "user_context": "用于艺术欣赏",
    "output_video_id": 12345,
    "veo3_model": "veo3-fast",
    "enhance_prompt": true,
    "image_url": null
}
```

#### 响应示例
```json
{
    "success": true,
    "analysis": {
        "main_theme": "日落美景与艺术表达",
        "key_elements": ["日落", "唯美", "诗意旁白"],
        "style_preference": "艺术唯美",
        "mood": "宁静抒情"
    },
    "video_prompt": "A breathtaking sunset scene over calm waters, golden hour lighting...",
    "audio_prompt": "在这个黄昏时刻，太阳正缓缓沉入地平线...",
    "video_generation": {
        "success": true,
        "task_id": "task_abc123",
        "output_path": "/backend/temp/generated_video/12345.mp4",
        "file_size": 15420000,
        "video_url": "https://...",
        "elapsed_seconds": 45.2
    }
}
```

### 2. 分步接口

#### 步骤1: 分析内容生成prompt
**POST** `/content-generation/analyze`

#### 步骤2: 使用prompt生成视频
**POST** `/content-generation/generate-video`

```json
{
    "video_prompt": "AI生成的视频描述",
    "output_video_id": 12345,
    "model": "veo3-fast",
    "enhance_prompt": true,
    "image_url": "https://example.com/image.jpg"  // 可选：图片转视频
}
```

### 3. 健康检查
**GET** `/content-generation/health`

检查所有服务状态：
```json
{
    "status": "healthy",
    "message": "All content generation services are operational",
    "services": {
        "openai": {
            "configured": true,
            "model": "gpt-4"
        },
        "veo3": {
            "configured": true,
            "base_url": "https://api.qingyuntop.top"
        }
    }
}
```

## 🧪 测试指南

### 快速测试
```bash
cd backend
python test_complete_workflow.py
```

### 启动服务测试
```bash
# 终端1: 启动API服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 终端2: 测试完整工作流程
curl -X POST "http://localhost:8000/content-generation/complete-workflow" \
     -H "Content-Type: application/json" \
     -d '{
       "user_input": "制作一个科技感的产品展示视频",
       "user_context": "产品宣传",
       "output_video_id": 999,
       "veo3_model": "veo3-fast",
       "enhance_prompt": true
     }'
```

## 🔧 配置说明

### VEO3模型选择
- `veo3-fast`: 快速生成，适合预览
- `veo3-quality`: 高质量生成，耗时较长

### 视频生成参数
- `enhance_prompt`: 是否增强prompt (推荐开启)
- `image_url`: 图片转视频功能 (可选)
- `output_video_id`: 输出视频的唯一ID

### 时间配置
- 轮询间隔: 5秒
- 最大等待: 15分钟
- 超时设置: 30秒

## 📁 文件结构

```
backend/
├── app/
│   ├── services/
│   │   ├── openai_service.py          # OpenAI内容分析
│   │   └── veo3_service.py            # VEO3视频生成 (新增)
│   └── routers/
│       └── content_generation.py      # 完整API路由 (扩展)
├── temp/
│   └── generated_video/               # 生成的视频文件
├── config.py                          # VEO3配置 (更新)
├── requirements.txt                    # 新增依赖 (更新)
└── test_complete_workflow.py          # 完整测试 (新增)
```

## ⚠️ 注意事项

1. **API密钥安全**: 确保VEO3和OpenAI密钥安全存储
2. **网络稳定**: 视频生成需要稳定的网络连接
3. **存储空间**: 生成的视频文件需要足够的磁盘空间
4. **处理时间**: 视频生成可能需要1-15分钟，请设置合理的超时时间

## 🚀 使用场景

### 1. 内容创作
```python
# 用户想法 → AI视频
user_input = "制作一个温馨的家庭聚餐视频"
# 系统自动生成专业的视频描述和实际视频文件
```

### 2. 产品宣传
```python
# 产品描述 → 宣传视频
user_input = "展示我们新AI助手的强大功能"
# 生成科技感十足的产品展示视频
```

### 3. 教育内容
```python
# 教学概念 → 可视化视频
user_input = "解释太阳系的运行原理"
# 生成直观的教学视频
```

## 📈 性能优化

1. **并发处理**: VEO3服务支持异步处理
2. **缓存机制**: 可以缓存生成的prompt和视频
3. **队列管理**: 对于大量请求可以添加任务队列
4. **进度跟踪**: 实时监控视频生成进度

## 🔄 下一步扩展

- [ ] 添加TTS语音合成集成
- [ ] 实现视频+音频合并
- [ ] 添加用户偏好学习
- [ ] 支持批量视频生成
- [ ] 添加视频预览功能
