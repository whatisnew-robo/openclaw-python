# 🚀 OpenClaw Python - 快速开始

> 5 分钟快速上手 OpenClaw Python

---

## 📋 前提条件

```bash
✅ Python 3.11 或更高
✅ uv 包管理器
✅ 至少一个 LLM API Key（选择一个即可）:
   - Anthropic Claude (推荐)
   - OpenAI GPT
   - Google Gemini
   - AWS Bedrock
   - Ollama (本地，免费)
```

---

## ⚡ 快速安装

### 1. 克隆项目

```bash
git clone https://github.com/zhaoyuong/openclaw-python.git
cd openclaw-python
```

### 2. 安装 uv（如果还没有）

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. 安装依赖

```bash
uv sync
```

### 4. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env，添加你的 API key（选择一个即可）
nano .env  # 或使用其他编辑器
```

**`.env` 配置示例**（至少选择一个）:

```bash
# 选项 1: Anthropic Claude (推荐)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# 选项 2: OpenAI GPT
OPENAI_API_KEY=sk-your-key-here

# 选项 3: Google Gemini
GOOGLE_API_KEY=your-gemini-key-here

# 选项 4: AWS Bedrock
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1

# 选项 5: Ollama (本地，免费 - 需要先运行 ollama serve)
# 不需要 API key，只需运行: ollama serve
```

---

## 🎯 使用方式

### 方式 1: 命令行对话（推荐入门）

```bash
# 使用默认模型对话
uv run openclaw agent chat "你好，介绍一下你自己"

# 指定使用 Claude
uv run openclaw agent chat "帮我写一个 Python 函数" --model anthropic/claude-opus-4-5

# 指定使用 GPT
uv run openclaw agent chat "今天天气怎么样？" --model openai/gpt-4

# 使用 Gemini
uv run openclaw agent chat "解释一下量子计算" --model gemini-3-flash-preview
```

### 方式 2: 交互式对话

```bash
# 启动交互式会话（推荐）
uv run openclaw agent interactive

# 或指定模型
uv run openclaw agent interactive --model anthropic/claude-opus-4-5
```

**交互模式命令**:
```
/help    - 查看帮助
/status  - 查看状态
/reset   - 重置会话
/exit    - 退出
```

### 方式 3: 启动 API 服务器

```bash
# 启动 API 服务器（后台服务）
uv run openclaw api start

# 默认端口: 18789
# API 文档: http://localhost:18789/docs
```

**使用 API**:
```bash
# 发送消息
curl -X POST http://localhost:18789/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "model": "anthropic/claude-opus-4-5",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

### 方式 4: Python 脚本

```python
# 创建文件: my_agent.py
import asyncio
from openclaw.agents import AgentRuntime, Session
from pathlib import Path

async def main():
    # 创建 agent runtime
    runtime = AgentRuntime(
        model="anthropic/claude-opus-4-5",  # 或其他模型
        max_tokens=1000,
        temperature=0.7
    )
    
    # 创建会话
    session = Session(
        session_id="my-session",
        workspace_dir=Path.cwd()
    )
    
    # 发送消息
    response = await runtime.run_turn(
        session=session,
        user_message="你好！请介绍一下你自己。"
    )
    
    # 输出响应
    async for event in response:
        if event["type"] == "text":
            print(event["text"], end="", flush=True)
    
    print()

# 运行
asyncio.run(main())
```

运行脚本:
```bash
uv run python my_agent.py
```

---

## 🤖 支持的 LLM Provider

### 1. Anthropic Claude（推荐）

```bash
# .env 配置
ANTHROPIC_API_KEY=sk-ant-your-key-here

# 使用
uv run openclaw agent chat "Hello" --model anthropic/claude-opus-4-5
```

**可用模型**:
- `anthropic/claude-opus-4-5` - 最强大
- `anthropic/claude-sonnet-4-5` - 平衡性能
- `anthropic/claude-haiku-4` - 快速便宜

### 2. OpenAI GPT

```bash
# .env 配置
OPENAI_API_KEY=sk-your-key-here

# 使用
uv run openclaw agent chat "Hello" --model openai/gpt-4
```

**可用模型**:
- `openai/gpt-4` - GPT-4
- `openai/gpt-4-turbo` - GPT-4 Turbo
- `openai/gpt-3.5-turbo` - GPT-3.5

### 3. Google Gemini

```bash
# .env 配置
GOOGLE_API_KEY=your-gemini-key-here

# 使用
uv run openclaw agent chat "Hello" --model gemini-3-flash-preview
```

**可用模型**:
- `gemini-3-flash-preview` - 最新最快
- `gemini-3-pro-preview` - 最强大
- `gemini-2.5-flash` - 稳定版

### 4. AWS Bedrock

```bash
# .env 配置
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1

# 使用
uv run openclaw agent chat "Hello" --model bedrock/anthropic.claude-3-sonnet
```

### 5. Ollama（本地，免费）

```bash
# 先启动 Ollama 服务
ollama serve

# 拉取模型（首次使用）
ollama pull llama3.2

# 使用
uv run openclaw agent chat "Hello" --model ollama/llama3.2
```

**优势**: 完全免费，本地运行，数据隐私

---

## 📝 基本使用示例

### 简单对话

```bash
uv run openclaw agent chat "什么是 Python？"
```

### 代码生成

