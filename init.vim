packadd nvim-lspconfig
packadd completion-nvim

lua << EOF
vim.lsp.set_log_level("debug")

require'lspconfig'.fpc.setup{}
EOF

syntax on
