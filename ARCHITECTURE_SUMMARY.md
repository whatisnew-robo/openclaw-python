# OpenClaw Python 架构总结

> 完整理解 Telegram Bot、Gateway 和 Agent 的真实关系

---

## 核心理解 - 一句话总结

**Telegram Bot 通过 HTTP Long Polling 连接 Telegram API，通过 Python 函数调用（同一进程内）直接访问 Agent Runtime，Gateway 负责管理 Bot 的生命周期并通过 WebSocket 为外部客户端（UI/CLI/Mobile）提供服务。**

---

## 完整消息流程（用户视角）

### 用户在 Telegram 发送 "Hello" 的完整过程

```
第1步：用户操作
  用户在 Telegram 客户端输入 "Hello" 并发送

第2步：Telegram 网络传输
  Telegram 客户端 ─HTTPS─→ Telegram API 服务器
  (Telegram 公司的服务器，与 OpenClaw 无关)

第3步：OpenClaw Server 收到消息
  Telegram Bot 轮询获取更新
  └─→ HTTP GET https://api.telegram.org/bot{token}/getUpdates
  └─→ 收到新消息通知

第4步：Bot 处理消息（进程内操作）
  Bot 解析消息
  └─→ 创建 InboundMessage(text="Hello", ...)
  └─→ 调用 handle_telegram_message(message)  [函数调用]
      └─→ session_manager.get_session(...)    [函数调用]
      └─→ agent_runtime.run_turn(session, "Hello")  [函数调用]

第5步：Agent 调用 LLM
  Agent Runtime 发送到 LLM API
  └─→ HTTPS POST https://api.anthropic.com/v1/messages
  └─→ 请求体: {"model": "claude-opus-4", "messages": [...]}
  └─→ 等待响应（流式或完整）

第6步：LLM 返回响应
  LLM API 返回: "Hello! How can I help you?"
  └─→ Agent Runtime 收到响应  [函数返回]
  └─→ handle_telegram_message 收到响应  [函数返回]

第7步：Bot 发送回复
  telegram_channel.send_text(chat_id, "Hello! How can I help?")
  └─→ HTTP POST https://api.telegram.org/bot{token}/sendMessage

第8步：Telegram 推送
  Telegram API ─推送─→ Telegram 客户端
  └─→ 用户看到回复

【并行流程】第9步：Gateway 广播（可选）
  Agent 在处理过程中发送事件
  └─→ emit("agent.start")  ─→  Gateway 收到
  └─→ emit("agent.text")   ─→  Gateway 收到
  └─→ emit("agent.done")   ─→  Gateway 收到
  
  Gateway 广播给所有 WebSocket 客户端
  └─→ Control UI 实时看到对话
  └─→ CLI 工具收到事件通知
  └─→ Mobile App 同步更新
```

---

## Gateway 的三个职责详解

### 职责 1：Channel 生命周期管理

**作用**：启动、停止、监控 channel 插件

**实现**：

```python
class IntegratedOpenClawServer:
    async def setup_telegram(self, bot_token):
        """Gateway 启动 Telegram channel"""
        
        # 1. 创建 channel 实例
        telegram = EnhancedTelegramChannel()
        
        # 2. 配置消息处理器
        telegram.set_message_handler(self.handle_message)
        
        # 3. 启动 channel
        await telegram.start({"bot_token": bot_token})
        
        # 4. 注册到 registry
        self.channels["telegram"] = telegram
        
    async def stop_telegram(self):
        """Gateway 停止 Telegram channel"""
        if "telegram" in self.channels:
            await self.channels["telegram"].stop()
            del self.channels["telegram"]
```

**对比 TypeScript**：

```typescript
// src/gateway/server-channels.ts
gateway.startChannel("telegram", accountId)
  ↓
plugin.gateway.startAccount(ctx)
  ↓
monitorTelegramProvider({ token, config, runtime })
  ↓
Telegram Bot 开始运行
```

### 职责 2：WebSocket API 服务

**作用**：为外部客户端（Control UI、CLI、Mobile）提供 WebSocket 接口

**支持的方法**：

