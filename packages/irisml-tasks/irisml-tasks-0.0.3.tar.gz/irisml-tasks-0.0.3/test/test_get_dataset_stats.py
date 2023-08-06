import unittest
import torch
from irisml.tasks.get_dataset_stats import Task


class TestGetDatasetStats(unittest.TestCase):
    def test_multiclass_classification(self):
        class Dataset(torch.utils.data.Dataset):
            def __len__(self):
                return 3

            def __getitem__(self, index):
                return (torch.zeros((3, 100, 100)), torch.Tensor([index]))

            def __iter__(self):
                yield self[0]
                yield self[1]
                yield self[2]

        dataset = Dataset()

        task = Task(Task.Config())
        outputs = task.execute(Task.Inputs(dataset))
        self.assertEqual(outputs.num_images, 3)
        self.assertEqual(outputs.num_classes, 3)
        self.assertEqual(outputs.dataset_type, 'multiclass_classification')

    def test_multilabel_classification(self):
        class Dataset(torch.utils.data.Dataset):
            DATA = [torch.Tensor([0, 1, 2]), torch.Tensor([0]), torch.Tensor([])]

            def __len__(self):
                return len(self.DATA)

            def __getitem__(self, index):
                return (torch.zeros((3, 100, 100)), self.DATA[index])

            def __iter__(self):
                yield self[0]
                yield self[0]
                yield self[0]

        dataset = Dataset()

        task = Task(Task.Config())
        outputs = task.execute(Task.Inputs(dataset))
        self.assertEqual(outputs.num_images, 3)
        self.assertEqual(outputs.num_classes, 3)
        self.assertEqual(outputs.dataset_type, 'multilabel_classification')

    def test_object_detection(self):
        class Dataset(torch.utils.data.Dataset):
            DATA = [torch.Tensor([[0, 0.1, 0.1, 0.2, 0.2], [1, 0.1, 0.1, 0.2, 0.2], [2, 0.1, 0.1, 0.2, 0.2]]), torch.Tensor([[0, 0.1, 0.1, 0.2, 0.2]]), torch.Tensor([])]

            def __len__(self):
                return len(self.DATA)

            def __getitem__(self, index):
                return (torch.zeros((3, 100, 100)), self.DATA[index])

            def __iter__(self):
                yield self[0]
                yield self[0]
                yield self[0]

        dataset = Dataset()

        task = Task(Task.Config())
        outputs = task.execute(Task.Inputs(dataset))
        self.assertEqual(outputs.num_images, 3)
        self.assertEqual(outputs.num_classes, 3)
        self.assertEqual(outputs.dataset_type, 'object_detection')
