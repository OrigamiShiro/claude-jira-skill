---
description: Show list of all Jira profiles
---

Show **all** configured profiles. Active one marked `(active)`.

## Step 1: get list

Run:
```bash
python ~/.claude/skills/jira/scripts/jira_config.py list
```

Parse output. Each line:
- ` *<name>` — active profile
- `  <name>` — regular

## Step 2: formatted output

Build a list and print **in your response as a code block**:

```
Profiles:
  1. myboard (active)
  2. work
  3. personal
```

Continuous numbering (1..N). Put `(active)` **only** on the active one.

**If user passed a name** after `/jira-show <name>` — run `python jira_config.py show <name>` and print the specific profile details (URL, Project, Board, Email, Token) in a code block.

**If no profiles** — print `❌ No profiles configured. Run /jira-init.`

No extra comments or questions.
