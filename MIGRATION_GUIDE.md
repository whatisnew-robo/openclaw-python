# Session Storage Migration Guide

## Overview

This guide explains how to migrate from the old per-session JSON file storage format to the new centralized sessions.json format.

## Why Migrate?

The new storage format provides:

- ✅ **Better Performance** - Single file load vs multiple file reads
- ✅ **File Locking** - Prevents concurrent access issues
- ✅ **Caching** - 45s TTL cache for faster access
- ✅ **Separate Transcripts** - Messages in efficient JSONL format
- ✅ **Full TypeScript Alignment** - Complete feature parity

## Before You Start

### Backup Your Data

**IMPORTANT:** The migration tool automatically creates backups, but we recommend making your own backup first:

```bash
# Backup your entire workspace
cp -r ~/.openclaw ~/.openclaw.backup.$(date +%Y%m%d)
```

### Check Your Current Storage

Look for these files in your workspace:

```
~/.openclaw/
└── .sessions/
    ├── {session-id-1}.json     # Old format - one file per session
    ├── {session-id-2}.json
    ├── session_map.json         # Session key mapping
    └── ...
```

## Migration Steps

### Step 1: Dry Run (Recommended)

First, run in dry-run mode to see what will happen:

```bash
cd /path/to/openclaw-python
python -m openclaw.tools.migrate_sessions ~/.openclaw --dry-run --verbose
```

**Output:**
```
Found 15 session files to migrate
DRY RUN MODE - no changes will be made
Migrated session: agent:main:abc123 (abc123-uuid)
...
============================================================
Migration Results
============================================================
Status: success
Sessions found: 15
Sessions migrated: 15
Errors: 0
============================================================
DRY RUN - No changes were made
```

### Step 2: Run Migration

If the dry run looks good, run the actual migration:

```bash
python -m openclaw.tools.migrate_sessions ~/.openclaw --agent-id main
```

**Output:**
```
Starting migration for workspace: /Users/you/.openclaw
Found 15 session files to migrate
Migrated session: agent:main:abc123 (abc123-uuid)
...
Saved centralized store to /Users/you/.openclaw/.sessions/sessions.json
Backed up 15 files to /Users/you/.openclaw/.sessions/backup_old_format
============================================================
Migration Results
============================================================
Status: success
Sessions found: 15
Sessions migrated: 15
Errors: 0
Backup location: /Users/you/.openclaw/.sessions/backup_old_format
============================================================
Migration complete!
```

### Step 3: Verify Migration

Check that the new format works:

```python
from openclaw.config.sessions.store import load_session_store

store = load_session_store("/Users/you/.openclaw/.sessions/sessions.json")
print(f"Loaded {len(store)} sessions")
for key, entry in store.items():
    print(f"  {key}: {entry.session_id}")
```

### Step 4: Clean Up (Optional)

After verifying everything works, you can optionally remove old files:

```bash
# Old session files are backed up in backup_old_format/
# You can delete the originals if everything works:
cd ~/.openclaw/.sessions
rm -f {old-session-files}.json  # Be careful!
```

**CAUTION:** Only do this after thoroughly testing the new system.

## Migration Options

### Command Line Arguments

```bash
python -m openclaw.tools.migrate_sessions [OPTIONS] WORKSPACE_DIR

Arguments:
  WORKSPACE_DIR     Workspace directory containing .sessions/

Options:
  --agent-id TEXT   Agent identifier (default: main)
  --no-backup       Skip backing up old files (NOT recommended)
  --dry-run         Analyze without making changes
  --verbose, -v     Verbose logging
  --help            Show this message and exit
```

### Examples

**Migrate with custom agent ID:**
```bash
python -m openclaw.tools.migrate_sessions ~/.openclaw --agent-id my-agent
```

**Migrate without backup (not recommended):**
```bash
python -m openclaw.tools.migrate_sessions ~/.openclaw --no-backup
```

**Verbose output:**
```bash
python -m openclaw.tools.migrate_sessions ~/.openclaw -v
```

## What Gets Migrated?

### Session Metadata

Old format (.json):
```json
{
  "session_id": "abc123",
  "messages": [...],
  "metadata": {
    "label": "My Session",
    "display_name": "Test"
  },
  "created_at": "2026-02-11T10:00:00Z",
  "updated_at": "2026-02-11T12:00:00Z"
}
```

New format (sessions.json):
```json
{
  "agent:main:abc123": {
    "session_id": "abc123",
    "updated_at": 1707651600000,
    "session_file": "abc123.jsonl",
    "label": "My Session",
    "display_name": "Test"
  }
}
```

### Messages to Transcripts

Messages are extracted to separate JSONL files:

