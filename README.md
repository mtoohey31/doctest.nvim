# `doctest.nvim`

A Neovim plugin for displaying doctest results when the buffer is entered and on write, using the Neovim virtual text feature. Note that by default, no output is displayed for doctests that succeed. See [Configuration](#Configuration) for information on how to change this behaviour if you prefer more verbose output.

[![demo](https://asciinema.org/a/6dApDMXFD1oAz9cM1UO5wkctm.svg)](https://asciinema.org/a/6dApDMXFD1oAz9cM1UO5wkctm)

## Installation

First, ensure that you have the `python3` provider set up by running `:checkhealth provider` and following the instructions there if things aren't set up. Then, if you're using [vim-plug](https://github.com/junegunn/vim-plug), add the following to the vim-plug section of your `init.vim`:

```vim
call plug#begin()
Plug 'mtoohey31/doctest.nvim', { 'do': ':UpdateRemotePlugins' }
call plug#end()
```

If you're using a different plugin manager, refer to its documentation for the correct syntax. Also, if you don't have them in your `init.vim` already, add:

```vim
filetype plugin on
set nocompatible
```

## Configuration

The first configuration variable is `g:doctest_verbose_string`. When set, tests that succeed will have this string displayed next to them. By default, nothing is displayed if the variable is unset. As an example, if you add the following to your `init.vim`, `# Succeeded` will be displayed next to every successful test.

```vim
let g:doctest_verbose_string = "Succeeded"
```

The second configuration variable is `g:doctest_remove_pycache`. By default, the `__pycache__` directory at the current location is removed when Neovim exits, if you want to disable this behaviour, set the following:

```vim
let g:doctest_remove_pycache = 0
```

The third configuration variable is `g:doctest_traceback_info`. By default, tests that produce errors will display long traceback messages indicating the origin of the error. If you want to disable this behaviour, set the following:

```vim
let g:doctest_traceback_info = 0
```
