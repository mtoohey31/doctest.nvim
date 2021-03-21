if exists('g:loaded_doctest') || &compatible
  finish
endif

let g:loaded_doctest = 1

echo("test")
autocmd TextChanged * :echo "test"
