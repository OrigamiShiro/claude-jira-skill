---
name: jira
description: Управление задачами в Jira через CLI-скрипты — создание, перевод статусов, связывание, поиск, worklog, спринты, batch-операции. Поддержка нескольких бордов (профилей) с переключением. Используй при упоминании Jira, ключей вида XYZ-123, командах /jira-*, или работе с задачами/спринтами.
---

# Jira CLI Skill

Набор Python-скриптов для работы с Jira Cloud REST API. Single-responsibility — каждый скрипт решает одну задачу.

## When to Use

Активируй скилл если пользователь:

- Упоминает **Jira**, **issue**, **спринт**, **worklog**, **бэклог**, **борду**
- Использует ключи задач вида `HOR-123`, `PROJ-42` (буквы-дефис-цифры)
- Просит **создать**, **закрыть**, **перевести в Done/In Progress**, **залогировать время**, **связать**, **найти задачи**
- Вызывает любую команду `/jira-*` (init, switch-board, add-board, show, remove, ping)
- Хочет **массово** что-то сделать с N задачами (используй `jira_batch.py`)

**Не активируй**, если речь о других трекерах (Linear, Asana, GitHub Issues).

## Slash-команды (триггеры)

| Команда юзера | Действие агента |
|---------------|-----------------|
| `/jira-init` | Запросить через AskUserQuestion: location (local/global), name, url, project, board-id, email, token. Затем `python jira_init.py ...` |
| `/jira-add-board` | То же что init, но `--name` другой. Существующий профиль не трогать |
| `/jira-switch-board` | `python jira_config.py list` → AskUserQuestion (выбор) → `jira_config.py switch <name>` |
| `/jira-show [name]` | `python jira_config.py show [name]` |
| `/jira-remove-board <name>` | `python jira_config.py remove <name>` |
| `/jira-ping` | `python jira_ping.py` |

## Где живёт скилл

- **Скрипты** (всегда глобально): `~/.claude/skills/jira/scripts/`
- **Config + boards + creds**: либо локально (`./.claude/skills/jira/`), либо глобально (`~/.claude/skills/jira/`) — выбор юзера при init
- **Поиск config** (автоматический в `lib/config.py`): сначала `.claude/skills/jira/config.json` от CWD вверх по дереву, потом глобальный

## Как агент находит путь к скрипту

Скрипты живут в `~/.claude/skills/jira/scripts/`. Используй:

```bash
python ~/.claude/skills/jira/scripts/<script>.py [args]
```

На Windows через bash: `python "C:/Users/<USER>/.claude/skills/jira/scripts/<script>.py"`.

Можно также: `python "$HOME/.claude/skills/jira/scripts/<script>.py"`.

---

## Каталог скриптов

### jira_init.py — первичная настройка борды

```bash
python jira_init.py \
  --location {local|global} \
  --name <slug> \
  --url <jira_url> \
  --project <KEY> \
  --board-id <N> \
  --email <email> \
  --token <api_token> \
  [--overwrite] [--no-ping]
```

