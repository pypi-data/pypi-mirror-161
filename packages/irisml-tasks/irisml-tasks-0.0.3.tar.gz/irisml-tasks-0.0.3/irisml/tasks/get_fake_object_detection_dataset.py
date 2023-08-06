import dataclasses
import logging
import random
import typing
import irisml.core
import torch
import PIL.Image
import PIL.ImageDraw

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Generate a fake object detection dataset.

    A generated dataset returns (image:PIL.Image, targets:List[Tensor[N, 5]])
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Config:
        num_images: int = 100
        num_classes: int = 10
        num_max_boxes: int = 10  # The max number of objects per image.

    @dataclasses.dataclass
    class Outputs:
        dataset: torch.utils.data.Dataset = None
        num_classes: int = 0

    _IMAGE_SIZE = (320, 320)  # Width, height of an image

    class FakeDataset(torch.utils.data.Dataset):
        def __init__(self, targets: typing.List[torch.Tensor], colors: typing.List[typing.Tuple[int, int, int]]):
            self._targets = targets
            self._colors = colors

        def __len__(self):
            return len(self._targets)

        def __getitem__(self, index):
            targets = self._targets[index]
            return self._generate_image(targets), targets

        def _generate_image(self, targets):
            image = PIL.Image.new('RGB', Task._IMAGE_SIZE)
            draw = PIL.ImageDraw.Draw(image)
            for t in targets:
                rect = [t[1] * Task._IMAGE_SIZE[0], t[2] * Task._IMAGE_SIZE[1], t[3] * Task._IMAGE_SIZE[0], t[4] * Task._IMAGE_SIZE[1]]
                draw.rectangle(rect, fill=self._colors[int(t[0])])
            return image

    def execute(self, inputs):
        def _random_box():
            cx = random.random()
            cy = random.random()
            w = random.uniform(0, min(1 - cx, cx))
            h = random.uniform(0, min(1 - cy, cy))
            return [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]

        targets = [torch.tensor([[random.randrange(self.config.num_classes), *_random_box()] for _ in range(random.randrange(self.config.num_max_boxes + 1))]).reshape(-1, 5)
                   for _ in range(self.config.num_images)]

        colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for i in range(self.config.num_classes)]
        logger.debug(f"Generated labels: {colors}")
        dataset = Task.FakeDataset(targets, colors)
        return self.Outputs(dataset, num_classes=self.config.num_classes)
