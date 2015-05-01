#!/usr/bin/env bash

mkdocs build --clean

cat > site/CNAME <<EOF
notes.shichao.io
EOF
