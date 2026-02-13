# Telegram 消息格式完整指南

参考: https://core.telegram.org/bots/api

## 📝 支持的消息类型

你的 Telegram Bot 现在支持发送各种格式的消息给用户！

---

## 1. 文本消息 (Text Messages)

### 基础文本

```python
await channel.send_text(
    target=chat_id,
    text="你好！这是一条普通消息。"
)
```

### Markdown 格式

```python
await channel.send_text(
    target=chat_id,
    text=(
        "*粗体文本* 和 _斜体文本_\n\n"
        "`行内代码` 和 ```\n代码块\n```\n\n"
        "[链接文本](https://example.com)"
    )
)
```

**支持的格式**:
- `*粗体*` - 粗体文本
- `_斜体_` - 斜体文本
- `` `代码` `` - 行内代码
- ```` ```代码块``` ```` - 代码块
- `[文本](URL)` - 超链接

---

## 2. 图片 (Photos)

```python
await channel.send_photo(
    target=chat_id,
    photo=open("image.jpg", "rb"),  # 或 URL
    caption="📸 图片说明（支持 *Markdown*）",
    reply_to=message_id,
    keyboard=inline_keyboard  # 可选
)
```

**特性**:
- 支持本地文件或 URL
- 可添加说明文字（caption）
- 支持 Markdown 格式
- 可添加回复和键盘

---

## 3. 视频 (Videos)

```python
await channel.send_video(
    target=chat_id,
    video=open("video.mp4", "rb"),
    caption="🎬 视频说明",
    reply_to=message_id
)
```

---

## 4. 文档/文件 (Documents)

```python
await channel.send_document(
    target=chat_id,
    document=open("file.pdf", "rb"),
    caption="📄 文件说明",
    keyboard=inline_keyboard
)
```

**支持的文件类型**:
- PDF 文档
- Word 文档
- Excel 表格
- 压缩文件 (ZIP, RAR)
- 任何其他文件类型

---

## 5. 音频 (Audio)

```python
await channel.send_audio(
    target=chat_id,
    audio=open("music.mp3", "rb"),
    caption="🎵 音频说明"
)
```

---

## 6. 位置 (Location)

```python
await channel.send_location(
    target=chat_id,
    latitude=37.7749,   # 纬度
    longitude=-122.4194  # 经度
)
```

**用途**:
- 分享地理位置
- 显示地图标记
- 导航和路线

---

## 7. 投票 (Polls)

```python
await channel.send_poll(
    target=chat_id,
    question="你最喜欢的 AI 模型？",
    options=["Gemini", "Claude", "GPT-4", "其他"],
    is_anonymous=True
)
```

**特性**:
- 最多 10 个选项
- 匿名或公开投票
- 单选或多选
- 测验模式（有正确答案）

---

## 8. 骰子/动画 (Dice & Animations)

```python
# 发送骰子
await channel.send_dice(
    target=chat_id,
    emoji="🎲"  # 可选: 🎲🎯🏀⚽🎳🎰
)
```

**支持的表情**:
- 🎲 骰子 (1-6)
- 🎯 飞镖 (1-6)
- 🏀 篮球 (1-5)
- ⚽ 足球 (1-5)
- 🎳 保龄球 (1-6)
- 🎰 老虎机 (1-64)

---

## 9. 内联键盘 (Inline Keyboards)

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# 创建按钮
keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("选项 1", callback_data="option_1"),
        InlineKeyboardButton("选项 2", callback_data="option_2")
    ],
    [
        InlineKeyboardButton("URL 按钮", url="https://example.com")
    ]
])

# 发送带按钮的消息
await channel.send_text(
    target=chat_id,
    text="请选择一个选项：",
    # 需要扩展 send_text 支持 keyboard 参数
)
```

**按钮类型**:
- `callback_data` - 点击触发回调
- `url` - 打开网址
- `switch_inline_query` - 切换到内联模式
- `login_url` - 登录按钮

---

## 10. 回复键盘 (Reply Keyboards)

```python
from telegram import ReplyKeyboardMarkup, KeyboardButton

keyboard = ReplyKeyboardMarkup([
    [KeyboardButton("💬 新对话"), KeyboardButton("📊 状态")],
    [KeyboardButton("❓ 帮助"), KeyboardButton("🤖 模型")]
], resize_keyboard=True)

# 已在 /start 命令中实现
```

---

## 🎯 实际使用示例

### 示例 1: 发送带图片和按钮的消息

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# 创建按钮
keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("👍 赞", callback_data="like")],
    [InlineKeyboardButton("💬 评论", callback_data="comment")]
])

# 发送图片
await channel.send_photo(
    target=chat_id,
    photo="https://example.com/image.jpg",
    caption="*查看这张图片！*\n\n点击下方按钮互动",
    keyboard=keyboard
)
```

