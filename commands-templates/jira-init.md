---
description: Первичная настройка Jira-борды (запрашивает credentials)
---

Нужно собрать **7 полей** от пользователя. У AskUserQuestion лимит 4 вопроса за вызов, поэтому опрашивай в **два этапа**.

## Этап 1 (AskUserQuestion): location, name, url, project

Задай сразу 4 вопроса в одном вызове AskUserQuestion:

1. **Location** — `local` (хранить в `./.claude/skills/jira/` текущего проекта) или `global` (по умолчанию, `~/.claude/skills/jira/`)
2. **Name профиля** — slug, например `hornyvilla`, `work`, `personal` (Other для ввода)
3. **URL Jira** — корневой URL инстанса, например `https://your-company.atlassian.net`. ⚠️ **Не полный URL борды** (без `/jira/software/projects/...`). Если юзер даст полный — скрипт сам обрежет до корня (Other)
4. **Project key** — короткий код проекта, например `HOR`, `PROJ`, `OV` (Other)

## Этап 2 (AskUserQuestion): board-id, email, token

После получения ответов из этапа 1 — сразу задай ещё 3 вопроса:

5. **Board ID** — число. Найти в URL борды: `.../boards/<ID>` → это `<ID>` (Other)
6. **Email** — Atlassian-аккаунт (Other)
7. **API Token** — https://id.atlassian.com/manage-profile/security/api-tokens → Create API token → скопировать (Other)

## Этап 3: запустить init

```bash
python ~/.claude/skills/jira/scripts/jira_init.py \
  --location <loc> --name <name> \
  --url <url> --project <key> --board-id <id> \
  --email <email> --token <token>
```

**Выведи stdout дословно в code-блоке** — там результат init + ping. Без лишних комментариев.
