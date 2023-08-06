import contextlib
import io
import sys
import typing
import unittest

from .command import Command


class HazwazTestCase(unittest.TestCase):
    def run_with_argv(
            self, cmd, argv: typing.List[str]
    ) -> typing.Dict[str, io.StringIO]:
        """
        Run a command with a list of command line options.

        :param argv: the full command line except for the program name,
                     as a list of strings; e.g. ``["subcommand",
                     "--help"]`` or ``["subcommand", "--option",
                     "value"]``.

        :return: stdout and stderr resulting from the command.
        """
        stream = {
            'stdout': io.StringIO(),
            'stderr': io.StringIO(),
        }
        old_argv = sys.argv
        sys.argv = argv
        with contextlib.redirect_stdout(stream['stdout']):
            with contextlib.redirect_stderr(stream['stderr']):
                cmd.run()
        sys.argv = old_argv
        return stream


class TestCommand(Command):
    """
    Run unittests.
    """
    name = "test"

    def __init__(self, test_cases: typing.Iterable[unittest.TestCase]):
        self.test_cases = test_cases
        super().__init__()

    def main(self):
        suite = unittest.TestSuite()
        for test_case in self.test_cases:
            suite.addTests(
                unittest.TestLoader().loadTestsFromTestCase(test_case)
            )
        unittest.TextTestRunner(verbosity=1).run(suite)


def main():
    unittest.main()
