---
description: Show list of available jira commands and scripts
---

Print the following help **verbatim** (as a code block, no comments or greetings):

```
Jira CLI Skill — help
─────────────────────────────────────────────

═══ Slash commands (Claude Code) ═══

  /jira-init                  Initial setup of a new board (location, name, url, project, board-id, email, token)
  /jira-add-board             Add another board (without touching existing ones)
  /jira-switch-board          Switch active board — interactive list picker
  /jira-show [name]           Show profile details (no name = active)
  /jira-remove-board <name>   Delete profile (boards/ + creds/ files)
  /jira-ping                  Check Jira connection (whoami)
  /jira-help                  Show this list

═══ CLI scripts (direct invocation) ═══

  jira_init.py      Initial setup: --location, --name, --url, --project, --board-id, --email, --token
  jira_config.py    Profiles: list | current | show [name] | switch <name> | remove <name>
  jira_ping.py      Connection check (whoami)
  jira_create.py    <summary> [-d TEXT] [-t Task|Bug|Story|Epic] [-a account_id] [--no-assignee]
  jira_update.py    transition <key> <status> | assign <key> <id> | unassign <key> | field <key> <field> <value>
  jira_delete.py    <key1> [<key2> ...] [--delete-subtasks]  — delete issue(s)
  jira_search.py    '<JQL>' [--limit N] [--fields f1,f2] [--all-projects]  — auto-scoped to active project
  jira_link.py      add <in> <out> --type TYPE | remove <link_id> | list <key> | types
  jira_worklog.py   add <key> <time> [--comment TEXT] [--started ISO] | list <key> | remove <key> <id>
  jira_sprint.py    list [--state] | show <id> | create --name NAME | move <id> <key1>... | start <id> | complete <id>
  jira_batch.py     JSON array via --file or stdin (ops: transition/worklog/link/assign/unassign/delete)

  Path: ~/.claude/skills/jira/scripts/<script>
  Flag --board <name> — one-off profile override in any script.

═══ Quick examples ═══

  # Create an issue
  python jira_create.py "New feature" -t Story

  # Close and log time
  python jira_update.py transition PROJ-1 "Done"
  python jira_worklog.py add PROJ-1 "2h 30m" --comment "done"

  # Batch
  echo '[{"op":"transition","key":"PROJ-1","status":"Done"}]' | python jira_batch.py

More: ~/.claude/skills/jira/SKILL.md and README.md
```

**Do not add** any comments, greetings, or questions — only the help.
