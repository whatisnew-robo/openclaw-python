# OpenClaw Python - 快速启动指南

**版本**: 0.6.0  
**更新时间**: 2026-02-11

---

## 🚀 快速启动

### 1️⃣ 环境准备

```bash
# 进入项目目录
cd /Users/openjavis/Desktop/xopen/openclaw-python

# 同步依赖（使用uv）
uv sync

# 或安装依赖（如果使用pip）
pip install -e .
```

---

### 2️⃣ 配置检查

检查您的配置文件是否存在：

```bash
# 查看配置文件
cat ~/.openclaw/openclaw.json

# 查看环境变量
cat .env
```

**必需的配置**:
- ✅ `~/.openclaw/openclaw.json` - 主配置文件
- ✅ `.env` - 环境变量（包含API密钥）

**必需的环境变量** (`.env`):
```bash
# Google/Gemini API
GOOGLE_API_KEY=your_google_api_key_here

# Telegram Bot (如果使用)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# 其他可选配置...
```

---

### 3️⃣ 启动方式

#### 方式A: 启动Gateway服务器（推荐）

```bash
# 使用uv启动Gateway
uv run openclaw gateway start

# 或使用Python直接启动
python -m openclaw.cli.main gateway start

# 指定端口
uv run openclaw gateway start --port 8080

# 查看帮助
uv run openclaw gateway --help
```

**Gateway会自动**:
- ✅ 加载配置
- ✅ 初始化Agent Runtime
- ✅ 启动WebSocket服务器
- ✅ 启动HTTP管理接口
- ✅ 启动Cron调度服务

---

#### 方式B: 直接使用Agent Runtime

如果只需要Agent对话功能（不需要Gateway）：

```python
# 创建文件: test_agent.py
import asyncio
from pathlib import Path
from openclaw.agents.runtime import MultiProviderRuntime
from openclaw.agents.session import Session

async def main():
    # 创建Agent Runtime
    runtime = MultiProviderRuntime(
        model="google/gemini-2.5-flash",
        api_key="your_google_api_key"  # 或从环境变量读取
    )
    
    # 创建Session
    workspace = Path.home() / ".openclaw" / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    
    session = Session(
        session_id="my-session",
        workspace_dir=workspace
    )
    
    # 对话
    print("发送消息到Agent...")
    async for event in runtime.run_turn(
        session=session,
        message="你好！请介绍一下自己。",
        max_tokens=500
    ):
        if "text" in str(event.type).lower():
            delta = event.data.get("delta", {})
            if isinstance(delta, dict):
                text = delta.get("text", "")
                if text:
                    print(text, end="", flush=True)
    
    print("\n完成!")

if __name__ == "__main__":
    asyncio.run(main())
```

运行：
```bash
uv run python test_agent.py
```

---

#### 方式C: 使用CLI命令

```bash
# 运行onboarding向导
uv run openclaw onboard

# 查看配置
uv run openclaw config show

# 测试连接
uv run openclaw test connection

# 查看所有命令
uv run openclaw --help
```

---

### 4️⃣ 验证运行

#### 检查Gateway是否运行

```bash
# 检查WebSocket端口
curl http://localhost:3001/health

# 或使用netstat
netstat -an | grep 3001
```

#### 测试Agent对话

```bash
# 运行真实API测试
uv run python test_real_api.py
```

#### 查看日志

```bash
# Gateway会输出日志到终端
# 查看特定日志
tail -f ~/.openclaw/logs/gateway.log  # 如果配置了日志文件
```

---

## 🔧 常见启动问题

### 问题1: 找不到模块

```bash
# 解决方法：安装项目
uv pip install -e .
# 或
pip install -e .
```

### 问题2: API密钥错误

```bash
# 检查.env文件
cat .env | grep API_KEY

# 确保格式正确
GOOGLE_API_KEY=AIza...  # 不要有引号
```

### 问题3: 端口已被占用