| Флаг | Назначение |
|------|-----------|
| `--location` | `local` (`.claude/skills/jira/` в CWD) или `global` (`~/.claude/skills/jira/`) |
| `--name` | Имя профиля (alphanumeric + дефис) |
| `--url` | Jira URL (например `https://passionpanda.atlassian.net`) |
| `--project` | Project key (например `HOR`) |
| `--board-id` | Board ID (целое число) |
| `--email` | Email Atlassian-аккаунта |
| `--token` | API token (создаётся на https://id.atlassian.com/manage-profile/security/api-tokens) |
| `--overwrite` | Перезаписать существующий профиль |
| `--no-ping` | Не проверять подключение после init |

**Выход:** `✓ Профиль '<name>' создан` + ping result или предупреждение.

---

### jira_config.py — управление профилями

```bash
python jira_config.py list                    # все профили
python jira_config.py current                 # активный
python jira_config.py show [name]             # детали (без name = активный)
python jira_config.py switch <name>           # сменить активный
python jira_config.py remove <name>           # удалить профиль
```

| Subcommand | Аргументы | Выход |
|------------|-----------|-------|
| `list` | — | Список профилей с `*` у активного |
| `current` | — | Имя активного профиля |
| `show` | `[name]` | URL, project, board, email, замаскированный токен |
| `switch` | `<name>` | `✓ Активный профиль: <name>` |
| `remove` | `<name>` | `✓ Профиль '<name>' удалён` |

---

### jira_ping.py — проверка подключения

```bash
python jira_ping.py [--board <name>]
```

Вызывает `/rest/api/3/myself`. Без `--board` — активный профиль.

**Выход:** `✓ Подключено как: <name> (<email>)` + URL/Project/Board.

---

### jira_create.py — создание issue

```bash
python jira_create.py <summary> \
  [-d, --description TEXT] \
  [-t, --type {Задача|Баг|История|Эпик}] \
  [-a, --assignee ACCOUNT_ID] \
  [--no-assignee] \
  [--board <name>]
```

| Флаг | Default | Описание |
|------|---------|----------|
| `summary` | (обязательный) | Заголовок |
| `-d, --description` | пусто | Описание (plain text, конвертируется в ADF) |
| `-t, --type` | `Задача` | Тип issue |
| `-a, --assignee` | None | accountId исполнителя |
| `--no-assignee` | False | Не назначать никого |

**Выход:** `✓ Задача создана: HOR-XXX | <browse_url>`.

---

### jira_delete.py — удаление issue

```bash
python jira_delete.py <key1> [<key2> ...] [--delete-subtasks] [--board <name>]
```

Удаляет одну или несколько issue. **Необратимо.**

| Флаг | Описание |
|------|----------|
| `keys` | Один или несколько ключей |
| `--delete-subtasks` | Удалить вместе с подзадачами (иначе Jira вернёт ошибку если есть subtasks) |

**Выход:** `✓ HOR-XXX удалена` (на каждую), в конце `✓ N удалено | ✗ M ошибок` если 2+.

---

### jira_update.py — обновление issue

```bash
python jira_update.py [--board <name>] <subcommand> ...
```

| Subcommand | Аргументы | Описание |
|------------|-----------|----------|
| `transition` | `<key> <status>` | Сменить статус (имя статуса или transition name) |
| `assign` | `<key> <account_id>` | Назначить assignee |
| `unassign` | `<key>` | Снять assignee |
| `field` | `<key> <field> <value>` | Обновить поле (`summary`, `description`, etc.) |

**Выход:** `✓ <key> → <status>`, `✓ <key> назначен на <id>`, `✓ <key>.<field> обновлено`.

---

### jira_search.py — JQL поиск

```bash
python jira_search.py "<JQL>" \
  [--limit N] \
  [--fields f1,f2,...] \
  [--board <name>]
```

| Флаг | Default | Описание |
|------|---------|----------|
| `JQL` | (обязательный) | Например `project=HOR AND status='В работе'` |
| `--limit` | 50 | Максимум результатов |
| `--fields` | `summary,status,issuetype` | Поля через запятую: `key`, `summary`, `status`, `issuetype`, `assignee`, или произвольное |

**Выход:** Таблица `KEY | <fields>` + `Found: N`.

---

### jira_link.py — связи между issues

```bash
python jira_link.py [--board <name>] <subcommand>
```

| Subcommand | Аргументы | Описание |
|------------|-----------|----------|
| `add` | `<inward> <outward> --type TYPE` | Создать связь (inward = "child"/"blocked", outward = "parent"/"blocker") |
| `remove` | `<link_id>` | Удалить связь по ID |
| `list` | `<key>` | Все связи issue (показывает ID для последующего remove) |
| `types` | — | Доступные типы связей с ID |

**Алиасы для `--type`:**
- `parent-child` → 10007 (`is child of` ↔ `is parent of`)
- `blocks` → 10000 (`is blocked by` ↔ `blocks`)
- `relates` → 10003 (`relates to` ↔ `relates to`)
- `duplicate` → 10002
- `cloners` → 10001

Можно передать ID напрямую: `--type 10007`.

**Выход:** `✓ HOR-1 ← HOR-2 (type id 10007)`.

---

### jira_worklog.py — журнал работы

```bash
python jira_worklog.py [--board <name>] <subcommand>
```

| Subcommand | Аргументы | Описание |
|------------|-----------|----------|
| `add` | `<key> <time> [--comment TEXT] [--started ISO]` | Добавить запись. `time`: `"3h 15m"`, `"1d"`, `"30m"`, `"1w"` |
| `list` | `<key>` | Все worklogs |
| `remove` | `<key> <worklog_id>` | Удалить worklog |

**Выход:** `✓ Worklog добавлен: <key> 3h 15m (id <wid>)`.

---

### jira_sprint.py — спринты (Agile)

```bash
python jira_sprint.py [--board <name>] <subcommand>
```

| Subcommand | Аргументы | Описание |
|------------|-----------|----------|
| `list` | `[--state {active|future|closed}] [--board-id N]` | Список спринтов борды |
| `show` | `<sprint_id>` | Детали + issues в спринте |
| `create` | `--name NAME [--goal TEXT] [--start ISO] [--end ISO] [--board-id N]` | Создать спринт |
| `move` | `<sprint_id> <key1> [<key2> ...]` | Переместить issues |
| `start` | `<sprint_id> [--start ISO] [--end ISO]` | Запустить спринт |
| `complete` | `<sprint_id>` | Закрыть спринт |

**Выход:**
- `Board <id>:` + список `[sprint_id] <name> (state)`
- `✓ Спринт '<name>' создан (id: N)`
- `✓ N issue(s) перемещены в спринт <id>`

---

### jira_batch.py — массовые операции

```bash
python jira_batch.py [--file <path>] [--board <name>]
```

Принимает JSON-массив команд из `--file` или stdin.

**Поддерживаемые операции (`op`):**

| `op` | Поля |
|------|------|
| `transition` | `key`, `status` |
| `worklog` | `key`, `time`, `comment` (опц.), `started` (опц.) |
| `link` | `inward`, `outward`, `type` |
| `assign` | `key`, `account_id` |
| `unassign` | `key` |
| `delete` | `key`, `delete_subtasks` (bool, опц.) |

**Пример JSON:**
```json
[
  {"op": "transition", "key": "HOR-1", "status": "Готово"},
  {"op": "worklog", "key": "HOR-1", "time": "2h", "comment": "fix bug"},
  {"op": "link", "inward": "HOR-2", "outward": "HOR-1", "type": "parent-child"}
]
```

**Выход:** построчные результаты + сводка `✓ N успехов | ✗ M ошибок`.

---

## Сценарии (флоу)

### Первый запуск (`/jira-init`)

1. Агент собирает данные через `AskUserQuestion`:
   - Location: `local` (хранить в проекте) или `global` (для всех проектов)
   - Name профиля (slug)
   - URL Jira
   - Project key
   - Board ID
   - Email
   - API token
2. Запускает: `python ~/.claude/skills/jira/scripts/jira_init.py --location ... --name ... --url ... --project ... --board-id ... --email ... --token ...`
3. Скрипт сам делает ping в конце.
4. Сообщает: `✓ Профиль '<name>' создан и подключён`.

### Добавление новой борды (`/jira-add-board`)

То же что init, но `--name <new>`. Существующий профиль не трогается. После — активным становится новый (последний init).

### Переключение борды (`/jira-switch-board`)

1. `python jira_config.py list` — получить список.
2. Через `AskUserQuestion` показать профили, дать выбрать.
3. `python jira_config.py switch <chosen>`.

### Показать активный (`/jira-show`)

`python jira_config.py current` — короткий вывод (только имя).
`python jira_config.py show` — подробности с маской токена.

### Несколько бордов в сессии — что делать

**НЕ надо переспрашивать каждый раз.** Active board в `config.json` живёт до явного `/jira-switch-board`. Все скрипты читают `config.json` — если активный профиль установлен, используют его.

Если вызвал команду и скрипт ответил "Активная борда не выбрана" → агент **сам** запускает флоу `/jira-switch-board` или `/jira-init`.

---

## Формат ответа в контекст

**Правила:**
1. **Однострочный итог** — выводи только ключевую информацию. JSON-ответы API не лей в контекст.
2. **Префиксы:** `✓` (успех), `❌` (ошибка), `⚠` (предупреждение).
3. **Ключи и URL** — обязательны для созданных/изменённых issues.

**Шаблоны успеха:**
```
✓ Задача создана: HOR-258 | https://passionpanda.atlassian.net/browse/HOR-258
✓ HOR-258 → Готово
✓ HOR-258 назначен на 712020:abc
✓ HOR-258 ← HOR-21 (type id 10007)
✓ Worklog добавлен: HOR-258 3h 15m (id 23016)
✓ Спринт 'Sprint 5' создан (id: 30)
✓ 5 операций | ✗ 0 ошибок
```

**Шаблоны ошибок:**
```
❌ Unauthorized (401). Проверь email и API token.
❌ Resource not found (404): https://...
❌ Профиль 'ghost' не найден. Доступны: hornyvilla, other
❌ Переход в статус 'Несуществует' недоступен для HOR-1
```

**Что НЕ делать:**
- Не пиши «вот результат API: {...}»
- Не дублируй полный JSON-payload созданного issue
- Не повторяй одно и то же сообщение если batch обработал 100 элементов — выведи сводку

---

## Установка зависимостей

Скилл требует только `requests`:

```bash
pip install requests
```

Для коллег: `pip install -r ~/.claude/skills/jira/requirements.txt`.

---

## Тесты

В скилле 93 unit-теста (`scripts/lib/tests/` и `scripts/tests/`):

```bash
cd ~/.claude/skills/jira/scripts
python -m unittest discover -s lib/tests
python -m unittest discover -s tests
```

Все тесты автономные (mock requests), не требуют живого Jira-инстанса. Subprocess-тесты используют env-флаги `JIRA_SKILL_NO_UPWARD_SEARCH=1` и `JIRA_SKILL_GLOBAL_CONFIG=<fake_path>` для изоляции.

---

## Env-переменные

| Переменная | Назначение |
|------------|-----------|
| `JIRA_SKILL_GLOBAL_CONFIG` | Override пути к глобальному config (для тестов) |
| `JIRA_SKILL_NO_UPWARD_SEARCH` | `1` отключает поиск config вверх по дереву (для тестов) |

В обычной работе эти переменные **не нужны**.

---

## Troubleshooting

| Симптом | Причина | Решение |
|---------|---------|---------|
| `❌ Unauthorized (401)` | Неверный токен или email | Проверь `.claude/skills/jira/creds/<name>.json`, перегенерируй токен |
| `❌ Resource not found (404)` | Неправильный issue key или URL | Проверь правильность ключа/URL |
| `❌ Активная борда не выбрана` | `config.json` без `active_board` | Запусти `/jira-init` или `/jira-switch-board` |
| `❌ config.json не найден` | Скилл не настроен | `/jira-init` |
| `❌ Переход в статус '...' недоступен` | Workflow не позволяет такую транзицию | Проверь доступные через `jira_search` |
| Юникод-ошибки на Windows | Старая консоль cp1252 | Скрипты сами переключают UTF-8 — обнови Python ≥3.7 |
