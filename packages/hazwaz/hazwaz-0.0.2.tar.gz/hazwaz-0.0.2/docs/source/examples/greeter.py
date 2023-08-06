#!/usr/bin/env python3
import hazwaz
import hazwaz.unittest


class World(hazwaz.Command):
    """
    Greet the whole world.
    """

    def main(self):
        print("Hello world!")


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


class TestGreeter(hazwaz.unittest.HazwazTestCase):
    def test_greet_world(self):
        cmd = Greet()
        stream = self.run_with_argv(cmd, [
            "./greeter.py",
            "world",
        ])

        self.assertEqual(stream["stdout"].getvalue(), "Hello world!\n")

    def test_greet_individual(self):
        cmd = Greet()
        stream = self.run_with_argv(cmd, [
            "./greeter.py",
            "individual",
            "Bob",
        ])

        self.assertEqual(stream["stdout"].getvalue(), "Hello Bob\n")


class Greet(hazwaz.MainCommand):
    """
    Greet people in different ways.
    """
    commands = (
        World(),
        Individual(),
        hazwaz.unittest.TestCommand([TestGreeter]),
    )


if __name__ == "__main__":
    Greet().run()