### 示例 2: 发送文件并通知

```python
# 发送文档
msg_id = await channel.send_document(
    target=chat_id,
    document=open("report.pdf", "rb"),
    caption="📄 *月度报告*\n\n报告已生成完成！"
)

# 发送确认消息
await channel.send_text(
    target=chat_id,
    text="✅ 文件发送成功！",
    reply_to=msg_id
)
```

### 示例 3: 交互式投票

```python
# 创建投票
await channel.send_poll(
    target=chat_id,
    question="下次会议时间？",
    options=[
        "周一 10:00",
        "周二 14:00",
        "周三 15:00",
        "其他时间"
    ],
    is_anonymous=False  # 公开投票，可看到谁投票
)
```

---

## 🤖 Agent 结果自动格式化

### 智能格式选择

Agent 可以根据内容类型自动选择最佳格式：

```python
# 文本结果 → 文本消息
if result_type == "text":
    await channel.send_text(target=chat_id, text=result)

# 图片 URL/路径 → 图片消息
elif result_type == "image":
    await channel.send_photo(target=chat_id, photo=result, caption=description)

# 文件路径 → 文档消息
elif result_type == "file":
    await channel.send_document(target=chat_id, document=open(result, "rb"))

# 位置信息 → 地图
elif result_type == "location":
    await channel.send_location(target=chat_id, latitude=lat, longitude=lon)

# 选择题 → 投票
elif result_type == "poll":
    await channel.send_poll(target=chat_id, question=q, options=opts)
```

---

## 📊 消息格式对比

| 格式 | API 方法 | 支持说明 | 支持键盘 | 最佳用途 |
|------|----------|----------|----------|----------|
| 文本 | `send_text` | ✅ | ✅ | 普通回复 |
| 图片 | `send_photo` | ✅ | ✅ | 可视化内容 |
| 视频 | `send_video` | ✅ | ✅ | 视频内容 |
| 文档 | `send_document` | ✅ | ✅ | 文件分享 |
| 音频 | `send_audio` | ✅ | ❌ | 音乐/录音 |
| 位置 | `send_location` | ✅ | ❌ | 地理位置 |
| 投票 | `send_poll` | ✅ | ❌ | 收集意见 |
| 骰子 | `send_dice` | ✅ | ❌ | 游戏/娱乐 |

---

## 🧪 测试所有格式

运行测试脚本：

```bash
# 设置环境变量
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TEST_CHAT_ID="your_user_id"

# 运行测试
uv run python test_telegram_formats.py
```

测试会发送：
1. Markdown 格式文本
2. 投票问题
3. 6 种骰子动画
4. 地理位置
5. 图片（如果有测试图片）
6. 文档文件

---

## 💡 最佳实践

### 1. 选择合适的格式

- **纯文本信息** → `send_text`
- **需要可视化** → `send_photo` / `send_video`
- **文件分享** → `send_document`
- **收集反馈** → `send_poll`
- **位置信息** → `send_location`

### 2. 使用 Markdown 增强可读性

```python
message = (
    "*🎯 任务完成*\n\n"
    "已处理 `123` 条记录\n"
    "• 成功: `120`\n"
    "• 失败: `3`\n\n"
    "_耗时: 5.2 秒_"
)
await channel.send_text(target=chat_id, text=message)
```

### 3. 添加交互按钮

```python
keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("✅ 确认", callback_data="confirm")],
    [InlineKeyboardButton("❌ 取消", callback_data="cancel")]
])
```

### 4. 使用回复功能

```python
# 回复用户的消息
await channel.send_text(
    target=chat_id,
    text="收到你的消息！",
    reply_to=user_message_id
)
```

---

## 📚 参考资源

- **Telegram Bot API**: https://core.telegram.org/bots/api
- **python-telegram-bot 文档**: https://docs.python-telegram-bot.org/
- **Markdown 语法**: https://core.telegram.org/bots/api#markdown-style

---

## ✅ 功能清单

- [x] 文本消息 (Markdown/HTML)
- [x] 图片消息
- [x] 视频消息
- [x] 文档消息
- [x] 音频消息
- [x] 位置消息
- [x] 投票消息
- [x] 骰子动画
- [x] 内联键盘
- [x] 回复键盘
- [x] 回调查询处理
- [x] 引用回复

---

## 🎉 总结

现在你的 Telegram Bot 支持：

✅ **8 种消息格式**
✅ **2 种键盘类型**
✅ **Markdown 格式化**
✅ **交互式按钮**
✅ **引用回复**

Agent 的结果可以用最合适的格式发送给你！

**立即测试**: 重启 Gateway，在 Telegram 中与你的 Bot 对话！

---

*更新时间: 2026-02-12*
