function! doctest#run_tests(folderpath, filename) abort
  let g:current_doctest_folder = a:folderpath
  let g:current_doctest_name = a:filename

  let ns_id = nvim_create_namespace("doctest")
  call nvim_buf_clear_namespace(0, ns_id, 0, -1)
  let g:current_doctest_ns_id = ns_id

  let g:pycache_path = a:folderpath . "/__pycache__/"
  let g:pycache_existed = isdirectory(g:pycache_path)

  python3 << endpython
import doctest
import pynvim
import importlib.util
import sys
import contextlib
import os

name = vim.api.get_var("current_doctest_name")
folder = vim.api.get_var("current_doctest_folder")
ns_id = vim.api.get_var("current_doctest_ns_id")

verbose_string = ""
try:
    verbose_string = str(vim.api.get_var("doctest_verbose_string"))
except:
    pass


class CustomRunner(doctest.DocTestRunner):
    """A special doctest.DocTestRunner to display test results as virtual text."""

    def report_success(self, out, test, example, got) -> None:
        """Report that the given example ran successfully.
        (Only displays a message if verbose_string != "")
        """
        if verbose_string != "":
            vim.api.buf_set_virtual_text(
                0, ns_id, example.lineno + test.lineno + 1, [["# " + verbose_string, "Comment"]], {})

    def report_failure(self, out, test, example, got) -> None:
        """Report that the given example failed."""
        raw_diff = self._checker.output_difference(
            example, got, doctest.REPORT_UDIFF)

        got_found = False
        got_line = 0
        for line in raw_diff.rstrip('\n').split('\n'):
            if got_found:
                vim.api.buf_set_virtual_text(
                    0, ns_id, example.lineno + test.lineno + 1 + got_line, [["# " + line.strip(), "Error"]], {})
                got_line += 1
            elif line == 'Got:':
                got_found = True

    def report_unexpected_exception(self, out, test, example, exc_info) -> None:
        """Report that the given example raised an unexpected exception."""
        traceback = doctest._exception_traceback(exc_info)
        vim.api.buf_set_virtual_text(0, ns_id, example.lineno + test.lineno + 1, [
                                     ["# " + traceback.split('\n')[-2].strip(), "Error"]], {})


if '.' not in name:
    with contextlib.redirect_stderr(open(os.devnull, 'w')):
        with contextlib.redirect_stdout(open(os.devnull, 'w')):
            sys.path.append(folder)
            imported = False
            try:
                lib = importlib.import_module(name)
                importlib.reload(lib)
                imported = True

                finder = doctest.DocTestFinder()

                tests_to_run = finder.find(lib)

                for test in tests_to_run:
                    runner = CustomRunner()
                    runner.run(test)
            except:
                if not imported:
                    vim.api.command('echoerr "doctest.nvim: import failed likely due to unwritten file or syntax error"')
                else:
                    vim.api.command('echoerr "doctest.nvim: unexpected error"')
else:
    vim.api.command('echoerr "doctest.nvim: filename contains period"')
endpython
endfunction