```bash
# 查找占用端口的进程
lsof -i :3001

# 杀死进程
kill -9 <PID>

# 或使用其他端口
uv run openclaw gateway start --port 8080
```

### 问题4: 配置文件不存在

```bash
# 运行onboarding创建配置
uv run openclaw onboard

# 或手动创建
mkdir -p ~/.openclaw
cp openclaw.example.json ~/.openclaw/openclaw.json
```

---

## 📊 启动后的操作

### 1. 连接到Gateway（使用WebSocket客户端）

```javascript
// JavaScript示例
const ws = new WebSocket('ws://localhost:3001');

ws.on('open', () => {
  // 发送消息
  ws.send(JSON.stringify({
    method: 'chat.send',
    params: {
      message: 'Hello!',
      sessionId: 'my-session'
    }
  }));
});

ws.on('message', (data) => {
  console.log('收到:', data);
});
```

### 2. 使用HTTP API

```bash
# 查询会话列表
curl http://localhost:3001/api/sessions

# 查询Cron任务
curl http://localhost:3001/api/cron/jobs

# 健康检查
curl http://localhost:3001/health
```

### 3. 使用Python客户端

```python
import asyncio
import websockets
import json

async def connect_gateway():
    uri = "ws://localhost:3001"
    async with websockets.connect(uri) as websocket:
        # 发送消息
        await websocket.send(json.dumps({
            "method": "chat.send",
            "params": {
                "message": "Hello from Python!",
                "sessionId": "test-session"
            }
        }))
        
        # 接收响应
        response = await websocket.recv()
        print(f"收到: {response}")

asyncio.run(connect_gateway())
```

---

## 🎯 推荐的启动流程

### 首次启动

```bash
# 1. 同步依赖
uv sync

# 2. 运行测试确保一切正常
uv run python run_new_tests.py
uv run python test_real_api.py

# 3. 检查配置
cat ~/.openclaw/openclaw.json
cat .env

# 4. 启动Gateway
uv run openclaw gateway start

# 5. 在另一个终端测试连接
uv run python test_agent.py
```

### 日常启动

```bash
# 直接启动Gateway
cd /Users/openjavis/Desktop/xopen/openclaw-python
uv run openclaw gateway start
```

---

## 🔄 开发模式

如果您正在开发，可以使用以下方式：

```bash
# 监控模式（需要watchdog）
uv pip install watchdog
watchmedo auto-restart --patterns="*.py" --recursive -- uv run openclaw gateway start

# 调试模式
OPENCLAW_DEBUG=true uv run openclaw gateway start

# 指定日志级别
OPENCLAW_LOG_LEVEL=DEBUG uv run openclaw gateway start
```

---

## 📝 下一步

启动成功后，您可以：

1. **配置Channels**
   - 连接Telegram Bot
   - 配置Discord
   - 配置Slack

2. **设置Cron任务**
   - 定时任务
   - 提醒功能

3. **自定义工具**
   - 添加自定义工具
   - 集成外部API

4. **监控和管理**
   - 查看会话历史
   - 管理Agent行为

---

## 🆘 获取帮助

```bash
# 查看命令帮助
uv run openclaw --help
uv run openclaw gateway --help

# 查看文档
cat README.md
cat TESTING_SUMMARY.md

# 运行测试
uv run pytest tests/ -v
```

---

## ✅ 启动检查清单

在启动前确保：

- [ ] Python 3.11+ 已安装
- [ ] uv 已安装
- [ ] 依赖已同步 (`uv sync`)
- [ ] 配置文件存在 (`~/.openclaw/openclaw.json`)
- [ ] 环境变量已设置 (`.env`)
- [ ] API密钥有效
- [ ] 端口未被占用 (默认3001)
- [ ] 测试通过 (`uv run python test_real_api.py`)

---

**祝您使用愉快！** 🎉

有问题可以查看日志或运行测试进行诊断。
