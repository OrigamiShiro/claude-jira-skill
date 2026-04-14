---
description: Check Jira connection (whoami) with board picker
---

Check Jira connection. If multiple profiles exist — let user choose which one to ping.

## Step 1: get profile data

Run **silently** (do not show stdout to user):

```bash
python ~/.claude/skills/jira/scripts/jira_config.py list
```

Parse the output. Each line like ` *name` is the active profile, ` name` is other. Asterisk `*` means active.

## Step 2: build list and ask

**If 0 profiles** → report: `❌ No profiles configured. Run /jira-init.` and stop.

**If 1 profile** → skip the question, ping directly.

**If 2+ profiles** — build `AskUserQuestion` options yourself:

- **Option 1** — active profile, label `<name> (active)`, description `Recommended`.
- **Options 2..N** — other profiles in list order.
- AskUserQuestion supports 2-4 options. If more than 4 profiles — take active + first 3 others; remaining are available via "Other".

Question: `"Which board to ping?"`

## Step 3: ping

```bash
python ~/.claude/skills/jira/scripts/jira_ping.py --board <chosen>
```

**Print stdout verbatim in a code block.** No extra comments.
