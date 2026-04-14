---
description: Добавить ещё одну Jira-борду (новый профиль)
---

То же что `/jira-init`, но для дополнительной борды — существующие профили не трогать.

Собери **7 полей** в **два этапа** AskUserQuestion (у него лимит 4 вопроса за вызов):

## Этап 1: location, name, url, project

1. **Location** — `local` или `global`
2. **Name** — новый slug (не должен совпадать с существующими — можно проверить через `python ~/.claude/skills/jira/scripts/jira_config.py list`)
3. **URL Jira** — корневой (например `https://company.atlassian.net`, без хвостов). Скрипт сам обрежет полный URL до корня.
4. **Project key** — например `PROJ`

## Этап 2: board-id, email, token

5. **Board ID** — число (из URL борды `.../boards/<ID>`)
6. **Email** — Atlassian-аккаунт
7. **API Token** — https://id.atlassian.com/manage-profile/security/api-tokens

## Запуск

```bash
python ~/.claude/skills/jira/scripts/jira_init.py \
  --location <loc> --name <новое имя> \
  --url <url> --project <key> --board-id <id> \
  --email <email> --token <token>
```

**Выведи stdout дословно в code-блоке.**

После init активным становится последний созданный профиль. Если нужно вернуться к старому — предложи `/jira-switch-board`.
