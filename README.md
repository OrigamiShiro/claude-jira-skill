# Jira CLI Skill for Claude Code

[🇬🇧 English](#english) · [🇷🇺 Русский](#russian)

Manage Jira from Claude Code via slash commands and CLI scripts.

- **11 scripts** with single-responsibility design (create, update, delete, link, worklog, sprint, search, batch, init, config, ping)
- **7 slash commands** for Claude: `/jira-init`, `/jira-help`, `/jira-switch-board`, `/jira-show`, etc.
- **Multi-board support** — profiles + switching
- **93 unit tests**, minimal dependencies (only `requests`)
- Works on Windows, macOS, Linux

---

<a id="english"></a>
## 🇬🇧 English

### Quick install (one command)

**macOS / Linux / WSL / Git Bash:**

```bash
curl -fsSL https://raw.githubusercontent.com/OrigamiShiro/claude-jira-skill/main/bootstrap.sh | bash
```

**Windows (PowerShell, Win10+):**

```powershell
iwr -useb https://raw.githubusercontent.com/OrigamiShiro/claude-jira-skill/main/bootstrap.ps1 | iex
```

The bootstrap script downloads the repo into `~/.claude/skills/jira`, installs the `requests` dependency, and copies slash commands into `~/.claude/commands/`.

Then restart Claude Code and run `/jira-init` to set up your first board.

### Manual install (3 commands)

If you prefer control over each step:

#### 1. Clone into the standard skills path

```bash
git clone https://github.com/OrigamiShiro/claude-jira-skill ~/.claude/skills/jira
```

> On Windows PowerShell `~` expands to `$env:USERPROFILE`. If it doesn't work — use the full path: `git clone <repo-url> "$env:USERPROFILE\.claude\skills\jira"`.

#### 2. Run the installer (deps + slash commands)

```bash
python ~/.claude/skills/jira/install.py
```

The script will:
- Install `requests` via pip
- Copy slash commands into `~/.claude/commands/`

#### 3. Initialize a board

Restart Claude Code, then type:

```
/jira-init
```

The agent will prompt for credentials (email, API token, project key, board ID). Get your token here:
https://id.atlassian.com/manage-profile/security/api-tokens

### Usage

#### Slash commands in Claude

| Command | Purpose |
|---------|---------|
| `/jira-init` | Initial setup of a new board |
| `/jira-add-board` | Add another board |
| `/jira-switch-board` | Switch active board |
| `/jira-show [name]` | List boards / show profile details |
| `/jira-remove-board <name>` | Delete profile |
| `/jira-ping` | Check connection |
| `/jira-help` | List all commands and scripts |

#### CLI scripts (direct terminal invocation)

```bash
# Create an issue (assignee = current user by default)
python ~/.claude/skills/jira/scripts/jira_create.py "New feature" -t Story

# Transition
python ~/.claude/skills/jira/scripts/jira_update.py transition PROJ-1 "Done"

# Log time
python ~/.claude/skills/jira/scripts/jira_worklog.py add PROJ-1 "2h 30m" --comment "done"

# Delete
python ~/.claude/skills/jira/scripts/jira_delete.py PROJ-999

# JQL search
python ~/.claude/skills/jira/scripts/jira_search.py "assignee=currentUser() AND status='In Progress'"

# Batch (stdin)
echo '[{"op":"transition","key":"PROJ-1","status":"Done"}]' | python ~/.claude/skills/jira/scripts/jira_batch.py
```

Full arg reference: `/jira-help` in Claude or `python ~/.claude/skills/jira/scripts/jira_help.py`.

### Multi-project setup

Each board is a separate profile:

```bash
/jira-add-board          # add a second/third board
/jira-switch-board       # switch active
/jira-show               # list all
```

Profiles are isolated — each has its own URL, project, board, email, token.

Config is stored at:
- **Global:** `~/.claude/skills/jira/config.json` (default)
- **Local:** `./.claude/skills/jira/config.json` (project-scoped, takes precedence)

### Tests

```bash
cd ~/.claude/skills/jira/scripts
python -m unittest discover -s lib/tests
python -m unittest discover -s tests
```

93 tests, all without network calls (mock requests).

### Security

- Tokens and credentials live in `creds/<name>.json` — **never** in git
- `.gitignore` explicitly excludes `creds/`, `boards/*.json`, `config.json`
- Tokens are masked in output: `ATAT...77CB`
- Each user runs their own `/jira-init` with their own credentials

### Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `❌ Unauthorized (401)` | Invalid/expired token | Regenerate at https://id.atlassian.com/manage-profile/security/api-tokens |
| `❌ Resource not found (404)` | Wrong key/URL | Check with `/jira-show` |
| `❌ No active board selected` | No active_board in config | `/jira-init` or `/jira-switch-board` |
| `❌ config.json not found` | Skill not configured | `/jira-init` |
| Unicode errors on Windows | Old console | Requires Python 3.9+ — scripts auto-switch to UTF-8 |

### Update

```bash
cd ~/.claude/skills/jira
git pull
python install.py    # updates slash commands if new ones appeared
```

### Uninstall

```bash
# Skill
rm -rf ~/.claude/skills/jira

# Slash commands
rm ~/.claude/commands/jira-*.md
```

### License

MIT — see [LICENSE](LICENSE).

---

<a id="russian"></a>
## 🇷🇺 Русский

Управление Jira из Claude Code через слеш-команды и CLI-скрипты.

### Быстрая установка (одна команда)

**macOS / Linux / WSL / Git Bash:**

```bash
curl -fsSL https://raw.githubusercontent.com/OrigamiShiro/claude-jira-skill/main/bootstrap.sh | bash
```

**Windows (PowerShell, Win10+):**

```powershell
iwr -useb https://raw.githubusercontent.com/OrigamiShiro/claude-jira-skill/main/bootstrap.ps1 | iex
```

Bootstrap-скрипт скачает репу в `~/.claude/skills/jira`, установит зависимость `requests` и скопирует slash-команды в `~/.claude/commands/`.

После этого перезапусти Claude Code и выполни `/jira-init` для настройки первой борды.

### Ручная установка (3 команды)

Если хочешь контроль над каждым шагом:

#### 1. Клонировать в стандартный путь скиллов

```bash
git clone https://github.com/OrigamiShiro/claude-jira-skill ~/.claude/skills/jira
```

> На Windows PowerShell `~` раскрывается в `$env:USERPROFILE`. Если не работает — используй полный путь: `git clone <repo-url> "$env:USERPROFILE\.claude\skills\jira"`.

#### 2. Запустить установщик (зависимости + slash-команды)

```bash
python ~/.claude/skills/jira/install.py
```

Скрипт:
- Установит `requests` через pip
- Скопирует slash-команды в `~/.claude/commands/`

#### 3. Инициализировать борду

Перезапусти Claude Code, потом набери:

```
/jira-init
```

Агент запросит credentials (email, API token, project key, board ID). Токен создаётся здесь:
https://id.atlassian.com/manage-profile/security/api-tokens

### Использование

#### Slash-команды в Claude

| Команда | Назначение |
|---------|-----------|
| `/jira-init` | Первичная настройка новой борды |
| `/jira-add-board` | Добавить ещё одну борду |
| `/jira-switch-board` | Переключить активную борду |
| `/jira-show [name]` | Список бордов / детали профиля |
| `/jira-remove-board <name>` | Удалить профиль |
| `/jira-ping` | Проверить подключение |
| `/jira-help` | Список всех команд и скриптов |

#### CLI-скрипты (прямой вызов из терминала)

```bash
# Создать задачу (assignee = я по умолчанию)
python ~/.claude/skills/jira/scripts/jira_create.py "New feature" -t Story

# Закрыть
python ~/.claude/skills/jira/scripts/jira_update.py transition PROJ-1 "Done"

# Залогировать время
python ~/.claude/skills/jira/scripts/jira_worklog.py add PROJ-1 "2h 30m" --comment "done"

# Удалить
python ~/.claude/skills/jira/scripts/jira_delete.py PROJ-999

# JQL-поиск
python ~/.claude/skills/jira/scripts/jira_search.py "assignee=currentUser() AND status='In Progress'"

# Массовые операции (stdin)
echo '[{"op":"transition","key":"PROJ-1","status":"Done"}]' | python ~/.claude/skills/jira/scripts/jira_batch.py
```

Подробности и все аргументы: `/jira-help` в Claude Code или `python ~/.claude/skills/jira/scripts/jira_help.py`.

### Несколько проектов

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

### Тесты

```bash
cd ~/.claude/skills/jira/scripts
python -m unittest discover -s lib/tests   # 44 теста
python -m unittest discover -s tests       # 49 тестов
```

Всего 93 unit-теста, без сетевых вызовов (mock requests).

### Безопасность

- Токены и credentials хранятся в `creds/<name>.json` — **не** в git
- В `.gitignore` явно исключены `creds/`, `boards/*.json`, `config.json`
- Токены маскируются в выводе: `ATAT...77CB`
- Каждый пользователь делает свой `/jira-init` со своими credentials

### Troubleshooting

| Симптом | Причина | Решение |
|---------|---------|---------|
| `❌ Unauthorized (401)` | Неверный/истёкший токен | Перегенерируй на https://id.atlassian.com/manage-profile/security/api-tokens |
| `❌ Resource not found (404)` | Неправильный ключ/URL | Проверь: `/jira-show` |
| `❌ No active board selected` | Нет active_board в config | `/jira-init` или `/jira-switch-board` |
| `❌ config.json not found` | Скилл не настроен | `/jira-init` |
| Юникод-ошибки на Windows | Старая консоль | Нужен Python 3.9+ — скрипты сами переключают UTF-8 |

### Обновление

```bash
cd ~/.claude/skills/jira
git pull
python install.py    # обновит команды если появились новые
```

### Удаление

```bash
# Скилл
rm -rf ~/.claude/skills/jira

# Slash-команды
rm ~/.claude/commands/jira-*.md
```

### Лицензия

MIT — см. [LICENSE](LICENSE).

---

## Structure

```
jira/
├── SKILL.md                  # for Claude Code
├── README.md                 # for humans (this file)
├── LICENSE                   # MIT
├── requirements.txt          # requests
├── install.py                # installer (install_commands + pip)
├── install_commands.py       # slash commands only (if needed)
│
├── scripts/                  # CLI scripts
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
│   └── lib/                  # shared code (config, auth, client)
│
├── commands-templates/       # slash command templates
│   └── jira-*.md
│
├── examples/                 # config templates
└── boards/, creds/           # empty (populated on init)
```