```python
# openclaw/gateway/handlers.py

# 方法1: agent - 发送消息给 Agent
@register_handler("agent")
async def handle_agent(connection, params):
    message = params["message"]
    session_id = params.get("sessionId", "main")
    
    session = session_manager.get_session(session_id)
    
    # 流式返回
    async for event in agent_runtime.run_turn(session, message):
        await connection.send_event("agent", event)

# 方法2: send - 通过 channel 发送消息
@register_handler("send")
async def handle_send(connection, params):
    channel_id = params["channel"]
    to = params["to"]
    message = params["message"]
    
    channel = channels[channel_id]
    await channel.send_text(to, message)

# 方法3: channels.list - 列出所有 channels
@register_handler("channels.list")
async def handle_channels_list(connection, params):
    return [
        {
            "id": ch_id,
            "running": ch.is_running(),
            "healthy": ch.is_healthy()
        }
        for ch_id, ch in channels.items()
    ]

# 方法4: sessions.list - 列出活跃会话
@register_handler("sessions.list")
async def handle_sessions_list(connection, params):
    return [
        {
            "sessionId": sid,
            "messageCount": len(session.messages)
        }
        for sid, session in session_manager.list_sessions()
    ]
```

**使用示例**：

```javascript
// Web UI 连接到 Gateway
const ws = new WebSocket('ws://localhost:8765');

ws.onopen = () => {
  // 连接握手
  ws.send(JSON.stringify({
    type: 'req',
    id: '1',
    method: 'connect',
    params: {
      maxProtocol: 1,
      client: {name: 'web-ui', version: '1.0', platform: 'web'}
    }
  }));
};

ws.onmessage = (event) => {
  const frame = JSON.parse(event.data);
  
  if (frame.type === 'res' && frame.ok) {
    console.log('Method response:', frame.payload);
  }
  
  if (frame.type === 'event') {
    console.log('Event:', frame.event, frame.payload);
  }
};

// 发送消息
ws.send(JSON.stringify({
  type: 'req',
  id: '2',
  method: 'agent',
  params: {message: 'Hello from Web!', sessionId: 'web-1'}
}));

// 查询 channels 状态
ws.send(JSON.stringify({
  type: 'req',
  id: '3',
  method: 'channels.list'
}));
```

### 职责 3：事件广播

**作用**：将 Agent 事件实时广播给所有 WebSocket 客户端

**事件类型**：

```python
# Agent 事件
"agent.start"      # Agent 开始处理
"agent.text"       # Agent 生成文本
"agent.tool_use"   # Agent 调用工具
"agent.done"       # Agent 完成
"agent.error"      # Agent 错误

# Channel 事件
"channel.message"  # Channel 收到消息
"channel.started"  # Channel 启动
"channel.stopped"  # Channel 停止

# System 事件
"system.startup"   # 系统启动
"system.shutdown"  # 系统关闭
```

**实现**：

```python
class GatewayServer:
    def __init__(self):
        self.connections = set()
        
        # 订阅 Agent 事件
        agent_event_bus.subscribe(self.on_agent_event)
    
    async def on_agent_event(self, event):
        """收到 Agent 事件，广播给所有客户端"""
        await self.broadcast_event(event["type"], event["data"])
    
    async def broadcast_event(self, event_type, payload):
        """广播给所有 WebSocket 连接"""
        disconnected = set()
        
        for connection in self.connections:
            try:
                await connection.send_event(event_type, payload)
            except Exception:
                disconnected.add(connection)
        
        # 清理断开的连接
        self.connections -= disconnected
```

---

## 四种通信方式总结

### 1. Bot ↔ Telegram API

```
协议：HTTP Long Polling + POST
目的：接收和发送用户消息
延迟：50-200ms
实现：python-telegram-bot 库

代码：
  # 接收
  updates = await telegram_api.get_updates()
  
  # 发送
  await telegram_api.send_message(chat_id, text)
```

### 2. Bot ↔ Agent

```
协议：Python 函数调用
目的：处理消息，生成回复
延迟：<1μs (微秒)
实现：直接方法调用

代码：
  # 调用 Agent
  async for event in agent_runtime.run_turn(session, message):
      response += event.data["text"]
  
  # 返回值
  return response
```

