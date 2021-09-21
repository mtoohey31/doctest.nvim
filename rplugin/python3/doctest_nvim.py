import pynvim
import doctest
import importlib.util
import re
import os
import sys
from typing import Optional


@pynvim.plugin
class DoctestPlugin:
    nvim: pynvim.Nvim
    runner: doctest.DocTestRunner
    disabled: bool

    def __init__(self, nvim):
        self.nvim = nvim
        self.disabled = False

        # Create the VirtualTextRunner class
        class VirtualTextRunner(doctest.DocTestRunner):
            nvim: pynvim.Nvim
            namespace_id: int
            filepath: str
            traceback_info: bool
            verbose_string: Optional[str] = None

            def __init__(self, nvim: pynvim.Nvim, namespace_id: int,
                         filepath: str, traceback_info: bool,
                         verbose_string: str = None) -> None:
                # Call the DocTestRunner init method
                super().__init__()
                self.nvim = nvim
                self.namespace_id = namespace_id
                self.filepath = filepath
                self.traceback_info = traceback_info
                self.verbose_string = verbose_string

            def report_success(self, out, test, example, got) -> None:
                """Report that the given example ran successfully.
                (Only displays a message if verbose_string is not None)
                """
                # Check if the verbose string is defined and display the
                # relevant virtualtext if so
                if self.verbose_string is not None:
                    self.nvim.api.buf_set_virtual_text(
                        0, self.namespace_id, example.lineno + test.lineno + 1,
                        [["# " + self.verbose_string, "Comment"]], {})

            def report_failure(self, out, test, example, got) -> None:
                """Report that the given example failed by displaying the error
                as virtualtext."""
                raw_diff = self._checker.output_difference(
                    example, got, doctest.REPORT_UDIFF)

                # Parse the output to find the line containing `Got:` and
                # display the relevant virtualtext
                got_found = False
                got_line = 0
                for line in raw_diff.rstrip('\n').split('\n'):
                    if got_found:
                        self.nvim.api.buf_set_virtual_text(
                            0, self.namespace_id, example.lineno + test.lineno +
                            1 + got_line, [["# " + line.strip(), "Error"]], {})
                        got_line += 1
                    elif line == 'Got:':
                        got_found = True

            def report_unexpected_exception(self, out, test, example,
                                            exc_info) -> None:
                """Report that the given example raised an unexpected exception
                by displaying the exception as virtualtext."""
                # Get the exception traceback
                traceback = doctest._exception_traceback(exc_info)
                traceback_string = '# ' + traceback.split('\n')[-2].strip()
                # Check whether detailed traceback info is enabled
                if self.traceback_info:
                    for line in [line.strip() for line
                                 in reversed(traceback.split('\n')[:-2])]:
                        # Handle lines differently based on whether they're
                        # showing the code that created the error, or the
                        # place where that code was found
                        if line[0:4] == 'File':
                            path = re.sub(r'(^[^"]*")|("[^"]*$)', '', line)
                            # Depending on whether the error was a result off
                            # code in the current file or another, display the
                            # file path or the line number
                            if path == self.filepath:
                                lineno = re.sub(
                                    r'(^.*line (?=\d))|((?<=\d), in .*$)', '',
                                    line)
                                traceback_string += f' on line {lineno}'
                                pass
                            else:
                                # Show the relative path to the file instead of
                                # the absolute path to save space
                                relpath = os.path.relpath(path)
                                traceback_string += f' in {relpath}'
                        else:
                            traceback_string += f'; by `{line}`'
                # Display the virtualtext
                self.nvim.api.buf_set_virtual_text(0, self.namespace_id,
                                                   example.lineno + test.lineno
                                                   + 1, [[traceback_string,
                                                          "Error"]], {})

        self.runner = VirtualTextRunner

    @pynvim.autocmd('BufEnter,BufWritePost', pattern='*.py',
                    eval='fnameescape(expand("<afile>:p"))')
    def run_tests(self, filepath) -> None:
        # Check if the plugin is set to disabled, meaning it is quitting
        if self.disabled:
            return None

        # Attempt to run tests
        try:
            # Import the current file
            sys.path.append(os.path.dirname(filepath))
            lib = importlib.import_module(
                re.sub(r'\.[^.]*$', '', os.path.basename(filepath)))
            importlib.reload(lib)

            finder = doctest.DocTestFinder()
            tests_to_run = finder.find(lib)

            # Check if the doctest namespace is defined, if not, create it
            namespaces = self.nvim.api.get_namespaces()
            if 'doctest' in namespaces:
                namespace_id = namespaces['doctest']
                # If the namespace already existed, clear it
                self.nvim.api.buf_clear_namespace(0, namespace_id, 0, -1)
            else:
                namespace_id = self.nvim.api.create_namespace('doctest')

            # Attempt to fetch the verbose string variable, set it to True
            # otherwise
            traceback_info = True
            try:
                traceback_info = bool(self.nvim.api.get_var(
                    'doctest_traceback_info'))
            except:
                pass

            # Attempt to fetch the verbose string variable, leave it blank
            # otherwise
            verbose_string = None
            try:
                verbose_string = self.nvim.api.get_var(
                    'doctest_verbose_string')
            except:
                pass

            # Run each test
            for test in tests_to_run:
                runner = self.runner(self.nvim, namespace_id, filepath,
                                     traceback_info, verbose_string)
                runner.run(test)

        # Except errors finding the module (which would occur when the file has
        # not yet been written, or when the file contains unsupported
        # characters) and inform the user only if the file already exits
        except ModuleNotFoundError:
            if os.path.isfile(filepath):
                self.nvim.api.command('echohl ErrorMsg | echo "doctest.nvim: '
                                      'Error importing file, path may contain '
                                      'unsupported characters" | echohl None')
        # Except syntax errors (which would originate from the imported file)
        # and inform the user of the error
        except SyntaxError:
            self.nvim.api.command('echohl ErrorMsg | echo "doctest.nvim: '
                                  'SyntaxError in file" | echohl None')
        # Except all other errors and inform the user of the kind of error that
        # occurred
        except Exception as e:
            self.nvim.api.command('echohl ErrorMsg | echo "doctest.nvim: '
                                  f'Encountered {type(e).__name__} while '
                                  'attempting to run tests" | echohl None')

    @pynvim.autocmd('QuitPre', sync=True)
    def disable(self) -> None:
        # Set the plugin to be disabled
        self.disabled = True

    @pynvim.autocmd('VimLeavePre', sync=True)
    def remove_pycache(self) -> None:
        # Set pycache removal to true by default
        remove_pycache = True

        # Check if the variable to disable pycache has been set
        try:
            if self.nvim.api.get_var('doctest_remove_pycache') == 0:
                remove_pycache = False
        except:
            pass

        # Remove the pycache directory, which will always be located in the
        # current directory, so no path parsing is necessary
        if remove_pycache:
            import os
            os.system("rm -r __pycache__")
