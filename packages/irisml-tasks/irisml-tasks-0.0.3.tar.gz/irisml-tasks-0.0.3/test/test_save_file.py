import pathlib
import tempfile
import unittest
from irisml.core import Context
from irisml.tasks.save_file import Task


class TestSaveFile(unittest.TestCase):
    def test_simple(self):
        inputs = Task.Inputs(b'12345')
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = pathlib.Path(temp_dir) / 'directory' / 'myfile'
            config = Task.Config(temp_file)
            task = Task(config, Context())
            task.execute(inputs)

            self.assertTrue(temp_file.exists())
            self.assertEqual(temp_file.read_bytes(), b'12345')
