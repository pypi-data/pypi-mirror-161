import unittest
from irisml.tasks.get_item import Task


class TestGetItem(unittest.TestCase):
    def test_simple(self):
        inputs = Task.Inputs([1, 2, 3])
        config = Task.Config(1)
        outputs = Task(config).execute(inputs)
        self.assertEqual(outputs.item, 2)

        with self.assertRaises(IndexError):
            Task(config).execute(Task.Inputs([0]))
