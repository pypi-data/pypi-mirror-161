import logging

import hazwaz
import hazwaz.unittest


class MySubCommand(hazwaz.Command):
    """
    A subcommand.

    This does very little.
    """

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--bar",
            action="store_true",
            help="barfoo things"
        )

    def main(self):
        print("Hello World")


class LoggingSubCommand(hazwaz.Command):
    """
    A subcommand that logs on various levels.
    """

    def main(self):
        logging.debug("This is a DEBUG message")
        logging.info("This is an INFO message")
        logging.warning("This is a WARNING message")


class MyCommand(hazwaz.MainCommand):
    """
    A command that does things.

    This is a command, but honestly it doesn't really do anything.
    """
    commands = (
        MySubCommand(),
        LoggingSubCommand(),
    )

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--foo",
            action="store_true",
            help="foobar things",
        )


class MyCommandWithNoVerbose(hazwaz.MainCommand):
    """
    A command that always talks.

    This command doesn't have the --verbose and --debug arguments.

    """

    def add_arguments(self, parser):
        # we override add_arguments and don't call
        # super().add_arguments(parser) so that --verbose and --debug
        # are missing.
        parser.add_argument(
            "--foo",
            action="store_true",
            help="foobar things",
        )


class testCommand(hazwaz.unittest.HazwazTestCase):
    def test_description(self):
        cmd = MyCommand()
        self.assertEqual(
            cmd.parser.description,
            "A command that does things."
        )
        self.assertEqual(
            cmd.parser.epilog,
            "This is a command, but honestly it doesn't really do anything."
        )

    def test_description_none(self):
        class NoHelpCommand(hazwaz.MainCommand):
            pass

        cmd = NoHelpCommand()
        self.assertEqual(cmd.parser.description, None)

    def test_description_empty(self):
        class NoHelpCommand(hazwaz.MainCommand):
            """
            """

        cmd = NoHelpCommand()
        self.assertEqual(cmd.parser.description, '')

    def test_arguments(self):
        cmd = MyCommand()
        cmd_help = cmd.parser.format_help()
        self.assertIn("--verbose", cmd_help)
        self.assertIn("--foo", cmd_help)

    def test_subparser(self):
        cmd = MyCommand()
        sub_parser = cmd.subparsers.choices["mysubcommand"]
        self.assertEqual(sub_parser.description, "A subcommand.")
        self.assertEqual(
            sub_parser.epilog,
            "This does very little.",
        )

    def test_run(self):
        cmd = MyCommand()
        cmd_help = cmd.parser.format_help()
        stream = self.run_with_argv(cmd, ["mycommand"])
        self.assertEqual(stream["stdout"].getvalue(), cmd_help)

    def test_run_with_option(self):
        cmd = MyCommand()
        cmd_help = cmd.parser.format_help()
        stream = self.run_with_argv(cmd, [
            "mycommand",
            "--verbose",
        ])
        self.assertEqual(stream["stdout"].getvalue(), cmd_help)
        stream = self.run_with_argv(cmd, [
            "mycommand",
            "--debug",
        ])
        self.assertEqual(stream["stdout"].getvalue(), cmd_help)

    def test_run_subcommand(self):
        cmd = MyCommand()
        stream = self.run_with_argv(cmd, ["mycommand", "mysubcommand"])
        self.assertEqual(stream["stdout"].getvalue(), "Hello World\n")

    def test_run_subcommand_with_option(self):
        cmd = MyCommand()
        stream = self.run_with_argv(cmd, [
            "mycommand",
            "mysubcommand",
            "--bar",
        ])
        self.assertEqual(stream["stdout"].getvalue(), "Hello World\n")

    def test_run_no_verbose(self):
        cmd = MyCommandWithNoVerbose()
        cmd_help = cmd.parser.format_help()
        stream = self.run_with_argv(cmd, ["mycommand"])
        self.assertEqual(stream["stdout"].getvalue(), cmd_help)

    def test_logging_regular_coloredlogs(self):
        cmd = MyCommand()
        cmd.coloredlogs = True
        with self.assertLogs():
            stream = self.run_with_argv(cmd, [
                "mycommand",
                "loggingsubcommand",
            ])
        log_lines = stream["stderr"].getvalue().strip().split("\n")
        self.assertEqual(len(log_lines), 1)

    def test_logging_verbose_coloredlogs(self):
        cmd = MyCommand()
        cmd.coloredlogs = True
        with self.assertLogs():
            stream = self.run_with_argv(cmd, [
                "mycommand",
                "--verbose",
                "loggingsubcommand",
            ])
        log_lines = stream["stderr"].getvalue().strip().split("\n")
        self.assertEqual(len(log_lines), 2)

    def test_logging_debug_coloredlogs(self):
        cmd = MyCommand()
        cmd.coloredlogs = True
        with self.assertLogs():
            stream = self.run_with_argv(cmd, [
                "mycommand",
                "--debug",
                "loggingsubcommand",
            ])
        log_lines = stream["stderr"].getvalue().strip().split("\n")
        self.assertEqual(len(log_lines), 3)

    def test_logging_regular_no_coloredlogs(self):
        cmd = MyCommand()
        cmd.coloredlogs = False
        with self.assertLogs():
            stream = self.run_with_argv(cmd, [
                "mycommand",
                "loggingsubcommand",
            ])
        log_lines = stream["stderr"].getvalue().strip().split("\n")
        self.assertEqual(len(log_lines), 1)

    def test_logging_verbose_no_coloredlogs(self):
        cmd = MyCommand()
        cmd.coloredlogs = False
        with self.assertLogs():
            stream = self.run_with_argv(cmd, [
                "mycommand",
                "--verbose",
                "loggingsubcommand",
            ])
        log_lines = stream["stderr"].getvalue().strip().split("\n")
        self.assertEqual(len(log_lines), 2)

    def test_logging_debug_no_coloredlogs(self):
        cmd = MyCommand()
        cmd.coloredlogs = False
        with self.assertLogs():
            stream = self.run_with_argv(cmd, [
                "mycommand",
                "--debug",
                "loggingsubcommand",
            ])
        log_lines = stream["stderr"].getvalue().strip().split("\n")
        self.assertEqual(len(log_lines), 3)


if __name__ == '__main__':
    hazwaz.unittest.main()