```bash
uv run openclaw agent chat "写一个计算斐波那契数列的 Python 函数"
```

### 文本分析

```bash
uv run openclaw agent chat "分析这段文字的情感：今天天气真好，心情也很愉快！"
```

### 翻译

```bash
uv run openclaw agent chat "把这段话翻译成英文：人工智能正在改变世界"
```

---

## 🛠️ 常用配置

### 设置默认模型

编辑 `~/.openclaw/openclaw.json`:

```json
{
  "agent": {
    "model": "anthropic/claude-opus-4-5",
    "max_tokens": 2000,
    "temperature": 0.7
  }
}
```

### 使用工具（可选）

```python
from openclaw.agents import AgentRuntime

runtime = AgentRuntime(
    model="anthropic/claude-opus-4-5",
    enable_tools=True,  # 启用工具
    allowed_tools=["bash", "read_file", "write_file"]  # 指定允许的工具
)
```

**注意**: 工具可以执行命令和操作文件，请谨慎使用！

---

## 📚 更多示例

### 查看所有示例

```bash
ls examples/
```

**可用示例**:
- `01_basic_agent.py` - 基础用法
- `02_with_tools.py` - 使用工具
- `03_streaming.py` - 流式输出
- `04_api_server.py` - API 服务器
- `08_advanced_features.py` - 高级特性
- `09_v0.6_features.py` - v0.6.0 新功能

### 运行示例

```bash
uv run python examples/01_basic_agent.py
```

---

## 🔧 故障排除

### 问题 1: 找不到 API key

```bash
错误: API key not found

解决:
1. 检查 .env 文件是否存在
2. 确认 API key 已正确配置
3. 检查环境变量名称是否正确
```

### 问题 2: 模型名称错误

```bash
错误: Invalid model name

解决:
使用正确的模型名称格式:
- anthropic/claude-opus-4-5
- openai/gpt-4
- gemini-3-flash-preview
```

### 问题 3: 网络连接错误

```bash
错误: Connection timeout

解决:
1. 检查网络连接
2. 确认 API key 有效
3. 尝试使用代理（如需要）
```

---

## 🎯 推荐使用流程

### 新手入门

1. **安装配置**（5 分钟）
   ```bash
   git clone https://github.com/zhaoyuong/openclaw-python.git
   cd openclaw-python
   uv sync
   cp .env.example .env
   # 编辑 .env 添加 API key
   ```

2. **首次测试**（1 分钟）
   ```bash
   uv run openclaw agent chat "你好，测试一下"
   ```

3. **交互式使用**（推荐日常使用）
   ```bash
   uv run openclaw agent interactive
   ```

### 进阶使用

1. **API 服务器**（适合集成）
   ```bash
   uv run openclaw api start
   ```

2. **Python 脚本**（适合自动化）
   ```python
   # 创建自己的脚本
   ```

3. **工具和高级特性**
   ```bash
   # 查看高级功能示例
   uv run python examples/08_advanced_features.py
   ```

---

## 📖 进一步学习

### 文档

- **完整文档**: [docs/README.md](docs/README.md)
- **配置参考**: [docs/guides/ADVANCED_FEATURES.md](docs/guides/ADVANCED_FEATURES.md)
- **安全指南**: [SECURITY_CHECK_REPORT.md](SECURITY_CHECK_REPORT.md)

### 测试脚本

```bash
# Gemini 测试
uv run python tests/manual/test_gemini_3_flash.py

# Google Search 测试
uv run python tests/manual/test_google_search_peppa.py

# Telegram 测试（需要配置 token）
uv run python tests/manual/test_telegram_restricted.py
```

---

## 💡 提示

### 选择合适的 Provider

| Provider | 优势 | 适用场景 |
|----------|------|----------|
| **Anthropic Claude** | 强大、安全、长上下文 | 复杂任务、代码生成 |
| **OpenAI GPT** | 生态成熟、API 稳定 | 通用对话、集成项目 |
| **Google Gemini** | 免费额度大、速度快 | 测试、简单任务 |
| **Ollama** | 完全免费、数据隐私 | 本地开发、离线使用 |

### 成本考虑

- **免费测试**: Gemini 或 Ollama
- **生产环境**: Claude 或 GPT-4
- **预算有限**: GPT-3.5 或 Gemini Flash

---

## ❓ 常见问题

**Q: 必须使用 Gemini 吗？**  
A: 不是！OpenClaw 支持多种 LLM，选择任何一个即可。

**Q: 推荐哪个 Provider？**  
A: Anthropic Claude（强大）或 Ollama（免费本地）。

**Q: 如何切换模型？**  
A: 使用 `--model` 参数或修改配置文件。

**Q: 是否支持本地运行？**  
A: 是！使用 Ollama 可以完全本地运行，无需 API key。

---

## 🚀 开始使用吧！

```bash
# 最简单的开始方式
cd openclaw-python
uv sync
cp .env.example .env
# 添加任何一个 API key
uv run openclaw agent chat "Hello, OpenClaw!"
```

**🦞 欢迎使用 OpenClaw Python！**

---

**需要帮助？**
- 📖 查看文档: [docs/](docs/)
- 🐛 报告问题: [GitHub Issues](https://github.com/zhaoyuong/openclaw-python/issues)
- 💬 加入讨论: [GitHub Discussions](https://github.com/zhaoyuong/openclaw-python/discussions)
