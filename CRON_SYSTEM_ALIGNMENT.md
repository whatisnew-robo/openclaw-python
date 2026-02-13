# OpenClaw Cron 系统对齐文档

## 📋 概述

OpenClaw 的 Cron 系统不是简单的 crontab，而是一个完整的 **定时 LLM 任务调度系统**，核心特点是通过 **Isolated Agent** 执行定时任务，本质上是 **调用 LLM 模型** 的定时服务。

---

## 🏗️ 架构对比

### TypeScript 版本 (src/cron/)

```
cron/
├── service.ts              # CronService 主类
├── types.ts                # 类型定义
├── store.ts                # 持久化存储
├── service/
│   ├── state.ts            # 服务状态
│   ├── ops.ts              # 操作函数 (add/list/remove/run)
│   ├── timer.ts            # 定时器管理
│   ├── store.ts            # Store 操作
│   ├── locked.ts           # 锁机制
│   ├── jobs.ts             # Job 逻辑
│   └── normalize.ts        # 数据标准化
├── isolated-agent/
│   ├── run.ts              # Isolated agent 执行
│   ├── session.ts          # Session 管理
│   ├── delivery-target.ts  # 投递目标解析
│   └── helpers.ts          # 辅助函数
├── schedule.ts             # 调度计算
├── delivery.ts             # 结果投递
├── run-log.ts              # 执行日志
└── parse.ts                # 解析工具
```

### Python 版本 (openclaw/cron/)

```
cron/
├── service.py              # CronService (需完善)
├── types.py                # 类型定义 ✅
├── store.py                # Store + RunLog ✅
├── timer.py                # Timer 管理 ✅
├── schedule.py             # 调度计算 ✅
├── isolated_agent/
│   ├── run.py              # Agent 执行 ✅
│   ├── session.py          # Session 管理 ✅
│   └── delivery.py         # 投递机制 (需完善)
└── __init__.py
```

---

## 🎯 核心概念

### 1. Job 类型

#### sessionTarget

- **main**: 向主 session 发送系统事件
  - 用于简单的提醒、通知
  - 不执行 LLM 调用
  - Payload: `systemEvent`

- **isolated**: 独立 session 执行 Agent 任务
  - **核心功能**：在独立 session 中调用 LLM
  - 每个 job 有自己的 session 和历史
  - Payload: `agentTurn`
  - 支持结果投递 (delivery)

#### Payload 类型

```python
# System Event (main session)
SystemEventPayload(
    kind="systemEvent",
    text="It's 9am - time for daily news summary"
)

# Agent Turn (isolated session) - 核心！
AgentTurnPayload(
    kind="agentTurn",
    prompt="Search for today's top tech news and summarize",
    model="google/gemini-3-pro-preview"  # 可选模型
)
```

#### Schedule 类型

```python
# 一次性 (绝对时间)
AtSchedule(
    type="at",
    timestamp="2026-02-12T15:00:00Z"
)

# 间隔重复
EverySchedule(
    type="every",
    interval_ms=3600000,  # 1 hour
    anchor="2026-02-12T09:00:00Z"  # 起始时间
)

# Cron 表达式
CronSchedule(
    type="cron",
    expression="0 9 * * *",  # 每天 9am
    timezone="UTC"
)
```

#### Delivery 配置

```python
# 投递到 Telegram
CronDelivery(
    channel="telegram",
    target="8366053063",  # User ID
    best_effort=True  # 投递失败不影响任务成功
)
```

---

## 🔄 执行流程

### Isolated Agent 任务流程

```
1. Timer 触发 (timer.py)
   ↓
2. 执行 isolated agent turn (isolated_agent/run.py)
   • 创建或加载 session (session.py)
   • 调用 LLM 模型 (通过 provider)
   • 传递 tools (如果需要)
   • 获取 agent 响应
   ↓
3. 提取结果摘要
   • 从响应中提取 summary (前200字符或第一段)
   ↓
4. 投递结果 (delivery.py)
   • 根据 delivery 配置
   • 发送到指定 channel
   • 格式化消息
   ↓
5. 更新 job 状态
   • 记录执行时间
   • 计算下次执行时间
   • 保存到 store
   ↓
6. 写入 run log (store.py)
   • JSONL 格式记录
   • 包含状态、摘要、耗时
```

---

## 🔧 关键组件实现

### 1. CronService (service.py)

**职责**:
- 管理 jobs 生命周期
- 协调 timer、store、executor
- 提供 API (add/list/remove/run)

