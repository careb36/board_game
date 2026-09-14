# board_game

board games

## Installed Tools

### context-mode
Context window optimization for AI coding agents. Installed globally via npm.

**Features:**
- Sandbox tools keep raw data out of the context window (98% reduction)
- Session continuity via SQLite tracking
- 11 MCP tools: `ctx_batch_execute`, `ctx_execute`, `ctx_execute_file`, `ctx_index`, `ctx_search`, `ctx_fetch_and_index`, `ctx_stats`, `ctx_doctor`, `ctx_upgrade`, `ctx_purge`, `ctx_insight`

**Usage:**
```bash
context-mode doctor    # Check installation and configuration
context-mode stats     # View context savings
```

### i-have-adhd
ADHD-friendly output skill for coding agents.

**Features:**
- Leads with the next action
- Numbers multi-step tasks
- Ends with one concrete next step
- Suppresses tangents
- Provides specific time estimates
- Makes wins visible

**Location:** `/usr/lib/node_modules/context-mode/skills/i-have-adhd/SKILL.md`

**Usage:**
Invoke with `/i-have-adhd` in Claude Code or compatible agents.
