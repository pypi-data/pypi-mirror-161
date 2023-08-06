import dataclasses
import sys
import unittest
import unittest.mock
from irisml.core import Context, TaskDescription, TaskBase
from irisml.tasks.run_parallel import Task


class FakeTask:
    class Task(TaskBase):
        @dataclasses.dataclass
        class Outputs:
            pass

        def execute(self, inputs):
            return self.Outputs()


class TestRunParallel(unittest.TestCase):
    def test_run(self):
        tasks = [
            {'task': 'fake_task', 'name': 'task0'},
            {'task': 'fake_task', 'name': 'task1'},
            {'task': 'fake_task', 'name': 'task2'}
        ]

        config = Task.Config(tasks=[TaskDescription.from_dict(t) for t in tasks])
        context = Context()

        with unittest.mock.patch.dict('sys.modules'):
            sys.modules['irisml.tasks.fake_task'] = FakeTask
            task = Task(config, context)
            task.execute(None)

        self.assertIsNotNone(context.get_outputs('task0'))
        self.assertIsNotNone(context.get_outputs('task1'))
        self.assertIsNotNone(context.get_outputs('task2'))