**Old:** Stored in session JSON  
**New:** `abc123.jsonl`
```jsonl
{"role": "user", "content": "Hello", "timestamp": "2026-02-11T10:00:00Z"}
{"role": "assistant", "content": "Hi there!", "timestamp": "2026-02-11T10:00:05Z"}
```

## After Migration

### New File Structure

```
~/.openclaw/
└── .sessions/
    ├── sessions.json                    # NEW: Centralized store
    ├── abc123.jsonl                     # NEW: Transcript files
    ├── def456.jsonl
    ├── sessions.json.lock               # NEW: File lock
    └── backup_old_format/               # NEW: Backup directory
        ├── abc123-uuid.json             # Old files backed up
        ├── def456-uuid.json
        └── session_map.json
```

### Using the New System

Load sessions:
```python
from openclaw.config.sessions.store import load_session_store

store = load_session_store("~/.openclaw/.sessions/sessions.json")
```

Update sessions:
```python
from openclaw.config.sessions.store import update_session_store

def update(store):
    store["agent:main:test"].thinking_level = "high"

update_session_store("~/.openclaw/.sessions/sessions.json", update)
```

Read transcripts:
```python
from openclaw.config.sessions.transcripts import read_transcript_preview

messages = read_transcript_preview(
    session_id="abc123",
    store_path="~/.openclaw/.sessions/sessions.json",
    limit=10
)
```

## Troubleshooting

### Error: "Sessions directory not found"

**Problem:** The .sessions directory doesn't exist.  
**Solution:** This is normal for new workspaces. No migration needed.

### Error: "Failed to migrate {file}"

**Problem:** A session file is corrupted or has invalid JSON.  
**Solution:** Check the error details. The migration continues with other files. You can manually fix or skip the problematic file.

### Error: "Failed to acquire lock"

**Problem:** Another process is accessing the store.  
**Solution:** Wait for the other process to complete, or increase the timeout.

### Sessions Not Appearing

**Problem:** Migrated but sessions don't show up.  
**Solution:**
1. Check the sessions.json file exists
2. Verify file permissions
3. Check logs for errors
4. Ensure you're using the correct agent_id

### Backup Recovery

If something goes wrong:

```bash
# Restore from automatic backup
cd ~/.openclaw/.sessions
cp backup_old_format/*.json .

# Or restore from your manual backup
cp -r ~/.openclaw.backup.20260211/.sessions ~/.openclaw/
```

## Rollback

To rollback to the old format:

1. Stop all openclaw processes
2. Delete the new files:
   ```bash
   cd ~/.openclaw/.sessions
   rm -f sessions.json sessions.json.lock *.jsonl
   ```
3. Restore from backup:
   ```bash
   cp backup_old_format/*.json .
   ```
4. Use the old openclaw-python version

**Note:** Rolling back will lose any changes made after migration.

## Best Practices

### Before Migration

1. ✅ Backup your data
2. ✅ Run dry-run first
3. ✅ Stop all openclaw processes
4. ✅ Verify disk space

### During Migration

1. ✅ Monitor the output
2. ✅ Note any errors
3. ✅ Don't interrupt the process

### After Migration

1. ✅ Verify sessions load correctly
2. ✅ Test key operations (list, update, etc.)
3. ✅ Keep backups for at least a week
4. ✅ Update any scripts/tools to use new format

## Getting Help

If you encounter issues:

1. **Check logs:** Run with `--verbose` for detailed output
2. **Review errors:** The migration reports detailed error information
3. **Verify format:** Ensure your session files are valid JSON
4. **Check permissions:** Ensure write access to .sessions directory

## Performance Benefits

After migration, you should see:

- **Faster startup:** Single file load vs multiple reads
- **Better concurrency:** File locking prevents conflicts
- **Reduced I/O:** Caching reduces disk access
- **Efficient queries:** Filtering without loading all transcripts

## Summary

The migration process is:

1. ✅ Safe (automatic backups)
2. ✅ Reversible (can rollback)
3. ✅ Well-tested (comprehensive test suite)
4. ✅ Documented (this guide)

**Recommended approach:**

```bash
# 1. Backup
cp -r ~/.openclaw ~/.openclaw.backup

# 2. Dry run
python -m openclaw.tools.migrate_sessions ~/.openclaw --dry-run -v

# 3. Migrate
python -m openclaw.tools.migrate_sessions ~/.openclaw

# 4. Verify
python -c "from openclaw.config.sessions.store import load_session_store; print(len(load_session_store('~/.openclaw/.sessions/sessions.json')))"
```

For more information, see:
- SESSION_MANAGEMENT_IMPLEMENTATION.md - Complete technical documentation
- tests/ - Example usage in test files
