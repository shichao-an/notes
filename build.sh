#!/usr/bin/env bash

mkdocs build "$@"

cat > site/CNAME <<EOF
notes.shichao.io
EOF
