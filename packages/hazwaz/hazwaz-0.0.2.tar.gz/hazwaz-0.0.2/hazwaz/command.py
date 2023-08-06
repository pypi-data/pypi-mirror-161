import argparse
import logging
import typing

try:
    import coloredlogs  # type: ignore
except ModuleNotFoundError:
    coloredlogs = None


def _get_first_docstring_line(obj):
    try:
        return obj.__doc__.split('\n')[1].strip()
    except (AttributeError, IndexError):
        return None


def _get_remaining_docstring_lines(obj):
    try:
        return "\n".join(obj.__doc__.split('\n')[2:]).strip()
    except (AttributeError, IndexError):
        return None


class MainCommand:
    '''
    The main class for a command line command.

    Your script will have to subclass this once, instantiate and run its
    :py:meth:`run()` e.g. as::

       class MyCommand(MainCommand):
           """
           A description that will be used in the help.
           """

       if __name__ == "__main__":
           MyCommand().run()
    '''

    commands: typing.Iterable["Command"] = ()
    """
    The subcommands: a tuple of :py:class:`Command` subclasses.
    """
    logformat: str = "%(levelname)s:%(name)s: %(message)s"
    """
    The format passed to logging.Formatter.
    """
    coloredlogs: bool = True
    """
    Whether coloredlogs is used (if available)
    """

    def __init__(self):
        desc = _get_first_docstring_line(self)
        epilog = _get_remaining_docstring_lines(self)
        self.parser = argparse.ArgumentParser(
            description=desc,
            epilog=epilog,
        )
        self.add_arguments(self.parser)
        self.parser.set_defaults(subcommand=self)
        self.subparsers = self.parser.add_subparsers()
        for sub in self.commands:
            sub_help = _get_first_docstring_line(sub)
            sub_epilog = _get_remaining_docstring_lines(sub)
            sub_parser = self.subparsers.add_parser(
                sub.name,
                description=sub_help,
                epilog=sub_epilog,
            )
            sub.add_arguments(sub_parser)
            sub_parser.set_defaults(subcommand=sub)

    def main(self):
        """
        The main function for a command with no subcommands.

        This default implementation that simply prints the help is good
        for most cases when there are subcommands and running the bare
        command doesn't do anything.
        """
        self.parser.print_help()

    def add_arguments(self, parser: argparse.ArgumentParser):
        """
        Add argparse arguments to an existing parser.

        If you need to override this method, you probably want to call
        super().add_arguments(parser) to add the default arguments.
        """
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '--verbose', '-v',
            action='store_true',
            help="Show more details",
        )
        group.add_argument(
            '--debug',
            action='store_true',
            help="Show debug messages",
        )

    def setup_logging(self):
        if getattr(self.args, "debug", False):
            level = logging.DEBUG
        elif getattr(self.args, "verbose", False):
            level = logging.INFO
        else:
            level = logging.WARNING

        if self.coloredlogs and coloredlogs:
            coloredlogs.install(level=level, fmt=self.logformat)
        else:
            logger = logging.getLogger()
            handler = logging.StreamHandler()
            formatter = logging.Formatter(self.logformat)
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(level)

    def run(self):
        """
        Run the command.

        This is the method called to start running the command.
        """
        self.args = self.parser.parse_args()
        self.setup_logging()

        self.args.subcommand.args = self.args
        self.args.subcommand.main()


class Command:
    """
    A subcommand to a MainCommand.

    Every subcommand of your script will be a subclass of this, added to
    the :py:attr:`MainCommand.subcommands`.
    """

    name: typing.Optional[str] = None
    """
    The name used to call this subcommand from the command line.

    If this property is none, the default is the name of the class set
    to lowercase.
    """

    def __init__(self):
        if self.name is None:
            self.name = self.__class__.__name__.lower()

    def add_arguments(self, parser: argparse.ArgumentParser):
        """
        Add argparse arguments to an existing parser.

        Override this method to add arguments to a subcommand.
        """
        pass

    def main(self):
        """
        Main code of this subcommand.

        Override this method to implement the actual program.
        """
        raise NotImplementedError
