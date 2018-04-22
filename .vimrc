let g:syntastic_markdown_mdl_args = ''
autocmd BufWritePre *.md :%s/’/'/ge
autocmd BufWritePre *.md :%s/“/"/ge
autocmd BufWritePre *.md :%s/”/"/ge