### 3. Gateway ↔ 外部客户端

```
协议：WebSocket
目的：为 UI/CLI 提供 API
延迟：10-50ms
实现：websockets 库

代码：
  # 客户端连接
  ws = new WebSocket('ws://localhost:8765')
  
  # 发送请求
  ws.send(JSON.stringify({
    type: 'req',
    method: 'agent',
    params: {message: 'Hello'}
  }))
  
  # 接收响应和事件
  ws.onmessage = (event) => { ... }
```

### 4. Agent ↔ LLM API

```
协议：HTTPS POST/Stream
目的：生成 AI 回复
延迟：500-3000ms
实现：anthropic/openai/google SDK

代码：
  # 调用 Claude
  response = await anthropic.messages.create(
    model="claude-opus-4",
    messages=[{"role": "user", "content": message}]
  )
```

---

## 配对机制说明

### 什么是 Pairing？

**不是设备配对！是用户授权机制！**

### 用途

控制哪些用户可以通过私聊（DM）使用 Bot。

### 场景

1. **Public Bot**（dmPolicy: "open"）
   - 任何人都可以私聊
   - 适合公开服务

2. **Private Bot**（dmPolicy: "pairing"）
   - 需要管理员批准
   - 更安全，防垃圾消息

### 实现流程

```python
class PairingManager:
    def __init__(self):
        self.pending = {}  # code -> user_info
        self.allowlist = set()  # approved user_ids
    
    def request_pairing(self, user_id: str) -> str:
        """用户请求配对"""
        code = generate_random_code()  # "ABC123"
        self.pending[code] = {
            "user_id": user_id,
            "created_at": datetime.now()
        }
        return code
    
    def approve_pairing(self, code: str) -> bool:
        """管理员批准配对"""
        if code in self.pending:
            user_id = self.pending[code]["user_id"]
            self.allowlist.add(user_id)
            del self.pending[code]
            return True
        return False
    
    def is_authorized(self, user_id: str) -> bool:
        """检查用户是否已授权"""
        return user_id in self.allowlist

# 使用
async def handle_message(message):
    if message.chat_type == "direct":
        if not pairing_manager.is_authorized(message.sender_id):
            # 生成配对码
            code = pairing_manager.request_pairing(message.sender_id)
            
            # 发送给用户
            await bot.send_text(
                message.chat_id,
                f"需要授权才能使用。\n"
                f"配对码：{code}\n"
                f"请将配对码发送给管理员。"
            )
            return
    
    # 已授权，正常处理
    await process_with_agent(message)
```

---

## 文档索引

### 核心文档

1. **[README.md](README.md)**
   - 项目概述
   - 三种连接方法
   - 架构图

2. **[TELEGRAM_CONNECTION_EXPLAINED.md](TELEGRAM_CONNECTION_EXPLAINED.md)**
   - Telegram Bot 连接原理
   - 详细的代码说明
   - 常见误解澄清

3. **[GATEWAY_ARCHITECTURE.md](GATEWAY_ARCHITECTURE.md)**
   - Gateway 的三个职责
   - 生命周期管理
   - WebSocket API
   - 事件广播

4. **[ARCHITECTURE_DIAGRAMS.md](ARCHITECTURE_DIAGRAMS.md)** ⭐ NEW
   - 错误理解 vs 正确理解
   - 完整消息流程图
   - 通信方式对比
   - 配对机制说明

### 代码示例

5. **[examples/05_telegram_bot.py](examples/05_telegram_bot.py)**
   - 直接 Telegram Bot（最简单）

6. **[examples/10_gateway_telegram_bridge.py](examples/10_gateway_telegram_bridge.py)** ⭐
   - 集成服务器（生产推荐）
   - Gateway + Telegram 完整实现

### Git 配置

7. **[.cursor/GIT_COMMIT_GUIDELINES.md](.cursor/GIT_COMMIT_GUIDELINES.md)** ⭐ NEW
   - 防止 Co-authored-by 的配置
   - Git 提交最佳实践

---

## 关键代码位置

### Python 项目

