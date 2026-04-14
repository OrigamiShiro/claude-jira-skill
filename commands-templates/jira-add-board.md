---
description: Add another Jira board (new profile)
---

Same as `/jira-init`, but for adding an additional board — existing profiles untouched.

Collect **7 fields** in **two AskUserQuestion stages** (4-question limit per call):

## Stage 1: location, name, url, project

1. **Location** — `local` or `global`
2. **Name** — new slug (must not collide with existing; check via `python ~/.claude/skills/jira/scripts/jira_config.py list`)
3. **Jira URL** — root (e.g. `https://company.atlassian.net`, without suffixes). Script will trim full URLs to root.
4. **Project key** — e.g. `PROJ`

## Stage 2: board-id, email, token

5. **Board ID** — integer (from board URL `.../boards/<ID>`)
6. **Email** — Atlassian account
7. **API Token** — https://id.atlassian.com/manage-profile/security/api-tokens

## Run

```bash
python ~/.claude/skills/jira/scripts/jira_init.py \
  --location <loc> --name <new name> \
  --url <url> --project <key> --board-id <id> \
  --email <email> --token <token>
```

**Print stdout verbatim in a code block.**

After init the newly created becomes active. If user wants to keep old profile active — suggest `/jira-switch-board`.
