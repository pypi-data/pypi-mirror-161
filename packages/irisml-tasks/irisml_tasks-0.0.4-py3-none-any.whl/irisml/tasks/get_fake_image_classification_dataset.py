import dataclasses
import logging
import random
import typing
import irisml.core
import torch
import PIL.Image

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Generate a fake image classification dataset.

    A generated dataset returns (image:PIL.Image, target:int)
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Config:
        num_images: int = 100
        num_classes: int = 10

    @dataclasses.dataclass
    class Outputs:
        dataset: torch.utils.data.Dataset = None
        num_classes: int = 0

    class FakeDataset(torch.utils.data.Dataset):
        def __init__(self, image_labels: typing.List[int], colors: typing.List[typing.Tuple[int, int, int]]):
            self._image_labels = image_labels
            self._colors = colors

        def __len__(self):
            return len(self._image_labels)

        def __getitem__(self, index):
            image_class = self._image_labels[index]
            return self._generate_image(image_class), image_class

        def _generate_image(self, class_id):
            return PIL.Image.new('RGB', (224, 224), color=self._colors[class_id])

    def execute(self, inputs):
        if not self.config.num_images or not self.config.num_classes or self.config.num_images < self.config.num_classes:
            raise ValueError(f"Invalid settings: num_images={self.config.num_images}, num_classes={self.config.num_classes}")

        num_images_per_class = [self.config.num_images // self.config.num_classes for _ in range(self.config.num_classes)]
        for i in range(self.config.num_images % self.config.num_classes):
            num_images_per_class[i] += 1

        assert sum(num_images_per_class) == self.config.num_images
        assert len(num_images_per_class) == self.config.num_classes

        labels = [c for c, x in enumerate(num_images_per_class) for _ in range(x)]
        random.shuffle(labels)

        colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for i in range(self.config.num_classes)]
        logger.debug(f"Generated labels: {colors}")
        dataset = Task.FakeDataset(labels, colors)
        return self.Outputs(dataset, num_classes=self.config.num_classes)
