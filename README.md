# Jira CLI Skill for Claude Code

Управление Jira из Claude Code через слеш-команды и CLI-скрипты.

- **10 скриптов** с разделением ответственности (create, update, delete, link, worklog, sprint, search, batch, init, config, ping)
- **7 slash-команд** для Claude: `/jira-init`, `/jira-help`, `/jira-switch-board`, `/jira-show`, и др.
- **Поддержка нескольких бордов** — профили + переключение
- **93 unit-теста**, минимум зависимостей (только `requests`)
- Работает на Windows, macOS, Linux

---

## Установка (3 команды)

### 1. Клонировать в стандартный путь скиллов

```bash
git clone <repo-url> ~/.claude/skills/jira
```

> На Windows PowerShell `~` раскрывается в `$env:USERPROFILE`. Если не работает — используй полный путь: `git clone <repo-url> "$env:USERPROFILE\.claude\skills\jira"`.

### 2. Установить скилл (зависимости + slash-команды)

```bash
python ~/.claude/skills/jira/install.py
```

Скрипт:
- Установит `requests` через pip
- Скопирует slash-команды в `~/.claude/commands/`

### 3. Инициализировать борду

Перезапусти Claude Code, потом набери:

```
/jira-init
```

Агент запросит credentials (email, API token, project key, board ID). Токен создаётся здесь:
https://id.atlassian.com/manage-profile/security/api-tokens

---

## Использование

### Slash-команды в Claude

| Команда | Назначение |
|---------|-----------|
| `/jira-init` | Первичная настройка новой борды |
| `/jira-add-board` | Добавить ещё одну борду |
| `/jira-switch-board` | Переключить активную борду |
| `/jira-show [name]` | Список бордов / детали профиля |
| `/jira-remove-board <name>` | Удалить профиль |
| `/jira-ping` | Проверить подключение |
| `/jira-help` | Список всех команд и скриптов |

### CLI-скрипты (прямой вызов из терминала)

```bash
# Создать задачу (assignee = я по умолчанию)
python ~/.claude/skills/jira/scripts/jira_create.py "New feature" -t История

# Закрыть
python ~/.claude/skills/jira/scripts/jira_update.py transition HOR-1 "Готово"

# Залогировать время
python ~/.claude/skills/jira/scripts/jira_worklog.py add HOR-1 "2h 30m" --comment "done"

# Удалить
python ~/.claude/skills/jira/scripts/jira_delete.py HOR-999

# JQL-поиск
python ~/.claude/skills/jira/scripts/jira_search.py "assignee=currentUser() AND status='В работе'"

# Массовые операции (stdin)
echo '[{"op":"transition","key":"HOR-1","status":"Готово"}]' | python ~/.claude/skills/jira/scripts/jira_batch.py
```

Подробности и все аргументы: `/jira-help` в Claude Code или `python ~/.claude/skills/jira/scripts/jira_help.py`.

---

## Несколько проектов

Каждая борда — отдельный профиль:

```bash
/jira-add-board          # добавить рабочую
/jira-switch-board       # переключиться на личную
/jira-show               # список всех
```

Профили изолированы — свой URL, project, board, email, token.

Конфиг хранится:
- **Global:** `~/.claude/skills/jira/config.json` (по умолчанию)
- **Local:** `./.claude/skills/jira/config.json` (в проекте, имеет приоритет)

---

## Структура репы

```
jira/
├── SKILL.md                  # для Claude Code
├── README.md                 # для людей (этот файл)
├── LICENSE                   # MIT
├── requirements.txt          # requests
├── install.py                # установщик (install_commands + pip)
├── install_commands.py       # только slash-команды (если нужно)
│
├── scripts/                  # CLI-скрипты
│   ├── jira_init.py
│   ├── jira_config.py
│   ├── jira_ping.py
│   ├── jira_create.py
│   ├── jira_update.py
│   ├── jira_delete.py
│   ├── jira_link.py
│   ├── jira_search.py
│   ├── jira_worklog.py
│   ├── jira_sprint.py
│   ├── jira_batch.py
│   ├── jira_help.py
│   └── lib/                  # общий код (config, auth, client)
│
├── commands-templates/       # шаблоны slash-команд
│   └── jira-*.md
│
├── examples/                 # шаблоны конфигов
└── boards/, creds/           # пустые (заполняются при init)
```

**В `.gitignore`:** `creds/*.json`, `boards/*.json`, `config.json` — секреты не уходят в git.

---

## Тесты

```bash
cd ~/.claude/skills/jira/scripts
python -m unittest discover -s lib/tests
python -m unittest discover -s tests
```

93 теста, все без сетевых вызовов (mock requests).

---

## Безопасность

- Токены и credentials хранятся в `creds/<name>.json` — **не** в git
- В `.gitignore` явно исключены `creds/`, `boards/*.json`, `config.json`
- Токены маскируются в выводе: `ATAT...77CB`
- Каждый пользователь делает свой `/jira-init` со своими credentials

---

## Troubleshooting

| Симптом | Причина | Решение |
|---------|---------|---------|
| `❌ Unauthorized (401)` | Неверный/истёкший токен | Перегенерируй на https://id.atlassian.com/manage-profile/security/api-tokens |
| `❌ Resource not found (404)` | Неправильный ключ/URL | Проверь: `/jira-show` |
| `❌ Активная борда не выбрана` | Нет active_board в config | `/jira-init` или `/jira-switch-board` |
| `❌ config.json не найден` | Скилл не настроен | `/jira-init` |
| Юникод-ошибки на Windows | Старая консоль | Нужен Python 3.9+ — скрипты сами переключают UTF-8 |

---

## Обновление

```bash
cd ~/.claude/skills/jira
git pull
python install.py    # обновит команды если появились новые
```

## Удаление

```bash
# Скилл
rm -rf ~/.claude/skills/jira

# Slash-команды
rm ~/.claude/commands/jira-*.md
```

---

## License

MIT — см. [LICENSE](LICENSE).