**当前状态**: ⚠️  需要完善
- [x] 基础框架
- [ ] Store 集成
- [ ] Timer 集成
- [ ] Executor 回调
- [ ] Event 广播

**需要添加**:
```python
class CronService:
    def __init__(self, deps: CronServiceDeps):
        self.store = CronStore(deps.store_path)
        self.timer = CronTimer(on_timer_callback=self._on_timer)
        self.deps = deps
        self.jobs: list[CronJob] = []
        self.running = False
    
    async def start(self):
        """加载 jobs 并启动 timer"""
        self.jobs = self.store.load()
        self.timer.arm_timer(self.jobs)
    
    async def _on_timer(self, due_jobs: list[CronJob]):
        """Timer 触发时执行 due jobs"""
        for job in due_jobs:
            await self._execute_job(job)
    
    async def _execute_job(self, job: CronJob):
        """执行单个 job"""
        if job.session_target == "main":
            # 发送 system event
            text = job.payload.text
            self.deps.enqueue_system_event(text, agent_id=job.agent_id)
        
        elif job.session_target == "isolated":
            # 执行 isolated agent
            result = await self.deps.run_isolated_agent(job)
            
            # 投递结果
            if job.delivery and result.get("success"):
                await self._deliver_result(job, result)
```

### 2. Delivery 机制 (delivery.py)

**职责**:
- 将 isolated agent 结果发送到指定 channel
- 格式化消息
- 错误处理

**当前状态**: ⚠️  需要完善

**需要实现**:
```python
async def deliver_result(
    job: CronJob,
    result: dict[str, Any],
    channel_registry: dict[str, BaseChannel],
) -> bool:
    """
    投递 cron job 执行结果
    
    Args:
        job: Cron job
        result: 执行结果 (包含 summary)
        channel_registry: Channel 注册表
    
    Returns:
        投递是否成功
    """
    if not job.delivery:
        return False
    
    delivery = job.delivery
    
    # 解析 channel
    channel_id = delivery.channel
    if channel_id == "last":
        # 使用最近使用的 channel
        channel_id = get_last_used_channel()
    
    channel = channel_registry.get(channel_id)
    if not channel:
        raise ValueError(f"Channel not found: {channel_id}")
    
    # 格式化消息
    summary = result.get("summary", "")
    message = f"🤖 Cron: {job.name}\n\n{summary}"
    
    # 发送消息
    try:
        await channel.send_text(
            target=delivery.target,
            text=message
        )
        return True
    except Exception as e:
        if not delivery.best_effort:
            raise
        logger.warning(f"Delivery failed (best effort): {e}")
        return False
```

### 3. Cron Tool (agents/tools/cron.py)

**职责**:
- Agent 可以使用的定时任务工具
- 添加、列表、删除任务

**当前状态**: ❌ 缺失

**需要实现**:
```python
class CronTool(AgentTool):
    """Cron job management tool"""
    
    def __init__(self, cron_service: CronService):
        super().__init__()
        self.name = "cron"
        self.description = """
Manage scheduled tasks and reminders.

ACTIONS:
- add: Create new job
- list: List all jobs
- remove: Delete job
- status: Check job info

EXAMPLES:
"Set daily news reminder at 9am"
"Cancel the morning alarm"
"Show all my scheduled tasks"
"""
        self.cron_service = cron_service
    
    def get_schema(self) -> dict[str, Any]:
        return {
            "name": "cron",
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["add", "list", "remove", "status"],
                        "description": "Action to perform"
                    },
                    "job_id": {
                        "type": "string",
                        "description": "Job ID (for remove/status)"
                    },
                    "job": {
                        "type": "object",
                        "description": "Job configuration (for add)",
                        "properties": {
                            "name": {"type": "string"},
                            "schedule": {"type": "object"},
                            "prompt": {"type": "string"},
                            "delivery": {"type": "object"}
                        }
                    }
                },
                "required": ["action"]
            }
        }
    
    async def execute(self, args: dict[str, Any]) -> ToolResult:
        action = args.get("action")
        
        if action == "add":
            return await self._add_job(args.get("job", {}))
        elif action == "list":
            return await self._list_jobs()
        elif action == "remove":
            return await self._remove_job(args.get("job_id"))
        elif action == "status":
            return await self._get_status(args.get("job_id"))
```

### 4. Gateway Bootstrap 集成

**职责**:
- 在 Gateway 启动时初始化 Cron Service
- 连接所有依赖 (provider, tools, channels)
- 设置回调函数

