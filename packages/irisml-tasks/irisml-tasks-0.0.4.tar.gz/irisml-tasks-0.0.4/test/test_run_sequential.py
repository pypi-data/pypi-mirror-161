import sys
import unittest
import unittest.mock
from irisml.core import TaskDescription, TaskBase
from irisml.tasks.run_sequential import Task


class FakeTask:
    class Task(TaskBase):
        def execute(self, inputs):
            pass


class TestRunSequential(unittest.TestCase):
    def test_run(self):
        tasks = [
            {'task': 'fake_task', 'name': 'task0'},
            {'task': 'fake_task', 'name': 'task1'},
            {'task': 'fake_task', 'name': 'task2'}
        ]

        config = Task.Config(tasks=[TaskDescription.from_dict(t) for t in tasks])
        context = unittest.mock.MagicMock()

        with unittest.mock.patch.dict('sys.modules'):
            sys.modules['irisml.tasks.fake_task'] = FakeTask
            task = Task(config, context)
            task.execute(None)

        context.add_outputs.assert_any_call('task0', unittest.mock.ANY)
        context.add_outputs.assert_any_call('task1', unittest.mock.ANY)
        context.add_outputs.assert_any_call('task2', unittest.mock.ANY)
