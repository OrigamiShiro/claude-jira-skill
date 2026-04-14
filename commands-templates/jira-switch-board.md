---
description: Switch active Jira profile (interactive picker)
---

Switch active Jira board.

## Step 1: get profile list

Run:
```bash
python ~/.claude/skills/jira/scripts/jira_config.py list
```

Print stdout in a code block.

## Step 2: ask user

Via `AskUserQuestion` show profiles from list and let user pick one.

## Step 3: switch

Run:
```bash
python ~/.claude/skills/jira/scripts/jira_config.py switch <chosen>
```

**Print stdout verbatim in a code block.** No extra comments.

If no profiles exist — suggest `/jira-init`.