**当前状态**: ⚠️  需要完善

**需要添加到 `gateway/bootstrap.py`**:
```python
def init_cron_service(state: BootstrapState) -> CronService:
    """Initialize cron service with full dependencies"""
    
    from ..cron import CronService, CronServiceDeps
    from ..cron.store import CronStore
    from pathlib import Path
    
    # Resolve store path
    store_dir = Path.home() / ".openclaw" / "cron"
    store_path = store_dir / "jobs.json"
    
    # Create deps
    deps = CronServiceDeps(
        store_path=store_path,
        cron_enabled=state.config.get("cron", {}).get("enabled", True),
        
        # System event callback
        enqueue_system_event=lambda text, agent_id=None: (
            enqueue_system_event_to_session(text, agent_id, state.session_manager)
        ),
        
        # Isolated agent callback
        run_isolated_agent=lambda job: (
            run_isolated_cron_job(
                job=job,
                provider=state.provider,
                tools=state.tools,
                session_manager=state.session_manager,
                channel_registry=state.channel_registry
            )
        ),
        
        # Heartbeat callbacks
        request_heartbeat_now=lambda: request_heartbeat(state),
        run_heartbeat_once=lambda reason: run_heartbeat_once(state, reason),
        
        # Event callback
        on_event=lambda evt: broadcast_event("cron", evt),
    )
    
    # Create service
    cron_service = CronService(deps)
    
    # Start service
    await cron_service.start()
    
    logger.info(f"Cron service started with {len(cron_service.jobs)} jobs")
    
    return cron_service
```

---

## 📝 配置示例

### openclaw.json

```json
{
  "cron": {
    "enabled": true,
    "store": "~/.openclaw/cron/jobs.json"
  }
}
```

### 添加 Job (通过 Agent)

```
User: "每天早上9点给我发送科技新闻摘要"

Agent uses cron tool:
{
  "action": "add",
  "job": {
    "name": "Daily Tech News",
    "schedule": {
      "type": "cron",
      "expression": "0 9 * * *",
      "timezone": "UTC"
    },
    "session_target": "isolated",
    "payload": {
      "kind": "agentTurn",
      "prompt": "Search for today's top tech news and provide a summary"
    },
    "delivery": {
      "channel": "telegram",
      "target": "8366053063"
    }
  }
}
```

---

## 🔄 对齐状态

### 完成度

| 组件 | TypeScript | Python | 状态 |
|------|------------|--------|------|
| 类型定义 | ✅ | ✅ | 完全对齐 |
| Store | ✅ | ✅ | 完全对齐 |
| Timer | ✅ | ✅ | 完全对齐 |
| Schedule | ✅ | ✅ | 完全对齐 |
| Isolated Agent | ✅ | ✅ | 完全对齐 |
| Service | ✅ | ⚠️ | 需完善 |
| Delivery | ✅ | ⚠️ | 需完善 |
| Cron Tool | ✅ | ❌ | 缺失 |
| Bootstrap | ✅ | ⚠️ | 需完善 |
| Run Logs | ✅ | ✅ | 完全对齐 |

### 下一步实现优先级

1. **高优先级** (核心功能):
   - [ ] 完善 CronService 集成 store + timer
   - [ ] 完善 Delivery 机制
   - [ ] 完善 Bootstrap 集成

2. **中优先级** (Agent 可用):
   - [ ] 实现 Cron Tool
   - [ ] 添加配置加载

3. **低优先级** (增强功能):
   - [ ] 心跳系统集成
   - [ ] Event 广播
   - [ ] Web UI 集成

---

## 💡 核心价值

OpenClaw 的 Cron 系统的核心价值在于：

1. **LLM 驱动**: 不是简单的脚本执行，而是调用 LLM 模型
2. **Isolated Session**: 每个任务有独立的上下文和历史
3. **Tool Access**: Agent 可以使用所有工具 (搜索、文件操作等)
4. **智能投递**: 结果自动发送到指定 channel
5. **Agent 可管理**: 用户通过对话创建/管理定时任务

**示例场景**:
```
用户: "每天早上8点总结昨天的股市动态"

系统:
1. 创建 isolated agent job
2. 每天 8am 触发
3. Agent 搜索昨天股市数据
4. Agent 生成总结
5. 自动发送到用户 Telegram
```

这就是为什么它不是简单的 crontab，而是一个 **AI 定时任务系统**！

---

*更新时间: 2026-02-12*
*版本: 1.0.0*
