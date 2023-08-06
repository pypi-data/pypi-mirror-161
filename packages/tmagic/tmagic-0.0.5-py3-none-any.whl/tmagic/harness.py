"""
Module providing the test harness infrastructure.
:author: András Aszódi
:date: 2020-11-04
"""

from sys import stderr, version_info
import ast
from code import InteractiveInterpreter
from unittest import TestCase

class Harness(InteractiveInterpreter):
    """
    This class can be configured to run code from an IPython cell
    and check its result.
    """

    def __init__(self):
        """
        Creates a Harness instance.
        Its parent is initialised with the current global variables.
        """
        super().__init__(globals())
        self._tc = TestCase()   # only to use the assertXXX methods
        self._tests = {}
        self._last = None

    def register_test(self, testname: str, expvalue) -> None:
        """
        Registers a test (stores the expected value)
        :param testname: The name of the test
        :param expvalue: The expected value coming from the test
        """
        self._tests[testname] = expvalue

    def test_expr(self, testname, cell):
        """
        This method serves as the back-end of the %%testexpr custom magic
        (see magic.TestMagic).
        It runs the contents of the cell decorated with `%%testexpr`
        and compares the result to an expected value which was registered before.
        :param testname: The name of the test (the parameter of the `%%testexpr` magic).
            This is the key to look up the expected value of the test.
        :param cell: Possibly multi-line string, the contents of the cell
            decorated with `%%testexpr`. It is supposed to contain Python code.
        :return: True if the test passed, False otherwise (including exceptions)
        """
        try:
            self._last = self._exec_script(cell)
            return self._check(testname)
        except Exception as err:
            print(str(err), file=stderr)
            return False

    @property
    def last(self):
        return self._last

    # -- "hidden" --

    def _exec_script(self, script):
        """
        Executes a script and returns the value of the last expression (R-style),
        or None if the last command was not an expression.
        :return: The value of the last expression seen, or None
        """
        # Implementation notes:
        # The basic idea comes from https://stackoverflow.com/a/47130538
        # AA modified the last expression evaluation part
        stmts = list(ast.iter_child_nodes(ast.parse(script)))
        if not stmts:
            return None
        try:
            if isinstance(stmts[-1], ast.Expr):
                # the last one is an expression and we will try to return the results
                # so we first execute the previous statements
                if len(stmts) > 1:
                    # NOTE: the signature of ast.Module.__init__ changed in Python V3.8.
                    # It requires a second argument which apparently should be the empty list.
                    # Could not find any official documentations, only indirect hints,
                    # e.g. https://github.com/ipython/ipython/issues/11590
                    # Workaround:
                    vmajor, vminor = version_info[:2]
                    if vmajor == 3 and vminor <= 7:
                        # old behaviour
                        code = ast.Module(stmts[:-1])
                    else:
                        # V3.8 and above, new signature, note 2nd argument []
                        code = ast.Module(stmts[:-1], [])
                    prevcode = compile(code, filename="<ast>", mode="exec")
                    self.runcode(prevcode)
                # Evaluate the last expression
                lastexpr = compile(ast.Expression(body=stmts[-1].value), filename="<ast>", mode="eval")
                # we don't use `self.runcode` because it always returns None
                # instead, run `eval` but set its "globals" to `self.locals`
                # in which code.InteractiveInterpreter maintains its state
                return eval(lastexpr, self.locals)
            else:
                # otherwise we just execute the entire code
                self.runsource(script)
                return None
        except (KeyboardInterrupt, SystemExit):
            pass    # ignore them silently

    def _check(self, testname):
        """
        Checks self._last against the expected value,
        using the TestCase.assertXXX methods.
        :param testname: The name of the test for looking up the expected value.
        :return: True if the check passed, False if failed.
        """
        # observed and expected values
        obsval = self._last
        expval = self._tests[testname]
        try:
            if expval is None:
                self._tc.assertIsNone(obsval)
            elif isinstance(expval, bool):
                if expval:
                    self._tc.assertTrue(obsval)
                else:
                    self._tc.assertFalse(obsval)
            elif isinstance(expval, dict):
                self._tc.assertDictEqual(expval, obsval)
            elif isinstance(expval, list):
                self._tc.assertListEqual(expval, obsval)
            elif isinstance(expval, tuple):
                self._tc.assertTupleEqual(expval, obsval)
            elif isinstance(expval, set) or isinstance(expval, frozenset):
                self._tc.assertSetEqual(expval, obsval)
            elif isinstance(expval, str):
                self._tc.assertMultiLineEqual(expval, obsval)
            else:
                self._tc.assertEqual(expval, obsval)
            return True
        except AssertionError:
            return False