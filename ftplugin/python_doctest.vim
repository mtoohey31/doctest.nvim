if exists('g:loaded_doctest') || &compatible
  finish
elseif !has('python3')
  echohl ErrorMsg
  echo 'doctest.nvim: python3 required'
  echohl None
  finish
endif

let g:loaded_doctest = 1

autocmd BufEnter * if &filetype == "python"|call doctest#run_tests(expand("<afile>:p:h"), expand("<afile>:t:r"))|endif
autocmd BufWritePost * if &filetype == "python"|call doctest#run_tests(expand("<afile>:p:h"), expand("<afile>:t:r"))|endif
