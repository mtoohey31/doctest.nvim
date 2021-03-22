# `doctest.nvim`

A Neovim plugin for displaying doctest results when the buffer is entered and on write, using the Neovim virtual text feature. Note that by default, no output is displayed for doctests that succeed. See [Configuration](#Configuration) for information on how to change this behaviour if you prefer more verbose output.

## Installation

If you're using [vim-plug](https://github.com/junegunn/vim-plug), add the following to the vim-plug section of your `init.vim`:

```vim
call plug#begin()

Plug 'mtoohey31/doctest.nvim'

call plug#end()
```

If you're using a different plugin manager, refer to its documentation for the correct syntax. Also, if you don't have them in your `init.vim` already, add:

```vim
filetype plugin on
set nocompatible
```

Finally, ensure that you have the `python3` provider set up by running `:checkhealth provider`.

## Configuration

As of now, the only configuration variable is `g:doctest_verbose_string`. When this variable is unset, no output will be displayed for doctests that succeed. When it is set, the output next to the succeeding doctest will be the string representation of whatever the variable is set to. To set it, use the following syntax:

```vim
let g:doctest_verbose_string = "Succeeded"
```
