import dataclasses
import sys
import unittest
import unittest.mock
from irisml.core import Context, TaskDescription, TaskBase
from irisml.tasks.search_grid_sequential import Task, SearchSpaceConfig


class FakeTask:
    class Task(TaskBase):
        @dataclasses.dataclass
        class Inputs:
            input1: int
            input2: float

        @dataclasses.dataclass
        class Outputs:
            output: float = 0

        def execute(self, inputs):
            print(inputs)
            return self.Outputs(inputs.input1 + inputs.input2)


class TestSearchGrid(unittest.TestCase):
    def test_execute(self):
        tasks = [{'task': 'fake_task', 'inputs': {'input1': '$env.VALUE1', 'input2': '$env.VALUE2'}}]
        config = Task.Config(search_space=[SearchSpaceConfig('VALUE1', [1, 3, 5]), SearchSpaceConfig('VALUE2', [0.1, 0.3, 0.5])],
                             tasks=[TaskDescription.from_dict(t) for t in tasks],
                             metrics_output_name='fake_task.output')

        context = Context()
        with unittest.mock.patch.dict('sys.modules'):
            sys.modules['irisml.tasks.fake_task'] = FakeTask
            task = Task(config, context)
            outputs = task.execute(None)

        self.assertEqual(outputs.best_parameters, {'VALUE1': 5, 'VALUE2': 0.5})
        self.assertEqual(context.get_outputs('fake_task').output, 5.5)
