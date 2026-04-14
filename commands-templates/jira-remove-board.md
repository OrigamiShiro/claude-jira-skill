---
description: Remove a Jira profile (board + credentials)
---

Remove a Jira board profile.

## If name not provided — ask

1. Run `python ~/.claude/skills/jira/scripts/jira_config.py list`, print stdout.
2. Via `AskUserQuestion` let user pick profile to remove.

## Remove

```bash
python ~/.claude/skills/jira/scripts/jira_config.py remove <name>
```

**Print stdout verbatim in a code block.** No extra comments.

If the removed profile was active — suggest `/jira-switch-board` or `/jira-init`.