| 功能 | 文件 | 关键行数 |
|------|------|----------|
| 集成服务器 | `examples/10_gateway_telegram_bridge.py` | 47-186 |
| Telegram 设置 | `examples/10_gateway_telegram_bridge.py` | 83-143 |
| 消息处理 | `examples/10_gateway_telegram_bridge.py` | 90-134 |
| Telegram Channel | `openclaw/channels/enhanced_telegram.py` | 19-287 |
| Gateway Server | `openclaw/gateway/server.py` | 1-201 |
| Gateway Handlers | `openclaw/gateway/handlers.py` | 1-205 |

### TypeScript 参考（官方实现）

| 功能 | 文件 | 说明 |
|------|------|------|
| Gateway 管理 | `src/gateway/server-channels.ts` | ChannelManager |
| Telegram 插件 | `extensions/telegram/src/channel.ts:390` | gateway.startAccount |
| Agent 方法 | `src/gateway/server-methods/agent.ts` | agent handler |
| 事件广播 | `src/gateway/server-broadcast.ts` | broadcast |
| Pairing 存储 | `src/telegram/pairing-store.ts` | 配对管理 |

---

## 常见问题 FAQ

### Q1: Telegram Bot 需要连接到 Gateway 吗？

**A**: 不需要！Bot 是服务器端插件，在同一进程内运行。Gateway 只是管理它的生命周期。

### Q2: 为什么需要 Gateway？

**A**: Gateway 提供三个功能：
1. 统一管理多个 channels（启动/停止）
2. 为外部应用提供 WebSocket API
3. 广播 Agent 事件给所有客户端

### Q3: 可以只运行 Telegram Bot 不运行 Gateway 吗？

**A**: 可以！使用 `examples/05_telegram_bot.py` 就是纯 Bot 模式，不需要 Gateway。

### Q4: Gateway 和 Telegram Bot 哪个先启动？

**A**: 都可以。它们并行运行，互不依赖。通常：
- 先启动 Gateway
- Gateway 启动 Telegram Bot
- 但技术上可以独立启动

### Q5: 配对（Pairing）是做什么的？

**A**: 用户授权机制。控制哪些 Telegram 用户可以私聊 Bot。不是设备配对！

### Q6: 消息延迟主要在哪里？

**A**: 主要瓶颈：
1. Telegram API 轮询：50-200ms
2. LLM API 调用：500-3000ms

Bot→Agent 的函数调用几乎零延迟（<1μs）。

---

## 快速开始

### 方式 1：只用 Telegram Bot

```bash
export TELEGRAM_BOT_TOKEN=your-token
export ANTHROPIC_API_KEY=sk-ant-...

uv run python examples/05_telegram_bot.py
```

### 方式 2：集成服务器（推荐）

```bash
export TELEGRAM_BOT_TOKEN=your-token
export ANTHROPIC_API_KEY=sk-ant-...

uv run python examples/10_gateway_telegram_bridge.py
```

然后可以：
- 通过 Telegram 与 Bot 对话
- 通过 WebSocket 连接 Gateway（`ws://localhost:8765`）
- Control UI 实时监控对话

---

## 架构对比

### 简单模式（Example 05）

```
Telegram User → Telegram API → Bot → Agent → LLM
                                ↑______________|
                                  函数调用
```

### 集成模式（Example 10）

```
Telegram User → Telegram API → Bot ─函数调用→ Agent → LLM
                                       ↓ 发送事件
WebSocket 客户端 ← Gateway ←───────────┘
(UI/CLI/Mobile)      ↑
                     │ WebSocket API
                外部应用连接
```

---

## 总结

### 核心要点

1. **Telegram Bot 是插件**，不是客户端
2. **Bot 通过函数调用**访问 Agent（同一进程）
3. **Gateway 管理生命周期** + **服务 WebSocket 客户端** + **广播事件**
4. **配对是用户授权**，不是设备连接

### 架构优势

- ✅ **零延迟**：Bot→Agent 是函数调用
- ✅ **统一管理**：Gateway 控制所有 channels
- ✅ **实时监控**：WebSocket 实时事件
- ✅ **灵活扩展**：可添加更多 channels

---

**查看在线文档**：https://github.com/zhaoyuong/openclaw-python

**现在你完全理解 OpenClaw 架构了！** 🎉
