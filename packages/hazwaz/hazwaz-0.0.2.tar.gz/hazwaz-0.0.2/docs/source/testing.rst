*********
 Testing
*********

Hazwaz provides the module :py:mod:`hazwaz.unittest` with helpers based
on :py:mod:`unittest` to write unit tests for command line behaviour.

The class :py:class:`hazwaz.unittest.HazwazTestCase` can be used instead
of :py:class:`unittest.TestCase` and works just as its parent: methods
whose name start with ``test`` are run as individual tests, and you can
use all the usual `unittest assert methods
<https://docs.python.org/3/library/unittest.html#assert-methods>`_.

To write a test that runs the command as if from the command line, with
certain parameters, you can use the method
:py:meth:`hazwaz.unittest.HazwazTestCase.run_with_argv` as in the
following example::

   import hazwaz.unittest

   import greeter


   class testGreeter(hazwaz.unittest.HazwazTestCase):
       def test_greet_world(self):
           cmd = greeter.Greet()
           stream = self.run_with_argv(cmd, [
               "./greeter.py",
               "world",
           ])

           self.assertEqual(
               stream["stdout"].getvalue(),
               "Hello world!\n"
           )



The first parameter should be the name of the command itself, as if this
was the full command line.

If the tests are in their own module, there is a convienence function
:py:func:`hazwaz.unittest.main` that runs :py:func:`unittest.main`,
to be used e.g.::

   if __name__ == "__main__":
       hazwaz.unittest.main()

However, if you're writing a self-contained script you can use the
command :py:class:`hazwaz.unittest.TestCommand` to add a subcommand called
``test`` which runs all tests from a list of :py:class:`unittest.TestCase`::

   class Greet(hazwaz.MainCommand):
       """
       Greet people in different ways.
       """
       commands = (
           World(),
           Individual(),
           hazwaz.unittest.TestCommand([TestGreeter]),
       )
