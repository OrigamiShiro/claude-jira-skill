# Examples

Шаблоны конфигов для скилла.

## Файлы

- `board.example.json` — структура `boards/<name>.json` (публичная инфа)
- `creds.example.json` — структура `creds/<name>.json` (секреты, в `.gitignore`)
- `config.example.json` — структура `config.json` (активный профиль)
- `batch.example.json` — пример входа для `jira_batch.py`

## Использование

Эти файлы — ТОЛЬКО шаблоны. Реальные конфиги создаются автоматически через `jira_init.py`. Не нужно их копировать вручную.

Для batch:
```bash
cp examples/batch.example.json /tmp/my-ops.json
# отредактируй
python scripts/jira_batch.py --file /tmp/my-ops.json
```
