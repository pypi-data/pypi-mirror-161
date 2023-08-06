import typing
import unittest
import torch
from irisml.core import Context
from irisml.tasks.get_dataset_subset import Task


class DummyDataset(torch.utils.data.Dataset):
    def __init__(self, data: typing.List):
        self._data = data

    def __len__(self):
        return len(self._data)

    def __getitem__(self, x):
        return self._data[x]


class TestGetDatasetSubset(unittest.TestCase):
    def test_simple(self):
        dataset = DummyDataset(list(range(100)))

        inputs = Task.Inputs(dataset=dataset)
        config = Task.Config(num_images=10)

        context = Context()
        task = Task(config, context)
        outputs = task.execute(inputs)
        self.assertEqual(len(outputs.dataset), 10)
