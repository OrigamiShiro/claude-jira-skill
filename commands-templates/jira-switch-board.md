---
description: Переключить активный Jira-профиль (интерактивный выбор)
---

## Шаг 1: получить список профилей

Запусти:
```bash
python ~/.claude/skills/jira/scripts/jira_config.py list
```

Выведи stdout в code-блоке.

## Шаг 2: спросить пользователя

Через `AskUserQuestion` покажи профили из списка и дай выбрать (один).

## Шаг 3: переключить

Запусти:
```bash
python ~/.claude/skills/jira/scripts/jira_config.py switch <выбранный>
```

**Выведи stdout дословно в code-блоке.** Без лишних комментариев.

Если профилей нет — предложи `/jira-init`.
