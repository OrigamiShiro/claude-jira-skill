---
description: Initial Jira board setup (prompts for credentials)
---

Collect **7 fields** from the user. `AskUserQuestion` has a 4-questions-per-call limit, so ask in **two stages**.

## Stage 1 (AskUserQuestion): location, name, url, project

Ask 4 questions in one AskUserQuestion call:

1. **Location** — `local` (store in `./.claude/skills/jira/` of current project) or `global` (default, `~/.claude/skills/jira/`)
2. **Profile name** — slug, e.g. `work`, `personal`, `myboard` (Other for input)
3. **Jira URL** — root instance URL, e.g. `https://your-company.atlassian.net`. ⚠️ **Not the full board URL** (no `/jira/software/projects/...`). If user gives full URL — script trims to root (Other)
4. **Project key** — short code, e.g. `PROJ`, `ABC` (Other)

## Stage 2 (AskUserQuestion): board-id, email, token

After stage 1 answers — ask 3 more:

5. **Board ID** — integer. Find it in the board URL: `.../boards/<ID>` → this `<ID>` (Other)
6. **Email** — Atlassian account (Other)
7. **API Token** — https://id.atlassian.com/manage-profile/security/api-tokens → Create API token → copy (Other)

## Stage 3: run init

```bash
python ~/.claude/skills/jira/scripts/jira_init.py \
  --location <loc> --name <name> \
  --url <url> --project <key> --board-id <id> \
  --email <email> --token <token>
```

**Print stdout verbatim in a code block** — it contains init + ping result. No extra comments.
