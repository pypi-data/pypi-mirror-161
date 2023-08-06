import unittest
from irisml.core import Context
from irisml.tasks.get_fake_image_classification_dataset import Task


class TestGetFakeImageClassificationDataset(unittest.TestCase):
    def test_simple(self):
        config = Task.Config(num_images=100, num_classes=10)
        task = Task(config, Context())
        outputs = task.execute(None)
        dataset = outputs.dataset
        self.assertEqual(len(dataset), 100)
        class_set = set(x[1] for x in dataset)
        self.assertEqual(len(class_set), 10)
