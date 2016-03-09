#!/usr/bin/env bash
set -e

echo "index.py: building contents pages..."
python index.py

echo "mkdocs build --clean"
mkdocs build --clean

cat > site/CNAME <<EOF
notes.shichao.io
EOF
