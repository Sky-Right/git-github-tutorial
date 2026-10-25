#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ -n "${PYTHON:-}" ]]; then
  python_bin="$PYTHON"
elif [[ -x .conda/bin/python ]]; then
  python_bin=.conda/bin/python
else
  python_bin=python3
fi
"$python_bin" engine/git_diagrams.py
"$python_bin" engine/build.py content/git-en.md --out dist --name git-en \
  --title "Git & GitHub" --template theme/git.html --html-only --standalone

mkdir -p dist/site
cp dist/git-en.html dist/site/index.html
cp dist/git-en.html dist/site/git-en.html
