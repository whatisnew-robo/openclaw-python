# Real Integration Testing Guide

## Overview

Test the complete openclaw-python system with real Telegram bot and Gemini API to verify alignment with the TypeScript implementation.

## Prerequisites

✓ uv environment installed  
✓ `.env` file with credentials:
  - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
  - `GOOGLE_API_KEY`: Your Gemini API key

## Quick Test (Automated)

Run the integration test script:

```bash
cd openclaw-python
uv run python test_real_integration.py
```

This will:
1. Load environment variables from `.env`
2. Initialize all OpenClaw components
3. Start the Telegram bot
4. Wait for messages

Then send a message to your Telegram bot to test the complete flow.

## Verify Alignment

The test verifies these critical components:

### 1. Message Flow (Telegram → Agent → Gemini → Telegram)
```
Telegram Message
  ↓
TelegramChannel.handle_message()
  ↓
InboundMessage created
  ↓
ChannelManager builds MsgContext
  ↓
finalize_inbound_context(ctx)
  ↓
runtime.run_turn(ctx.BodyForAgent, images=ctx.MediaUrls)
  ↓
Agent processes with full context
  ↓
Gemini API call
  ↓
Response sent back to Telegram
```

### 2. Context Verification

Check that MsgContext includes:
- ✓ `Body`: Original message text
- ✓ `BodyForAgent`: Processed text for agent
- ✓ `From`: Sender info (id, username, first_name)
- ✓ `To`: Bot info
- ✓ `ChatType`: "dm" or "group"
- ✓ `SenderName`: Display name
- ✓ `SenderId`: Unique sender ID
- ✓ `SessionKey`: Session identifier
- ✓ `ConversationLabel`: Human-readable label
- ✓ `OriginatingChannel`: "telegram"

### 3. Session Persistence

Check session files created:
```bash
~/.openclaw/agents/main/sessions/
├── sessions.json          # Session metadata
└── {session-id}.jsonl     # Message transcript
```

### 4. Expected Behavior

When you send "Hello bot!" to your Telegram bot:

1. **Bot receives message** (console shows log)
2. **Context is built** with all fields
3. **Session is loaded/created** in sessions.json
4. **Message added to transcript** in .jsonl file
5. **Gemini API called** with full context
6. **Response sent** back to Telegram
7. **Response logged** to transcript

## Manual Testing Steps

### Step 1: Start the bot
```bash
uv run python test_real_integration.py
```

### Step 2: Send test messages

**Test 1: Simple greeting**
- Send: "Hello!"
- Expected: Bot responds with a greeting
- Verify: Session created in `~/.openclaw/agents/main/sessions/`

**Test 2: Multi-turn conversation**
- Send: "What is Python?"
- Expected: Bot explains Python
- Send: "Give me an example"
- Expected: Bot provides an example with context from previous message
- Verify: Transcript shows both turns in .jsonl file

**Test 3: Group chat (if applicable)**
- Add bot to a group
- Send: "Hello bot!"
- Expected: Bot responds
- Verify: `ChatType` is "group" and `SenderName` includes sender's name

**Test 4: Media messages (if supported)**
- Send an image with caption
- Expected: Bot receives image URL in `MediaUrls`
- Verify: Gemini processes the image

### Step 3: Verify session files

```bash
# Check session store
cat ~/.openclaw/agents/main/sessions/sessions.json

# Check transcript
cat ~/.openclaw/agents/main/sessions/{session-id}.jsonl
```

## Troubleshooting

### Issue: Bot doesn't respond

**Check**:
1. Console for errors
2. .env file has correct tokens
3. Telegram bot is not blocked
4. Internet connection is working

**Debug**:
```bash
# Enable debug logging
export CLAWDBOT_LOG_LEVEL=DEBUG
uv run python test_real_integration.py
```

### Issue: Import errors

**Fix**:
```bash
# Reinstall dependencies
cd openclaw-python
uv pip install -e .
```

### Issue: Session not persisting

**Check**:
1. `~/.openclaw/agents/main/sessions/` directory exists
2. Write permissions on the directory
3. No disk space issues

**Debug**:
```python
# Check session manager
from openclaw.agents.session_manager import SessionManager
sm = SessionManager(agent_id="main")
print(sm.sessions_dir)
```

## Comparison with TypeScript

To verify perfect alignment, compare:

### 1. Session Store Format
```bash
# Python
cat ~/.openclaw/agents/main/sessions/sessions.json

# TypeScript
cat ~/.openclaw/agents/main/sessions/sessions.json
```

Should be identical JSON structure.

### 2. Transcript Format
```bash
# Python
head -n 5 ~/.openclaw/agents/main/sessions/{session-id}.jsonl

# TypeScript
head -n 5 ~/.openclaw/agents/main/sessions/{session-id}.jsonl
```

Should have identical JSONL format with same fields.

### 3. Message Context
Enable debug logging in both versions and compare the `MsgContext` objects logged when a message is received. All fields should match.

## Success Criteria

✓ Bot responds to messages  
✓ Session files created correctly  
✓ Transcripts in JSONL format  
✓ Multi-turn conversations maintain context  
✓ Session metadata matches TypeScript format  
✓ Gateway events properly broadcast  
✓ No errors in console  

## Performance Notes

- First message may be slower (cold start)
- Subsequent messages should be fast (~1-3s response time)
- Session loading should be instant for existing sessions
- Memory usage should be stable over time

## Next Steps

After verifying real integration:

1. **Load Testing**: Test with multiple concurrent users
2. **Long Conversations**: Test context window management
3. **Error Recovery**: Test bot behavior on API errors
4. **Gateway Testing**: Test WebSocket gateway connections
5. **Format Comparison**: Run side-by-side with TypeScript version

## Support

If you encounter issues:

1. Check console logs for errors
2. Verify `.env` file contents
3. Check `~/.openclaw/agents/main/sessions/` for session files
4. Enable DEBUG logging for detailed output
5. Compare with TypeScript implementation behavior

---

**Ready to test?** Run `uv run python test_real_integration.py` and send a message to your Telegram bot!
