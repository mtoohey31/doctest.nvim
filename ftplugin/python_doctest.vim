if exists('g:loaded_doctest') || &compatible
  finish
elseif !has('python3')
  echohl ErrorMsg
  echo 'doctest.nvim: python3 required'
  echohl None
  finish
endif

let g:loaded_doctest = 1

autocmd BufEnter * call doctest#run_tests(expand("<afile>:p:h"), expand("<afile>:t:r"))
autocmd BufWritePost * call doctest#run_tests(expand("<afile>:p:h"), expand("<afile>:t:r"))
