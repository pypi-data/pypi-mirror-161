import io
import pathlib
import tempfile
import unittest

import torch
from irisml.tasks.load_state_dict import Task


class TestLoadStateDict(unittest.TestCase):
    def test_simple(self):
        fake_model = torch.nn.Conv2d(3, 3, 3)
        fake_model2 = torch.nn.Conv2d(3, 3, 3)
        self.assertFalse(self._is_equal_state_dict(fake_model.state_dict(), fake_model2.state_dict()))

        # Load from a file.
        inputs = Task.Inputs(model=fake_model)
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = pathlib.Path(temp_dir) / 'test.pth'
            torch.save(fake_model2.state_dict(), temp_file)

            config = Task.Config(path=temp_file)

            task = Task(config)
            outputs = task.execute(inputs)
            model = outputs.model
            self.assertTrue(self._is_equal_state_dict(model.state_dict(), fake_model2.state_dict()))

        # Load from state_dict
        task = Task(Task.Config())
        fake_model = torch.nn.Conv2d(3, 3, 3)
        inputs = Task.Inputs(model=fake_model, state_dict=fake_model2.state_dict())
        outputs = task.execute(inputs)
        self.assertTrue(self._is_equal_state_dict(outputs.model.state_dict(), fake_model2.state_dict()))

        # Load from state_dict_bytes
        state_buffer = io.BytesIO()
        torch.save(fake_model2.state_dict(), state_buffer)
        fake_model = torch.nn.Conv2d(3, 3, 3)
        inputs = Task.Inputs(model=fake_model, state_dict_bytes=state_buffer.getbuffer().tobytes())
        outputs = task.execute(inputs)
        self.assertTrue(self._is_equal_state_dict(outputs.model.state_dict(), fake_model2.state_dict()))

    def test_copied(self):
        fake_model = torch.nn.Conv2d(3, 3, 3)
        fake_model2 = torch.nn.Conv2d(3, 3, 3)
        task = Task(Task.Config())
        inputs = Task.Inputs(model=fake_model, state_dict=fake_model2.state_dict())
        task.execute(inputs)
        self.assertFalse(self._is_equal_state_dict(fake_model.state_dict(), fake_model2.state_dict()))

    def test_multiple_source(self):
        fake_model = torch.nn.Conv2d(3, 3, 3)
        task = Task(Task.Config('temp.path'))
        inputs = Task.Inputs(model=fake_model, state_dict={'a': torch.zeros(1)})
        with self.assertRaises(ValueError):
            task.execute(inputs)

        inputs = Task.Inputs(model=fake_model, state_dict_bytes=b'123')
        with self.assertRaises(ValueError):
            task.execute(inputs)

        task = Task(Task.Config())
        inputs = Task.Inputs(model=fake_model, state_dict={'a': torch.zeros(1)}, state_dict_bytes=b'123')
        with self.assertRaises(ValueError):
            task.execute(inputs)

    def _is_equal_state_dict(self, state_dict1, state_dict2):
        if set(state_dict1) != set(state_dict2):
            return False

        for key in state_dict1:
            if not torch.equal(state_dict1[key], state_dict2[key]):
                return False
        return True
