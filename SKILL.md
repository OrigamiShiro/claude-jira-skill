---
name: jira
description: Manage Jira tasks via CLI scripts — create, transition, link, search, worklog, sprints, batch operations. Multi-board (profile) support with switching. Activate when user mentions Jira, issue keys like XYZ-123, `/jira-*` commands, or works with tasks/sprints.
---

# Jira CLI Skill

Set of Python CLI scripts for Jira Cloud REST API. Single-responsibility — one script, one concern.

## When to Use

Activate this skill when user:

- Mentions **Jira**, **issue**, **sprint**, **worklog**, **backlog**, **board**
- Uses issue keys like `ABC-123`, `PROJ-42` (letters-dash-digits)
- Asks to **create**, **close**, **transition to Done/In Progress**, **log time**, **link**, **find issues**
- Invokes any `/jira-*` command (init, switch-board, add-board, show, remove, ping, help)
- Wants **bulk** action on N issues (use `jira_batch.py`)

**Do NOT activate** for other trackers (Linear, Asana, GitHub Issues).

## Slash commands (triggers)

| User command | Agent action |
|--------------|--------------|
| `/jira-init` | Via AskUserQuestion: location (local/global), name, url, project, board-id, email, token. Then `python jira_init.py ...` |
| `/jira-add-board` | Same as init, but different `--name`. Existing profiles untouched. |
| `/jira-switch-board` | `python jira_config.py list` → AskUserQuestion (pick) → `jira_config.py switch <name>`. |
| `/jira-show [name]` | `python jira_config.py show [name]`. |
| `/jira-remove-board <name>` | `python jira_config.py remove <name>`. |
| `/jira-ping` | `python jira_ping.py`. |
| `/jira-help` | Show list of all commands and scripts. |

## Where the skill lives

- **Scripts** (always global): `~/.claude/skills/jira/scripts/`
- **Config + boards + creds**: either local (`./.claude/skills/jira/`) or global (`~/.claude/skills/jira/`) — chosen by user at init.
- **Config lookup** (automatic in `lib/config.py`): first `.claude/skills/jira/config.json` walking up from CWD, then global.

## Script path

Scripts live in `~/.claude/skills/jira/scripts/`. Use:

```bash
python ~/.claude/skills/jira/scripts/<script>.py [args]
```

On Windows via bash: `python "C:/Users/<USER>/.claude/skills/jira/scripts/<script>.py"`.

Or: `python "$HOME/.claude/skills/jira/scripts/<script>.py"`.

---

## Script catalog

### jira_init.py — board setup

```bash
python jira_init.py \
  --location {local|global} \
  --name <slug> \
  --url <jira_url> \
  --project <KEY> \
  --board-id <N> \
  --email <email> \
  --token <api_token> \
  [--overwrite] [--no-ping]
```

