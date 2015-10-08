#!/usr/bin/env bash

mkdocs build --clean

python index.py

cat > site/CNAME <<EOF
notes.shichao.io
EOF
