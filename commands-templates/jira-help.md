---
description: Показать список доступных jira-команд и скриптов
---

Выведи пользователю следующую справку **дословно** (в code-блоке, без своих комментариев и приветствий):

```
Jira CLI Skill — справка
──────────────────────────────────────────────

═══ Slash-команды (в Claude Code) ═══

  /jira-init                  Первичная настройка новой борды (location, name, url, project, board-id, email, token)
  /jira-add-board             Добавить ещё одну борду (не трогая существующие)
  /jira-switch-board          Переключить активную борду — интерактивный выбор из списка
  /jira-show [name]           Показать детали профиля (без имени — активный)
  /jira-remove-board <name>   Удалить профиль (boards/ + creds/ файлы)
  /jira-ping                  Проверить подключение к Jira (whoami)
  /jira-help                  Показать этот список

═══ CLI-скрипты (прямой вызов) ═══

  jira_init.py      Первичная настройка: --location, --name, --url, --project, --board-id, --email, --token
  jira_config.py    Профили: list | current | show [name] | switch <name> | remove <name>
  jira_ping.py      Проверка подключения (whoami)
  jira_create.py    <summary> [-d TEXT] [-t Задача|Баг|История|Эпик] [-a account_id] [--no-assignee]
  jira_update.py    transition <key> <status> | assign <key> <id> | unassign <key> | field <key> <field> <value>
  jira_delete.py    <key1> [<key2> ...] [--delete-subtasks]  — удалить issue
  jira_search.py    '<JQL>' [--limit N] [--fields f1,f2]
  jira_link.py      add <in> <out> --type TYPE | remove <link_id> | list <key> | types
  jira_worklog.py   add <key> <time> [--comment TEXT] [--started ISO] | list <key> | remove <key> <id>
  jira_sprint.py    list [--state] | show <id> | create --name NAME | move <id> <key1>... | start <id> | complete <id>
  jira_batch.py     JSON-массив через --file или stdin (ops: transition/worklog/link/assign/unassign/delete)

  Путь: ~/.claude/skills/jira/scripts/<script>
  Флаг --board <name> — разовый override профиля в любом скрипте.

═══ Быстрые примеры ═══

  # Создать задачу
  python jira_create.py "New feature" -t История

  # Закрыть и залогировать время
  python jira_update.py transition HOR-1 "Готово"
  python jira_worklog.py add HOR-1 "2h 30m" --comment "done"

  # Batch
  echo '[{"op":"transition","key":"HOR-1","status":"Готово"}]' | python jira_batch.py

Подробнее: ~/.claude/skills/jira/SKILL.md и README.md
```

**Не добавляй** никаких комментариев, приветствий, вопросов типа "какую борду сегодня мучить" — только справка.
