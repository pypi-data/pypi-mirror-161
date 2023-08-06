**********
 Tutorial
**********

In this tutorial, we'll write a command that greets people in different
ways.

We start with the scaffolding (shebang, imports, …) and with a class
that subclasses :py:class:`MainCommand <hazwaz.command.MainCommand>`, is
instantiated and its method :py:meth:`run
<hazwaz.command.MainCommand.run>` is called::


   #!/usr/bin/env python3
   import hazwaz


   class Greet(hazwaz.MainCommand):
       """
       Greet people in different ways.
       """


   if __name__ == "__main__":
       Greet().run()

Save this in a file called greeter.py and run it, and it will print an
help message where you can already see a couple of options,
``--verbose`` and ``debug``, as well as the first line of the docstring
used as the usage.

Now we add our first subcommand: we write a new class, subclassing
:py:class:`Command <hazwaz.command.Command>` and writing some code in
its :py:meth:`main <hazwaz.command.Command.main>` method::

   class World(hazwaz.Command):
       """
       Greet the whole world.
       """

       def main(self):
           print("Hello world!")

And we add an instance to the tuple of subcommands in our MainCommand::

   class Greet(hazwaz.MainCommand):
       """
       Greet people in different ways.
       """
       commands = (
           World(),
       )

now if we run the program as ``./greeter.py`` we see that there is a
possible choice for a positional argument, ``world``, and if we run
``./greeter.py world`` we get, as expected, a greeting ``Hello world!``.

With ``./greeter.py world --help`` we can see the help message for this
subcommand, and notice that the first line in the docstring has again
been used as the usage notes.

Of course, a subcommand can also have options: we write a second
subclass of :py:class:`Command <hazwaz.command.Command>` and this time
we add some argparser option in the :py:meth:`add_arguments
<hazwaz.command.Command.add_arguments>` method::

   class Individual(hazwaz.Command):
       """
       Greet an individual.
       """

       def add_arguments(self, parser):
           parser.add_argument(
               "gretee",
               help="The person to be greeted",
           )

       def main(self):
           print("Hello {}".format(self.args.gretee))

And again we add it to the tuple of subcommands::

   class Greet(hazwaz.MainCommand):
       """
       Greet people in different ways.
       """
       commands = (
           World(),
           Individual(),
       )

You can then run the program as ``./greeter.py individual Bob`` to see
the new greeting.

:py:meth:`add_arguments <hazwaz.command.Command.add_arguments>` requires
an :py:class:`argparse.ArgumentParser` as its second parameter, and
uses it to add arbitrary arguments, giving access to all argparse
features.
