import unittest
from irisml.tasks.get_fake_object_detection_dataset import Task


class TestGetFakeObjectDetectionDataset(unittest.TestCase):
    def test_simple(self):
        config = Task.Config(num_images=100, num_classes=10, num_max_boxes=10)
        task = Task(config)
        outputs = task.execute(None)
        dataset = outputs.dataset
        self.assertEqual(len(dataset), 100)
        class_set = set(int(t[0]) for x in dataset for t in x[1])
        self.assertEqual(len(class_set), 10)
        self.assertTrue(all(len(x[1]) <= 10 for x in dataset))
        self.assertLess(sum(len(x[1]) for x in dataset), 1000)
        self.assertTrue(all(len(x[1].shape) == 2 for x in dataset))
        self.assertTrue(all(0 <= x[1] < x[3] <= 1 for _, t in dataset for x in t))
        self.assertTrue(all(0 <= x[2] < x[4] <= 1 for _, t in dataset for x in t))
