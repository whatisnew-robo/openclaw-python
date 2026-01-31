# 👋 从这里开始 - OpenClaw Python

**5 分钟快速上手指南**

---

## 🎯 你想做什么？

### 1️⃣ 只想快速试用对话功能

```bash
# 安装
git clone https://github.com/zhaoyuong/openclaw-python.git
cd openclaw-python
uv sync

# 配置（选择一个）
cp .env.example .env
# 在 .env 中添加：
# ANTHROPIC_API_KEY=your-key  (或)
# OPENAI_API_KEY=your-key     (或)
# GOOGLE_API_KEY=your-key

# 开始聊天
uv run openclaw agent chat "你好"
```

✅ **完成！** 就这么简单。

---

### 2️⃣ 想要交互式对话（推荐）

```bash
# 启动交互模式
uv run openclaw agent interactive

# 输入消息，按回车发送
# 输入 /exit 退出
```

**交互命令**:
- `/help` - 帮助
- `/status` - 状态
- `/reset` - 重置
- `/exit` - 退出

---

### 3️⃣ 想要运行 API 服务器

```bash
# 启动服务器
uv run openclaw api start

# 访问 API 文档
# http://localhost:18789/docs
```

---

### 4️⃣ 想用 Python 代码

```python
# my_chat.py
import asyncio
from openclaw.agents import AgentRuntime, Session
from pathlib import Path

async def main():
    runtime = AgentRuntime(
        model="anthropic/claude-opus-4-5"  # 或其他模型
    )
    
    session = Session(
        session_id="test",
        workspace_dir=Path.cwd()
    )
    
    response = await runtime.run_turn(
        session=session,
        user_message="Hello!"
    )
    
    async for event in response:
        if event["type"] == "text":
            print(event["text"], end="")

asyncio.run(main())
```

运行:
```bash
uv run python my_chat.py
```

---

## 🤖 选择 LLM Provider

**不一定要用 Gemini！** 选择任何一个：

| Provider | 配置 | 推荐度 |
|----------|------|--------|
| **Claude** | `ANTHROPIC_API_KEY` | ⭐⭐⭐⭐⭐ 最强 |
| **GPT** | `OPENAI_API_KEY` | ⭐⭐⭐⭐ 稳定 |
| **Gemini** | `GOOGLE_API_KEY` | ⭐⭐⭐ 免费额度大 |
| **Ollama** | 本地运行 | ⭐⭐⭐⭐⭐ 免费 |

### 使用 Ollama（本地，完全免费）

```bash
# 安装 Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 启动服务
ollama serve

# 拉取模型
ollama pull llama3.2

# 使用
uv run openclaw agent chat "Hello" --model ollama/llama3.2
```

**无需 API key，完全免费！**

---

## 📚 下一步

- 📖 **详细指南**: [QUICK_START.md](QUICK_START.md)
- 🔧 **高级功能**: [docs/guides/ADVANCED_FEATURES.md](docs/guides/ADVANCED_FEATURES.md)
- 💬 **示例代码**: `examples/` 目录

---

## ❓ 遇到问题？

**找不到 API key？**
```bash
# 检查 .env 文件
cat .env

# 确保格式正确
ANTHROPIC_API_KEY=sk-ant-...
```

**想切换模型？**
```bash
# 使用 --model 参数
uv run openclaw agent chat "Hello" --model openai/gpt-4
```

**不想配置 API key？**
```bash
# 使用 Ollama（本地，免费）
ollama serve
uv run openclaw agent chat "Hello" --model ollama/llama3.2
```

---

## 🎉 就是这么简单！

OpenClaw 支持多种 LLM，选择最适合你的即可。

**🦞 开始使用 OpenClaw Python！**
