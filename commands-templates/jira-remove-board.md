---
description: Удалить Jira-профиль (боард + креды)
---

## Если имя не указано — спросить

1. Запусти `python ~/.claude/skills/jira/scripts/jira_config.py list`, выведи stdout.
2. Через `AskUserQuestion` дай пользователю выбрать профиль для удаления.

## Удалить

```bash
python ~/.claude/skills/jira/scripts/jira_config.py remove <name>
```

**Выведи stdout дословно в code-блоке.** Без лишних комментариев.

Если удалили активный — предложи `/jira-switch-board` или `/jira-init`.
