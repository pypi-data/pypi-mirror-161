import dataclasses
import random
import torch.utils.data
import irisml.core


class Task(irisml.core.TaskBase):
    """Get a subset of the given dataset."""
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Config:
        num_images: int

    @dataclasses.dataclass
    class Inputs:
        dataset: torch.utils.data.Dataset

    @dataclasses.dataclass
    class Outputs:
        dataset: torch.utils.data.Dataset = None

    def execute(self, inputs):
        num_images = len(inputs.dataset)
        new_num_images = self.config.num_images
        indexes = random.sample(range(num_images), new_num_images)
        new_dataset = torch.utils.data.Subset(inputs.dataset, indexes)
        return self.Outputs(new_dataset)
