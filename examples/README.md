# Examples

Config templates for the skill.

## Files

- `board.example.json` — structure of `boards/<name>.json` (public info)
- `creds.example.json` — structure of `creds/<name>.json` (secrets, in `.gitignore`)
- `config.example.json` — structure of `config.json` (active profile)
- `batch.example.json` — sample input for `jira_batch.py`

## Usage

These are templates **only**. Real configs are created automatically via `jira_init.py`. No need to copy them manually.

For batch operations:

```bash
cp examples/batch.example.json /tmp/my-ops.json
# edit the file
python scripts/jira_batch.py --file /tmp/my-ops.json
```
