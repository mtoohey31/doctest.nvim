if exists('g:loaded_doctest') || &compatible
  finish
elseif !has('python3')
  echoerr 'doctest.nvim: python3 required, run :checkhealth provider'
  finish
endif

let g:loaded_doctest = 1

autocmd BufEnter * if &filetype == "python" && filereadable(expand('%:p'))|call doctest#run_tests(fnameescape(expand("<afile>:p:h")), fnameescape(expand("<afile>:t:r")))|endif
autocmd BufWritePost * if &filetype == "python"|call doctest#run_tests(fnameescape(expand("<afile>:p:h")), fnameescape(expand("<afile>:t:r")))|endif
autocmd VimLeavePre * if !g:pycache_existed|call delete(g:pycache_path, "rf")|endif

