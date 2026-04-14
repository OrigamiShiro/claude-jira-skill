#!/usr/bin/env bash
# Jira CLI Skill — one-line installer for macOS/Linux/WSL/Git Bash.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/<user>/claude-jira-skill/main/bootstrap.sh | bash
#
# Optional: override repo:
#   curl -fsSL .../bootstrap.sh | REPO_URL=https://... bash

set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/<user>/claude-jira-skill}"
BRANCH="${BRANCH:-main}"
DEST="${DEST:-$HOME/.claude/skills/jira}"

echo "Jira CLI Skill — installer"
echo "  repo: $REPO_URL"
echo "  dest: $DEST"
echo ""

if [ -d "$DEST" ]; then
    echo "⚠ Destination already exists: $DEST"
    echo "  Delete it first if you want a clean install:"
    echo "  rm -rf \"$DEST\""
    exit 1
fi

mkdir -p "$(dirname "$DEST")"

if command -v git >/dev/null 2>&1; then
    echo "→ cloning via git"
    git clone --depth 1 -b "$BRANCH" "$REPO_URL" "$DEST"
else
    echo "→ git not found — downloading tarball"
    TMP=$(mktemp -d)
    TARBALL="$REPO_URL/archive/refs/heads/$BRANCH.tar.gz"
    curl -fsSL "$TARBALL" | tar -xz --strip-components=1 -C "$TMP"
    mv "$TMP" "$DEST"
fi

echo ""
python3 "$DEST/install.py" || python "$DEST/install.py"
