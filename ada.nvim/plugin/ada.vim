" Ada.nvim plugin registration
" Prevents loading if already loaded
if exists('g:loaded_ada_nvim')
  finish
endif
let g:loaded_ada_nvim = 1

" Note: Plugin is loaded via lua/ada/init.lua
" User should call require('ada').setup() in their init.lua