| Flag | Purpose |
|------|---------|
| `--location` | `local` (`.claude/skills/jira/` in CWD) or `global` (`~/.claude/skills/jira/`) |
| `--name` | Profile name (alphanumeric + dash) |
| `--url` | Jira URL (e.g. `https://your-company.atlassian.net`) — full board URLs are normalized to root |
| `--project` | Project key (e.g. `PROJ`) |
| `--board-id` | Board ID (integer) |
| `--email` | Atlassian account email |
| `--token` | API token (create at https://id.atlassian.com/manage-profile/security/api-tokens) |
| `--overwrite` | Overwrite existing profile |
| `--no-ping` | Skip post-init connection check |

**Output:** `✓ Profile '<name>' created` + ping result or warning.

---

### jira_config.py — profile management

```bash
python jira_config.py list                    # all profiles
python jira_config.py current                 # active profile
python jira_config.py show [name]             # details (no name = active)
python jira_config.py switch <name>           # change active
python jira_config.py remove <name>           # delete profile
```

| Subcommand | Args | Output |
|------------|------|--------|
| `list` | — | Profile list, `*` marks active |
| `current` | — | Active profile name |
| `show` | `[name]` | URL, project, board, email, masked token |
| `switch` | `<name>` | `✓ Active profile: <name>` |
| `remove` | `<name>` | `✓ Profile '<name>' removed` |

---

### jira_ping.py — connection check

```bash
python jira_ping.py [--board <name>]
```

Calls `/rest/api/3/myself`. Without `--board` — active profile.

**Output:** `✓ Connected as: <name> (<email>)` + URL/Project/Board.

---

### jira_create.py — create issue

```bash
python jira_create.py <summary> \
  [-d, --description TEXT] \
  [-t, --type {Task|Bug|Story|Epic}] \
  [-a, --assignee ACCOUNT_ID] \
  [--no-assignee] \
  [--board <name>]
```

| Flag | Default | Description |
|------|---------|-------------|
| `summary` | (required) | Issue title |
| `-d, --description` | empty | Description (plain text, converted to ADF) |
| `-t, --type` | `Task` | Issue type |
| `-a, --assignee` | current user | accountId of assignee (defaults to current user) |
| `--no-assignee` | false | Don't assign anyone |

**Output:** `✓ Issue created: PROJ-XXX | <browse_url>`.

---

### jira_delete.py — delete issue

```bash
python jira_delete.py <key1> [<key2> ...] [--delete-subtasks] [--board <name>]
```

Deletes one or more issues. **Irreversible.**

| Flag | Description |
|------|-------------|
| `keys` | One or more keys |
| `--delete-subtasks` | Delete together with subtasks (otherwise Jira returns error if subtasks exist) |

**Output:** `✓ PROJ-XXX deleted` (per issue), summary `✓ N deleted | ✗ M errors` if 2+.

---

### jira_update.py — update issue

```bash
python jira_update.py [--board <name>] <subcommand> ...
```

| Subcommand | Args | Description |
|------------|------|-------------|
| `transition` | `<key> <status>` | Change status (status name or transition name) |
| `assign` | `<key> <account_id>` | Set assignee |
| `unassign` | `<key>` | Remove assignee |
| `field` | `<key> <field> <value>` | Update any field (`summary`, `description`, etc.) |

**Output:** `✓ <key> → <status>`, `✓ <key> assigned to <id>`, `✓ <key>.<field> updated`.

---

### jira_search.py — JQL search

```bash
python jira_search.py "<JQL>" \
  [--limit N] \
  [--fields f1,f2,...] \
  [--all-projects] \
  [--board <name>]
```

| Flag | Default | Description |
|------|---------|-------------|
| `JQL` | (required) | E.g. `status='In Progress'` or `assignee=currentUser()` |
| `--limit` | 50 | Max results |
| `--fields` | `summary,status,issuetype` | Comma-separated: `key`, `summary`, `status`, `issuetype`, `assignee`, or any field |
| `--all-projects` | false | Search across the whole Jira instance instead of just the active profile's project |

**Scoping behavior:** by default the query is auto-scoped to the **active profile's project** — the JQL gets wrapped as `project="<key>" AND (<user_jql>)`. This avoids leaking tasks from other projects under the same instance. Use `--all-projects` to disable. If the JQL already contains `project=` / `project IN (...)`, auto-scoping is skipped.

**Output:** Table `KEY | <fields>` + `Found: N`.

---

### jira_link.py — issue links

```bash
python jira_link.py [--board <name>] <subcommand>
```

| Subcommand | Args | Description |
|------------|------|-------------|
| `add` | `<inward> <outward> --type TYPE` | Create link (inward = "child"/"blocked", outward = "parent"/"blocker") |
| `remove` | `<link_id>` | Delete link by ID |
| `list` | `<key>` | All links for issue (shows IDs for remove) |
| `types` | — | Available link types with IDs |

**Aliases for `--type`:**
- `parent-child` → 10007 (`is child of` ↔ `is parent of`)
- `blocks` → 10000 (`is blocked by` ↔ `blocks`)
- `relates` → 10003 (`relates to` ↔ `relates to`)
- `duplicate` → 10002
- `cloners` → 10001

Or pass ID directly: `--type 10007`.

**Output:** `✓ PROJ-1 ← PROJ-2 (type id 10007)`.

---

### jira_worklog.py — work log

```bash
python jira_worklog.py [--board <name>] <subcommand>
```

| Subcommand | Args | Description |
|------------|------|-------------|
| `add` | `<key> <time> [--comment TEXT] [--started ISO]` | Add entry. `time`: `"3h 15m"`, `"1d"`, `"30m"`, `"1w"` |
| `list` | `<key>` | All worklogs |
| `remove` | `<key> <worklog_id>` | Remove worklog |

**Output:** `✓ Worklog added: <key> 3h 15m (id <wid>)`.

---

### jira_sprint.py — sprints (Agile)

```bash
python jira_sprint.py [--board <name>] <subcommand>
```

| Subcommand | Args | Description |
|------------|------|-------------|
| `list` | `[--state {active|future|closed}] [--board-id N]` | Board sprints |
| `show` | `<sprint_id>` | Details + issues |
| `create` | `--name NAME [--goal TEXT] [--start ISO] [--end ISO] [--board-id N]` | Create sprint |
| `move` | `<sprint_id> <key1> [<key2> ...]` | Move issues into sprint |
| `start` | `<sprint_id> [--start ISO] [--end ISO]` | Start sprint |
| `complete` | `<sprint_id>` | Close sprint |

**Output:**
- `Board <id>:` + list `[sprint_id] <name> (state)`
- `✓ Sprint '<name>' created (id: N)`
- `✓ N issue(s) moved to sprint <id>`

---

### jira_batch.py — bulk operations

```bash
python jira_batch.py [--file <path>] [--board <name>]
```

Accepts JSON array of commands from `--file` or stdin.

**Supported operations (`op`):**

| `op` | Fields |
|------|--------|
| `transition` | `key`, `status` |
| `worklog` | `key`, `time`, `comment` (opt.), `started` (opt.) |
| `link` | `inward`, `outward`, `type` |
| `assign` | `key`, `account_id` |
| `unassign` | `key` |
| `delete` | `key`, `delete_subtasks` (bool, opt.) |

**Example JSON:**
```json
[
  {"op": "transition", "key": "PROJ-1", "status": "Done"},
  {"op": "worklog", "key": "PROJ-1", "time": "2h", "comment": "fix bug"},
  {"op": "link", "inward": "PROJ-2", "outward": "PROJ-1", "type": "parent-child"}
]
```

**Output:** per-line results + summary `✓ N success | ✗ M errors`.

---

## Scenarios (flows)

### First run (`/jira-init`)

1. Agent collects via `AskUserQuestion`:
   - Location: `local` (project) or `global` (all projects)
   - Profile name (slug)
   - Jira URL
   - Project key
   - Board ID
   - Email
   - API token
2. Run: `python ~/.claude/skills/jira/scripts/jira_init.py --location ... --name ... --url ... --project ... --board-id ... --email ... --token ...`
3. Script auto-pings at the end.
4. Report: `✓ Profile '<name>' created and connected`.

### Add new board (`/jira-add-board`)

Same as init but with new `--name`. Existing profile untouched. After init the newly created becomes active (init always sets the freshly created as active).

### Switch board (`/jira-switch-board`)

1. `python jira_config.py list` — get list.
2. Show profiles via `AskUserQuestion`, let user pick.
3. `python jira_config.py switch <chosen>`.

### Show active (`/jira-show`)

`python jira_config.py current` — brief output (name only).
`python jira_config.py show` — details with masked token.

### Multiple boards in session — what to do

**Do NOT re-ask every time.** Active board in `config.json` persists until explicit `/jira-switch-board`. All scripts read `config.json` — if active profile is set, they use it.

If you call a command and the script returns "No active board selected" → agent **itself** runs `/jira-switch-board` or `/jira-init`.

---

## Response format (in context)

**Rules:**
1. **One-line summary** — output only the essence. Don't leak API JSON responses.
2. **Prefixes:** `✓` (success), `❌` (error), `⚠` (warning).
3. **Keys and URLs** — mandatory for created/changed issues.

**Success templates:**
```
✓ Issue created: PROJ-123 | https://your-company.atlassian.net/browse/PROJ-123
✓ PROJ-123 → Done
✓ PROJ-123 assigned to 712020:abc
✓ PROJ-123 ← PROJ-42 (type id 10007)
✓ Worklog added: PROJ-123 3h 15m (id 23016)
✓ Sprint 'Sprint 5' created (id: 30)
✓ 5 ops | ✗ 0 errors
```

**Error templates:**
```
❌ Unauthorized (401). Check email and API token.
❌ Resource not found (404): https://...
❌ Profile 'ghost' not found. Available: alpha, beta
❌ Transition to 'Unknown' unavailable for PROJ-1
```

**Do NOT:**
- Say "here's the API result: {...}"
- Duplicate full JSON payload of created issue
- Repeat the same message for 100 batch items — print a summary

---

## Install dependencies

Skill only needs `requests`:

```bash
pip install requests
```

For colleagues: `pip install -r ~/.claude/skills/jira/requirements.txt`.

---

## Tests

93 unit tests in `scripts/lib/tests/` and `scripts/tests/`:

```bash
cd ~/.claude/skills/jira/scripts
python -m unittest discover -s lib/tests
python -m unittest discover -s tests
```

All tests are self-contained (mock requests), no live Jira required. Subprocess tests use env flags `JIRA_SKILL_NO_UPWARD_SEARCH=1` and `JIRA_SKILL_GLOBAL_CONFIG=<fake_path>` for isolation.

---

## Env variables

| Variable | Purpose |
|----------|---------|
| `JIRA_SKILL_GLOBAL_CONFIG` | Override global config path (for tests) |
| `JIRA_SKILL_NO_UPWARD_SEARCH` | `1` disables upward config lookup (for tests) |

Not needed in normal operation.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `❌ Unauthorized (401)` | Invalid token or email | Check `.claude/skills/jira/creds/<name>.json`, regenerate token |
| `❌ Resource not found (404)` | Wrong issue key or URL | Verify key/URL |
| `❌ No active board selected` | `config.json` without `active_board` | Run `/jira-init` or `/jira-switch-board` |
| `❌ config.json not found` | Skill not configured | `/jira-init` |
| `❌ Transition '...' unavailable` | Workflow doesn't allow this transition | Check available transitions via `jira_search` |
| Unicode errors on Windows | Old cp1252 console | Scripts auto-switch to UTF-8 — update Python ≥3.7 |
