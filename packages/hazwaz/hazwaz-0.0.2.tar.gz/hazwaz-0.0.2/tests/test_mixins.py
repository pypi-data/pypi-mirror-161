import tempfile
import unittest

import hazwaz
import hazwaz.unittest


class testEditorMixin(unittest.TestCase):
    def test_open_with_cat_existing_file(self):
        subcmd = hazwaz.mixins.ExternalEditorMixin()
        subcmd.editors = [("cat", "cat")]
        # TODO: suppress this output in the tests (we can't use
        # contextlib.redirect_stdout because that doesn't redirect the
        # stdout used by subprocess.
        res = subcmd.edit_file_in_external_editor("/bin/fgrep")
        self.assertTrue(res)

    def test_open_with_cat_missing_file(self):
        subcmd = hazwaz.mixins.ExternalEditorMixin()
        subcmd.editors = [("cat", "cat")]
        # TODO: suppress this output in the tests (we can't use
        # contextlib.redirect_stderr because that doesn't redirect the
        # stderr used by subprocess.
        res = subcmd.edit_file_in_external_editor("no_such_file")
        self.assertFalse(res)

    def test_open_with_non_existing_editor(self):
        subcmd = hazwaz.mixins.ExternalEditorMixin()
        subcmd.editors = [("no_such_command", "no_such_command")]
        with self.assertLogs() as cm:
            subcmd.edit_file_in_external_editor("no_such_file")
        self.assertIn(
            "Could not open file no_such_file with no_such_command",
            cm.output[0]
        )


class MyCommand(hazwaz.MainCommand, hazwaz.mixins.ExternalEditorMixin):
    """
    A command that edits a file
    """

    def main(self):
        my_file = tempfile.NamedTemporaryFile()
        self.edit_file_in_external_editor(my_file.name)
        my_file.close()


class testCommandWithMixin(hazwaz.unittest.HazwazTestCase):
    def test_run(self):
        cmd = MyCommand()
        cmd.editors = [("true", "true")]
        stream = self.run_with_argv(cmd, [
            "mycommand",
        ])
        self.assertEqual(stream["stdout"].getvalue(), "")
        self.assertEqual(stream["stderr"].getvalue(), "")


if __name__ == '__main__':
    unittest.main()
